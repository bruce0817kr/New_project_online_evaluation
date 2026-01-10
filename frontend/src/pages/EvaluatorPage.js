import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import evaluationService from '../services/evaluationService';
import EvaluationDetailPage from './EvaluationDetailPage';

function EvaluatorPage() {
  return (
    <Routes>
      <Route index element={<EvaluationListPage />} />
      <Route path=":evaluationId" element={<EvaluationDetailPage />} />
    </Routes>
  );
}

/**
 * 평가 목록 페이지
 */
function EvaluationListPage() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const [evaluations, setEvaluations] = useState([]);
  const [filter, setFilter] = useState('all'); // 'all' | 'in_progress' | 'submitted'
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 평가 목록 로드
  useEffect(() => {
    loadEvaluations();
  }, [filter]);

  const loadEvaluations = async () => {
    try {
      setLoading(true);
      setError(null);

      const status = filter === 'all' ? null : filter;
      const data = await evaluationService.getMyEvaluations(status);

      setEvaluations(data);
    } catch (err) {
      console.error('Failed to load evaluations:', err);
      setError(err.response?.data?.detail || '평가 목록을 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  // 평가 카드 클릭
  const handleEvaluationClick = (evaluationId) => {
    navigate(`/evaluator/${evaluationId}`);
  };

  // 통계 계산
  const stats = {
    total: evaluations.length,
    inProgress: evaluations.filter((e) => !e.is_submitted).length,
    submitted: evaluations.filter((e) => e.is_submitted).length,
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">내 평가 목록</h1>
            <p className="text-sm text-gray-600 mt-1">
              {user?.full_name} 님 ({user?.username})
            </p>
          </div>

          <button
            onClick={logout}
            className="px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            로그아웃
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-600 mb-2">전체 평가</div>
            <div className="text-3xl font-bold text-gray-900">{stats.total}</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-600 mb-2">진행중</div>
            <div className="text-3xl font-bold text-blue-600">{stats.inProgress}</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-600 mb-2">제출완료</div>
            <div className="text-3xl font-bold text-green-600">{stats.submitted}</div>
          </div>
        </div>

        {/* 필터 탭 */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setFilter('all')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  filter === 'all'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                전체 ({stats.total})
              </button>

              <button
                onClick={() => setFilter('in_progress')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  filter === 'in_progress'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                진행중 ({stats.inProgress})
              </button>

              <button
                onClick={() => setFilter('submitted')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  filter === 'submitted'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                제출완료 ({stats.submitted})
              </button>
            </nav>
          </div>
        </div>

        {/* 로딩 상태 */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
          </div>
        )}

        {/* 에러 상태 */}
        {error && !loading && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-600 text-sm">{error}</p>
            <button
              onClick={loadEvaluations}
              className="mt-2 text-sm text-red-700 hover:text-red-900 underline"
            >
              다시 시도
            </button>
          </div>
        )}

        {/* 평가 목록 */}
        {!loading && !error && (
          <div className="space-y-4">
            {evaluations.length === 0 ? (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <p className="text-gray-500">평가 과제가 없습니다</p>
              </div>
            ) : (
              evaluations.map((evaluation) => (
                <div
                  key={evaluation.id}
                  onClick={() => handleEvaluationClick(evaluation.id)}
                  className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer p-6"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {evaluation.company_name || '기업명 없음'}
                        </h3>

                        {/* 상태 배지 */}
                        {evaluation.is_submitted ? (
                          <span className="px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                            제출완료
                          </span>
                        ) : (
                          <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                            진행중
                          </span>
                        )}
                      </div>

                      <p className="text-sm text-gray-600 mb-3">
                        {evaluation.project_name || '프로젝트명 없음'}
                      </p>

                      {/* 점수 미리보기 */}
                      {evaluation.scores && Object.keys(evaluation.scores).length > 0 && (
                        <div className="flex gap-4 text-sm">
                          {Object.entries(evaluation.scores).map(([key, value]) => (
                            <div key={key}>
                              <span className="text-gray-600">{key}: </span>
                              <span className="font-semibold text-gray-900">{value}점</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* 화살표 아이콘 */}
                    <div className="ml-4">
                      <svg
                        className="w-6 h-6 text-gray-400"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </div>
                  </div>

                  {/* 마지막 업데이트 시간 */}
                  <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-500">
                    {evaluation.is_submitted ? (
                      <span>
                        제출: {new Date(evaluation.submitted_at).toLocaleString('ko-KR')}
                      </span>
                    ) : (
                      <span>
                        최종 수정: {new Date(evaluation.updated_at).toLocaleString('ko-KR')}
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default EvaluatorPage;
