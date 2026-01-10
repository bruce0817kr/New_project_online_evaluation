import api from './api';

/**
 * 프로젝트 관련 API 서비스
 */
export const projectService = {
  /**
   * 전체 프로젝트 목록 조회
   * @returns {Promise<Array>} 프로젝트 목록
   */
  getAllProjects: async () => {
    return await api.get('/projects');
  },

  /**
   * 프로젝트 상세 조회
   * @param {string} id - 프로젝트 ID
   * @returns {Promise<Object>} 프로젝트 상세 정보
   */
  getProjectById: async (id) => {
    return await api.get(`/projects/${id}`);
  },

  /**
   * 프로젝트 생성
   * @param {Object} data - { name, year, description, deadline }
   * @returns {Promise<Object>} 생성된 프로젝트
   */
  createProject: async (data) => {
    return await api.post('/projects', data);
  },

  /**
   * 프로젝트 수정
   * @param {string} id - 프로젝트 ID
   * @param {Object} data - 수정할 데이터
   * @returns {Promise<Object>} 수정된 프로젝트
   */
  updateProject: async (id, data) => {
    return await api.put(`/projects/${id}`, data);
  },

  /**
   * 프로젝트 삭제
   * @param {string} id - 프로젝트 ID
   * @returns {Promise<void>}
   */
  deleteProject: async (id) => {
    return await api.delete(`/projects/${id}`);
  },

  /**
   * 프로젝트에 참여 기업 추가
   * @param {string} projectId - 프로젝트 ID
   * @param {string} companyId - 기업 ID
   * @returns {Promise<Object>} 업데이트된 프로젝트
   */
  addCompanyToProject: async (projectId, companyId) => {
    return await api.post(`/projects/${projectId}/companies/${companyId}`);
  },

  /**
   * 프로젝트에서 참여 기업 제거
   * @param {string} projectId - 프로젝트 ID
   * @param {string} companyId - 기업 ID
   * @returns {Promise<void>}
   */
  removeCompanyFromProject: async (projectId, companyId) => {
    return await api.delete(`/projects/${projectId}/companies/${companyId}`);
  },

  /**
   * 프로젝트별 평가 결과 집계
   * @param {string} projectId - 프로젝트 ID
   * @returns {Promise<Object>} 집계 결과
   */
  getProjectResults: async (projectId) => {
    return await api.get(`/projects/${projectId}/results`);
  },
};

export default projectService;
