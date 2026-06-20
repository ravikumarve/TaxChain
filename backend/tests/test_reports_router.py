"""
Tests for reports router endpoints.
Uses app.dependency_overrides for proper FastAPI test DI.

Patterns in this router:
- result.scalars().all() → list of transactions/tax events
- db.get(Model, id)      → single object lookup
"""
import pytest
import io
import csv
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import FastAPI

from app.routers.reports import router
from app.services.auth_service import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.models.tax_event import TaxEvent

test_app = FastAPI()
test_app.include_router(router, prefix="/api/reports")
client = TestClient(test_app, raise_server_exceptions=False)


@pytest.fixture
def mock_user():
    return User(id=uuid4(), email="test@example.com", plan="pro", financial_year_start="04-01", cost_basis_method="fifo")


@pytest.fixture
def mock_free_user():
    return User(id=uuid4(), email="free@example.com", plan="free", financial_year_start="04-01", cost_basis_method="fifo")


@pytest.fixture
def mock_tx():
    return Transaction(
        id=uuid4(), tx_hash=f"0x{uuid4().hex[:40]}", chain="eth",
        tx_type="trade", token_symbol="ETH",
        token_address="0x0000000000000000000000000000000000000000",
        quantity=Decimal("1.5"), price_usd=Decimal("2000.0"),
        value_usd=Decimal("3000.0"), fee_usd=Decimal("10.0"),
        timestamp=datetime(2024, 6, 15, 12, 0, 0),
        wallet_id=uuid4(), user_id=uuid4(),
    )


def make_mock_db():
    """Create AsyncSession mock with MagicMock result (sync scalars)."""
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock()
    mock_db.get = AsyncMock()
    mock_db.commit = AsyncMock()
    return mock_db


def override_deps(user, db):
    test_app.dependency_overrides[get_current_user] = lambda: user
    test_app.dependency_overrides[get_db] = lambda: db


def clear_overrides():
    test_app.dependency_overrides = {}


# ── Tax Summary ──────────────────────────────────────────────────────────

def test_get_tax_summary_success(mock_user, mock_tx):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)
    mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_tx]

    with patch("app.routers.reports.calculate_with_method") as mock_calc:
        mock_calc.return_value = [
            TaxEvent(id=uuid4(), user_id=mock_user.id, token_symbol="ETH",
                     quantity=Decimal("1.0"), proceeds_usd=Decimal("2000.0"),
                     cost_basis_usd=Decimal("1000.0"), gain_loss_usd=Decimal("1000.0"),
                     is_short_term=True, disposed_at=datetime(2024, 6, 15),
                     acquired_at=datetime(2024, 1, 15), financial_year="2024-25")
        ]

        response = client.get("/api/reports/tax/summary?financial_year=2024-25")
        clear_overrides()

        assert response.status_code == 200
        data = response.json()
        assert data["financial_year"] == "2024-25"
        assert data["total_gain_loss_usd"] == 1000.0


def test_get_tax_summary_no_transactions(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    response = client.get("/api/reports/tax/summary?financial_year=2024-25")
    clear_overrides()

    assert response.status_code == 200
    assert response.json()["total_gain_loss_usd"] == 0.0


def test_get_tax_summary_error_handling(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)
    mock_db.execute.side_effect = Exception("DB connection failed")

    response = client.get("/api/reports/tax/summary?financial_year=2024-25")
    clear_overrides()

    assert response.status_code == 500


# ── ITR Report ───────────────────────────────────────────────────────────

def test_generate_itr_report_success(mock_user, mock_tx):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)

    tax_event = TaxEvent(
        id=uuid4(), user_id=mock_user.id, token_symbol="ETH",
        quantity=Decimal("1.0"), proceeds_usd=Decimal("2000.0"),
        cost_basis_usd=Decimal("1000.0"), gain_loss_usd=Decimal("1000.0"),
        is_short_term=True, disposed_at=datetime(2024, 6, 15),
        acquired_at=datetime(2024, 1, 15), financial_year="2024-25",
        sale_tx_id=mock_tx.id,
    )
    mock_db.execute.return_value.scalars.return_value.all.return_value = [tax_event]
    mock_db.get.return_value = mock_tx

    with patch("app.routers.reports.get_usd_to_inr_exchange_rate", new_callable=AsyncMock) as mock_rate:
        mock_rate.return_value = Decimal("83.50")

        response = client.post("/api/reports/itr?financial_year=2024-25")
        clear_overrides()

        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "itr_schedule_vda" in response.headers["content-disposition"]
        content = response.content.decode("utf-8")
        assert "Description of Digital Asset" in content


def test_generate_itr_report_no_tax_events(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    response = client.post("/api/reports/itr?financial_year=2024-25")
    clear_overrides()

    assert response.status_code == 404
    assert "No tax events found" in response.json()["detail"]


def test_generate_itr_report_free_plan_user(mock_free_user):
    mock_db = make_mock_db()
    override_deps(mock_free_user, mock_db)

    response = client.post("/api/reports/itr?financial_year=2024-25")
    clear_overrides()

    assert response.status_code == 403
    assert "Pro plan" in response.json()["detail"]


# ── CSV Report ────────────────────────────────────────────────────────────

def test_generate_csv_report(mock_user, mock_tx):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)
    mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_tx]
    mock_db.get.return_value = mock_tx

    with patch("app.routers.reports.calculate_with_method") as mock_calc:
        tax_event = TaxEvent(
            id=uuid4(), user_id=mock_user.id, token_symbol="ETH",
            quantity=Decimal("1.0"), proceeds_usd=Decimal("2000.0"),
            cost_basis_usd=Decimal("1000.0"), gain_loss_usd=Decimal("1000.0"),
            is_short_term=True, disposed_at=datetime(2024, 6, 15),
            acquired_at=datetime(2024, 1, 15), financial_year="2024-25",
            sale_tx_id=mock_tx.id,
        )
        mock_calc.return_value = [tax_event]

        response = client.post("/api/reports/csv?financial_year=2024-25")
        clear_overrides()

        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]


# ── Financial Year Utility Tests (pure, no DI) ──────────────────────────

def test_get_financial_year_range_valid():
    from app.routers.reports import get_financial_year_range
    start, end = get_financial_year_range("2024-25", "04-01")
    assert start == datetime(2024, 4, 1)
    # end_date is exclusive: next FY start
    assert end == datetime(2025, 4, 1)


def test_get_financial_year_range_invalid_format():
    from app.routers.reports import get_financial_year_range
    with pytest.raises(HTTPException) as exc:
        get_financial_year_range("invalid", "04-01")
    assert exc.value.status_code == 400


def test_calculate_financial_year_india():
    from app.routers.reports import calculate_financial_year
    assert calculate_financial_year(datetime(2024, 4, 1), "04-01") == "2024-25"
    assert calculate_financial_year(datetime(2024, 3, 31), "04-01") == "2023-24"


def test_calculate_financial_year_us():
    from app.routers.reports import calculate_financial_year
    assert calculate_financial_year(datetime(2024, 1, 1), "01-01") == "2024-25"
    assert calculate_financial_year(datetime(2024, 12, 31), "01-01") == "2024-25"


def test_validate_itr_financial_year_valid():
    from app.routers.reports import validate_itr_financial_year
    assert validate_itr_financial_year("2024-25") is True
    assert validate_itr_financial_year("2023-24") is True


def test_validate_itr_financial_year_invalid():
    from app.routers.reports import validate_itr_financial_year
    assert validate_itr_financial_year("2024") is False
    assert validate_itr_financial_year("invalid") is False
    assert validate_itr_financial_year("") is False
