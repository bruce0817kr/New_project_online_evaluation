# 보안 표준 - 온프레미스 평가 시스템

## 목적
본 문서는 기업 지원 사업 평가 시스템의 보안 요구사항, 위협 모델, 대응 전략을 정의합니다.
온프레미스 환경의 특성을 고려한 실질적인 보안 가이드를 제공합니다.

## 1. 보안 원칙

### 1.1 최소 권한 원칙 (Principle of Least Privilege)
사용자는 업무 수행에 필요한 최소한의 권한만 보유합니다.

| 역할       | 권한 범위                               |
|------------|-----------------------------------------|
| 관리자     | 전체 시스템 읽기/쓰기, 사용자 관리      |
| 심사위원   | 본인에게 배정된 기업 데이터만 읽기/쓰기 |
| 일반 사용자| 자사 최종 결과 조회 (평가 완료 후)      |

### 1.2 데이터 무결성 보장
- 제출 완료 데이터는 **불변성** 유지
- 모든 중요 작업은 **감사 로그** 기록
- 데이터베이스 트랜잭션으로 **원자성** 보장

### 1.3 심층 방어 (Defense in Depth)
단일 보안 조치에 의존하지 않고 다층 보안을 적용합니다.
```
Application Layer: 입력 검증, 출력 인코딩
Authentication Layer: 비밀번호 정책, 2FA (옵션)
Authorization Layer: RBAC (Role-Based Access Control)
Database Layer: 암호화, 백업
Network Layer: 방화벽, VPN
```

## 2. 인증 및 인가

### 2.1 비밀번호 정책

#### 최소 요구사항
- **길이**: 최소 8자 이상
- **복잡도**: 영문 대소문자, 숫자, 특수문자 중 3종 이상 조합
- **재사용 제한**: 최근 3회 사용한 비밀번호 재사용 금지
- **유효기간**: 90일 (권장)

#### 구현 예시
```python
import re
from passlib.hash import bcrypt

def validate_password(password: str) -> bool:
    """비밀번호 복잡도 검증"""
    if len(password) < 8:
        return False

    complexity = sum([
        bool(re.search(r'[a-z]', password)),  # 소문자
        bool(re.search(r'[A-Z]', password)),  # 대문자
        bool(re.search(r'\d', password)),     # 숫자
        bool(re.search(r'[^a-zA-Z\d]', password))  # 특수문자
    ])

    return complexity >= 3

def hash_password(password: str) -> str:
    """bcrypt로 비밀번호 해싱"""
    return bcrypt.hash(password)
```

### 2.2 세션 관리

#### 세션 타임아웃
- **일반 세션**: 30분 무활동 시 자동 로그아웃
- **평가 세션**: 60분 (평가 중 연장 가능)
- **관리자 세션**: 15분 (보안 강화)

#### JWT 토큰 설정
```python
from datetime import timedelta
from jose import jwt

JWT_SECRET_KEY = "환경변수로 관리"  # .env 파일
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
```

### 2.3 역할 기반 접근 제어 (RBAC)

#### 권한 매트릭스
| 리소스         | 관리자 | 심사위원 | 일반 사용자 |
|----------------|--------|----------|-------------|
| 사업 관리      | C/R/U/D| R        | -           |
| 기업 서류 업로드| C/R/U/D| -        | -           |
| 평가 데이터 입력| R      | C/R/U    | -           |
| 평가 결과 조회 | R      | R (본인) | R (자사)    |
| Audit Log 조회 | R      | -        | -           |

#### FastAPI 구현 예시
```python
from fastapi import Depends, HTTPException
from app.models.user import User, UserRole

def require_role(allowed_roles: List[UserRole]):
    def decorator(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="권한이 없습니다")
        return current_user
    return decorator

# 사용 예시
@app.get("/admin/users")
def get_all_users(user: User = Depends(require_role([UserRole.ADMIN]))):
    # 관리자만 접근 가능
    pass
```

## 3. 데이터 보호

### 3.1 데이터 암호화

#### 저장 시 암호화 (Encryption at Rest)
- **민감 정보**: AES-256-GCM 암호화
  - 사업자등록번호
  - 대표자 주민번호 (수집 시)
  - 은행 계좌 정보

```python
from cryptography.fernet import Fernet
import os

class DataEncryption:
    def __init__(self):
        # 환경 변수에서 키 로드
        key = os.getenv("ENCRYPTION_KEY").encode()
        self.cipher = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self.cipher.decrypt(ciphertext.encode()).decode()
```

#### 전송 중 암호화 (Encryption in Transit)
- **HTTPS 필수**: TLS 1.2 이상
- **인증서**: Let's Encrypt 또는 자체 서명 (내부망)
- **HSTS 헤더**: `Strict-Transport-Security: max-age=31536000`

### 3.2 파일 업로드 보안

#### 허용 파일 유형
```python
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_upload(file):
    # 확장자 검증
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("허용되지 않은 파일 형식")

    # 크기 검증
    if file.size > MAX_FILE_SIZE:
        raise ValueError("파일 크기 초과 (최대 10MB)")

    # MIME 타입 검증
    import magic
    mime_type = magic.from_buffer(file.read(1024), mime=True)
    if mime_type not in ['application/pdf', 'image/jpeg', 'image/png']:
        raise ValueError("파일 내용이 확장자와 일치하지 않습니다")

    file.seek(0)  # 파일 포인터 리셋
```

#### 안전한 파일 저장
```python
import uuid
from pathlib import Path

def save_upload_file(file, upload_dir: str = "/var/uploads"):
    # 원본 파일명 사용 금지 (경로 탐색 공격 방지)
    safe_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"

    # 절대 경로 사용
    upload_path = Path(upload_dir).resolve()
    file_path = upload_path / safe_filename

    # 경로 탐색 방지
    if not str(file_path).startswith(str(upload_path)):
        raise ValueError("잘못된 경로")

    with open(file_path, "wb") as f:
        f.write(file.read())

    return file_path
```

### 3.3 PDF 스트리밍 보안
PDF 파일은 직접 URL 노출을 금지하고 Stream 방식으로 제공합니다.

```python
from fastapi import StreamingResponse
from fastapi.responses import FileResponse

@app.get("/api/v1/files/{file_id}")
async def stream_pdf(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    # 권한 검증
    file_record = await get_file_by_id(file_id)
    if not can_access_file(current_user, file_record):
        raise HTTPException(status_code=403, detail="접근 권한 없음")

    # 스트리밍 응답
    def iterfile():
        with open(file_record.path, "rb") as f:
            yield from f

    return StreamingResponse(
        iterfile(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": "inline; filename=document.pdf",
            "X-Content-Type-Options": "nosniff"
        }
    )
```

## 4. 입력 검증 및 출력 인코딩

### 4.1 SQL Injection 방어
**절대 사용 금지**:
```python
# 취약한 코드
query = f"SELECT * FROM users WHERE id = {user_id}"
db.execute(query)
```

**권장 방법** (SQLAlchemy ORM):
```python
from sqlalchemy import select

# ORM 사용
user = db.query(User).filter(User.id == user_id).first()

# 또는 파라미터 바인딩
query = select(User).where(User.id == :user_id)
result = db.execute(query, {"user_id": user_id})
```

### 4.2 XSS (Cross-Site Scripting) 방어

#### 백엔드: 입력 검증
```python
from pydantic import BaseModel, validator
import bleach

class EvaluationInput(BaseModel):
    comment: str

    @validator('comment')
    def sanitize_comment(cls, v):
        # HTML 태그 제거
        return bleach.clean(v, tags=[], strip=True)
```

#### 프론트엔드: 출력 인코딩
```javascript
// React에서는 기본적으로 XSS 방어
// dangerouslySetInnerHTML 사용 금지

function CommentDisplay({ comment }) {
  // 안전: 자동 이스케이핑
  return <div>{comment}</div>;

  // 위험: 절대 사용 금지
  // return <div dangerouslySetInnerHTML={{ __html: comment }} />;
}
```

### 4.3 CSRF (Cross-Site Request Forgery) 방어

```python
from fastapi_csrf_protect import CsrfProtect

@app.post("/api/v1/evaluations/submit")
async def submit_evaluation(
    csrf_protect: CsrfProtect = Depends()
):
    await csrf_protect.validate_csrf_in_cookies(request)
    # 평가 제출 로직
```

## 5. 감사 로그 (Audit Trail)

### 5.1 기록 대상 이벤트
다음 이벤트는 반드시 로그에 기록:
- [ ] 로그인/로그아웃 시도 (성공/실패)
- [ ] 권한 변경
- [ ] 평가 데이터 생성/수정/제출
- [ ] 파일 업로드/다운로드
- [ ] 관리자 데이터 조회
- [ ] 설정 변경

### 5.2 로그 형식
```json
{
  "timestamp": "2026-01-09T12:34:56Z",
  "user_id": 123,
  "username": "evaluator1",
  "ip_address": "192.168.1.100",
  "action": "EVALUATION_SUBMIT",
  "resource": "evaluation:456",
  "details": {
    "company_id": 789,
    "total_score": 87.5
  },
  "status": "SUCCESS"
}
```

### 5.3 구현 예시
```python
from app.models.audit_log import AuditLog
from fastapi import Request

async def log_audit_event(
    user: User,
    action: str,
    resource: str,
    details: dict,
    request: Request,
    status: str = "SUCCESS"
):
    log = AuditLog(
        user_id=user.id,
        username=user.username,
        ip_address=request.client.host,
        action=action,
        resource=resource,
        details=details,
        status=status
    )
    await db.add(log)
    await db.commit()
```

### 5.4 로그 보존 정책
- **보존 기간**: 최소 3년
- **백업**: 월 1회 외부 저장소
- **조회 권한**: 관리자만
- **무결성**: 로그 변조 방지 (Hash Chain)

## 6. 온프레미스 환경 보안

### 6.1 네트워크 분리
```
[인터넷]
   |
[방화벽] - 외부 접근 차단
   |
[리버스 프록시 (Nginx)]
   |
   +-- [Frontend Container] (React)
   |
   +-- [Backend Container] (FastAPI)
   |
   +-- [Database Container] (PostgreSQL) - 외부 접근 불가
```

### 6.2 Docker 보안 설정

#### Dockerfile 최적화
```dockerfile
# 비root 사용자 실행
FROM python:3.10-slim
RUN useradd -m -u 1000 appuser

# 불필요한 패키지 제거
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
 && rm -rf /var/lib/apt/lists/*

USER appuser
WORKDIR /app
```

#### docker-compose.yml 보안
```yaml
services:
  backend:
    read_only: true  # 파일시스템 읽기 전용
    security_opt:
      - no-new-privileges:true  # 권한 상승 방지
    cap_drop:
      - ALL  # 불필요한 권한 제거
    networks:
      - internal  # 내부 네트워크만 사용

  db:
    networks:
      - internal  # 외부 접근 차단
    volumes:
      - ./data:/var/lib/postgresql/data:rw,Z  # SELinux 레이블
```

### 6.3 환경 변수 관리
```bash
# .env 파일은 절대 Git에 커밋 금지
.env
.env.local
.env.production

# 예시: .env.example (템플릿만 제공)
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=generate-random-key-here
ENCRYPTION_KEY=generate-encryption-key-here
```

## 7. 취약점 대응

### 7.1 보안 업데이트 정책
- **주기**: 월 1회 보안 패치 적용
- **긴급 패치**: 치명적 취약점 발견 시 24시간 내
- **테스트**: 스테이징 환경에서 1주일 테스트 후 프로덕션 적용

### 7.2 취약점 스캐닝
```bash
# Python 의존성 취약점 검사
pip install safety
safety check

# Docker 이미지 스캔
docker scan backend:latest

# OWASP ZAP 자동화 스캔
zap-cli quick-scan http://localhost:8000
```

### 7.3 침해 대응 절차
1. **탐지**: 비정상 로그인 시도, 이상 트래픽 감지
2. **격리**: 의심 계정 즉시 비활성화
3. **분석**: Audit Log 및 시스템 로그 분석
4. **복구**: 백업에서 복원 (필요 시)
5. **보고**: 관리자 및 책임자에게 보고
6. **개선**: 재발 방지 대책 수립

## 8. 백업 및 재해 복구

### 8.1 백업 전략 (3-2-1 규칙)
- **3개 복사본**: 원본 + 2개 백업
- **2개 매체**: 로컬 디스크 + 외부 스토리지
- **1개 원격**: 물리적으로 분리된 위치

### 8.2 백업 스크립트
```bash
#!/bin/bash
# daily_backup.sh

BACKUP_DIR="/var/backups/evaluation_system"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# PostgreSQL 백업
docker exec postgres pg_dump -U postgres evaluation_db | gzip > \
  "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"

# 파일 백업
tar -czf "$BACKUP_DIR/files_$TIMESTAMP.tar.gz" /var/uploads

# 30일 이전 백업 삭제
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $TIMESTAMP"
```

### 8.3 복구 테스트
- **주기**: 분기 1회
- **시나리오**: DB 손상, 파일 손실, 전체 시스템 장애
- **목표**: RPO(복구 시점) < 24시간, RTO(복구 시간) < 4시간

## 9. 보안 체크리스트

### 9.1 개발 단계
- [ ] 입력 검증 로직 구현
- [ ] SQL Injection 방어 (ORM 사용)
- [ ] XSS 방어 (출력 인코딩)
- [ ] CSRF 토큰 적용
- [ ] 비밀번호 해싱 (bcrypt)
- [ ] 환경 변수로 비밀 정보 관리

### 9.2 배포 단계
- [ ] HTTPS 인증서 설정
- [ ] 방화벽 규칙 적용
- [ ] Docker 컨테이너 보안 설정
- [ ] DB 외부 접근 차단
- [ ] Audit Log 활성화
- [ ] 백업 스크립트 cron 등록

### 9.3 운영 단계
- [ ] 보안 패치 월 1회 적용
- [ ] Audit Log 주간 리뷰
- [ ] 비정상 접근 모니터링
- [ ] 백업 복구 테스트 (분기 1회)
- [ ] 사용자 권한 정기 검토

## 10. 관련 표준 및 규정

- **개인정보보호법**: 기업 정보 및 평가 데이터 보호
- **OWASP Top 10**: 웹 애플리케이션 보안 취약점 대응
- **ISO 27001**: 정보 보안 관리 체계
- **NIST Cybersecurity Framework**: 사이버 보안 프레임워크

## 11. 문의

보안 이슈 발견 시:
- **긴급**: 시스템 관리자에게 즉시 연락
- **일반**: security@company.com

---

**본 보안 표준은 시스템의 기밀성(Confidentiality), 무결성(Integrity), 가용성(Availability)을 보장하기 위한 최소 요구사항입니다.**
