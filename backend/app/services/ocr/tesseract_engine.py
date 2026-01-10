"""
Tesseract OCR Engine - 온프레미스 구현

참고: .claude/skills/biz-support-eval-dev/scripts/ocr_parser.py
"""
import re
import time
from typing import Dict, Any
from PIL import Image
import pytesseract

from .base import BaseOCREngine, OCREngineType, DocumentType, OCRResult


class TesseractEngine(BaseOCREngine):
    """Tesseract OCR 엔진"""

    def _get_engine_type(self) -> OCREngineType:
        return OCREngineType.TESSERACT

    def is_available(self) -> bool:
        """Tesseract 설치 여부 확인"""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    async def extract_text(self, image_path: str) -> str:
        """이미지에서 텍스트 추출"""
        try:
            image = Image.open(image_path)
            # 한글+영어 지원
            text = pytesseract.image_to_string(image, lang='kor+eng')
            return text
        except Exception as e:
            raise RuntimeError(f"Tesseract 텍스트 추출 실패: {str(e)}")

    async def analyze_document(
        self,
        image_path: str,
        document_type: DocumentType = DocumentType.GENERAL
    ) -> OCRResult:
        """문서 분석"""
        start_time = time.time()
        errors = []

        try:
            # 텍스트 추출
            raw_text = await self.extract_text(image_path)

            # 문서 타입별 파싱
            if document_type == DocumentType.BUSINESS_LICENSE:
                extracted_data = self._parse_business_license(raw_text)
            elif document_type == DocumentType.CORPORATE_REGISTRY:
                extracted_data = self._parse_corporate_registry(raw_text)
            else:
                extracted_data = {"raw_text": raw_text}

            # 신뢰도 계산
            confidence = self._calculate_confidence(extracted_data, document_type)

            processing_time = (time.time() - start_time) * 1000

            return OCRResult(
                engine=self.engine_type,
                document_type=document_type,
                extracted_data=extracted_data,
                confidence_score=confidence,
                raw_text=raw_text,
                needs_manual_verification=confidence < self.get_confidence_threshold(),
                processing_time_ms=processing_time,
                errors=errors
            )

        except Exception as e:
            errors.append(f"Tesseract 오류: {str(e)}")
            return OCRResult(
                engine=self.engine_type,
                document_type=document_type,
                extracted_data={},
                confidence_score=0.0,
                raw_text="",
                needs_manual_verification=True,
                processing_time_ms=(time.time() - start_time) * 1000,
                errors=errors
            )

    def _parse_business_license(self, text: str) -> Dict[str, Any]:
        """사업자등록증 파싱"""
        data = {}

        # 사업자등록번호
        business_number_pattern = r'\d{3}-\d{2}-\d{5}'
        match = re.search(business_number_pattern, text)
        if match:
            data["사업자등록번호"] = match.group()

        # 상호
        company_patterns = [
            r'상\s*호\s*[:：]\s*([^\n]{2,30})',
            r'법인명\s*[:：]\s*([^\n]{2,30})',
        ]
        for pattern in company_patterns:
            match = re.search(pattern, text)
            if match:
                data["상호"] = match.group(1).strip()
                break

        # 대표자
        ceo_patterns = [
            r'대표자\s*[:：]\s*([가-힣]{2,5})',
            r'성\s*명\s*[:：]\s*([가-힣]{2,5})',
        ]
        for pattern in ceo_patterns:
            match = re.search(pattern, text)
            if match:
                data["대표자"] = match.group(1).strip()
                break

        # 주소
        address_patterns = [
            r'소재지\s*[:：]\s*([^\n]{10,100})',
            r'사업장\s*주소\s*[:：]\s*([^\n]{10,100})',
        ]
        for pattern in address_patterns:
            match = re.search(pattern, text)
            if match:
                address = match.group(1).strip()
                if any(keyword in address for keyword in ['시', '구', '동', '로', '길']):
                    data["사업장주소"] = address
                    break

        # 개업일자
        date_pattern = r'\d{4}[년\-\.]\s?\d{1,2}[월\-\.]\s?\d{1,2}일?'
        match = re.search(date_pattern, text)
        if match:
            data["개업일자"] = match.group()

        return data

    def _parse_corporate_registry(self, text: str) -> Dict[str, Any]:
        """법인등기부등본 파싱"""
        data = {}

        # 법인등록번호
        corporate_pattern = r'\d{6}-\d{7}'
        match = re.search(corporate_pattern, text)
        if match:
            data["법인등록번호"] = match.group()

        # 법인명
        company_pattern = r'상\s*호\s*[:：]\s*([^\n]{2,30})'
        match = re.search(company_pattern, text)
        if match:
            data["법인명"] = match.group(1).strip()

        # 자본금
        capital_pattern = r'자본금\s*[:：]\s*([0-9,]+)\s*원'
        match = re.search(capital_pattern, text)
        if match:
            data["자본금"] = match.group(1).replace(',', '')

        return data

    def _calculate_confidence(self, extracted_data: Dict[str, Any], doc_type: DocumentType) -> float:
        """신뢰도 계산"""
        if not extracted_data:
            return 0.0

        required_fields = {
            DocumentType.BUSINESS_LICENSE: ["사업자등록번호", "상호", "대표자"],
            DocumentType.CORPORATE_REGISTRY: ["법인등록번호", "법인명"],
        }

        if doc_type not in required_fields:
            return 0.5

        fields = required_fields[doc_type]
        found_fields = sum(1 for field in fields if field in extracted_data)

        base_confidence = found_fields / len(fields)

        # 추가 검증 (사업자등록번호 형식)
        if "사업자등록번호" in extracted_data:
            number = extracted_data["사업자등록번호"]
            if self._validate_business_number(number):
                base_confidence += 0.1

        return min(base_confidence, 1.0)

    def _validate_business_number(self, number: str) -> bool:
        """사업자등록번호 체크섬 검증"""
        digits = number.replace('-', '')
        if len(digits) != 10 or not digits.isdigit():
            return False

        multipliers = [1, 3, 7, 1, 3, 7, 1, 3, 5]
        total = sum(int(digits[i]) * multipliers[i] for i in range(9))
        total += int((int(digits[8]) * 5) / 10)

        check_digit = (10 - (total % 10)) % 10
        return check_digit == int(digits[9])
