"""
Pydantic schemas for authentication
"""

from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    country: str = "IN"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
