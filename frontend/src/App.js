import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import AdminDashboard from './pages/AdminDashboard';
import EvaluatorPage from './pages/EvaluatorPage';
import LoginPage from './pages/LoginPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          {/* 루트 경로는 로그인 페이지로 리다이렉트 */}
          <Route path="/" element={<Navigate to="/login" replace />} />

          {/* 로그인 페이지 */}
          <Route path="/login" element={<LoginPage />} />

          {/* 관리자 전용 페이지 - admin 역할만 접근 가능 */}
          <Route
            path="/admin/*"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />

          {/* 심사위원 전용 페이지 - evaluator 역할만 접근 가능 */}
          <Route
            path="/evaluator/*"
            element={
              <ProtectedRoute allowedRoles={['evaluator']}>
                <EvaluatorPage />
              </ProtectedRoute>
            }
          />

          {/* 404 Not Found */}
          <Route
            path="*"
            element={
              <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                  <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
                  <p className="text-xl text-gray-600 mb-8">페이지를 찾을 수 없습니다</p>
                  <a href="/login" className="text-blue-600 hover:text-blue-700">
                    로그인 페이지로 돌아가기
                  </a>
                </div>
              </div>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
