"""
Company Management Endpoints
"""
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db

router = APIRouter()


@router.get("/")
async def list_companies(project_id: UUID = None, db: Session = Depends(get_db)):
    """기업 목록 조회"""
    # TODO: Implement company listing
    return []


@router.post("/")
async def create_company(db: Session = Depends(get_db)):
    """새 기업 등록"""
    # TODO: Implement company creation
    return {"message": "Company created"}


@router.get("/{company_id}")
async def get_company(company_id: UUID, db: Session = Depends(get_db)):
    """기업 상세 조회"""
    # TODO: Implement company retrieval
    return {"id": str(company_id), "name": "Sample Company"}


@router.post("/{company_id}/upload")
async def upload_document(
    company_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """기업 서류 업로드"""
    # TODO: Implement file upload and OCR processing
    return {"message": "File uploaded", "filename": file.filename}
