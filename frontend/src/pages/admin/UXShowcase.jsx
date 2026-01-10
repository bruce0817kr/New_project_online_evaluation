import React, { useState } from 'react';
import { useToast } from '../../contexts/ToastContext';
import {
  Skeleton,
  TableSkeleton,
  CardSkeleton,
  ListSkeleton,
  StatCardSkeleton,
  DashboardSkeleton,
  FormSkeleton,
} from '../../components/common/Skeleton';

/**
 * UX Showcase - 모든 UX 개선사항 데모 페이지
 */
function UXShowcase() {
  const toast = useToast();
  const [activeDemo, setActiveDemo] = useState('toasts');

  const demos = [
    { id: 'toasts', label: '🎨 Toast 알림', icon: '🔔' },
    { id: 'skeletons', label: '💀 로딩 스켈레톤', icon: '⏳' },
    { id: 'errors', label: '⚠️ 에러 처리', icon: '🚨' },
    { id: 'accessibility', label: '♿ 접근성', icon: '👁️' },
  ];

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🎨 UX 개선사항 쇼케이스
        </h1>
        <p className="text-gray-600">
          Phase 4에서 구현된 모든 UX 개선사항을 확인하세요
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="mb-8 flex gap-2 flex-wrap">
        {demos.map((demo) => (
          <button
            key={demo.id}
            onClick={() => setActiveDemo(demo.id)}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              activeDemo === demo.id
                ? 'bg-blue-600 text-white shadow-lg scale-105'
                : 'bg-white text-gray-700 hover:bg-gray-100 shadow'
            }`}
          >
            <span className="mr-2">{demo.icon}</span>
            {demo.label}
          </button>
        ))}
      </div>

      {/* Demo Content */}
      <div className="bg-white rounded-lg shadow-lg p-8">
        {activeDemo === 'toasts' && <ToastsDemo toast={toast} />}
        {activeDemo === 'skeletons' && <SkeletonsDemo />}
        {activeDemo === 'errors' && <ErrorsDemo />}
        {activeDemo === 'accessibility' && <AccessibilityDemo />}
      </div>
    </div>
  );
}

/**
 * Toast 알림 데모
 */
function ToastsDemo({ toast }) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Toast 알림 시스템</h2>
        <p className="text-gray-600 mb-6">
          alert() 대신 사용하는 우아한 알림 시스템입니다.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ToastButton
          type="success"
          label="Success Toast"
          onClick={() => toast.success('작업이 성공적으로 완료되었습니다!')}
        />
        <ToastButton
          type="error"
          label="Error Toast"
          onClick={() => toast.error('오류가 발생했습니다. 다시 시도해주세요.')}
        />
        <ToastButton
          type="warning"
          label="Warning Toast"
          onClick={() => toast.warning('주의: 이 작업은 되돌릴 수 없습니다.')}
        />
        <ToastButton
          type="info"
          label="Info Toast"
          onClick={() => toast.info('새로운 업데이트가 있습니다.')}
        />
      </div>

      {/* Custom Duration */}
      <div className="border-t border-gray-200 pt-6">
        <h3 className="text-lg font-semibold mb-3">커스텀 지속 시간</h3>
        <div className="flex gap-3">
          <button
            onClick={() => toast.info('1초 후 사라집니다', 1000)}
            className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            1초
          </button>
          <button
            onClick={() => toast.info('5초 후 사라집니다', 5000)}
            className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            5초
          </button>
          <button
            onClick={() => toast.info('10초 후 사라집니다', 10000)}
            className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            10초
          </button>
        </div>
      </div>

      {/* Code Example */}
      <div className="border-t border-gray-200 pt-6">
        <h3 className="text-lg font-semibold mb-3">사용 예시</h3>
        <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
{`import { useToast } from '../../contexts/ToastContext';

function MyComponent() {
  const toast = useToast();

  const handleSubmit = async () => {
    try {
      await submitData();
      toast.success('저장되었습니다!');
    } catch (error) {
      toast.error('저장에 실패했습니다.');
    }
  };

  return <button onClick={handleSubmit}>저장</button>;
}`}
        </pre>
      </div>
    </div>
  );
}

function ToastButton({ type, label, onClick }) {
  const colors = {
    success: 'bg-green-600 hover:bg-green-700',
    error: 'bg-red-600 hover:bg-red-700',
    warning: 'bg-yellow-600 hover:bg-yellow-700',
    info: 'bg-blue-600 hover:bg-blue-700',
  };

  return (
    <button
      onClick={onClick}
      className={`${colors[type]} text-white px-6 py-4 rounded-lg font-medium transition-colors shadow-lg hover:shadow-xl`}
    >
      {label}
    </button>
  );
}

/**
 * 로딩 스켈레톤 데모
 */
function SkeletonsDemo() {
  const [showSkeleton, setShowSkeleton] = useState({
    table: true,
    card: true,
    list: true,
    stat: true,
    dashboard: false,
    form: true,
  });

  const toggleSkeleton = (key) => {
    setShowSkeleton((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-2">로딩 스켈레톤</h2>
        <p className="text-gray-600 mb-6">
          로딩 스피너 대신 사용하는 컨텐츠 모양 스켈레톤입니다.
        </p>
      </div>

      {/* Table Skeleton */}
      <SkeletonSection
        title="테이블 스켈레톤"
        show={showSkeleton.table}
        onToggle={() => toggleSkeleton('table')}
      >
        {showSkeleton.table ? (
          <TableSkeleton rows={3} columns={4} />
        ) : (
          <div className="bg-white rounded-lg shadow p-6">
            <table className="min-w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">이름</th>
                  <th className="text-left py-2">이메일</th>
                  <th className="text-left py-2">역할</th>
                  <th className="text-left py-2">상태</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="py-3">홍길동</td>
                  <td className="py-3">hong@example.com</td>
                  <td className="py-3">관리자</td>
                  <td className="py-3">활성</td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </SkeletonSection>

      {/* Card Skeleton */}
      <SkeletonSection
        title="카드 스켈레톤"
        show={showSkeleton.card}
        onToggle={() => toggleSkeleton('card')}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {showSkeleton.card ? (
            <CardSkeleton count={2} />
          ) : (
            <>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-bold mb-2">프로젝트 A</h3>
                <p className="text-gray-600 mb-4">프로젝트 설명입니다.</p>
                <div className="flex gap-3">
                  <button className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg">
                    상세보기
                  </button>
                  <button className="px-4 py-2 bg-red-50 text-red-600 rounded-lg">
                    삭제
                  </button>
                </div>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-bold mb-2">프로젝트 B</h3>
                <p className="text-gray-600 mb-4">프로젝트 설명입니다.</p>
                <div className="flex gap-3">
                  <button className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg">
                    상세보기
                  </button>
                  <button className="px-4 py-2 bg-red-50 text-red-600 rounded-lg">
                    삭제
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </SkeletonSection>

      {/* List Skeleton */}
      <SkeletonSection
        title="리스트 스켈레톤"
        show={showSkeleton.list}
        onToggle={() => toggleSkeleton('list')}
      >
        {showSkeleton.list ? (
          <ListSkeleton items={3} />
        ) : (
          <div className="bg-white rounded-lg shadow divide-y">
            <div className="p-6 flex items-start gap-4">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                H
              </div>
              <div>
                <h4 className="font-semibold">홍길동</h4>
                <p className="text-sm text-gray-600">hong@example.com</p>
                <p className="text-xs text-gray-500">관리자</p>
              </div>
            </div>
          </div>
        )}
      </SkeletonSection>

      {/* Stat Card Skeleton */}
      <SkeletonSection
        title="통계 카드 스켈레톤"
        show={showSkeleton.stat}
        onToggle={() => toggleSkeleton('stat')}
      >
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {showSkeleton.stat ? (
            <StatCardSkeleton count={4} />
          ) : (
            <>
              <StatCard title="전체 사업" value="12" icon="📁" />
              <StatCard title="평가 기업" value="45" icon="🏢" />
              <StatCard title="심사위원" value="8" icon="👥" />
              <StatCard title="진행중 평가" value="23" icon="📝" />
            </>
          )}
        </div>
      </SkeletonSection>

      {/* Code Example */}
      <div className="border-t border-gray-200 pt-6">
        <h3 className="text-lg font-semibold mb-3">사용 예시</h3>
        <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
{`import { TableSkeleton, CardSkeleton } from '../../components/common/Skeleton';

function MyPage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);

  if (loading) {
    return <TableSkeleton rows={5} columns={4} />;
  }

  return <DataTable data={data} />;
}`}
        </pre>
      </div>
    </div>
  );
}

function SkeletonSection({ title, show, onToggle, children }) {
  return (
    <div className="border border-gray-200 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">{title}</h3>
        <button
          onClick={onToggle}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            show
              ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {show ? '실제 데이터 보기' : '스켈레톤 보기'}
        </button>
      </div>
      {children}
    </div>
  );
}

function StatCard({ title, value, icon }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <span className="text-2xl">{icon}</span>
        <span className="text-sm font-medium text-gray-600">{title}</span>
      </div>
      <div className="text-3xl font-bold text-gray-900">{value}</div>
    </div>
  );
}

/**
 * 에러 처리 데모
 */
function ErrorsDemo() {
  const toast = useToast();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">에러 처리</h2>
        <p className="text-gray-600 mb-6">
          Error Boundary와 에러 핸들링 패턴입니다.
        </p>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-yellow-900 mb-2">
          🛡️ Error Boundary
        </h3>
        <p className="text-yellow-800 mb-4">
          React 컴포넌트 트리에서 발생하는 JavaScript 에러를 catch하고 fallback UI를 표시합니다.
        </p>
        <pre className="bg-yellow-100 text-yellow-900 p-4 rounded text-sm overflow-x-auto">
{`import ErrorBoundary from './components/common/ErrorBoundary';

<ErrorBoundary>
  <YourComponent />
</ErrorBoundary>`}
        </pre>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h4 className="font-semibold text-red-900 mb-2">❌ Before (Bad)</h4>
          <pre className="bg-red-100 text-red-900 p-3 rounded text-xs overflow-x-auto">
{`try {
  await api.post('/data');
  alert('성공!');
} catch (error) {
  alert('실패!');
}`}
          </pre>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h4 className="font-semibold text-green-900 mb-2">✅ After (Good)</h4>
          <pre className="bg-green-100 text-green-900 p-3 rounded text-xs overflow-x-auto">
{`try {
  await api.post('/data');
  toast.success('성공!');
} catch (error) {
  toast.error(error.message);
}`}
          </pre>
        </div>
      </div>

      <div className="border-t border-gray-200 pt-6">
        <h3 className="text-lg font-semibold mb-3">에러 핸들링 데모</h3>
        <div className="flex gap-3">
          <button
            onClick={() => {
              toast.error('네트워크 오류가 발생했습니다.');
            }}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            네트워크 오류 시뮬레이션
          </button>
          <button
            onClick={() => {
              toast.error('권한이 없습니다 (403 Forbidden)');
            }}
            className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
          >
            권한 오류 시뮬레이션
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * 접근성 데모
 */
function AccessibilityDemo() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">접근성 개선</h2>
        <p className="text-gray-600 mb-6">
          ARIA 레이블, 키보드 네비게이션, 시맨틱 HTML 사용
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-3">✅ 구현된 기능</h3>
          <ul className="space-y-2 text-sm text-blue-800">
            <li>• ARIA labels (aria-label, aria-hidden)</li>
            <li>• 키보드 네비게이션 지원</li>
            <li>• 시맨틱 HTML (button, nav, main, aside)</li>
            <li>• 포커스 표시 (focus:ring)</li>
            <li>• 스크린 리더 지원 (role, aria-live)</li>
            <li>• 색상 대비 (WCAG AA 준수)</li>
          </ul>
        </div>

        <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
          <h3 className="font-semibold text-purple-900 mb-3">📋 체크리스트</h3>
          <ul className="space-y-2 text-sm text-purple-800">
            <li>✅ 모든 버튼에 명확한 레이블</li>
            <li>✅ 폼 input에 label 연결</li>
            <li>✅ 이미지에 alt 텍스트</li>
            <li>✅ 키보드만으로 전체 네비게이션 가능</li>
            <li>✅ 포커스 순서가 논리적</li>
            <li>✅ 에러 메시지가 명확</li>
          </ul>
        </div>
      </div>

      <div className="border-t border-gray-200 pt-6">
        <h3 className="text-lg font-semibold mb-3">접근성 예시</h3>
        <div className="space-y-4">
          <div>
            <label htmlFor="demo-input" className="block text-sm font-medium text-gray-700 mb-2">
              이름 (키보드로 이동 가능)
            </label>
            <input
              id="demo-input"
              type="text"
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Tab 키로 이동해보세요"
              aria-label="이름 입력"
            />
          </div>

          <div className="flex gap-3">
            <button
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              aria-label="제출하기"
            >
              제출 (Tab으로 포커스)
            </button>
            <button
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              aria-label="취소하기"
            >
              취소 (Enter로 실행)
            </button>
          </div>
        </div>
      </div>

      <div className="bg-gray-100 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-3">코드 예시</h3>
        <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
{`// Good: 접근성 고려
<button
  onClick={handleSubmit}
  className="px-4 py-2 bg-blue-600 rounded focus:ring-2"
  aria-label="폼 제출하기"
>
  제출
</button>

// Bad: 접근성 미고려
<div onClick={handleSubmit} className="px-4 py-2 bg-blue-600">
  제출
</div>`}
        </pre>
      </div>
    </div>
  );
}

export default UXShowcase;
