import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from app.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.models.tax_event import TaxEvent
from app.services.tax_engine import calculate_fifo
from app.utils.error_handler import (
    handle_database_error,
    handle_external_api_error,
    handle_permission_error,
    handle_not_found_error,
    handle_general_error,
    log_request_info,
    validate_financial_year_format,
)
from app.utils.validators import sanitize_string, validate_csv_content
from app.middleware.rate_limit import reports_rate_limit

logger = logging.getLogger(__name__)
router = APIRouter()


def get_financial_year_range(
    financial_year: str, user_fy_start: str = "04-01"
) -> tuple:
    """
    Convert financial year string (e.g., "2024-25") to date range.
    For India: April 1 of first year to March 31 of second year.
    """
    try:
        # Validate financial year format
        if not validate_financial_year_format(financial_year):
            raise HTTPException(
                status_code=400,
                detail="Invalid financial year format. Use format 'YYYY-YY' (e.g., '2024-25')",
            )
        # Extract years from format "2024-25"
        start_year = int(financial_year[:4])
        # Parse user's financial year start (default "04-01" for India)
        month, day = map(int, user_fy_start.split("-"))
        # Validate month and day
        if not (1 <= month <= 12) or not (1 <= day <= 31):
            raise HTTPException(
                status_code=400,
                detail="Invalid financial year start date format. Use format 'MM-DD' (e.g., '04-01')",
            )
        # Calculate date range (end_date is exclusive upper bound)
        start_date = datetime(start_year, month, day)
        end_date = datetime(start_year + 1, month, day)
        return start_date, end_date
    except (ValueError, IndexError) as e:
        logger.error(f"Financial year parsing error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail="Invalid financial year format. Use format 'YYYY-YY' (e.g., '2024-25')",
        )


def calculate_financial_year(timestamp: datetime, user_fy_start: str = "04-01") -> str:
    """
    Calculate financial year for a given timestamp.
    """
    try:
        month, day = map(int, user_fy_start.split("-"))
        # Validate month and day
        if not (1 <= month <= 12) or not (1 <= day <= 31):
            logger.warning(
                f"Invalid financial year start: {user_fy_start}, using default"
            )
            return f"{timestamp.year}-{str(timestamp.year + 1)[2:]}"
        if timestamp.month >= month or (
            timestamp.month == month and timestamp.day >= day
        ):
            # Falls in the financial year starting this calendar year
            return f"{timestamp.year}-{str(timestamp.year + 1)[2:]}"
        else:
            # Falls in the financial year starting previous calendar year
            return f"{timestamp.year - 1}-{str(timestamp.year)[2:]}"
    except (ValueError, IndexError) as e:
        logger.error(f"Financial year calculation error: {str(e)}", exc_info=True)
        return f"{timestamp.year}-{str(timestamp.year + 1)[2:]}"


def validate_itr_financial_year(financial_year: str) -> bool:
    """
    Validate financial year format for ITR reporting.
    Indian ITR requires specific format validation.
    """
    return validate_financial_year_format(financial_year)


@router.get("/tax/summary")
@reports_rate_limit
async def get_tax_summary(
    financial_year: Optional[str] = Query(
        None, description="Financial year in format 'YYYY-YY' (e.g., '2024-25')"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get tax summary for a specific financial year.
    Calculates FIFO gains/losses with short-term vs long-term classification.
    """
    try:
        # Log request info
        log_request_info(
            user_id=str(current_user.id),
            endpoint="/tax/summary",
            params={"financial_year": financial_year},
            status_code=200,
        )
        # Validate financial year parameter
        user_fy_start = current_user.financial_year_start or "04-01"
        if financial_year:
            # Validate financial year format
            if not validate_financial_year_format(financial_year):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid financial year format. Use format 'YYYY-YY' (e.g., '2024-25')",
                )
            start_date, end_date = get_financial_year_range(
                financial_year, user_fy_start
            )
        else:
            # Default to current financial year
            current_date = datetime.now()
            financial_year = calculate_financial_year(current_date, user_fy_start)
            start_date, end_date = get_financial_year_range(
                financial_year, user_fy_start
            )
        # Get all user transactions within the financial year
        try:
            result = await db.execute(
                select(Transaction)
                .where(Transaction.user_id == current_user.id)
                .where(Transaction.timestamp >= start_date)
                .where(Transaction.timestamp < end_date)
                .order_by(Transaction.timestamp)
            )
            transactions = result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(
                f"Database error fetching transactions: {str(e)}", exc_info=True
            )
            raise handle_database_error(e, "fetch_transactions")
        if not transactions:
            logger.info(
                f"No transactions found for user {current_user.id} in FY {financial_year}"
            )
            return {
                "financial_year": financial_year,
                "total_gain_loss_usd": Decimal("0"),
                "short_term_gain_loss_usd": Decimal("0"),
                "long_term_gain_loss_usd": Decimal("0"),
                "token_breakdown": [],
                "transaction_count": 0,
                "tax_event_count": 0,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
                "message": "No transactions found for this financial year",
            }
        # Group transactions by token symbol
        transactions_by_token: Dict[str, List[Transaction]] = {}
        for tx in transactions:
            if tx.token_symbol:
                sanitized_symbol = sanitize_string(tx.token_symbol)
                if sanitized_symbol:
                    if sanitized_symbol not in transactions_by_token:
                        transactions_by_token[sanitized_symbol] = []
                    transactions_by_token[sanitized_symbol].append(tx)
        # Calculate tax events for each token
        tax_events: List[TaxEvent] = []
        token_breakdown = []
        for token_symbol, token_transactions in transactions_by_token.items():
            try:
                events = calculate_fifo(
                    str(current_user.id), token_symbol, token_transactions
                )
                tax_events.extend(events)
                # Calculate token-level summary
                token_gain_loss = sum(event.gain_loss_usd for event in events)
                short_term_gain_loss = sum(
                    event.gain_loss_usd for event in events if event.is_short_term
                )
                long_term_gain_loss = sum(
                    event.gain_loss_usd for event in events if not event.is_short_term
                )
                token_breakdown.append(
                    {
                        "token_symbol": token_symbol,
                        "total_gain_loss_usd": token_gain_loss,
                        "short_term_gain_loss_usd": short_term_gain_loss,
                        "long_term_gain_loss_usd": long_term_gain_loss,
                        "transaction_count": len(token_transactions),
                        "tax_event_count": len(events),
                    }
                )
            except Exception as e:
                logger.error(
                    f"Error calculating FIFO for token {token_symbol}: {str(e)}",
                    exc_info=True,
                )
                continue  # Skip this token but continue with others
        # Calculate overall totals
        total_gain_loss = sum(event.gain_loss_usd for event in tax_events)
        short_term_total = sum(
            event.gain_loss_usd for event in tax_events if event.is_short_term
        )
        long_term_total = sum(
            event.gain_loss_usd for event in tax_events if not event.is_short_term
        )
        logger.info(
            f"Tax summary generated for user {current_user.id}, FY {financial_year}: {len(tax_events)} events"
        )
        return {
            "financial_year": financial_year,
            "total_gain_loss_usd": total_gain_loss,
            "short_term_gain_loss_usd": short_term_total,
            "long_term_gain_loss_usd": long_term_total,
            "token_breakdown": token_breakdown,
            "transaction_count": len(transactions),
            "tax_event_count": len(tax_events),
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in tax summary: {str(e)}", exc_info=True)
        raise handle_general_error(e, "tax_summary_calculation")


@router.post("/csv")
@reports_rate_limit
async def generate_csv_report(
    fy_param: Optional[str] = Query(
        None,
        description="Financial year in format 'YYYY-YY' (e.g., '2024-25')",
        alias="financial_year",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate comprehensive CSV tax report for the specified financial year.
    Includes transaction details, tax calculations, and gain/loss information.
    Returns a downloadable CSV file.
    """
    try:
        # Determine financial year range
        user_fy_start = current_user.financial_year_start or "04-01"
        if fy_param:
            start_date, end_date = get_financial_year_range(fy_param, user_fy_start)
            financial_year = fy_param
        else:
            # Default to current financial year
            current_date = datetime.now()
            financial_year = calculate_financial_year(current_date, user_fy_start)
            start_date, end_date = get_financial_year_range(
                financial_year, user_fy_start
            )
        # Get all user transactions within the financial year
        result = await db.execute(
            select(Transaction)
            .where(Transaction.user_id == current_user.id)
            .where(Transaction.timestamp >= start_date)
            .where(Transaction.timestamp < end_date)
            .order_by(Transaction.timestamp)
        )
        transactions = result.scalars().all()
        if not transactions:
            raise HTTPException(
                status_code=404,
                detail=f"No transactions found for financial year {financial_year}",
            )
        # Group transactions by token symbol
        transactions_by_token: Dict[str, List[Transaction]] = {}
        for tx in transactions:
            if tx.token_symbol:
                if tx.token_symbol not in transactions_by_token:
                    transactions_by_token[tx.token_symbol] = []
                transactions_by_token[tx.token_symbol].append(tx)
        # Calculate tax events for each token
        tax_events: List[TaxEvent] = []
        for token_symbol, token_transactions in transactions_by_token.items():
            events = calculate_fifo(
                str(current_user.id), token_symbol, token_transactions
            )
            tax_events.extend(events)
        if not tax_events:
            raise HTTPException(
                status_code=404,
                detail=f"No tax events calculated for financial year {financial_year}",
            )
        # Create CSV content
        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)
        # Write CSV headers
        headers = [
            "Financial Year",
            "Transaction Date",
            "Token Symbol",
            "Transaction Type",
            "Chain",
            "Transaction Hash",
            "Quantity",
            "Price USD",
            "Value USD",
            "Fee USD",
            "Acquisition Date",
            "Disposal Date",
            "Holding Period",
            "Quantity Sold",
            "Cost Basis USD",
            "Proceeds USD",
            "Gain/Loss USD",
            "Gain/Loss Type",
        ]
        csv_writer.writerow(headers)
        # Write tax event data
        for event in tax_events:
            # Get the sale transaction
            sale_tx = await db.get(Transaction, event.sale_tx_id)
            # Format holding period
            holding_period = "Short-Term" if event.is_short_term else "Long-Term"
            # Format dates
            tx_date = sale_tx.timestamp.strftime("%Y-%m-%d %H:%M:%S") if sale_tx else ""
            disposal_date = event.disposed_at.strftime("%Y-%m-%d %H:%M:%S")
            acquisition_date = (
                event.acquired_at.strftime("%Y-%m-%d %H:%M:%S")
                if event.acquired_at
                else ""
            )
            csv_writer.writerow(
                [
                    event.financial_year or financial_year,
                    tx_date,
                    event.token_symbol,
                    sale_tx.tx_type if sale_tx else "sale",
                    sale_tx.chain if sale_tx else "",
                    sale_tx.tx_hash if sale_tx else "",
                    f"{event.quantity:.8f}",
                    f"{sale_tx.price_usd:.2f}"
                    if sale_tx and sale_tx.price_usd
                    else "0.00",
                    f"{sale_tx.value_usd:.2f}"
                    if sale_tx and sale_tx.value_usd
                    else "0.00",
                    f"{sale_tx.fee_usd:.2f}" if sale_tx and sale_tx.fee_usd else "0.00",
                    acquisition_date,
                    disposal_date,
                    holding_period,
                    f"{event.quantity:.8f}",
                    f"{event.cost_basis_usd:.2f}",
                    f"{event.proceeds_usd:.2f}",
                    f"{event.gain_loss_usd:.2f}",
                    "Gain" if event.gain_loss_usd >= 0 else "Loss",
                ]
            )
        csv_content = csv_buffer.getvalue()
        csv_buffer.close()
        # Return as downloadable file
        filename = f"taxchain_report_{financial_year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/csv; charset=utf-8",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating CSV report: {str(e)}"
        )


@router.post("/pdf")
async def generate_pdf_report(
    fy_param: Optional[str] = Query(
        None,
        description="Financial year in format 'YYYY-YY' (e.g., '2024-25')",
        alias="financial_year",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate comprehensive PDF tax report for the specified financial year.
    Includes professional cover page, executive summary, detailed transaction breakdown,
    and tax calculation methodology explanation.
    Returns a downloadable PDF file.
    """
    try:
        # Import ReportLab here to avoid dependency issues if not installed
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.units import inch
            from reportlab.lib.colors import HexColor
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                Table,
                TableStyle,
                PageBreak,
            )
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="PDF generation requires ReportLab library. Please install with 'pip install reportlab'",
            )
        # Determine financial year range
        user_fy_start = current_user.financial_year_start or "04-01"
        if fy_param:
            start_date, end_date = get_financial_year_range(fy_param, user_fy_start)
            financial_year = fy_param
        else:
            # Default to current financial year
            current_date = datetime.now()
            financial_year = calculate_financial_year(current_date, user_fy_start)
            start_date, end_date = get_financial_year_range(
                financial_year, user_fy_start
            )
        # Get all user transactions within the financial year
        result = await db.execute(
            select(Transaction)
            .where(Transaction.user_id == current_user.id)
            .where(Transaction.timestamp >= start_date)
            .where(Transaction.timestamp < end_date)
            .order_by(Transaction.timestamp)
        )
        transactions = result.scalars().all()
        if not transactions:
            raise HTTPException(
                status_code=404,
                detail=f"No transactions found for financial year {financial_year}",
            )
        # Get tax summary data by calling the internal function
        tax_summary = await get_tax_summary(financial_year, db, current_user)
        # Create PDF in memory buffer
        pdf_buffer = io.BytesIO()
        # Use A4 paper size for international compatibility
        doc = SimpleDocTemplate(
            pdf_buffer, pagesize=A4, topMargin=0.5 * inch, bottomMargin=0.5 * inch
        )
        # Create story (content elements)
        story = []
        styles = getSampleStyleSheet()
        # Define custom styles
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Title"],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor("#0F172A"),
            alignment=TA_CENTER,
        )
        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading1"],
            fontSize=16,
            spaceAfter=12,
            textColor=HexColor("#0F172A"),
            spaceBefore=20,
        )
        subheading_style = ParagraphStyle(
            "CustomSubheading",
            parent=styles["Heading2"],
            fontSize=14,
            spaceAfter=8,
            textColor=HexColor("#64748B"),
            spaceBefore=15,
        )
        normal_style = ParagraphStyle(
            "CustomNormal",
            parent=styles["Normal"],
            fontSize=10,
            spaceAfter=6,
            textColor=HexColor("#0F172A"),
        )
        small_style = ParagraphStyle(
            "CustomSmall",
            parent=styles["Normal"],
            fontSize=8,
            spaceAfter=4,
            textColor=HexColor("#64748B"),
        )
        # Cover Page
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph("TAXCHAIN", title_style))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph("Cryptocurrency Tax Report", heading_style))
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph(f"Financial Year: {financial_year}", normal_style))
        story.append(
            Paragraph(
                f"Generated: {datetime.now().strftime('%B %d, %Y')}", normal_style
            )
        )
        story.append(Spacer(1, 1 * inch))
        story.append(Paragraph(f"Prepared for: {current_user.email}", small_style))
        story.append(PageBreak())
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        # Summary table
        summary_data = [
            ["Metric", "Amount (USD)"],
            ["Total Gain/Loss", f"${tax_summary['total_gain_loss_usd']:,.2f}"],
            [
                "Short-Term Gain/Loss",
                f"${tax_summary['short_term_gain_loss_usd']:,.2f}",
            ],
            ["Long-Term Gain/Loss", f"${tax_summary['long_term_gain_loss_usd']:,.2f}"],
            ["Total Transactions", f"{tax_summary['transaction_count']}"],
            ["Tax Events Calculated", f"{tax_summary['tax_event_count']}"],
        ]
        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F8F9FA")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#0F172A")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), HexColor("#FFFFFF")),
                    ("GRID", (0, 0), (-1, -1), 1, HexColor("#E2E8F0")),
                ]
            )
        )
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))
        # Token Breakdown
        story.append(Paragraph("Token Breakdown", subheading_style))
        if tax_summary["token_breakdown"]:
            token_data = [["Token", "Gain/Loss (USD)", "Transactions", "Tax Events"]]
            for token in tax_summary["token_breakdown"]:
                gain_loss = token["total_gain_loss_usd"]
                color = HexColor("#10B981") if gain_loss >= 0 else HexColor("#EF4444")
                token_data.append(
                    [
                        token["token_symbol"],
                        f"${gain_loss:,.2f}",
                        str(token["transaction_count"]),
                        str(token["tax_event_count"]),
                    ]
                )
            token_table = Table(
                token_data, colWidths=[1.5 * inch, 1.5 * inch, 1 * inch, 1 * inch]
            )
            token_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F8F9FA")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#0F172A")),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                        ("BACKGROUND", (0, 1), (-1, -1), HexColor("#FFFFFF")),
                        ("GRID", (0, 0), (-1, -1), 1, HexColor("#E2E8F0")),
                        (
                            "TEXTCOLOR",
                            (1, 1),
                            (1, -1),
                            lambda r, c: (
                                HexColor("#10B981")
                                if r > 0
                                and float(
                                    token_data[r][1].replace("$", "").replace(",", "")
                                )
                                >= 0
                                else HexColor("#EF4444")
                            ),
                        ),
                    ]
                )
            )
            story.append(token_table)
        else:
            story.append(Paragraph("No token data available", normal_style))
        story.append(Spacer(1, 0.3 * inch))
        # Detailed Transactions
        story.append(Paragraph("Detailed Tax Events", heading_style))
        story.append(PageBreak())
        # Group transactions by token symbol
        transactions_by_token: Dict[str, List[Transaction]] = {}
        for tx in transactions:
            if tx.token_symbol:
                if tx.token_symbol not in transactions_by_token:
                    transactions_by_token[tx.token_symbol] = []
                transactions_by_token[tx.token_symbol].append(tx)
        # Calculate tax events for each token
        tax_events: List[TaxEvent] = []
        for token_symbol, token_transactions in transactions_by_token.items():
            events = calculate_fifo(
                str(current_user.id), token_symbol, token_transactions
            )
            tax_events.extend(events)
        if tax_events:
            # Create transaction table
            tx_data = [
                [
                    "Date",
                    "Token",
                    "Type",
                    "Quantity",
                    "Price USD",
                    "Gain/Loss USD",
                    "Period",
                ]
            ]
            for event in tax_events:
                sale_tx = await db.get(Transaction, event.sale_tx_id)
                tx_date = sale_tx.timestamp.strftime("%Y-%m-%d") if sale_tx else ""
                gain_loss = event.gain_loss_usd
                period = "Short-Term" if event.is_short_term else "Long-Term"
                tx_data.append(
                    [
                        tx_date,
                        event.token_symbol,
                        sale_tx.tx_type if sale_tx else "sale",
                        f"{event.quantity:.8f}",
                        f"${sale_tx.price_usd:.2f}"
                        if sale_tx and sale_tx.price_usd
                        else "$0.00",
                        f"${gain_loss:,.2f}",
                        period,
                    ]
                )
            tx_table = Table(
                tx_data,
                colWidths=[
                    0.8 * inch,
                    0.7 * inch,
                    0.8 * inch,
                    1 * inch,
                    1 * inch,
                    1 * inch,
                    0.8 * inch,
                ],
            )
            tx_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F8F9FA")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#0F172A")),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("ALIGN", (3, 0), (6, -1), "RIGHT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                        ("BACKGROUND", (0, 1), (-1, -1), HexColor("#FFFFFF")),
                        ("GRID", (0, 0), (-1, -1), 1, HexColor("#E2E8F0")),
                        (
                            "TEXTCOLOR",
                            (5, 1),
                            (5, -1),
                            lambda r, c: (
                                HexColor("#10B981")
                                if r > 0
                                and float(
                                    tx_data[r][5].replace("$", "").replace(",", "")
                                )
                                >= 0
                                else HexColor("#EF4444")
                            ),
                        ),
                    ]
                )
            )
            story.append(tx_table)
        else:
            story.append(Paragraph("No tax events calculated", normal_style))
        story.append(Spacer(1, 0.3 * inch))
        # Methodology Explanation
        story.append(Paragraph("Calculation Methodology", heading_style))
        story.append(
            Paragraph(
                "This report uses the First-In-First-Out (FIFO) method for calculating capital gains and losses. "
                "FIFO is the default accounting method for most jurisdictions and assumes that the first assets "
                "acquired are the first ones sold or disposed of.",
                normal_style,
            )
        )
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("Key Definitions:", subheading_style))
        story.append(
            Paragraph("• Short-Term: Assets held for less than 365 days", normal_style)
        )
        story.append(
            Paragraph("• Long-Term: Assets held for 365 days or more", normal_style)
        )
        story.append(Paragraph("• Gain: Proceeds exceed cost basis", normal_style))
        story.append(Paragraph("• Loss: Cost basis exceeds proceeds", normal_style))
        story.append(Spacer(1, 0.3 * inch))
        # Footer with disclaimer
        story.append(Paragraph("Disclaimer", subheading_style))
        story.append(
            Paragraph(
                "This report is provided for informational purposes only and should not be considered tax advice. "
                "Please consult with a qualified tax professional before filing your taxes. TaxChain is not "
                "responsible for any errors or omissions in this report.",
                small_style,
            )
        )
        story.append(Spacer(1, 0.2 * inch))
        story.append(
            Paragraph(
                f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                ParagraphStyle(
                    "Footer",
                    parent=styles["Normal"],
                    fontSize=7,
                    textColor=HexColor("#94A3B8"),
                    alignment=TA_CENTER,
                ),
            )
        )
        # Build PDF document
        doc.build(story)
        # Get PDF content
        pdf_content = pdf_buffer.getvalue()
        pdf_buffer.close()
        # Return as downloadable file
        filename = f"taxchain_tax_report_{financial_year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/pdf",
            },
        )
    except HTTPException:
        raise
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="PDF generation requires ReportLab library. Please install with 'pip install reportlab'",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating PDF report: {str(e)}"
        )


@router.post("/itr")
async def generate_itr_report(
    fy_param: Optional[str] = Query(
        None,
        description="Financial year in format 'YYYY-YY' (e.g., '2024-25')",
        alias="financial_year",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate ITR Schedule VDA report for Indian tax filing.
    Returns CSV in official Schedule VDA format as per Indian tax laws.
    """
    try:
        # Check if user has pro plan (ITR export is pro-only feature)
        if current_user.plan != "pro":
            raise HTTPException(
                status_code=403,
                detail="ITR Schedule VDA export requires Pro plan. Please upgrade to access this feature.",
            )
        # Determine financial year range
        user_fy_start = current_user.financial_year_start or "04-01"
        if fy_param:
            # Validate ITR financial year format
            if not validate_itr_financial_year(fy_param):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid financial year format for ITR. Use format 'YYYY-YY' (e.g., '2024-25')",
                )
            start_date, end_date = get_financial_year_range(fy_param, user_fy_start)
            financial_year = fy_param
        else:
            # Default to current financial year
            current_date = datetime.now()
            financial_year = calculate_financial_year(current_date, user_fy_start)
            start_date, end_date = get_financial_year_range(
                financial_year, user_fy_start
            )
        # Get all user tax events within the financial year
        result = await db.execute(
            select(TaxEvent)
            .where(TaxEvent.user_id == current_user.id)
            .where(TaxEvent.disposed_at >= start_date)
            .where(TaxEvent.disposed_at < end_date)
            .order_by(TaxEvent.disposed_at)
        )
        tax_events = result.scalars().all()
        if not tax_events:
            raise HTTPException(
                status_code=404,
                detail=f"No tax events found for financial year {financial_year}",
            )
        # Get current USD to INR exchange rate
        # In production, this should fetch from a reliable API like RBI, Forex, etc.
        # Using a placeholder rate - replace with actual API call
        usd_to_inr_rate = await get_usd_to_inr_exchange_rate()
        # Create CSV content
        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)
        # Write ITR Schedule VDA headers as per Indian tax requirements
        headers = [
            "Description of Digital Asset",
            "Date of Acquisition",
            "Date of Transfer/Disposal",
            "Cost of Acquisition (INR)",
            "Full Value of Consideration (INR)",
            "Capital Gains (INR)",
            "Type of Capital Gains",
            "Quantity of Digital Asset",
            "Blockchain/Platform",
            "Transaction Hash/ID",
            "Financial Year",
        ]
        csv_writer.writerow(headers)
        # Write tax event data in ITR VDA format
        for event in tax_events:
            # Get the sale transaction details
            sale_tx = await db.get(Transaction, event.sale_tx_id)
            # Convert USD amounts to INR with proper rounding for tax filing
            cost_acquisition_inr = round(event.cost_basis_usd * usd_to_inr_rate, 2)
            consideration_inr = round(event.proceeds_usd * usd_to_inr_rate, 2)
            capital_gains_inr = round(event.gain_loss_usd * usd_to_inr_rate, 2)
            # Format dates as per Indian tax requirements (DD/MM/YYYY)
            acquisition_date = (
                event.acquired_at.strftime("%d/%m/%Y") if event.acquired_at else ""
            )
            disposal_date = event.disposed_at.strftime("%d/%m/%Y")
            # Determine capital gains type
            capital_gains_type = "Short-term" if event.is_short_term else "Long-term"
            # Get blockchain/platform information
            blockchain = sale_tx.chain if sale_tx else "Unknown"
            # Format blockchain name for ITR
            blockchain_map = {
                "eth": "Ethereum",
                "bnb": "BNB Chain",
                "polygon": "Polygon",
                "sol": "Solana",
            }
            blockchain_display = blockchain_map.get(blockchain, blockchain.capitalize())
            csv_writer.writerow(
                [
                    event.token_symbol,  # Description of Digital Asset
                    acquisition_date,  # Date of Acquisition
                    disposal_date,  # Date of Transfer/Disposal
                    f"{cost_acquisition_inr:.2f}",  # Cost of Acquisition (INR)
                    f"{consideration_inr:.2f}",  # Full Value of Consideration (INR)
                    f"{capital_gains_inr:.2f}",  # Capital Gains (INR)
                    capital_gains_type,  # Type of Capital Gains
                    f"{event.quantity:.8f}",  # Quantity of Digital Asset
                    blockchain_display,  # Blockchain/Platform
                    sale_tx.tx_hash if sale_tx else "",  # Transaction Hash/ID
                    financial_year,  # Financial Year
                ]
            )
        csv_content = csv_buffer.getvalue()
        csv_buffer.close()
        # Return as downloadable file
        filename = f"itr_schedule_vda_{financial_year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/csv; charset=utf-8",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating ITR report: {str(e)}"
        )


async def get_usd_to_inr_exchange_rate() -> Decimal:
    """Get current USD to INR exchange rate via the exchange rate service."""
    from app.services.exchange_rate import get_usd_rate
    return await get_usd_rate("INR")


# ── Global Tax Format Endpoints ────────────────────────────────────────────


@router.post("/irs8949")
async def generate_irs_form_8949(
    tax_year: Optional[int] = Query(
        None, description="Tax year (e.g., 2025 for 2025 tax year)",
        alias="tax_year",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate IRS Form 8949 format (United States).
    Reports capital gains and losses for US tax filing.
    Returns CSV in IRS Form 8949 compatible format.
    """
    try:
        # Default to previous year (taxes filed in current year for prior year)
        year = tax_year or (datetime.now().year - 1)
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)

        # Get all user tax events within the tax year
        result = await db.execute(
            select(TaxEvent)
            .where(TaxEvent.user_id == current_user.id)
            .where(TaxEvent.disposed_at >= start_date)
            .where(TaxEvent.disposed_at < end_date)
            .order_by(TaxEvent.disposed_at)
        )
        tax_events = result.scalars().all()

        if not tax_events:
            raise HTTPException(
                status_code=404,
                detail=f"No tax events found for tax year {year}",
            )

        # Build IRS Form 8949 CSV
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)

        # Header
        writer.writerow(["IRS Form 8949 — Sales and Other Dispositions of Capital Assets"])
        writer.writerow([f"Tax Year: {year}"])
        writer.writerow([])

        # Part I: Short-Term Capital Gains (held ≤ 1 year)
        writer.writerow(["PART I: Short-Term Capital Gains and Losses"])
        writer.writerow([
            "Description", "Date Acquired", "Date Sold",
            "Proceeds", "Cost Basis", "Gain/Loss",
            "Holding Period",
        ])
        short_term_total = Decimal("0")
        for event in tax_events:
            if not event.is_short_term:
                continue
            acquired = event.acquired_at.strftime("%Y-%m-%d") if event.acquired_at else "VARIOUS"
            disposed = event.disposed_at.strftime("%Y-%m-%d")
            writer.writerow([
                f"{event.quantity:.8f} {event.token_symbol}",
                acquired,
                disposed,
                f"{event.proceeds_usd:.2f}",
                f"{event.cost_basis_usd:.2f}",
                f"{event.gain_loss_usd:.2f}",
                "Short",
            ])
            short_term_total += event.gain_loss_usd

        writer.writerow([])
        writer.writerow(["Short-Term Total:", "", "", "", "", f"{short_term_total:.2f}", ""])
        writer.writerow([])

        # Part II: Long-Term Capital Gains (held > 1 year)
        writer.writerow(["PART II: Long-Term Capital Gains and Losses"])
        writer.writerow([
            "Description", "Date Acquired", "Date Sold",
            "Proceeds", "Cost Basis", "Gain/Loss",
            "Holding Period",
        ])
        long_term_total = Decimal("0")
        for event in tax_events:
            if event.is_short_term:
                continue
            acquired = event.acquired_at.strftime("%Y-%m-%d") if event.acquired_at else "VARIOUS"
            disposed = event.disposed_at.strftime("%Y-%m-%d")
            writer.writerow([
                f"{event.quantity:.8f} {event.token_symbol}",
                acquired,
                disposed,
                f"{event.proceeds_usd:.2f}",
                f"{event.cost_basis_usd:.2f}",
                f"{event.gain_loss_usd:.2f}",
                "Long",
            ])
            long_term_total += event.gain_loss_usd

        writer.writerow([])
        writer.writerow(["Long-Term Total:", "", "", "", "", f"{long_term_total:.2f}", ""])
        writer.writerow([])

        # Grand total
        writer.writerow(["GRAND TOTAL (Short + Long):", f"{short_term_total + long_term_total:.2f}"])

        csv_content = csv_buffer.getvalue()
        csv_buffer.close()

        filename = f"irs8949_{year}_{datetime.now().strftime('%Y%m%d')}.csv"
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating IRS 8949 report: {str(e)}"
        )


@router.post("/hmrc")
async def generate_hmrc_report(
    tax_year: Optional[int] = Query(
        None, description="UK tax year (e.g., 2025 for 2025-26)",
        alias="tax_year",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate HMRC Capital Gains format (United Kingdom).
    Reports capital gains for UK self-assessment tax filing.
    UK tax year runs April 6 to April 5.
    """
    try:
        year = tax_year or (datetime.now().year - 1)
        # UK tax year: April 6 to April 5
        start_date = datetime(year, 4, 6)
        end_date = datetime(year + 1, 4, 6)

        result = await db.execute(
            select(TaxEvent)
            .where(TaxEvent.user_id == current_user.id)
            .where(TaxEvent.disposed_at >= start_date)
            .where(TaxEvent.disposed_at < end_date)
            .order_by(TaxEvent.disposed_at)
        )
        tax_events = result.scalars().all()

        if not tax_events:
            raise HTTPException(
                status_code=404,
                detail=f"No tax events found for UK tax year {year}-{year+1}",
            )

        # Convert to GBP
        from app.services.exchange_rate import get_usd_rate, format_currency
        gbp_rate = await get_usd_rate("GBP")

        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)

        writer.writerow(["HMRC Capital Gains Tax Report — Crypto Assets"])
        writer.writerow([f"Tax Year: {year}-{year+1} (April 6 to April 5)"])
        writer.writerow([f"Exchange Rate: 1 USD = {gbp_rate:.4f} GBP"])
        writer.writerow([])
        writer.writerow([
            "Asset", "Date Acquired", "Date Disposed",
            "Proceeds (GBP)", "Cost Basis (GBP)", "Gain/Loss (GBP)",
            "Holding Period",
        ])

        total_gbp = Decimal("0")
        for event in tax_events:
            acquired = event.acquired_at.strftime("%Y-%m-%d") if event.acquired_at else "VARIOUS"
            disposed = event.disposed_at.strftime("%Y-%m-%d")
            proceeds_gbp = event.proceeds_usd * gbp_rate
            cost_gbp = event.cost_basis_usd * gbp_rate
            gain_gbp = event.gain_loss_usd * gbp_rate
            period = "Short" if event.is_short_term else "Long"

            writer.writerow([
                event.token_symbol,
                acquired,
                disposed,
                f"{proceeds_gbp:.2f}",
                f"{cost_gbp:.2f}",
                f"{gain_gbp:.2f}",
                period,
            ])
            total_gbp += gain_gbp

        writer.writerow([])
        writer.writerow(["Total Capital Gain/Loss (GBP):", f"{total_gbp:.2f}"])
        writer.writerow(["Notes:"])
        writer.writerow(["1. UK tax-free allowance applies (check current HMRC threshold)"])
        writer.writerow(["2. All values converted from USD to GBP using daily rate"])

        csv_content = csv_buffer.getvalue()
        csv_buffer.close()

        filename = f"hmrc_cgt_{year}-{year+1}_{datetime.now().strftime('%Y%m%d')}.csv"
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating HMRC report: {str(e)}"
        )


@router.post("/ato")
async def generate_ato_report(
    tax_year: Optional[int] = Query(
        None, description="Australian tax year (e.g., 2025 for 2025-26 FY)",
        alias="tax_year",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate ATO Crypto Capital Gains format (Australia).
    Reports capital gains for Australian tax return.
    ATO tax year runs July 1 to June 30.
    """
    try:
        year = tax_year or (datetime.now().year - 1)
        # ATO tax year: July 1 to June 30
        start_date = datetime(year, 7, 1)
        end_date = datetime(year + 1, 7, 1)

        result = await db.execute(
            select(TaxEvent)
            .where(TaxEvent.user_id == current_user.id)
            .where(TaxEvent.disposed_at >= start_date)
            .where(TaxEvent.disposed_at < end_date)
            .order_by(TaxEvent.disposed_at)
        )
        tax_events = result.scalars().all()

        if not tax_events:
            raise HTTPException(
                status_code=404,
                detail=f"No tax events found for ATO tax year {year}-{year+1}",
            )

        # Convert to AUD
        from app.services.exchange_rate import get_usd_rate
        aud_rate = await get_usd_rate("AUD")

        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)

        writer.writerow(["ATO Crypto Capital Gains Report"])
        writer.writerow([f"Tax Year: {year}-{year+1} (July 1 to June 30)"])
        writer.writerow([f"Exchange Rate: 1 USD = {aud_rate:.4f} AUD"])
        writer.writerow([])
        writer.writerow([
            "Crypto Asset", "Date Acquired", "Date Disposed",
            "Proceeds (AUD)", "Cost Base (AUD)", "Capital Gain/Loss (AUD)",
            "CGT Discount Eligible",
        ])

        total_aud = Decimal("0")
        for event in tax_events:
            acquired = event.acquired_at.strftime("%Y-%m-%d") if event.acquired_at else "VARIOUS"
            disposed = event.disposed_at.strftime("%Y-%m-%d")
            proceeds_aud = event.proceeds_usd * aud_rate
            cost_aud = event.cost_basis_usd * aud_rate
            gain_aud = event.gain_loss_usd * aud_rate
            # ATO 50% CGT discount applies for assets held > 12 months
            cgt_discount_eligible = "Yes" if not event.is_short_term else "No"

            writer.writerow([
                event.token_symbol,
                acquired,
                disposed,
                f"{proceeds_aud:.2f}",
                f"{cost_aud:.2f}",
                f"{gain_aud:.2f}",
                cgt_discount_eligible,
            ])
            total_aud += gain_aud

        writer.writerow([])
        writer.writerow(["Total Capital Gain/Loss (AUD):", f"{total_aud:.2f}"])
        writer.writerow(["Notes:"])
        writer.writerow(["1. 50% CGT discount may apply for assets held > 12 months"])
        writer.writerow(["2. All values converted from USD to AUD using daily rate"])

        csv_content = csv_buffer.getvalue()
        csv_buffer.close()

        filename = f"ato_crypto_{year}-{year+1}_{datetime.now().strftime('%Y%m%d')}.csv"
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating ATO report: {str(e)}"
        )
