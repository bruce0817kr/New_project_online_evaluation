"""
Company Model - 평가 대상 기업
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    business_number = Column(String(50), nullable=False)  # 사업자등록번호
    ceo_name = Column(String(100))  # 대표자명

    # OCR 추출 데이터 (JSONB로 유연하게 저장)
    ocr_data = Column(JSON)

    # 첨부 파일 경로
    document_path = Column(String(500))  # 사업계획서 등 주요 서류
    attachment_paths = Column(JSON)  # 추가 첨부파일들

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="companies")
    evaluations = relationship("Evaluation", back_populates="company", cascade="all, delete-orphan")
