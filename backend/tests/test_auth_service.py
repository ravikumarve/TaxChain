import pytest
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock

from app.services.auth_service import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    refresh_access_token,
    get_current_user,
)
from app.models.user import User
from app.config import settings


@pytest.mark.asyncio
async def test_verify_password():
    """Test password hashing and verification"""
    password = "testpass123"  # Reasonable length password
    hashed_password = get_password_hash(password)

    # Correct password should verify
    assert verify_password(password, hashed_password) is True

    # Wrong password should not verify
    assert verify_password("wrongpass", hashed_password) is False


def test_create_access_token():
    """Test access token creation and validation"""
    data = {"sub": "test@example.com"}
    token = create_access_token(data)

    # Token should be created
    assert isinstance(token, str)
    assert len(token) > 0

    # Should be able to decode with correct secret
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == "test@example.com"
    assert "exp" in decoded

    # Should fail with wrong secret
    with pytest.raises(JWTError):
        jwt.decode(token, "wrong-secret-key", algorithms=[settings.ALGORITHM])


def test_create_refresh_token():
    """Test refresh token creation"""
    data = {"sub": "test@example.com"}
    token = create_refresh_token(data)

    assert isinstance(token, str)
    assert len(token) > 0

    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == "test@example.com"
    assert decoded["type"] == "refresh"
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_refresh_access_token_valid():
    """Test valid refresh token flow"""
    mock_db = AsyncMock(spec=AsyncSession)

    # Create a mock user
    mock_user = User(
        id="123e4567-e89b-12d3-a456-426614174000",
        email="test@example.com",
        password_hash="hashed",
    )

    # Mock the database query - use regular Mock for scalar result
    from unittest.mock import Mock

    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db.execute.return_value = mock_result

    # Create refresh token
    refresh_token = create_refresh_token({"sub": "test@example.com"})

    # Refresh should work
    result = await refresh_access_token(mock_db, refresh_token)

    assert "access_token" in result
    assert "refresh_token" in result
    assert "token_type" in result
    assert result["refresh_token"] == refresh_token


@pytest.mark.asyncio
async def test_refresh_access_token_invalid():
    """Test refresh token with invalid token"""
    mock_db = AsyncMock(spec=AsyncSession)

    # Invalid token should raise exception
    with pytest.raises(HTTPException) as exc_info:
        await refresh_access_token(mock_db, "invalid-token")

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh_access_token_expired():
    """Test refresh token with expired token"""
    mock_db = AsyncMock(spec=AsyncSession)

    # Create expired token
    expired_data = {
        "sub": "test@example.com",
        "type": "refresh",
        "exp": datetime.utcnow() - timedelta(hours=1),
    }
    expired_token = jwt.encode(
        expired_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    with pytest.raises(HTTPException) as exc_info:
        await refresh_access_token(mock_db, expired_token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh_access_token_wrong_type():
    """Test refresh token with wrong token type"""
    mock_db = AsyncMock(spec=AsyncSession)

    # Create access token instead of refresh token
    access_token = create_access_token({"sub": "test@example.com"})

    with pytest.raises(HTTPException) as exc_info:
        await refresh_access_token(mock_db, access_token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh_access_token_user_not_found():
    """Test refresh token for non-existent user"""
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock user not found
    from unittest.mock import Mock

    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    refresh_token = create_refresh_token({"sub": "nonexistent@example.com"})

    with pytest.raises(HTTPException) as exc_info:
        await refresh_access_token(mock_db, refresh_token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "User not found" in str(exc_info.value.detail)


def test_password_hashing_salt():
    """Test that password hashing uses different salts"""
    password = "samepassword123"  # Reasonable length password
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)

    # Hashes should be different due to different salts
    assert hash1 != hash2

    # But both should verify correctly
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


def test_token_expiration():
    """Test token expiration timing"""
    data = {"sub": "test@example.com"}

    # Test with custom expiration
    short_token = create_access_token(data, timedelta(minutes=5))
    decoded = jwt.decode(
        short_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    # Check expiration is within expected range
    exp_time = datetime.utcfromtimestamp(decoded["exp"])
    expected_exp = datetime.utcnow() + timedelta(minutes=5)

    # Allow 10 seconds tolerance for test execution time
    assert abs((exp_time - expected_exp).total_seconds()) < 10
