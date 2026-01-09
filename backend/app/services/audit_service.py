"""
Audit Log Service - 감사 추적

참고: .claude/skills/biz-support-eval-dev/references/security_standard.md
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime

from app.models.audit_log import AuditLog


async def log_audit_event(
    db: Session,
    user_id: Optional[str],
    username: str,
    action: str,
    resource: str,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    status: str = "SUCCESS"
) -> AuditLog:
    """
    감사 로그 기록

    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID (UUID)
        username: 사용자명
        action: 작업 유형 (LOGIN, LOGOUT, EVALUATION_SUBMIT 등)
        resource: 대상 리소스 (auth, evaluation:123 등)
        details: 추가 상세 정보 (JSONB)
        ip_address: IP 주소
        status: 성공/실패 (SUCCESS, FAILED)

    Returns:
        생성된 AuditLog 객체
    """
    audit_log = AuditLog(
        user_id=user_id,
        username=username,
        action=action,
        resource=resource,
        details=details or {},
        ip_address=ip_address,
        status=status
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log


def get_audit_logs(
    db: Session,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100
) -> list[AuditLog]:
    """
    감사 로그 조회

    Args:
        db: 데이터베이스 세션
        user_id: 특정 사용자 필터
        action: 특정 작업 필터
        limit: 최대 조회 개수

    Returns:
        AuditLog 리스트 (최신순)
    """
    query = db.query(AuditLog)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    if action:
        query = query.filter(AuditLog.action == action)

    return query.order_by(AuditLog.created_at.desc()).limit(limit).all()
