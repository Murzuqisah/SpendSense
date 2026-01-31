"""Tests for confidence and risk scoring."""

import pytest
from src.scoring import ConfidenceScorer


class TestCalculateConfidenceScore:
    """Tests for confidence score calculation."""

    def test_zero_purchase_zero_disposable(self):
        """Test score when both purchase and disposable are near zero."""
        # When disposable is 0, we use max(0, 1) = 1
        # score = 0 / 1 = 0
        score = ConfidenceScorer.calculate_confidence_score(0, 0)
        assert score == 0.0

    def test_low_purchase_high_disposable(self):
        """Test score with low purchase vs high disposable."""
        # score = 100 / 1000 = 0.1
        score = ConfidenceScorer.calculate_confidence_score(100, 1000)
        assert score == 0.1

    def test_high_purchase_low_disposable(self):
        """Test score with high purchase vs low disposable."""
        # score = 900 / 1000 = 0.9, capped at 1.0
        score = ConfidenceScorer.calculate_confidence_score(900, 1000)
        assert score == 0.9

    def test_purchase_exceeds_disposable(self):
        """Test score when purchase exceeds disposable."""
        # score = 1500 / 1000 = 1.5, capped at 1.0
        score = ConfidenceScorer.calculate_confidence_score(1500, 1000)
        assert score == 1.0

    def test_purchase_equals_disposable(self):
        """Test score when purchase equals disposable."""
        # score = 1000 / 1000 = 1.0
        score = ConfidenceScorer.calculate_confidence_score(1000, 1000)
        assert score == 1.0

    def test_negative_disposable_uses_one(self):
        """Test that negative disposable is treated as 1."""
        # score = 100 / max(-500, 1) = 100 / 1 = 100, capped at 1.0
        score = ConfidenceScorer.calculate_confidence_score(100, -500)
        assert score == 1.0

    def test_fractional_amounts(self):
        """Test with fractional amounts."""
        # score = 99.50 / 500.00 = 0.199
        score = ConfidenceScorer.calculate_confidence_score(99.50, 500.00)
        assert pytest.approx(score, 0.001) == 0.199

    def test_very_small_purchase(self):
        """Test with very small purchase."""
        # score = 1 / 10000 = 0.0001, rounded to 3 decimals = 0.0
        score = ConfidenceScorer.calculate_confidence_score(1, 10000)
        assert score == 0.0  # Rounds to 0 when rounded to 3 decimals

    def test_score_rounded_to_three_decimals(self):
        """Test that score is rounded to 3 decimal places."""
        score = ConfidenceScorer.calculate_confidence_score(333.33, 1000)
        # 333.33 / 1000 = 0.33333
        assert len(str(score).split(".")[1]) <= 3

    def test_boundary_low_risk_max(self):
        """Test boundary case for low risk maximum."""
        # score = 400 / 1000 = 0.4
        score = ConfidenceScorer.calculate_confidence_score(400, 1000)
        assert score == 0.4

    def test_boundary_medium_risk_max(self):
        """Test boundary case for medium risk maximum."""
        # score = 700 / 1000 = 0.7
        score = ConfidenceScorer.calculate_confidence_score(700, 1000)
        assert score == 0.7


class TestGetRiskLevelFromScore:
    """Tests for risk level mapping from score."""

    def test_low_risk_boundary_lower(self):
        """Test low risk at lower boundary."""
        risk = ConfidenceScorer.get_risk_level_from_score(0.0)
        assert risk == "Low Risk"

    def test_low_risk_boundary_upper(self):
        """Test low risk at upper boundary."""
        risk = ConfidenceScorer.get_risk_level_from_score(0.4)
        assert risk == "Low Risk"

    def test_low_risk_midpoint(self):
        """Test low risk at midpoint."""
        risk = ConfidenceScorer.get_risk_level_from_score(0.2)
        assert risk == "Low Risk"

    def test_medium_risk_boundary_lower(self):
        """Test medium risk at lower boundary."""
        risk = ConfidenceScorer.get_risk_level_from_score(0.41)
        assert risk == "Medium Risk"

    def test_medium_risk_boundary_upper(self):
        """Test medium risk at upper boundary."""
        risk = ConfidenceScorer.get_risk_level_from_score(0.7)
        assert risk == "Medium Risk"

    def test_medium_risk_midpoint(self):
        """Test medium risk at midpoint."""
        risk = ConfidenceScorer.get_risk_level_from_score(0.55)
        assert risk == "Medium Risk"

    def test_high_risk_boundary_lower(self):
        """Test high risk at lower boundary."""
        risk = ConfidenceScorer.get_risk_level_from_score(0.71)
        assert risk == "High Risk"

    def test_high_risk_boundary_upper(self):
        """Test high risk at upper boundary."""
        risk = ConfidenceScorer.get_risk_level_from_score(1.0)
        assert risk == "High Risk"

    def test_high_risk_midpoint(self):
        """Test high risk at midpoint."""
        risk = ConfidenceScorer.get_risk_level_from_score(0.85)
        assert risk == "High Risk"


class TestScorePurchase:
    """Tests for score_purchase method."""

    def test_low_risk_purchase_returns_tuple(self):
        """Test that low risk purchase returns correct tuple."""
        score, risk = ConfidenceScorer.score_purchase(200, 1000)
        assert score == 0.2
        assert risk == "Low Risk"

    def test_medium_risk_purchase_returns_tuple(self):
        """Test that medium risk purchase returns correct tuple."""
        score, risk = ConfidenceScorer.score_purchase(500, 1000)
        assert score == 0.5
        assert risk == "Medium Risk"

    def test_high_risk_purchase_returns_tuple(self):
        """Test that high risk purchase returns correct tuple."""
        score, risk = ConfidenceScorer.score_purchase(800, 1000)
        assert score == 0.8
        assert risk == "High Risk"


class TestScoreWithBreakdown:
    """Tests for detailed score breakdown."""

    def test_breakdown_structure(self):
        """Test that breakdown contains all required fields."""
        breakdown = ConfidenceScorer.score_with_breakdown(300, 1000)

        assert "confidence_score" in breakdown
        assert "risk_level" in breakdown
        assert "percentage_of_disposable" in breakdown
        assert "color" in breakdown

    def test_low_risk_color(self):
        """Test low risk gets green color."""
        breakdown = ConfidenceScorer.score_with_breakdown(300, 1000)
        assert breakdown["color"] == "green"
        assert breakdown["risk_level"] == "Low Risk"

    def test_medium_risk_color(self):
        """Test medium risk gets yellow color."""
        breakdown = ConfidenceScorer.score_with_breakdown(500, 1000)
        assert breakdown["color"] == "yellow"
        assert breakdown["risk_level"] == "Medium Risk"

    def test_high_risk_color(self):
        """Test high risk gets red color."""
        breakdown = ConfidenceScorer.score_with_breakdown(800, 1000)
        assert breakdown["color"] == "red"
        assert breakdown["risk_level"] == "High Risk"

    def test_percentage_calculation(self):
        """Test percentage of disposable calculation."""
        breakdown = ConfidenceScorer.score_with_breakdown(300, 1000)
        # (300 / 1000) * 100 = 30%
        assert pytest.approx(breakdown["percentage_of_disposable"], 0.1) == 30.0

    def test_percentage_exceeds_100(self):
        """Test percentage can exceed 100% when purchase > disposable."""
        breakdown = ConfidenceScorer.score_with_breakdown(1500, 1000)
        # (1500 / 1000) * 100 = 150%
        assert pytest.approx(breakdown["percentage_of_disposable"], 0.1) == 150.0

    def test_percentage_with_zero_disposable(self):
        """Test percentage calculation with zero disposable."""
        breakdown = ConfidenceScorer.score_with_breakdown(100, 0)
        # (100 / max(0, 1)) * 100 = 10000%
        assert pytest.approx(breakdown["percentage_of_disposable"], 0.1) == 10000.0

    def test_comprehensive_low_risk_scenario(self):
        """Test complete low risk scenario."""
        breakdown = ConfidenceScorer.score_with_breakdown(250, 2000)
        assert breakdown["confidence_score"] == 0.125
        assert breakdown["risk_level"] == "Low Risk"
        assert pytest.approx(breakdown["percentage_of_disposable"], 0.1) == 12.5
        assert breakdown["color"] == "green"

    def test_comprehensive_high_risk_scenario(self):
        """Test complete high risk scenario."""
        breakdown = ConfidenceScorer.score_with_breakdown(900, 1000)
        assert breakdown["confidence_score"] == 0.9
        assert breakdown["risk_level"] == "High Risk"
        assert pytest.approx(breakdown["percentage_of_disposable"], 0.1) == 90.0
        assert breakdown["color"] == "red"


class TestScoreEdgeCases:
    """Tests for edge cases."""

    def test_very_large_numbers(self):
        """Test with very large numbers."""
        score = ConfidenceScorer.calculate_confidence_score(1000000, 5000000)
        assert pytest.approx(score, 0.01) == 0.2

    def test_very_small_numbers(self):
        """Test with very small numbers."""
        score = ConfidenceScorer.calculate_confidence_score(0.01, 0.1)
        # 0.01 / 0.1 = 0.1, but rounds to 0.01 in 3 decimals
        assert score == 0.01

    def test_single_cent_purchase(self):
        """Test purchase of single cent."""
        score = ConfidenceScorer.calculate_confidence_score(0.01, 100)
        assert score == 0.0  # Rounds to 0 when rounded to 3 decimals

    def test_realistic_scenario_1(self):
        """Test realistic scenario 1: Coffee."""
        # Monthly income: 5000, expenses: 1500, savings: 500
        # Disposable: 3000, Purchase: $5 coffee
        score = ConfidenceScorer.calculate_confidence_score(5, 3000)
        assert pytest.approx(score, 0.001) == 0.002
        risk = ConfidenceScorer.get_risk_level_from_score(score)
        assert risk == "Low Risk"

    def test_realistic_scenario_2(self):
        """Test realistic scenario 2: Monthly subscription."""
        # Disposable: 2000, Purchase: $50 streaming service
        score = ConfidenceScorer.calculate_confidence_score(50, 2000)
        assert pytest.approx(score, 0.001) == 0.025
        risk = ConfidenceScorer.get_risk_level_from_score(score)
        assert risk == "Low Risk"

    def test_realistic_scenario_3(self):
        """Test realistic scenario 3: Expensive gadget."""
        # Disposable: 1000, Purchase: $700 headphones
        score = ConfidenceScorer.calculate_confidence_score(700, 1000)
        assert score == 0.7
        risk = ConfidenceScorer.get_risk_level_from_score(score)
        assert risk == "Medium Risk"

    def test_realistic_scenario_4(self):
        """Test realistic scenario 4: Unaffordable purchase."""
        # Disposable: 500, Purchase: $1000 monitor
        score = ConfidenceScorer.calculate_confidence_score(1000, 500)
        assert score == 1.0
        risk = ConfidenceScorer.get_risk_level_from_score(score)
        assert risk == "High Risk"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
