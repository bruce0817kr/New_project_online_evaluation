import api from './api';

/**
 * 관리자 전용 API 서비스
 */
export const adminService = {
  /**
   * 대시보드 통계 조회
   * @returns {Promise<Object>} 통계 데이터
   */
  getDashboardStats: async () => {
    return await api.get('/admin/stats');
  },

  /**
   * 평가 생성 (수동 배정)
   * @param {Object} data - { project_id, company_id, evaluator_id }
   * @returns {Promise<Object>} 생성된 평가
   */
  createEvaluation: async (data) => {
    return await api.post('/evaluations', data);
  },

  /**
   * 평가 일괄 생성
   * @param {Object} data - { project_id, company_ids[], evaluator_ids[] }
   * @returns {Promise<Object>} 생성 결과
   */
  createBulkEvaluations: async (data) => {
    return await api.post('/admin/evaluations/bulk', data);
  },

  /**
   * 사용자 목록 조회
   * @param {Object} params - { role?, search? }
   * @returns {Promise<Array>} 사용자 목록
   */
  getUsers: async (params = {}) => {
    return await api.get('/admin/users', { params });
  },

  /**
   * 사용자 생성
   * @param {Object} data - { username, full_name, email, role, password }
   * @returns {Promise<Object>} 생성된 사용자
   */
  createUser: async (data) => {
    return await api.post('/admin/users', data);
  },

  /**
   * 사용자 수정
   * @param {string} id - 사용자 ID
   * @param {Object} data - 수정할 데이터
   * @returns {Promise<Object>} 수정된 사용자
   */
  updateUser: async (id, data) => {
    return await api.put(`/admin/users/${id}`, data);
  },

  /**
   * 사용자 삭제
   * @param {string} id - 사용자 ID
   * @returns {Promise<void>}
   */
  deleteUser: async (id) => {
    return await api.delete(`/admin/users/${id}`);
  },

  /**
   * 감사 로그 조회
   * @param {Object} params - { user_id?, action?, start_date?, end_date?, limit?, offset? }
   * @returns {Promise<Object>} { items: [], total: number }
   */
  getAuditLogs: async (params = {}) => {
    return await api.get('/admin/audit-logs', { params });
  },

  /**
   * 평가 배정 목록 조회 (프로젝트별)
   * @param {string} projectId - 프로젝트 ID
   * @returns {Promise<Array>} 평가 배정 목록
   */
  getEvaluationAssignments: async (projectId) => {
    return await api.get(`/admin/projects/${projectId}/assignments`);
  },

  /**
   * 평가 배정 생성
   * @param {Object} data - { project_id, company_id, evaluator_id, order }
   * @returns {Promise<Object>} 생성된 평가
   */
  createAssignment: async (data) => {
    return await api.post('/admin/assignments', data);
  },

  /**
   * 평가 배정 삭제
   * @param {string} evaluationId - 평가 ID
   * @returns {Promise<void>}
   */
  deleteAssignment: async (evaluationId) => {
    return await api.delete(`/evaluations/${evaluationId}`);
  },

  /**
   * 평가 순서 변경
   * @param {string} evaluatorId - 심사위원 ID
   * @param {Array} evaluationOrders - [{ evaluation_id, order }, ...]
   * @returns {Promise<Object>} 업데이트 결과
   */
  updateEvaluationOrders: async (evaluatorId, evaluationOrders) => {
    return await api.put(`/admin/evaluators/${evaluatorId}/evaluation-orders`, {
      orders: evaluationOrders,
    });
  },

  /**
   * 평가 일괄 배정 (매트릭스)
   * @param {Object} data - { project_id, assignments: [{ company_id, evaluator_ids[] }] }
   * @returns {Promise<Object>} 생성 결과
   */
  bulkAssignEvaluations: async (data) => {
    return await api.post('/admin/assignments/bulk', data);
  },
};

export default adminService;
