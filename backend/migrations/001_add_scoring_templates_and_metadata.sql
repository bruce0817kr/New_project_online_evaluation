-- Migration: Add scoring templates, score history, and evaluation metadata
-- Date: 2026-01-11
-- Description: P1 features and Canvas signature system

-- ============================================
-- 1. Create scoring_templates table
-- ============================================
CREATE TABLE IF NOT EXISTS scoring_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    total_score INTEGER NOT NULL DEFAULT 100,
    sections JSONB NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_scoring_templates_active ON scoring_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_scoring_templates_default ON scoring_templates(is_default);
CREATE INDEX IF NOT EXISTS idx_scoring_templates_created_at ON scoring_templates(created_at);

-- ============================================
-- 2. Add scoring_template_id to projects table
-- ============================================
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS scoring_template_id UUID REFERENCES scoring_templates(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_projects_scoring_template ON projects(scoring_template_id);

-- ============================================
-- 3. Create score_history table (Audit Log)
-- ============================================
CREATE TABLE IF NOT EXISTS score_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluation_id UUID NOT NULL REFERENCES evaluations(id) ON DELETE CASCADE,
    evaluator_id UUID REFERENCES users(id) ON DELETE SET NULL,
    item_id VARCHAR(100) NOT NULL,
    item_name VARCHAR(200),
    old_score DOUBLE PRECISION,
    new_score DOUBLE PRECISION NOT NULL,
    change_type VARCHAR(50) DEFAULT 'UPDATE',
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_score_history_evaluation ON score_history(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_score_history_evaluator ON score_history(evaluator_id);
CREATE INDEX IF NOT EXISTS idx_score_history_created_at ON score_history(created_at);

-- ============================================
-- 4. Add metadata fields to evaluations table
--    (Canvas signature system - non-repudiation)
-- ============================================
ALTER TABLE evaluations
ADD COLUMN IF NOT EXISTS submit_ip VARCHAR(45),
ADD COLUMN IF NOT EXISTS submit_user_agent VARCHAR(500);

-- Index for IP-based queries (security/audit)
CREATE INDEX IF NOT EXISTS idx_evaluations_submit_ip ON evaluations(submit_ip);

-- ============================================
-- 5. Comments on tables and columns
-- ============================================
COMMENT ON TABLE scoring_templates IS '평가 배점표 템플릿 - 동적 평가 기준 관리';
COMMENT ON COLUMN scoring_templates.sections IS 'JSON 형식의 평가 섹션 및 항목 정의';
COMMENT ON COLUMN scoring_templates.is_default IS '기본 템플릿 여부 (하나만 true)';

COMMENT ON TABLE score_history IS '평가 점수 변경 이력 - 감사 로그';
COMMENT ON COLUMN score_history.change_type IS '변경 유형: CREATE, UPDATE, DELETE';

COMMENT ON COLUMN evaluations.submit_ip IS '평가 제출 시 클라이언트 IP 주소 (부인 방지)';
COMMENT ON COLUMN evaluations.submit_user_agent IS '평가 제출 시 브라우저 정보 (부인 방지)';
COMMENT ON COLUMN evaluations.signature_data IS 'Canvas Base64 이미지 데이터 (전자 서명)';

-- ============================================
-- Migration complete
-- ============================================
