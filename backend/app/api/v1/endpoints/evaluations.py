"""
Evaluation Endpoints - 평가 관련 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict, Any

from app.core.database import get_db

router = APIRouter()


@router.get("/{company_id}")
async def get_evaluation(
    company_id: UUID,
    db: Session = Depends(get_db)
):
    """
    특정 기업에 대한 평가 데이터 로드
    GET /api/v1/evaluations/{company_id}
    """
    # TODO: Implement evaluation retrieval
    return {
        "company_id": str(company_id),
        "scores_data": {},
        "is_submitted": False
    }


@router.patch("/save")
async def save_evaluation(
    evaluation_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    평가 임시 저장 (Auto-save with Debounce)
    PATCH /api/v1/evaluations/save
    """
    # TODO: Implement auto-save logic
    return {"message": "Evaluation saved", "timestamp": "2024-01-01T00:00:00"}


@router.post("/submit")
async def submit_evaluation(
    evaluation_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    평가 최종 제출 및 서명
    POST /api/v1/evaluations/submit
    """
    # TODO: Implement final submission with signature
    return {"message": "Evaluation submitted successfully"}


@router.get("/company/{company_id}/aggregate")
async def get_aggregated_scores(
    company_id: UUID,
    db: Session = Depends(get_db)
):
    """
    기업별 전체 심사위원 점수 집계
    최고/최저점 제외 평균 계산
    """
    # TODO: Implement score aggregation logic
    return {
        "company_id": str(company_id),
        "average_score": 0.0,
        "trimmed_average": 0.0,
        "evaluator_count": 0
    }
