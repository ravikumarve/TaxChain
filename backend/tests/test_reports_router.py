import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from decimal import Decimal

from app.routers.reports import router
from app.models.user import User
from app.models.transaction import Transaction
from app.models.tax_event import TaxEvent

# Create a test app with just the reports router
from fastapi import FastAPI

test_app = FastAPI()
test_app.include_router(router, prefix="/api/reports")
client = TestClient(test_app)


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    return User(
        id=uuid4(), email="test@example.com", plan="pro", financial_year_start="04-01"
    )


@pytest.fixture
def mock_user_us():
    """Create a mock user with US financial year"""
    return User(
        id=uuid4(), email="us@example.com", plan="pro", financial_year_start="01-01"
    )


@pytest.fixture
def mock_transaction():
    """Create a mock transaction"""
    return Transaction(
        id=uuid4(),
        tx_hash=f"0x{uuid4().hex[:40]}",
        chain="eth",
        tx_type="transfer_in",
        token_symbol="ETH",
        token_address="0x0000000000000000000000000000000000000000",
        quantity=Decimal("1.5"),
        price_usd=Decimal("2000.0"),
        value_usd=Decimal("3000.0"),
        fee_usd=Decimal("10.0"),
        timestamp=datetime(2024, 1, 15, 12, 0, 0),
        wallet_id=uuid4(),
        user_id=uuid4(),
    )


@pytest.fixture
def mock_tax_event():
    """Create a mock tax event"""
    return TaxEvent(
        id=uuid4(),
        user_id=uuid4(),
        token_symbol="ETH",
        quantity=Decimal("1.0"),
        proceeds_usd=Decimal("2000.0"),
        cost_basis_usd=Decimal("1000.0"),
        gain_loss_usd=Decimal("1000.0"),
        is_short_term=True,
        disposed_at=datetime(2024, 6, 15),
        acquired_at=datetime(2024, 1, 15),
        financial_year="2024-25",
        sale_tx_id=uuid4(),
    )


@pytest.mark.asyncio
async def test_get_tax_summary_success(mock_user, mock_transaction):
    """Test successful tax summary retrieval"""
    with (
        patch("app.routers.reports.get_db") as mock_get_db,
        patch("app.routers.reports.get_current_user") as mock_get_user,
        patch("app.routers.reports.calculate_fifo") as mock_calculate_fifo,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock transaction query
        mock_db.execute.return_value.scalars.return_value.all.return_value = [
            mock_transaction
        ]

        # Mock FIFO calculation
        mock_tax_events = [
            TaxEvent(
                id=uuid4(),
                user_id=mock_user.id,
                token_symbol="ETH",
                quantity=Decimal("1.0"),
                proceeds_usd=Decimal("2000.0"),
                cost_basis_usd=Decimal("1000.0"),
                gain_loss_usd=Decimal("1000.0"),
                is_short_term=True,
                disposed_at=datetime(2024, 6, 15),
                acquired_at=datetime(2024, 1, 15),
                financial_year="2024-25",
            )
        ]
        mock_calculate_fifo.return_value = mock_tax_events

        response = client.get("/api/reports/tax/summary?financial_year=2024-25")

        assert response.status_code == 200
        assert response.json()["financial_year"] == "2024-25"
        assert response.json()["total_gain_loss_usd"] == "1000.0"
        assert response.json()["short_term_gain_loss_usd"] == "1000.0"
        assert response.json()["long_term_gain_loss_usd"] == "0.0"
        assert len(response.json()["token_breakdown"]) == 1
        assert response.json()["token_breakdown"][0]["token_symbol"] == "ETH"


@pytest.mark.asyncio
async def test_get_tax_summary_default_financial_year(mock_user, mock_transaction):
    """Test tax summary with default financial year"""
    with (
        patch("app.routers.reports.get_db") as mock_get_db,
        patch("app.routers.reports.get_current_user") as mock_get_user,
        patch("app.routers.reports.calculate_fifo") as mock_calculate_fifo,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        mock_db.execute.return_value.scalars.return_value.all.return_value = [
            mock_transaction
        ]
        mock_calculate_fifo.return_value = []

        response = client.get("/api/reports/tax/summary")

        assert response.status_code == 200
        # Should default to current financial year
        assert "financial_year" in response.json()


@pytest.mark.asyncio
async def test_get_tax_summary_no_transactions(mock_user):
    """Test tax summary with no transactions"""
    with (
        patch("app.routers.reports.get_db") as mock_get_db,
        patch("app.routers.reports.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock empty transaction query
        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        response = client.get("/api/reports/tax/summary?financial_year=2024-25")

        assert response.status_code == 200
        assert response.json()["financial_year"] == "2024-25"
        assert response.json()["total_gain_loss_usd"] == "0.0"
        assert response.json()["transaction_count"] == 0
        assert (
            response.json()["message"]
            == "No transactions found for this financial year"
        )


@pytest.mark.asyncio
async def test_get_tax_summary_multiple_tokens(mock_user):
    """Test tax summary with multiple tokens"""
    with (
        patch("app.routers.reports.get_db") as mock_get_db,
        patch("app.routers.reports.get_current_user") as mock_get_user,
        patch("app.routers.reports.calculate_fifo") as mock_calculate_fifo,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock transactions for multiple tokens
        eth_tx = mock_transaction
        btc_tx = Transaction(
            id=uuid4(),
            tx_hash=f"0x{uuid4().hex[:40]}",
            chain="eth",
            tx_type="transfer_in",
            token_symbol="BTC",
            token_address="0x0000000000000000000000000000000000000001",
            quantity=Decimal("0.1"),
            price_usd=Decimal("30000.0"),
            value_usd=Decimal("3000.0"),
            fee_usd=Decimal("15.0"),
            timestamp=datetime(2024, 2, 15, 12, 0, 0),
            wallet_id=uuid4(),
            user_id=mock_user.id,
        )
        mock_db.execute.return_value.scalars.return_value.all.return_value = [
            eth_tx,
            btc_tx,
        ]

        # Mock FIFO calculations
        eth_events = [
            TaxEvent(
                id=uuid4(),
                user_id=mock_user.id,
                token_symbol="ETH",
                quantity=Decimal("1.0"),
                proceeds_usd=Decimal("2000.0"),
                cost_basis_usd=Decimal("1000.0"),
                gain_loss_usd=Decimal("1000.0"),
                is_short_term=True,
            )
        ]
        btc_events = [
            TaxEvent(
                id=uuid4(),
                user_id=mock_user.id,
                token_symbol="BTC",
                quantity=Decimal("0.1"),
                proceeds_usd=Decimal("4000.0"),
                cost_basis_usd=Decimal("3000.0"),
                gain_loss_usd=Decimal("1000.0"),
                is_short_term=False,
            )
        ]

        def mock_fifo_side_effect(user_id, token_symbol, transactions):
            if token_symbol == "ETH":
                return eth_events
            elif token_symbol == "BTC":
                return btc_events
            return []

        mock_calculate_fifo.side_effect = mock_fifo_side_effect

        response = client.get("/api/reports/tax/summary?financial_year=2024-25")

        assert response.status_code == 200
        assert len(response.json()["token_breakdown"]) == 2

        # Find ETH and BTC breakdowns
        eth_breakdown = next(
            b for b in response.json()["token_breakdown"] if b["token_symbol"] == "ETH"
        )
        btc_breakdown = next(
            b for b in response.json()["token_breakdown"] if b["token_symbol"] == "BTC"
        )

        assert eth_breakdown["total_gain_loss_usd"] == "1000.0"
        assert eth_breakdown["short_term_gain_loss_usd"] == "1000.0"
        assert eth_breakdown["long_term_gain_loss_usd"] == "0.0"

        assert btc_breakdown["total_gain_loss_usd"] == "1000.0"
        assert btc_breakdown["short_term_gain_loss_usd"] == "0.0"
        assert btc_breakdown["long_term_gain_loss_usd"] == "1000.0"


@pytest.mark.asyncio
async def test_get_tax_summary_invalid_financial_year_format(mock_user):
    """Test tax summary with invalid financial year format"""
    with patch("app.routers.reports.get_current_user") as mock_get_user:
        mock_get_user.return_value = mock_user

        response = client.get("/api/reports/tax/summary?financial_year=invalid")

        assert response.status_code == 400
        assert "Invalid financial year format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_tax_summary_us_financial_year(mock_user_us):
    """Test tax summary with US financial year (Jan 1 start)"""
    with (
        patch("app.routers.reports.get_db") as mock_get_db,
        patch("app.routers.reports.get_current_user") as mock_get_user,
        patch("app.routers.reports.calculate_fifo") as mock_calculate_fifo,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user_us

        # Mock transaction in US financial year 2024 (Jan 1 - Dec 31)
        tx_in_2024 = Transaction(
            id=uuid4(),
            tx_hash=f"0x{uuid4().hex[:40]}",
            chain="eth",
            tx_type="transfer_in",
            token_symbol="ETH",
            quantity=Decimal("1.0"),
            price_usd=Decimal("1000.0"),
            timestamp=datetime(2024, 6, 15),  # Within US FY 2024
            wallet_id=uuid4(),
            user_id=mock_user_us.id,
        )
        mock_db.execute.return_value.scalars.return_value.all.return_value = [
            tx_in_2024
        ]
        mock_calculate_fifo.return_value = []

        response = client.get("/api/reports/tax/summary?financial_year=2024")

        assert response.status_code == 200
        assert response.json()["financial_year"] == "2024"


@pytest.mark.asyncio
async def test_get_tax_summary_error_handling(mock_user):
    """Test tax summary error handling"""
    with (
        patch("app.routers.reports.get_db") as mock_get_db,
        patch("app.routers.reports.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock database error
        mock_db.execute.side_effect = Exception("Database connection failed")

        response = client.get("/api/reports/tax/summary?financial_year=2024-25")

        assert response.status_code == 500
        assert "Error calculating tax summary" in response.json()["detail"]


@pytest.mark.asyncio
async def test_generate_csv_report_not_implemented():
    """Test CSV report endpoint (not implemented)"""
    response = client.post("/api/reports/csv")
    assert response.status_code == 200
    assert response.json()["message"] == "CSV report endpoint - TODO"


@pytest.mark.asyncio
async def test_generate_pdf_report_success(mock_user, mock_transaction):
    """Test PDF report generation success"""
    with (
        patch("app.routers.reports.get_db") as mock_get_db,
        patch("app.routers.reports.get_current_user") as mock_get_user,
        patch("app.routers.reports.calculate_fifo") as mock_calculate_fifo,
        patch("app.routers.reports.SimpleDocTemplate") as mock_doc_template,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock transaction query
        mock_db.execute.return_value.scalars.return_value.all.return_value = [
            mock_transaction
        ]

        # Mock FIFO calculation
        mock_tax_events = [
            TaxEvent(
                id=uuid4(),
                user_id=mock_user.id,
                token_symbol="ETH",
                quantity=Decimal("1.0"),
                proceeds_usd=Decimal("2000.0"),
                cost_basis_usd=Decimal("1000.0"),
                gain_loss_usd=Decimal("1000.0"),
                is_short_term=True,
                disposed_at=datetime(2024, 6, 15),
                acquired_at=datetime(2024, 1, 15),
                financial_year="2024-25",
                sale_tx_id=uuid4(),
            )
        ]
        mock_calculate_fifo.return_value = mock_tax_events

        # Mock PDF document
        mock_doc_instance = AsyncMock()
        mock_doc_template.return_value = mock_doc_instance

        response = client.post("/api/reports/pdf?financial_year=2024-25")

        # Should return PDF response
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]
        assert "taxchain_tax_report_2024-25" in response.headers["content-disposition"]


@pytest.mark.asyncio
async def test_generate_pdf_report_no_transactions(mock_user):
    """Test PDF report with no transactions"""
    with (
        patch("app.routers.reports.get_db") as mock_get_db,
        patch("app.routers.reports.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock empty transaction query
        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        response = client.post("/api/reports/pdf?financial_year=2024-25")

        assert response.status_code == 404
        assert "No transactions found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_generate_pdf_report_default_financial_year(mock_user, mock_transaction):
    """Test PDF report with default financial year"""
    with (
        patch("app.routers.reports.get_db") as mock_get_db,
        patch("app.routers.reports.get_current_user") as mock_get_user,
        patch("app.routers.reports.calculate_fifo") as mock_calculate_fifo,
        patch("app.routers.reports.SimpleDocTemplate") as mock_doc_template,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        mock_db.execute.return_value.scalars.return_value.all.return_value = [
            mock_transaction
        ]
        mock_calculate_fifo.return_value = []

        # Mock PDF document
        mock_doc_instance = AsyncMock()
        mock_doc_template.return_value = mock_doc_instance

        response = client.post("/api/reports/pdf")

        # Should still succeed with default financial year
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"


@pytest.mark.asyncio
async def test_generate_pdf_report_reportlab_not_installed(mock_user, mock_transaction):
    """Test PDF report when ReportLab is not available"""
    with (
        patch("app.routers.reports.get_db") as mock_get_db,
        patch("app.routers.reports.get_current_user") as mock_get_user,
        patch("app.routers.reports.calculate_fifo") as mock_calculate_fifo,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        mock_db.execute.return_value.scalars.return_value.all.return_value = [
            mock_transaction
        ]
        mock_calculate_fifo.return_value = []

        # Mock ImportError when trying to import ReportLab
        with patch("app.routers.reports.SimpleDocTemplate", side_effect=ImportError):
            response = client.post("/api/reports/pdf?financial_year=2024-25")

            assert response.status_code == 500
            assert "ReportLab library" in response.json()["detail"]


@pytest.mark.asyncio
async def test_generate_itr_report_success(mock_user, mock_tax_event):
    """Test ITR report generation success"""
    with (
        patch("app.routers.reports.get_db") as mock_get_db,
        patch("app.routers.reports.get_current_user") as mock_get_user,
        patch("app.routers.reports.get_usd_to_inr_exchange_rate") as mock_exchange_rate,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        mock_exchange_rate.return_value = Decimal("83.50")

        # Mock tax event query
        mock_db.execute.return_value.scalars.return_value.all.return_value = [
            mock_tax_event
        ]

        # Mock transaction lookup
        mock_transaction = Transaction(
            id=mock_tax_event.sale_tx_id,
            tx_hash="0x1234567890abcdef",
            chain="eth",
            tx_type="trade",
            token_symbol="ETH",
            timestamp=datetime(2024, 6, 15),
            wallet_id=uuid4(),
            user_id=mock_user.id,
        )
        mock_db.get.return_value = mock_transaction

        response = client.post("/api/reports/itr?financial_year=2024-25")

        # Should return CSV response
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv"
        assert "attachment" in response.headers["content-disposition"]
        assert "itr_schedule_vda_2024-25" in response.headers["content-disposition"]

        # Should contain ITR VDA headers
        content = response.content.decode("utf-8")
        assert "Description of Digital Asset" in content
        assert "Cost of Acquisition (INR)" in content
        assert "Capital Gains (INR)" in content


@pytest.mark.asyncio
async def test_generate_itr_report_no_tax_events(mock_user):
    """Test ITR report with no tax events"""
    with (
        patch("app.routers.reports.get_db") as mock_get_db,
        patch("app.routers.reports.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock empty tax event query
        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        response = client.post("/api/reports/itr?financial_year=2024-25")

        assert response.status_code == 404
        assert "No tax events found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_generate_itr_report_free_plan_user():
    """Test ITR report with free plan user (should be denied)"""
    with patch("app.routers.reports.get_current_user") as mock_get_user:
        free_user = User(
            id=uuid4(),
            email="free@example.com",
            plan="free",
            financial_year_start="04-01",
        )
        mock_get_user.return_value = free_user

        response = client.post("/api/reports/itr?financial_year=2024-25")

        assert response.status_code == 403
        assert "Pro plan" in response.json()["detail"]
        assert "upgrade" in response.json()["detail"]


@pytest.mark.asyncio
async def test_generate_itr_report_invalid_financial_year_format(mock_user):
    """Test ITR report with invalid financial year format"""
    with patch("app.routers.reports.get_current_user") as mock_get_user:
        mock_get_user.return_value = mock_user

        response = client.post("/api/reports/itr?financial_year=invalid-format")

        assert response.status_code == 400
        assert "Invalid financial year format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_generate_itr_report_default_financial_year(mock_user, mock_tax_event):
    """Test ITR report with default financial year"""
    with (
        patch("app.routers.reports.get_db") as mock_get_db,
        patch("app.routers.reports.get_current_user") as mock_get_user,
        patch("app.routers.reports.get_usd_to_inr_exchange_rate") as mock_exchange_rate,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        mock_exchange_rate.return_value = Decimal("83.50")

        # Mock tax event query
        mock_db.execute.return_value.scalars.return_value.all.return_value = [
            mock_tax_event
        ]

        # Mock transaction lookup
        mock_transaction = Transaction(
            id=mock_tax_event.sale_tx_id,
            tx_hash="0x1234567890abcdef",
            chain="eth",
            tx_type="trade",
            token_symbol="ETH",
            timestamp=datetime(2024, 6, 15),
            wallet_id=uuid4(),
            user_id=mock_user.id,
        )
        mock_db.get.return_value = mock_transaction

        response = client.post("/api/reports/itr")

        # Should return CSV response with default financial year
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv"
        assert "attachment" in response.headers["content-disposition"]


def test_get_financial_year_range_valid():
    """Test valid financial year range calculation"""
    from app.routers.reports import get_financial_year_range

    start_date, end_date = get_financial_year_range("2024-25", "04-01")

    assert start_date == datetime(2024, 4, 1)
    assert end_date == datetime(2025, 3, 31, 23, 59, 59, 999999)


def test_get_financial_year_range_invalid_format():
    """Test invalid financial year format handling"""
    from app.routers.reports import get_financial_year_range

    with pytest.raises(HTTPException) as exc_info:
        get_financial_year_range("invalid", "04-01")

    assert exc_info.value.status_code == 400
    assert "Invalid financial year format" in exc_info.value.detail


def test_calculate_financial_year_india():
    """Test financial year calculation for India (Apr 1 start)"""
    from app.routers.reports import calculate_financial_year

    # Test dates in different financial years
    assert calculate_financial_year(datetime(2024, 4, 1), "04-01") == "2024-25"
    assert calculate_financial_year(datetime(2024, 3, 31), "04-01") == "2023-24"
    assert calculate_financial_year(datetime(2024, 12, 31), "04-01") == "2024-25"
    assert calculate_financial_year(datetime(2025, 1, 1), "04-01") == "2024-25"


def test_calculate_financial_year_us():
    """Test financial year calculation for US (Jan 1 start)"""
    from app.routers.reports import calculate_financial_year

    assert calculate_financial_year(datetime(2024, 1, 1), "01-01") == "2024-25"
    assert calculate_financial_year(datetime(2024, 12, 31), "01-01") == "2024-25"
    assert calculate_financial_year(datetime(2023, 12, 31), "01-01") == "2023-24"


def test_calculate_financial_year_edge_cases():
    """Test financial year calculation edge cases"""
    from app.routers.reports import calculate_financial_year

    # Test invalid financial year start format
    result = calculate_financial_year(datetime(2024, 6, 15), "invalid")
    assert result == "2024-25"  # Should fall back to default behavior


def test_validate_itr_financial_year_valid():
    """Test valid ITR financial year validation"""
    from app.routers.reports import validate_itr_financial_year

    assert validate_itr_financial_year("2024-25") == True
    assert validate_itr_financial_year("2023-24") == True
    assert validate_itr_financial_year("2025-26") == True


def test_validate_itr_financial_year_invalid():
    """Test invalid ITR financial year validation"""
    from app.routers.reports import validate_itr_financial_year

    assert validate_itr_financial_year("2024") == False  # Too short
    assert validate_itr_financial_year("2024-2025") == False  # Too long
    assert validate_itr_financial_year("invalid") == False  # Not a number
    assert validate_itr_financial_year("2024-24") == False  # Wrong suffix
    assert validate_itr_financial_year("2024-26") == False  # Wrong suffix
    assert validate_itr_financial_year("") == False  # Empty
    assert validate_itr_financial_year("2024-25-") == False  # Extra dash


def test_get_usd_to_inr_exchange_rate():
    """Test USD to INR exchange rate function"""
    from app.routers.reports import get_usd_to_inr_exchange_rate
    import asyncio

    # Test that it returns a Decimal value
    rate = asyncio.run(get_usd_to_inr_exchange_rate())
    assert isinstance(rate, Decimal)
    assert rate > Decimal("0")


@pytest.mark.asyncio
async def test_get_tax_summary_mixed_short_long_term(mock_user):
    """Test tax summary with mixed short-term and long-term gains"""
    with (
        patch("app.routers.reports.get_db") as mock_get_db,
        patch("app.routers.reports.get_current_user") as mock_get_user,
        patch("app.routers.reports.calculate_fifo") as mock_calculate_fifo,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        mock_db.execute.return_value.scalars.return_value.all.return_value = [
            mock_transaction
        ]

        # Mock mixed short-term and long-term tax events
        mock_tax_events = [
            TaxEvent(
                id=uuid4(),
                user_id=mock_user.id,
                token_symbol="ETH",
                quantity=Decimal("0.5"),
                proceeds_usd=Decimal("1500.0"),
                cost_basis_usd=Decimal("500.0"),
                gain_loss_usd=Decimal("1000.0"),
                is_short_term=True,
            ),
            TaxEvent(
                id=uuid4(),
                user_id=mock_user.id,
                token_symbol="ETH",
                quantity=Decimal("0.5"),
                proceeds_usd=Decimal("1000.0"),
                cost_basis_usd=Decimal("300.0"),
                gain_loss_usd=Decimal("700.0"),
                is_short_term=False,
            ),
        ]
        mock_calculate_fifo.return_value = mock_tax_events

        response = client.get("/api/reports/tax/summary?financial_year=2024-25")

        assert response.status_code == 200
        assert response.json()["total_gain_loss_usd"] == "1700.0"  # 1000 + 700
        assert response.json()["short_term_gain_loss_usd"] == "1000.0"
        assert response.json()["long_term_gain_loss_usd"] == "700.0"
        assert response.json()["tax_event_count"] == 2


@pytest.mark.asyncio
async def test_get_tax_summary_loss_scenario(mock_user):
    """Test tax summary with loss scenario"""
    with (
        patch("app.routers.reports.get_db") as mock_get_db,
        patch("app.routers.reports.get_current_user") as mock_get_user,
        patch("app.routers.reports.calculate_fifo") as mock_calculate_fifo,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        mock_db.execute.return_value.scalars.return_value.all.return_value = [
            mock_transaction
        ]

        # Mock tax event with loss
        mock_tax_events = [
            TaxEvent(
                id=uuid4(),
                user_id=mock_user.id,
                token_symbol="ETH",
                quantity=Decimal("1.0"),
                proceeds_usd=Decimal("800.0"),
                cost_basis_usd=Decimal("1000.0"),
                gain_loss_usd=Decimal("-200.0"),  # Loss
                is_short_term=True,
            )
        ]
        mock_calculate_fifo.return_value = mock_tax_events

        response = client.get("/api/reports/tax/summary?financial_year=2024-25")

        assert response.status_code == 200
        assert response.json()["total_gain_loss_usd"] == "-200.0"
        assert response.json()["short_term_gain_loss_usd"] == "-200.0"
        assert response.json()["long_term_gain_loss_usd"] == "0.0"
