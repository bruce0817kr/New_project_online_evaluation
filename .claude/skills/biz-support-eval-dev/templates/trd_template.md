# 기술 설계 문서 (Technical Requirements Document)

## 문서 정보

| 항목           | 내용                          |
|----------------|-------------------------------|
| 프로젝트명     | [프로젝트명을 입력하세요]     |
| 작성자         | [작성자명]                    |
| 작성일         | [YYYY-MM-DD]                  |
| 버전           | 1.0                           |
| 관련 문서      | PRD v1.0                      |

---

## 1. 시스템 아키텍처

### 1.1 전체 구성도

```mermaid
graph TB
    subgraph "Client Layer"
        A[Web Browser]
    end

    subgraph "Presentation Layer"
        B[Nginx Reverse Proxy]
        C[React Frontend]
    end

    subgraph "Application Layer"
        D[FastAPI Backend]
        E[OCR Service]
        F[Score Service]
    end

    subgraph "Data Layer"
        G[(PostgreSQL)]
        H[File Storage]
    end

    A --> B
    B --> C
    B --> D
    C --> D
    D --> E
    D --> F
    D --> G
    D --> H
```

### 1.2 기술 스택

#### Frontend
- **프레임워크**: React 18.x
- **상태 관리**: Zustand
- **스타일링**: TailwindCSS 3.x
- **PDF 뷰어**: react-pdf-viewer
- **HTTP 클라이언트**: Axios
- **폼 검증**: React Hook Form + Yup

#### Backend
- **프레임워크**: FastAPI 0.100+
- **ORM**: SQLAlchemy 2.0
- **인증**: JWT (python-jose)
- **파일 처리**: python-multipart
- **OCR**: Tesseract OCR (pytesseract)
- **PDF 생성**: ReportLab 또는 WeasyPrint

#### Database
- **DBMS**: PostgreSQL 14+
- **마이그레이션**: Alembic
- **연결 풀**: asyncpg

#### Infrastructure
- **컨테이너**: Docker, Docker Compose
- **웹 서버**: Nginx
- **프로세스 관리**: Uvicorn (ASGI)

---

## 2. 데이터베이스 설계

### 2.1 ERD (Entity Relationship Diagram)

```mermaid
erDiagram
    USERS ||--o{ EVALUATIONS : creates
    PROJECTS ||--o{ COMPANIES : contains
    COMPANIES ||--o{ EVALUATIONS : evaluated_by
    EVALUATIONS ||--o{ AUDIT_LOGS : generates

    USERS {
        int id PK
        string username UK
        string password_hash
        string email
        enum role
        timestamp created_at
    }

    PROJECTS {
        int id PK
        string name
        enum stage
        enum status
        jsonb evaluation_template
        timestamp created_at
    }

    COMPANIES {
        int id PK
        int project_id FK
        string name
        string business_number UK
        string documents_path
        jsonb ocr_data
        timestamp created_at
    }

    EVALUATIONS {
        int id PK
        int company_id FK
        int evaluator_id FK
        jsonb scores_data
        boolean is_submitted
        text signature_image
        timestamp created_at
        timestamp updated_at
    }

    AUDIT_LOGS {
        int id PK
        int user_id FK
        string action
        string resource
        jsonb details
        timestamp created_at
    }
```

### 2.2 테이블 상세 명세

#### users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'evaluator', 'viewer')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
```

#### projects
```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    stage VARCHAR(20) NOT NULL CHECK (stage IN ('document', 'presentation')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('planning', 'in_progress', 'completed')),
    evaluation_template JSONB NOT NULL DEFAULT '{}',
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 평가 템플릿 예시
-- {
--   "items": [
--     {"name": "기술성", "weight": 0.4, "max_score": 100},
--     {"name": "사업성", "weight": 0.3, "max_score": 100}
--   ]
-- }
```

#### companies
```sql
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    business_number VARCHAR(20) UNIQUE,
    ceo_name VARCHAR(50),
    address TEXT,
    documents_path TEXT,
    ocr_data JSONB DEFAULT '{}',
    ocr_confidence DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_companies_project ON companies(project_id);
CREATE INDEX idx_companies_business_number ON companies(business_number);
```

#### evaluations
```sql
CREATE TABLE evaluations (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    evaluator_id INTEGER NOT NULL REFERENCES users(id),
    scores_data JSONB NOT NULL DEFAULT '{}',
    comment TEXT,
    is_submitted BOOLEAN DEFAULT FALSE,
    signature_image TEXT,
    submitted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(company_id, evaluator_id)
);

-- scores_data 예시
-- {
--   "기술성": 85,
--   "사업성": 90,
--   "시장성": 88,
--   "total_score": 87.4
-- }

CREATE INDEX idx_evaluations_company ON evaluations(company_id);
CREATE INDEX idx_evaluations_evaluator ON evaluations(evaluator_id);
CREATE INDEX idx_evaluations_submitted ON evaluations(is_submitted);
```

#### audit_logs
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    username VARCHAR(50),
    ip_address VARCHAR(45),
    action VARCHAR(50) NOT NULL,
    resource VARCHAR(100),
    details JSONB,
    status VARCHAR(20) DEFAULT 'SUCCESS',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);
```

---

## 3. API 명세

### 3.1 인증 (Authentication)

#### POST /api/v1/auth/login
로그인

**Request**:
```json
{
  "username": "evaluator1",
  "password": "password123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "evaluator1",
    "role": "evaluator"
  }
}
```

**Error** (401 Unauthorized):
```json
{
  "detail": "잘못된 사용자명 또는 비밀번호"
}
```

---

### 3.2 OCR 처리

#### POST /api/v1/ocr/analyze
사업자등록증 OCR 분석

**Request**:
- Content-Type: `multipart/form-data`
- Body: `file` (PDF/JPG/PNG, max 10MB)

**Response** (200 OK):
```json
{
  "document_type": "사업자등록증",
  "extracted_data": {
    "사업자등록번호": "123-45-67890",
    "상호": "(주)테크이노베이션",
    "대표자": "홍길동",
    "사업장주소": "서울특별시 강남구 테헤란로 123"
  },
  "confidence_score": 0.92,
  "needs_manual_verification": false
}
```

**구현 파일**: `backend/app/services/ocr_service.py`

---

### 3.3 평가 관리

#### GET /api/v1/evaluations/{company_id}
평가 데이터 조회

**Response** (200 OK):
```json
{
  "id": 1,
  "company_id": 5,
  "evaluator_id": 2,
  "scores_data": {
    "기술성": 85,
    "사업성": 90,
    "시장성": 88
  },
  "comment": "우수한 기술력을 보유하고 있음",
  "is_submitted": false,
  "created_at": "2026-01-09T10:00:00Z",
  "updated_at": "2026-01-09T10:30:00Z"
}
```

#### PATCH /api/v1/evaluations/{evaluation_id}/save
임시 저장 (Auto-save)

**Request**:
```json
{
  "scores_data": {
    "기술성": 85,
    "사업성": 90
  },
  "comment": "평가 진행 중..."
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "저장되었습니다",
  "updated_at": "2026-01-09T10:31:00Z"
}
```

#### POST /api/v1/evaluations/{evaluation_id}/submit
최종 제출

**Request**:
```json
{
  "scores_data": {
    "기술성": 85,
    "사업성": 90,
    "시장성": 88,
    "total_score": 87.4
  },
  "comment": "최종 의견",
  "signature_image": "data:image/png;base64,iVBORw0KGgoAAAANS..."
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "제출이 완료되었습니다",
  "is_submitted": true,
  "submitted_at": "2026-01-09T10:35:00Z"
}
```

**Error** (400 Bad Request):
```json
{
  "detail": "이미 제출된 평가입니다"
}
```

---

### 3.4 점수 집계

#### GET /api/v1/companies/{company_id}/aggregate
기업별 점수 집계

**Response** (200 OK):
```json
{
  "company_id": 5,
  "company_name": "(주)테크이노베이션",
  "evaluations_count": 5,
  "scores": {
    "average": 87.6,
    "trimmed_average": 88.0,
    "min": 82.0,
    "max": 95.0,
    "std_dev": 4.2
  },
  "evaluators": [
    {
      "name": "홍길동",
      "total_score": 87.4,
      "submitted_at": "2026-01-09T10:35:00Z"
    },
    {
      "name": "김철수",
      "total_score": 89.6,
      "submitted_at": "2026-01-09T11:20:00Z"
    }
  ]
}
```

**구현 파일**: `backend/app/services/score_service.py`

---

### 3.5 리포트 생성

#### GET /api/v1/reports/{company_id}/pdf
평가 리포트 PDF 다운로드

**Response**:
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="evaluation_report_123.pdf"`

**구현 기술**:
- WeasyPrint (HTML → PDF)
- 템플릿: Jinja2

---

## 4. 프론트엔드 구조

### 4.1 폴더 구조
```
frontend/
├── src/
│   ├── components/
│   │   ├── admin/
│   │   │   ├── ProjectManager.js
│   │   │   └── UserManager.js
│   │   ├── evaluator/
│   │   │   ├── PDFViewer.js
│   │   │   ├── ScoreInput.js
│   │   │   └── SplitViewEvaluator.js
│   │   └── common/
│   │       ├── Header.js
│   │       └── Footer.js
│   ├── pages/
│   │   ├── LoginPage.js
│   │   ├── AdminDashboard.js
│   │   └── EvaluatorPage.js
│   ├── services/
│   │   ├── api.js
│   │   └── auth.js
│   ├── stores/
│   │   └── useAuthStore.js
│   ├── hooks/
│   │   └── useAutoSave.js
│   └── utils/
│       └── validators.js
```

### 4.2 상태 관리 (Zustand)

```javascript
// stores/useAuthStore.js
import create from 'zustand';

const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem('token'),

  login: (user, token) => {
    localStorage.setItem('token', token);
    set({ user, token });
  },

  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null });
  },
}));

export default useAuthStore;
```

### 4.3 Auto-Save Hook

```javascript
// hooks/useAutoSave.js
import { useEffect, useRef } from 'react';

export const useAutoSave = (data, saveFunction, delay = 3000) => {
  const timerRef = useRef(null);

  useEffect(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    timerRef.current = setTimeout(() => {
      saveFunction(data);
    }, delay);

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [data, saveFunction, delay]);
};
```

**사용 예시**:
```javascript
const [scores, setScores] = useState({});

useAutoSave(scores, async (data) => {
  await api.patch(`/evaluations/${evaluationId}/save`, { scores_data: data });
}, 3000);
```

---

## 5. 보안 구현

### 5.1 JWT 인증

```python
# backend/app/core/security.py
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key"  # 환경 변수로 관리
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)
```

### 5.2 권한 검증

```python
# backend/app/api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt, JWTError

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = await get_user_by_id(user_id)
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")
    return current_user
```

---

## 6. 배포 구성

### 6.1 Docker Compose

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
    depends_on:
      - frontend
      - backend

  frontend:
    build: ./frontend
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    volumes:
      - ./frontend/src:/app/src

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/evaluation_db
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db

  db:
    image: postgres:14-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=evaluation_db
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 6.2 환경 변수

```bash
# .env.example
DATABASE_URL=postgresql://user:password@localhost:5432/evaluation_db
SECRET_KEY=your-secret-key-change-this
ENCRYPTION_KEY=your-encryption-key-change-this
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:80
MAX_UPLOAD_SIZE=10485760  # 10MB
OCR_LANGUAGE=kor+eng
```

---

## 7. 성능 최적화

### 7.1 데이터베이스
- [ ] 인덱스 적용 (외래 키, 검색 필드)
- [ ] 연결 풀 설정 (최소 5, 최대 20)
- [ ] 쿼리 최적화 (N+1 문제 해결)

### 7.2 백엔드
- [ ] 비동기 처리 (async/await)
- [ ] 캐싱 (Redis, 선택 사항)
- [ ] 파일 스트리밍 (대용량 PDF)

### 7.3 프론트엔드
- [ ] 코드 스플리팅 (React.lazy)
- [ ] 이미지 최적화 (WebP 변환)
- [ ] 번들 크기 최소화 (Tree Shaking)

---

## 8. 테스트 전략

### 8.1 단위 테스트 (Backend)
```python
# backend/tests/test_score_service.py
import pytest
from app.services.score_service import ScoreService

def test_calculate_average():
    scores = [85, 90, 88]
    result = ScoreService.calculate_average(scores)
    assert result == 87.67

def test_trimmed_mean_with_5_scores():
    scores = [60, 85, 90, 92, 95]
    result = ScoreService.calculate_trimmed_mean(scores)
    assert result == 89.0  # 60과 95 제외
```

### 8.2 통합 테스트 (Frontend)
```javascript
// frontend/src/__tests__/EvaluatorPage.test.js
import { render, screen } from '@testing-library/react';
import EvaluatorPage from '../pages/EvaluatorPage';

test('renders evaluation form', () => {
  render(<EvaluatorPage />);
  expect(screen.getByText('평가 항목')).toBeInTheDocument();
});
```

### 8.3 E2E 테스트
- 도구: Playwright 또는 Cypress
- 시나리오:
  1. 로그인
  2. 평가 대상 선택
  3. 점수 입력 및 Auto-save 확인
  4. 최종 제출

---

## 9. 모니터링 및 로깅

### 9.1 애플리케이션 로그
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/app/backend.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### 9.2 모니터링 지표
- [ ] 응답 시간 (P95, P99)
- [ ] 에러율 (4xx, 5xx)
- [ ] 동시 접속자 수
- [ ] DB 연결 풀 사용률

---

## 10. 개발 일정 (예시)

| 단계           | 기간       | 담당자   | 산출물                     |
|----------------|------------|----------|----------------------------|
| 요구사항 분석  | 1주        | PM       | PRD                        |
| 기술 설계      | 1주        | Architect| TRD, ERD                   |
| DB 스키마 구축 | 3일        | Backend  | 마이그레이션 스크립트      |
| API 개발       | 2주        | Backend  | API 엔드포인트, 테스트     |
| UI 개발        | 2주        | Frontend | React 컴포넌트             |
| 통합 및 테스트 | 1주        | Full Team| E2E 테스트, 버그 수정      |
| 배포 준비      | 3일        | DevOps   | Docker, 환경 설정          |
| UAT            | 1주        | QA       | 사용자 승인 테스트         |

**총 개발 기간**: 약 8주

---

## 11. 참고 자료

- `backend/app/services/score_service.py` - 점수 계산 구현
- `backend/app/services/ocr_service.py` - OCR 파싱 구현
- `frontend/src/hooks/useAutoSave.js` - Auto-save Hook
- `references/security_standard.md` - 보안 표준
- `references/eval_guidelines.md` - 평가 가이드라인

---

**문서 검토**

| 역할       | 이름 | 승인 | 날짜 |
|------------|------|------|------|
| 기술 책임자|      |      |      |
| 백엔드 개발자|    |      |      |
| 프론트엔드 개발자||    |      |
