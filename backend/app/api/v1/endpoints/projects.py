"""
Project Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db

router = APIRouter()


@router.get("/")
async def list_projects(db: Session = Depends(get_db)):
    """사업 목록 조회"""
    # TODO: Implement project listing
    return []


@router.post("/")
async def create_project(db: Session = Depends(get_db)):
    """새 사업 생성"""
    # TODO: Implement project creation
    return {"message": "Project created"}


@router.get("/{project_id}")
async def get_project(project_id: UUID, db: Session = Depends(get_db)):
    """사업 상세 조회"""
    # TODO: Implement project retrieval
    return {"id": str(project_id), "name": "Sample Project"}


@router.patch("/{project_id}")
async def update_project(project_id: UUID, db: Session = Depends(get_db)):
    """사업 정보 수정"""
    # TODO: Implement project update
    return {"message": "Project updated"}


@router.delete("/{project_id}")
async def delete_project(project_id: UUID, db: Session = Depends(get_db)):
    """사업 삭제"""
    # TODO: Implement project deletion
    return {"message": "Project deleted"}
