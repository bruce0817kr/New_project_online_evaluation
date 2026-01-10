import React, { useState, useEffect } from 'react';
import projectService from '../../services/projectService';
import evaluationService from '../../services/evaluationService';

function EvaluationsPage() {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [evaluations, setEvaluations] = useState([]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      loadProjectEvaluations(selectedProject);
    }
  }, [selectedProject]);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const data = await projectService.getAllProjects();
      setProjects(data);
      if (data.length > 0) {
        setSelectedProject(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load projects:', err);
      setError(err.response?.data?.detail || '프로젝트 목록을 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const loadProjectEvaluations = async (projectId) => {
    try {
      setLoading(true);
      setError(null);

      const [evalData, resultsData] = await Promise.all([
        evaluationService.getEvaluationsByProject(projectId),
        projectService.getProjectResults(projectId),
      ]);

      setEvaluations(evalData);
      setResults(resultsData);
    } catch (err) {
      console.error('Failed to load evaluations:', err);
      setError(err.response?.data?.detail || '평가 정보를 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  if (loading && projects.length === 0) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className="p-8">
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-500">등록된 프로젝트가 없습니다</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">평가 관리</h1>
        <p className="text-gray-600 mt-2">평가 현황 및 결과를 확인합니다</p>
      </div>

      {/* 프로젝트 선택 */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          프로젝트 선택
        </label>
        <select
          value={selectedProject || ''}
          onChange={(e) => setSelectedProject(e.target.value)}
          className="w-full max-w-md px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {projects.map((project) => (
            <option key={project.id} value={project.id}>
              {project.name} ({project.year}년)
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
        </div>
      ) : (
        <>
          {/* 평가 통계 */}
          {results && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-600 mb-2">전체 평가</div>
                <div className="text-3xl font-bold text-gray-900">
                  {results.total_evaluations || 0}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-600 mb-2">제출 완료</div>
                <div className="text-3xl font-bold text-green-600">
                  {results.submitted_evaluations || 0}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-600 mb-2">진행 중</div>
                <div className="text-3xl font-bold text-blue-600">
                  {results.in_progress_evaluations || 0}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-600 mb-2">평균 점수</div>
                <div className="text-3xl font-bold text-purple-600">
                  {results.average_score?.toFixed(1) || 'N/A'}
                </div>
              </div>
            </div>
          )}

          {/* 기업별 평가 결과 */}
          {results?.company_results && results.company_results.length > 0 && (
            <div className="bg-white rounded-lg shadow mb-8">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold">기업별 평가 결과</h2>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        기업명
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                        기술성
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                        사업성
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                        경제성
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                        평균 점수
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                        평가 완료
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {results.company_results.map((company, index) => {
                      const avgScore =
                        (company.scores?.['기술성'] +
                          company.scores?.['사업성'] +
                          company.scores?.['경제성']) / 3 || 0;

                      return (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">
                              {company.company_name}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            <div className="text-sm text-gray-900">
                              {company.scores?.['기술성']?.toFixed(1) || '-'}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            <div className="text-sm text-gray-900">
                              {company.scores?.['사업성']?.toFixed(1) || '-'}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            <div className="text-sm text-gray-900">
                              {company.scores?.['경제성']?.toFixed(1) || '-'}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            <div className="text-sm font-semibold text-blue-600">
                              {avgScore.toFixed(1)}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            <span
                              className={`px-3 py-1 text-xs font-medium rounded-full ${
                                company.completed_evaluations === company.total_evaluations
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-yellow-100 text-yellow-800'
                              }`}
                            >
                              {company.completed_evaluations} / {company.total_evaluations}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 평가 목록 */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold">평가 목록</h2>
            </div>

            {evaluations.length === 0 ? (
              <div className="p-12 text-center text-gray-500">
                평가가 없습니다
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        기업명
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        심사위원
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                        상태
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                        점수
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        제출일
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {evaluations.map((evaluation) => {
                      const scores = evaluation.scores || {};
                      const avgScore = Object.keys(scores).length > 0
                        ? Object.values(scores).reduce((a, b) => a + b, 0) / Object.keys(scores).length
                        : null;

                      return (
                        <tr key={evaluation.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">
                              {evaluation.company_name}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-600">
                              {evaluation.evaluator_name}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            <span
                              className={`px-3 py-1 text-xs font-medium rounded-full ${
                                evaluation.is_submitted
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-yellow-100 text-yellow-800'
                              }`}
                            >
                              {evaluation.is_submitted ? '제출완료' : '진행중'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            <div className="text-sm font-semibold text-gray-900">
                              {avgScore !== null ? avgScore.toFixed(1) : '-'}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-600">
                              {evaluation.submitted_at
                                ? new Date(evaluation.submitted_at).toLocaleString('ko-KR')
                                : '-'}
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default EvaluationsPage;
