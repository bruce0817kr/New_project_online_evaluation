import { useState, useEffect, useRef } from 'react';

/**
 * Auto-save Hook
 * 데이터 변경 시 자동으로 저장 (Debounce 적용)
 */
export function useAutoSave(data, delay = 3000) {
  const [status, setStatus] = useState({
    saving: false,
    saved: false
  });
  const timeoutRef = useRef(null);

  useEffect(() => {
    // Clear previous timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Set saving status
    setStatus({ saving: true, saved: false });

    // Create new timeout
    timeoutRef.current = setTimeout(async () => {
      try {
        // TODO: Implement actual API call
        console.log('Auto-saving:', data);
        await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API call

        setStatus({ saving: false, saved: true });

        // Clear saved status after 2 seconds
        setTimeout(() => {
          setStatus({ saving: false, saved: false });
        }, 2000);
      } catch (error) {
        console.error('Auto-save failed:', error);
        setStatus({ saving: false, saved: false });
      }
    }, delay);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [data, delay]);

  return status;
}
