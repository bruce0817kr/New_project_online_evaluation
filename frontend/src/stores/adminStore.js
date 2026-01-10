import { create } from 'zustand';

/**
 * 관리자 전용 상태 관리 스토어
 */
export const useAdminStore = create((set, get) => ({
  // 프로젝트 관련
  projects: [],
  currentProject: null,

  // 기업 관련
  companies: [],
  currentCompany: null,

  // 사용자 관련
  users: [],
  currentUser: null,

  // 통계 데이터
  stats: null,

  // OCR 결과
  ocrResult: null,

  // UI 상태
  loading: false,
  error: null,

  // 프로젝트 액션
  setProjects: (projects) => set({ projects }),
  setCurrentProject: (project) => set({ currentProject: project }),
  addProject: (project) => set((state) => ({ projects: [...state.projects, project] })),
  updateProjectInList: (id, updatedData) => set((state) => ({
    projects: state.projects.map((p) => p.id === id ? { ...p, ...updatedData } : p),
  })),
  removeProject: (id) => set((state) => ({
    projects: state.projects.filter((p) => p.id !== id),
  })),

  // 기업 액션
  setCompanies: (companies) => set({ companies }),
  setCurrentCompany: (company) => set({ currentCompany: company }),
  addCompany: (company) => set((state) => ({ companies: [...state.companies, company] })),
  updateCompanyInList: (id, updatedData) => set((state) => ({
    companies: state.companies.map((c) => c.id === id ? { ...c, ...updatedData } : c),
  })),
  removeCompany: (id) => set((state) => ({
    companies: state.companies.filter((c) => c.id !== id),
  })),

  // OCR 액션
  setOcrResult: (result) => set({ ocrResult: result }),
  clearOcrResult: () => set({ ocrResult: null }),

  // 사용자 액션
  setUsers: (users) => set({ users }),
  setCurrentUser: (user) => set({ currentUser: user }),
  addUser: (user) => set((state) => ({ users: [...state.users, user] })),
  updateUserInList: (id, updatedData) => set((state) => ({
    users: state.users.map((u) => u.id === id ? { ...u, ...updatedData } : u),
  })),
  removeUser: (id) => set((state) => ({
    users: state.users.filter((u) => u.id !== id),
  })),

  // 통계 액션
  setStats: (stats) => set({ stats }),

  // UI 상태 액션
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),

  // 초기화
  reset: () => set({
    projects: [],
    currentProject: null,
    companies: [],
    currentCompany: null,
    users: [],
    currentUser: null,
    stats: null,
    ocrResult: null,
    loading: false,
    error: null,
  }),
}));

export default useAdminStore;
