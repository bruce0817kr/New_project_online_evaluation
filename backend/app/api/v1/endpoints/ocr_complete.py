"""
OCR API Endpoints - 멀티 엔진 통합

참고:
- .claude/skills/biz-support-eval-dev/scripts/ocr_parser.py
- .claude/skills/biz-support-eval-dev/references/eval_guidelines.md
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.services.ocr import OCRManager, DocumentType, OCREngineType
from app.services.audit_service import log_audit_event

router = APIRouter()


def get_ocr_manager() -> OCRManager:
    """OCR 매니저 인스턴스 생성"""
    config = {
        "tesseract": {
            "confidence_threshold": 0.85
        },
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "gpt-4o"
        },
        "gemini": {
            "api_key": os.getenv("GOOGLE_API_KEY"),
            "model": "gemini-1.5-flash"
        },
        "mistral": {
            "api_key": os.getenv("MISTRAL_API_KEY"),
            "model": "pixtral-12b-2409"
        },
        "fallback_strategy": os.getenv("OCR_FALLBACK_STRATEGY", "on_low_confidence"),
        "confidence_threshold": float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.85")),
        "enable_ensemble": os.getenv("OCR_ENABLE_ENSEMBLE", "false").lower() == "true"
    }

    return OCRManager(config)


@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    document_type: str = Form("사업자등록증"),
    preferred_engine: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    문서 OCR 분석

    - **file**: 업로드할 이미지 파일 (PDF/JPG/PNG)
    - **document_type**: 문서 유형 (사업자등록증, 법인등기부등본, 일반문서)
    - **preferred_engine**: 선호 엔진 (tesseract, openai, gemini, mistral)

    Returns:
        OCR 분석 결과 (구조화된 데이터)
    """
    # 파일 검증
    allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png"}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다")

    # 임시 파일 저장
    temp_filename = f"{uuid.uuid4()}{file_ext}"
    temp_path = os.path.join(settings.UPLOAD_DIR, "temp", temp_filename)

    os.makedirs(os.path.dirname(temp_path), exist_ok=True)

    try:
        # 파일 저장
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        # 문서 타입 변환
        doc_type_map = {
            "사업자등록증": DocumentType.BUSINESS_LICENSE,
            "법인등기부등본": DocumentType.CORPORATE_REGISTRY,
            "재무제표": DocumentType.FINANCIAL_STATEMENT,
            "일반문서": DocumentType.GENERAL
        }
        doc_type = doc_type_map.get(document_type, DocumentType.GENERAL)

        # 선호 엔진 변환
        engine_type = None
        if preferred_engine:
            engine_map = {
                "tesseract": OCREngineType.TESSERACT,
                "openai": OCREngineType.OPENAI,
                "gemini": OCREngineType.GEMINI,
                "mistral": OCREngineType.MISTRAL
            }
            engine_type = engine_map.get(preferred_engine.lower())

        # OCR 분석
        ocr_manager = get_ocr_manager()
        result = await ocr_manager.analyze_document(
            temp_path,
            doc_type,
            preferred_engine=engine_type
        )

        # 감사 로그
        await log_audit_event(
            db=db,
            user_id=str(current_user.id),
            username=current_user.username,
            action="OCR_ANALYZE",
            resource=f"file:{file.filename}",
            details={
                "document_type": document_type,
                "engine": result.engine.value,
                "confidence": result.confidence_score
            },
            status="SUCCESS"
        )

        # 응답
        return {
            "success": True,
            "engine": result.engine.value,
            "document_type": result.document_type.value,
            "extracted_data": result.extracted_data,
            "confidence_score": result.confidence_score,
            "needs_manual_verification": result.needs_manual_verification,
            "processing_time_ms": result.processing_time_ms,
            "errors": result.errors
        }

    except Exception as e:
        # 감사 로그 (실패)
        await log_audit_event(
            db=db,
            user_id=str(current_user.id),
            username=current_user.username,
            action="OCR_ANALYZE_FAILED",
            resource=f"file:{file.filename}",
            details={"error": str(e)},
            status="FAILED"
        )

        raise HTTPException(status_code=500, detail=f"OCR 처리 실패: {str(e)}")

    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/engines")
async def get_available_engines(
    current_user: User = Depends(get_current_user)
):
    """
    사용 가능한 OCR 엔진 목록 조회

    Returns:
        엔진 목록 및 상태
    """
    ocr_manager = get_ocr_manager()
    available_engines = ocr_manager.get_available_engines()

    return {
        "engines": available_engines,
        "fallback_strategy": ocr_manager.fallback_strategy.value,
        "confidence_threshold": ocr_manager.confidence_threshold,
        "ensemble_enabled": ocr_manager.enable_ensemble
    }


@router.post("/extract-text")
async def extract_text_only(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    간단한 텍스트 추출 (구조화 없이 원본 텍스트만)

    - **file**: 업로드할 이미지 파일

    Returns:
        추출된 텍스트
    """
    # 파일 저장
    temp_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
    temp_path = os.path.join(settings.UPLOAD_DIR, "temp", temp_filename)

    os.makedirs(os.path.dirname(temp_path), exist_ok=True)

    try:
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        # 텍스트 추출
        ocr_manager = get_ocr_manager()
        text = await ocr_manager.extract_text_simple(temp_path)

        return {
            "success": True,
            "text": text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"텍스트 추출 실패: {str(e)}")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
