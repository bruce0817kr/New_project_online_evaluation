"""
Admin Endpoints - 관리자 API
평가 배정, 순서 조정, 통계 등 관리 기능
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.user import User
from app.models.evaluation import Evaluation
from app.models.company import Company
from app.models.project import Project
from app.services.audit_service import log_audit_event

router = APIRouter()


# ============== Schemas ==============

class AssignmentCreate(BaseModel):
    """평가 배정 생성"""
    project_id: str
    company_id: str
    evaluator_id: str
    order: int = None


class BulkAssignmentCreate(BaseModel):
    """일괄 배정 요청"""
    project_id: str
    assignments: List[dict]  # [{ company_id, evaluator_id }, ...]


class EvaluationOrderUpdate(BaseModel):
    """평가 순서 변경"""
    orders: List[dict]  # [{ evaluation_id, order }, ...]


class AssignmentResponse(BaseModel):
    """배정 응답"""
    id: str
    project_id: str
    company_id: str
    company_name: str
    company_business_number: str = None
    evaluator_id: str
    evaluator_name: str
    order: int = None
    is_submitted: bool
    submitted_at: datetime = None
    created_at: datetime

    class Config:
        orm_mode = True


class DashboardStats(BaseModel):
    """대시보드 통계"""
    total_projects: int
    total_companies: int
    total_evaluators: int
    total_evaluations: int
    evaluations_submitted: int
    evaluations_in_progress: int
    average_score: float = None
    today_submissions: int
    active_users: int


# ============== Endpoints ==============

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """대시보드 통계 조회"""

    # 기본 통계
    total_projects = db.query(func.count(Project.id)).scalar()
    total_companies = db.query(func.count(Company.id)).scalar()
    total_evaluators = db.query(func.count(User.id)).filter(User.role == "evaluator").scalar()
    total_evaluations = db.query(func.count(Evaluation.id)).scalar()

    # 평가 상태별 통계
    evaluations_submitted = db.query(func.count(Evaluation.id)).filter(
        Evaluation.is_submitted == True
    ).scalar()
    evaluations_in_progress = total_evaluations - evaluations_submitted

    # 평균 점수
    avg_score = db.query(func.avg(Evaluation.total_score)).filter(
        Evaluation.is_submitted == True
    ).scalar()

    # 오늘 제출 건수
    today = datetime.utcnow().date()
    today_submissions = db.query(func.count(Evaluation.id)).filter(
        Evaluation.is_submitted == True,
        func.date(Evaluation.submitted_at) == today
    ).scalar()

    # 활성 사용자 (최근 제출한 사용자)
    active_users = db.query(func.count(func.distinct(Evaluation.evaluator_id))).filter(
        Evaluation.is_submitted == True
    ).scalar()

    return DashboardStats(
        total_projects=total_projects or 0,
        total_companies=total_companies or 0,
        total_evaluators=total_evaluators or 0,
        total_evaluations=total_evaluations or 0,
        evaluations_submitted=evaluations_submitted or 0,
        evaluations_in_progress=evaluations_in_progress or 0,
        average_score=float(avg_score) if avg_score else None,
        today_submissions=today_submissions or 0,
        active_users=active_users or 0
    )


@router.get("/projects/{project_id}/assignments", response_model=List[AssignmentResponse])
async def get_project_assignments(
    project_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """프로젝트별 평가 배정 목록 조회"""

    # 프로젝트 존재 확인
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다")

    # 배정 목록 조회 (JOIN으로 한 번에 가져오기)
    evaluations = db.query(Evaluation).filter(
        Evaluation.project_id == project_id
    ).all()

    result = []
    for evaluation in evaluations:
        company = db.query(Company).filter(Company.id == evaluation.company_id).first()
        evaluator = db.query(User).filter(User.id == evaluation.evaluator_id).first()

        result.append(AssignmentResponse(
            id=str(evaluation.id),
            project_id=str(evaluation.project_id),
            company_id=str(evaluation.company_id),
            company_name=company.name if company else "Unknown",
            company_business_number=company.business_number if company else None,
            evaluator_id=str(evaluation.evaluator_id),
            evaluator_name=evaluator.full_name if evaluator else "Unknown",
            order=evaluation.order,
            is_submitted=evaluation.is_submitted,
            submitted_at=evaluation.submitted_at,
            created_at=evaluation.created_at
        ))

    return result


@router.post("/assignments", response_model=AssignmentResponse)
async def create_assignment(
    data: AssignmentCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """평가 배정 생성"""

    # 중복 체크
    existing = db.query(Evaluation).filter(
        Evaluation.project_id == data.project_id,
        Evaluation.company_id == data.company_id,
        Evaluation.evaluator_id == data.evaluator_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="이미 배정된 조합입니다")

    # 기업 확인
    company = db.query(Company).filter(Company.id == data.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="기업을 찾을 수 없습니다")

    # 심사위원 확인
    evaluator = db.query(User).filter(
        User.id == data.evaluator_id,
        User.role == "evaluator"
    ).first()
    if not evaluator:
        raise HTTPException(status_code=404, detail="심사위원을 찾을 수 없습니다")

    # 순서 자동 계산 (없으면)
    if data.order is None:
        max_order = db.query(func.max(Evaluation.order)).filter(
            Evaluation.evaluator_id == data.evaluator_id
        ).scalar()
        data.order = (max_order or 0) + 1

    # 평가 생성
    evaluation = Evaluation(
        project_id=data.project_id,
        company_id=data.company_id,
        evaluator_id=data.evaluator_id,
        order=data.order,
        scores_data={},
        is_submitted=False
    )

    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    # 감사 로그
    await log_audit_event(
        db=db,
        user_id=str(current_user.id),
        username=current_user.username,
        action="ASSIGNMENT_CREATE",
        resource=f"evaluation:{evaluation.id}",
        details={
            "project_id": data.project_id,
            "company_id": data.company_id,
            "evaluator_id": data.evaluator_id
        },
        status="SUCCESS"
    )

    return AssignmentResponse(
        id=str(evaluation.id),
        project_id=str(evaluation.project_id),
        company_id=str(evaluation.company_id),
        company_name=company.name,
        company_business_number=company.business_number,
        evaluator_id=str(evaluation.evaluator_id),
        evaluator_name=evaluator.full_name,
        order=evaluation.order,
        is_submitted=evaluation.is_submitted,
        submitted_at=evaluation.submitted_at,
        created_at=evaluation.created_at
    )


@router.post("/assignments/bulk")
async def bulk_assign_evaluations(
    data: BulkAssignmentCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """일괄 평가 배정"""

    created_count = 0
    skipped_count = 0
    errors = []

    for assignment in data.assignments:
        company_id = assignment.get("company_id")
        evaluator_id = assignment.get("evaluator_id")

        if not company_id or not evaluator_id:
            errors.append(f"Invalid assignment data: {assignment}")
            continue

        # 중복 체크
        existing = db.query(Evaluation).filter(
            Evaluation.project_id == data.project_id,
            Evaluation.company_id == company_id,
            Evaluation.evaluator_id == evaluator_id
        ).first()

        if existing:
            skipped_count += 1
            continue

        # 순서 자동 계산
        max_order = db.query(func.max(Evaluation.order)).filter(
            Evaluation.evaluator_id == evaluator_id
        ).scalar()
        order = (max_order or 0) + 1

        # 평가 생성
        evaluation = Evaluation(
            project_id=data.project_id,
            company_id=company_id,
            evaluator_id=evaluator_id,
            order=order,
            scores_data={},
            is_submitted=False
        )

        db.add(evaluation)
        created_count += 1

    db.commit()

    # 감사 로그
    await log_audit_event(
        db=db,
        user_id=str(current_user.id),
        username=current_user.username,
        action="BULK_ASSIGNMENT_CREATE",
        resource=f"project:{data.project_id}",
        details={
            "created": created_count,
            "skipped": skipped_count,
            "total": len(data.assignments)
        },
        status="SUCCESS"
    )

    return {
        "message": "일괄 배정이 완료되었습니다",
        "created": created_count,
        "skipped": skipped_count,
        "errors": errors
    }


@router.put("/evaluators/{evaluator_id}/evaluation-orders")
async def update_evaluation_orders(
    evaluator_id: str,
    data: EvaluationOrderUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """심사위원의 평가 순서 변경"""

    # 심사위원 확인
    evaluator = db.query(User).filter(
        User.id == evaluator_id,
        User.role == "evaluator"
    ).first()
    if not evaluator:
        raise HTTPException(status_code=404, detail="심사위원을 찾을 수 없습니다")

    updated_count = 0

    for order_data in data.orders:
        evaluation_id = order_data.get("evaluation_id")
        new_order = order_data.get("order")

        if not evaluation_id or new_order is None:
            continue

        # 평가 조회 및 업데이트
        evaluation = db.query(Evaluation).filter(
            Evaluation.id == evaluation_id,
            Evaluation.evaluator_id == evaluator_id
        ).first()

        if evaluation:
            evaluation.order = new_order
            updated_count += 1

    db.commit()

    # 감사 로그
    await log_audit_event(
        db=db,
        user_id=str(current_user.id),
        username=current_user.username,
        action="EVALUATION_ORDER_UPDATE",
        resource=f"evaluator:{evaluator_id}",
        details={"updated_count": updated_count},
        status="SUCCESS"
    )

    return {
        "message": "평가 순서가 변경되었습니다",
        "updated": updated_count
    }


@router.get("/users", response_model=List[dict])
async def get_users(
    role: str = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """사용자 목록 조회 (역할별 필터)"""

    query = db.query(User)

    if role:
        query = query.filter(User.role == role)

    users = query.all()

    return [
        {
            "id": str(user.id),
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at
        }
        for user in users
    ]


@router.post("/users", response_model=dict)
async def create_user(
    username: str,
    full_name: str,
    email: str,
    role: str,
    password: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """사용자 생성"""
    from app.core.security import get_password_hash

    # 중복 체크
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자명입니다")

    # 사용자 생성
    user = User(
        username=username,
        full_name=full_name,
        email=email,
        role=role,
        hashed_password=get_password_hash(password),
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # 감사 로그
    await log_audit_event(
        db=db,
        user_id=str(current_user.id),
        username=current_user.username,
        action="USER_CREATE",
        resource=f"user:{user.id}",
        details={"username": username, "role": role},
        status="SUCCESS"
    )

    return {
        "id": str(user.id),
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """사용자 삭제"""

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    # 자기 자신은 삭제 불가
    if str(user.id) == str(current_user.id):
        raise HTTPException(status_code=400, detail="자기 자신은 삭제할 수 없습니다")

    db.delete(user)
    db.commit()

    # 감사 로그
    await log_audit_event(
        db=db,
        user_id=str(current_user.id),
        username=current_user.username,
        action="USER_DELETE",
        resource=f"user:{user_id}",
        details={"username": user.username},
        status="SUCCESS"
    )

    return {"message": "사용자가 삭제되었습니다"}
