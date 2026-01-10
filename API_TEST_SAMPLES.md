# API 테스트 샘플 (cURL)

## 개요

이 문서는 모든 API 엔드포인트의 테스트 샘플을 제공합니다.

## 기본 설정

```bash
# API Base URL
BASE_URL="http://localhost:8000/api/v1"

# jq 설치 (JSON 파싱용)
# Ubuntu/Debian: sudo apt-get install jq
# macOS: brew install jq
```

---

## 1. 인증 (Authentication)

### 1.1 로그인

```bash
# 관리자 로그인
curl -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=Admin123!" | jq

# 심사위원 로그인
curl -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=evaluator1&password=Eval123!" | jq
```

**응답 예시**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "...",
    "username": "admin",
    "email": "admin@sme-eval.com",
    "full_name": "시스템 관리자",
    "role": "admin"
  }
}
```

**토큰 저장**:
```bash
# 관리자 토큰
ADMIN_TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=Admin123!" | jq -r .access_token)

# 심사위원 토큰
EVAL_TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=evaluator1&password=Eval123!" | jq -r .access_token)

echo "Admin Token: $ADMIN_TOKEN"
echo "Evaluator Token: $EVAL_TOKEN"
```

### 1.2 현재 사용자 정보

```bash
curl -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
```

**응답 예시**:
```json
{
  "id": "...",
  "username": "admin",
  "email": "admin@sme-eval.com",
  "full_name": "시스템 관리자",
  "role": "admin",
  "is_active": true,
  "created_at": "2026-01-10T00:00:00Z"
}
```

### 1.3 회원가입

```bash
curl -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "username": "evaluator6",
    "email": "evaluator6@example.com",
    "password": "Eval123!",
    "full_name": "심사위원6",
    "role": "evaluator"
  }' | jq
```

### 1.4 비밀번호 변경

```bash
curl -X POST "$BASE_URL/auth/change-password" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $EVAL_TOKEN" \
  -d '{
    "current_password": "Eval123!",
    "new_password": "NewPassword123!"
  }' | jq
```

### 1.5 로그아웃

```bash
curl -X POST "$BASE_URL/auth/logout" \
  -H "Authorization: Bearer $EVAL_TOKEN" | jq
```

---

## 2. OCR (문서 인식)

### 2.1 사용 가능한 엔진 조회

```bash
curl -X GET "$BASE_URL/ocr/engines" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
```

**응답 예시**:
```json
{
  "engines": ["tesseract", "openai", "gemini", "mistral"],
  "fallback_strategy": "on_low_confidence",
  "confidence_threshold": 0.85,
  "ensemble_mode": false
}
```

### 2.2 문서 분석 (Tesseract)

```bash
# 테스트 이미지 준비
# test_data/business_license.jpg 파일이 있다고 가정

curl -X POST "$BASE_URL/ocr/analyze" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@test_data/business_license.jpg" \
  -F "document_type=사업자등록증" | jq
```

**응답 예시**:
```json
{
  "success": true,
  "engine": "tesseract",
  "document_type": "사업자등록증",
  "extracted_data": {
    "사업자등록번호": "123-45-67890",
    "상호": "(주)테크이노베이션",
    "대표자": "홍길동",
    "개업연월일": "2020년 1월 15일",
    "사업장소재지": "서울특별시 강남구 테헤란로 123"
  },
  "confidence_score": 0.92,
  "needs_manual_verification": false,
  "processing_time_ms": 150.5,
  "raw_text": "사업자등록증\n사업자등록번호: 123-45-67890\n상호: (주)테크이노베이션...",
  "errors": []
}
```

### 2.3 문서 분석 (OpenAI 지정)

```bash
curl -X POST "$BASE_URL/ocr/analyze" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@test_data/business_license.jpg" \
  -F "document_type=사업자등록증" \
  -F "preferred_engine=openai" | jq
```

### 2.4 문서 분석 (법인등기부등본)

```bash
curl -X POST "$BASE_URL/ocr/analyze" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@test_data/corporate_registry.jpg" \
  -F "document_type=법인등기부등본" | jq
```

### 2.5 간단한 텍스트 추출

```bash
curl -X POST "$BASE_URL/ocr/extract-text" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@test_data/document.jpg" | jq
```

**응답 예시**:
```json
{
  "success": true,
  "text": "추출된 텍스트 내용입니다...",
  "engine": "tesseract"
}
```

### 2.6 잘못된 파일 형식 (오류 테스트)

```bash
# .txt 파일 업로드 (실패해야 함)
echo "test" > test.txt
curl -X POST "$BASE_URL/ocr/analyze" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@test.txt" \
  -F "document_type=사업자등록증" | jq

# 예상: 400 Bad Request
rm test.txt
```

---

## 3. 프로젝트 (Projects)

### 3.1 프로젝트 목록 조회

```bash
curl -X GET "$BASE_URL/projects" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
```

**응답 예시**:
```json
[
  {
    "id": "...",
    "name": "2026년 스마트제조 혁신기술 지원사업",
    "description": "중소 제조기업의 스마트 제조 기술 도입 지원",
    "year": 2026,
    "status": "active",
    "start_date": "2026-01-01",
    "end_date": "2026-12-31",
    "total_budget": 5000000000.0,
    "created_at": "2026-01-10T00:00:00Z"
  }
]
```

**프로젝트 ID 저장**:
```bash
PROJECT_ID=$(curl -s -X GET "$BASE_URL/projects" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r .[0].id)

echo "Project ID: $PROJECT_ID"
```

### 3.2 프로젝트 상세 조회

```bash
curl -X GET "$BASE_URL/projects/$PROJECT_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
```

### 3.3 프로젝트 생성

```bash
curl -X POST "$BASE_URL/projects" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "2026년 AI 기술 혁신 지원사업",
    "description": "인공지능 기술 도입 및 활용 지원",
    "year": 2026,
    "start_date": "2026-03-01",
    "end_date": "2026-12-31",
    "total_budget": 3000000000.0,
    "evaluation_criteria": {
      "기술성": 40,
      "사업성": 30,
      "경제성": 30
    }
  }' | jq
```

### 3.4 프로젝트 수정

```bash
curl -X PUT "$BASE_URL/projects/$PROJECT_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "중소 제조기업의 디지털 전환 지원 (수정됨)",
    "total_budget": 6000000000.0
  }' | jq
```

### 3.5 프로젝트에 속한 기업 목록

```bash
curl -X GET "$BASE_URL/projects/$PROJECT_ID/companies" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
```

---

## 4. 기업 (Companies)

### 4.1 기업 목록 조회

```bash
curl -X GET "$BASE_URL/companies" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
```

**기업 ID 저장**:
```bash
COMPANY_ID=$(curl -s -X GET "$BASE_URL/companies" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r .[0].id)

echo "Company ID: $COMPANY_ID"
```

### 4.2 기업 상세 조회

```bash
curl -X GET "$BASE_URL/companies/$COMPANY_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
```

### 4.3 기업 등록 (OCR 데이터 포함)

```bash
curl -X POST "$BASE_URL/companies" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "'"$PROJECT_ID"'",
    "name": "(주)뉴테크솔루션",
    "business_number": "234-56-78901",
    "ceo_name": "김철수",
    "established_date": "2021-05-10",
    "address": "경기도 성남시 분당구 판교로 256",
    "industry": "소프트웨어 개발",
    "employee_count": 25,
    "ocr_data": {
      "사업자등록번호": "234-56-78901",
      "상호": "(주)뉴테크솔루션",
      "대표자": "김철수"
    },
    "ocr_confidence": 0.95,
    "ocr_engine": "openai"
  }' | jq
```

### 4.4 기업 정보 수정

```bash
curl -X PUT "$BASE_URL/companies/$COMPANY_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_count": 30,
    "address": "경기도 성남시 분당구 판교로 256 (수정됨)"
  }' | jq
```

---

## 5. 평가 (Evaluations)

### 5.1 내 평가 목록 (심사위원)

```bash
# 전체
curl -X GET "$BASE_URL/evaluations/my" \
  -H "Authorization: Bearer $EVAL_TOKEN" | jq

# 미제출만
curl -X GET "$BASE_URL/evaluations/my?status=in_progress" \
  -H "Authorization: Bearer $EVAL_TOKEN" | jq

# 제출 완료만
curl -X GET "$BASE_URL/evaluations/my?status=submitted" \
  -H "Authorization: Bearer $EVAL_TOKEN" | jq
```

**평가 ID 저장**:
```bash
EVAL_ID=$(curl -s -X GET "$BASE_URL/evaluations/my?status=in_progress" \
  -H "Authorization: Bearer $EVAL_TOKEN" | jq -r .[0].id)

echo "Evaluation ID: $EVAL_ID"
```

### 5.2 평가 상세 조회

```bash
curl -X GET "$BASE_URL/evaluations/$EVAL_ID" \
  -H "Authorization: Bearer $EVAL_TOKEN" | jq
```

### 5.3 평가 생성 (관리자)

```bash
curl -X POST "$BASE_URL/evaluations" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "'"$PROJECT_ID"'",
    "company_id": "'"$COMPANY_ID"'",
    "evaluator_id": "'"$(curl -s -X GET "$BASE_URL/auth/me" -H "Authorization: Bearer $EVAL_TOKEN" | jq -r .id)"'"
  }' | jq
```

### 5.4 평가 저장 (임시 저장)

```bash
curl -X PUT "$BASE_URL/evaluations/$EVAL_ID" \
  -H "Authorization: Bearer $EVAL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scores": {
      "기술성": 85.0,
      "사업성": 78.0,
      "경제성": 90.0
    },
    "comments": "기술력이 우수하며 사업화 가능성이 높음.\n다만 시장 진입 전략에 대한 보완이 필요함."
  }' | jq
```

**응답 예시**:
```json
{
  "id": "...",
  "project_id": "...",
  "company_id": "...",
  "evaluator_id": "...",
  "scores": {
    "기술성": 85.0,
    "사업성": 78.0,
    "경제성": 90.0
  },
  "comments": "기술력이 우수하며 사업화 가능성이 높음...",
  "is_submitted": false,
  "submitted_at": null,
  "updated_at": "2026-01-10T12:30:00Z"
}
```

### 5.5 평가 제출 (불변)

```bash
curl -X POST "$BASE_URL/evaluations/$EVAL_ID/submit" \
  -H "Authorization: Bearer $EVAL_TOKEN" | jq
```

**응답 예시**:
```json
{
  "id": "...",
  "is_submitted": true,
  "submitted_at": "2026-01-10T12:35:00Z",
  "message": "평가가 성공적으로 제출되었습니다. 더 이상 수정할 수 없습니다."
}
```

### 5.6 제출 후 수정 시도 (실패 테스트)

```bash
curl -X PUT "$BASE_URL/evaluations/$EVAL_ID" \
  -H "Authorization: Bearer $EVAL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scores": {
      "기술성": 95.0
    }
  }' | jq

# 예상: 400 Bad Request
# {"detail": "이미 제출된 평가는 수정할 수 없습니다"}
```

### 5.7 프로젝트별 평가 목록 (관리자)

```bash
curl -X GET "$BASE_URL/evaluations/project/$PROJECT_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
```

### 5.8 기업별 평가 목록 (관리자)

```bash
curl -X GET "$BASE_URL/evaluations/company/$COMPANY_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
```

---

## 6. 점수 집계 (Scores)

### 6.1 프로젝트 전체 집계

```bash
curl -X GET "$BASE_URL/scores/project/$PROJECT_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
```

**응답 예시**:
```json
{
  "project_id": "...",
  "project_name": "2026년 스마트제조 혁신기술 지원사업",
  "total_companies": 5,
  "evaluated_companies": 5,
  "company_scores": [
    {
      "company_id": "...",
      "company_name": "(주)테크이노베이션",
      "final_score": 82.27,
      "submitted_evaluations": 5,
      "total_evaluators": 5,
      "rank": 1
    },
    {
      "company_id": "...",
      "company_name": "(주)스마트솔루션",
      "final_score": 78.53,
      "submitted_evaluations": 5,
      "total_evaluators": 5,
      "rank": 2
    }
  ],
  "calculation_method": "trimmed_mean"
}
```

### 6.2 특정 기업 점수 상세

```bash
curl -X GET "$BASE_URL/scores/project/$PROJECT_ID/company/$COMPANY_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
```

**응답 예시**:
```json
{
  "project_id": "...",
  "company_id": "...",
  "company_name": "(주)테크이노베이션",
  "total_evaluators": 5,
  "submitted_count": 5,
  "aggregated_scores": {
    "기술성": 82.5,
    "사업성": 76.0,
    "경제성": 88.3
  },
  "final_score": 82.27,
  "calculation_method": "trimmed_mean",
  "individual_scores": [
    {
      "evaluator_id": "...",
      "evaluator_name": "심사위원1",
      "scores": {
        "기술성": 85.0,
        "사업성": 78.0,
        "경제성": 90.0
      },
      "submitted_at": "2026-01-10T10:00:00Z"
    },
    {
      "evaluator_id": "...",
      "evaluator_name": "심사위원2",
      "scores": {
        "기술성": 88.0,
        "사업성": 82.0,
        "경제성": 92.0
      },
      "submitted_at": "2026-01-10T11:00:00Z"
    },
    {
      "evaluator_id": "...",
      "evaluator_name": "심사위원3",
      "scores": {
        "기술성": 80.0,
        "사업성": 75.0,
        "경제성": 85.0
      },
      "submitted_at": "2026-01-10T12:00:00Z"
    },
    {
      "evaluator_id": "...",
      "evaluator_name": "심사위원4",
      "scores": {
        "기술성": 75.0,
        "사업성": 70.0,
        "경제성": 83.0
      },
      "submitted_at": "2026-01-10T13:00:00Z"
    },
    {
      "evaluator_id": "...",
      "evaluator_name": "심사위원5",
      "scores": {
        "기술성": 84.0,
        "사업성": 75.0,
        "경제성": 91.5
      },
      "submitted_at": "2026-01-10T14:00:00Z"
    }
  ],
  "calculation_details": {
    "기술성": {
      "raw_scores": [85.0, 88.0, 80.0, 75.0, 84.0],
      "sorted_scores": [75.0, 80.0, 84.0, 85.0, 88.0],
      "trimmed_scores": [80.0, 84.0, 85.0],
      "trimmed_mean": 82.5
    },
    "사업성": {
      "raw_scores": [78.0, 82.0, 75.0, 70.0, 75.0],
      "sorted_scores": [70.0, 75.0, 75.0, 78.0, 82.0],
      "trimmed_scores": [75.0, 75.0, 78.0],
      "trimmed_mean": 76.0
    },
    "경제성": {
      "raw_scores": [90.0, 92.0, 85.0, 83.0, 91.5],
      "sorted_scores": [83.0, 85.0, 90.0, 91.5, 92.0],
      "trimmed_scores": [85.0, 90.0, 91.5],
      "trimmed_mean": 88.3
    }
  }
}
```

---

## 7. 감사 로그 (Audit Logs) - 관리자 전용

### 7.1 전체 감사 로그 조회

```bash
curl -X GET "$BASE_URL/audit/logs?limit=50" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
```

### 7.2 사용자별 감사 로그

```bash
curl -X GET "$BASE_URL/audit/logs?username=evaluator1&limit=20" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
```

### 7.3 액션별 감사 로그

```bash
# 로그인 이벤트만
curl -X GET "$BASE_URL/audit/logs?action=LOGIN&limit=20" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

# 평가 제출 이벤트만
curl -X GET "$BASE_URL/audit/logs?action=SUBMIT_EVALUATION&limit=20" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
```

### 7.4 날짜 범위로 감사 로그 조회

```bash
curl -X GET "$BASE_URL/audit/logs?start_date=2026-01-01&end_date=2026-01-31" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
```

---

## 8. 헬스 체크

### 8.1 API 상태 확인

```bash
curl -X GET "http://localhost:8000/health" | jq
```

**응답 예시**:
```json
{
  "status": "ok",
  "timestamp": "2026-01-10T12:00:00Z",
  "version": "1.0.0"
}
```

### 8.2 데이터베이스 연결 확인

```bash
curl -X GET "http://localhost:8000/health/db" | jq
```

---

## 9. 통합 테스트 시나리오

### 시나리오 1: 완전한 평가 워크플로우

```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api/v1"

echo "=== 1. 관리자 로그인 ==="
ADMIN_TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=Admin123!" | jq -r .access_token)
echo "Token: $ADMIN_TOKEN"

echo -e "\n=== 2. 프로젝트 목록 조회 ==="
PROJECT_ID=$(curl -s -X GET "$BASE_URL/projects" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r .[0].id)
echo "Project ID: $PROJECT_ID"

echo -e "\n=== 3. 기업 목록 조회 ==="
COMPANY_ID=$(curl -s -X GET "$BASE_URL/projects/$PROJECT_ID/companies" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r .[0].id)
echo "Company ID: $COMPANY_ID"

echo -e "\n=== 4. 심사위원 로그인 ==="
EVAL_TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=evaluator1&password=Eval123!" | jq -r .access_token)
echo "Token: $EVAL_TOKEN"

echo -e "\n=== 5. 내 평가 목록 조회 ==="
EVAL_ID=$(curl -s -X GET "$BASE_URL/evaluations/my?status=in_progress" \
  -H "Authorization: Bearer $EVAL_TOKEN" | jq -r .[0].id)
echo "Evaluation ID: $EVAL_ID"

echo -e "\n=== 6. 평가 작성 ==="
curl -s -X PUT "$BASE_URL/evaluations/$EVAL_ID" \
  -H "Authorization: Bearer $EVAL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scores": {
      "기술성": 85.0,
      "사업성": 78.0,
      "경제성": 90.0
    },
    "comments": "우수한 기술력과 사업 계획"
  }' | jq

echo -e "\n=== 7. 평가 제출 ==="
curl -s -X POST "$BASE_URL/evaluations/$EVAL_ID/submit" \
  -H "Authorization: Bearer $EVAL_TOKEN" | jq

echo -e "\n=== 8. 점수 집계 확인 ==="
curl -s -X GET "$BASE_URL/scores/project/$PROJECT_ID/company/$COMPANY_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

echo -e "\n=== 완료 ==="
```

### 시나리오 2: OCR 처리 워크플로우

```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api/v1"

echo "=== 1. 관리자 로그인 ==="
ADMIN_TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=Admin123!" | jq -r .access_token)

echo -e "\n=== 2. OCR 엔진 목록 확인 ==="
curl -s -X GET "$BASE_URL/ocr/engines" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

echo -e "\n=== 3. Tesseract로 사업자등록증 분석 ==="
curl -s -X POST "$BASE_URL/ocr/analyze" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@test_data/business_license.jpg" \
  -F "document_type=사업자등록증" | jq > ocr_tesseract.json

echo -e "\n=== 4. OpenAI로 동일 문서 분석 (비교) ==="
curl -s -X POST "$BASE_URL/ocr/analyze" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@test_data/business_license.jpg" \
  -F "document_type=사업자등록증" \
  -F "preferred_engine=openai" | jq > ocr_openai.json

echo -e "\n=== 5. OCR 결과로 기업 등록 ==="
BUSINESS_NUMBER=$(jq -r '.extracted_data.사업자등록번호' ocr_tesseract.json)
COMPANY_NAME=$(jq -r '.extracted_data.상호' ocr_tesseract.json)
CEO_NAME=$(jq -r '.extracted_data.대표자' ocr_tesseract.json)

PROJECT_ID=$(curl -s -X GET "$BASE_URL/projects" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r .[0].id)

curl -s -X POST "$BASE_URL/companies" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "'"$PROJECT_ID"'",
    "name": "'"$COMPANY_NAME"'",
    "business_number": "'"$BUSINESS_NUMBER"'",
    "ceo_name": "'"$CEO_NAME"'",
    "ocr_data": '"$(jq -c '.extracted_data' ocr_tesseract.json)"',
    "ocr_confidence": '"$(jq -r '.confidence_score' ocr_tesseract.json)"',
    "ocr_engine": "tesseract"
  }' | jq

echo -e "\n=== 완료 ==="
```

---

## 10. 오류 테스트

### 10.1 인증 오류

```bash
# 토큰 없이 요청
curl -X GET "$BASE_URL/projects" | jq
# 예상: 401 Unauthorized

# 잘못된 토큰
curl -X GET "$BASE_URL/projects" \
  -H "Authorization: Bearer invalid-token" | jq
# 예상: 401 Unauthorized
```

### 10.2 권한 오류

```bash
# 심사위원이 관리자 API 호출
curl -X POST "$BASE_URL/projects" \
  -H "Authorization: Bearer $EVAL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "테스트 프로젝트"}' | jq
# 예상: 403 Forbidden
```

### 10.3 데이터 검증 오류

```bash
# 필수 필드 누락
curl -X POST "$BASE_URL/companies" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "테스트"}' | jq
# 예상: 422 Validation Error
```

---

## 참고

- **통합 테스트 가이드**: `INTEGRATION_TEST_GUIDE.md`
- **API 문서**: http://localhost:8000/api/docs
- **OCR 테스트**: `backend/tests/test_ocr/README.md`
