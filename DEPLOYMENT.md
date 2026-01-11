# 배포 가이드 (Deployment Guide)

중소기업 선정평가 시스템의 프로덕션 배포 가이드입니다.

## 📋 목차

1. [사전 준비](#사전-준비)
2. [환경 설정](#환경-설정)
3. [데이터베이스 마이그레이션](#데이터베이스-마이그레이션)
4. [Docker 배포](#docker-배포)
5. [수동 배포](#수동-배포)
6. [모니터링 및 유지보수](#모니터링-및-유지보수)

---

## 사전 준비

### 시스템 요구사항

**최소 사양**:
- CPU: 2 Core
- RAM: 4GB
- Disk: 20GB SSD
- OS: Ubuntu 20.04 LTS 이상 / CentOS 8 이상

**권장 사양**:
- CPU: 4 Core
- RAM: 8GB
- Disk: 50GB SSD
- OS: Ubuntu 22.04 LTS

### 필수 소프트웨어

```bash
# Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Git
sudo apt update
sudo apt install -y git

# (선택) PostgreSQL Client
sudo apt install -y postgresql-client
```

---

## 환경 설정

### 1. 프로젝트 클론

```bash
git clone https://github.com/bruce0817kr/New_project_online_evaluation.git
cd New_project_online_evaluation
git checkout main  # 또는 배포할 브랜치
```

### 2. 환경 변수 설정

**Backend 환경 변수**:

```bash
# backend/.env.production
cat > backend/.env <<EOF
# 데이터베이스
DATABASE_URL=postgresql://sme_admin:CHANGE_THIS_PASSWORD@postgres:5432/sme_evaluation

# JWT 보안
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# 파일 업로드
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE=52428800

# OCR 설정
OCR_LANGUAGE=kor+eng
OCR_CONFIG=--psm 6 --oem 3
OCR_FALLBACK_STRATEGY=on_low_confidence
OCR_CONFIDENCE_THRESHOLD=0.85
OCR_ENABLE_ENSEMBLE=false

# AI Vision API (선택)
OPENAI_API_KEY=
GOOGLE_API_KEY=
MISTRAL_API_KEY=
EOF
```

**Frontend 환경 변수**:

```bash
# frontend/.env.production
cat > frontend/.env.production <<EOF
REACT_APP_API_URL=https://api.yourdomain.com/api/v1
REACT_APP_ENV=production
EOF
```

**Docker Compose 환경 변수**:

```bash
# .env
cat > .env <<EOF
# 데이터베이스
DB_PASSWORD=CHANGE_THIS_STRONG_PASSWORD

# JWT
SECRET_KEY=$(openssl rand -hex 32)

# Frontend API URL
REACT_APP_API_URL=https://api.yourdomain.com/api/v1

# OCR
OCR_FALLBACK_STRATEGY=on_low_confidence
OCR_CONFIDENCE_THRESHOLD=0.85
OCR_ENABLE_ENSEMBLE=false

# AI API Keys (선택)
OPENAI_API_KEY=
GOOGLE_API_KEY=
MISTRAL_API_KEY=
EOF
```

### 3. SSL/TLS 인증서 설정

**Let's Encrypt 사용 (권장)**:

```bash
# Certbot 설치
sudo apt install -y certbot python3-certbot-nginx

# 인증서 발급
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# 인증서 복사
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
```

**자체 서명 인증서 (개발/테스트용)**:

```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=KR/ST=Seoul/L=Seoul/O=Organization/CN=yourdomain.com"
```

---

## 데이터베이스 마이그레이션

### 1. 데이터베이스 백업 (기존 시스템)

```bash
# PostgreSQL 전체 백업
pg_dump -U sme_admin -h localhost sme_evaluation > backup_$(date +%Y%m%d_%H%M%S).sql

# 특정 테이블만 백업
pg_dump -U sme_admin -t evaluations -t projects sme_evaluation > backup_critical_tables.sql
```

### 2. 마이그레이션 실행

**Docker 환경**:

```bash
# 1. PostgreSQL 컨테이너 시작
docker-compose up -d postgres

# 2. 마이그레이션 실행
docker-compose exec backend python create_tables.py

# 또는 SQL 파일 직접 실행
docker-compose exec postgres psql -U sme_admin -d sme_evaluation -f /app/migrations/001_add_scoring_templates_and_metadata.sql
```

**수동 환경**:

```bash
cd backend
python3 create_tables.py

# 또는
psql -U sme_admin -d sme_evaluation -f migrations/001_add_scoring_templates_and_metadata.sql
```

### 3. 마이그레이션 검증

```sql
-- 테이블 확인
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- 새 컬럼 확인
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name IN ('evaluations', 'projects', 'scoring_templates', 'score_history')
ORDER BY table_name, ordinal_position;
```

---

## Docker 배포

### 1. 프로덕션 빌드

```bash
# 이미지 빌드
docker-compose -f docker-compose.prod.yml build

# 의존성 업데이트 확인
docker-compose -f docker-compose.prod.yml run --rm backend pip list --outdated
docker-compose -f docker-compose.prod.yml run --rm frontend npm outdated
```

### 2. 컨테이너 시작

```bash
# 전체 스택 시작
docker-compose -f docker-compose.prod.yml up -d

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f

# 특정 서비스 로그
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 3. 헬스 체크

```bash
# 데이터베이스
docker-compose exec postgres pg_isready -U sme_admin

# Backend API
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000/health

# Nginx
curl http://localhost/health
```

### 4. 초기 관리자 계정 생성

```bash
# Backend 컨테이너 접속
docker-compose exec backend bash

# Python 스크립트 실행
python -c "
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password
import uuid

db = SessionLocal()
admin = User(
    id=uuid.uuid4(),
    username='admin',
    email='admin@yourdomain.com',
    hashed_password=hash_password('ChangeThisPassword123!'),
    full_name='관리자',
    role='admin'
)
db.add(admin)
db.commit()
print('관리자 계정 생성 완료')
"
```

---

## 수동 배포

### Backend (FastAPI)

```bash
cd backend

# 1. 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 마이그레이션 실행
python create_tables.py

# 4. Gunicorn으로 실행 (프로덕션)
pip install gunicorn
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile /var/log/sme_eval/access.log \
  --error-logfile /var/log/sme_eval/error.log \
  --daemon
```

### Frontend (React)

```bash
cd frontend

# 1. 의존성 설치
npm ci --production

# 2. 프로덕션 빌드
npm run build

# 3. Nginx로 서빙 (build 디렉토리를 Nginx root로 설정)
sudo cp -r build/* /var/www/html/
```

### Systemd 서비스 등록

**Backend Service**:

```bash
sudo tee /etc/systemd/system/sme-backend.service > /dev/null <<EOF
[Unit]
Description=SME Evaluation Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/sme_evaluation/backend
Environment="PATH=/opt/sme_evaluation/backend/venv/bin"
ExecStart=/opt/sme_evaluation/backend/venv/bin/gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 서비스 시작
sudo systemctl daemon-reload
sudo systemctl enable sme-backend
sudo systemctl start sme-backend
sudo systemctl status sme-backend
```

---

## 모니터링 및 유지보수

### 1. 로그 관리

```bash
# Docker 로그
docker-compose logs -f --tail=100 backend

# 수동 배포 로그
tail -f /var/log/sme_eval/access.log
tail -f /var/log/sme_eval/error.log

# 로그 로테이션 설정
sudo tee /etc/logrotate.d/sme-eval > /dev/null <<EOF
/var/log/sme_eval/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 640 www-data www-data
    sharedscripts
}
EOF
```

### 2. 백업 자동화

```bash
# 백업 스크립트 생성
sudo tee /usr/local/bin/sme-backup.sh > /dev/null <<'EOF'
#!/bin/bash
BACKUP_DIR="/backups/sme_evaluation"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 데이터베이스 백업
docker-compose exec -T postgres pg_dump -U sme_admin sme_evaluation | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# 업로드 파일 백업
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" -C /opt/sme_evaluation/backend uploads/

# 7일 이상 된 백업 삭제
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

sudo chmod +x /usr/local/bin/sme-backup.sh

# Cron 등록 (매일 새벽 3시)
(crontab -l 2>/dev/null; echo "0 3 * * * /usr/local/bin/sme-backup.sh >> /var/log/sme-backup.log 2>&1") | crontab -
```

### 3. 모니터링

**Prometheus + Grafana (권장)**:

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  prometheus_data:
  grafana_data:
```

### 4. 업데이트

```bash
# 1. 최신 코드 가져오기
git pull origin main

# 2. 데이터베이스 백업
./usr/local/bin/sme-backup.sh

# 3. 컨테이너 재시작
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 4. 헬스 체크
curl http://localhost:8000/health
```

---

## 문제 해결

### PostgreSQL 연결 실패

```bash
# 컨테이너 로그 확인
docker-compose logs postgres

# 포트 확인
netstat -tulpn | grep 5432

# 연결 테스트
docker-compose exec postgres psql -U sme_admin -d sme_evaluation -c "SELECT version();"
```

### Nginx 502 Bad Gateway

```bash
# Backend 상태 확인
docker-compose ps backend
curl http://localhost:8000/health

# Nginx 설정 테스트
docker-compose exec nginx nginx -t

# 로그 확인
docker-compose logs nginx
```

### 디스크 공간 부족

```bash
# Docker 정리
docker system prune -a --volumes

# 로그 크기 확인
du -sh /var/log/sme_eval/
du -sh /opt/sme_evaluation/backend/uploads/

# 오래된 업로드 파일 정리 (예: 1년 이상)
find /opt/sme_evaluation/backend/uploads -type f -mtime +365 -delete
```

---

## 보안 체크리스트

배포 전 확인 사항:

- [ ] `.env` 파일의 모든 비밀번호 변경
- [ ] `SECRET_KEY` 강력한 값으로 설정
- [ ] HTTPS/TLS 인증서 설정
- [ ] 방화벽 설정 (80, 443, 22만 허용)
- [ ] PostgreSQL 외부 접근 차단
- [ ] 관리자 계정 비밀번호 변경
- [ ] CORS allowed_origins 프로덕션 도메인으로 설정
- [ ] 백업 자동화 설정
- [ ] 모니터링 설정
- [ ] 로그 로테이션 설정

---

**마지막 업데이트**: 2026-01-11
**버전**: 1.0.0

문의: admin@yourdomain.com
