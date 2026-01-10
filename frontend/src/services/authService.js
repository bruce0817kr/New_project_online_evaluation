import api from './api';

/**
 * 인증 관련 API 서비스
 */
export const authService = {
  /**
   * 로그인
   * @param {string} username - 사용자명
   * @param {string} password - 비밀번호
   * @returns {Promise} 로그인 응답 (토큰 + 사용자 정보)
   */
  login: async (username, password) => {
    // FastAPI는 OAuth2 형식 (application/x-www-form-urlencoded)을 요구
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    return response;
  },

  /**
   * 로그아웃
   * @returns {Promise}
   */
  logout: async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout API error:', error);
      // 로그아웃은 실패해도 로컬 데이터는 삭제
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  },

  /**
   * 현재 사용자 정보 조회
   * @returns {Promise} 사용자 정보
   */
  getCurrentUser: async () => {
    return await api.get('/auth/me');
  },

  /**
   * 회원가입 (관리자만 가능)
   * @param {Object} userData - 사용자 데이터
   * @returns {Promise}
   */
  register: async (userData) => {
    return await api.post('/auth/register', userData);
  },

  /**
   * 비밀번호 변경
   * @param {string} currentPassword - 현재 비밀번호
   * @param {string} newPassword - 새 비밀번호
   * @returns {Promise}
   */
  changePassword: async (currentPassword, newPassword) => {
    return await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },
};

export default authService;
