# 중소기업 선정평가 관리 시스템 (MVP)

> 중소기업 지원사업의 서류 및 발표 평가를 디지털화하여 행정 소모를 줄이고 공정성을 확보하는 온프레미스 평가 시스템

## 📋 프로젝트 개요

### 목적
- 중소기업 지원사업의 평가 프로세스 디지털화
- 심사위원의 평가 효율성 향상
- 공정하고 투명한 평가 절차 구축

### 주요 사용자
- **관리자(사무국)**: 사업 관리, 기업 서류 업로드, 심사위원 배정, 결과 집계
- **심사위원**: 배정된 기업 서류 열람, 평가 항목별 점수 입력, 종합 의견 작성

## 🎯 핵심 기능 (MVP Scope)

### 1. OCR 서류 검증
- 업로드된 사업자등록증에서 핵심 데이터 자동 추출
- 사업자번호, 기업명, 대표자명 자동 인식
- 수동 수정 가능한 UI 제공

### 2. 2분할 평가 UI
- 좌측: PDF 뷰어 (서류 열람)
- 우측: 점수 입력창
- 독립적인 스크롤 영역

### 3. 자동 점수 산출
- 가중치 적용 점수 계산
- 5인 이상 시 최고/최저점 제외 평균
- 실시간 자동 저장 (Debounce 3초)

### 4. 평가 리포트
- 심사위원 서명 포함 PDF 결과물 생성
- 평가 이력 추적 및 감사 로그

## 🛠 Tech Stack

### Backend
- **Framework**: Python 3.11, FastAPI
- **Database**: PostgreSQL 15 (JSONB 활용)
- **ORM**: SQLAlchemy
- **OCR Engine**: Tesseract OCR

### Frontend
- **Framework**: React 18
- **Styling**: TailwindCSS
- **State Management**: Zustand
- **PDF Viewer**: react-pdf

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Reverse Proxy**: Nginx
- **Deployment**: On-premise

## 🚀 Quick Start

### 사전 요구사항
- Docker & Docker Compose
- Git

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd New_project_online_evaluation
```

### 2. 환경 변수 설정
```bash
# 루트 디렉토리
cp .env.example .env

# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

**중요**: `.env` 파일의 `SECRET_KEY`를 반드시 변경하세요!

### 3. Docker로 실행
```bash
# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 4. 접속
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API 문서**: http://localhost:8000/api/docs

### 5. 기본 계정
- **관리자**: `admin` / `admin123`
- **심사위원**: `evaluator1` / `evaluator123`

## 📂 프로젝트 구조

```
New_project_online_evaluation/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/            # API 엔드포인트
│   │   ├── core/              # 설정, DB 연결
│   │   ├── models/            # SQLAlchemy 모델
│   │   ├── schemas/           # Pydantic 스키마
│   │   ├── services/          # 비즈니스 로직
│   │   └── main.py            # 앱 엔트리포인트
│   ├── migrations/            # DB 마이그레이션
│   ├── tests/                 # 테스트 코드
│   ├── requirements.txt       # Python 의존성
│   └── Dockerfile
│
├── frontend/                  # React Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/       # 재사용 컴포넌트
│   │   ├── pages/            # 페이지 컴포넌트
│   │   ├── hooks/            # Custom Hooks
│   │   ├── services/         # API 호출
│   │   └── stores/           # Zustand 스토어
│   ├── package.json
│   └── Dockerfile
│
├── nginx/                     # Nginx 설정
│   ├── nginx.conf
│   └── conf.d/
│
├── docs/                      # 프로젝트 문서
│   ├── Claude.md             # 개발 규칙
│   └── Skills.md             # 기술 가이드
│
├── docker-compose.yml        # Docker Compose 설정
├── .env.example              # 환경 변수 템플릿
├── .gitignore
└── README.md
```

## 🧪 테스트

### Backend 테스트
```bash
# Docker 컨테이너 내에서 실행
docker-compose exec backend pytest

# 커버리지 포함
docker-compose exec backend pytest --cov=app --cov-report=html
```

### Frontend 테스트
```bash
# Docker 컨테이너 내에서 실행
docker-compose exec frontend npm test
```

## 📚 API 문서

### 주요 엔드포인트

#### 인증
- `POST /api/v1/auth/login` - 로그인
- `GET /api/v1/auth/me` - 현재 사용자 정보

#### 사업 관리
- `GET /api/v1/projects` - 사업 목록
- `POST /api/v1/projects` - 사업 생성
- `GET /api/v1/projects/{id}` - 사업 상세
- `PATCH /api/v1/projects/{id}` - 사업 수정

#### 기업 관리
- `GET /api/v1/companies` - 기업 목록
- `POST /api/v1/companies` - 기업 등록
- `POST /api/v1/companies/{id}/upload` - 서류 업로드

#### 평가
- `GET /api/v1/evaluations/{company_id}` - 평가 데이터 조회
- `PATCH /api/v1/evaluations/save` - 임시 저장
- `POST /api/v1/evaluations/submit` - 최종 제출
- `GET /api/v1/evaluations/company/{company_id}/aggregate` - 점수 집계

#### OCR
- `POST /api/v1/ocr/analyze` - 서류 분석
- `POST /api/v1/ocr/verify` - 데이터 검증

자세한 API 문서는 http://localhost:8000/api/docs 에서 확인할 수 있습니다.

## 🔧 개발 가이드

### 개발 환경 설정
```bash
# Backend 개발 환경
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend 개발 환경
cd frontend
npm install
npm start
```

### 코드 스타일
- **Backend**: PEP 8 준수, Black 포맷터 사용
- **Frontend**: ESLint + Prettier

### 개발 규칙
프로젝트 개발 시 반드시 [docs/Claude.md](docs/Claude.md)의 규칙을 준수하세요.

### 핵심 기술
구현에 필요한 핵심 로직은 [docs/Skills.md](docs/Skills.md)를 참고하세요.

## 🔒 보안 고려사항

### 데이터 보호
- 제출된 평가 데이터는 관리자 권한 없이 수정 불가
- PDF 파일 스트리밍 방식으로 보안 강화
- 개인정보 및 기업 데이터 암호화

### 감사 추적
- 모든 평가 수정 이력 audit_logs 테이블 기록
- IP 주소, User Agent 포함 상세 로그

## 📊 데이터베이스 스키마

### 주요 테이블
- **users**: 사용자 (관리자, 심사위원)
- **projects**: 사업 프로젝트
- **companies**: 평가 대상 기업
- **evaluations**: 평가 데이터 (JSONB 활용)
- **audit_logs**: 수정 이력 추적

자세한 스키마는 [backend/migrations/init.sql](backend/migrations/init.sql)을 참고하세요.

## 🤝 기여 가이드

### 브랜치 전략
- `main`: 프로덕션 배포 브랜치
- `develop`: 개발 통합 브랜치
- `feature/*`: 기능 개발 브랜치
- `bugfix/*`: 버그 수정 브랜치

### 커밋 메시지 형식
```
[타입] 간단한 설명

상세 설명 (선택사항)

예:
[feat] 평가 점수 자동 계산 기능 추가
[fix] PDF 뷰어 스크롤 오류 수정
[docs] README 업데이트
[test] 점수 계산 로직 테스트 추가
```

## 📝 라이선스

이 프로젝트는 내부 사용을 위한 프로젝트입니다.

## 👥 팀

- **개발자**: [Your Name]
- **문의**: [Contact Information]

## 📖 추가 문서

- [개발 규칙 (Claude.md)](docs/Claude.md)
- [기술 가이드 (Skills.md)](docs/Skills.md)
- [API 문서](http://localhost:8000/api/docs)

---

**Version**: 1.0.0-MVP
**Last Updated**: 2024-01-09
