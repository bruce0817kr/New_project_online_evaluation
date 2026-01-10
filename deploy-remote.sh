#!/bin/bash
# VM 자동 배포 스크립트

HOST="20.196.83.145"
USER="admin_gtp"

echo "🚀 중소기업 평가 시스템 자동 배포 시작..."
echo ""

# 1. 시스템 업데이트
echo "📦 1/8 시스템 업데이트..."
sudo apt-get update -qq && sudo apt-get upgrade -y -qq

# 2. Docker 설치 확인
echo "🐳 2/8 Docker 설치..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# 3. Docker Compose 설치
echo "🔧 3/8 Docker Compose 설치..."
if ! docker compose version &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 4. Git 설치
echo "📥 4/8 Git 설치..."
if ! command -v git &> /dev/null; then
    sudo apt-get install -y git
fi

# 5. 프로젝트 클론
echo "📂 5/8 프로젝트 클론..."
cd /home/$USER
if [ -d "New_project_online_evaluation" ]; then
    echo "기존 프로젝트가 있습니다. 업데이트합니다..."
    cd New_project_online_evaluation
    git pull
else
    git clone https://github.com/bruce0817kr/New_project_online_evaluation.git
    cd New_project_online_evaluation
fi

# 6. 환경 설정
echo "⚙️  6/8 환경 설정..."
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env

    # SECRET_KEY 자동 생성
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/your-super-secret-key-min-32-chars/${SECRET_KEY}/" backend/.env

    # DB_PASSWORD 자동 생성
    DB_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-20)
    sed -i "s/sme_secure_pass_2024/${DB_PASSWORD}/" backend/.env

    echo "✅ 환경 설정 완료"
fi

# 7. 권한 설정
echo "🔐 7/8 권한 설정..."
chmod +x start.sh

# 8. 시스템 시작
echo "🚀 8/8 시스템 시작..."
./start.sh

echo ""
echo "============================================================================"
echo "✅ 배포 완료!"
echo "============================================================================"
echo ""
echo "📍 접속 정보:"
echo "   Frontend: http://20.196.83.145:3000"
echo "   Backend API: http://20.196.83.145:8000"
echo "   API Docs: http://20.196.83.145:8000/api/docs"
echo ""
echo "🔑 테스트 계정:"
echo "   관리자: admin / Admin123!"
echo "   심사위원: evaluator1 / Eval123!"
echo ""
echo "============================================================================"
