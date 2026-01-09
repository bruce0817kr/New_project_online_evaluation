"""
Score Aggregation Service - 점수 계산 로직
"""
from typing import List, Dict, Any
import statistics


class ScoreService:
    """평가 점수 계산 서비스"""

    @staticmethod
    def calculate_average(scores: List[float]) -> float:
        """단순 평균 계산"""
        if not scores:
            return 0.0
        return round(statistics.mean(scores), 2)

    @staticmethod
    def calculate_trimmed_mean(scores: List[float], trim_count: int = 1) -> float:
        """
        최고/최저점 제외 평균 (Trimmed Mean)

        Args:
            scores: 점수 리스트
            trim_count: 제외할 최고/최저 점수 개수 (기본 1개씩)

        Returns:
            소수점 셋째 자리 반올림한 평균값
        """
        if len(scores) < 5:
            # 5인 미만인 경우 단순 평균
            return ScoreService.calculate_average(scores)

        # 정렬 후 최고/최저 제외
        sorted_scores = sorted(scores)
        trimmed_scores = sorted_scores[trim_count:-trim_count]

        if not trimmed_scores:
            return 0.0

        return round(statistics.mean(trimmed_scores), 2)

    @staticmethod
    def apply_weights(
        scores: Dict[str, float],
        weights: Dict[str, float]
    ) -> float:
        """
        가중치 적용 점수 계산

        Args:
            scores: {"항목1": 85, "항목2": 90, ...}
            weights: {"항목1": 0.3, "항목2": 0.4, ...}

        Returns:
            가중치 합산 점수
        """
        total = 0.0
        for item, score in scores.items():
            weight = weights.get(item, 0)
            total += score * weight

        return round(total, 2)

    @staticmethod
    def aggregate_evaluations(
        evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        여러 심사위원의 평가 집계

        Args:
            evaluations: 평가 데이터 리스트

        Returns:
            집계된 평가 결과
        """
        if not evaluations:
            return {"average": 0.0, "trimmed_average": 0.0, "count": 0}

        scores = [eval_data.get("total_score", 0) for eval_data in evaluations]

        return {
            "average": ScoreService.calculate_average(scores),
            "trimmed_average": ScoreService.calculate_trimmed_mean(scores),
            "count": len(scores),
            "min": min(scores),
            "max": max(scores)
        }
