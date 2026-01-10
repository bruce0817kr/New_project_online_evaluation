import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import projectService from '../../services/projectService';
import useAdminStore from '../../stores/adminStore';

function ProjectsPage() {
  return (
    <Routes>
      <Route index element={<ProjectsList />} />
      <Route path=":projectId" element={<ProjectDetail />} />
    </Routes>
  );
}

/**
 * 프로젝트 목록 페이지
 */
function ProjectsList() {
  const navigate = useNavigate();
  const { projects, setProjects, addProject, removeProject } = useAdminStore();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    year: new Date().getFullYear(),
    description: '',
    deadline: '',
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await projectService.getAllProjects();
      setProjects(data);
    } catch (err) {
      console.error('Failed to load projects:', err);
      setError(err.response?.data?.detail || '프로젝트 목록을 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      alert('사업명을 입력하세요');
      return;
    }
    if (!formData.deadline) {
      alert('마감일을 선택하세요');
      return;
    }

    try {
      setSubmitting(true);
      const newProject = await projectService.createProject(formData);
      addProject(newProject);
      setShowModal(false);
      setFormData({ name: '', year: new Date().getFullYear(), description: '', deadline: '' });
      alert('사업이 생성되었습니다');
    } catch (err) {
      console.error('Failed to create project:', err);
      alert(err.response?.data?.detail || '사업 생성에 실패했습니다');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`"${name}" 사업을 삭제하시겠습니까?`)) {
      return;
    }

    try {
      await projectService.deleteProject(id);
      removeProject(id);
      alert('사업이 삭제되었습니다');
    } catch (err) {
      console.error('Failed to delete project:', err);
      alert(err.response?.data?.detail || '사업 삭제에 실패했습니다');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">사업 관리</h1>
          <p className="text-gray-600 mt-2">평가 사업을 관리합니다</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          사업 추가
        </button>
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">{error}</p>
          <button
            onClick={loadProjects}
            className="mt-2 text-sm text-red-700 hover:text-red-900 underline"
          >
            다시 시도
          </button>
        </div>
      )}

      {/* 프로젝트 목록 */}
      {projects.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-500 mb-4">등록된 사업이 없습니다</p>
          <button
            onClick={() => setShowModal(true)}
            className="text-blue-600 hover:text-blue-700"
          >
            첫 사업 추가하기 →
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {projects.map((project) => (
            <div
              key={project.id}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow"
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      {project.name}
                    </h3>
                    <p className="text-sm text-gray-600 mb-3">{project.description}</p>

                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>🗓️ {project.year}년</span>
                      <span>
                        📅 마감: {new Date(project.deadline).toLocaleDateString('ko-KR')}
                      </span>
                    </div>
                  </div>

                  <span
                    className={`px-3 py-1 text-xs font-medium rounded-full ${
                      new Date(project.deadline) > new Date()
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {new Date(project.deadline) > new Date() ? '진행중' : '마감'}
                  </span>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={() => navigate(`/admin/projects/${project.id}`)}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    상세보기
                  </button>
                  <button
                    onClick={() => handleDelete(project.id, project.name)}
                    className="px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
                  >
                    삭제
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 생성 모달 */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold">새 사업 추가</h2>
            </div>

            <form onSubmit={handleCreate} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  사업명 *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="예: 2026년 기술혁신 지원사업"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  년도 *
                </label>
                <input
                  type="number"
                  value={formData.year}
                  onChange={(e) => setFormData({ ...formData, year: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="2020"
                  max="2030"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  설명
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={3}
                  placeholder="사업 설명을 입력하세요"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  마감일 *
                </label>
                <input
                  type="date"
                  value={formData.deadline}
                  onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
                  disabled={submitting}
                >
                  취소
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                  disabled={submitting}
                >
                  {submitting ? '생성 중...' : '생성'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * 프로젝트 상세 페이지
 */
function ProjectDetail() {
  const navigate = useNavigate();
  // TODO: Implement project detail view with evaluations and companies

  return (
    <div className="p-8">
      <button
        onClick={() => navigate('/admin/projects')}
        className="mb-6 flex items-center gap-2 text-gray-600 hover:text-gray-900"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        목록으로 돌아가기
      </button>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">프로젝트 상세 (개발 예정)</h2>
        <p className="text-gray-600">
          이 페이지에서는 프로젝트별 참여 기업, 평가 현황, 결과 집계 등을 확인할 수 있습니다.
        </p>
      </div>
    </div>
  );
}

export default ProjectsPage;
