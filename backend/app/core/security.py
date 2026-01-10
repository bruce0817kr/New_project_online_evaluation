"""
Security utilities - JWT 인증 및 비밀번호 해싱

참고: .claude/skills/biz-support-eval-dev/references/security_standard.md
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token
security_scheme = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    비밀번호 검증

    Args:
        plain_password: 평문 비밀번호
        hashed_password: 해시된 비밀번호

    Returns:
        일치 여부
    """
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """
    비밀번호 해싱 (bcrypt)

    Args:
        password: 평문 비밀번호

    Returns:
        해시된 비밀번호
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT 액세스 토큰 생성

    Args:
        data: 토큰에 포함할 데이터 (user_id, role 등)
        expires_delta: 만료 시간 (기본: 8시간)

    Returns:
        JWT 토큰 문자열
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    JWT 토큰 디코딩 및 검증

    Args:
        token: JWT 토큰

    Returns:
        페이로드 데이터 또는 None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    현재 로그인한 사용자 정보 조회

    Args:
        credentials: Bearer 토큰
        db: 데이터베이스 세션

    Returns:
        User 객체

    Raises:
        HTTPException: 인증 실패 시
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 계정입니다"
        )

    return user


async def get_current_active_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    관리자 권한 검증

    Args:
        current_user: 현재 사용자

    Returns:
        User 객체

    Raises:
        HTTPException: 관리자가 아닐 경우
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    return current_user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    사용자 인증

    Args:
        db: 데이터베이스 세션
        username: 사용자명
        password: 평문 비밀번호

    Returns:
        인증 성공 시 User 객체, 실패 시 None
    """
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


# Alias for backward compatibility
require_admin = get_current_active_admin


def get_password_hash(password: str) -> str:
    """비밀번호 해싱 (hash_password의 별칭)"""
    return hash_password(password)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    비밀번호 강도 검증

    보안 표준:
    - 최소 8자 이상
    - 영문 대소문자, 숫자, 특수문자 중 3종 이상 조합

    Args:
        password: 검증할 비밀번호

    Returns:
        (유효 여부, 에러 메시지)
    """
    if len(password) < 8:
        return False, "비밀번호는 최소 8자 이상이어야 합니다"

    import re

    complexity = sum([
        bool(re.search(r'[a-z]', password)),  # 소문자
        bool(re.search(r'[A-Z]', password)),  # 대문자
        bool(re.search(r'\d', password)),     # 숫자
        bool(re.search(r'[^a-zA-Z\d]', password))  # 특수문자
    ])

    if complexity < 3:
        return False, "비밀번호는 영문 대소문자, 숫자, 특수문자 중 3종 이상 조합이어야 합니다"

    return True, ""
