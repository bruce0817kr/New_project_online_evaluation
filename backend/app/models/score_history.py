"""
Score History Model - 점수 변경 이력
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class ScoreHistory(Base):
    """점수 변경 이력 테이블"""
    __tablename__ = "score_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # 관계 필드
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False, index=True)
    evaluator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # 변경 내용
    item_id = Column(String(100), nullable=False)  # 평가 항목 ID
    item_name = Column(String(200), nullable=True)  # 평가 항목 이름
    old_score = Column(Float, nullable=True)  # 이전 점수
    new_score = Column(Float, nullable=False)  # 새 점수

    # 메타 정보
    change_type = Column(String(50), default="UPDATE")  # CREATE, UPDATE, DELETE
    ip_address = Column(String(50), nullable=True)  # 변경 IP
    user_agent = Column(String(500), nullable=True)  # User Agent

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    evaluation = relationship("Evaluation", back_populates="score_history")
    evaluator = relationship("User")

    def __repr__(self):
        return f"<ScoreHistory(evaluation_id={self.evaluation_id}, item_id={self.item_id}, {self.old_score}->{self.new_score})>"
