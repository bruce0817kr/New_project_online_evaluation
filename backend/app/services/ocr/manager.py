"""
OCR Manager - 멀티 엔진 통합 및 폴백 전략

전략:
1. Tesseract 우선 (온프레미스, 무료)
2. 실패 시 또는 신뢰도 낮을 시 클라우드 API로 폴백
3. 앙상블 옵션 (여러 엔진 결과 비교)
"""
from typing import Optional, List, Dict, Any
from enum import Enum
import asyncio

from .base import BaseOCREngine, OCREngineType, DocumentType, OCRResult
from .tesseract_engine import TesseractEngine
from .openai_engine import OpenAIEngine
from .gemini_engine import GeminiEngine
from .mistral_engine import MistralEngine


class FallbackStrategy(Enum):
    """폴백 전략"""
    NONE = "none"  # 폴백 없음
    ON_FAILURE = "on_failure"  # 실패 시에만
    ON_LOW_CONFIDENCE = "on_low_confidence"  # 신뢰도 낮을 시
    ALWAYS = "always"  # 항상 다음 엔진 시도


class OCRManager:
    """
    OCR 엔진 매니저

    여러 OCR 엔진을 관리하고 폴백 전략을 적용합니다.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Args:
            config: 설정
            {
                "tesseract": {...},
                "openai": {"api_key": "sk-..."},
                "gemini": {"api_key": "..."},
                "mistral": {"api_key": "..."},
                "fallback_strategy": "on_low_confidence",
                "confidence_threshold": 0.85,
                "enable_ensemble": False
            }
        """
        self.config = config or {}
        self.engines: List[BaseOCREngine] = []
        self.fallback_strategy = FallbackStrategy(
            self.config.get("fallback_strategy", "on_low_confidence")
        )
        self.confidence_threshold = self.config.get("confidence_threshold", 0.85)
        self.enable_ensemble = self.config.get("enable_ensemble", False)

        # 엔진 초기화 (우선순위 순서)
        self._initialize_engines()

    def _initialize_engines(self):
        """사용 가능한 엔진 초기화"""
        # 1. Tesseract (온프레미스 우선)
        try:
            tesseract_config = self.config.get("tesseract", {})
            tesseract = TesseractEngine(tesseract_config)
            if tesseract.is_available():
                self.engines.append(tesseract)
        except Exception as e:
            print(f"Tesseract 초기화 실패: {e}")

        # 2. OpenAI Vision
        if self.config.get("openai", {}).get("api_key"):
            try:
                openai_engine = OpenAIEngine(self.config.get("openai"))
                if openai_engine.is_available():
                    self.engines.append(openai_engine)
            except Exception as e:
                print(f"OpenAI 초기화 실패: {e}")

        # 3. Google Gemini
        if self.config.get("gemini", {}).get("api_key"):
            try:
                gemini_engine = GeminiEngine(self.config.get("gemini"))
                if gemini_engine.is_available():
                    self.engines.append(gemini_engine)
            except Exception as e:
                print(f"Gemini 초기화 실패: {e}")

        # 4. Mistral Pixtral
        if self.config.get("mistral", {}).get("api_key"):
            try:
                mistral_engine = MistralEngine(self.config.get("mistral"))
                if mistral_engine.is_available():
                    self.engines.append(mistral_engine)
            except Exception as e:
                print(f"Mistral 초기화 실패: {e}")

        if not self.engines:
            raise RuntimeError("사용 가능한 OCR 엔진이 없습니다")

    async def analyze_document(
        self,
        image_path: str,
        document_type: DocumentType = DocumentType.GENERAL,
        preferred_engine: Optional[OCREngineType] = None
    ) -> OCRResult:
        """
        문서 분석 (폴백 전략 적용)

        Args:
            image_path: 이미지 경로
            document_type: 문서 타입
            preferred_engine: 선호 엔진 (None이면 자동 선택)

        Returns:
            OCRResult
        """
        if self.enable_ensemble:
            return await self._analyze_with_ensemble(image_path, document_type)

        # 선호 엔진이 지정된 경우
        if preferred_engine:
            engine = self._get_engine_by_type(preferred_engine)
            if engine:
                result = await engine.analyze_document(image_path, document_type)
                if self._is_result_acceptable(result):
                    return result

        # 폴백 전략 적용
        return await self._analyze_with_fallback(image_path, document_type)

    async def _analyze_with_fallback(
        self,
        image_path: str,
        document_type: DocumentType
    ) -> OCRResult:
        """폴백 전략 적용"""
        last_result = None

        for engine in self.engines:
            try:
                result = await engine.analyze_document(image_path, document_type)
                last_result = result

                # 결과가 만족스러우면 반환
                if self._is_result_acceptable(result):
                    return result

                # 폴백 조건 확인
                if self.fallback_strategy == FallbackStrategy.NONE:
                    return result
                elif self.fallback_strategy == FallbackStrategy.ON_FAILURE:
                    if result.confidence_score > 0:
                        return result
                elif self.fallback_strategy == FallbackStrategy.ON_LOW_CONFIDENCE:
                    if result.confidence_score >= self.confidence_threshold:
                        return result

                # 다음 엔진으로 계속

            except Exception as e:
                print(f"{engine.engine_type.value} 실패: {e}")
                continue

        # 모든 엔진 시도 후 마지막 결과 반환
        if last_result:
            return last_result

        # 모든 엔진 실패
        raise RuntimeError("모든 OCR 엔진이 실패했습니다")

    async def _analyze_with_ensemble(
        self,
        image_path: str,
        document_type: DocumentType
    ) -> OCRResult:
        """
        앙상블 방식 (여러 엔진 병렬 실행 후 결과 비교)

        가장 신뢰도가 높은 결과를 선택하거나, 투표 방식으로 결정
        """
        tasks = [
            engine.analyze_document(image_path, document_type)
            for engine in self.engines
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 에러가 아닌 결과만 필터링
        valid_results = [
            r for r in results
            if isinstance(r, OCRResult) and r.confidence_score > 0
        ]

        if not valid_results:
            raise RuntimeError("모든 OCR 엔진이 실패했습니다")

        # 가장 신뢰도가 높은 결과 반환
        best_result = max(valid_results, key=lambda x: x.confidence_score)

        # 앙상블 정보 추가
        best_result.extracted_data["ensemble_info"] = {
            "engines_used": [r.engine.value for r in valid_results],
            "confidence_scores": {
                r.engine.value: r.confidence_score for r in valid_results
            }
        }

        return best_result

    def _is_result_acceptable(self, result: OCRResult) -> bool:
        """결과가 허용 가능한지 확인"""
        return (
            result.confidence_score >= self.confidence_threshold and
            not result.needs_manual_verification and
            not result.errors
        )

    def _get_engine_by_type(self, engine_type: OCREngineType) -> Optional[BaseOCREngine]:
        """엔진 타입으로 엔진 찾기"""
        for engine in self.engines:
            if engine.engine_type == engine_type:
                return engine
        return None

    def get_available_engines(self) -> List[str]:
        """사용 가능한 엔진 목록"""
        return [engine.engine_type.value for engine in self.engines]

    async def extract_text_simple(self, image_path: str) -> str:
        """간단한 텍스트 추출 (첫 번째 엔진 사용)"""
        if not self.engines:
            raise RuntimeError("사용 가능한 OCR 엔진이 없습니다")

        return await self.engines[0].extract_text(image_path)
