# 보안 가이드 (Security Guide)

중소기업 선정평가 시스템의 보안 구현 및 모범 사례 문서입니다.

## 📋 목차

1. [인증 및 권한 관리](#인증-및-권한-관리)
2. [API 보안](#api-보안)
3. [데이터 보호](#데이터-보호)
4. [감사 및 로깅](#감사-및-로깅)
5. [배포 보안](#배포-보안)
6. [보안 체크리스트](#보안-체크리스트)

---

## 인증 및 권한 관리

### JWT 토큰 기반 인증

**구현 위치**: `backend/app/core/security.py`

```python
# JWT 토큰 생성
access_token = create_access_token(
    data={"sub": str(user.id), "username": user.username, "role": user.role},
    expires_delta=timedelta(minutes=480)  # 8시간
)
```

**보안 설정**:
- ✅ **알고리즘**: HS256 (HMAC with SHA-256)
- ✅ **만료 시간**: 8시간 (조정 가능)
- ✅ **SECRET_KEY**: 환경 변수로 관리 (최소 32자)

**권장사항**:
```bash
# 강력한 SECRET_KEY 생성
openssl rand -hex 32
```

### 역할 기반 접근 제어 (RBAC)

**역할 정의**:
- `admin`: 모든 기능 접근 가능
- `evaluator`: 평가 기능만 접근 가능

**구현 예시**:
```python
from app.core.security import get_current_user, require_role

@router.post("/register")
async def register_user(current_admin: User = Depends(get_current_user)):
    if current_admin.role != "admin":
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")
```

### 비밀번호 보안

**해싱 알고리즘**: bcrypt
- ✅ **Salt rounds**: 자동 (bcrypt 기본값: 12)
- ✅ **복잡도 검증**: Pydantic validator 적용

**구현**: `backend/app/schemas/auth.py`
```python
@validator('password')
def validate_password(cls, v):
    if len(v) < 8:
        raise ValueError('비밀번호는 최소 8자 이상이어야 합니다')
    if not any(c.isupper() for c in v):
        raise ValueError('비밀번호에 대문자가 포함되어야 합니다')
    if not any(c.isdigit() for c in v):
        raise ValueError('비밀번호에 숫자가 포함되어야 합니다')
    return v
```

---

## API 보안

### Rate Limiting (속도 제한)

**라이브러리**: slowapi
**구현 위치**: `backend/app/main.py`, `backend/app/api/v1/endpoints/auth.py`

**보호 엔드포인트**:

| 엔드포인트 | 제한 | 목적 |
|-----------|------|------|
| `/api/v1/auth/login` | 5회/분 | 브루트포스 공격 방지 |
| `/api/v1/auth/register` | 3회/분 | 스팸 계정 생성 방지 |
| `/api/v1/auth/change-password` | 5회/분 | 비밀번호 변경 남용 방지 |

**구현 예시**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    ...
```

**프록시 환경 고려**:
- `X-Forwarded-For` 헤더 지원
- 실제 클라이언트 IP 추출

### CORS (Cross-Origin Resource Sharing)

**구현 위치**: `backend/app/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # 개발 환경
        "http://localhost:80",
        "http://frontend:3000",
        # 프로덕션 도메인 추가
        # "https://yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**프로덕션 설정**:
```python
# .env
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Input Validation (입력 검증)

**Pydantic 모델 사용**:
```python
from pydantic import BaseModel, validator, Field

class EvaluationCreate(BaseModel):
    company_id: str = Field(..., regex=r'^[a-f0-9-]{36}$')  # UUID 검증
    scores_data: Optional[Dict[str, float]] = None

    @validator('scores_data')
    def validate_scores(cls, v):
        if v:
            for score in v.values():
                if not (0 <= score <= 100):
                    raise ValueError('점수는 0-100 사이여야 합니다')
        return v
```

### SQL Injection 방지

✅ **SQLAlchemy ORM 사용** (Parameterized Queries)
- 모든 데이터베이스 쿼리는 ORM을 통해 실행
- Raw SQL 사용 금지

**안전한 쿼리**:
```python
# ✅ Good
user = db.query(User).filter(User.username == username).first()

# ❌ Bad (절대 사용 금지)
db.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

---

## 데이터 보호

### 부인 방지 (Non-repudiation)

평가 제출 시 4가지 증거 자동 기록:

**구현 위치**: `backend/app/api/v1/endpoints/evaluations.py`

```python
@router.post("/{evaluation_id}/submit")
async def submit_evaluation(
    evaluation_id: str,
    request: Request,
    data: EvaluationSubmit,
    ...
):
    # 1. Canvas 서명 이미지
    evaluation.signature_data = data.signature_data  # Base64 PNG

    # 2. 제출 시간
    evaluation.submitted_at = datetime.utcnow()  # ISO 8601

    # 3. IP 주소 (프록시 고려)
    client_ip = request.headers.get("X-Forwarded-For")
    if client_ip:
        client_ip = client_ip.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else None
    evaluation.submit_ip = client_ip

    # 4. User-Agent
    evaluation.submit_user_agent = request.headers.get("User-Agent")
```

**저장 데이터**:
- `signature_data`: Canvas 서명 Base64 이미지
- `submitted_at`: 제출 시간 (UTC)
- `submit_ip`: IPv4/IPv6 주소
- `submit_user_agent`: 브라우저/디바이스 정보

### 감사 추적 (Audit Trail)

**자동 로깅 대상**:
- ✅ 로그인/로그아웃
- ✅ 사용자 생성/수정/삭제
- ✅ 평가 점수 변경
- ✅ 템플릿 생성/수정
- ✅ 프로젝트 생성/수정

**점수 변경 이력**:
```python
# ScoreHistory 모델 자동 기록
history = ScoreHistory(
    evaluation_id=evaluation.id,
    evaluator_id=current_user.id,
    item_id=item_id,
    old_score=old_score,
    new_score=new_score,
    change_type="UPDATE",  # CREATE, UPDATE, DELETE
    ip_address=get_client_ip(request),
    created_at=datetime.utcnow()
)
```

**조회 API**: `GET /api/v1/evaluations/{id}/history` (관리자 전용)

### 파일 업로드 보안

**제한 사항**:
- ✅ **파일 유형**: PDF, DOCX, HWP만 허용
- ✅ **파일 크기**: 최대 50MB
- ✅ **파일명 검증**: UUID 기반 안전한 파일명 생성

**구현**:
```python
@router.post("/{company_id}/upload-document")
async def upload_company_document(
    company_id: str,
    file: UploadFile = File(...),
    ...
):
    # 파일 확장자 검증
    allowed_extensions = {'.pdf', '.docx', '.hwp'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(400, "허용되지 않는 파일 형식입니다")

    # 파일 크기 검증
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "파일 크기가 50MB를 초과합니다")

    # 안전한 파일명 생성
    safe_filename = f"{company_id}_{uuid.uuid4()}{file_ext}"
```

---

## 감사 및 로깅

### 감사 로그 시스템

**테이블**: `audit_logs`

**기록 항목**:
```python
class AuditLog(Base):
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    username = Column(String(100))
    action = Column(String(100), nullable=False)  # LOGIN, LOGOUT, CREATE, UPDATE, DELETE
    resource = Column(String(200))  # 대상 리소스
    resource_id = Column(String(100))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    details = Column(JSON)  # 추가 정보
    status = Column(String(50))  # SUCCESS, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)
```

**조회 API**: `GET /api/v1/admin/audit-logs` (관리자 전용)

### 애플리케이션 로깅

**권장 설정** (프로덕션):
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/sme_eval/app.log'),
        logging.StreamHandler()
    ]
)
```

**로깅 대상**:
- ✅ 인증 실패
- ✅ 권한 부족
- ✅ 예외 및 에러
- ✅ 중요 비즈니스 이벤트

---

## 배포 보안

### 환경 변수 관리

**절대 커밋 금지**:
- ❌ `.env` 파일
- ❌ `SECRET_KEY`
- ❌ 데이터베이스 비밀번호
- ❌ API 키

**프로덕션 설정**:
```bash
# .env.production (예시 - 절대 커밋 금지!)
SECRET_KEY=<openssl rand -hex 32로 생성>
DB_PASSWORD=<강력한 비밀번호>
DATABASE_URL=postgresql://sme_admin:${DB_PASSWORD}@db:5432/sme_evaluation

# CORS 설정
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# OCR API 키 (선택)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
MISTRAL_API_KEY=...
```

### HTTPS/TLS 설정

**Nginx 설정** (권장):
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Docker 보안

**권장사항**:
1. ✅ **Non-root 사용자 실행**
   ```dockerfile
   RUN useradd -m -u 1000 appuser
   USER appuser
   ```

2. ✅ **최소 권한 원칙**
   - 필요한 패키지만 설치
   - Multi-stage build로 빌드 도구 제외

3. ✅ **정기 이미지 업데이트**
   ```bash
   docker pull postgres:15-alpine
   docker pull python:3.11-slim
   ```

4. ✅ **시크릿 관리**
   ```bash
   # Docker Secrets 사용 (Swarm 모드)
   echo "secret_value" | docker secret create db_password -
   ```

---

## 보안 체크리스트

### 개발 환경

- [x] JWT SECRET_KEY 설정
- [x] 비밀번호 복잡도 검증
- [x] bcrypt 해싱 적용
- [x] Pydantic input validation
- [x] SQLAlchemy ORM 사용 (SQL Injection 방지)
- [x] CORS 설정 적용
- [x] Rate limiting 구현

### 프로덕션 배포 전

- [ ] 강력한 SECRET_KEY 생성 및 설정
- [ ] 데이터베이스 비밀번호 변경
- [ ] HTTPS/TLS 인증서 설정
- [ ] CORS allowed_origins에 프로덕션 도메인 추가
- [ ] 환경 변수 `.env` 파일 검증
- [ ] 파일 업로드 디렉토리 권한 설정 (755)
- [ ] 로그 디렉토리 생성 및 권한 설정
- [ ] PostgreSQL 외부 접근 제한 (방화벽)
- [ ] Docker 컨테이너 non-root 사용자 실행
- [ ] Nginx 보안 헤더 설정
- [ ] 정기 백업 스케줄 설정

### 운영 및 모니터링

- [ ] 감사 로그 정기 검토
- [ ] 비정상 로그인 시도 모니터링
- [ ] 파일 업로드 용량 모니터링
- [ ] Rate limit 임계값 조정
- [ ] 의존성 보안 업데이트 (npm audit, pip-audit)
- [ ] 침투 테스트 (Penetration Testing)
- [ ] 복구 계획 (Disaster Recovery Plan)

---

## 취약점 보고

보안 취약점을 발견하신 경우:

1. **즉시 보고**: security@yourdomain.com
2. **비공개 유지**: 공개 이슈로 등록하지 마세요
3. **상세 정보 제공**:
   - 취약점 설명
   - 재현 단계
   - 영향 범위
   - 제안 해결 방법

---

## 참고 자료

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [PostgreSQL Security Best Practices](https://www.postgresql.org/docs/current/security.html)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

**마지막 업데이트**: 2026-01-11
**버전**: 1.0.0
