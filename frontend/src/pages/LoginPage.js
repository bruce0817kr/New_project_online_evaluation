import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

function LoginPage() {
  const navigate = useNavigate();
  const { login, isAuthenticated, loading, error, isAdmin } = useAuth();

  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [localError, setLocalError] = useState('');

  // 이미 로그인된 경우 리다이렉트
  useEffect(() => {
    if (isAuthenticated) {
      // 관리자는 관리자 대시보드로, 심사위원은 평가 페이지로
      if (isAdmin()) {
        navigate('/admin');
      } else {
        navigate('/evaluator');
      }
    }
  }, [isAuthenticated, isAdmin, navigate]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLocalError('');

    // 입력 검증
    if (!credentials.username.trim()) {
      setLocalError('사용자명을 입력하세요');
      return;
    }

    if (!credentials.password) {
      setLocalError('비밀번호를 입력하세요');
      return;
    }

    // 로그인 API 호출
    const result = await login(credentials.username, credentials.password);

    if (result.success) {
      // 성공 시 자동으로 useEffect에서 리다이렉트됨
      console.log('로그인 성공!');
    } else {
      setLocalError(result.error);
    }
  };

  const handleInputChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
    // 입력 시 에러 메시지 초기화
    setLocalError('');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600 px-4">
      <div className="bg-white p-8 rounded-lg shadow-2xl w-full max-w-md">
        {/* 헤더 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            중소기업 선정평가 시스템
          </h1>
          <p className="text-gray-600 text-sm">
            SME Evaluation Management System
          </p>
        </div>

        {/* 에러 메시지 */}
        {(localError || error) && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600 text-sm flex items-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              {localError || error}
            </p>
          </div>
        )}

        {/* 로그인 폼 */}
        <form onSubmit={handleLogin} className="space-y-6">
          {/* 사용자명 입력 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              사용자명
            </label>
            <input
              type="text"
              name="username"
              value={credentials.username}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
              placeholder="아이디를 입력하세요"
              disabled={loading}
              autoComplete="username"
              autoFocus
            />
          </div>

          {/* 비밀번호 입력 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              비밀번호
            </label>
            <input
              type="password"
              name="password"
              value={credentials.password}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
              placeholder="비밀번호를 입력하세요"
              disabled={loading}
              autoComplete="current-password"
            />
          </div>

          {/* 로그인 버튼 */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                로그인 중...
              </>
            ) : (
              '로그인'
            )}
          </button>
        </form>

        {/* 테스트 계정 안내 (개발 환경에서만) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <p className="text-xs text-gray-600 font-semibold mb-2">테스트 계정:</p>
            <div className="text-xs text-gray-500 space-y-1">
              <p>• 관리자: <code className="bg-gray-200 px-1 rounded">admin / Admin123!</code></p>
              <p>• 심사위원: <code className="bg-gray-200 px-1 rounded">evaluator1 / Eval123!</code></p>
            </div>
          </div>
        )}

        {/* 푸터 */}
        <div className="mt-8 text-center text-xs text-gray-500">
          <p>© 2026 SME Evaluation System</p>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
