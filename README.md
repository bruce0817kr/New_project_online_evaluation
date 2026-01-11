# 중소기업 평가관리 시스템 (SME Evaluation System)

기업 선정평가를 위한 종합 관리 시스템 - MVP 버전

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-18.2-blue.svg)](https://reactjs.org/)

## 📋 목차

- [개요](#개요)
- [주요 기능](#주요-기능)
- [기술 스택](#기술-스택)
- [시스템 아키텍처](#시스템-아키텍처)
- [설치 및 실행](#설치-및-실행)
- [데이터베이스 마이그레이션](#데이터베이스-마이그레이션)
- [API 문서](#api-문서)
- [사용자 가이드](#사용자-가이드)
- [보안 기능](#보안-기능)

---

## 🎯 개요

중소기업 R&D 과제 선정을 위한 평가 관리 시스템입니다. 평가위원이 기업의 사업계획서를 검토하고 점수를 부여하며, 관리자가 결과를 집계하고 분석할 수 있습니다.

### 핵심 가치
- ✅ **효율적인 평가 프로세스**: Split View UI로 서류와 평가표를 동시에 확인
- ✅ **투명한 감사 추적**: 모든 점수 변경 이력을 자동 기록
- ✅ **법적 효력 있는 서명**: Canvas 기반 전자 서명 + IP/User-Agent 기록
- ✅ **유연한 평가 기준**: 사업별 맞춤형 배점표 템플릿

---

## 🚀 주요 기능

### 관리자 (Admin)
- 📁 **사업 관리**: 평가 행사 생성 및 관리
- 🏢 **기업 관리**: 참여 기업 등록 및 서류 업로드
- 📋 **템플릿 관리** ⭐ NEW: 동적 평가 배점표 생성/수정
- 🔗 **평가 배정**: 평가위원에게 기업 할당 (순서 지정)
- 📊 **평가 현황**: 실시간 평가 진행 상황 모니터링
- 📈 **랭킹 및 집계** ⭐ NEW: 최고/최저점 제외 평균, 보너스 점수 적용
- 📄 **리포트 생성** ⭐ NEW: CSV/Excel 내보내기
- 🔍 **감사 로그** ⭐ NEW: 점수 변경 이력 조회
- 👥 **사용자 관리**: 평가위원 계정 관리

### 평가위원 (Evaluator)
- 📝 **평가 수행**: Split View로 PDF 서류 + 평가표 동시 보기
- 💾 **자동 저장**: 3초 디바운스로 작업 내용 자동 저장
- ✍️ **전자 서명** ⭐ NEW: Canvas 드로잉 기반 직필 서명
- 📊 **실시간 점수 계산**: Sticky Footer로 총점 실시간 표시
- 🔒 **제출 완료**: 서명 후 제출 시 수정 불가

---

## 🛠 기술 스택

### Backend
- **Framework**: FastAPI 0.109+
- **ORM**: SQLAlchemy 2.0+
- **Database**: PostgreSQL 14+
- **Authentication**: JWT (HS256)
- **Validation**: Pydantic 2.0+
- **File Processing**: python-multipart, openpyxl
- **Signature**: Base64 이미지 저장

### Frontend
- **Framework**: React 18.2
- **Router**: React Router DOM 6.21
- **State Management**: Zustand 4.4
- **HTTP Client**: Axios 1.6
- **UI Framework**: Tailwind CSS 3.4
- **Signature** ⭐: react-signature-canvas 1.0.6
- **PDF Viewer**: react-pdf 7.6

### DevOps
- **Database Migration**: Custom Python scripts + SQL
- **Environment**: python-dotenv
- **Version Control**: Git

---

## 🏗 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │  Admin   │  │Evaluator │  │  Signature Canvas    │  │
│  │Dashboard │  │   Page   │  │  (react-signature)   │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │ Axios (JWT)
┌────────────────────▼────────────────────────────────────┐
│                 Backend (FastAPI)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │   Auth   │  │Templates │  │Rankings  │             │
│  │   API    │  │   API    │  │   API    │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│  ┌──────────────────────────────────────────┐          │
│  │        Evaluations API                   │          │
│  │  - Score History (Audit Log)             │          │
│  │  - Non-repudiation (IP + User-Agent)     │          │
│  └──────────────────────────────────────────┘          │
└────────────────────┬────────────────────────────────────┘
                     │ SQLAlchemy ORM
┌────────────────────▼────────────────────────────────────┐
│              PostgreSQL Database                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │  users   │  │ projects │  │ scoring_templates    │  │
│  ├──────────┤  ├──────────┤  ├──────────────────────┤  │
│  │companies │  │evaluations│ │  score_history       │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 설치 및 실행

### 사전 요구사항
- Python 3.9 이상
- Node.js 16 이상
- PostgreSQL 14 이상

### 1. 저장소 클론
```bash
git clone https://github.com/bruce0817kr/New_project_online_evaluation.git
cd New_project_online_evaluation
```

### 2. 백엔드 설정
```bash
cd backend

# Python 가상환경 생성 (선택)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 DATABASE_URL 및 SECRET_KEY 수정

# 데이터베이스 마이그레이션
python3 create_tables.py

# 초기 데이터 생성 (선택)
python3 migrations/seed_data.py

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 프론트엔드 설정
```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm start
```

### 4. 접속
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 기본 계정
```
관리자:
- ID: admin
- PW: admin123

평가위원:
- ID: evaluator1
- PW: eval123
```

---

## 🗄 데이터베이스 마이그레이션

자세한 내용은 [`backend/README_MIGRATION.md`](backend/README_MIGRATION.md) 참고

### 빠른 시작
```bash
cd backend

# 방법 1: SQLAlchemy 자동 생성 (권장)
python3 create_tables.py

# 방법 2: SQL 직접 실행
psql -U sme_admin -d sme_evaluation -f migrations/001_add_scoring_templates_and_metadata.sql
```

### 주요 테이블
- **users**: 사용자 (관리자, 평가위원)
- **projects**: 평가 사업
- **companies**: 참여 기업
- **evaluations**: 평가 결과
- **scoring_templates** ⭐ NEW: 평가 배점표 템플릿
- **score_history** ⭐ NEW: 점수 변경 감사 로그

---

## 📚 API 문서

### 인증 (Authentication)
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/auth/login` | 로그인 (JWT 토큰 발급) |
| GET | `/api/v1/auth/me` | 현재 사용자 정보 조회 |

### 사업 관리 (Projects)
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| GET | `/api/v1/projects` | 사업 목록 조회 | All |
| POST | `/api/v1/projects` | 사업 생성 | Admin |
| PUT | `/api/v1/projects/{id}` | 사업 수정 | Admin |
| DELETE | `/api/v1/projects/{id}` | 사업 삭제 | Admin |

### 템플릿 관리 (Templates) ⭐ NEW
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| GET | `/api/v1/templates` | 템플릿 목록 조회 | All |
| POST | `/api/v1/templates` | 템플릿 생성 | Admin |
| PUT | `/api/v1/templates/{id}` | 템플릿 수정 | Admin |
| PATCH | `/api/v1/templates/{id}/toggle-active` | 활성화/비활성화 | Admin |
| POST | `/api/v1/templates/{id}/set-default` | 기본 템플릿 설정 | Admin |
| POST | `/api/v1/templates/create-default` | R&D 표준 템플릿 생성 | Admin |

### 평가 관리 (Evaluations)
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| GET | `/api/v1/evaluations/my` | 내 평가 목록 조회 | Evaluator |
| GET | `/api/v1/evaluations/{id}` | 평가 상세 조회 | Evaluator |
| PUT | `/api/v1/evaluations/{id}` | 평가 임시 저장 | Evaluator |
| POST | `/api/v1/evaluations/{id}/submit` | 평가 제출 (서명 포함) | Evaluator |
| GET | `/api/v1/evaluations/{id}/history` ⭐ | 점수 변경 이력 조회 | Admin |

### 랭킹 및 집계 ⭐ NEW
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| GET | `/api/v1/evaluations/project/{id}/rankings` | 프로젝트별 랭킹 조회 | Admin |
| PATCH | `/api/v1/evaluations/company/{id}/bonus` | 보너스 점수 설정 | Admin |
| GET | `/api/v1/evaluations/project/{id}/export-csv` | CSV 내보내기 | Admin |
| GET | `/api/v1/evaluations/project/{id}/export-excel` | Excel 내보내기 | Admin |

전체 API 문서: http://localhost:8000/docs (Swagger UI)

---

## 📖 사용자 가이드

### 관리자 워크플로우

#### 1. 사업 생성
```
관리자 대시보드 → 사업 관리 → 사업 추가
- 사업명, 연도, 마감일 입력
- 평가 템플릿 선택 (또는 새로 생성)
```

#### 2. 템플릿 생성 ⭐ NEW
```
템플릿 관리 → 템플릿 추가
- 템플릿 이름, 총점 설정
- 섹션 추가 (예: 기술성, 사업성, 경제성)
- 평가 항목 추가 및 배점 설정
- 점수 합계 검증 (자동)
```

#### 3. 기업 등록
```
기업 관리 → 기업 추가
- 기업 정보 입력
- 사업계획서 PDF 업로드
```

#### 4. 평가위원 배정
```
평가 배정 → 배정 생성
- 평가위원 선택
- 기업 선택
- 평가 순서 지정
```

#### 5. 결과 확인
```
평가 현황 → 프로젝트 선택
- 실시간 제출 현황 확인
- 랭킹 조회
- CSV/Excel 다운로드
```

### 평가위원 워크플로우

#### 1. 평가 시작
```
평가위원 페이지 → 평가 시작 버튼
- Split View 화면 진입
- 좌측: PDF 서류 (60%), 우측: 평가표 (40%)
```

#### 2. 점수 입력
```
평가 항목별 점수 입력
- 동적 템플릿에 따른 평가 항목
- 자동 저장 (3초 디바운스)
- Sticky Footer로 총점 실시간 확인
```

#### 3. 평가 제출 ⭐ NEW
```
평가 제출 버튼 → Canvas 전자 서명 모달
- 마우스/터치로 직접 서명 작성
- 지우기 버튼으로 재작성 가능
- 서명하고 제출 버튼 클릭
- IP, User-Agent 자동 기록 (부인 방지)
```

---

## 🎨 주요 UI 스크린샷

### Split View 평가 화면
```
┌────────────────────────────────────────────────────────┐
│  [← 뒤로]  기업명 평가                    [임시저장]   │
├──────────────────────┬─────────────────────────────────┤
│                      │  평가 항목                      │
│   PDF 서류 보기      │  ┌─────────────────────────┐  │
│   (60%)              │  │ 기술성 (40점)           │  │
│                      │  │  • 독창성: [__] /20     │  │
│   [Scroll]           │  │  • 구체성: [__] /20     │  │
│                      │  └─────────────────────────┘  │
│                      │  ┌─────────────────────────┐  │
│                      │  │ 사업성 (40점)           │  │
│                      │  └─────────────────────────┘  │
│                      │  [Scroll]                     │
├──────────────────────┴─────────────────────────────────┤
│  총점: 85.0 / 100점               [평가 제출 ✓]      │
└────────────────────────────────────────────────────────┘
```

### Canvas 전자 서명 모달 ⭐ NEW
```
┌──────────────────────────────────────────┐
│  전자 서명                               │
│  아래 서명란에 마우스나 터치로 서명해주세요│
├──────────────────────────────────────────┤
│  서명란                                  │
│  ┌────────────────────────────────────┐ │
│  │                                    │ │
│  │    ~~~홍길동~~~                   │ │
│  │                                    │ │
│  └────────────────────────────────────┘ │
│  [🗑️ 지우기]  * 제출 후 수정 불가      │
├──────────────────────────────────────────┤
│           [취소]  [✅ 서명하고 제출]      │
└──────────────────────────────────────────┘
```

---

## 🔐 보안 기능

### 인증 및 권한
- JWT 토큰 기반 인증 (HS256)
- 역할 기반 접근 제어 (RBAC)
- 토큰 만료 시간: 8시간

### 부인 방지 (Non-repudiation) ⭐ NEW
평가 제출 시 다음 정보 자동 기록:
- ✅ Canvas 서명 이미지 (Base64 PNG)
- ✅ 제출 시간 (ISO 8601)
- ✅ IP 주소 (IPv4/IPv6)
- ✅ User-Agent (브라우저/디바이스 정보)

### 감사 로그 ⭐ NEW
- 모든 점수 변경 이력 자동 기록 (`score_history` 테이블)
- 이전 점수 → 새 점수 추적
- 변경 시간 및 평가자 ID 저장
- 관리자 전용 이력 조회 API

---

## 📂 프로젝트 구조

```
New_project_online_evaluation/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/            # API 엔드포인트
│   │   │   └── endpoints/
│   │   │       ├── auth.py
│   │   │       ├── projects.py
│   │   │       ├── companies.py
│   │   │       ├── evaluations.py
│   │   │       ├── templates.py      ⭐ NEW
│   │   │       └── admin.py
│   │   ├── core/              # 설정, DB 연결
│   │   ├── models/            # SQLAlchemy 모델
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── company.py
│   │   │   ├── evaluation.py
│   │   │   ├── scoring_template.py   ⭐ NEW
│   │   │   └── score_history.py      ⭐ NEW
│   │   └── main.py            # 앱 엔트리포인트
│   ├── migrations/            # DB 마이그레이션
│   │   ├── init.sql
│   │   ├── 001_add_scoring_templates_and_metadata.sql  ⭐ NEW
│   │   └── seed_data.py
│   ├── create_tables.py       ⭐ NEW
│   ├── run_migration.py       ⭐ NEW
│   ├── README_MIGRATION.md    ⭐ NEW
│   └── requirements.txt
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── components/       # 재사용 컴포넌트
│   │   ├── pages/            # 페이지 컴포넌트
│   │   │   ├── AdminDashboard.js
│   │   │   ├── EvaluatorPage.js
│   │   │   ├── EvaluationDetailPage.jsx  (Canvas 서명) ⭐
│   │   │   └── admin/
│   │   │       ├── ProjectsPage.jsx
│   │   │       ├── CompaniesPage.jsx
│   │   │       ├── TemplatesPage.jsx     ⭐ NEW
│   │   │       └── EvaluationsPage.jsx
│   │   ├── services/         # API 호출
│   │   │   ├── api.js
│   │   │   ├── authService.js
│   │   │   ├── projectService.js
│   │   │   ├── evaluationService.js
│   │   │   ├── templateService.js        ⭐ NEW
│   │   │   └── companyService.js
│   │   └── stores/           # Zustand 스토어
│   └── package.json
│
└── README.md                  ⭐ (This file - Updated)
```

---

## 📊 구현 현황

### ✅ Phase 0 (완료)
- [x] 동적 배점표 (Scoring Templates)
- [x] Split View UI (60% PDF / 40% Form)
- [x] 전자 서명 (텍스트 → Canvas 업그레이드)
- [x] 부인 방지 메타데이터 (IP, User-Agent)

### ✅ Phase 1 (완료)
- [x] 템플릿 관리 UI
- [x] 랭킹 및 보너스 계산
- [x] CSV/Excel 리포트 생성
- [x] 감사 로그 (Score History)

### 🔄 Phase 2 (계획)
- [ ] PDF 결과보고서 생성 (서명 이미지 포함)
- [ ] 이메일 알림 (평가 배정, 마감 임박)
- [ ] 대시보드 통계 차트
- [ ] 모바일 반응형 UI 개선

### 🔮 Phase 3 (향후)
- [ ] SSO 연동 (카카오, PASS)
- [ ] OCR 기반 자동 점수 추출
- [ ] AI 기반 서류 분석 보조
- [ ] 다국어 지원 (i18n)

---

## 🤝 기여하기

이 프로젝트는 오픈소스 기여를 환영합니다.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 커밋 메시지 형식
```
[타입] 간단한 설명

예:
[feat] 평가 템플릿 관리 UI 추가
[fix] PDF 뷰어 스크롤 오류 수정
[chore] 데이터베이스 마이그레이션 스크립트 추가
[docs] README 업데이트
```

---

## 📝 라이선스

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 개발 정보

- **Backend**: FastAPI + PostgreSQL + SQLAlchemy
- **Frontend**: React + Tailwind CSS + Zustand
- **Signature**: Canvas API + react-signature-canvas
- **Version**: 1.0.0-MVP
- **Last Updated**: 2026-01-11

---

## 📞 문의

- GitHub Issues: [New Issue](https://github.com/bruce0817kr/New_project_online_evaluation/issues)
- Email: support@example.com

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - JavaScript library for building user interfaces
- [react-signature-canvas](https://github.com/agilgur5/react-signature-canvas) - Signature canvas library
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel file generation
