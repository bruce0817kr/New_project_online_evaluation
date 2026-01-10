import { useState, useCallback } from 'react';
import { useAuthStore } from '../stores/authStore';
import authService from '../services/authService';

/**
 * 인증 관련 커스텀 훅
 * 로그인, 로그아웃, 사용자 정보 관리
 */
export const useAuth = () => {
  const {
    user,
    token,
    isAuthenticated,
    setUser,
    logout: storeLogout,
    setError,
    clearError,
    isAdmin,
    isEvaluator,
  } = useAuthStore();

  const [loading, setLoading] = useState(false);
  const [error, setLocalError] = useState(null);

  /**
   * 로그인
   */
  const login = useCallback(async (username, password) => {
    try {
      setLoading(true);
      setLocalError(null);
      clearError();

      const response = await authService.login(username, password);
      const { access_token, user: userData } = response;

      // Store에 사용자 정보 저장
      setUser(userData, access_token);

      return { success: true };
    } catch (err) {
      const errorMessage = err.response?.data?.detail || '로그인에 실패했습니다';
      setLocalError(errorMessage);
      setError(errorMessage);

      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [setUser, setError, clearError]);

  /**
   * 로그아웃
   */
  const logout = useCallback(async () => {
    try {
      setLoading(true);
      await authService.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      storeLogout();
      setLoading(false);
    }
  }, [storeLogout]);

  /**
   * 현재 사용자 정보 새로고침
   */
  const refreshUser = useCallback(async () => {
    try {
      setLoading(true);
      const userData = await authService.getCurrentUser();
      setUser(userData, token);
      return userData;
    } catch (err) {
      console.error('Refresh user error:', err);
      // 토큰이 유효하지 않으면 로그아웃
      storeLogout();
      throw err;
    } finally {
      setLoading(false);
    }
  }, [setUser, token, storeLogout]);

  /**
   * 비밀번호 변경
   */
  const changePassword = useCallback(async (currentPassword, newPassword) => {
    try {
      setLoading(true);
      setLocalError(null);

      await authService.changePassword(currentPassword, newPassword);

      return { success: true };
    } catch (err) {
      const errorMessage = err.response?.data?.detail || '비밀번호 변경에 실패했습니다';
      setLocalError(errorMessage);

      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    // 상태
    user,
    token,
    isAuthenticated,
    loading,
    error,

    // 액션
    login,
    logout,
    refreshUser,
    changePassword,

    // 헬퍼
    isAdmin,
    isEvaluator,
  };
};

export default useAuth;
