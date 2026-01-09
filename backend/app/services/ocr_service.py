"""
OCR Service - Tesseract를 활용한 서류 분석
"""
import pytesseract
from PIL import Image
from typing import Dict, Any, Optional
import re


class OCRService:
    """OCR 처리 서비스"""

    def __init__(self, language: str = "kor+eng"):
        self.language = language
        self.config = "--psm 6 --oem 3"

    def extract_text(self, image_path: str) -> str:
        """이미지에서 텍스트 추출"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(
                image,
                lang=self.language,
                config=self.config
            )
            return text
        except Exception as e:
            raise Exception(f"OCR processing failed: {str(e)}")

    def extract_business_data(self, text: str) -> Dict[str, Any]:
        """
        사업자등록증에서 핵심 데이터 추출
        RegEx 패턴을 활용한 정보 추출
        """
        data = {
            "business_number": self._extract_business_number(text),
            "company_name": self._extract_company_name(text),
            "ceo_name": self._extract_ceo_name(text)
        }
        return data

    def _extract_business_number(self, text: str) -> Optional[str]:
        """사업자등록번호 추출 (XXX-XX-XXXXX 형식)"""
        pattern = r'\d{3}-\d{2}-\d{5}'
        match = re.search(pattern, text)
        return match.group(0) if match else None

    def _extract_company_name(self, text: str) -> Optional[str]:
        """기업명 추출"""
        # TODO: Implement more sophisticated extraction logic
        return None

    def _extract_ceo_name(self, text: str) -> Optional[str]:
        """대표자명 추출"""
        # TODO: Implement more sophisticated extraction logic
        return None
