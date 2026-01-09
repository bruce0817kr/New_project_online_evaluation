import React, { useState } from 'react';
import PDFViewer from './PDFViewer';
import ScoreInput from './ScoreInput';

/**
 * 2분할 평가 UI
 * 좌측: PDF 뷰어
 * 우측: 점수 입력
 */
function SplitViewEvaluator() {
  const [pdfUrl, setPdfUrl] = useState(null);
  const [scores, setScores] = useState({});

  return (
    <div className="h-full flex">
      {/* 좌측: PDF 뷰어 */}
      <div className="w-1/2 border-r border-gray-200 overflow-auto">
        <PDFViewer pdfUrl={pdfUrl} />
      </div>

      {/* 우측: 점수 입력 */}
      <div className="w-1/2 overflow-auto bg-gray-50">
        <ScoreInput scores={scores} onScoreChange={setScores} />
      </div>
    </div>
  );
}

export default SplitViewEvaluator;
