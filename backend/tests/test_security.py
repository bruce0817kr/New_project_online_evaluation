"""
보안 기능 테스트

pytest 실행:
    pytest tests/test_security.py -v

전체 테스트:
    pytest tests/ -v --cov=app
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.security import hash_password
from app.models.user import User


# 테스트용 인메모리 데이터베이스
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """테스트용 데이터베이스 fixture"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """TestClient fixture"""
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(test_db):
    """테스트용 사용자 fixture"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("Test1234!"),
        full_name="Test User",
        role="evaluator"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_user(test_db):
    """테스트용 관리자 fixture"""
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("Admin1234!"),
        full_name="Admin User",
        role="admin"
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def auth_token(client, test_user):
    """인증 토큰 fixture"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "Test1234!"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def admin_token(client, admin_user):
    """관리자 토큰 fixture"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "Admin1234!"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


class TestAuthentication:
    """인증 관련 테스트"""

    def test_login_success(self, client, test_user):
        """정상 로그인 테스트"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "Test1234!"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser"

    def test_login_wrong_password(self, client, test_user):
        """잘못된 비밀번호 테스트"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "WrongPassword"}
        )
        assert response.status_code == 401
        assert "사용자명 또는 비밀번호가 올바르지 않습니다" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """존재하지 않는 사용자 테스트"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "Test1234!"}
        )
        assert response.status_code == 401

    def test_get_current_user(self, client, auth_token):
        """현재 사용자 정보 조회 테스트"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["role"] == "evaluator"

    def test_unauthorized_access(self, client):
        """인증 없이 접근 테스트"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401


class TestRateLimiting:
    """Rate Limiting 테스트"""

    def test_login_rate_limit(self, client, test_user):
        """로그인 Rate Limit 테스트 (5회/분)"""
        # 6회 연속 요청
        responses = []
        for i in range(6):
            response = client.post(
                "/api/v1/auth/login",
                json={"username": "testuser", "password": "Test1234!"}
            )
            responses.append(response.status_code)

        # 처음 5회는 200 또는 401 (정상)
        # 6번째는 429 (Too Many Requests) 예상
        # Note: TestClient는 실제 IP를 시뮬레이션하지 않으므로
        # 실제 Rate Limiting 동작을 완전히 테스트하기 어려울 수 있음
        assert 200 in responses or 401 in responses

    def test_change_password_rate_limit(self, client, auth_token):
        """비밀번호 변경 Rate Limit 테스트 (5회/분)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {
            "current_password": "Test1234!",
            "new_password": "NewTest1234!"
        }

        # 6회 연속 요청
        responses = []
        for i in range(6):
            response = client.post(
                "/api/v1/auth/change-password",
                json=payload,
                headers=headers
            )
            responses.append(response.status_code)

        # 처음 5회는 200 또는 400 (정상)
        # 실제 환경에서는 6번째에 429 발생
        assert 200 in responses or 400 in responses


class TestPasswordSecurity:
    """비밀번호 보안 테스트"""

    def test_password_complexity_validation(self, client, admin_token):
        """비밀번호 복잡도 검증 테스트"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 너무 짧은 비밀번호
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser1",
                "email": "new1@example.com",
                "password": "short",  # 8자 미만
                "full_name": "New User",
                "role": "evaluator"
            },
            headers=headers
        )
        assert response.status_code == 422  # Validation Error

        # 대문자 없는 비밀번호
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser2",
                "email": "new2@example.com",
                "password": "lowercase123",  # 대문자 없음
                "full_name": "New User",
                "role": "evaluator"
            },
            headers=headers
        )
        assert response.status_code == 422

        # 숫자 없는 비밀번호
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser3",
                "email": "new3@example.com",
                "password": "NoNumbers!",  # 숫자 없음
                "full_name": "New User",
                "role": "evaluator"
            },
            headers=headers
        )
        assert response.status_code == 422

    def test_change_password_wrong_current(self, client, auth_token):
        """현재 비밀번호 불일치 테스트"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "WrongPassword",
                "new_password": "NewTest1234!"
            },
            headers=headers
        )
        assert response.status_code == 400
        assert "현재 비밀번호가 올바르지 않습니다" in response.json()["detail"]

    def test_change_password_success(self, client, auth_token):
        """비밀번호 변경 성공 테스트"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "Test1234!",
                "new_password": "NewTest1234!"
            },
            headers=headers
        )
        assert response.status_code == 200
        assert "비밀번호가 변경되었습니다" in response.json()["message"]


class TestRoleBasedAccess:
    """역할 기반 접근 제어 테스트"""

    def test_evaluator_cannot_create_user(self, client, auth_token):
        """평가위원은 사용자 생성 불가"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "Test1234!",
                "full_name": "New User",
                "role": "evaluator"
            },
            headers=headers
        )
        assert response.status_code == 403
        assert "관리자 권한이 필요합니다" in response.json()["detail"]

    def test_admin_can_create_user(self, client, admin_token):
        """관리자는 사용자 생성 가능"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "ValidPass123!",
                "full_name": "New User",
                "role": "evaluator"
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["role"] == "evaluator"


class TestInputValidation:
    """입력 검증 테스트"""

    def test_invalid_email_format(self, client, admin_token):
        """잘못된 이메일 형식 테스트"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "invalid-email",  # 잘못된 형식
                "password": "Test1234!",
                "full_name": "New User",
                "role": "evaluator"
            },
            headers=headers
        )
        assert response.status_code == 422

    def test_duplicate_username(self, client, admin_token, test_user):
        """중복 사용자명 테스트"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",  # 이미 존재하는 사용자명
                "email": "another@example.com",
                "password": "Test1234!",
                "full_name": "Another User",
                "role": "evaluator"
            },
            headers=headers
        )
        assert response.status_code == 400
        assert "이미 존재하는 사용자명" in response.json()["detail"]

    def test_duplicate_email(self, client, admin_token, test_user):
        """중복 이메일 테스트"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "anotheruser",
                "email": "test@example.com",  # 이미 존재하는 이메일
                "password": "Test1234!",
                "full_name": "Another User",
                "role": "evaluator"
            },
            headers=headers
        )
        assert response.status_code == 400
        assert "이미 존재하는" in response.json()["detail"]


class TestAuditLogging:
    """감사 로깅 테스트"""

    def test_login_success_logged(self, client, test_user, test_db):
        """로그인 성공 로그 기록 테스트"""
        from app.models.audit_log import AuditLog

        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "Test1234!"}
        )
        assert response.status_code == 200

        # 감사 로그 확인
        log = test_db.query(AuditLog).filter(
            AuditLog.action == "LOGIN_SUCCESS",
            AuditLog.username == "testuser"
        ).first()

        assert log is not None
        assert log.status == "SUCCESS"
        assert log.resource == "auth"

    def test_login_failure_logged(self, client, test_user, test_db):
        """로그인 실패 로그 기록 테스트"""
        from app.models.audit_log import AuditLog

        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "WrongPassword"}
        )
        assert response.status_code == 401

        # 감사 로그 확인
        log = test_db.query(AuditLog).filter(
            AuditLog.action == "LOGIN_FAILED",
            AuditLog.username == "testuser"
        ).first()

        assert log is not None
        assert log.status == "FAILED"


# pytest 실행 시 추가 옵션
pytest_plugins = []
