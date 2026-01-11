import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useEvaluationStore } from '../stores/evaluationStore';
import evaluationService from '../services/evaluationService';
import companyService from '../services/companyService';
import { useAutoSave } from '../hooks/useAutoSave';
import SignatureCanvas from 'react-signature-canvas';

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
  const [showSignatureModal, setShowSignatureModal] = useState(false);
  const [signatureData, setSignatureData] = useState(null);

  // Canvas 서명 참조
  const signatureCanvasRef = useRef(null);

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

  // 제출 버튼 클릭 (서명 모달 열기)
  const handleSubmitClick = () => {
    setShowSignatureModal(true);
  };

  // 평가 제출 (서명 포함)
  const handleSubmit = async () => {
    // Canvas가 비어있는지 확인
    if (!signatureCanvasRef.current || signatureCanvasRef.current.isEmpty()) {
      alert('서명을 작성해주세요');
      return;
    }

    try {
      setSubmitting(true);

      // Canvas에서 Base64 이미지 추출
      const signatureImage = signatureCanvasRef.current.toDataURL('image/png');

      // 서명 데이터와 함께 제출
      await evaluationService.submitEvaluation(evaluationId, { signature_data: signatureImage });

      alert('평가가 성공적으로 제출되었습니다!');
      navigate('/evaluator');
    } catch (err) {
      console.error('Submit failed:', err);
      alert(err.response?.data?.detail || '제출에 실패했습니다');
    } finally {
      setSubmitting(false);
      setShowSignatureModal(false);
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

      {/* Main Content - Split View */}
      <main className="h-[calc(100vh-100px)]">
        <div className="h-full flex">
          {/* Left Panel: PDF Viewer (60%) */}
          <div className="w-3/5 border-r border-gray-200 flex flex-col bg-gray-50">
            <div className="flex-shrink-0 px-6 py-4 border-b border-gray-200 bg-white">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">사업계획서</h2>
                  {documentInfo?.has_document && (
                    <p className="text-sm text-gray-600 mt-1">
                      {documentInfo.filename} ({(documentInfo.file_size / 1024 / 1024).toFixed(2)} MB)
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Document Viewer Area */}
            <div className="flex-1 overflow-auto p-6">
              {documentInfo?.has_document ? (
                documentInfo.file_type === '.pdf' ? (
                  <iframe
                    src={companyService.getDocumentUrl(evaluation.company_id)}
                    className="w-full h-full border border-gray-300 rounded-lg"
                    title="사업계획서"
                  />
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
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
                  </div>
                )
              ) : (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p className="mt-2 text-sm text-gray-600">⚠️ 이 기업은 아직 서류를 제출하지 않았습니다.</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel: Evaluation Form (40%) */}
          <div className="w-2/5 flex flex-col bg-white">
            <div className="flex-1 overflow-y-auto">
              {/* 점수 입력 섹션 */}
          <div className="p-6">
            <h2 className="text-lg font-semibold mb-4">평가 점수</h2>

            {/* 동적 배점표 렌더링 */}
            {evaluation.scoring_template ? (
              <div className="space-y-6">
                {evaluation.scoring_template.sections.map((section, sectionIdx) => (
                  <div key={sectionIdx} className="border-b border-gray-200 pb-6 last:border-0">
                    <h3 className="font-medium text-gray-900 mb-3">
                      {section.section_name} (배점: {section.max_score}점)
                    </h3>

                    <div className="space-y-4">
                      {section.items.map((item) => (
                        <div key={item.item_id} className="bg-gray-50 p-4 rounded-lg">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex-1">
                              <label className="block text-sm font-medium text-gray-700">
                                {item.title}
                              </label>
                              {item.description && (
                                <p className="text-xs text-gray-500 mt-1">{item.description}</p>
                              )}
                            </div>
                            <span className="text-sm text-gray-600 ml-2">/ {item.max_score}점</span>
                          </div>

                          <input
                            type="number"
                            min="0"
                            max={item.max_score}
                            step={item.step || 1}
                            value={evaluation.scores?.[item.item_id] || 0}
                            onChange={(e) => updateScore(item.item_id, e.target.value)}
                            disabled={readOnly}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              /* 기본 하드코딩 항목 (템플릿 없을 때) */
              <div className="space-y-4">
                {['기술성', '사업성', '경제성'].map((criteria) => (
                  <div key={criteria}>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {criteria}
                    </label>

                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={evaluation.scores?.[criteria] || 0}
                      onChange={(e) => updateScore(criteria, e.target.value)}
                      disabled={readOnly}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                    />
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 코멘트 섹션 */}
          <div className="p-6 border-t border-gray-200">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              종합 의견 (필수)
            </label>

            <textarea
              value={evaluation.comments || ''}
              onChange={(e) => updateComments(e.target.value)}
              disabled={readOnly}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 resize-none"
              placeholder="종합 평가 의견을 입력하세요... (최소 50자)"
            />
          </div>
            </div>

            {/* Sticky Footer: 총점 및 액션 버튼 */}
            <div className="flex-shrink-0 border-t border-gray-200 bg-gray-50">
              {/* 총점 표시 */}
              <div className="px-6 py-3 bg-blue-50 border-b border-blue-100">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">총점</span>
                  <span className="text-2xl font-bold text-blue-600">
                    {Object.values(evaluation.scores || {}).reduce((sum, val) => sum + (parseFloat(val) || 0), 0).toFixed(1)}
                    <span className="text-sm text-gray-600 ml-1">
                      / {evaluation.scoring_template?.total_score || 100}점
                    </span>
                  </span>
                </div>
              </div>

              {/* 액션 버튼 */}
              {!readOnly ? (
                <div className="p-4 flex justify-end gap-3">
                  <button
                    onClick={() => navigate('/evaluator')}
                    className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    목록으로
                  </button>

                  <button
                    onClick={handleSubmitClick}
                    disabled={submitting}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
                  >
                    평가 제출
                  </button>
                </div>
              ) : (
                <div className="p-4 bg-green-50">
                  <p className="text-sm text-green-800 text-center">
                    ✓ {new Date(evaluation.submitted_at).toLocaleString('ko-KR')}에 제출 완료
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* 전자 서명 모달 (Canvas 드로잉) */}
      {showSignatureModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold">전자 서명</h2>
              <p className="text-sm text-gray-600 mt-1">
                아래 서명란에 마우스나 터치로 직접 서명해주세요
              </p>
            </div>

            <div className="p-6">
              {/* Canvas 서명 패드 */}
              <div className="border-2 border-gray-300 rounded-lg bg-white mb-4 relative">
                <SignatureCanvas
                  ref={signatureCanvasRef}
                  canvasProps={{
                    width: 600,
                    height: 200,
                    className: 'signature-canvas w-full h-full'
                  }}
                  backgroundColor="#ffffff"
                  penColor="#000000"
                />
                {/* 안내 텍스트 */}
                <div className="absolute top-2 left-2 text-xs text-gray-400 pointer-events-none">
                  서명란
                </div>
              </div>

              <div className="flex items-center justify-between">
                <button
                  onClick={() => signatureCanvasRef.current?.clear()}
                  className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  disabled={submitting}
                >
                  🗑️ 지우기
                </button>
                <p className="text-xs text-gray-500">
                  * 제출 후에는 수정할 수 없습니다
                </p>
              </div>
            </div>

            <div className="p-6 bg-gray-50 rounded-b-lg flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowSignatureModal(false);
                  signatureCanvasRef.current?.clear();
                }}
                className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
                disabled={submitting}
              >
                취소
              </button>

              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {submitting ? (
                  <>
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                    제출 중...
                  </>
                ) : (
                  '✅ 서명하고 제출'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default EvaluationDetailPage;
