"""
Authentication Endpoints

참고: .claude/skills/biz-support-eval-dev/references/security_standard.md
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password
)
from app.core.config import settings
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse, UserCreate, PasswordChange
from app.models.user import User
from app.services.audit_service import log_audit_event

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    사용자 로그인

    - **username**: 사용자명
    - **password**: 비밀번호

    성공 시 JWT 토큰 반환
    """
    user = authenticate_user(db, request.username, request.password)

    if not user:
        # 감사 로그 기록 (실패)
        await log_audit_event(
            db=db,
            user_id=None,
            username=request.username,
            action="LOGIN_FAILED",
            resource="auth",
            status="FAILED"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자명 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # JWT 토큰 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role},
        expires_delta=access_token_expires
    )

    # 감사 로그 기록 (성공)
    await log_audit_event(
        db=db,
        user_id=str(user.id),
        username=user.username,
        action="LOGIN_SUCCESS",
        resource="auth",
        status="SUCCESS"
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    사용자 로그아웃

    JWT 토큰은 stateless이므로 클라이언트에서 토큰 삭제 처리
    """
    await log_audit_event(
        db=db,
        user_id=str(current_user.id),
        username=current_user.username,
        action="LOGOUT",
        resource="auth",
        status="SUCCESS"
    )

    return {"message": "로그아웃되었습니다"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    현재 로그인한 사용자 정보 조회

    JWT 토큰에서 사용자 정보 추출
    """
    return UserResponse.from_orm(current_user)


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user)
):
    """
    새 사용자 등록 (관리자 전용)

    - **username**: 사용자명 (고유)
    - **email**: 이메일 (고유)
    - **password**: 비밀번호 (8자 이상, 복잡도 검증)
    - **full_name**: 전체 이름
    - **role**: admin 또는 evaluator
    """
    # 관리자 권한 확인 (이미 Depends에서 처리되지만 명시적으로)
    if current_admin.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )

    # 중복 체크
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 사용자명 또는 이메일입니다"
        )

    # 사용자 생성
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 감사 로그
    await log_audit_event(
        db=db,
        user_id=str(current_admin.id),
        username=current_admin.username,
        action="USER_CREATE",
        resource=f"user:{new_user.id}",
        details={"new_username": new_user.username, "role": new_user.role},
        status="SUCCESS"
    )

    return UserResponse.from_orm(new_user)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    비밀번호 변경

    - **current_password**: 현재 비밀번호
    - **new_password**: 새 비밀번호 (복잡도 검증)
    """
    from app.core.security import verify_password

    # 현재 비밀번호 확인
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 올바르지 않습니다"
        )

    # 새 비밀번호로 변경
    current_user.hashed_password = hash_password(password_data.new_password)
    db.commit()

    # 감사 로그
    await log_audit_event(
        db=db,
        user_id=str(current_user.id),
        username=current_user.username,
        action="PASSWORD_CHANGE",
        resource="auth",
        status="SUCCESS"
    )

    return {"message": "비밀번호가 변경되었습니다"}
