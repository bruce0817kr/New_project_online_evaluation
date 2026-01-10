import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useEvaluationStore } from '../stores/evaluationStore';
import evaluationService from '../services/evaluationService';
import companyService from '../services/companyService';
import { useAutoSave } from '../hooks/useAutoSave';

function EvaluationDetailPage() {
  const { evaluationId } = useParams();
  const navigate = useNavigate();

  const {
    currentEvaluation,
    setCurrentEvaluation,
    updateScore,
    updateComments,
    isDirty,
    lastSaved,
    markAsSaved,
    isSubmitted,
  } = useEvaluationStore();

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [documentInfo, setDocumentInfo] = useState(null);
  const [showDocument, setShowDocument] = useState(false);

  // 평가 상세 로드
  useEffect(() => {
    loadEvaluation();
  }, [evaluationId]);

  const loadEvaluation = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await evaluationService.getEvaluationById(evaluationId);
      setCurrentEvaluation(data);

      // 서류 정보 로드
      if (data.company_id) {
        try {
          const docInfo = await companyService.getDocumentInfo(data.company_id);
          setDocumentInfo(docInfo);
        } catch (err) {
          console.error('Failed to load document info:', err);
        }
      }
    } catch (err) {
      console.error('Failed to load evaluation:', err);
      setError(err.response?.data?.detail || '평가를 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  // 자동 저장 함수
  const handleAutoSave = async (data) => {
    if (isSubmitted()) {
      console.log('Already submitted, skipping auto-save');
      return;
    }

    try {
      await evaluationService.updateEvaluation(evaluationId, {
        scores: data.scores,
        comments: data.comments,
      });
      markAsSaved();
    } catch (error) {
      console.error('Auto-save failed:', error);
    }
  };

  // 자동 저장 훅 (3초 디바운스, 제출되지 않았을 때만)
  useAutoSave(currentEvaluation, handleAutoSave, 3000, !isSubmitted());

  // 평가 제출
  const handleSubmit = async () => {
    if (!window.confirm('평가를 제출하시겠습니까? 제출 후에는 수정할 수 없습니다.')) {
      return;
    }

    try {
      setSubmitting(true);
      await evaluationService.submitEvaluation(evaluationId);

      alert('평가가 성공적으로 제출되었습니다!');
      navigate('/evaluator');
    } catch (err) {
      console.error('Submit failed:', err);
      alert(err.response?.data?.detail || '제출에 실패했습니다');
    } finally {
      setSubmitting(false);
    }
  };

  // 로딩 상태
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  // 에러 상태
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/evaluator')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            목록으로 돌아가기
          </button>
        </div>
      </div>
    );
  }

  if (!currentEvaluation) {
    return null;
  }

  const evaluation = currentEvaluation;
  const readOnly = evaluation.is_submitted;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/evaluator')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <div>
              <h1 className="text-xl font-bold text-gray-900">{evaluation.company_name}</h1>
              <p className="text-sm text-gray-600">{evaluation.project_name}</p>
            </div>
          </div>

          {/* 상태 표시 */}
          <div className="flex items-center gap-3">
            {readOnly ? (
              <span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded-full">
                제출완료
              </span>
            ) : (
              <>
                {isDirty ? (
                  <span className="text-sm text-yellow-600">저장 중...</span>
                ) : lastSaved ? (
                  <span className="text-sm text-gray-500">
                    저장됨 {lastSaved.toLocaleTimeString()}
                  </span>
                ) : null}
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-6 py-8">
        {/* 서류 보기 섹션 */}
        {documentInfo?.has_document && (
          <div className="bg-white rounded-lg shadow mb-6">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">사업계획서</h2>
                  <p className="text-sm text-gray-600 mt-1">
                    {documentInfo.filename} ({(documentInfo.file_size / 1024 / 1024).toFixed(2)} MB)
                  </p>
                </div>
                <button
                  onClick={() => setShowDocument(!showDocument)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d={showDocument ? "M6 18L18 6M6 6l12 12" : "M15 12a3 3 0 11-6 0 3 3 0 016 0z"}
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d={showDocument ? "" : "M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"}
                    />
                  </svg>
                  {showDocument ? '닫기' : '서류 보기'}
                </button>
              </div>
            </div>

            {/* 문서 뷰어 */}
            {showDocument && (
              <div className="p-6 bg-gray-50">
                {documentInfo.file_type === '.pdf' ? (
                  <iframe
                    src={companyService.getDocumentUrl(evaluation.company_id)}
                    className="w-full h-[600px] border border-gray-300 rounded-lg"
                    title="사업계획서"
                  />
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-600 mb-4">
                      미리보기를 지원하지 않는 파일 형식입니다.
                    </p>
                    <button
                      onClick={async () => {
                        try {
                          const blob = await companyService.downloadDocument(evaluation.company_id);
                          const url = window.URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = documentInfo.filename;
                          a.click();
                          window.URL.revokeObjectURL(url);
                        } catch (err) {
                          console.error('Download failed:', err);
                          alert('다운로드에 실패했습니다');
                        }
                      }}
                      className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                    >
                      다운로드
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* 서류 없음 안내 */}
        {documentInfo && !documentInfo.has_document && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-yellow-800">
              ⚠️ 이 기업은 아직 서류를 제출하지 않았습니다.
            </p>
          </div>
        )}

        <div className="bg-white rounded-lg shadow">
          {/* 점수 입력 섹션 */}
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold mb-4">평가 점수</h2>

            <div className="space-y-4">
              {['기술성', '사업성', '경제성'].map((criteria) => (
                <div key={criteria}>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {criteria}
                  </label>

                  <div className="flex items-center gap-4">
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={evaluation.scores?.[criteria] || 0}
                      onChange={(e) => updateScore(criteria, e.target.value)}
                      disabled={readOnly}
                      className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50"
                    />

                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      value={evaluation.scores?.[criteria] || 0}
                      onChange={(e) => updateScore(criteria, e.target.value)}
                      disabled={readOnly}
                      className="w-20 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                    />

                    <span className="text-sm text-gray-600 w-8">점</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 코멘트 섹션 */}
          <div className="p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              평가 의견
            </label>

            <textarea
              value={evaluation.comments || ''}
              onChange={(e) => updateComments(e.target.value)}
              disabled={readOnly}
              rows={6}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 resize-none"
              placeholder="평가 의견을 입력하세요..."
            />
          </div>

          {/* 액션 버튼 */}
          {!readOnly && (
            <div className="p-6 bg-gray-50 rounded-b-lg flex justify-end gap-3">
              <button
                onClick={() => navigate('/evaluator')}
                className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
              >
                취소
              </button>

              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {submitting ? (
                  <>
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                    제출 중...
                  </>
                ) : (
                  '평가 제출'
                )}
              </button>
            </div>
          )}

          {/* 제출 완료 안내 */}
          {readOnly && (
            <div className="p-6 bg-green-50 rounded-b-lg">
              <p className="text-sm text-green-800">
                이 평가는 {new Date(evaluation.submitted_at).toLocaleString('ko-KR')}에 제출되었습니다.
                <br />
                제출된 평가는 수정할 수 없습니다.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default EvaluationDetailPage;
