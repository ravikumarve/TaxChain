"""
Tests for transactions router endpoints.
Uses app.dependency_overrides for proper FastAPI test DI.

Patterns in this router:
- result.scalar()      → single count value
- result.scalars().all() → list of transactions
- result.first()       → summary row
"""
import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, date
from fastapi import FastAPI

from app.routers.transactions import router
from app.services.auth_service import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.models.wallet import Wallet
from app.constants import ALL_CHAINS

# Create a test app with just the transactions router
test_app = FastAPI()
test_app.include_router(router, prefix="/api/transactions")
client = TestClient(test_app, raise_server_exceptions=False)


@pytest.fixture
def mock_user():
    return User(id=uuid4(), email="test@example.com", plan="pro")


def make_mock_db():
    """Create AsyncSession mock with MagicMock result (sync scalars)."""
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock()
    return mock_db


def override_deps(user, db):
    test_app.dependency_overrides[get_current_user] = lambda: user
    test_app.dependency_overrides[get_db] = lambda: db


def clear_overrides():
    test_app.dependency_overrides = {}


def make_tx(**kwargs):
    """Helper to create a Transaction with defaults."""
    defaults = dict(
        id=uuid4(), tx_hash=f"0x{uuid4().hex[:40]}", chain="eth",
        tx_type="transfer_in", token_symbol="ETH",
        token_address="0x0000000000000000000000000000000000000000",
        quantity=Decimal("1.5"), price_usd=Decimal("2000.0"),
        value_usd=Decimal("3000.0"), fee_usd=Decimal("10.0"),
        timestamp=datetime(2024, 1, 15, 12, 0, 0),
        wallet_id=uuid4(), user_id=uuid4(),
    )
    defaults.update(kwargs)
    return Transaction(**defaults)


# ── List Transactions ─────────────────────────────────────────────────────

def test_list_transactions_success(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)

    # Two db.execute calls: count + data
    txs = [make_tx(), make_tx()]
    results = [MagicMock(), MagicMock()]
    results[0].scalar.return_value = 2          # total_count
    results[1].scalars.return_value.all.return_value = txs  # transaction list
    mock_db.execute.side_effect = results

    response = client.get("/api/transactions/?page=1&limit=50")
    clear_overrides()

    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["total"] == 2
    assert len(data["transactions"]) == 2


def test_list_transactions_with_filters(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)

    txs = [make_tx(chain="eth", tx_type="trade")]
    results = [MagicMock(), MagicMock()]
    results[0].scalar.return_value = 1
    results[1].scalars.return_value.all.return_value = txs
    mock_db.execute.side_effect = results

    response = client.get(
        "/api/transactions/?chain=eth&tx_type=trade&page=1&limit=50"
    )
    clear_overrides()

    assert response.status_code == 200
    assert response.json()["pagination"]["total"] == 1


def test_list_transactions_pagination_limits(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)

    results = [MagicMock(), MagicMock()]
    results[0].scalar.return_value = 100
    results[1].scalars.return_value.all.return_value = []
    mock_db.execute.side_effect = results

    # limit=5 is below min (1) → FastAPI clamps to 1? No, it validates ge=1
    # limit=0 fails validation
    response = client.get("/api/transactions/?page=1&limit=50")
    clear_overrides()

    assert response.status_code == 200


def test_list_transactions_date_filters(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)

    results = [MagicMock(), MagicMock()]
    results[0].scalar.return_value = 1
    results[1].scalars.return_value.all.return_value = [make_tx()]
    mock_db.execute.side_effect = results

    response = client.get(
        "/api/transactions/?start_date=2024-01-01&end_date=2024-12-31&page=1&limit=50"
    )
    clear_overrides()

    assert response.status_code == 200


def test_list_transactions_error_handling(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)

    mock_db.execute.side_effect = Exception("DB error")

    response = client.get("/api/transactions/?page=1&limit=50")
    clear_overrides()

    assert response.status_code == 500


# ── Transaction Summary ───────────────────────────────────────────────────

def test_get_transaction_summary_success(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)

    mock_db.execute.return_value.first.return_value = MagicMock(
        total_transactions=10,
        chains_count=2,
        types_count=3,
        total_value_usd=Decimal("50000.0"),
        total_fee_usd=Decimal("100.0"),
        first_transaction=datetime(2023, 1, 1),
        last_transaction=datetime(2024, 1, 1),
    )

    response = client.get("/api/transactions/summary")
    clear_overrides()

    assert response.status_code == 200
    data = response.json()
    assert data["total_transactions"] == 10
    assert data["total_value_usd"] == 50000.0


def test_get_transaction_summary_empty(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)

    mock_db.execute.return_value.first.return_value = None

    response = client.get("/api/transactions/summary")
    clear_overrides()

    assert response.status_code == 200
    data = response.json()
    assert data["total_transactions"] == 0


def test_get_transaction_summary_with_filters(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)

    mock_db.execute.return_value.first.return_value = MagicMock(
        total_transactions=5, chains_count=1, types_count=1,
        total_value_usd=Decimal("10000.0"), total_fee_usd=Decimal("50.0"),
        first_transaction=datetime(2024, 6, 1),
        last_transaction=datetime(2024, 12, 1),
    )

    response = client.get(
        "/api/transactions/summary?chain=eth&tx_type=trade"
    )
    clear_overrides()

    assert response.status_code == 200
    assert response.json()["total_transactions"] == 5


def test_get_transaction_summary_error_handling(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)

    mock_db.execute.side_effect = Exception("DB error")

    response = client.get("/api/transactions/summary")
    clear_overrides()

    assert response.status_code == 500


# ── Invalid Input Tests ──────────────────────────────────────────────────

def test_list_transactions_invalid_chain(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)

    response = client.get("/api/transactions/?chain=invalid")
    clear_overrides()

    assert response.status_code == 400
    assert "Invalid chain" in response.json()["detail"]


def test_get_summary_invalid_chain(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)

    response = client.get("/api/transactions/summary?chain=invalid")
    clear_overrides()

    assert response.status_code == 400
    assert "Invalid chain" in response.json()["detail"]
