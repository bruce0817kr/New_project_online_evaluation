"""
Evaluation Endpoints - 평가 관련 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from uuid import UUID
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.user import User
from app.models.evaluation import Evaluation
from app.models.company import Company
from app.models.project import Project

router = APIRouter()


# ============== Schemas ==============

class EvaluationResponse(BaseModel):
    """평가 응답"""
    id: str
    project_id: str = None
    project_name: str = None
    company_id: str
    company_name: str
    evaluator_id: str
    order: float = None
    scores_data: dict = {}
    total_score: float = None
    overall_comment: str = None
    is_submitted: bool
    submitted_at: datetime = None
    created_at: datetime
    updated_at: datetime = None

    # 동적 배점표 정보
    scoring_template: dict = None

    class Config:
        orm_mode = True


class EvaluationUpdate(BaseModel):
    """평가 업데이트"""
    scores_data: dict = None
    overall_comment: str = None


class EvaluationSubmit(BaseModel):
    """평가 제출"""
    signature_data: str = None


# ============== Endpoints ==============

@router.get("/my", response_model=List[EvaluationResponse])
async def get_my_evaluations(
    status: Optional[str] = None,  # 'in_progress' | 'submitted'
    project_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    내 평가 목록 조회 (심사위원용)
    """
    query = db.query(Evaluation).filter(
        Evaluation.evaluator_id == current_user.id
    ).options(
        joinedload(Evaluation.company),
        joinedload(Evaluation.company).joinedload(Company.project)
    )

    # 상태 필터
    if status == "in_progress":
        query = query.filter(Evaluation.is_submitted == False)
    elif status == "submitted":
        query = query.filter(Evaluation.is_submitted == True)

    # 프로젝트 필터
    if project_id:
        query = query.filter(Evaluation.project_id == project_id)

    # 순서대로 정렬
    evaluations = query.order_by(Evaluation.order.asc().nullslast()).all()

    return [
        EvaluationResponse(
            id=str(evaluation.id),
            project_id=str(evaluation.project_id) if evaluation.project_id else None,
            project_name=evaluation.company.project.name if evaluation.company and evaluation.company.project else None,
            company_id=str(evaluation.company_id),
            company_name=evaluation.company.name if evaluation.company else "알 수 없음",
            evaluator_id=str(evaluation.evaluator_id),
            order=evaluation.order,
            scores_data=evaluation.scores_data or {},
            total_score=evaluation.total_score,
            overall_comment=evaluation.overall_comment,
            is_submitted=evaluation.is_submitted,
            submitted_at=evaluation.submitted_at,
            created_at=evaluation.created_at,
            updated_at=evaluation.updated_at
        )
        for evaluation in evaluations
    ]


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation_detail(
    evaluation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    평가 상세 조회 (배점표 템플릿 포함)
    """
    from app.models.scoring_template import ScoringTemplate

    evaluation = db.query(Evaluation).filter(
        Evaluation.id == evaluation_id
    ).options(
        joinedload(Evaluation.company),
        joinedload(Evaluation.company).joinedload(Company.project)
    ).first()

    if not evaluation:
        raise HTTPException(status_code=404, detail="평가를 찾을 수 없습니다")

    # 권한 체크: 본인 평가이거나 관리자
    if current_user.role != "admin" and str(evaluation.evaluator_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

    # 배점표 템플릿 조회
    scoring_template = None
    if evaluation.company and evaluation.company.project and evaluation.company.project.scoring_template_id:
        template = db.query(ScoringTemplate).filter(
            ScoringTemplate.id == evaluation.company.project.scoring_template_id
        ).first()
        if template:
            scoring_template = {
                "id": str(template.id),
                "name": template.name,
                "total_score": template.total_score,
                "sections": template.sections.get("sections", []) if template.sections else []
            }

    return EvaluationResponse(
        id=str(evaluation.id),
        project_id=str(evaluation.project_id) if evaluation.project_id else None,
        project_name=evaluation.company.project.name if evaluation.company and evaluation.company.project else None,
        company_id=str(evaluation.company_id),
        company_name=evaluation.company.name if evaluation.company else "알 수 없음",
        evaluator_id=str(evaluation.evaluator_id),
        order=evaluation.order,
        scores_data=evaluation.scores_data or {},
        total_score=evaluation.total_score,
        overall_comment=evaluation.overall_comment,
        is_submitted=evaluation.is_submitted,
        submitted_at=evaluation.submitted_at,
        created_at=evaluation.created_at,
        updated_at=evaluation.updated_at,
        scoring_template=scoring_template
    )


@router.put("/{evaluation_id}", response_model=EvaluationResponse)
async def update_evaluation(
    evaluation_id: str,
    data: EvaluationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    평가 임시 저장
    """
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
        # 총점 계산 (간단 버전)
        if data.scores_data:
            total = sum([v for v in data.scores_data.values() if isinstance(v, (int, float))])
            evaluation.total_score = total

    if data.overall_comment is not None:
        evaluation.overall_comment = data.overall_comment

    evaluation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(evaluation)

    # 관계 로드
    db.refresh(evaluation, ["company"])
    if evaluation.company:
        db.refresh(evaluation.company, ["project"])

    return EvaluationResponse(
        id=str(evaluation.id),
        project_id=str(evaluation.project_id) if evaluation.project_id else None,
        project_name=evaluation.company.project.name if evaluation.company and evaluation.company.project else None,
        company_id=str(evaluation.company_id),
        company_name=evaluation.company.name if evaluation.company else "알 수 없음",
        evaluator_id=str(evaluation.evaluator_id),
        order=evaluation.order,
        scores_data=evaluation.scores_data or {},
        total_score=evaluation.total_score,
        overall_comment=evaluation.overall_comment,
        is_submitted=evaluation.is_submitted,
        submitted_at=evaluation.submitted_at,
        created_at=evaluation.created_at,
        updated_at=evaluation.updated_at
    )


@router.post("/{evaluation_id}/submit", response_model=EvaluationResponse)
async def submit_evaluation(
    evaluation_id: str,
    data: EvaluationSubmit = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    평가 최종 제출
    """
    evaluation = db.query(Evaluation).filter(
        Evaluation.id == evaluation_id,
        Evaluation.evaluator_id == current_user.id
    ).first()

    if not evaluation:
        raise HTTPException(status_code=404, detail="평가를 찾을 수 없습니다")

    if evaluation.is_submitted:
        raise HTTPException(status_code=400, detail="이미 제출된 평가입니다")

    # 제출 처리
    evaluation.is_submitted = True
    evaluation.submitted_at = datetime.utcnow()

    if data and data.signature_data:
        evaluation.signature_data = data.signature_data

    db.commit()
    db.refresh(evaluation)

    # 관계 로드
    db.refresh(evaluation, ["company"])
    if evaluation.company:
        db.refresh(evaluation.company, ["project"])

    return EvaluationResponse(
        id=str(evaluation.id),
        project_id=str(evaluation.project_id) if evaluation.project_id else None,
        project_name=evaluation.company.project.name if evaluation.company and evaluation.company.project else None,
        company_id=str(evaluation.company_id),
        company_name=evaluation.company.name if evaluation.company else "알 수 없음",
        evaluator_id=str(evaluation.evaluator_id),
        order=evaluation.order,
        scores_data=evaluation.scores_data or {},
        total_score=evaluation.total_score,
        overall_comment=evaluation.overall_comment,
        is_submitted=evaluation.is_submitted,
        submitted_at=evaluation.submitted_at,
        created_at=evaluation.created_at,
        updated_at=evaluation.updated_at
    )


@router.get("/project/{project_id}", response_model=List[EvaluationResponse])
async def get_evaluations_by_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    프로젝트별 평가 목록 조회 (관리자)
    """
    evaluations = db.query(Evaluation).filter(
        Evaluation.project_id == project_id
    ).options(
        joinedload(Evaluation.company),
        joinedload(Evaluation.evaluator)
    ).all()

    return [
        EvaluationResponse(
            id=str(evaluation.id),
            project_id=str(evaluation.project_id) if evaluation.project_id else None,
            project_name=evaluation.company.project.name if evaluation.company and evaluation.company.project else None,
            company_id=str(evaluation.company_id),
            company_name=evaluation.company.name if evaluation.company else "알 수 없음",
            evaluator_id=str(evaluation.evaluator_id),
            order=evaluation.order,
            scores_data=evaluation.scores_data or {},
            total_score=evaluation.total_score,
            overall_comment=evaluation.overall_comment,
            is_submitted=evaluation.is_submitted,
            submitted_at=evaluation.submitted_at,
            created_at=evaluation.created_at,
            updated_at=evaluation.updated_at
        )
        for evaluation in evaluations
    ]


@router.get("/company/{company_id}", response_model=List[EvaluationResponse])
async def get_evaluations_by_company(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    기업별 평가 목록 조회 (관리자)
    """
    evaluations = db.query(Evaluation).filter(
        Evaluation.company_id == company_id
    ).options(
        joinedload(Evaluation.company),
        joinedload(Evaluation.evaluator)
    ).all()

    return [
        EvaluationResponse(
            id=str(evaluation.id),
            project_id=str(evaluation.project_id) if evaluation.project_id else None,
            project_name=evaluation.company.project.name if evaluation.company and evaluation.company.project else None,
            company_id=str(evaluation.company_id),
            company_name=evaluation.company.name if evaluation.company else "알 수 없음",
            evaluator_id=str(evaluation.evaluator_id),
            order=evaluation.order,
            scores_data=evaluation.scores_data or {},
            total_score=evaluation.total_score,
            overall_comment=evaluation.overall_comment,
            is_submitted=evaluation.is_submitted,
            submitted_at=evaluation.submitted_at,
            created_at=evaluation.created_at,
            updated_at=evaluation.updated_at
        )
        for evaluation in evaluations
    ]


@router.get("/company/{company_id}/aggregate")
async def get_aggregated_scores(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    기업별 전체 심사위원 점수 집계
    최고/최저점 제외 평균 계산
    """
    evaluations = db.query(Evaluation).filter(
        Evaluation.company_id == company_id,
        Evaluation.is_submitted == True
    ).all()

    if not evaluations:
        return {
            "company_id": company_id,
            "average_score": 0.0,
            "trimmed_average": 0.0,
            "evaluator_count": 0
        }

    scores = [e.total_score for e in evaluations if e.total_score is not None]

    if not scores:
        return {
            "company_id": company_id,
            "average_score": 0.0,
            "trimmed_average": 0.0,
            "evaluator_count": len(evaluations)
        }

    # 평균 계산
    average_score = sum(scores) / len(scores)

    # 최고/최저 제외 평균 (3명 이상일 때만)
    trimmed_average = average_score
    if len(scores) >= 3:
        sorted_scores = sorted(scores)
        trimmed_scores = sorted_scores[1:-1]  # 최고, 최저 제외
        trimmed_average = sum(trimmed_scores) / len(trimmed_scores)

    return {
        "company_id": company_id,
        "average_score": round(average_score, 2),
        "trimmed_average": round(trimmed_average, 2),
        "evaluator_count": len(evaluations),
        "submitted_count": len(scores)
    }
