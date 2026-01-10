"""
Project Management Endpoints - 프로젝트 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.user import User
from app.models.project import Project
from app.models.company import Company
from app.models.evaluation import Evaluation

router = APIRouter()


# ============== Schemas ==============

class ProjectCreate(BaseModel):
    """프로젝트 생성"""
    name: str
    description: str = None
    year: int
    deadline: datetime


class ProjectUpdate(BaseModel):
    """프로젝트 수정"""
    name: str = None
    description: str = None
    year: int = None


class ProjectResponse(BaseModel):
    """프로젝트 응답"""
    id: str
    name: str
    description: str = None
    year: str
    deadline: datetime = None
    created_at: datetime
    updated_at: datetime = None

    class Config:
        orm_mode = True


class CompanyResponse(BaseModel):
    """기업 응답"""
    id: str
    name: str
    business_number: str = None
    ceo_name: str = None

    class Config:
        orm_mode = True


# ============== Endpoints ==============

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """프로젝트 목록 조회"""
    projects = db.query(Project).order_by(Project.created_at.desc()).all()

    return [
        ProjectResponse(
            id=str(project.id),
            name=project.name,
            description=project.description,
            year=project.year,
            deadline=None,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
        for project in projects
    ]


@router.post("/", response_model=ProjectResponse)
async def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """새 프로젝트 생성"""

    project = Project(
        name=data.name,
        description=data.description,
        year=str(data.year)
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return ProjectResponse(
        id=str(project.id),
        name=project.name,
        description=project.description,
        year=project.year,
        deadline=data.deadline,
        created_at=project.created_at,
        updated_at=project.updated_at
    )


@router.get("/{project_id}/companies", response_model=List[CompanyResponse])
async def get_project_companies(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """프로젝트별 기업 목록 조회"""

    # 프로젝트 확인
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다")

    # 기업 목록 조회
    companies = db.query(Company).filter(Company.project_id == project_id).all()

    return [
        CompanyResponse(
            id=str(company.id),
            name=company.name,
            business_number=company.business_number,
            ceo_name=company.ceo_name
        )
        for company in companies
    ]
