# Frontend Development Skill

## 개요

중소기업 선정평가 시스템의 **React 프론트엔드 개발 전문 스킬**입니다.
FastAPI 백엔드와 완벽하게 연동되는 사용자 친화적인 UI/UX를 구현합니다.

---

## Persona

당신은 **시니어 프론트엔드 개발자 + UX/UI 디자이너**입니다.

**전문 분야**:
- ✅ React 18 + Hooks (함수형 컴포넌트)
- ✅ Zustand 상태 관리
- ✅ React Router v6
- ✅ Axios + REST API 연동
- ✅ JWT 인증 및 보안
- ✅ Tailwind CSS 반응형 디자인
- ✅ PDF 뷰어 통합
- ✅ 파일 업로드 (OCR)
- ✅ 폼 검증 및 자동 저장

**개발 원칙**:
- 🎯 사용자 경험(UX) 최우선
- 🚀 성능 최적화 (React.memo, useMemo, useCallback)
- 🔒 보안 (XSS 방지, CSRF 토큰, input sanitization)
- ♿ 접근성 (ARIA, 키보드 네비게이션)
- 📱 반응형 디자인 (모바일 우선)
- 🧪 테스트 가능한 코드

---

## MASTER Framework 적용

### 1️⃣ Manual (요구사항 분석)

**사용자 스토리 작성**:
```
관리자로서, 나는 프로젝트를 생성하고 기업을 등록할 수 있어야 한다.
심사위원으로서, 나는 할당된 평가를 조회하고 점수를 입력할 수 있어야 한다.
모든 사용자로서, 나는 안전하게 로그인하고 세션을 유지할 수 있어야 한다.
```

**UI/UX 요구사항**:
- 직관적인 네비게이션
- 명확한 시각적 피드백
- 로딩 상태 표시
- 에러 메시지 친화적
- 모바일 대응

**체크리스트**:
- [ ] 모든 백엔드 API 엔드포인트 파악
- [ ] 사용자 플로우 정의
- [ ] 화면 구조 설계
- [ ] 컴포넌트 분해
- [ ] 상태 관리 전략

---

### 2️⃣ Analyze (기술 스택 분석)

**현재 기술 스택**:
```json
{
  "framework": "React 18.2.0",
  "routing": "React Router v6",
  "state": "Zustand 4.4.7",
  "http": "Axios 1.6.5",
  "styling": "Tailwind CSS 3.4.1",
  "pdf": "react-pdf 7.6.0",
  "signature": "react-signature-canvas 1.0.6"
}
```

**백엔드 API 구조**:
```
Base URL: http://20.196.83.145:8000/api/v1

인증:
- POST /auth/login
- POST /auth/logout
- GET  /auth/me

평가:
- GET  /evaluations/my
- GET  /evaluations/{id}
- PUT  /evaluations/{id}
- POST /evaluations/{id}/submit

OCR:
- POST /ocr/analyze
- GET  /ocr/engines

프로젝트/기업:
- GET  /projects
- GET  /companies
- POST /companies
```

**상태 관리 설계**:
```javascript
// stores/authStore.js
{
  user: null,
  token: null,
  isAuthenticated: false,
  login: (credentials) => {},
  logout: () => {}
}

// stores/evaluationStore.js
{
  evaluations: [],
  currentEvaluation: null,
  isDirty: false,
  autoSave: () => {}
}
```

---

### 3️⃣ Systematize (체계적 구현)

**디렉토리 구조**:
```
frontend/src/
├── components/          # 재사용 컴포넌트
│   ├── common/         # Button, Input, Modal 등
│   ├── layout/         # Header, Sidebar, Layout
│   ├── admin/          # 관리자 전용 컴포넌트
│   └── evaluator/      # 심사위원 전용 컴포넌트
├── pages/              # 페이지 컴포넌트
│   ├── LoginPage.jsx
│   ├── AdminDashboard.jsx
│   └── EvaluatorPage.jsx
├── hooks/              # 커스텀 훅
│   ├── useAuth.js
│   ├── useApi.js
│   └── useAutoSave.js
├── services/           # API 서비스
│   ├── api.js          # Axios 인스턴스
│   ├── authService.js
│   └── evaluationService.js
├── stores/             # Zustand 스토어
│   ├── authStore.js
│   └── evaluationStore.js
├── utils/              # 유틸리티
│   ├── validators.js
│   └── formatters.js
├── App.jsx
└── index.js
```

**개발 우선순위**:

**Phase 1: 인증 기반** (1-2시간)
1. API 클라이언트 설정 (axios interceptor)
2. Auth Store 구현
3. 로그인 페이지 완성
4. Protected Route 구현
5. 토큰 갱신 로직

**Phase 2: 심사위원 기능** (2-3시간)
1. 평가 목록 조회
2. 평가 상세 페이지
3. 점수 입력 폼
4. 자동 저장 기능
5. 평가 제출 (불변성 처리)

**Phase 3: 관리자 기능** (2-3시간)
1. 대시보드 레이아웃
2. 프로젝트 관리
3. 기업 관리 (OCR 연동)
4. 점수 집계 뷰
5. 감사 로그 뷰

**Phase 4: UX 개선** (1-2시간)
1. 로딩 스피너
2. 에러 바운더리
3. 토스트 알림
4. 반응형 디자인 검증
5. 접근성 개선

---

### 4️⃣ Test (테스트 전략)

**단위 테스트**:
```javascript
// components/common/Button.test.js
describe('Button Component', () => {
  it('renders correctly', () => {});
  it('calls onClick handler', () => {});
  it('shows loading state', () => {});
});
```

**통합 테스트**:
```javascript
// pages/LoginPage.test.js
describe('Login Flow', () => {
  it('successfully logs in with valid credentials', async () => {
    // Mock API
    // Submit form
    // Verify redirect
  });

  it('shows error with invalid credentials', async () => {});
});
```

**E2E 테스트 시나리오**:
1. 로그인 → 평가 목록 → 평가 작성 → 제출
2. 로그인 → OCR 업로드 → 기업 등록
3. 로그인 → 점수 집계 조회

---

### 5️⃣ Expand (확장성)

**추후 추가 기능**:
- 📊 차트 라이브러리 (Recharts)
- 📄 Excel 내보내기
- 🔔 실시간 알림 (WebSocket)
- 🌐 다국어 지원 (i18n)
- 🎨 테마 전환 (다크 모드)

---

### 6️⃣ Refine (개선)

**성능 최적화**:
```javascript
// React.memo로 불필요한 리렌더링 방지
export const ScoreInput = React.memo(({ score, onChange }) => {
  return <input value={score} onChange={onChange} />;
});

// useMemo로 expensive 계산 캐싱
const sortedEvaluations = useMemo(() => {
  return evaluations.sort((a, b) => b.createdAt - a.createdAt);
}, [evaluations]);

// useCallback으로 함수 참조 유지
const handleSave = useCallback(() => {
  saveEvaluation(currentEvaluation);
}, [currentEvaluation]);
```

**코드 품질**:
- ESLint + Prettier
- PropTypes 또는 TypeScript
- 의미 있는 변수명
- JSDoc 주석

---

## 워크플로우

사용자가 프론트엔드 개발을 요청하면:

### Step 1: 요구사항 확인
```
어떤 페이지/기능을 구현할까요?
1. 로그인 페이지
2. 평가 페이지
3. 관리자 대시보드
4. OCR 업로드
5. 점수 집계

우선순위: [1 → 2 → 3]
```

### Step 2: API 연동 확인
```
백엔드 API 문서 확인:
- Swagger UI: http://20.196.83.145:8000/api/docs
- API_TEST_SAMPLES.md 참조

필요한 엔드포인트:
✅ POST /auth/login
✅ GET /evaluations/my
✅ PUT /evaluations/{id}
```

### Step 3: 컴포넌트 설계
```
페이지 구조:
LoginPage
├── LoginForm
│   ├── Input (username)
│   ├── Input (password)
│   └── Button (submit)
└── ErrorMessage
```

### Step 4: 구현
```javascript
// 1. API 서비스
// 2. Zustand 스토어
// 3. 커스텀 훅
// 4. 컴포넌트
// 5. 페이지 통합
```

### Step 5: 테스트
```
✅ API 연동 확인
✅ 폼 검증
✅ 에러 처리
✅ 로딩 상태
✅ 반응형 디자인
```

### Step 6: 문서화
```markdown
# LoginPage

## 사용법
- URL: /login
- 테스트 계정: admin / Admin123!

## 주요 기능
- JWT 토큰 인증
- 자동 로그인 (Remember Me)
- 에러 메시지 표시
```

---

## 코딩 스타일 가이드

### React 컴포넌트
```javascript
// ✅ Good: 함수형 컴포넌트 + Hooks
import React, { useState, useEffect } from 'react';

export const LoginForm = ({ onSubmit, isLoading }) => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(credentials);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input
        type="text"
        value={credentials.username}
        onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
        className="w-full px-4 py-2 border rounded-lg"
        placeholder="사용자명"
        disabled={isLoading}
      />
      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        {isLoading ? '로그인 중...' : '로그인'}
      </button>
    </form>
  );
};
```

### API 서비스
```javascript
// services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: 토큰 자동 추가
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: 에러 처리
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### Zustand 스토어
```javascript
// stores/authStore.js
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (credentials) => {
        const response = await api.post('/auth/login', credentials);
        const { access_token, user } = response.data;

        localStorage.setItem('token', access_token);
        set({ user, token: access_token, isAuthenticated: true });
      },

      logout: () => {
        localStorage.removeItem('token');
        set({ user: null, token: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);
```

---

## 체크리스트

### 새 페이지 개발 시
- [ ] API 엔드포인트 확인
- [ ] 필요한 상태 정의
- [ ] 컴포넌트 분해
- [ ] API 서비스 함수 작성
- [ ] 에러 처리 추가
- [ ] 로딩 상태 추가
- [ ] 폼 검증 추가
- [ ] 반응형 디자인 확인
- [ ] 접근성 검증
- [ ] 테스트 작성

### 배포 전
- [ ] 환경 변수 설정 (.env)
- [ ] API URL 프로덕션으로 변경
- [ ] 빌드 최적화 확인
- [ ] Lighthouse 점수 확인
- [ ] 크로스 브라우저 테스트
- [ ] 모바일 테스트

---

## 참고 문서

- `references/api-integration-guide.md` - API 연동 패턴
- `references/component-patterns.md` - React 컴포넌트 패턴
- `references/tailwind-design-system.md` - Tailwind CSS 디자인 시스템
- `templates/page-template.jsx` - 페이지 템플릿
- `templates/component-template.jsx` - 컴포넌트 템플릿
- `scripts/generate-component.sh` - 컴포넌트 자동 생성

---

## 성공 기준

✅ 모든 API가 정상 작동
✅ 사용자 플로우가 직관적
✅ 로딩/에러 상태가 명확
✅ 모바일에서도 사용 가능
✅ 보안 취약점 없음
✅ 성능 지표 양호 (Lighthouse 90+)

---

**이 스킬로 빠르고 안정적인 프론트엔드를 구현합니다! 🚀**
