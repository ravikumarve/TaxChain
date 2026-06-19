"""
Tests for auth router endpoints.
Uses app.dependency_overrides for proper FastAPI test DI.
"""
import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI

from app.routers.auth import router, auth_limiter
from app.database import get_db
from app.models.user import User

# Disable rate limiting for tests
auth_limiter.enabled = False

# Create a test app with just the auth router
test_app = FastAPI()
test_app.include_router(router, prefix="/api/auth")
client = TestClient(test_app)


# ── Helpers ──────────────────────────────────────────────────────────────

def make_mock_db():
    """Create a mock db session with proper execute side_effect."""
    mock_db = AsyncMock(spec=AsyncSession)
    # Use side_effect as a factory that returns a fresh MagicMock per call
    def execute_side(*args, **kwargs):
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        return result
    mock_db.execute.side_effect = execute_side
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    mock_db.add = MagicMock()
    return mock_db


def register_test_app(mock_db=None):
    """Set up dependency overrides for tests."""
    if mock_db is None:
        mock_db = make_mock_db()
    test_app.dependency_overrides[get_db] = lambda: mock_db
    return mock_db


def clear_overrides():
    """Clear all dependency overrides."""
    test_app.dependency_overrides = {}


# ── Register Tests ───────────────────────────────────────────────────────

def test_different_country_registration():
    """Test registration with different countries — run first to avoid rate limit"""
    register_test_app()
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test_US@example.com",
            "password": "securepassword123",
            "country": "US",
        },
    )
    assert response.status_code == 200, f"Failed for US: {response.text}"
    clear_overrides()


def test_register_user_success():
    """Test successful user registration"""
    register_test_app()
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
            "country": "IN",
        },
    )
    clear_overrides()
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User created successfully"
    assert "access_token" in data
    assert "refresh_token" in data


def test_register_user_already_exists():
    """Test registration with existing email"""
    mock_db = register_test_app()
    # Override the side_effect: first (and only) execute returns an existing user
    mock_db.execute.side_effect = None
    mock_db.execute.return_value = MagicMock()
    mock_db.execute.return_value.scalar_one_or_none.return_value = User(
        email="existing@example.com", password_hash="hashed"
    )

    response = client.post(
        "/api/auth/register",
        json={
            "email": "existing@example.com",
            "password": "password123",
            "country": "IN",
        },
    )
    clear_overrides()
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_register_user_short_password():
    """Test registration with short password (validated before DB call)"""
    register_test_app()
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "short", "country": "IN"},
    )
    clear_overrides()
    assert response.status_code == 400
    assert "at least 8 characters" in response.json()["detail"]


def test_register_user_invalid_email_format():
    """Test registration with invalid email format"""
    response = client.post(
        "/api/auth/register",
        json={"email": "invalid-email", "password": "securepassword123", "country": "IN"},
    )
    assert response.status_code == 422


def test_register_user_missing_country():
    """Test registration with missing country (defaults to 'IN')"""
    register_test_app()
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "securepassword123"},
    )
    clear_overrides()
    assert response.status_code == 200


def test_password_hashing_security():
    """Test password is not returned in response"""
    register_test_app()
    response = client.post(
        "/api/auth/register",
        json={
            "email": "security_test@example.com",
            "password": "very_secure_password_123",
            "country": "IN",
        },
    )
    clear_overrides()
    assert response.status_code == 200
    assert "password" not in response.json()
    assert "password_hash" not in response.json()


# ── Login Tests ──────────────────────────────────────────────────────────

def test_login_success():
    """Test successful login"""
    register_test_app()
    with patch("app.routers.auth.authenticate_user") as mock_auth:
        mock_user = User(email="test@example.com", password_hash="hashed")
        mock_auth.return_value = mock_user

        response = client.post(
            "/api/auth/login",
            data={"username": "test@example.com", "password": "correctpassword"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    clear_overrides()


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    register_test_app()
    with patch("app.routers.auth.authenticate_user") as mock_auth:
        mock_auth.return_value = None

        response = client.post(
            "/api/auth/login",
            data={"username": "test@example.com", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    clear_overrides()


def test_login_empty_password():
    """Test login with empty password — OAuth2 form rejects empty strings"""
    register_test_app()
    response = client.post(
        "/api/auth/login",
        data={"username": "test@example.com", "password": ""},
    )
    # OAuth2PasswordRequestForm treats empty password as missing field
    assert response.status_code == 422
    clear_overrides()


def test_token_expiration():
    """Test that access token contains exp claim"""
    register_test_app()
    with patch("app.routers.auth.authenticate_user") as mock_auth:
        mock_user = User(email="test@example.com", password_hash="hashed")
        mock_auth.return_value = mock_user

        response = client.post(
            "/api/auth/login",
            data={"username": "test@example.com", "password": "correctpassword"},
        )

        assert response.status_code == 200
        from jose import jwt
        access_token = response.json()["access_token"]
        # Use test secret key to decode (from app.config)
        from app.config import settings
        decoded = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
        assert "exp" in decoded
    clear_overrides()


# ── Refresh Token Tests ──────────────────────────────────────────────────

def test_refresh_token_success():
    """Test successful token refresh"""
    register_test_app()
    with patch("app.routers.auth.refresh_access_token") as mock_refresh:
        mock_refresh.return_value = {
            "access_token": "new_access_token",
            "token_type": "bearer",
            "refresh_token": "same_refresh_token",
        }

        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": "some_valid_token"},
        )

        assert response.status_code == 200
        assert response.json()["access_token"] == "new_access_token"
    clear_overrides()


def test_refresh_token_invalid():
    """Test refresh token with invalid token"""
    register_test_app()
    with patch("app.routers.auth.refresh_access_token") as mock_refresh:
        mock_refresh.side_effect = HTTPException(
            status_code=401, detail="Invalid refresh token"
        )

        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )

        assert response.status_code == 401
        assert "Invalid" in response.json()["detail"]
    clear_overrides()


def test_refresh_token_expired():
    """Test refresh with expired token"""
    register_test_app()
    with patch("app.routers.auth.refresh_access_token") as mock_refresh:
        mock_refresh.side_effect = HTTPException(
            status_code=401, detail="Refresh token expired"
        )

        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": "expired.token"},
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"]
    clear_overrides()
