"""
Evaluation Endpoints - 평가 API (완전 구현)

참고:
- .claude/skills/biz-support-eval-dev/scripts/calculator.py
- .claude/skills/biz-support-eval-dev/references/eval_guidelines.md
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.evaluation import Evaluation
from app.models.company import Company
from app.schemas.evaluation import (
    EvaluationResponse,
    EvaluationUpdate,
    EvaluationSubmit,
    AggregatedScoreResponse
)
from app.services.score_service import ScoreService
from app.services.audit_service import log_audit_event

router = APIRouter()


@router.get("/{company_id}", response_model=EvaluationResponse)
async def get_evaluation(
    company_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 기업에 대한 평가 데이터 조회"""
    evaluation = db.query(Evaluation).filter(
        Evaluation.company_id == company_id,
        Evaluation.evaluator_id == current_user.id
    ).first()

    if not evaluation:
        # 평가가 없으면 새로 생성
        evaluation = Evaluation(
            company_id=company_id,
            evaluator_id=current_user.id,
            scores_data={}
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)

    return EvaluationResponse.from_orm(evaluation)


@router.patch("/{evaluation_id}/save")
async def save_evaluation(
    evaluation_id: str,
    data: EvaluationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """평가 임시 저장 (Auto-save)"""
    evaluation = db.query(Evaluation).filter(
        Evaluation.id == evaluation_id,
        Evaluation.evaluator_id == current_user.id
    ).first()

    if not evaluation:
        raise HTTPException(status_code=404, detail="평가를 찾을 수 없습니다")

    if evaluation.is_submitted:
        raise HTTPException(status_code=400, detail="이미 제출된 평가는 수정할 수 없습니다")

    # 업데이트
    if data.scores_data is not None:
        evaluation.scores_data = data.scores_data
    if data.overall_comment is not None:
        evaluation.overall_comment = data.overall_comment

    db.commit()

    return {"message": "저장되었습니다", "updated_at": evaluation.updated_at}


@router.post("/{evaluation_id}/submit")
async def submit_evaluation(
    evaluation_id: str,
    data: EvaluationSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """평가 최종 제출"""
    evaluation = db.query(Evaluation).filter(
        Evaluation.id == evaluation_id,
        Evaluation.evaluator_id == current_user.id
    ).first()

    if not evaluation:
        raise HTTPException(status_code=404, detail="평가를 찾을 수 없습니다")

    if evaluation.is_submitted:
        raise HTTPException(status_code=400, detail="이미 제출된 평가입니다")

    # 최종 데이터 업데이트
    evaluation.scores_data = data.scores_data
    evaluation.overall_comment = data.overall_comment
    evaluation.total_score = data.total_score
    evaluation.weighted_score = data.weighted_score
    evaluation.signature_data = data.signature_data
    evaluation.is_submitted = True
    evaluation.submitted_at = datetime.utcnow()

    db.commit()

    # 감사 로그
    await log_audit_event(
        db=db,
        user_id=str(current_user.id),
        username=current_user.username,
        action="EVALUATION_SUBMIT",
        resource=f"evaluation:{evaluation_id}",
        details={"company_id": str(evaluation.company_id), "total_score": data.total_score},
        status="SUCCESS"
    )

    return {"message": "제출이 완료되었습니다", "submitted_at": evaluation.submitted_at}


@router.get("/company/{company_id}/aggregate", response_model=AggregatedScoreResponse)
async def get_aggregated_scores(
    company_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """기업별 전체 심사위원 점수 집계"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="기업을 찾을 수 없습니다")

    evaluations = db.query(Evaluation).filter(
        Evaluation.company_id == company_id,
        Evaluation.is_submitted == True
    ).all()

    if not evaluations:
        raise HTTPException(status_code=404, detail="제출된 평가가 없습니다")

    # 점수 집계 (ScoreService 활용)
    eval_data = [{"total_score": e.total_score} for e in evaluations]
    aggregated = ScoreService.aggregate_evaluations(eval_data)

    return AggregatedScoreResponse(
        company_id=str(company_id),
        company_name=company.name,
        evaluations_count=aggregated["count"],
        average_score=aggregated["average"],
        trimmed_average=aggregated["trimmed_average"],
        min_score=aggregated["min"],
        max_score=aggregated["max"],
        std_dev=aggregated.get("std_dev", 0.0)
    )
