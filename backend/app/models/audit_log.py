"""
Audit Log Model - 점수 수정 이력 추적
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey("evaluations.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # 변경 내용
    action = Column(String(50), nullable=False)  # 'create', 'update', 'submit'
    changes = Column(JSON)  # 변경된 필드와 값

    # IP 및 추가 메타데이터
    ip_address = Column(String(45))
    user_agent = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
