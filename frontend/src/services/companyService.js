import api from './api';

/**
 * 기업 관련 API 서비스
 */
export const companyService = {
  /**
   * 전체 기업 목록 조회
   * @param {Object} params - 쿼리 파라미터 { project_id?, search? }
   * @returns {Promise<Array>} 기업 목록
   */
  getAllCompanies: async (params = {}) => {
    return await api.get('/companies', { params });
  },

  /**
   * 기업 상세 조회
   * @param {string} id - 기업 ID
   * @returns {Promise<Object>} 기업 상세 정보
   */
  getCompanyById: async (id) => {
    return await api.get(`/companies/${id}`);
  },

  /**
   * 기업 생성
   * @param {Object} data - { name, business_number, ceo_name, address, phone, email }
   * @returns {Promise<Object>} 생성된 기업
   */
  createCompany: async (data) => {
    return await api.post('/companies', data);
  },

  /**
   * 기업 정보 수정
   * @param {string} id - 기업 ID
   * @param {Object} data - 수정할 데이터
   * @returns {Promise<Object>} 수정된 기업
   */
  updateCompany: async (id, data) => {
    return await api.put(`/companies/${id}`, data);
  },

  /**
   * 기업 삭제
   * @param {string} id - 기업 ID
   * @returns {Promise<void>}
   */
  deleteCompany: async (id) => {
    return await api.delete(`/companies/${id}`);
  },

  /**
   * OCR 파일 업로드 (사업자등록증)
   * @param {File} file - 업로드할 파일
   * @returns {Promise<Object>} OCR 추출 결과
   */
  uploadOCR: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    return await api.post('/companies/ocr/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  /**
   * 기업별 평가 목록 조회
   * @param {string} companyId - 기업 ID
   * @returns {Promise<Array>} 평가 목록
   */
  getCompanyEvaluations: async (companyId) => {
    return await api.get(`/companies/${companyId}/evaluations`);
  },

  /**
   * 프로젝트별 기업 목록 조회
   * @param {string} projectId - 프로젝트 ID
   * @returns {Promise<Array>} 기업 목록
   */
  getCompaniesByProject: async (projectId) => {
    return await api.get(`/projects/${projectId}/companies`);
  },

  /**
   * 기업 서류 업로드 (관리자)
   * @param {string} companyId - 기업 ID
   * @param {File} file - 업로드할 파일 (PDF/Word)
   * @returns {Promise<Object>} 업로드 결과
   */
  uploadDocument: async (companyId, file) => {
    const formData = new FormData();
    formData.append('file', file);

    return await api.post(`/companies/${companyId}/upload-document`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  /**
   * 기업 서류 다운로드
   * @param {string} companyId - 기업 ID
   * @returns {Promise<Blob>} 파일 Blob
   */
  downloadDocument: async (companyId) => {
    return await api.get(`/companies/${companyId}/document`, {
      responseType: 'blob',
    });
  },

  /**
   * 기업 서류 정보 조회
   * @param {string} companyId - 기업 ID
   * @returns {Promise<Object>} 서류 정보 { has_document, filename?, file_size?, file_type? }
   */
  getDocumentInfo: async (companyId) => {
    return await api.get(`/companies/${companyId}/document-info`);
  },

  /**
   * 기업 서류 URL 가져오기 (iframe용)
   * @param {string} companyId - 기업 ID
   * @returns {string} 서류 다운로드 URL
   */
  getDocumentUrl: (companyId) => {
    const token = localStorage.getItem('token');
    const baseURL = api.defaults.baseURL || '';
    return `${baseURL}/companies/${companyId}/document?token=${token}`;
  },
};

export default companyService;
