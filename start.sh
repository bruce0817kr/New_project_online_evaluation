#!/bin/bash

# 중소기업 선정평가 시스템 시작 스크립트
# 전체 시스템 초기화 및 실행

set -e

echo "🚀 중소기업 선정평가 시스템 시작..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 환경 변수 파일 확인
echo "📋 1. 환경 변수 확인..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 파일이 없습니다. .env.example에서 복사합니다...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env 파일 생성 완료${NC}"
    echo -e "${YELLOW}⚠️  .env 파일을 열어 필요한 설정을 변경하세요${NC}"
fi
echo ""

# 2. Docker 이미지 빌드
echo "🔨 2. Docker 이미지 빌드..."
docker-compose build --no-cache
echo -e "${GREEN}✅ Docker 이미지 빌드 완료${NC}"
echo ""

# 3. 기존 컨테이너 정리
echo "🧹 3. 기존 컨테이너 정리..."
docker-compose down -v
echo -e "${GREEN}✅ 컨테이너 정리 완료${NC}"
echo ""

# 4. PostgreSQL 시작
echo "🗄️  4. PostgreSQL 시작..."
docker-compose up -d postgres
echo "   데이터베이스 준비 중..."
sleep 10
echo -e "${GREEN}✅ PostgreSQL 시작 완료${NC}"
echo ""

# 5. 데이터베이스 마이그레이션
echo "📦 5. 데이터베이스 마이그레이션..."
docker-compose exec -T postgres psql -U sme_admin -d sme_evaluation <<-EOSQL
    -- Check if tables exist
    SELECT table_name FROM information_schema.tables
    WHERE table_schema = 'public';
EOSQL

# Alembic 마이그레이션 실행
docker-compose run --rm backend alembic upgrade head || {
    echo -e "${YELLOW}⚠️  Alembic 마이그레이션 실패. SQL 직접 실행...${NC}"
    docker-compose exec -T postgres psql -U sme_admin -d sme_evaluation < backend/migrations/versions/2026_01_10_0000-initial_schema.py
}
echo -e "${GREEN}✅ 마이그레이션 완료${NC}"
echo ""

# 6. 초기 데이터 삽입
echo "🌱 6. 초기 데이터 삽입..."
docker-compose run --rm backend python migrations/seed_data.py
echo -e "${GREEN}✅ 초기 데이터 삽입 완료${NC}"
echo ""

# 7. 전체 서비스 시작
echo "🎬 7. 전체 서비스 시작..."
docker-compose up -d
echo -e "${GREEN}✅ 모든 서비스 시작 완료${NC}"
echo ""

# 8. 서비스 상태 확인
echo "🔍 8. 서비스 상태 확인..."
sleep 5
docker-compose ps
echo ""

# 9. 완료 메시지
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ 시스템 시작 완료!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 접속 정보:"
echo "   🌐 Frontend:  http://localhost:3000"
echo "   🔧 Backend API: http://localhost:8000"
echo "   📚 API Docs:  http://localhost:8000/api/docs"
echo "   🗄️  Database:  localhost:5432"
echo ""
echo "🔑 로그인 계정:"
echo "   관리자:"
echo "      Username: admin"
echo "      Password: Admin123!"
echo ""
echo "   심사위원:"
echo "      Username: evaluator1~5"
echo "      Password: Eval123!"
echo ""
echo "📋 유용한 명령어:"
echo "   로그 확인:        docker-compose logs -f"
echo "   특정 서비스 로그:  docker-compose logs -f backend"
echo "   서비스 중지:      docker-compose down"
echo "   완전 삭제:        docker-compose down -v"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
