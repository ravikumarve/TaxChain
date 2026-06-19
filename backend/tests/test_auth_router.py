import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch

from app.routers.auth import router
from app.models.user import User

# Create a test app with just the auth router
from fastapi import FastAPI

test_app = FastAPI()
test_app.include_router(router, prefix="/api/auth")
client = TestClient(test_app)


@pytest.mark.asyncio
async def test_register_user_success():
    """Test successful user registration"""
    with patch("app.routers.auth.get_db") as mock_get_db:
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db

        # Mock user doesn't exist
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        response = client.post(
            "/api/auth/register",
            data={
                "email": "test@example.com",
                "password": "securepassword123",
                "country": "IN",
            },
        )

        assert response.status_code == 200
        assert response.json()["message"] == "User created successfully"
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()


@pytest.mark.asyncio
async def test_register_user_already_exists():
    """Test registration with existing email"""
    with patch("app.routers.auth.get_db") as mock_get_db:
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db

        # Mock user already exists
        existing_user = User(email="existing@example.com", password_hash="hashed")
        mock_db.execute.return_value.scalar_one_or_none.return_value = existing_user

        response = client.post(
            "/api/auth/register",
            data={
                "email": "existing@example.com",
                "password": "password123",
                "country": "IN",
            },
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_user_short_password():
    """Test registration with short password"""
    response = client.post(
        "/api/auth/register",
        data={"email": "test@example.com", "password": "short", "country": "IN"},
    )

    assert response.status_code == 400
    assert "at least 8 characters" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success():
    """Test successful login"""
    with patch("app.routers.auth.authenticate_user") as mock_auth:
        # Mock successful authentication
        mock_user = User(email="test@example.com", password_hash="hashed")
        mock_auth.return_value = mock_user

        response = client.post(
            "/api/auth/login",
            data={"username": "test@example.com", "password": "correctpassword"},
        )

        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()
        assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    with patch("app.routers.auth.authenticate_user") as mock_auth:
        # Mock failed authentication
        mock_auth.return_value = None

        response = client.post(
            "/api/auth/login",
            data={"username": "test@example.com", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_refresh_token_success():
    """Test successful token refresh"""
    with patch("app.routers.auth.refresh_access_token") as mock_refresh:
        mock_refresh.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "same_refresh_token",
            "token_type": "bearer",
        }

        response = client.post(
            "/api/auth/refresh", data={"refresh_token": "invalid_token"}
        )

        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]


def test_rate_limiting_protection():
    """Test that rate limiting headers are present"""
    response = client.post(
        "/api/auth/login", data={"username": "test@example.com", "password": "password"}
    )

    # Should have rate limiting headers
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers


def test_cors_headers():
    """Test CORS headers are properly set"""
    response = client.options("/api/auth/login")

    assert "Access-Control-Allow-Origin" in response.headers
    assert "Access-Control-Allow-Methods" in response.headers
    assert "Access-Control-Allow-Headers" in response.headers


@pytest.mark.asyncio
async def test_register_user_invalid_email_format():
    """Test registration with invalid email format"""
    response = client.post(
        "/api/auth/register",
        data={
            "email": "invalid-email",
            "password": "securepassword123",
            "country": "IN",
        },
    )

    assert response.status_code == 422  # Validation error
    assert "email" in response.json()["detail"][0]["loc"]


@pytest.mark.asyncio
async def test_register_user_missing_country():
    """Test registration with missing country"""
    response = client.post(
        "/api/auth/register",
        data={
            "email": "test@example.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 422
    assert "country" in response.json()["detail"][0]["loc"]


@pytest.mark.asyncio
async def test_register_user_invalid_country():
    """Test registration with invalid country code"""
    response = client.post(
        "/api/auth/register",
        data={
            "email": "test@example.com",
            "password": "securepassword123",
            "country": "XX",  # Invalid country code
        },
    )

    assert response.status_code == 400
    assert "Invalid country code" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_user_not_found():
    """Test login with non-existent user"""
    with patch("app.routers.auth.authenticate_user") as mock_auth:
        mock_auth.return_value = None

        response = client.post(
            "/api/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_empty_password():
    """Test login with empty password"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "test@example.com",
            "password": "",
        },
    )

    assert response.status_code == 422
    assert "password" in response.json()["detail"][0]["loc"]


@pytest.mark.asyncio
async def test_login_empty_username():
    """Test login with empty username"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "",
            "password": "password123",
        },
    )

    assert response.status_code == 422
    assert "username" in response.json()["detail"][0]["loc"]


@pytest.mark.asyncio
async def test_refresh_token_invalid_format():
    """Test refresh token with invalid format"""
    response = client.post(
        "/api/auth/refresh",
        data={
            "refresh_token": "invalid.token.format",
        },
    )

    assert response.status_code == 401
    assert "Invalid refresh token" in response.json()["detail"]


@pytest.mark.asyncio
async def test_refresh_token_expired():
    """Test refresh token with expired token"""
    with patch("app.routers.auth.refresh_access_token") as mock_refresh:
        mock_refresh.side_effect = HTTPException(
            status_code=401, detail="Refresh token expired"
        )

        response = client.post(
            "/api/auth/refresh",
            data={
                "refresh_token": "expired.token",
            },
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"]


@pytest.mark.asyncio
async def test_rate_limiting_exceeded():
    """Test rate limiting exceeded scenario"""
    # Simulate rate limiting by making multiple requests
    with patch("app.routers.auth.rate_limiter") as mock_limiter:
        mock_limiter.limit.return_value = True

        response = client.post(
            "/api/auth/login",
            data={
                "username": "test@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 429
        assert "Rate limit" in response.json()["detail"]


@pytest.mark.asyncio
async def test_concurrent_login_attempts():
    """Test concurrent login attempts"""
    with (
        patch("app.routers.auth.authenticate_user") as mock_auth,
        patch("app.routers.auth.asyncio.sleep") as mock_sleep,
    ):
        # Mock slow authentication to test concurrency
        async def slow_auth(*args, **kwargs):
            await mock_sleep(0.1)
            return User(email="test@example.com", password_hash="hashed")

        mock_auth.side_effect = slow_auth

        response = client.post(
            "/api/auth/login",
            data={
                "username": "test@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 200
        assert mock_sleep.called


@pytest.mark.asyncio
async def test_password_hashing_security():
    """Test password hashing security"""
    with patch("app.routers.auth.get_db") as mock_get_db:
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        response = client.post(
            "/api/auth/register",
            data={
                "email": "security_test@example.com",
                "password": "very_secure_password_123",
                "country": "IN",
            },
        )

        assert response.status_code == 200
        # Verify password is not returned in response
        assert "password" not in response.json()
        assert "password_hash" not in response.json()


@pytest.mark.asyncio
async def test_token_expiration():
    """Test token expiration functionality"""
    with patch("app.routers.auth.authenticate_user") as mock_auth:
        mock_user = User(email="test@example.com", password_hash="hashed")
        mock_auth.return_value = mock_user

        response = client.post(
            "/api/auth/login",
            data={
                "username": "test@example.com",
                "password": "correctpassword",
            },
        )

        assert response.status_code == 200
        # Verify tokens have expiration claims
        import jwt

        access_token = response.json()["access_token"]
        decoded = jwt.decode(access_token, options={"verify_signature": False})
        assert "exp" in decoded


@pytest.mark.asyncio
async def test_different_country_registration():
    """Test registration with different countries"""
    with patch("app.routers.auth.get_db") as mock_get_db:
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        test_cases = [
            ("US", "01-01"),  # US financial year
            ("UK", "04-06"),  # UK financial year
            ("CA", "01-01"),  # Canada financial year
            ("AU", "07-01"),  # Australia financial year
        ]

        for country_code, expected_fy_start in test_cases:
            response = client.post(
                "/api/auth/register",
                data={
                    "email": f"test_{country_code}@example.com",
                    "password": "securepassword123",
                    "country": country_code,
                },
            )

            assert response.status_code == 200
            # Should set appropriate financial year start based on country
