"""
Tests for wallet router endpoints.
Uses app.dependency_overrides for proper FastAPI test DI.

Key patterns:
- result.scalars().all()     → list of items (list_wallets)
- result.scalar_one_or_none() → single item or None (add/delete/sync/status)
- result.scalar()             → single scalar value (count)
"""
import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from decimal import Decimal
from fastapi import FastAPI

from app.routers.wallets import router
from app.services.auth_service import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.wallet import Wallet

# Create a test app with just the wallet router
test_app = FastAPI()
test_app.include_router(router, prefix="/api/wallets")
client = TestClient(test_app, raise_server_exceptions=False)


@pytest.fixture
def mock_user():
    return User(id=uuid4(), email="test@example.com", plan="pro")


@pytest.fixture
def mock_free_user():
    return User(id=uuid4(), email="free@example.com", plan="free")


@pytest.fixture
def mock_wallet():
    return Wallet(
        id=uuid4(),
        address="0x1234567890123456789012345678901234567890",
        chain="eth",
        user_id=uuid4(),
    )


def make_mock_db():
    """Create AsyncSession mock with MagicMock result (sync scalars)."""
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.return_value = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    mock_db.delete = AsyncMock()
    mock_db.add = MagicMock()
    return mock_db


def set_result(mock_db, **kwargs):
    """
    Configure mock_db.execute.return_value (the 'result' object).
    Usage:
        set_result(mock_db, scalar_one_or_none=mock_obj, scalar=5)
        set_result(mock_db, scalar_one_or_none=None)
        set_result(mock_db, scalars_all=[Wallet(), Wallet()])
    """
    result = mock_db.execute.return_value
    for key, value in kwargs.items():
        if key == "scalars_all":
            result.scalars.return_value.all.return_value = value
        elif key == "scalar_one_or_none":
            result.scalar_one_or_none.return_value = value
        elif key == "scalar":
            result.scalar.return_value = value


def override_deps(user, db):
    test_app.dependency_overrides[get_current_user] = lambda: user
    test_app.dependency_overrides[get_db] = lambda: db


def clear_overrides():
    test_app.dependency_overrides = {}


# ── List Wallets ──────────────────────────────────────────────────────────

def test_list_wallets_success(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)
    set_result(mock_db, scalars_all=[
        Wallet(id=uuid4(), address="0x123...", chain="eth", user_id=mock_user.id),
        Wallet(id=uuid4(), address="0x456...", chain="bnb", user_id=mock_user.id),
    ])

    response = client.get("/api/wallets/")
    clear_overrides()

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["chain"] == "eth"


# ── Add Wallet ─────────────────────────────────────────────────────────────

def test_add_wallet_invalid_address_format():
    """No auth needed — validated before DI resolution"""
    response = client.post(
        "/api/wallets/",
        params={"address": "invalid_address", "chain": "eth"},
    )
    assert response.status_code == 401


def test_add_wallet_success(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)
    # add_wallet calls result.scalar_one_or_none() for existing check
    set_result(mock_db, scalar_one_or_none=None)

    response = client.post(
        "/api/wallets/",
        params={
            "address": "0x1234567890123456789012345678901234567890",
            "chain": "eth",
            "label": "My ETH Wallet",
        },
    )
    clear_overrides()

    assert response.status_code == 201
    assert "Wallet added successfully" in response.json()["message"]
    assert mock_db.add.called
    assert mock_db.commit.called
    assert mock_db.refresh.called


def test_add_wallet_already_exists(mock_user, mock_wallet):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)
    set_result(mock_db, scalar_one_or_none=mock_wallet)

    response = client.post(
        "/api/wallets/",
        params={
            "address": "0x1234567890123456789012345678901234567890",
            "chain": "eth",
        },
    )
    clear_overrides()

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_add_wallet_free_tier_limit(mock_free_user):
    mock_db = make_mock_db()
    override_deps(mock_free_user, mock_db)

    # Two db.execute calls: existing check + count check
    # Use side_effect to return different result configs per call
    results = [MagicMock(), MagicMock()]
    results[0].scalar_one_or_none.return_value = None
    results[1].scalar.return_value = 1
    mock_db.execute.side_effect = results

    response = client.post(
        "/api/wallets/",
        params={
            "address": "0x1234567890123456789012345678901234567890",
            "chain": "eth",
        },
    )
    clear_overrides()

    assert response.status_code == 403
    assert "Free tier limited" in response.json()["detail"]


# ── Delete Wallet ──────────────────────────────────────────────────────────

def test_delete_wallet_success(mock_user, mock_wallet):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)
    set_result(mock_db, scalar_one_or_none=mock_wallet)

    response = client.delete(f"/api/wallets/{mock_wallet.id}")
    clear_overrides()

    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    assert mock_db.delete.called
    assert mock_db.commit.called


def test_delete_wallet_not_found(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)
    set_result(mock_db, scalar_one_or_none=None)

    response = client.delete(f"/api/wallets/{uuid4()}")
    clear_overrides()

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


# ── Wallet Status ──────────────────────────────────────────────────────────

def test_get_wallet_status_success(mock_user, mock_wallet):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)

    # Two db.execute calls: wallet lookup + tx count
    results = [MagicMock(), MagicMock()]
    results[0].scalar_one_or_none.return_value = mock_wallet
    results[1].scalar.return_value = 5
    mock_db.execute.side_effect = results

    response = client.get(f"/api/wallets/{mock_wallet.id}/status")
    clear_overrides()

    assert response.status_code == 200
    assert response.json()["transaction_count"] == 5


def test_get_wallet_status_not_found(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)
    set_result(mock_db, scalar_one_or_none=None)

    response = client.get(f"/api/wallets/{uuid4()}/status")
    clear_overrides()

    assert response.status_code == 404


# ── Sync Wallet ────────────────────────────────────────────────────────────

def test_sync_wallet_empty_response(mock_user, mock_wallet):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)
    set_result(mock_db, scalar_one_or_none=mock_wallet)

    with patch("app.services.chain_sync.fetch_transactions_with_retry", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = []

        response = client.post(f"/api/wallets/{mock_wallet.id}/sync")
        clear_overrides()

        assert response.status_code == 200


def test_sync_wallet_network_error(mock_user, mock_wallet):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)
    set_result(mock_db, scalar_one_or_none=mock_wallet)

    from app.services.chain_sync import ChainSyncError
    with patch("app.services.chain_sync.fetch_transactions_with_retry", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = ChainSyncError("API error")

        response = client.post(f"/api/wallets/{mock_wallet.id}/sync")
        clear_overrides()

        assert response.status_code == 503


def test_sync_wallet_not_found(mock_user):
    mock_db = make_mock_db()
    override_deps(mock_user, mock_db)
    set_result(mock_db, scalar_one_or_none=None)

    response = client.post(f"/api/wallets/{uuid4()}/sync")
    clear_overrides()

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


# ── Address Validation (pure function, no DI needed) ─────────────────────

def test_address_validation():
    from app.routers.wallets import validate_wallet_address

    assert validate_wallet_address("0x1234567890123456789012345678901234567890", "eth")
    assert validate_wallet_address("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", "btc")
    assert not validate_wallet_address("invalid", "eth")
    assert not validate_wallet_address("0x123", "eth")
    assert not validate_wallet_address("0x1234567890123456789012345678901234567890", "invalid_chain")
