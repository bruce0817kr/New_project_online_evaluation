"""
Test Score Service - TDD Approach
"""
import pytest
from app.services.score_service import ScoreService


class TestScoreService:
    """점수 계산 서비스 테스트"""

    def test_calculate_average(self):
        """단순 평균 계산 테스트"""
        scores = [80, 85, 90, 95, 100]
        result = ScoreService.calculate_average(scores)
        assert result == 90.0

    def test_calculate_average_empty(self):
        """빈 리스트 평균 계산"""
        scores = []
        result = ScoreService.calculate_average(scores)
        assert result == 0.0

    def test_calculate_trimmed_mean_with_5_scores(self):
        """5인 이상 - 최고/최저 제외 평균"""
        scores = [60, 70, 80, 90, 100]  # 최저 60, 최고 100 제외 -> 70,80,90
        result = ScoreService.calculate_trimmed_mean(scores)
        expected = round((70 + 80 + 90) / 3, 2)
        assert result == expected

    def test_calculate_trimmed_mean_with_less_than_5(self):
        """5인 미만 - 단순 평균"""
        scores = [70, 80, 90, 100]
        result = ScoreService.calculate_trimmed_mean(scores)
        expected = 85.0
        assert result == expected

    def test_apply_weights(self):
        """가중치 적용 점수 계산"""
        scores = {"항목1": 80, "항목2": 90, "항목3": 85}
        weights = {"항목1": 0.3, "항목2": 0.4, "항목3": 0.3}
        result = ScoreService.apply_weights(scores, weights)
        expected = round(80 * 0.3 + 90 * 0.4 + 85 * 0.3, 2)
        assert result == expected

    def test_aggregate_evaluations(self):
        """여러 심사위원 평가 집계"""
        evaluations = [
            {"total_score": 85},
            {"total_score": 90},
            {"total_score": 88},
            {"total_score": 92},
            {"total_score": 87}
        ]
        result = ScoreService.aggregate_evaluations(evaluations)

        assert result["count"] == 5
        assert result["average"] == 88.4
        assert result["min"] == 85
        assert result["max"] == 92
