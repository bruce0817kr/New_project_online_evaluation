#!/bin/bash

# ============================================================================
# Azure VM 자동 설정 스크립트
# 중소기업 선정평가 시스템 - Azure VM 배포 자동화
# ============================================================================

set -e  # 에러 발생 시 즉시 중단

echo "🚀 Azure VM 환경 설정을 시작합니다..."
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 시스템 업데이트
echo -e "${YELLOW}📦 1/7 시스템 패키지 업데이트...${NC}"
sudo apt-get update -qq
sudo apt-get upgrade -y -qq
echo -e "${GREEN}✅ 시스템 업데이트 완료${NC}"
echo ""

# 2. Docker 설치 확인 및 설치
echo -e "${YELLOW}🐳 2/7 Docker 설치 확인...${NC}"
if ! command -v docker &> /dev/null; then
    echo "Docker가 설치되어 있지 않습니다. 설치를 시작합니다..."

    # Docker 공식 GPG 키 추가
    sudo apt-get install -y ca-certificates curl gnupg lsb-release
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Docker 저장소 추가
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Docker 설치
    sudo apt-get update -qq
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # 현재 사용자를 docker 그룹에 추가
    sudo usermod -aG docker $USER

    echo -e "${GREEN}✅ Docker 설치 완료${NC}"
else
    echo -e "${GREEN}✅ Docker가 이미 설치되어 있습니다: $(docker --version)${NC}"
fi
echo ""

# 3. Docker Compose 설치 확인
echo -e "${YELLOW}🔧 3/7 Docker Compose 설치 확인...${NC}"
if ! docker compose version &> /dev/null; then
    echo "Docker Compose를 설치합니다..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose 설치 완료${NC}"
else
    echo -e "${GREEN}✅ Docker Compose가 이미 설치되어 있습니다${NC}"
fi
echo ""

# 4. Git 설치 확인
echo -e "${YELLOW}📥 4/7 Git 설치 확인...${NC}"
if ! command -v git &> /dev/null; then
    sudo apt-get install -y git
    echo -e "${GREEN}✅ Git 설치 완료${NC}"
else
    echo -e "${GREEN}✅ Git이 이미 설치되어 있습니다: $(git --version)${NC}"
fi
echo ""

# 5. 방화벽 설정 (UFW)
echo -e "${YELLOW}🔒 5/7 방화벽 설정...${NC}"
if command -v ufw &> /dev/null; then
    sudo ufw --force enable
    sudo ufw allow 22/tcp    # SSH
    sudo ufw allow 80/tcp    # HTTP
    sudo ufw allow 443/tcp   # HTTPS
    sudo ufw allow 3000/tcp  # Frontend (개발용)
    sudo ufw allow 8000/tcp  # Backend API (개발용)
    echo -e "${GREEN}✅ 방화벽 설정 완료${NC}"
else
    echo -e "${YELLOW}⚠️  UFW가 설치되어 있지 않습니다. 건너뜁니다.${NC}"
fi
echo ""

# 6. 프로젝트 디렉토리로 이동 또는 생성
echo -e "${YELLOW}📂 6/7 프로젝트 설정...${NC}"

# 현재 디렉토리가 프로젝트 루트인지 확인
if [ -f "start.sh" ] && [ -f "docker-compose.yml" ]; then
    echo -e "${GREEN}✅ 현재 디렉토리가 프로젝트 루트입니다${NC}"
    PROJECT_DIR=$(pwd)
else
    echo -e "${YELLOW}⚠️  프로젝트를 클론해야 합니다${NC}"
    read -p "Git 저장소 URL을 입력하세요 (Enter로 건너뛰기): " REPO_URL

    if [ -n "$REPO_URL" ]; then
        PROJECT_DIR="$HOME/sme-evaluation-system"
        if [ -d "$PROJECT_DIR" ]; then
            echo "기존 프로젝트 디렉토리가 있습니다. 업데이트합니다..."
            cd "$PROJECT_DIR"
            git pull
        else
            git clone "$REPO_URL" "$PROJECT_DIR"
            cd "$PROJECT_DIR"
        fi
        echo -e "${GREEN}✅ 프로젝트 준비 완료${NC}"
    else
        echo -e "${RED}❌ 프로젝트 디렉토리를 찾을 수 없습니다${NC}"
        echo "이 스크립트를 프로젝트 루트에서 실행하거나 Git URL을 제공하세요"
        exit 1
    fi
fi
echo ""

# 7. 환경 설정 파일 생성
echo -e "${YELLOW}⚙️  7/7 환경 설정 파일 생성...${NC}"

if [ ! -f "backend/.env" ]; then
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo -e "${GREEN}✅ .env 파일 생성 완료${NC}"
        echo -e "${YELLOW}⚠️  중요: backend/.env 파일을 편집하여 다음 항목을 설정하세요:${NC}"
        echo "   - SECRET_KEY (32자 이상 무작위 문자열)"
        echo "   - DB_PASSWORD (강력한 비밀번호)"
        echo "   - OPENAI_API_KEY (선택사항)"
        echo "   - GOOGLE_API_KEY (선택사항)"
        echo "   - MISTRAL_API_KEY (선택사항)"
        echo ""

        # SECRET_KEY 자동 생성
        SECRET_KEY=$(openssl rand -hex 32)
        sed -i "s/your-super-secret-key-min-32-chars/${SECRET_KEY}/" backend/.env
        echo -e "${GREEN}✅ SECRET_KEY 자동 생성 완료${NC}"

        # DB_PASSWORD 자동 생성
        DB_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-20)
        sed -i "s/sme_secure_pass_2024/${DB_PASSWORD}/" backend/.env
        echo -e "${GREEN}✅ DB_PASSWORD 자동 생성 완료${NC}"
    else
        echo -e "${RED}❌ .env.example 파일을 찾을 수 없습니다${NC}"
    fi
else
    echo -e "${GREEN}✅ .env 파일이 이미 존재합니다${NC}"
fi
echo ""

# VM 공인 IP 주소 확인
echo -e "${YELLOW}🌐 네트워크 정보 확인...${NC}"
PUBLIC_IP=$(curl -s ifconfig.me || echo "알 수 없음")
PRIVATE_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "============================================================================"
echo -e "${GREEN}🎉 Azure VM 설정이 완료되었습니다!${NC}"
echo "============================================================================"
echo ""
echo "📍 네트워크 정보:"
echo "   공인 IP: $PUBLIC_IP"
echo "   사설 IP: $PRIVATE_IP"
echo ""
echo "🚀 다음 단계:"
echo ""
echo "1. 환경 설정 파일 확인 및 수정:"
echo "   nano backend/.env"
echo ""
echo "2. 시스템 시작:"
echo "   chmod +x start.sh"
echo "   ./start.sh"
echo ""
echo "3. 서비스 접속:"
echo "   Frontend: http://$PUBLIC_IP:3000"
echo "   Backend API: http://$PUBLIC_IP:8000"
echo "   API Docs: http://$PUBLIC_IP:8000/api/docs"
echo ""
echo "4. 테스트 계정:"
echo "   관리자: admin / Admin123!"
echo "   심사위원: evaluator1 / Eval123!"
echo ""
echo "============================================================================"
echo ""
echo -e "${YELLOW}⚠️  주의사항:${NC}"
echo "- Azure Portal에서 네트워크 보안 그룹 인바운드 규칙을 설정하세요"
echo "  (포트 80, 443, 3000, 8000 허용)"
echo "- Docker 그룹 권한 적용을 위해 재로그인이 필요할 수 있습니다"
echo "- 프로덕션 환경에서는 HTTPS 설정을 권장합니다"
echo ""
echo "============================================================================"
echo ""

# Docker 그룹 확인
if groups | grep -q docker; then
    echo -e "${GREEN}✅ Docker 그룹 권한이 이미 적용되어 있습니다${NC}"
else
    echo -e "${YELLOW}⚠️  Docker 그룹 권한을 적용하려면 다음 명령을 실행하세요:${NC}"
    echo "   newgrp docker"
    echo "   또는 SSH를 다시 접속하세요"
fi

echo ""
echo "설정 완료! 🎯"
