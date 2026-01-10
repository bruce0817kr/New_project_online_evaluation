# 통합 테스트 가이드

## 개요

이 문서는 중소기업 선정평가 시스템의 전체 통합 테스트 절차를 설명합니다.

## 전제 조건

### 필수 소프트웨어
- Docker 20.10+
- Docker Compose 1.29+
- curl (API 테스트용)
- jq (JSON 파싱용, 선택사항)

### 환경 설정
```bash
# .env 파일 확인 및 수정
cp .env.example .env
nano .env
```

**중요 환경 변수**:
```bash
# 데이터베이스
DB_PASSWORD=sme_secure_pass_2024

# JWT 인증
SECRET_KEY=your-super-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OCR API 키 (선택사항)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
MISTRAL_API_KEY=...

# OCR 설정
OCR_FALLBACK_STRATEGY=on_low_confidence
OCR_CONFIDENCE_THRESHOLD=0.85
```

## 1단계: 시스템 시작

### 자동 시작 (권장)
```bash
chmod +x start.sh
./start.sh
```

이 스크립트는 다음을 자동으로 수행합니다:
1. ✅ 환경 변수 파일 확인
2. ✅ Docker 이미지 빌드
3. ✅ 기존 컨테이너 정리
4. ✅ PostgreSQL 시작 및 대기
5. ✅ Alembic 마이그레이션 실행
6. ✅ 초기 데이터 삽입
7. ✅ 전체 서비스 시작
8. ✅ 서비스 상태 확인

### 수동 시작

```bash
# 1. 빌드
docker-compose build --no-cache

# 2. 기존 컨테이너 정리
docker-compose down -v

# 3. PostgreSQL만 시작
docker-compose up -d postgres
sleep 10

# 4. 마이그레이션 실행
docker-compose run --rm backend alembic upgrade head

# 5. 초기 데이터 삽입
docker-compose run --rm backend python migrations/seed_data.py

# 6. 전체 서비스 시작
docker-compose up -d

# 7. 상태 확인
docker-compose ps
```

## 2단계: 서비스 상태 확인

### 컨테이너 상태
```bash
docker-compose ps
```

**예상 출력**:
```
NAME                           STATUS              PORTS
sme-evaluation-backend         Up 30 seconds       0.0.0.0:8000->8000/tcp
sme-evaluation-frontend        Up 30 seconds       0.0.0.0:3000->3000/tcp
sme-evaluation-postgres        Up 1 minute         0.0.0.0:5432->5432/tcp
sme-evaluation-nginx           Up 30 seconds       0.0.0.0:80->80/tcp
```

### 로그 확인
```bash
# 전체 로그
docker-compose logs -f

# 백엔드만
docker-compose logs -f backend

# 최근 50줄
docker-compose logs --tail=50 backend
```

### 헬스 체크
```bash
# Backend API
curl http://localhost:8000/health
# 예상: {"status":"ok"}

# API Docs
curl http://localhost:8000/api/docs
# Swagger UI 접속 가능
```

## 3단계: 데이터베이스 확인

### 테이블 생성 확인
```bash
docker-compose exec postgres psql -U sme_admin -d sme_evaluation -c "
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';
"
```

**예상 테이블**:
- users
- audit_logs
- projects
- companies
- evaluations

### 초기 데이터 확인
```bash
# 사용자 수
docker-compose exec postgres psql -U sme_admin -d sme_evaluation -c "
SELECT role, COUNT(*)
FROM users
GROUP BY role;
"
# 예상: admin (1), evaluator (5)

# 프로젝트 수
docker-compose exec postgres psql -U sme_admin -d sme_evaluation -c "
SELECT COUNT(*) FROM projects;
"
# 예상: 1

# 기업 수
docker-compose exec postgres psql -U sme_admin -d sme_evaluation -c "
SELECT COUNT(*) FROM companies;
"
# 예상: 5

# 평가 수
docker-compose exec postgres psql -U sme_admin -d sme_evaluation -c "
SELECT is_submitted, COUNT(*)
FROM evaluations
GROUP BY is_submitted;
"
# 예상: true (15), false (10)
```

## 4단계: API 테스트

자세한 API 테스트는 `API_TEST_SAMPLES.md`를 참조하세요.

### 빠른 테스트

```bash
# 1. 로그인
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=Admin123!" | jq -r .access_token)

echo "Token: $TOKEN"

# 2. 현재 사용자 정보
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN" | jq

# 3. 프로젝트 목록
curl -X GET http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" | jq

# 4. OCR 엔진 목록
curl -X GET http://localhost:8000/api/v1/ocr/engines \
  -H "Authorization: Bearer $TOKEN" | jq
```

## 5단계: OCR 기능 테스트

### 테스트 이미지 준비
```bash
# 샘플 이미지 다운로드 (또는 실제 사업자등록증 이미지 사용)
mkdir -p test_data
# 실제 이미지를 test_data/business_license.jpg에 저장
```

### OCR 분석 요청
```bash
# Tesseract 엔진 사용
curl -X POST http://localhost:8000/api/v1/ocr/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_data/business_license.jpg" \
  -F "document_type=사업자등록증" | jq

# OpenAI 엔진 지정 (API 키 필요)
curl -X POST http://localhost:8000/api/v1/ocr/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_data/business_license.jpg" \
  -F "document_type=사업자등록증" \
  -F "preferred_engine=openai" | jq
```

## 6단계: 평가 워크플로우 테스트

### 심사위원으로 로그인
```bash
EVAL_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=evaluator1&password=Eval123!" | jq -r .access_token)
```

### 평가 조회 및 수정
```bash
# 내 평가 목록 (미제출)
curl -X GET "http://localhost:8000/api/v1/evaluations/my?status=in_progress" \
  -H "Authorization: Bearer $EVAL_TOKEN" | jq

# 평가 ID 추출 (첫 번째 평가)
EVAL_ID=$(curl -s -X GET "http://localhost:8000/api/v1/evaluations/my?status=in_progress" \
  -H "Authorization: Bearer $EVAL_TOKEN" | jq -r .[0].id)

echo "Evaluation ID: $EVAL_ID"

# 평가 상세 조회
curl -X GET "http://localhost:8000/api/v1/evaluations/$EVAL_ID" \
  -H "Authorization: Bearer $EVAL_TOKEN" | jq

# 평가 저장 (제출 전 임시 저장)
curl -X PUT "http://localhost:8000/api/v1/evaluations/$EVAL_ID" \
  -H "Authorization: Bearer $EVAL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scores": {
      "기술성": 85.0,
      "사업성": 78.0,
      "경제성": 90.0
    },
    "comments": "기술력이 우수하며 사업화 가능성이 높음"
  }' | jq

# 평가 제출 (불변)
curl -X POST "http://localhost:8000/api/v1/evaluations/$EVAL_ID/submit" \
  -H "Authorization: Bearer $EVAL_TOKEN" | jq
```

### 제출 후 수정 시도 (실패해야 함)
```bash
curl -X PUT "http://localhost:8000/api/v1/evaluations/$EVAL_ID" \
  -H "Authorization: Bearer $EVAL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scores": {
      "기술성": 95.0
    }
  }'
# 예상: 400 Bad Request - "이미 제출된 평가는 수정할 수 없습니다"
```

## 7단계: 점수 집계 테스트

### 관리자로 점수 조회
```bash
# 프로젝트 ID 추출
PROJECT_ID=$(curl -s -X GET http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" | jq -r .[0].id)

# 기업 ID 추출
COMPANY_ID=$(curl -s -X GET "http://localhost:8000/api/v1/projects/$PROJECT_ID/companies" \
  -H "Authorization: Bearer $TOKEN" | jq -r .[0].id)

# 점수 집계 조회
curl -X GET "http://localhost:8000/api/v1/scores/project/$PROJECT_ID/company/$COMPANY_ID" \
  -H "Authorization: Bearer $TOKEN" | jq
```

**예상 응답**:
```json
{
  "project_id": "...",
  "company_id": "...",
  "company_name": "(주)테크이노베이션",
  "total_evaluators": 5,
  "submitted_count": 3,
  "aggregated_scores": {
    "기술성": 82.5,
    "사업성": 76.0,
    "경제성": 88.3
  },
  "final_score": 82.27,
  "calculation_method": "trimmed_mean",
  "individual_scores": [...]
}
```

## 8단계: 감사 로그 확인

```bash
# 최근 감사 로그
docker-compose exec postgres psql -U sme_admin -d sme_evaluation -c "
SELECT username, action, resource, status, created_at
FROM audit_logs
ORDER BY created_at DESC
LIMIT 10;
"
```

## 트러블슈팅

### 컨테이너가 시작되지 않음
```bash
# 로그 확인
docker-compose logs backend

# 포트 충돌 확인
sudo netstat -tulpn | grep -E ':(3000|8000|5432|80)'

# 기존 컨테이너 완전 삭제
docker-compose down -v
docker system prune -a
```

### 데이터베이스 연결 실패
```bash
# PostgreSQL 준비 대기
docker-compose up -d postgres
sleep 15

# 연결 테스트
docker-compose exec postgres psql -U sme_admin -d sme_evaluation -c "SELECT 1;"
```

### 마이그레이션 실패
```bash
# 마이그레이션 히스토리 확인
docker-compose run --rm backend alembic history

# 현재 버전 확인
docker-compose run --rm backend alembic current

# 마이그레이션 재실행
docker-compose down -v
docker-compose up -d postgres
sleep 10
docker-compose run --rm backend alembic upgrade head
```

### OCR 실패
```bash
# Tesseract 설치 확인
docker-compose exec backend tesseract --version

# 환경 변수 확인
docker-compose exec backend env | grep OCR

# API 키 확인
docker-compose exec backend env | grep -E '(OPENAI|GOOGLE|MISTRAL)_API_KEY'
```

## 성능 테스트

### 동시 요청 테스트
```bash
# Apache Bench 사용
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/projects

# 또는 wrk 사용
wrk -t 4 -c 10 -d 30s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/projects
```

### 데이터베이스 성능
```bash
# 쿼리 실행 계획
docker-compose exec postgres psql -U sme_admin -d sme_evaluation -c "
EXPLAIN ANALYZE
SELECT * FROM evaluations
WHERE project_id = '...' AND is_submitted = true;
"
```

## 정리

### 서비스 중지
```bash
docker-compose down
```

### 데이터 완전 삭제
```bash
docker-compose down -v
docker volume prune -f
```

### 로그 정리
```bash
docker-compose logs > system_logs_$(date +%Y%m%d_%H%M%S).txt
```

## 다음 단계

1. ✅ 기본 통합 테스트 완료
2. ⏭️ 프론트엔드 연동 테스트
3. ⏭️ 실제 OCR 이미지 테스트
4. ⏭️ 부하 테스트 및 최적화
5. ⏭️ 보안 테스트 (OWASP Top 10)
6. ⏭️ 사용자 수용 테스트 (UAT)

## 참고 문서

- **API 테스트 샘플**: `API_TEST_SAMPLES.md`
- **OCR 테스트**: `backend/tests/test_ocr/README.md`
- **보안 표준**: `.claude/skills/biz-support-eval-dev/references/security_standard.md`
- **평가 가이드라인**: `.claude/skills/biz-support-eval-dev/references/eval_guidelines.md`
