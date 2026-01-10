import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * 인증 상태 관리 Store (Zustand + LocalStorage Persist)
 */
export const useAuthStore = create(
  persist(
    (set, get) => ({
      // 상태
      user: null,
      token: null,
      isAuthenticated: false,
      loading: false,
      error: null,

      // 액션: 사용자 설정
      setUser: (user, token) => {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));

        set({
          user,
          token,
          isAuthenticated: true,
          error: null,
        });
      },

      // 액션: 로그아웃
      logout: () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');

        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        });
      },

      // 액션: 에러 설정
      setError: (error) => {
        set({ error });
      },

      // 액션: 에러 초기화
      clearError: () => {
        set({ error: null });
      },

      // 액션: 로딩 상태 설정
      setLoading: (loading) => {
        set({ loading });
      },

      // 헬퍼: 관리자 여부 확인
      isAdmin: () => {
        const { user } = get();
        return user?.role === 'admin';
      },

      // 헬퍼: 심사위원 여부 확인
      isEvaluator: () => {
        const { user } = get();
        return user?.role === 'evaluator';
      },
    }),
    {
      name: 'auth-storage', // LocalStorage 키 이름
      partialize: (state) => ({
        // LocalStorage에 저장할 상태만 선택
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useAuthStore;
