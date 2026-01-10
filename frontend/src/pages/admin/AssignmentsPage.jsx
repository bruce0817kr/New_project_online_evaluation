import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import adminService from '../../services/adminService';
import projectService from '../../services/projectService';
import companyService from '../../services/companyService';
import { useToast } from '../../contexts/ToastContext';
import { TableSkeleton } from '../../components/common/Skeleton';

/**
 * 평가 배정 관리 페이지
 * - 프로젝트별 평가 배정
 * - 심사위원별 평가 순서 조정 (드래그 앤 드롭)
 * - 일괄 배정
 */
function AssignmentsPage() {
  const navigate = useNavigate();
  const toast = useToast();

  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [companies, setCompanies] = useState([]);
  const [evaluators, setEvaluators] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [showBulkModal, setShowBulkModal] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      loadProjectAssignments(selectedProject.id);
    }
  }, [selectedProject]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [projectsData, evaluatorsData] = await Promise.all([
        projectService.getAllProjects(),
        adminService.getUsers({ role: 'evaluator' }),
      ]);

      setProjects(projectsData);
      setEvaluators(evaluatorsData);

      if (projectsData.length > 0) {
        setSelectedProject(projectsData[0]);
      }
    } catch (err) {
      console.error('Failed to load initial data:', err);
      toast.error('데이터를 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const loadProjectAssignments = async (projectId) => {
    try {
      setLoading(true);
      const [assignmentsData, companiesData] = await Promise.all([
        adminService.getEvaluationAssignments(projectId),
        companyService.getCompaniesByProject(projectId),
      ]);

      setAssignments(assignmentsData);
      setCompanies(companiesData);
    } catch (err) {
      console.error('Failed to load assignments:', err);
      toast.error('배정 정보를 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  // 심사위원별로 배정 그룹화
  const groupedAssignments = evaluators.reduce((acc, evaluator) => {
    acc[evaluator.id] = assignments
      .filter((a) => a.evaluator_id === evaluator.id)
      .sort((a, b) => (a.order || 0) - (b.order || 0));
    return acc;
  }, {});

  if (loading && projects.length === 0) {
    return (
      <div className="p-8">
        <TableSkeleton rows={5} columns={4} />
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className="p-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <p className="text-yellow-800">등록된 프로젝트가 없습니다.</p>
          <button
            onClick={() => navigate('/admin/projects')}
            className="mt-3 text-yellow-900 hover:text-yellow-700 underline"
          >
            프로젝트 관리 페이지로 이동 →
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">평가 배정 관리</h1>
          <p className="text-gray-600 mt-2">
            심사위원별로 평가할 기업을 배정하고 순서를 조정합니다
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowAssignModal(true)}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            평가 배정
          </button>
          <button
            onClick={() => setShowBulkModal(true)}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
            일괄 배정
          </button>
        </div>
      </div>

      {/* 프로젝트 선택 */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          프로젝트 선택
        </label>
        <select
          value={selectedProject?.id || ''}
          onChange={(e) => {
            const project = projects.find((p) => p.id === e.target.value);
            setSelectedProject(project);
          }}
          className="w-full max-w-md px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {projects.map((project) => (
            <option key={project.id} value={project.id}>
              {project.name} ({project.year}년)
            </option>
          ))}
        </select>
      </div>

      {/* 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-2">전체 기업</div>
          <div className="text-3xl font-bold text-gray-900">{companies.length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-2">심사위원</div>
          <div className="text-3xl font-bold text-blue-600">{evaluators.length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-2">총 배정</div>
          <div className="text-3xl font-bold text-green-600">{assignments.length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-2">평균 배정</div>
          <div className="text-3xl font-bold text-purple-600">
            {evaluators.length > 0 ? (assignments.length / evaluators.length).toFixed(1) : 0}
          </div>
        </div>
      </div>

      {/* 심사위원별 배정 목록 */}
      {loading ? (
        <TableSkeleton rows={5} columns={3} />
      ) : (
        <div className="space-y-6">
          {evaluators.map((evaluator) => (
            <EvaluatorAssignmentCard
              key={evaluator.id}
              evaluator={evaluator}
              assignments={groupedAssignments[evaluator.id] || []}
              onReorder={(newAssignments) => handleReorder(evaluator.id, newAssignments)}
              onDelete={(assignmentId) => handleDeleteAssignment(assignmentId)}
              toast={toast}
            />
          ))}

          {evaluators.length === 0 && (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <p className="text-gray-500">등록된 심사위원이 없습니다</p>
              <button
                onClick={() => navigate('/admin/users')}
                className="mt-3 text-blue-600 hover:text-blue-700 underline"
              >
                사용자 관리 페이지로 이동 →
              </button>
            </div>
          )}
        </div>
      )}

      {/* 개별 배정 모달 */}
      {showAssignModal && (
        <AssignModal
          project={selectedProject}
          companies={companies}
          evaluators={evaluators}
          existingAssignments={assignments}
          onClose={() => setShowAssignModal(false)}
          onSuccess={() => {
            setShowAssignModal(false);
            loadProjectAssignments(selectedProject.id);
            toast.success('평가가 배정되었습니다');
          }}
          toast={toast}
        />
      )}

      {/* 일괄 배정 모달 */}
      {showBulkModal && (
        <BulkAssignModal
          project={selectedProject}
          companies={companies}
          evaluators={evaluators}
          onClose={() => setShowBulkModal(false)}
          onSuccess={() => {
            setShowBulkModal(false);
            loadProjectAssignments(selectedProject.id);
            toast.success('일괄 배정이 완료되었습니다');
          }}
          toast={toast}
        />
      )}
    </div>
  );

  async function handleReorder(evaluatorId, newAssignments) {
    try {
      const orders = newAssignments.map((assignment, index) => ({
        evaluation_id: assignment.id,
        order: index + 1,
      }));

      await adminService.updateEvaluationOrders(evaluatorId, orders);
      setAssignments((prev) =>
        prev.map((a) => {
          const newOrder = orders.find((o) => o.evaluation_id === a.id);
          return newOrder ? { ...a, order: newOrder.order } : a;
        })
      );
      toast.success('평가 순서가 변경되었습니다');
    } catch (err) {
      console.error('Failed to reorder:', err);
      toast.error('순서 변경에 실패했습니다');
    }
  }

  async function handleDeleteAssignment(assignmentId) {
    if (!window.confirm('이 배정을 삭제하시겠습니까?')) return;

    try {
      await adminService.deleteAssignment(assignmentId);
      setAssignments((prev) => prev.filter((a) => a.id !== assignmentId));
      toast.success('배정이 삭제되었습니다');
    } catch (err) {
      console.error('Failed to delete:', err);
      toast.error('배정 삭제에 실패했습니다');
    }
  }
}

/**
 * 심사위원별 배정 카드 (드래그 앤 드롭)
 */
function EvaluatorAssignmentCard({ evaluator, assignments, onReorder, onDelete, toast }) {
  const [draggedIndex, setDraggedIndex] = useState(null);
  const [items, setItems] = useState(assignments);

  useEffect(() => {
    setItems(assignments);
  }, [assignments]);

  const handleDragStart = (index) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e, index) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === index) return;

    const newItems = [...items];
    const draggedItem = newItems[draggedIndex];
    newItems.splice(draggedIndex, 1);
    newItems.splice(index, 0, draggedItem);

    setItems(newItems);
    setDraggedIndex(index);
  };

  const handleDragEnd = () => {
    if (draggedIndex !== null) {
      onReorder(items);
    }
    setDraggedIndex(null);
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{evaluator.full_name}</h3>
          <p className="text-sm text-gray-600">
            {evaluator.email} • {items.length}개 평가 배정
          </p>
        </div>
        <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
          심사위원
        </span>
      </div>

      {items.length === 0 ? (
        <div className="p-12 text-center text-gray-500">
          배정된 평가가 없습니다
        </div>
      ) : (
        <div className="divide-y divide-gray-200">
          {items.map((assignment, index) => (
            <div
              key={assignment.id}
              draggable
              onDragStart={() => handleDragStart(index)}
              onDragOver={(e) => handleDragOver(e, index)}
              onDragEnd={handleDragEnd}
              className={`p-4 flex items-center gap-4 hover:bg-gray-50 cursor-move transition-colors ${
                draggedIndex === index ? 'opacity-50' : ''
              }`}
            >
              {/* Drag Handle */}
              <div className="text-gray-400">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8h16M4 16h16" />
                </svg>
              </div>

              {/* Order Number */}
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-sm font-bold text-blue-600">{index + 1}</span>
              </div>

              {/* Company Info */}
              <div className="flex-1">
                <div className="font-medium text-gray-900">{assignment.company_name}</div>
                <div className="text-sm text-gray-600">
                  {assignment.company_business_number || '사업자번호 미등록'}
                </div>
              </div>

              {/* Status Badge */}
              <span
                className={`px-3 py-1 text-xs font-medium rounded-full ${
                  assignment.is_submitted
                    ? 'bg-green-100 text-green-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}
              >
                {assignment.is_submitted ? '제출완료' : '미제출'}
              </span>

              {/* Delete Button */}
              <button
                onClick={() => onDelete(assignment.id)}
                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="배정 삭제"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="p-4 bg-gray-50 text-xs text-gray-600 text-center">
        💡 드래그하여 평가 순서를 변경할 수 있습니다
      </div>
    </div>
  );
}

/**
 * 개별 배정 모달
 */
function AssignModal({ project, companies, evaluators, existingAssignments, onClose, onSuccess, toast }) {
  const [selectedCompany, setSelectedCompany] = useState('');
  const [selectedEvaluator, setSelectedEvaluator] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!selectedCompany || !selectedEvaluator) {
      toast.warning('기업과 심사위원을 선택하세요');
      return;
    }

    // 중복 체크
    const isDuplicate = existingAssignments.some(
      (a) => a.company_id === selectedCompany && a.evaluator_id === selectedEvaluator
    );

    if (isDuplicate) {
      toast.error('이미 배정된 조합입니다');
      return;
    }

    try {
      setSubmitting(true);
      await adminService.createAssignment({
        project_id: project.id,
        company_id: selectedCompany,
        evaluator_id: selectedEvaluator,
      });
      onSuccess();
    } catch (err) {
      console.error('Failed to create assignment:', err);
      toast.error(err.response?.data?.detail || '배정 생성에 실패했습니다');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold">평가 배정</h2>
          <p className="text-sm text-gray-600 mt-1">{project.name}</p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              평가 대상 기업 *
            </label>
            <select
              value={selectedCompany}
              onChange={(e) => setSelectedCompany(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value="">선택하세요</option>
              {companies.map((company) => (
                <option key={company.id} value={company.id}>
                  {company.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              심사위원 *
            </label>
            <select
              value={selectedEvaluator}
              onChange={(e) => setSelectedEvaluator(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value="">선택하세요</option>
              {evaluators.map((evaluator) => (
                <option key={evaluator.id} value={evaluator.id}>
                  {evaluator.full_name} ({evaluator.username})
                </option>
              ))}
            </select>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
              disabled={submitting}
            >
              취소
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              disabled={submitting}
            >
              {submitting ? '배정 중...' : '배정'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

/**
 * 일괄 배정 모달 (매트릭스)
 */
function BulkAssignModal({ project, companies, evaluators, onClose, onSuccess, toast }) {
  const [matrix, setMatrix] = useState({});
  const [submitting, setSubmitting] = useState(false);

  const toggleAssignment = (companyId, evaluatorId) => {
    setMatrix((prev) => {
      const key = `${companyId}_${evaluatorId}`;
      const newMatrix = { ...prev };
      if (newMatrix[key]) {
        delete newMatrix[key];
      } else {
        newMatrix[key] = true;
      }
      return newMatrix;
    });
  };

  const handleSubmit = async () => {
    const assignments = [];
    Object.keys(matrix).forEach((key) => {
      const [companyId, evaluatorId] = key.split('_');
      assignments.push({ company_id: companyId, evaluator_id: evaluatorId });
    });

    if (assignments.length === 0) {
      toast.warning('최소 1개 이상 선택하세요');
      return;
    }

    try {
      setSubmitting(true);
      await adminService.bulkAssignEvaluations({
        project_id: project.id,
        assignments,
      });
      onSuccess();
    } catch (err) {
      console.error('Failed to bulk assign:', err);
      toast.error('일괄 배정에 실패했습니다');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold">일괄 배정</h2>
          <p className="text-sm text-gray-600 mt-1">
            체크박스를 선택하여 여러 평가를 한 번에 배정합니다
          </p>
        </div>

        <div className="flex-1 overflow-auto p-6">
          <table className="min-w-full border-collapse">
            <thead>
              <tr>
                <th className="border border-gray-300 p-3 bg-gray-50 text-left sticky top-0">
                  기업 \ 심사위원
                </th>
                {evaluators.map((evaluator) => (
                  <th
                    key={evaluator.id}
                    className="border border-gray-300 p-3 bg-gray-50 text-center sticky top-0"
                  >
                    <div className="font-medium">{evaluator.full_name}</div>
                    <div className="text-xs text-gray-600">{evaluator.username}</div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {companies.map((company) => (
                <tr key={company.id} className="hover:bg-gray-50">
                  <td className="border border-gray-300 p-3 font-medium">{company.name}</td>
                  {evaluators.map((evaluator) => {
                    const key = `${company.id}_${evaluator.id}`;
                    return (
                      <td key={evaluator.id} className="border border-gray-300 p-3 text-center">
                        <input
                          type="checkbox"
                          checked={!!matrix[key]}
                          onChange={() => toggleAssignment(company.id, evaluator.id)}
                          className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                        />
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="p-6 border-t border-gray-200 flex items-center justify-between">
          <div className="text-sm text-gray-600">
            선택된 배정: <span className="font-bold">{Object.keys(matrix).length}개</span>
          </div>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
              disabled={submitting}
            >
              취소
            </button>
            <button
              onClick={handleSubmit}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              disabled={submitting}
            >
              {submitting ? '배정 중...' : '일괄 배정'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AssignmentsPage;
