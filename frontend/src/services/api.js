import axios from 'axios';

// API Base URL - 환경 변수에서 가져오기
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Axios 인스턴스 생성
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30초
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: 모든 요청에 JWT 토큰 자동 추가
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 요청 로깅 (개발 환경에서만)
    if (process.env.NODE_ENV === 'development') {
      console.log('🚀 API Request:', config.method.toUpperCase(), config.url);
    }

    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response Interceptor: 응답 처리 및 에러 핸들링
api.interceptors.response.use(
  (response) => {
    // 성공 응답 로깅 (개발 환경에서만)
    if (process.env.NODE_ENV === 'development') {
      console.log('✅ API Response:', response.config.url, response.status);
    }

    // 응답 데이터만 반환
    return response.data;
  },
  (error) => {
    // 에러 로깅
    console.error('❌ API Error:', error.response?.status, error.response?.data);

    // 401 Unauthorized: 토큰 만료 또는 인증 실패
    if (error.response?.status === 401) {
      // 토큰 제거
      localStorage.removeItem('token');
      localStorage.removeItem('user');

      // 로그인 페이지로 리다이렉트 (현재 페이지가 로그인이 아닐 때만)
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }

    // 403 Forbidden: 권한 없음
    if (error.response?.status === 403) {
      alert('접근 권한이 없습니다.');
    }

    // 500 Internal Server Error
    if (error.response?.status === 500) {
      console.error('서버 오류가 발생했습니다.');
    }

    return Promise.reject(error);
  }
);

export default api;
