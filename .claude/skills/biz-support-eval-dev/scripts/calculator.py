"""
점수 계산 알고리즘 - 평가 시스템용 참고 구현체

이 스크립트는 Claude Skills에서 참조하는 표준 구현 패턴입니다.
실제 프로젝트의 backend/app/services/score_service.py와 동기화됩니다.
"""

import statistics
from typing import List, Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP


class ScoreCalculator:
    """평가 점수 계산 유틸리티"""

    @staticmethod
    def calculate_average(scores: List[float]) -> float:
        """
        단순 평균 계산

        Args:
            scores: 점수 리스트

        Returns:
            소수점 둘째 자리 반올림한 평균값

        Examples:
            >>> ScoreCalculator.calculate_average([85, 90, 88])
            87.67
        """
        if not scores:
            return 0.0

        avg = statistics.mean(scores)
        return float(Decimal(str(avg)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    @staticmethod
    def calculate_trimmed_mean(
        scores: List[float],
        trim_count: int = 1
    ) -> float:
        """
        최고/최저점 제외 평균 (Trimmed Mean)

        5인 이상의 심사위원이 있을 경우, 최고점과 최저점을 각 1개씩 제외한 평균을 계산합니다.
        이는 극단적인 점수의 영향을 줄여 공정성을 높이는 방식입니다.

        Args:
            scores: 점수 리스트
            trim_count: 제외할 최고/최저 점수 개수 (기본 1개씩)

        Returns:
            소수점 둘째 자리 반올림한 평균값

        Examples:
            >>> ScoreCalculator.calculate_trimmed_mean([60, 85, 90, 92, 95])
            89.0  # 60과 95 제외

            >>> ScoreCalculator.calculate_trimmed_mean([85, 90, 88])
            87.67  # 5인 미만이므로 단순 평균
        """
        if len(scores) < 5:
            # 5인 미만인 경우 단순 평균 반환
            return ScoreCalculator.calculate_average(scores)

        # 정렬 후 최고/최저 제외
        sorted_scores = sorted(scores)
        trimmed_scores = sorted_scores[trim_count:-trim_count]

        if not trimmed_scores:
            return 0.0

        avg = statistics.mean(trimmed_scores)
        return float(Decimal(str(avg)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    @staticmethod
    def apply_weights(
        scores: Dict[str, float],
        weights: Dict[str, float]
    ) -> float:
        """
        가중치 적용 점수 계산

        각 평가 항목의 점수에 가중치를 곱하여 최종 점수를 산출합니다.
        가중치의 합이 1.0이 아닌 경우 자동으로 정규화됩니다.

        Args:
            scores: {"기술성": 85, "사업성": 90, ...}
            weights: {"기술성": 0.4, "사업성": 0.3, ...}

        Returns:
            가중치 합산 점수 (소수점 둘째 자리 반올림)

        Examples:
            >>> scores = {"기술성": 85, "사업성": 90, "시장성": 88}
            >>> weights = {"기술성": 0.4, "사업성": 0.3, "시장성": 0.3}
            >>> ScoreCalculator.apply_weights(scores, weights)
            87.4
        """
        # 가중치 정규화 (합이 1.0이 아닐 경우)
        total_weight = sum(weights.values())
        if total_weight == 0:
            return 0.0

        normalized_weights = {
            k: v / total_weight for k, v in weights.items()
        }

        # 가중 합계 계산
        total = 0.0
        for item, score in scores.items():
            weight = normalized_weights.get(item, 0)
            total += score * weight

        return float(Decimal(str(total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    @staticmethod
    def aggregate_evaluations(
        evaluations: List[Dict[str, Any]],
        use_trimmed_mean: bool = True
    ) -> Dict[str, Any]:
        """
        여러 심사위원의 평가 집계

        Args:
            evaluations: 평가 데이터 리스트
            use_trimmed_mean: True일 경우 최고/최저점 제외 평균 사용

        Returns:
            집계된 평가 결과
            {
                "average": 87.5,
                "trimmed_average": 88.0,
                "count": 5,
                "min": 82,
                "max": 95,
                "std_dev": 4.2
            }

        Examples:
            >>> evals = [
            ...     {"total_score": 85},
            ...     {"total_score": 90},
            ...     {"total_score": 88}
            ... ]
            >>> ScoreCalculator.aggregate_evaluations(evals)
            {'average': 87.67, 'trimmed_average': 87.67, ...}
        """
        if not evaluations:
            return {
                "average": 0.0,
                "trimmed_average": 0.0,
                "count": 0,
                "min": 0.0,
                "max": 0.0,
                "std_dev": 0.0
            }

        scores = [eval_data.get("total_score", 0) for eval_data in evaluations]

        avg = ScoreCalculator.calculate_average(scores)
        trimmed_avg = ScoreCalculator.calculate_trimmed_mean(scores)

        return {
            "average": avg,
            "trimmed_average": trimmed_avg if use_trimmed_mean else avg,
            "count": len(scores),
            "min": min(scores),
            "max": max(scores),
            "std_dev": round(statistics.stdev(scores), 2) if len(scores) > 1 else 0.0
        }

    @staticmethod
    def calculate_percentile(scores: List[float], percentile: int) -> float:
        """
        백분위수 계산

        Args:
            scores: 점수 리스트
            percentile: 백분위 (0-100)

        Returns:
            해당 백분위의 점수

        Examples:
            >>> scores = [60, 70, 80, 90, 100]
            >>> ScoreCalculator.calculate_percentile(scores, 50)
            80.0  # 중앙값
        """
        if not scores:
            return 0.0

        sorted_scores = sorted(scores)
        index = (percentile / 100) * (len(sorted_scores) - 1)

        if index.is_integer():
            return sorted_scores[int(index)]

        # 선형 보간
        lower = sorted_scores[int(index)]
        upper = sorted_scores[int(index) + 1]
        fraction = index - int(index)

        result = lower + (upper - lower) * fraction
        return float(Decimal(str(result)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    @staticmethod
    def detect_outliers(
        scores: List[float],
        method: str = "iqr"
    ) -> Dict[str, Any]:
        """
        이상치 탐지

        Args:
            scores: 점수 리스트
            method: "iqr" (사분위수) 또는 "zscore" (표준편차)

        Returns:
            이상치 정보
            {
                "outliers": [60, 100],
                "lower_bound": 70,
                "upper_bound": 95
            }
        """
        if len(scores) < 4:
            return {"outliers": [], "lower_bound": None, "upper_bound": None}

        sorted_scores = sorted(scores)

        if method == "iqr":
            q1 = ScoreCalculator.calculate_percentile(sorted_scores, 25)
            q3 = ScoreCalculator.calculate_percentile(sorted_scores, 75)
            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outliers = [s for s in scores if s < lower_bound or s > upper_bound]

            return {
                "outliers": outliers,
                "lower_bound": round(lower_bound, 2),
                "upper_bound": round(upper_bound, 2),
                "method": "IQR"
            }

        elif method == "zscore":
            mean = statistics.mean(scores)
            std = statistics.stdev(scores)

            outliers = [
                s for s in scores
                if abs(s - mean) > 2 * std  # 2 표준편차 초과
            ]

            return {
                "outliers": outliers,
                "lower_bound": round(mean - 2 * std, 2),
                "upper_bound": round(mean + 2 * std, 2),
                "method": "Z-Score"
            }

        return {"outliers": [], "lower_bound": None, "upper_bound": None}


# 사용 예시
if __name__ == "__main__":
    # 예제 1: 단순 평균
    scores = [85, 90, 88, 92, 87]
    print(f"평균 점수: {ScoreCalculator.calculate_average(scores)}")

    # 예제 2: 최고/최저점 제외 평균
    scores_with_outlier = [60, 85, 90, 92, 95]
    print(f"Trimmed Mean: {ScoreCalculator.calculate_trimmed_mean(scores_with_outlier)}")

    # 예제 3: 가중치 적용
    item_scores = {
        "기술성": 85,
        "사업성": 90,
        "시장성": 88
    }
    item_weights = {
        "기술성": 0.4,
        "사업성": 0.3,
        "시장성": 0.3
    }
    print(f"가중 점수: {ScoreCalculator.apply_weights(item_scores, item_weights)}")

    # 예제 4: 평가 집계
    evaluations = [
        {"total_score": 85},
        {"total_score": 90},
        {"total_score": 88},
        {"total_score": 92},
        {"total_score": 87}
    ]
    result = ScoreCalculator.aggregate_evaluations(evaluations)
    print(f"집계 결과: {result}")

    # 예제 5: 이상치 탐지
    outlier_result = ScoreCalculator.detect_outliers(scores_with_outlier)
    print(f"이상치 탐지: {outlier_result}")
