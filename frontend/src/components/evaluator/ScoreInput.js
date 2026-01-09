import React, { useEffect, useRef } from 'react';
import { useAutoSave } from '../../hooks/useAutoSave';

/**
 * 점수 입력 컴포넌트
 * Auto-save 기능 포함
 */
function ScoreInput({ scores, onScoreChange }) {
  const autoSaveStatus = useAutoSave(scores, 3000); // 3초 debounce

  const handleScoreChange = (itemName, value) => {
    const numValue = parseFloat(value) || 0;
    onScoreChange({
      ...scores,
      [itemName]: numValue
    });
  };

  return (
    <div className="p-6">
      <div className="mb-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold">평가 항목</h2>
        {autoSaveStatus.saving && (
          <span className="text-sm text-gray-500">저장 중...</span>
        )}
        {autoSaveStatus.saved && (
          <span className="text-sm text-green-600">✓ 저장됨</span>
        )}
      </div>

      <div className="space-y-6">
        {/* 평가 항목 예시 */}
        <div className="bg-white p-4 rounded-lg shadow">
          <label className="block text-sm font-semibold mb-2">
            항목 1: 기술 혁신성 (0-100점)
          </label>
          <input
            type="number"
            min="0"
            max="100"
            value={scores['항목1'] || ''}
            onChange={(e) => handleScoreChange('항목1', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <label className="block text-sm font-semibold mb-2">
            항목 2: 사업 타당성 (0-100점)
          </label>
          <input
            type="number"
            min="0"
            max="100"
            value={scores['항목2'] || ''}
            onChange={(e) => handleScoreChange('항목2', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <label className="block text-sm font-semibold mb-2">
            종합 의견
          </label>
          <textarea
            rows="4"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="종합적인 평가 의견을 작성해주세요..."
          />
        </div>

        <button className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
          평가 제출
        </button>
      </div>
    </div>
  );
}

export default ScoreInput;
