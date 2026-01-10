import React from 'react';

/**
 * Skeleton - 로딩 스켈레톤 컴포넌트
 *
 * @param {Object} props
 * @param {string} props.variant - 'text' | 'circular' | 'rectangular' | 'card'
 * @param {string} props.width - CSS width (예: '100%', '200px')
 * @param {string} props.height - CSS height (예: '20px', '100px')
 * @param {string} props.className - 추가 CSS 클래스
 */
export function Skeleton({ variant = 'text', width, height, className = '' }) {
  const baseClass = 'bg-gray-200 animate-pulse';

  const variantClasses = {
    text: 'rounded h-4',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
    card: 'rounded-lg',
  };

  const style = {
    width: width,
    height: height || (variant === 'text' ? '1rem' : undefined),
  };

  return (
    <div
      className={`${baseClass} ${variantClasses[variant]} ${className}`}
      style={style}
      aria-hidden="true"
    />
  );
}

/**
 * TableSkeleton - 테이블 로딩 스켈레톤
 */
export function TableSkeleton({ rows = 5, columns = 5 }) {
  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      {/* Header */}
      <div className="bg-gray-50 border-b border-gray-200 p-6 flex gap-4">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} variant="text" width={`${100 / columns}%`} height="12px" />
        ))}
      </div>

      {/* Rows */}
      <div className="divide-y divide-gray-200">
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <div key={rowIndex} className="p-6 flex gap-4">
            {Array.from({ length: columns }).map((_, colIndex) => (
              <Skeleton key={colIndex} variant="text" width={`${100 / columns}%`} height="16px" />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * CardSkeleton - 카드 로딩 스켈레톤
 */
export function CardSkeleton({ count = 1 }) {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="bg-white rounded-lg shadow p-6 space-y-4">
          <Skeleton variant="text" width="60%" height="24px" />
          <Skeleton variant="text" width="100%" height="16px" />
          <Skeleton variant="text" width="80%" height="16px" />
          <div className="flex gap-3 pt-4">
            <Skeleton variant="rectangular" width="50%" height="40px" />
            <Skeleton variant="rectangular" width="50%" height="40px" />
          </div>
        </div>
      ))}
    </>
  );
}

/**
 * ListSkeleton - 리스트 로딩 스켈레톤
 */
export function ListSkeleton({ items = 5 }) {
  return (
    <div className="bg-white rounded-lg shadow divide-y divide-gray-200">
      {Array.from({ length: items }).map((_, index) => (
        <div key={index} className="p-6 flex items-start gap-4">
          <Skeleton variant="circular" width="48px" height="48px" />
          <div className="flex-1 space-y-2">
            <Skeleton variant="text" width="40%" height="20px" />
            <Skeleton variant="text" width="80%" height="16px" />
            <Skeleton variant="text" width="60%" height="16px" />
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * StatCardSkeleton - 통계 카드 로딩 스켈레톤
 */
export function StatCardSkeleton({ count = 4 }) {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <Skeleton variant="circular" width="32px" height="32px" />
            <Skeleton variant="rectangular" width="80px" height="24px" />
          </div>
          <Skeleton variant="text" width="60%" height="36px" />
        </div>
      ))}
    </>
  );
}

/**
 * DashboardSkeleton - 대시보드 전체 로딩 스켈레톤
 */
export function DashboardSkeleton() {
  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <Skeleton variant="text" width="300px" height="32px" />
        <Skeleton variant="text" width="200px" height="16px" />
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCardSkeleton count={4} />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <Skeleton variant="text" width="150px" height="20px" />
          <Skeleton variant="rectangular" width="100%" height="200px" />
        </div>
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <Skeleton variant="text" width="150px" height="20px" />
          <Skeleton variant="rectangular" width="100%" height="200px" />
        </div>
      </div>

      {/* Table */}
      <TableSkeleton rows={5} columns={5} />
    </div>
  );
}

/**
 * FormSkeleton - 폼 로딩 스켈레톤
 */
export function FormSkeleton({ fields = 5 }) {
  return (
    <div className="bg-white rounded-lg shadow p-6 space-y-6">
      <Skeleton variant="text" width="200px" height="28px" />

      {Array.from({ length: fields }).map((_, index) => (
        <div key={index} className="space-y-2">
          <Skeleton variant="text" width="120px" height="16px" />
          <Skeleton variant="rectangular" width="100%" height="40px" />
        </div>
      ))}

      <div className="flex gap-3 pt-4">
        <Skeleton variant="rectangular" width="100px" height="40px" />
        <Skeleton variant="rectangular" width="100px" height="40px" />
      </div>
    </div>
  );
}

export default Skeleton;
