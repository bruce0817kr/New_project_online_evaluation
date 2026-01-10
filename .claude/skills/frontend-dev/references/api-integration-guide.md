# API 연동 가이드

## Axios 설정

### 기본 설정
```javascript
// src/services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// JWT 토큰 자동 추가
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 에러 처리
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## 서비스 함수 패턴

### 인증 서비스
```javascript
// src/services/authService.js
import { api } from './api';

export const authService = {
  login: async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response;
  },

  logout: async () => {
    await api.post('/auth/logout');
    localStorage.removeItem('token');
  },

  getCurrentUser: async () => {
    return await api.get('/auth/me');
  },
};
```

### 평가 서비스
```javascript
// src/services/evaluationService.js
import { api } from './api';

export const evaluationService = {
  getMyEvaluations: async (status = null) => {
    const params = status ? { status } : {};
    return await api.get('/evaluations/my', { params });
  },

  getEvaluationById: async (id) => {
    return await api.get(`/evaluations/${id}`);
  },

  updateEvaluation: async (id, data) => {
    return await api.put(`/evaluations/${id}`, data);
  },

  submitEvaluation: async (id) => {
    return await api.post(`/evaluations/${id}/submit`);
  },
};
```

### OCR 서비스
```javascript
// src/services/ocrService.js
import { api } from './api';

export const ocrService = {
  analyzeDocument: async (file, documentType, preferredEngine = null) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    if (preferredEngine) {
      formData.append('preferred_engine', preferredEngine);
    }

    return await api.post('/ocr/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  getAvailableEngines: async () => {
    return await api.get('/ocr/engines');
  },
};
```

## 커스텀 훅 패턴

### useApi 훅
```javascript
// src/hooks/useApi.js
import { useState, useCallback } from 'react';

export const useApi = (apiFunc) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(
    async (...args) => {
      try {
        setLoading(true);
        setError(null);
        const result = await apiFunc(...args);
        setData(result);
        return result;
      } catch (err) {
        setError(err.response?.data?.detail || '오류가 발생했습니다');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [apiFunc]
  );

  return { data, loading, error, execute };
};

// 사용 예시
const { data: evaluations, loading, error, execute: loadEvaluations } = useApi(
  evaluationService.getMyEvaluations
);

useEffect(() => {
  loadEvaluations('in_progress');
}, []);
```

### useAuth 훅
```javascript
// src/hooks/useAuth.js
import { useAuthStore } from '../stores/authStore';
import { authService } from '../services/authService';
import { useState } from 'react';

export const useAuth = () => {
  const { user, isAuthenticated, setUser, logout: storeLogout } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const login = async (username, password) => {
    try {
      setLoading(true);
      setError(null);

      const response = await authService.login(username, password);
      const { access_token, user: userData } = response;

      localStorage.setItem('token', access_token);
      setUser(userData, access_token);

      return true;
    } catch (err) {
      setError(err.response?.data?.detail || '로그인에 실패했습니다');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      storeLogout();
    }
  };

  return { user, isAuthenticated, login, logout, loading, error };
};
```

## 에러 처리 패턴

### 에러 바운더리
```javascript
// src/components/common/ErrorBoundary.jsx
import React from 'react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-red-600 mb-4">
              오류가 발생했습니다
            </h1>
            <p className="text-gray-600 mb-4">{this.state.error?.message}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-600 text-white rounded"
            >
              새로고침
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### 토스트 알림
```javascript
// src/hooks/useToast.js
import { useState, useCallback } from 'react';

export const useToast = () => {
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((message, type = 'info') => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);

    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3000);
  }, []);

  return { toasts, showToast };
};

// Toast 컴포넌트
export const Toast = ({ message, type, onClose }) => {
  const bgColors = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    info: 'bg-blue-500',
  };

  return (
    <div className={`${bgColors[type]} text-white px-6 py-3 rounded-lg shadow-lg`}>
      <div className="flex items-center justify-between">
        <span>{message}</span>
        <button onClick={onClose} className="ml-4">×</button>
      </div>
    </div>
  );
};
```

## 로딩 상태 패턴

### 스켈레톤 로더
```javascript
// src/components/common/Skeleton.jsx
export const Skeleton = ({ className = '' }) => {
  return (
    <div className={`animate-pulse bg-gray-200 rounded ${className}`} />
  );
};

// 사용 예시
{loading ? (
  <div className="space-y-4">
    <Skeleton className="h-20 w-full" />
    <Skeleton className="h-20 w-full" />
    <Skeleton className="h-20 w-full" />
  </div>
) : (
  <EvaluationList evaluations={evaluations} />
)}
```

### 인라인 로더
```javascript
// src/components/common/Spinner.jsx
export const Spinner = ({ size = 'md' }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className={`${sizes[size]} border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin`} />
  );
};
```

## 폼 처리 패턴

### 폼 검증
```javascript
// src/utils/validators.js
export const validators = {
  required: (value) => {
    return value && value.trim() !== '' ? null : '필수 입력 항목입니다';
  },

  email: (value) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value) ? null : '올바른 이메일 형식이 아닙니다';
  },

  minLength: (min) => (value) => {
    return value && value.length >= min ? null : `최소 ${min}자 이상 입력해주세요`;
  },

  scoreRange: (value) => {
    const num = parseFloat(value);
    return num >= 0 && num <= 100 ? null : '0-100 사이의 값을 입력해주세요';
  },
};

// 사용 예시
const [errors, setErrors] = useState({});

const validateForm = () => {
  const newErrors = {};

  const usernameError = validators.required(username);
  if (usernameError) newErrors.username = usernameError;

  const passwordError = validators.minLength(6)(password);
  if (passwordError) newErrors.password = passwordError;

  setErrors(newErrors);
  return Object.keys(newErrors).length === 0;
};
```

### 자동 저장
```javascript
// src/hooks/useAutoSave.js
import { useEffect, useRef } from 'react';

export const useAutoSave = (data, saveFunction, delay = 2000) => {
  const timeoutRef = useRef(null);

  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      saveFunction(data);
    }, delay);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [data, saveFunction, delay]);
};

// 사용 예시
const [evaluation, setEvaluation] = useState({});
const [lastSaved, setLastSaved] = useState(null);

const handleSave = async (data) => {
  await evaluationService.updateEvaluation(evaluationId, data);
  setLastSaved(new Date());
};

useAutoSave(evaluation, handleSave, 3000);
```

## 보안 패턴

### XSS 방지
```javascript
// React는 기본적으로 XSS를 방지하지만,
// dangerouslySetInnerHTML 사용 시 주의

import DOMPurify from 'dompurify';

export const SafeHTML = ({ html }) => {
  const sanitized = DOMPurify.sanitize(html);
  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
};
```

### Protected Route
```javascript
// src/components/common/ProtectedRoute.jsx
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';

export const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { isAuthenticated, user } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user?.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

// 사용 예시
<Route
  path="/admin/*"
  element={
    <ProtectedRoute allowedRoles={['admin']}>
      <AdminDashboard />
    </ProtectedRoute>
  }
/>
```
