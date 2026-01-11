#!/usr/bin/env python3
"""
Rate Limiting 테스트 스크립트

사용법:
    python test_rate_limiting.py

요구사항:
    - 백엔드 서버가 http://localhost:8000 에서 실행 중이어야 합니다
    - pip install requests
"""

import requests
import time
from typing import Dict, Any


class Colors:
    """터미널 컬러 출력"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(text: str):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def test_rate_limit_login(base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """
    로그인 엔드포인트 Rate Limit 테스트
    제한: 5회/분
    """
    print_header("로그인 Rate Limit 테스트 (5회/분)")

    endpoint = f"{base_url}/api/v1/auth/login"
    payload = {
        "username": "test_user",
        "password": "test_password"
    }

    results = {
        "total_requests": 0,
        "successful": 0,
        "rate_limited": 0,
        "errors": 0
    }

    print_info(f"엔드포인트: {endpoint}")
    print_info("6회 연속 요청 시도 중...\n")

    for i in range(1, 7):
        try:
            response = requests.post(endpoint, json=payload, timeout=5)
            results["total_requests"] += 1

            if response.status_code == 429:  # Too Many Requests
                results["rate_limited"] += 1
                print_warning(f"요청 #{i}: Rate Limited (429) - {response.text[:100]}")
            elif response.status_code == 401:  # Unauthorized (예상됨)
                results["successful"] += 1
                print_success(f"요청 #{i}: 성공 (401 Unauthorized - 정상)")
            else:
                results["errors"] += 1
                print_error(f"요청 #{i}: 예상치 못한 응답 ({response.status_code})")

            time.sleep(0.5)  # 0.5초 대기

        except requests.exceptions.RequestException as e:
            results["errors"] += 1
            print_error(f"요청 #{i}: 연결 실패 - {str(e)}")

    # 결과 요약
    print(f"\n{Colors.BOLD}테스트 결과:{Colors.ENDC}")
    print(f"  총 요청: {results['total_requests']}")
    print(f"  성공 (401): {results['successful']}")
    print(f"  Rate Limited (429): {results['rate_limited']}")
    print(f"  오류: {results['errors']}")

    # 검증
    if results['rate_limited'] > 0:
        print_success("\n✅ Rate Limiting이 정상 작동합니다!")
    elif results['errors'] == results['total_requests']:
        print_error("\n❌ 서버 연결 실패 - 서버가 실행 중인지 확인하세요")
    else:
        print_warning("\n⚠️  Rate Limiting이 작동하지 않을 수 있습니다")

    return results


def test_rate_limit_change_password(base_url: str = "http://localhost:8000", token: str = None):
    """
    비밀번호 변경 엔드포인트 Rate Limit 테스트
    제한: 5회/분
    """
    print_header("비밀번호 변경 Rate Limit 테스트 (5회/분)")

    if not token:
        print_warning("JWT 토큰이 없어 테스트를 건너뜁니다")
        print_info("실제 토큰으로 테스트하려면 token 파라미터를 전달하세요\n")
        return None

    endpoint = f"{base_url}/api/v1/auth/change-password"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "current_password": "old_password",
        "new_password": "new_password"
    }

    results = {
        "total_requests": 0,
        "successful": 0,
        "rate_limited": 0,
        "errors": 0
    }

    print_info(f"엔드포인트: {endpoint}")
    print_info("6회 연속 요청 시도 중...\n")

    for i in range(1, 7):
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=5)
            results["total_requests"] += 1

            if response.status_code == 429:
                results["rate_limited"] += 1
                print_warning(f"요청 #{i}: Rate Limited (429)")
            elif response.status_code in [200, 400, 401]:
                results["successful"] += 1
                print_success(f"요청 #{i}: 성공 ({response.status_code})")
            else:
                results["errors"] += 1
                print_error(f"요청 #{i}: 예상치 못한 응답 ({response.status_code})")

            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            results["errors"] += 1
            print_error(f"요청 #{i}: 연결 실패 - {str(e)}")

    print(f"\n{Colors.BOLD}테스트 결과:{Colors.ENDC}")
    print(f"  총 요청: {results['total_requests']}")
    print(f"  성공: {results['successful']}")
    print(f"  Rate Limited (429): {results['rate_limited']}")
    print(f"  오류: {results['errors']}")

    if results['rate_limited'] > 0:
        print_success("\n✅ Rate Limiting이 정상 작동합니다!")

    return results


def test_server_health(base_url: str = "http://localhost:8000") -> bool:
    """서버 상태 확인"""
    print_header("서버 상태 확인")

    try:
        # API docs 엔드포인트로 서버 확인
        response = requests.get(f"{base_url}/api/docs", timeout=5)

        if response.status_code == 200:
            print_success(f"서버가 {base_url}에서 정상 작동 중입니다")
            return True
        else:
            print_warning(f"서버 응답: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print_error(f"서버 연결 실패: {str(e)}")
        print_info("\n서버 시작 방법:")
        print_info("  1. Docker: docker-compose up -d")
        print_info("  2. 수동: cd backend && uvicorn app.main:app --reload")
        return False


def main():
    """메인 테스트 실행"""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        중소기업 선정평가 시스템 - Rate Limit 테스트        ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

    base_url = "http://localhost:8000"

    # 1. 서버 상태 확인
    if not test_server_health(base_url):
        print_error("\n테스트를 계속할 수 없습니다. 서버를 먼저 시작하세요.")
        return

    # 2. 로그인 Rate Limit 테스트
    login_results = test_rate_limit_login(base_url)

    # 3. 비밀번호 변경 Rate Limit 테스트 (토큰 없이 스킵)
    test_rate_limit_change_password(base_url, token=None)

    # 최종 요약
    print_header("테스트 완료")

    if login_results.get("rate_limited", 0) > 0:
        print_success("Rate Limiting이 정상적으로 작동합니다! 🎉")
        print_info("\n프로덕션 배포 권장 사항:")
        print_info("  - HTTPS 활성화")
        print_info("  - 강력한 SECRET_KEY 설정")
        print_info("  - 데이터베이스 비밀번호 변경")
        print_info("  - 환경 변수 검토 (.env)")
    else:
        print_warning("Rate Limiting 동작을 확인하세요")

    print(f"\n{Colors.OKCYAN}자세한 보안 가이드: SECURITY.md{Colors.ENDC}")
    print(f"{Colors.OKCYAN}배포 가이드: DEPLOYMENT.md{Colors.ENDC}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}테스트가 사용자에 의해 중단되었습니다{Colors.ENDC}\n")
    except Exception as e:
        print_error(f"\n예상치 못한 오류: {str(e)}\n")
