"""
Evaluation Schemas - 평가 관련 스키마
"""
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime


class EvaluationBase(BaseModel):
    """평가 기본 스키마"""
    scores_data: Dict[str, Any]
    overall_comment: Optional[str] = None


class EvaluationCreate(EvaluationBase):
    """평가 생성"""
    company_id: str
    evaluator_id: str


class EvaluationUpdate(BaseModel):
    """평가 임시 저장 (Auto-save)"""
    scores_data: Optional[Dict[str, Any]] = None
    overall_comment: Optional[str] = None


class EvaluationSubmit(EvaluationBase):
    """평가 최종 제출"""
    signature_data: str  # Base64 이미지
    total_score: float
    weighted_score: Optional[float] = None


class EvaluationResponse(BaseModel):
    """평가 응답"""
    id: str
    company_id: str
    evaluator_id: str
    scores_data: Dict[str, Any]
    overall_comment: Optional[str]
    total_score: Optional[float]
    weighted_score: Optional[float]
    is_submitted: bool
    submitted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AggregatedScoreResponse(BaseModel):
    """점수 집계 응답"""
    company_id: str
    company_name: str
    evaluations_count: int
    average_score: float
    trimmed_average: float
    min_score: float
    max_score: float
    std_dev: float
