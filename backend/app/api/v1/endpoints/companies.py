"""
Company Endpoints - 기업 및 서류 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
from fastapi.responses import FileResponse
import uuid as uuid_lib

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.user import User
from app.models.company import Company

router = APIRouter()

# 파일 저장 경로
UPLOAD_DIR = Path("uploads/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/{company_id}/upload-document")
async def upload_company_document(
    company_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """기업 서류 업로드 (관리자)"""

    # 기업 확인
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="기업을 찾을 수 없습니다")

    # 파일 타입 검증
    allowed_types = ["application/pdf", "application/msword",
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="PDF 또는 Word 문서만 업로드 가능합니다")

    # 파일 크기 검증 (50MB)
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="파일 크기는 50MB 이하여야 합니다")

    # 파일 저장
    file_ext = Path(file.filename).suffix
    filename = f"{company_id}_{uuid_lib.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as f:
        f.write(content)

    # DB 업데이트
    company.document_path = str(file_path)
    db.commit()

    return {
        "message": "파일이 업로드되었습니다",
        "filename": filename,
        "path": str(file_path)
    }


@router.get("/{company_id}/document")
async def get_company_document(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """기업 서류 다운로드"""

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="기업을 찾을 수 없습니다")

    if not company.document_path:
        raise HTTPException(status_code=404, detail="업로드된 서류가 없습니다")

    file_path = Path(company.document_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")

    return FileResponse(
        path=file_path,
        filename=f"{company.name}_사업계획서{file_path.suffix}",
        media_type="application/octet-stream"
    )


@router.get("/{company_id}/document-info")
async def get_company_document_info(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """기업 서류 정보 조회"""

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="기업을 찾을 수 없습니다")

    if not company.document_path:
        return {"has_document": False}

    file_path = Path(company.document_path)
    if not file_path.exists():
        return {"has_document": False}

    return {
        "has_document": True,
        "filename": file_path.name,
        "file_size": file_path.stat().st_size,
        "file_type": file_path.suffix
    }
