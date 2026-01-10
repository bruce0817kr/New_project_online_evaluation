import { create } from 'zustand';

/**
 * 평가 상태 관리 Store (Zustand)
 */
export const useEvaluationStore = create((set, get) => ({
  // 상태
  evaluations: [], // 내 평가 목록
  currentEvaluation: null, // 현재 작업 중인 평가
  isDirty: false, // 변경사항이 있는지 여부
  lastSaved: null, // 마지막 저장 시간
  loading: false,
  error: null,

  // 액션: 평가 목록 설정
  setEvaluations: (evaluations) => {
    set({ evaluations });
  },

  // 액션: 현재 평가 설정
  setCurrentEvaluation: (evaluation) => {
    set({
      currentEvaluation: evaluation,
      isDirty: false,
      lastSaved: evaluation?.updated_at ? new Date(evaluation.updated_at) : null,
    });
  },

  // 액션: 평가 데이터 업데이트 (로컬 상태만)
  updateEvaluationData: (data) => {
    const { currentEvaluation } = get();

    if (!currentEvaluation) return;

    set({
      currentEvaluation: {
        ...currentEvaluation,
        ...data,
      },
      isDirty: true,
    });
  },

  // 액션: 점수 업데이트
  updateScore: (criteriaName, value) => {
    const { currentEvaluation } = get();

    if (!currentEvaluation) return;

    const newScores = {
      ...(currentEvaluation.scores || {}),
      [criteriaName]: parseFloat(value),
    };

    set({
      currentEvaluation: {
        ...currentEvaluation,
        scores: newScores,
      },
      isDirty: true,
    });
  },

  // 액션: 코멘트 업데이트
  updateComments: (comments) => {
    const { currentEvaluation } = get();

    if (!currentEvaluation) return;

    set({
      currentEvaluation: {
        ...currentEvaluation,
        comments,
      },
      isDirty: true,
    });
  },

  // 액션: 저장 완료 표시
  markAsSaved: () => {
    set({
      isDirty: false,
      lastSaved: new Date(),
    });
  },

  // 액션: 에러 설정
  setError: (error) => {
    set({ error });
  },

  // 액션: 로딩 상태 설정
  setLoading: (loading) => {
    set({ loading });
  },

  // 액션: 초기화
  reset: () => {
    set({
      evaluations: [],
      currentEvaluation: null,
      isDirty: false,
      lastSaved: null,
      loading: false,
      error: null,
    });
  },

  // 헬퍼: 제출 여부 확인
  isSubmitted: () => {
    const { currentEvaluation } = get();
    return currentEvaluation?.is_submitted === true;
  },

  // 헬퍼: 모든 점수가 입력되었는지 확인
  isScoresComplete: () => {
    const { currentEvaluation } = get();

    if (!currentEvaluation || !currentEvaluation.scores) {
      return false;
    }

    const scores = currentEvaluation.scores;
    const scoreValues = Object.values(scores);

    // 모든 점수가 0-100 사이의 숫자인지 확인
    return scoreValues.every(
      (score) => typeof score === 'number' && score >= 0 && score <= 100
    );
  },
}));

export default useEvaluationStore;
