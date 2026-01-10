import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import companyService from '../../services/companyService';
import useAdminStore from '../../stores/adminStore';

function CompaniesPage() {
  const navigate = useNavigate();
  const {
    companies,
    setCompanies,
    addCompany,
    removeCompany,
    ocrResult,
    setOcrResult,
    clearOcrResult,
  } = useAdminStore();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    business_number: '',
    ceo_name: '',
    address: '',
    phone: '',
    email: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await companyService.getAllCompanies();
      setCompanies(data);
    } catch (err) {
      console.error('Failed to load companies:', err);
      setError(err.response?.data?.detail || '기업 목록을 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // 파일 타입 검증
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
    if (!validTypes.includes(file.type)) {
      alert('JPG, PNG 또는 PDF 파일만 업로드 가능합니다');
      return;
    }

    // 파일 크기 검증 (10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('파일 크기는 10MB 이하여야 합니다');
      return;
    }

    try {
      setUploading(true);
      const result = await companyService.uploadOCR(file);
      setOcrResult(result);

      // OCR 결과를 폼에 자동 입력
      setFormData({
        name: result.company_name || '',
        business_number: result.business_number || '',
        ceo_name: result.ceo_name || '',
        address: result.address || '',
        phone: formData.phone, // OCR에서 추출 안됨
        email: formData.email, // OCR에서 추출 안됨
      });

      alert('OCR 처리가 완료되었습니다. 정보를 확인하고 수정하세요.');
    } catch (err) {
      console.error('OCR upload failed:', err);
      alert(err.response?.data?.detail || 'OCR 처리에 실패했습니다');
    } finally {
      setUploading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      alert('기업명을 입력하세요');
      return;
    }

    try {
      setSubmitting(true);
      const newCompany = await companyService.createCompany(formData);
      addCompany(newCompany);
      setShowModal(false);
      setFormData({
        name: '',
        business_number: '',
        ceo_name: '',
        address: '',
        phone: '',
        email: '',
      });
      clearOcrResult();
      alert('기업이 생성되었습니다');
    } catch (err) {
      console.error('Failed to create company:', err);
      alert(err.response?.data?.detail || '기업 생성에 실패했습니다');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`"${name}" 기업을 삭제하시겠습니까?`)) {
      return;
    }

    try {
      await companyService.deleteCompany(id);
      removeCompany(id);
      alert('기업이 삭제되었습니다');
    } catch (err) {
      console.error('Failed to delete company:', err);
      alert(err.response?.data?.detail || '기업 삭제에 실패했습니다');
    }
  };

  const filteredCompanies = companies.filter((company) =>
    company.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    company.business_number?.includes(searchTerm) ||
    company.ceo_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">기업 관리</h1>
          <p className="text-gray-600 mt-2">평가 대상 기업을 관리합니다</p>
        </div>
        <button
          onClick={() => {
            setShowModal(true);
            clearOcrResult();
          }}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          기업 추가
        </button>
      </div>

      {/* 검색 */}
      <div className="mb-6">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full max-w-md px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="기업명, 사업자번호, 대표자명으로 검색..."
        />
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* 기업 목록 */}
      {filteredCompanies.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-500 mb-4">
            {searchTerm ? '검색 결과가 없습니다' : '등록된 기업이 없습니다'}
          </p>
          {!searchTerm && (
            <button
              onClick={() => setShowModal(true)}
              className="text-blue-600 hover:text-blue-700"
            >
              첫 기업 추가하기 →
            </button>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  기업명
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  사업자번호
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  대표자
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  연락처
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  작업
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredCompanies.map((company) => (
                <tr key={company.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{company.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-600">{company.business_number || '-'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-600">{company.ceo_name || '-'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-600">{company.phone || '-'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleDelete(company.id, company.name)}
                      className="text-red-600 hover:text-red-900"
                    >
                      삭제
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 생성 모달 */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-screen overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold">새 기업 추가</h2>
              <p className="text-sm text-gray-600 mt-1">
                사업자등록증을 업로드하면 정보가 자동으로 입력됩니다
              </p>
            </div>

            <form onSubmit={handleCreate} className="p-6 space-y-6">
              {/* OCR 업로드 */}
              <div className="bg-blue-50 border-2 border-dashed border-blue-300 rounded-lg p-6">
                <div className="text-center">
                  <svg
                    className="mx-auto h-12 w-12 text-blue-400"
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 48 48"
                  >
                    <path
                      d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                      strokeWidth={2}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <div className="mt-4">
                    <label
                      htmlFor="file-upload"
                      className="cursor-pointer inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                    >
                      {uploading ? '처리 중...' : '사업자등록증 업로드'}
                      <input
                        id="file-upload"
                        type="file"
                        className="sr-only"
                        accept="image/jpeg,image/jpg,image/png,application/pdf"
                        onChange={handleFileUpload}
                        disabled={uploading}
                      />
                    </label>
                  </div>
                  <p className="mt-2 text-xs text-gray-500">JPG, PNG, PDF (최대 10MB)</p>
                </div>

                {ocrResult && (
                  <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm text-green-800 font-medium">
                      ✓ OCR 처리 완료! 신뢰도: {(ocrResult.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                )}
              </div>

              {/* 기업 정보 입력 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    기업명 *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    사업자등록번호
                  </label>
                  <input
                    type="text"
                    value={formData.business_number}
                    onChange={(e) => setFormData({ ...formData, business_number: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="000-00-00000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    대표자명
                  </label>
                  <input
                    type="text"
                    value={formData.ceo_name}
                    onChange={(e) => setFormData({ ...formData, ceo_name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    전화번호
                  </label>
                  <input
                    type="text"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="02-1234-5678"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    이메일
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="company@example.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  주소
                </label>
                <textarea
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={2}
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    clearOcrResult();
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
                  disabled={submitting}
                >
                  취소
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                  disabled={submitting}
                >
                  {submitting ? '생성 중...' : '생성'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default CompaniesPage;
