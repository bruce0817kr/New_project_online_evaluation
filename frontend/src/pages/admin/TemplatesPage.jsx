import React, { useState, useEffect } from 'react';
import templateService from '../../services/templateService';

function TemplatesPage() {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [showAllTemplates, setShowAllTemplates] = useState(false);

  useEffect(() => {
    loadTemplates();
  }, [showAllTemplates]);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await templateService.getAllTemplates(!showAllTemplates);
      setTemplates(data);
    } catch (err) {
      console.error('Failed to load templates:', err);
      setError(err.response?.data?.detail || '템플릿 목록을 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`"${name}" 템플릿을 삭제하시겠습니까?`)) {
      return;
    }

    try {
      await templateService.deleteTemplate(id);
      setTemplates(templates.filter((t) => t.id !== id));
      alert('템플릿이 삭제되었습니다');
    } catch (err) {
      console.error('Failed to delete template:', err);
      alert(err.response?.data?.detail || '템플릿 삭제에 실패했습니다');
    }
  };

  const handleToggleActive = async (id, currentStatus) => {
    try {
      await templateService.toggleTemplateActive(id, !currentStatus);
      await loadTemplates();
      alert(`템플릿이 ${!currentStatus ? '활성화' : '비활성화'}되었습니다`);
    } catch (err) {
      console.error('Failed to toggle template:', err);
      alert(err.response?.data?.detail || '템플릿 상태 변경에 실패했습니다');
    }
  };

  const handleSetDefault = async (id) => {
    if (!window.confirm('이 템플릿을 기본 템플릿으로 설정하시겠습니까?')) {
      return;
    }

    try {
      await templateService.setDefaultTemplate(id);
      await loadTemplates();
      alert('기본 템플릿이 설정되었습니다');
    } catch (err) {
      console.error('Failed to set default template:', err);
      alert(err.response?.data?.detail || '기본 템플릿 설정에 실패했습니다');
    }
  };

  const handleCreateDefaultTemplate = async () => {
    if (!window.confirm('R&D 표준 템플릿을 생성하시겠습니까?')) {
      return;
    }

    try {
      const newTemplate = await templateService.createDefaultTemplate();
      setTemplates([...templates, newTemplate]);
      alert('기본 템플릿이 생성되었습니다');
    } catch (err) {
      console.error('Failed to create default template:', err);
      alert(err.response?.data?.detail || '기본 템플릿 생성에 실패했습니다');
    }
  };

  const handlePreview = (template) => {
    setSelectedTemplate(template);
    setShowPreviewModal(true);
  };

  const handleEdit = (template) => {
    setSelectedTemplate(template);
    setShowEditModal(true);
  };

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
          <h1 className="text-3xl font-bold text-gray-900">평가 템플릿 관리</h1>
          <p className="text-gray-600 mt-2">평가 기준 템플릿을 생성하고 관리합니다</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleCreateDefaultTemplate}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            R&D 표준 템플릿
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            템플릿 추가
          </button>
        </div>
      </div>

      {/* Filter */}
      <div className="mb-6">
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={showAllTemplates}
            onChange={(e) => setShowAllTemplates(e.target.checked)}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          비활성화된 템플릿도 표시
        </label>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">{error}</p>
          <button
            onClick={loadTemplates}
            className="mt-2 text-sm text-red-700 hover:text-red-900 underline"
          >
            다시 시도
          </button>
        </div>
      )}

      {/* Templates List */}
      {templates.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-500 mb-4">등록된 템플릿이 없습니다</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="text-blue-600 hover:text-blue-700"
          >
            첫 템플릿 추가하기 →
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {templates.map((template) => (
            <div
              key={template.id}
              className={`bg-white rounded-lg shadow hover:shadow-lg transition-shadow ${
                !template.is_active ? 'opacity-60' : ''
              }`}
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="text-xl font-semibold text-gray-900">
                        {template.name}
                      </h3>
                      {template.is_default && (
                        <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                          기본
                        </span>
                      )}
                    </div>
                    {template.description && (
                      <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                    )}

                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>📊 총점: {template.total_score}점</span>
                      <span>📝 섹션: {template.sections?.sections?.length || 0}개</span>
                    </div>
                  </div>

                  <span
                    className={`px-3 py-1 text-xs font-medium rounded-full ${
                      template.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {template.is_active ? '활성' : '비활성'}
                  </span>
                </div>

                {/* Sections Preview */}
                <div className="mb-4 space-y-2">
                  {template.sections?.sections?.slice(0, 3).map((section, idx) => (
                    <div key={idx} className="flex items-center justify-between text-sm bg-gray-50 rounded px-3 py-2">
                      <span className="text-gray-700">{section.section_name}</span>
                      <span className="text-gray-500 font-medium">{section.max_score}점</span>
                    </div>
                  ))}
                  {template.sections?.sections?.length > 3 && (
                    <div className="text-xs text-gray-500 text-center">
                      +{template.sections.sections.length - 3}개 더보기
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handlePreview(template)}
                    className="flex-1 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
                  >
                    미리보기
                  </button>
                  <button
                    onClick={() => handleEdit(template)}
                    className="flex-1 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors text-sm"
                  >
                    수정
                  </button>
                  {!template.is_default && (
                    <button
                      onClick={() => handleToggleActive(template.id, template.is_active)}
                      className={`px-3 py-2 rounded-lg transition-colors text-sm ${
                        template.is_active
                          ? 'bg-yellow-50 text-yellow-600 hover:bg-yellow-100'
                          : 'bg-green-50 text-green-600 hover:bg-green-100'
                      }`}
                    >
                      {template.is_active ? '비활성' : '활성'}
                    </button>
                  )}
                  {!template.is_default && template.is_active && (
                    <button
                      onClick={() => handleSetDefault(template.id)}
                      className="px-3 py-2 bg-purple-50 text-purple-600 rounded-lg hover:bg-purple-100 transition-colors text-sm"
                    >
                      기본설정
                    </button>
                  )}
                  {!template.is_default && (
                    <button
                      onClick={() => handleDelete(template.id, template.name)}
                      className="px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors text-sm"
                    >
                      삭제
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <TemplateFormModal
          onClose={() => setShowCreateModal(false)}
          onSave={async (data) => {
            await templateService.createTemplate(data);
            await loadTemplates();
            setShowCreateModal(false);
            alert('템플릿이 생성되었습니다');
          }}
        />
      )}

      {/* Edit Modal */}
      {showEditModal && selectedTemplate && (
        <TemplateFormModal
          template={selectedTemplate}
          onClose={() => {
            setShowEditModal(false);
            setSelectedTemplate(null);
          }}
          onSave={async (data) => {
            await templateService.updateTemplate(selectedTemplate.id, data);
            await loadTemplates();
            setShowEditModal(false);
            setSelectedTemplate(null);
            alert('템플릿이 수정되었습니다');
          }}
        />
      )}

      {/* Preview Modal */}
      {showPreviewModal && selectedTemplate && (
        <TemplatePreviewModal
          template={selectedTemplate}
          onClose={() => {
            setShowPreviewModal(false);
            setSelectedTemplate(null);
          }}
        />
      )}
    </div>
  );
}

/**
 * 템플릿 생성/수정 모달
 */
function TemplateFormModal({ template, onClose, onSave }) {
  const isEdit = !!template;
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState(
    template
      ? {
          name: template.name,
          description: template.description || '',
          total_score: template.total_score,
          // 백엔드에서 sections는 배열 형태로 옴
          sections: template.sections || [],
        }
      : {
          name: '',
          description: '',
          total_score: 100,
          sections: [],
        }
  );

  // 섹션 추가
  const addSection = () => {
    setFormData({
      ...formData,
      sections: [
        ...formData.sections,
        {
          section_name: '',
          max_score: 0,
          items: [],
        },
      ],
    });
  };

  // 섹션 삭제
  const removeSection = (sectionIdx) => {
    const newSections = formData.sections.filter((_, idx) => idx !== sectionIdx);
    setFormData({ ...formData, sections: newSections });
  };

  // 섹션 수정
  const updateSection = (sectionIdx, field, value) => {
    const newSections = [...formData.sections];
    newSections[sectionIdx] = {
      ...newSections[sectionIdx],
      [field]: field === 'max_score' ? parseInt(value) || 0 : value,
    };
    setFormData({ ...formData, sections: newSections });
  };

  // 평가 항목 추가
  const addItem = (sectionIdx) => {
    const newSections = [...formData.sections];
    newSections[sectionIdx].items.push({
      item_id: `item_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      title: '',
      max_score: 0,
      step: 1,
    });
    setFormData({ ...formData, sections: newSections });
  };

  // 평가 항목 삭제
  const removeItem = (sectionIdx, itemIdx) => {
    const newSections = [...formData.sections];
    newSections[sectionIdx].items = newSections[sectionIdx].items.filter(
      (_, idx) => idx !== itemIdx
    );
    setFormData({ ...formData, sections: newSections });
  };

  // 평가 항목 수정
  const updateItem = (sectionIdx, itemIdx, field, value) => {
    const newSections = [...formData.sections];
    newSections[sectionIdx].items[itemIdx] = {
      ...newSections[sectionIdx].items[itemIdx],
      [field]: ['max_score', 'step'].includes(field) ? parseFloat(value) || 0 : value,
    };
    setFormData({ ...formData, sections: newSections });
  };

  // 검증 및 저장
  const handleSubmit = async (e) => {
    e.preventDefault();

    // 유효성 검증
    if (!formData.name.trim()) {
      alert('템플릿 이름을 입력하세요');
      return;
    }

    if (formData.sections.length === 0) {
      alert('최소 1개 이상의 섹션을 추가하세요');
      return;
    }

    // 각 섹션의 항목 점수 합계 검증
    for (const section of formData.sections) {
      if (!section.section_name.trim()) {
        alert('섹션 이름을 입력하세요');
        return;
      }

      if (section.items.length === 0) {
        alert(`"${section.section_name}" 섹션에 최소 1개 이상의 평가 항목을 추가하세요`);
        return;
      }

      const itemsTotal = section.items.reduce((sum, item) => sum + (item.max_score || 0), 0);
      if (itemsTotal !== section.max_score) {
        alert(
          `"${section.section_name}" 섹션의 평가 항목 점수 합계(${itemsTotal})가 섹션 배점(${section.max_score})과 일치하지 않습니다`
        );
        return;
      }
    }

    // 전체 섹션 점수 합계 검증
    const sectionsTotal = formData.sections.reduce((sum, s) => sum + (s.max_score || 0), 0);
    if (sectionsTotal !== formData.total_score) {
      alert(
        `섹션 점수 합계(${sectionsTotal})가 총점(${formData.total_score})과 일치하지 않습니다`
      );
      return;
    }

    try {
      setSubmitting(true);
      // 백엔드는 sections를 배열로 기대 (List[ScoringSection])
      await onSave(formData);
    } catch (err) {
      console.error('Failed to save template:', err);
      alert(err.response?.data?.detail || '템플릿 저장에 실패했습니다');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-auto">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-auto">
        <div className="sticky top-0 bg-white p-6 border-b border-gray-200 z-10">
          <h2 className="text-xl font-bold">{isEdit ? '템플릿 수정' : '새 템플릿 추가'}</h2>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* 기본 정보 */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">템플릿 이름 *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="예: 기술혁신 사업 평가 템플릿"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">설명</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={2}
                placeholder="템플릿 설명을 입력하세요"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">총점 *</label>
              <input
                type="number"
                value={formData.total_score}
                onChange={(e) =>
                  setFormData({ ...formData, total_score: parseInt(e.target.value) || 0 })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                min="1"
                required
              />
            </div>
          </div>

          {/* 섹션 및 항목 */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <label className="block text-sm font-medium text-gray-700">평가 섹션 *</label>
              <button
                type="button"
                onClick={addSection}
                className="px-3 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
              >
                + 섹션 추가
              </button>
            </div>

            <div className="space-y-4">
              {formData.sections.map((section, sectionIdx) => (
                <div key={sectionIdx} className="border border-gray-300 rounded-lg p-4 bg-gray-50">
                  {/* 섹션 헤더 */}
                  <div className="flex items-start gap-3 mb-3">
                    <div className="flex-1 grid grid-cols-2 gap-3">
                      <input
                        type="text"
                        value={section.section_name}
                        onChange={(e) =>
                          updateSection(sectionIdx, 'section_name', e.target.value)
                        }
                        className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="섹션 이름 (예: 기술성)"
                        required
                      />
                      <input
                        type="number"
                        value={section.max_score}
                        onChange={(e) => updateSection(sectionIdx, 'max_score', e.target.value)}
                        className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="배점"
                        min="1"
                        required
                      />
                    </div>
                    <button
                      type="button"
                      onClick={() => removeSection(sectionIdx)}
                      className="px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
                    >
                      섹션 삭제
                    </button>
                  </div>

                  {/* 평가 항목 */}
                  <div className="ml-4 space-y-2">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-600">평가 항목</span>
                      <button
                        type="button"
                        onClick={() => addItem(sectionIdx)}
                        className="px-2 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 transition-colors"
                      >
                        + 항목 추가
                      </button>
                    </div>

                    {section.items.map((item, itemIdx) => (
                      <div key={itemIdx} className="flex items-start gap-2 bg-white p-2 rounded">
                        <input
                          type="text"
                          value={item.title}
                          onChange={(e) =>
                            updateItem(sectionIdx, itemIdx, 'title', e.target.value)
                          }
                          className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="항목 제목"
                          required
                        />
                        <input
                          type="number"
                          value={item.max_score}
                          onChange={(e) =>
                            updateItem(sectionIdx, itemIdx, 'max_score', e.target.value)
                          }
                          className="w-20 px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="점수"
                          min="0"
                          step="0.1"
                          required
                        />
                        <input
                          type="number"
                          value={item.step}
                          onChange={(e) => updateItem(sectionIdx, itemIdx, 'step', e.target.value)}
                          className="w-16 px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="단위"
                          min="0.1"
                          step="0.1"
                          required
                        />
                        <button
                          type="button"
                          onClick={() => removeItem(sectionIdx, itemIdx)}
                          className="px-2 py-1 bg-red-50 text-red-600 text-xs rounded hover:bg-red-100 transition-colors"
                        >
                          삭제
                        </button>
                      </div>
                    ))}

                    {section.items.length === 0 && (
                      <div className="text-xs text-gray-500 text-center py-2">
                        평가 항목을 추가하세요
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {formData.sections.length === 0 && (
                <div className="text-sm text-gray-500 text-center py-8 border-2 border-dashed border-gray-300 rounded-lg">
                  섹션을 추가하세요
                </div>
              )}
            </div>
          </div>

          {/* 점수 합계 표시 */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-700">섹션 점수 합계:</span>
              <span
                className={`font-bold ${
                  formData.sections.reduce((sum, s) => sum + (s.max_score || 0), 0) ===
                  formData.total_score
                    ? 'text-green-600'
                    : 'text-red-600'
                }`}
              >
                {formData.sections.reduce((sum, s) => sum + (s.max_score || 0), 0)} /{' '}
                {formData.total_score}점
              </span>
            </div>
          </div>

          {/* 버튼 */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
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
              {submitting ? '저장 중...' : isEdit ? '수정' : '생성'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

/**
 * 템플릿 미리보기 모달
 */
function TemplatePreviewModal({ template, onClose }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-auto">
        <div className="sticky top-0 bg-white p-6 border-b border-gray-200 z-10">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold">{template.name}</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
          {template.description && <p className="text-sm text-gray-600 mt-2">{template.description}</p>}
        </div>

        <div className="p-6 space-y-6">
          {/* 총점 표시 */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-700 font-medium">총점</span>
              <span className="text-2xl font-bold text-blue-600">{template.total_score}점</span>
            </div>
          </div>

          {/* 섹션 및 항목 표시 */}
          {template.sections?.sections?.map((section, sectionIdx) => (
            <div key={sectionIdx} className="border border-gray-200 rounded-lg overflow-hidden">
              <div className="bg-gray-100 px-4 py-3 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium text-gray-900">{section.section_name}</h3>
                  <span className="text-sm font-medium text-gray-600">
                    배점: {section.max_score}점
                  </span>
                </div>
              </div>

              <div className="p-4 space-y-3">
                {section.items?.map((item, itemIdx) => (
                  <div
                    key={itemIdx}
                    className="flex items-center justify-between bg-gray-50 px-4 py-3 rounded-lg"
                  >
                    <div className="flex-1">
                      <span className="text-gray-900">{item.title}</span>
                      <span className="text-xs text-gray-500 ml-2">(단위: {item.step}점)</span>
                    </div>
                    <span className="text-sm font-medium text-gray-600">{item.max_score}점</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="sticky bottom-0 bg-white p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
}

export default TemplatesPage;
