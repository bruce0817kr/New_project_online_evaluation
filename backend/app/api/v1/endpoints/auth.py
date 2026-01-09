"""
Authentication Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter()


@router.post("/login")
async def login(db: Session = Depends(get_db)):
    """사용자 로그인"""
    # TODO: Implement authentication logic
    return {"access_token": "dummy_token", "token_type": "bearer"}


@router.post("/logout")
async def logout():
    """사용자 로그아웃"""
    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_current_user():
    """현재 사용자 정보 조회"""
    # TODO: Implement user info retrieval
    return {"username": "admin", "role": "admin"}
