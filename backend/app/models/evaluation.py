"""
Evaluation Model - 평가 데이터
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Float, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    evaluator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    order = Column(Float, nullable=True)  # 심사위원별 평가 순서

    # 평가 점수 데이터 (JSONB로 유연하게 저장)
    # 예시: {"항목1": 85, "항목2": 90, "항목3": {"세부1": 20, "세부2": 15}}
    scores_data = Column(JSON, nullable=False, default={})

    # 종합 점수 (자동 계산)
    total_score = Column(Float)
    weighted_score = Column(Float)

    # 종합 의견
    overall_comment = Column(Text)

    # 제출 상태
    is_submitted = Column(Boolean, default=False, nullable=False)
    submitted_at = Column(DateTime)

    # 전자 서명 (Canvas Base64 이미지 데이터)
    signature_data = Column(Text)

    # 부인 방지용 메타데이터
    submit_ip = Column(String(45), nullable=True)  # IPv6 지원
    submit_user_agent = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="evaluations")
    evaluator = relationship("User")
    score_history = relationship("ScoreHistory", back_populates="evaluation", cascade="all, delete-orphan")
