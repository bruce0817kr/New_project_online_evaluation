import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import adminService from '../../services/adminService';
import projectService from '../../services/projectService';
import useAdminStore from '../../stores/adminStore';

function DashboardHome() {
  const navigate = useNavigate();
  const { stats, setStats } = useAdminStore();
  const [recentProjects, setRecentProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 통계 데이터 로드
      const statsData = await adminService.getDashboardStats();
      setStats(statsData);

      // 최근 프로젝트 로드
      const projectsData = await projectService.getAllProjects();
      setRecentProjects(projectsData.slice(0, 5)); // 최근 5개만
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError(err.response?.data?.detail || '데이터를 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <p className="text-red-600">{error}</p>
          <button
            onClick={loadDashboardData}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">관리자 대시보드</h1>
        <p className="text-gray-600 mt-2">전체 시스템 현황을 확인하세요</p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="전체 사업"
          value={stats?.total_projects || 0}
          color="blue"
          icon="📁"
          onClick={() => navigate('/admin/projects')}
        />
        <StatCard
          title="평가 대상 기업"
          value={stats?.total_companies || 0}
          color="green"
          icon="🏢"
          onClick={() => navigate('/admin/companies')}
        />
        <StatCard
          title="심사위원"
          value={stats?.total_evaluators || 0}
          color="purple"
          icon="👥"
          onClick={() => navigate('/admin/users')}
        />
        <StatCard
          title="진행 중 평가"
          value={stats?.evaluations_in_progress || 0}
          color="yellow"
          icon="📝"
          onClick={() => navigate('/admin/evaluations')}
        />
      </div>

      {/* 평가 진행률 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">평가 진행 현황</h2>
          <div className="space-y-4">
            <ProgressBar
              label="제출 완료"
              value={stats?.evaluations_submitted || 0}
              total={stats?.total_evaluations || 1}
              color="green"
            />
            <ProgressBar
              label="진행 중"
              value={stats?.evaluations_in_progress || 0}
              total={stats?.total_evaluations || 1}
              color="blue"
            />
            <ProgressBar
              label="미시작"
              value={
                (stats?.total_evaluations || 0) -
                (stats?.evaluations_submitted || 0) -
                (stats?.evaluations_in_progress || 0)
              }
              total={stats?.total_evaluations || 1}
              color="gray"
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">시스템 활동</h2>
          <div className="space-y-3">
            <ActivityItem
              icon="✅"
              text={`오늘 제출된 평가: ${stats?.today_submissions || 0}건`}
            />
            <ActivityItem
              icon="👤"
              text={`활성 사용자: ${stats?.active_users || 0}명`}
            />
            <ActivityItem
              icon="📊"
              text={`평균 평가 점수: ${stats?.average_score?.toFixed(1) || 'N/A'}점`}
            />
            <ActivityItem
              icon="⏱️"
              text={`평균 평가 시간: ${stats?.average_eval_time || 'N/A'}분`}
            />
          </div>
        </div>
      </div>

      {/* 최근 프로젝트 */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold">최근 사업</h2>
          <button
            onClick={() => navigate('/admin/projects')}
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            전체 보기 →
          </button>
        </div>

        {recentProjects.length === 0 ? (
          <div className="p-12 text-center text-gray-500">
            등록된 사업이 없습니다
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {recentProjects.map((project) => (
              <div
                key={project.id}
                onClick={() => navigate(`/admin/projects/${project.id}`)}
                className="p-6 hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">
                      {project.name}
                    </h3>
                    <p className="text-sm text-gray-600">{project.description}</p>
                    <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                      <span>🗓️ {project.year}년</span>
                      <span>
                        📅 마감: {new Date(project.deadline).toLocaleDateString('ko-KR')}
                      </span>
                    </div>
                  </div>
                  <span
                    className={`px-3 py-1 text-xs font-medium rounded-full ${
                      new Date(project.deadline) > new Date()
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {new Date(project.deadline) > new Date() ? '진행중' : '마감'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// 통계 카드 컴포넌트
function StatCard({ title, value, color, icon, onClick }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    yellow: 'bg-yellow-50 text-yellow-600',
  };

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg shadow p-6 cursor-pointer hover:shadow-lg transition-shadow"
    >
      <div className="flex items-center justify-between mb-4">
        <span className="text-2xl">{icon}</span>
        <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
          <span className="text-sm font-medium">{title}</span>
        </div>
      </div>
      <div className="text-3xl font-bold text-gray-900">{value}</div>
    </div>
  );
}

// 진행률 바 컴포넌트
function ProgressBar({ label, value, total, color }) {
  const percentage = total > 0 ? (value / total) * 100 : 0;

  const colorClasses = {
    green: 'bg-green-500',
    blue: 'bg-blue-500',
    gray: 'bg-gray-300',
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-600">{label}</span>
        <span className="text-sm font-semibold text-gray-900">
          {value} / {total} ({percentage.toFixed(0)}%)
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`${colorClasses[color]} h-2 rounded-full transition-all`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
}

// 활동 아이템 컴포넌트
function ActivityItem({ icon, text }) {
  return (
    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
      <span className="text-xl">{icon}</span>
      <span className="text-sm text-gray-700">{text}</span>
    </div>
  );
}

export default DashboardHome;
