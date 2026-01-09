import React from 'react';

/**
 * PDF 뷰어 컴포넌트
 * react-pdf 라이브러리를 활용한 문서 렌더링
 */
function PDFViewer({ pdfUrl }) {
  if (!pdfUrl) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        <div className="text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          <p className="mt-4">서류를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4">
      {/* TODO: Implement PDF rendering with react-pdf */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
        <p className="text-gray-500">PDF 뷰어가 여기에 렌더링됩니다</p>
        <p className="text-sm text-gray-400 mt-2">{pdfUrl}</p>
      </div>
    </div>
  );
}

export default PDFViewer;
