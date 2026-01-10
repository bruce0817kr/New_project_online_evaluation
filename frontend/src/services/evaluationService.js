import api from './api';

/**
 * 평가 관련 API 서비스
 */
export const evaluationService = {
  /**
   * 내 평가 목록 조회
   * @param {string} status - 'in_progress' | 'submitted' | null
   * @param {string} projectId - 프로젝트 ID 필터 (선택)
   * @returns {Promise<Array>} 평가 목록
   */
  getMyEvaluations: async (status = null, projectId = null) => {
    const params = {};
    if (status) {
      params.status = status;
    }
    if (projectId) {
      params.project_id = projectId;
    }
    return await api.get('/evaluations/my', { params });
  },

  /**
   * 평가 상세 조회
   * @param {string} id - 평가 ID
   * @returns {Promise<Object>} 평가 상세 정보
   */
  getEvaluationById: async (id) => {
    return await api.get(`/evaluations/${id}`);
  },

  /**
   * 평가 저장 (임시 저장)
   * @param {string} id - 평가 ID
   * @param {Object} data - 평가 데이터 { scores, comments }
   * @returns {Promise<Object>} 업데이트된 평가
   */
  updateEvaluation: async (id, data) => {
    return await api.put(`/evaluations/${id}`, data);
  },

  /**
   * 평가 제출 (최종 제출, 이후 수정 불가)
   * @param {string} id - 평가 ID
   * @param {Object} data - { signature_data?: string }
   * @returns {Promise<Object>} 제출 결과
   */
  submitEvaluation: async (id, data = {}) => {
    return await api.post(`/evaluations/${id}/submit`, data);
  },

  /**
   * 프로젝트별 평가 목록 조회 (관리자)
   * @param {string} projectId - 프로젝트 ID
   * @returns {Promise<Array>} 평가 목록
   */
  getEvaluationsByProject: async (projectId) => {
    return await api.get(`/evaluations/project/${projectId}`);
  },

  /**
   * 기업별 평가 목록 조회 (관리자)
   * @param {string} companyId - 기업 ID
   * @returns {Promise<Array>} 평가 목록
   */
  getEvaluationsByCompany: async (companyId) => {
    return await api.get(`/evaluations/company/${companyId}`);
  },

  /**
   * 평가 생성 (관리자)
   * @param {Object} data - { project_id, company_id, evaluator_id }
   * @returns {Promise<Object>} 생성된 평가
   */
  createEvaluation: async (data) => {
    return await api.post('/evaluations', data);
  },
};

export default evaluationService;
