"""
Project Model - 사업 프로젝트
"""
from sqlalchemy import Column, String, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class ProjectStage(str, enum.Enum):
    DOCUMENT = "document"  # 서류 평가
    PRESENTATION = "presentation"  # 발표 평가


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"  # 준비 중
    IN_PROGRESS = "in_progress"  # 평가 진행 중
    COMPLETED = "completed"  # 평가 완료
    ARCHIVED = "archived"  # 종료됨


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    stage = Column(Enum(ProjectStage), nullable=False, default=ProjectStage.DOCUMENT)
    status = Column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.DRAFT)
    year = Column(String(4), nullable=False)  # 사업 연도
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    companies = relationship("Company", back_populates="project", cascade="all, delete-orphan")
