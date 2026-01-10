import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';

/**
 * 보호된 라우트 컴포넌트
 * 로그인하지 않은 사용자는 로그인 페이지로 리다이렉트
 * 권한이 없는 사용자는 접근 거부
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - 보호할 컴포넌트
 * @param {string[]} [props.allowedRoles] - 허용된 역할 목록 (admin, evaluator)
 */
export const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { isAuthenticated, user } = useAuthStore();

  // 인증되지 않은 경우 로그인 페이지로
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // 역할 권한 체크
  if (allowedRoles.length > 0 && user && !allowedRoles.includes(user.role)) {
    // 권한 없음 페이지로 리다이렉트
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="mb-6">
            <svg
              className="mx-auto h-24 w-24 text-red-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            접근 권한이 없습니다
          </h1>
          <p className="text-gray-600 mb-8">
            이 페이지에 접근할 권한이 없습니다.
          </p>
          <button
            onClick={() => window.history.back()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            돌아가기
          </button>
        </div>
      </div>
    );
  }

  // 인증 및 권한 확인 완료, children 렌더링
  return children;
};

export default ProtectedRoute;
