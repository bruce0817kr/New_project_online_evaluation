import { useEffect, useRef, useCallback } from 'react';

/**
 * 자동 저장 Hook (Debounce 적용)
 *
 * @param {*} data - 저장할 데이터 (변경되면 자동 저장 트리거)
 * @param {Function} saveFunction - 실제 저장 함수 (API 호출)
 * @param {number} delay - 디바운스 지연 시간 (ms)
 * @param {boolean} enabled - 자동 저장 활성화 여부
 *
 * @example
 * const handleSave = async (data) => {
 *   await evaluationService.updateEvaluation(id, data);
 * };
 *
 * useAutoSave(evaluation, handleSave, 3000);
 */
export const useAutoSave = (data, saveFunction, delay = 3000, enabled = true) => {
  const timeoutRef = useRef(null);
  const dataRef = useRef(data);
  const isMountedRef = useRef(false);

  useEffect(() => {
    // 첫 마운트 시에는 저장하지 않음
    if (!isMountedRef.current) {
      isMountedRef.current = true;
      dataRef.current = data;
      return;
    }

    // 자동 저장 비활성화 시
    if (!enabled) {
      return;
    }

    // 데이터가 변경되지 않았으면 저장하지 않음
    if (JSON.stringify(dataRef.current) === JSON.stringify(data)) {
      return;
    }

    // 이전 타이머 취소
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // 새 타이머 설정
    timeoutRef.current = setTimeout(async () => {
      try {
        console.log('⏰ Auto-saving...', new Date().toLocaleTimeString());
        await saveFunction(data);
        dataRef.current = data;
        console.log('✅ Auto-save successful');
      } catch (error) {
        console.error('❌ Auto-save failed:', error);
      }
    }, delay);

    // 클린업
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [data, saveFunction, delay, enabled]);

  // 즉시 저장 함수 반환
  const saveNow = useCallback(async () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    try {
      await saveFunction(data);
      dataRef.current = data;
      return { success: true };
    } catch (error) {
      console.error('Save failed:', error);
      return { success: false, error };
    }
  }, [data, saveFunction]);

  return { saveNow };
};

export default useAutoSave;
