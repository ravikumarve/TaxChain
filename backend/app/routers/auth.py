from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_password_hash,
    refresh_access_token,
)
from app.models.user import User
from app.schemas.auth import UserLogin, UserRegister, TokenResponse, RefreshTokenRequest

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register_user(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Validate password strength
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long",
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        country=user_data.country,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Generate tokens
    access_token = create_access_token(data={"sub": new_user.email})
    refresh_token = create_refresh_token(data={"sub": new_user.email})

    return {
        "message": "User created successfully",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login", summary="Login with form data (OAuth2 compatible)")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login/json", summary="Login with JSON body (SPA compatible)")
async def login_json(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    return await refresh_access_token(db, token_data.refresh_token)


@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Get current user's profile information."""
    return {
        "email": current_user.email,
        "plan": current_user.plan,
        "country": current_user.country,
        "financial_year_start": current_user.financial_year_start,
        "cost_basis_method": current_user.cost_basis_method,
    }
