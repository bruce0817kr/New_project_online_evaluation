"""
Scoring Template Endpoints - 평가 배점표 템플릿 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, validator

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.user import User
from app.models.scoring_template import ScoringTemplate

router = APIRouter()


# ============== Schemas ==============

class ScoringItem(BaseModel):
    """평가 항목"""
    item_id: str
    title: str
    description: str = ""
    max_score: int
    input_type: str = "NUMBER"  # NUMBER, RADIO, SELECT
    step: int = 1


class ScoringSection(BaseModel):
    """평가 섹션 (대분류)"""
    section_name: str
    max_score: int
    items: List[ScoringItem]


class TemplateCreate(BaseModel):
    """템플릿 생성"""
    name: str
    description: str = ""
    total_score: int = 100
    sections: List[ScoringSection]

    @validator('sections')
    def validate_sections(cls, sections, values):
        """섹션 합계가 total_score와 일치하는지 검증"""
        if 'total_score' in values:
            section_total = sum(s.max_score for s in sections)
            if section_total != values['total_score']:
                raise ValueError(
                    f"섹션 배점 합계({section_total})가 총점({values['total_score']})과 일치하지 않습니다"
                )

        # 각 섹션의 항목 합계 검증
        for section in sections:
            items_total = sum(item.max_score for item in section.items)
            if items_total != section.max_score:
                raise ValueError(
                    f"'{section.section_name}' 섹션의 항목 배점 합계({items_total})가 "
                    f"섹션 배점({section.max_score})과 일치하지 않습니다"
                )

        return sections


class TemplateUpdate(BaseModel):
    """템플릿 수정"""
    name: Optional[str] = None
    description: Optional[str] = None
    sections: Optional[List[ScoringSection]] = None
    is_active: Optional[bool] = None


class TemplateResponse(BaseModel):
    """템플릿 응답"""
    id: str
    name: str
    description: str = ""
    total_score: int
    sections: List[dict]
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime = None

    class Config:
        orm_mode = True


# ============== Endpoints ==============

@router.get("/", response_model=List[TemplateResponse])
async def list_templates(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    템플릿 목록 조회
    """
    query = db.query(ScoringTemplate)

    if active_only:
        query = query.filter(ScoringTemplate.is_active == True)

    templates = query.order_by(
        ScoringTemplate.is_default.desc(),
        ScoringTemplate.created_at.desc()
    ).all()

    return [
        TemplateResponse(
            id=str(template.id),
            name=template.name,
            description=template.description or "",
            total_score=template.total_score,
            sections=template.sections.get("sections", []) if template.sections else [],
            is_active=template.is_active,
            is_default=template.is_default,
            created_at=template.created_at,
            updated_at=template.updated_at
        )
        for template in templates
    ]


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    템플릿 상세 조회
    """
    template = db.query(ScoringTemplate).filter(
        ScoringTemplate.id == template_id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        description=template.description or "",
        total_score=template.total_score,
        sections=template.sections.get("sections", []) if template.sections else [],
        is_active=template.is_active,
        is_default=template.is_default,
        created_at=template.created_at,
        updated_at=template.updated_at
    )


@router.post("/", response_model=TemplateResponse)
async def create_template(
    data: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    새 템플릿 생성 (관리자)
    """
    # 섹션 데이터를 JSON으로 변환
    sections_json = {
        "sections": [section.dict() for section in data.sections]
    }

    template = ScoringTemplate(
        name=data.name,
        description=data.description,
        total_score=data.total_score,
        sections=sections_json,
        created_by=current_user.id
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        description=template.description or "",
        total_score=template.total_score,
        sections=template.sections.get("sections", []),
        is_active=template.is_active,
        is_default=template.is_default,
        created_at=template.created_at,
        updated_at=template.updated_at
    )


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    data: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    템플릿 수정 (관리자)
    """
    template = db.query(ScoringTemplate).filter(
        ScoringTemplate.id == template_id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

    # 업데이트
    if data.name is not None:
        template.name = data.name

    if data.description is not None:
        template.description = data.description

    if data.sections is not None:
        template.sections = {
            "sections": [section.dict() for section in data.sections]
        }

    if data.is_active is not None:
        template.is_active = data.is_active

    template.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(template)

    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        description=template.description or "",
        total_score=template.total_score,
        sections=template.sections.get("sections", []),
        is_active=template.is_active,
        is_default=template.is_default,
        created_at=template.created_at,
        updated_at=template.updated_at
    )


@router.patch("/{template_id}/toggle-active")
async def toggle_template_active(
    template_id: str,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    템플릿 활성화/비활성화 (관리자)
    """
    template = db.query(ScoringTemplate).filter(
        ScoringTemplate.id == template_id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

    is_active = data.get("is_active", True)
    template.is_active = is_active
    template.updated_at = datetime.utcnow()
    db.commit()

    return {"message": f"템플릿이 {'활성화' if is_active else '비활성화'}되었습니다"}


@router.post("/{template_id}/set-default")
async def set_default_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    기본 템플릿 설정 (관리자)
    """
    template = db.query(ScoringTemplate).filter(
        ScoringTemplate.id == template_id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

    # 기존 기본 템플릿 해제
    db.query(ScoringTemplate).update({"is_default": False})

    # 새 기본 템플릿 설정
    template.is_default = True
    db.commit()

    return {"message": "기본 템플릿이 설정되었습니다"}


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    템플릿 삭제 (관리자)
    """
    template = db.query(ScoringTemplate).filter(
        ScoringTemplate.id == template_id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

    if template.is_default:
        raise HTTPException(
            status_code=400,
            detail="기본 템플릿은 삭제할 수 없습니다. 먼저 다른 템플릿을 기본으로 설정하세요"
        )

    # Soft delete (is_active = False)
    template.is_active = False
    db.commit()

    return {"message": "템플릿이 삭제되었습니다"}


@router.post("/create-default")
async def create_default_template(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    기본 R&D 평가 템플릿 생성 (초기 설정용)
    """
    # 기본 템플릿이 이미 있는지 확인
    existing = db.query(ScoringTemplate).filter(
        ScoringTemplate.is_default == True
    ).first()

    if existing:
        return {"message": "기본 템플릿이 이미 존재합니다", "template_id": str(existing.id)}

    # 기본 R&D 평가 템플릿 생성
    default_sections = {
        "sections": [
            {
                "section_name": "기술성",
                "max_score": 40,
                "items": [
                    {
                        "item_id": "tech_1",
                        "title": "기술의 차별성 및 독창성",
                        "description": "기존 기술 대비 독창적인가?",
                        "max_score": 20,
                        "input_type": "NUMBER",
                        "step": 1
                    },
                    {
                        "item_id": "tech_2",
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
                "max_score": 40,
                "items": [
                    {
                        "item_id": "biz_1",
                        "title": "시장 진입 가능성",
                        "description": "타겟 시장 분석이 명확한가?",
                        "max_score": 20,
                        "input_type": "NUMBER",
                        "step": 1
                    },
                    {
                        "item_id": "biz_2",
                        "title": "사업화 의지 및 역량",
                        "description": "대표자의 역량 및 의지",
                        "max_score": 20,
                        "input_type": "NUMBER",
                        "step": 1
                    }
                ]
            },
            {
                "section_name": "경제성",
                "max_score": 20,
                "items": [
                    {
                        "item_id": "econ_1",
                        "title": "경제적 파급효과",
                        "description": "사회적·경제적 파급효과",
                        "max_score": 20,
                        "input_type": "NUMBER",
                        "step": 1
                    }
                ]
            }
        ]
    }

    template = ScoringTemplate(
        name="R&D 표준 평가 템플릿",
        description="연구개발 과제 선정평가 표준 템플릿 (기술성 40점, 사업성 40점, 경제성 20점)",
        total_score=100,
        sections=default_sections,
        is_default=True,
        created_by=current_user.id
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return {
        "message": "기본 템플릿이 생성되었습니다",
        "template_id": str(template.id)
    }
