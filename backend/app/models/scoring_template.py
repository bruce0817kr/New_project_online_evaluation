"""
Scoring Template Model - 평가 배점표 템플릿
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class ScoringTemplate(Base):
    """
    평가 배점표 템플릿

    사업마다 다른 평가 기준(항목, 배점)을 관리하기 위한 템플릿
    JSON 형태로 유연하게 저장하여 다양한 평가 유형 지원
    """
    __tablename__ = "scoring_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)  # 템플릿명 (예: "R&D 표준안")
    description = Column(Text)  # 템플릿 설명

    # 총점
    total_score = Column(Integer, default=100, nullable=False)

    # 평가 항목 구조 (JSON)
    # 예시 구조는 아래 참조
    sections = Column(JSON, nullable=False)

    # 템플릿 상태
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)  # 기본 템플릿 여부

    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))  # 생성자 ID

    # Relationships
    # projects = relationship("Project", back_populates="scoring_template")


"""
JSON 구조 예시:

{
  "sections": [
    {
      "section_name": "기술성",
      "max_score": 40,
      "items": [
        {
          "item_id": "Q1",
          "title": "기술의 차별성 및 독창성",
          "description": "기존 기술 대비 독창적인가?",
          "max_score": 20,
          "input_type": "NUMBER",
          "step": 1
        },
        {
          "item_id": "Q2",
          "title": "개발 계획의 구체성",
          "description": "로드맵이 실현 가능한가?",
          "max_score": 20,
          "input_type": "NUMBER",
          "step": 1
        }
      ]
    },
    {
      "section_name": "사업성",
      "max_score": 60,
      "items": [
        {
          "item_id": "Q3",
          "title": "시장 진입 가능성",
          "description": "타겟 시장 분석이 명확한가?",
          "max_score": 30,
          "input_type": "NUMBER",
          "step": 1
        },
        {
          "item_id": "Q4",
          "title": "사업화 의지",
          "description": "대표자의 역량 및 의지",
          "max_score": 30,
          "input_type": "NUMBER",
          "step": 1
        }
      ]
    }
  ]
}
"""
