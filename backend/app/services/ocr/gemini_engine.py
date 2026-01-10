"""
Google Gemini Vision API Engine

참고: https://ai.google.dev/docs/vision
"""
import base64
import time
import json
from typing import Dict, Any, Optional
import google.generativeai as genai
from PIL import Image

from .base import BaseOCREngine, OCREngineType, DocumentType, OCRResult


class GeminiEngine(BaseOCREngine):
    """Google Gemini Vision 엔진"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        api_key = self.config.get("api_key")
        if not api_key:
            raise ValueError("Google Gemini API 키가 설정되지 않았습니다")

        genai.configure(api_key=api_key)
        self.model_name = self.config.get("model", "gemini-1.5-flash")  # 또는 gemini-pro-vision
        self.model = genai.GenerativeModel(self.model_name)

    def _get_engine_type(self) -> OCREngineType:
        return OCREngineType.GEMINI

    def is_available(self) -> bool:
        """API 키 설정 여부 확인"""
        return bool(self.config.get("api_key"))

    async def extract_text(self, image_path: str) -> str:
        """이미지에서 텍스트 추출"""
        try:
            image = Image.open(image_path)

            response = self.model.generate_content([
                "이 이미지의 모든 텍스트를 정확히 추출해주세요. 한글과 영문 모두 포함하여 원본 그대로 반환해주세요.",
                image
            ])

            return response.text

        except Exception as e:
            raise RuntimeError(f"Gemini Vision API 오류: {str(e)}")

    async def analyze_document(
        self,
        image_path: str,
        document_type: DocumentType = DocumentType.GENERAL
    ) -> OCRResult:
        """문서 분석"""
        start_time = time.time()
        errors = []

        try:
            image = Image.open(image_path)
            prompt = self._get_prompt_for_document_type(document_type)

            response = self.model.generate_content(
                [prompt, image],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=2048
                )
            )

            raw_text = response.text

            # JSON 파싱 시도
            try:
                # Gemini는 종종 마크다운 코드 블록으로 감싸서 반환
                if "```json" in raw_text:
                    json_str = raw_text.split("```json")[1].split("```")[0].strip()
                elif "```" in raw_text:
                    json_str = raw_text.split("```")[1].split("```")[0].strip()
                else:
                    json_str = raw_text

                extracted_data = json.loads(json_str)
                confidence = extracted_data.pop("confidence", 0.9)
            except (json.JSONDecodeError, IndexError):
                extracted_data = {"raw_text": raw_text}
                confidence = 0.7

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
            errors.append(f"Gemini Vision 오류: {str(e)}")
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

    def _get_prompt_for_document_type(self, doc_type: DocumentType) -> str:
        """문서 타입별 프롬프트"""
        if doc_type == DocumentType.BUSINESS_LICENSE:
            return """
이 이미지는 한국의 사업자등록증입니다. 다음 정보를 JSON 형식으로 정확히 추출해주세요:

{
  "사업자등록번호": "XXX-XX-XXXXX 형식",
  "상호": "회사명",
  "대표자": "대표자 이름",
  "사업장주소": "전체 주소",
  "개업일자": "날짜",
  "업태": "업태",
  "종목": "종목",
  "confidence": 0.0~1.0
}

JSON만 반환하고, 추가 설명은 하지 말아주세요.
"""
        elif doc_type == DocumentType.CORPORATE_REGISTRY:
            return """
이 이미지는 법인등기부등본입니다. 다음 정보를 JSON 형식으로 추출해주세요:

{
  "법인등록번호": "XXXXXX-XXXXXXX 형식",
  "법인명": "회사명",
  "자본금": "숫자만",
  "대표이사": "이름",
  "confidence": 0.0~1.0
}

JSON만 반환하고, 추가 설명은 하지 말아주세요.
"""
        else:
            return "이 문서의 모든 텍스트를 추출하고, 주요 정보를 JSON 형식으로 구조화해주세요."
