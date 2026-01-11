import api from './api';

/**
 * 평가 템플릿 관련 API 서비스
 */
export const templateService = {
  /**
   * 템플릿 목록 조회
   * @param {boolean} activeOnly - 활성 템플릿만 조회
   * @returns {Promise<Array>} 템플릿 목록
   */
  getAllTemplates: async (activeOnly = true) => {
    return await api.get('/templates', { params: { active_only: activeOnly } });
  },

  /**
   * 템플릿 상세 조회
   * @param {string} id - 템플릿 ID
   * @returns {Promise<Object>} 템플릿 상세 정보
   */
  getTemplateById: async (id) => {
    return await api.get(`/templates/${id}`);
  },

  /**
   * 템플릿 생성
   * @param {Object} data - { name, description, total_score, sections, is_default }
   * @returns {Promise<Object>} 생성된 템플릿
   */
  createTemplate: async (data) => {
    return await api.post('/templates', data);
  },

  /**
   * 템플릿 수정
   * @param {string} id - 템플릿 ID
   * @param {Object} data - 수정할 데이터
   * @returns {Promise<Object>} 수정된 템플릿
   */
  updateTemplate: async (id, data) => {
    return await api.put(`/templates/${id}`, data);
  },

  /**
   * 템플릿 삭제
   * @param {string} id - 템플릿 ID
   * @returns {Promise<void>}
   */
  deleteTemplate: async (id) => {
    return await api.delete(`/templates/${id}`);
  },

  /**
   * 템플릿 활성화/비활성화
   * @param {string} id - 템플릿 ID
   * @param {boolean} isActive - 활성화 여부
   * @returns {Promise<Object>} 업데이트된 템플릿
   */
  toggleTemplateActive: async (id, isActive) => {
    return await api.patch(`/templates/${id}/toggle-active`, { is_active: isActive });
  },

  /**
   * 기본 템플릿 설정
   * @param {string} id - 템플릿 ID
   * @returns {Promise<Object>} 업데이트된 템플릿
   */
  setDefaultTemplate: async (id) => {
    return await api.post(`/templates/${id}/set-default`);
  },

  /**
   * 기본 R&D 템플릿 생성
   * @returns {Promise<Object>} 생성된 템플릿
   */
  createDefaultTemplate: async () => {
    return await api.post('/templates/create-default');
  },
};

export default templateService;
