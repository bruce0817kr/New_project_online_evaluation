# Azure VM 배포 가이드

## 개요

이 가이드는 중소기업 선정평가 시스템을 Azure 가상 머신(VM)에 배포하는 전체 과정을 단계별로 설명합니다.

---

## 📋 사전 준비사항

### 필수
- Azure 계정 (무료 체험 가능: https://azure.microsoft.com/ko-kr/free/)
- SSH 클라이언트 (Windows: PuTTY 또는 Windows Terminal, Mac/Linux: 기본 터미널)

### 선택사항
- 도메인 이름 (프로덕션 환경)
- OCR API 키 (OpenAI, Google Cloud, Mistral)

---

## 1단계: Azure VM 생성

### Azure Portal에서 VM 생성

1. **Azure Portal 접속**: https://portal.azure.com

2. **가상 머신 만들기**:
   - 검색창에 "가상 머신" 입력
   - "만들기" → "Azure 가상 머신" 클릭

3. **기본 설정**:
   ```
   구독: (사용자의 Azure 구독)
   리소스 그룹: sme-evaluation-rg (새로 만들기)
   가상 머신 이름: sme-eval-vm
   지역: Korea Central (또는 가까운 지역)
   가용성 옵션: 인프라 중복이 필요하지 않음
   이미지: Ubuntu Server 22.04 LTS - x64 Gen2
   크기: Standard_B2s (2 vCPU, 4GB RAM) - 개발/테스트용
        Standard_B2ms (2 vCPU, 8GB RAM) - 프로덕션 권장
   ```

4. **관리자 계정**:
   ```
   인증 형식: SSH 공개 키 (권장) 또는 암호
   사용자 이름: azureuser
   SSH 공개 키 소스: 새 키 쌍 생성
   키 쌍 이름: sme-eval-vm_key
   ```

5. **인바운드 포트 규칙**:
   ```
   공용 인바운드 포트: 선택한 포트 허용
   인바운드 포트 선택:
     - SSH (22)
     - HTTP (80)
     - HTTPS (443)
   ```

6. **디스크 설정** (다음 탭):
   ```
   OS 디스크 유형: 프리미엄 SSD (권장) 또는 표준 SSD
   크기: 30GB 이상
   ```

7. **네트워킹** (다음 탭):
   ```
   가상 네트워크: (자동 생성)
   서브넷: (자동 생성)
   공용 IP: (자동 생성)
   NIC 네트워크 보안 그룹: 기본
   ```

8. **검토 + 만들기**:
   - 설정 확인 후 "만들기" 클릭
   - SSH 키 다운로드 (중요! 나중에 다시 받을 수 없음)

---

## 2단계: 네트워크 보안 그룹 설정

VM이 생성된 후, 추가 포트를 열어야 합니다:

1. **VM으로 이동**: Azure Portal에서 생성한 VM 선택

2. **네트워킹** 메뉴 클릭

3. **인바운드 포트 규칙 추가**:

   ### 포트 3000 (Frontend - 개발용)
   ```
   소스: Any
   원본 포트 범위: *
   대상: Any
   서비스: 사용자 지정
   대상 포트 범위: 3000
   프로토콜: TCP
   작업: 허용
   우선 순위: 310
   이름: Allow_Frontend_3000
   ```

   ### 포트 8000 (Backend API - 개발용)
   ```
   소스: Any
   원본 포트 범위: *
   대상: Any
   서비스: 사용자 지정
   대상 포트 범위: 8000
   프로토콜: TCP
   작업: 허용
   우선 순위: 320
   이름: Allow_Backend_8000
   ```

   **참고**: 프로덕션 환경에서는 3000, 8000 포트를 닫고 Nginx(80/443)만 사용하세요.

---

## 3단계: VM에 SSH 접속

### Windows (PowerShell 또는 Windows Terminal)

```powershell
# SSH 키 파일 위치로 이동
cd ~\Downloads

# 권한 설정 (처음 한 번만)
icacls sme-eval-vm_key.pem /inheritance:r
icacls sme-eval-vm_key.pem /grant:r "%username%:R"

# SSH 접속
ssh -i sme-eval-vm_key.pem azureuser@<VM-공인-IP>
```

### Mac/Linux

```bash
# SSH 키 파일 권한 설정
chmod 400 ~/Downloads/sme-eval-vm_key.pem

# SSH 접속
ssh -i ~/Downloads/sme-eval-vm_key.pem azureuser@<VM-공인-IP>
```

**VM 공인 IP 확인 방법**:
- Azure Portal → VM → "개요" 페이지에서 확인

---

## 4단계: 자동 설정 스크립트 실행

SSH 접속 후 다음 명령을 실행하세요:

### 방법 1: Git 저장소에서 직접 실행 (권장)

```bash
# 프로젝트 클론
git clone https://github.com/bruce0817kr/New_project_online_evaluation.git
cd New_project_online_evaluation

# 자동 설정 스크립트 실행
chmod +x azure-vm-setup.sh
./azure-vm-setup.sh
```

### 방법 2: 스크립트만 다운로드

```bash
# 스크립트 다운로드
curl -O https://raw.githubusercontent.com/bruce0817kr/New_project_online_evaluation/main/azure-vm-setup.sh

# 실행 권한 부여
chmod +x azure-vm-setup.sh

# 실행
./azure-vm-setup.sh
```

이 스크립트는 자동으로:
- ✅ 시스템 업데이트
- ✅ Docker 및 Docker Compose 설치
- ✅ Git 설치
- ✅ 방화벽 설정
- ✅ 환경 설정 파일 생성 (.env)
- ✅ SECRET_KEY 및 DB_PASSWORD 자동 생성

---

## 5단계: 환경 설정 (중요!)

자동 설정 후 환경 파일을 편집하세요:

```bash
nano backend/.env
```

### 필수 설정 항목

```bash
# 이미 자동 생성됨 (확인만)
SECRET_KEY=<자동생성된-32자-문자열>
DB_PASSWORD=<자동생성된-비밀번호>

# OCR API 키 추가 (선택사항)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
MISTRAL_API_KEY=...

# OCR 설정
OCR_FALLBACK_STRATEGY=on_low_confidence
OCR_CONFIDENCE_THRESHOLD=0.85
```

**저장**: `Ctrl + O` → `Enter` → `Ctrl + X`

---

## 6단계: 시스템 시작

```bash
# Docker 그룹 권한 적용 (필요 시)
newgrp docker

# 시스템 시작
chmod +x start.sh
./start.sh
```

시작 과정:
1. ✅ 환경 변수 확인
2. ✅ Docker 이미지 빌드
3. ✅ 기존 컨테이너 정리
4. ✅ PostgreSQL 시작
5. ✅ 데이터베이스 마이그레이션
6. ✅ 초기 데이터 삽입
7. ✅ 전체 서비스 시작
8. ✅ 서비스 상태 확인

---

## 7단계: 접속 및 테스트

### 서비스 접속 URL

```
Frontend:     http://<VM-공인-IP>:3000
Backend API:  http://<VM-공인-IP>:8000
API Docs:     http://<VM-공인-IP>:8000/api/docs
```

### 테스트 계정

```
관리자:
  ID: admin
  PW: Admin123!

심사위원:
  ID: evaluator1 (또는 evaluator2~5)
  PW: Eval123!
```

### API 테스트 (터미널에서)

```bash
# VM에서 직접 테스트
curl http://localhost:8000/health
# 응답: {"status":"ok"}

# 로그인 테스트
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=Admin123!"
```

---

## 8단계: 시스템 관리

### 서비스 상태 확인

```bash
# 컨테이너 상태
docker compose ps

# 로그 확인
docker compose logs -f backend
docker compose logs -f frontend

# 리소스 사용량
docker stats
```

### 서비스 재시작

```bash
# 전체 재시작
docker compose restart

# 특정 서비스만
docker compose restart backend
```

### 서비스 중지

```bash
docker compose down
```

### 서비스 완전 초기화

```bash
docker compose down -v  # 볼륨도 삭제
./start.sh              # 재시작
```

---

## 9단계: 프로덕션 배포 (선택사항)

### HTTPS 설정 (Let's Encrypt)

#### 1. 도메인 연결

Azure Portal에서 VM에 DNS 이름 할당:
- VM → "구성" → "DNS 이름 레이블" 설정
- 예: `sme-eval.koreacentral.cloudapp.azure.com`

또는 본인 소유 도메인의 A 레코드를 VM 공인 IP로 설정

#### 2. Certbot 설치

```bash
sudo apt install certbot python3-certbot-nginx
```

#### 3. Nginx 설정 수정

```bash
# Nginx 설정 파일 편집
sudo nano /etc/nginx/sites-available/sme-eval

# 다음 내용 추가
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/sme-eval /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. SSL 인증서 발급

```bash
sudo certbot --nginx -d your-domain.com
```

#### 5. 자동 갱신 설정

```bash
# Cron 작업 추가
sudo crontab -e

# 다음 줄 추가 (매일 자정에 갱신 확인)
0 0 * * * certbot renew --quiet
```

### 환경 변수 프로덕션 설정

```bash
nano backend/.env

# 다음 값 변경
DEBUG=false
ENVIRONMENT=production
ALLOWED_HOSTS=your-domain.com
CORS_ORIGINS=https://your-domain.com
```

---

## 10단계: 모니터링 및 백업

### 로그 관리

```bash
# 로그 파일 위치
docker compose logs > logs/$(date +%Y%m%d).log

# 로그 로테이션 설정
sudo nano /etc/logrotate.d/docker-compose
```

### 데이터베이스 백업

```bash
# 백업 스크립트 생성
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="$HOME/backups"
mkdir -p $BACKUP_DIR

# PostgreSQL 백업
docker compose exec -T postgres pg_dump -U sme_admin sme_evaluation > \
  $BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql

# 7일 이상 된 백업 삭제
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete
EOF

chmod +x backup.sh

# 매일 새벽 2시에 백업 (Cron)
crontab -e
# 추가: 0 2 * * * /home/azureuser/New_project_online_evaluation/backup.sh
```

### Azure Backup 설정 (권장)

Azure Portal에서:
1. VM → "백업" 메뉴
2. "백업 사용" 클릭
3. 일일 백업 정책 설정

---

## 트러블슈팅

### Docker 권한 오류

```bash
# Docker 그룹에 사용자 추가 확인
groups | grep docker

# 재로그인 필요 시
newgrp docker
# 또는 SSH 재접속
```

### 포트 접속 불가

```bash
# 방화벽 상태 확인
sudo ufw status

# Docker 컨테이너 상태 확인
docker compose ps

# Azure 네트워크 보안 그룹 확인
# Azure Portal → VM → 네트워킹
```

### 메모리 부족

```bash
# 현재 사용량 확인
free -h

# VM 크기 업그레이드 (Azure Portal)
# VM 중지 → 크기 변경 → Standard_B2ms 선택
```

### 데이터베이스 연결 오류

```bash
# PostgreSQL 로그 확인
docker compose logs postgres

# 컨테이너 재시작
docker compose restart postgres

# .env 파일의 DB_PASSWORD 확인
cat backend/.env | grep DB_PASSWORD
```

---

## 비용 절감 팁

### 개발/테스트 환경

1. **VM 자동 종료 설정**:
   - Azure Portal → VM → "자동 종료" 활성화
   - 야간/주말 자동 종료

2. **예약 인스턴스**:
   - 1년 또는 3년 약정으로 최대 72% 할당

3. **스팟 인스턴스**:
   - 개발 환경에서 최대 90% 할인

### 프로덕션 환경

1. **Azure Advisor 권장사항 확인**
2. **리소스 모니터링 및 최적화**
3. **사용하지 않는 리소스 정리**

---

## 다음 단계

- ✅ Azure VM 설정 완료
- ✅ 시스템 실행 및 테스트
- ⏭️ 프론트엔드 개발 및 커스터마이징
- ⏭️ OCR 이미지 테스트 (실제 사업자등록증)
- ⏭️ 사용자 교육 및 매뉴얼 작성
- ⏭️ 프로덕션 배포 및 HTTPS 설정
- ⏭️ 모니터링 및 백업 자동화

---

## 참고 문서

- **통합 테스트 가이드**: `INTEGRATION_TEST_GUIDE.md`
- **API 테스트 샘플**: `API_TEST_SAMPLES.md`
- **OCR 테스트**: `backend/tests/test_ocr/README.md`
- **Azure 공식 문서**: https://docs.microsoft.com/ko-kr/azure/

---

## 지원

문제가 발생하면:
1. 이 문서의 트러블슈팅 섹션 확인
2. GitHub Issues에 문의
3. Azure 지원 센터 문의

---

**배포 성공을 기원합니다! 🚀**
