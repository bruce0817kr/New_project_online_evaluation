# 데이터베이스 마이그레이션 가이드

P1 기능 및 Canvas 전자 서명 시스템을 위한 데이터베이스 마이그레이션 가이드입니다.

## 새로 추가된 테이블 및 컬럼

### 1. 새 테이블
- **`scoring_templates`**: 평가 배점표 템플릿 관리
- **`score_history`**: 평가 점수 변경 감사 로그

### 2. 기존 테이블에 추가된 컬럼
- **`projects.scoring_template_id`**: 프로젝트별 평가 템플릿 연결 (UUID, FK)
- **`evaluations.submit_ip`**: 평가 제출 시 IP 주소 (VARCHAR(45))
- **`evaluations.submit_user_agent`**: 평가 제출 시 브라우저 정보 (VARCHAR(500))

---

## 마이그레이션 방법

### 옵션 1: SQLAlchemy 자동 생성 (권장 - 개발 환경)

```bash
cd backend
python3 create_tables.py
```

**특징**:
- 새 테이블을 자동으로 생성
- 기존 테이블은 건드리지 않음 (안전)
- **주의**: 기존 테이블에 컬럼을 추가하지 않음

**기존 테이블에 컬럼 추가**:
```bash
python3 run_migration.py --yes
```

---

### 옵션 2: SQL 파일 직접 실행 (권장 - 프로덕션)

```bash
# PostgreSQL
psql -U sme_admin -d sme_evaluation -f migrations/001_add_scoring_templates_and_metadata.sql

# 또는 환경변수 사용
export PGPASSWORD=sme_secure_pass_2024
psql -h localhost -U sme_admin -d sme_evaluation -f migrations/001_add_scoring_templates_and_metadata.sql
```

---

### 옵션 3: Alembic 사용 (선택)

Alembic이 설치되어 있지 않다면:

```bash
pip install alembic
alembic init alembic
```

`alembic/env.py` 설정 후:

```bash
alembic revision --autogenerate -m "Add scoring templates and metadata"
alembic upgrade head
```

---

## 사전 준비

### 1. 데이터베이스 실행 확인

```bash
# PostgreSQL 상태 확인
sudo systemctl status postgresql

# 또는 Docker Compose 사용 시
docker-compose ps
```

### 2. 데이터베이스 연결 확인

```bash
# .env 파일 확인
cat .env | grep DATABASE_URL

# 연결 테스트
psql -U sme_admin -d sme_evaluation -c "SELECT version();"
```

### 3. 백업 (프로덕션 환경)

```bash
# 전체 데이터베이스 백업
pg_dump -U sme_admin sme_evaluation > backup_$(date +%Y%m%d_%H%M%S).sql

# 특정 테이블만 백업
pg_dump -U sme_admin -t evaluations -t projects sme_evaluation > backup_tables.sql
```

---

## 마이그레이션 검증

마이그레이션 완료 후 확인:

```sql
-- 1. 새 테이블 확인
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('scoring_templates', 'score_history');

-- 2. 새 컬럼 확인
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'evaluations'
AND column_name IN ('submit_ip', 'submit_user_agent');

-- 3. 외래 키 확인
SELECT constraint_name, table_name, column_name
FROM information_schema.key_column_usage
WHERE table_name = 'projects' AND column_name = 'scoring_template_id';
```

---

## 롤백 (문제 발생 시)

```sql
-- 테이블 삭제 (역순)
DROP TABLE IF EXISTS score_history CASCADE;
DROP TABLE IF EXISTS scoring_templates CASCADE;

-- 컬럼 삭제
ALTER TABLE evaluations DROP COLUMN IF EXISTS submit_ip;
ALTER TABLE evaluations DROP COLUMN IF EXISTS submit_user_agent;
ALTER TABLE projects DROP COLUMN IF EXISTS scoring_template_id;
```

---

## 문제 해결

### 오류: "relation already exists"
- 이미 테이블이 존재합니다. `CREATE TABLE IF NOT EXISTS` 사용으로 안전하게 처리됨

### 오류: "column already exists"
- 이미 컬럼이 존재합니다. `ADD COLUMN IF NOT EXISTS` 사용으로 안전하게 처리됨

### 오류: "connection refused"
- PostgreSQL이 실행 중이 아닙니다. `sudo systemctl start postgresql` 또는 Docker 컨테이너 시작

### 오류: "authentication failed"
- `.env` 파일의 DATABASE_URL 확인
- PostgreSQL 사용자 권한 확인: `GRANT ALL PRIVILEGES ON DATABASE sme_evaluation TO sme_admin;`

---

## 참고 파일

- `migrations/001_add_scoring_templates_and_metadata.sql`: SQL 마이그레이션 파일
- `run_migration.py`: Python 마이그레이션 실행 스크립트
- `create_tables.py`: SQLAlchemy 테이블 생성 스크립트
- `backend/app/models/scoring_template.py`: ScoringTemplate 모델
- `backend/app/models/score_history.py`: ScoreHistory 모델
- `backend/app/models/evaluation.py`: Evaluation 모델 (업데이트됨)

---

## 마이그레이션 완료 체크리스트

- [ ] 데이터베이스 백업 완료
- [ ] 마이그레이션 실행 성공
- [ ] 새 테이블 생성 확인 (scoring_templates, score_history)
- [ ] 새 컬럼 추가 확인 (submit_ip, submit_user_agent, scoring_template_id)
- [ ] 인덱스 생성 확인
- [ ] 외래 키 제약조건 확인
- [ ] 애플리케이션 테스트 (템플릿 관리, 전자 서명)
- [ ] 롤백 절차 문서화
