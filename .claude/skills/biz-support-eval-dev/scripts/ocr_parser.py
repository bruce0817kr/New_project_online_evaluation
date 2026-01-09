"""
OCR 파싱 로직 - 사업자등록증 및 기업 서류 분석

Tesseract OCR을 활용한 문서 자동 파싱 참고 구현체입니다.
실제 프로젝트의 backend/app/services/ocr_service.py와 동기화됩니다.
"""

import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class DocumentType(Enum):
    """지원 가능한 문서 유형"""
    BUSINESS_LICENSE = "사업자등록증"
    CORPORATE_REGISTRY = "법인등기부등본"
    FINANCIAL_STATEMENT = "재무제표"
    UNKNOWN = "알 수 없음"


@dataclass
class OCRResult:
    """OCR 분석 결과"""
    document_type: DocumentType
    extracted_data: Dict[str, Any]
    confidence_score: float  # 0.0 ~ 1.0
    raw_text: str
    needs_manual_verification: bool
    errors: List[str]


class OCRParser:
    """OCR 텍스트 파싱 유틸리티"""

    # 정규표현식 패턴
    BUSINESS_NUMBER_PATTERN = r'\d{3}-\d{2}-\d{5}'  # XXX-XX-XXXXX
    CORPORATE_NUMBER_PATTERN = r'\d{6}-\d{7}'  # XXXXXX-XXXXXXX
    DATE_PATTERN = r'\d{4}[년\-\.]\s?\d{1,2}[월\-\.]\s?\d{1,2}일?'
    PHONE_PATTERN = r'0\d{1,2}[-\s]?\d{3,4}[-\s]?\d{4}'
    EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    # 신뢰도 임계값
    CONFIDENCE_THRESHOLD = 0.8

    @staticmethod
    def detect_document_type(text: str) -> DocumentType:
        """
        문서 유형 자동 감지

        Args:
            text: OCR로 추출한 원본 텍스트

        Returns:
            문서 유형
        """
        text_lower = text.lower()

        if "사업자등록증" in text or "사업자" in text:
            return DocumentType.BUSINESS_LICENSE
        elif "법인등기부" in text or "등기사항" in text:
            return DocumentType.CORPORATE_REGISTRY
        elif "재무상태표" in text or "손익계산서" in text:
            return DocumentType.FINANCIAL_STATEMENT
        else:
            return DocumentType.UNKNOWN

    @staticmethod
    def parse_business_license(text: str) -> OCRResult:
        """
        사업자등록증 파싱

        Args:
            text: OCR 추출 텍스트

        Returns:
            OCRResult 객체
        """
        extracted_data = {}
        errors = []
        confidence_scores = []

        # 1. 사업자등록번호 추출
        business_numbers = re.findall(OCRParser.BUSINESS_NUMBER_PATTERN, text)
        if business_numbers:
            extracted_data["사업자등록번호"] = business_numbers[0]
            confidence_scores.append(1.0)
        else:
            errors.append("사업자등록번호를 찾을 수 없습니다")
            confidence_scores.append(0.0)

        # 2. 상호명 추출
        company_name = OCRParser._extract_company_name(text)
        if company_name:
            extracted_data["상호"] = company_name
            confidence_scores.append(0.9)
        else:
            errors.append("상호를 찾을 수 없습니다")
            confidence_scores.append(0.0)

        # 3. 대표자명 추출
        ceo_name = OCRParser._extract_ceo_name(text)
        if ceo_name:
            extracted_data["대표자"] = ceo_name
            confidence_scores.append(0.85)
        else:
            errors.append("대표자명을 찾을 수 없습니다")
            confidence_scores.append(0.5)

        # 4. 개업일자 추출
        dates = re.findall(OCRParser.DATE_PATTERN, text)
        if dates:
            extracted_data["개업일자"] = dates[0]
            confidence_scores.append(0.9)

        # 5. 주소 추출
        address = OCRParser._extract_address(text)
        if address:
            extracted_data["사업장주소"] = address
            confidence_scores.append(0.75)

        # 6. 업태 및 종목 추출
        business_type = OCRParser._extract_business_type(text)
        if business_type:
            extracted_data["업태"] = business_type.get("업태", "")
            extracted_data["종목"] = business_type.get("종목", "")
            confidence_scores.append(0.8)

        # 신뢰도 계산
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        return OCRResult(
            document_type=DocumentType.BUSINESS_LICENSE,
            extracted_data=extracted_data,
            confidence_score=round(overall_confidence, 2),
            raw_text=text,
            needs_manual_verification=overall_confidence < OCRParser.CONFIDENCE_THRESHOLD,
            errors=errors
        )

    @staticmethod
    def _extract_company_name(text: str) -> Optional[str]:
        """
        상호명 추출

        패턴:
        - "상호:" 다음 텍스트
        - "상 호:" 다음 텍스트
        """
        patterns = [
            r'상\s*호\s*[:：]\s*([^\n]{2,30})',
            r'법인명\s*[:：]\s*([^\n]{2,30})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                # 특수문자 및 불필요한 공백 제거
                name = re.sub(r'[_\-\s]{2,}', ' ', name)
                return name

        return None

    @staticmethod
    def _extract_ceo_name(text: str) -> Optional[str]:
        """
        대표자명 추출

        패턴:
        - "대표자:" 다음 텍스트
        - 한글 2-5자
        """
        patterns = [
            r'대표자\s*[:：]\s*([가-힣]{2,5})',
            r'성\s*명\s*[:：]\s*([가-힣]{2,5})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return None

    @staticmethod
    def _extract_address(text: str) -> Optional[str]:
        """
        주소 추출

        패턴:
        - "소재지:", "주소:" 다음 텍스트
        - 도/시/구/동 포함
        """
        patterns = [
            r'소재지\s*[:：]\s*([^\n]{10,100})',
            r'사업장\s*주소\s*[:：]\s*([^\n]{10,100})',
            r'주\s*소\s*[:：]\s*([^\n]{10,100})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                address = match.group(1).strip()
                # 주소에 도/시/구/동이 포함되어 있는지 검증
                if any(keyword in address for keyword in ['시', '구', '동', '로', '길']):
                    return address

        return None

    @staticmethod
    def _extract_business_type(text: str) -> Optional[Dict[str, str]]:
        """
        업태 및 종목 추출

        Returns:
            {"업태": "도소매업", "종목": "의류"}
        """
        result = {}

        # 업태 추출
        business_pattern = r'업\s*태\s*[:：]\s*([^\n가-힣\s]{2,30}|[가-힣\s,]{2,30})'
        business_match = re.search(business_pattern, text)
        if business_match:
            result["업태"] = business_match.group(1).strip()

        # 종목 추출
        item_pattern = r'종\s*목\s*[:：]\s*([^\n가-힣\s]{2,50}|[가-힣\s,]{2,50})'
        item_match = re.search(item_pattern, text)
        if item_match:
            result["종목"] = item_match.group(1).strip()

        return result if result else None

    @staticmethod
    def parse_corporate_registry(text: str) -> OCRResult:
        """
        법인등기부등본 파싱

        Args:
            text: OCR 추출 텍스트

        Returns:
            OCRResult 객체
        """
        extracted_data = {}
        errors = []
        confidence_scores = []

        # 법인등록번호 추출
        corporate_numbers = re.findall(OCRParser.CORPORATE_NUMBER_PATTERN, text)
        if corporate_numbers:
            extracted_data["법인등록번호"] = corporate_numbers[0]
            confidence_scores.append(1.0)
        else:
            errors.append("법인등록번호를 찾을 수 없습니다")
            confidence_scores.append(0.0)

        # 법인명 추출
        company_name = OCRParser._extract_company_name(text)
        if company_name:
            extracted_data["법인명"] = company_name
            confidence_scores.append(0.9)

        # 자본금 추출
        capital_pattern = r'자본금\s*[:：]\s*([0-9,]+)\s*원'
        capital_match = re.search(capital_pattern, text)
        if capital_match:
            extracted_data["자본금"] = capital_match.group(1).replace(',', '')
            confidence_scores.append(0.85)

        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        return OCRResult(
            document_type=DocumentType.CORPORATE_REGISTRY,
            extracted_data=extracted_data,
            confidence_score=round(overall_confidence, 2),
            raw_text=text,
            needs_manual_verification=overall_confidence < OCRParser.CONFIDENCE_THRESHOLD,
            errors=errors
        )

    @staticmethod
    def validate_business_number(number: str) -> bool:
        """
        사업자등록번호 유효성 검증 (체크섬 알고리즘)

        Args:
            number: XXX-XX-XXXXX 형식

        Returns:
            유효하면 True
        """
        # 하이픈 제거
        digits = number.replace('-', '')

        if len(digits) != 10 or not digits.isdigit():
            return False

        # 체크섬 계산
        multipliers = [1, 3, 7, 1, 3, 7, 1, 3, 5]
        total = 0

        for i in range(9):
            total += int(digits[i]) * multipliers[i]

        # 8번째 자리 추가 처리
        total += int((int(digits[8]) * 5) / 10)

        # 체크 디지트 검증
        check_digit = (10 - (total % 10)) % 10
        return check_digit == int(digits[9])

    @staticmethod
    def preprocess_image_recommendations() -> Dict[str, str]:
        """
        OCR 정확도 향상을 위한 이미지 전처리 권장사항

        Returns:
            권장 설정 딕셔너리
        """
        return {
            "해상도": "최소 300 DPI",
            "포맷": "PNG 또는 TIFF (JPEG는 손실 압축으로 비권장)",
            "색상": "그레이스케일 변환 (흑백 대비 향상)",
            "노이즈": "Gaussian Blur 적용 (커널 크기: 3x3)",
            "이진화": "Otsu's Binarization 또는 Adaptive Thresholding",
            "기울기": "Deskew 알고리즘으로 자동 보정",
            "여백": "최소 10px 여백 유지"
        }


# 사용 예시
if __name__ == "__main__":
    # 예제 1: 사업자등록증 샘플 텍스트
    sample_text = """
    사업자등록증

    사업자등록번호: 123-45-67890
    상 호: (주)테크이노베이션
    대표자: 홍길동
    개업일자: 2020년 3월 15일
    사업장 소재지: 서울특별시 강남구 테헤란로 123
    업 태: 정보통신업
    종 목: 소프트웨어 개발 및 공급
    """

    result = OCRParser.parse_business_license(sample_text)

    print("=== OCR 파싱 결과 ===")
    print(f"문서 유형: {result.document_type.value}")
    print(f"신뢰도: {result.confidence_score * 100}%")
    print(f"추출 데이터: {result.extracted_data}")
    print(f"수동 검증 필요: {result.needs_manual_verification}")
    if result.errors:
        print(f"오류: {result.errors}")

    # 예제 2: 사업자등록번호 검증
    test_number = "123-45-67890"
    is_valid = OCRParser.validate_business_number(test_number)
    print(f"\n사업자등록번호 {test_number} 유효성: {is_valid}")

    # 예제 3: 이미지 전처리 권장사항
    recommendations = OCRParser.preprocess_image_recommendations()
    print("\n=== 이미지 전처리 권장사항 ===")
    for key, value in recommendations.items():
        print(f"{key}: {value}")
