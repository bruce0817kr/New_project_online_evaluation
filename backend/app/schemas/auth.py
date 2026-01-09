"""
Authentication Schemas
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """로그인 요청"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """토큰 응답"""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    """사용자 정보 응답"""
    id: str
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """사용자 생성 요청"""
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: str = "evaluator"

    @validator('password')
    def validate_password(cls, v):
        from app.core.security import validate_password_strength
        is_valid, message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v


class PasswordChange(BaseModel):
    """비밀번호 변경"""
    current_password: str
    new_password: str

    @validator('new_password')
    def validate_new_password(cls, v):
        from app.core.security import validate_password_strength
        is_valid, message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v
