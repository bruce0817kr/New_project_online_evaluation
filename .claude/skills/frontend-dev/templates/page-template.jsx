// Template: 새 페이지 생성 시 사용
// 파일명: [PageName]Page.jsx

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { Spinner } from '../components/common/Spinner';
import { ErrorMessage } from '../components/common/ErrorMessage';

/**
 * [페이지 설명]
 *
 * @component
 * @example
 * <ExamplePage />
 */
export const ExamplePage = () => {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const { loading, error, execute: fetchData } = useApi(yourApiService.getData);

  // 초기 데이터 로드
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const result = await fetchData();
      setData(result);
    } catch (err) {
      console.error('Failed to load data:', err);
    }
  };

  // 핸들러 함수
  const handleAction = async () => {
    try {
      // API 호출
      await yourApiService.doSomething();
      // 성공 처리
      await loadData();
    } catch (err) {
      console.error('Action failed:', err);
    }
  };

  // 로딩 상태
  if (loading && !data) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner size="lg" />
      </div>
    );
  }

  // 에러 상태
  if (error && !data) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <ErrorMessage message={error} onRetry={loadData} />
      </div>
    );
  }

  // 메인 렌더링
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900">페이지 제목</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Content here */}
        <div className="bg-white rounded-lg shadow p-6">
          {data ? (
            <div>
              {/* 데이터 렌더링 */}
            </div>
          ) : (
            <p className="text-gray-500">데이터가 없습니다</p>
          )}
        </div>
      </main>
    </div>
  );
};

export default ExamplePage;
