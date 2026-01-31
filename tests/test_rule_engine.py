"""Tests for rule engine."""

import pytest
from src.rule_engine import RuleEngine, RiskLevel


class TestCalculateDisposableIncome:
    """Tests for disposable income calculation."""

    def test_basic_calculation(self):
        """Test basic disposable income calculation."""
        result = RuleEngine.calculate_disposable_income(5000, 1500, 500)
        assert result == 3000  # 5000 - 1500 - 500

    def test_zero_expenses_and_savings(self):
        """Test with zero expenses and savings."""
        result = RuleEngine.calculate_disposable_income(5000, 0, 0)
        assert result == 5000

    def test_no_savings_goal(self):
        """Test with no savings goal."""
        result = RuleEngine.calculate_disposable_income(5000, 1500, 0)
        assert result == 3500

    def test_negative_disposable_income(self):
        """Test when expenses exceed income."""
        result = RuleEngine.calculate_disposable_income(5000, 4000, 2000)
        assert result == -1000

    def test_equal_income_and_expenses(self):
        """Test when expenses equal income."""
        result = RuleEngine.calculate_disposable_income(5000, 5000, 0)
        assert result == 0

    def test_fractional_amounts(self):
        """Test with fractional amounts."""
        result = RuleEngine.calculate_disposable_income(5000.50, 1500.25, 500.75)
        assert pytest.approx(result, 0.01) == 3000.50


class TestCheckHardStops:
    """Tests for hard stop conditions."""

    def test_no_hard_stops(self):
        """Test when no hard stops are triggered."""
        triggered, reason = RuleEngine.check_hard_stops(5000, 3000, 1000)
        assert triggered is False
        assert reason == ""

    def test_zero_disposable_income_hard_stop(self):
        """Test hard stop when disposable income is zero."""
        triggered, reason = RuleEngine.check_hard_stops(5000, 0, 1000)
        assert triggered is True
        assert "No disposable income" in reason

    def test_negative_disposable_income_hard_stop(self):
        """Test hard stop when disposable income is negative."""
        triggered, reason = RuleEngine.check_hard_stops(5000, -500, 1000)
        assert triggered is True
        assert "No disposable income" in reason

    def test_purchase_exceeds_income_hard_stop(self):
        """Test hard stop when purchase exceeds monthly income."""
        triggered, reason = RuleEngine.check_hard_stops(5000, 2000, 6000)
        assert triggered is True
        assert "exceeds monthly income" in reason

    def test_purchase_equals_income(self):
        """Test when purchase equals monthly income."""
        triggered, reason = RuleEngine.check_hard_stops(5000, 2000, 5000)
        assert triggered is True
        assert "exceeds monthly income" in reason

    def test_purchase_just_below_income(self):
        """Test when purchase is just below monthly income."""
        triggered, reason = RuleEngine.check_hard_stops(5000, 2000, 4999)
        assert triggered is False

    def test_hard_stop_reason_includes_amounts(self):
        """Test that hard stop reasons include relevant amounts."""
        triggered, reason = RuleEngine.check_hard_stops(5000, -1000, 1000)
        assert "$" in reason
        assert "5000" in reason or "5000.00" in reason


class TestAssessRiskLevel:
    """Tests for risk level assessment."""

    def test_low_risk_at_threshold(self):
        """Test low risk at exactly 30% of disposable."""
        # 30% of 1000 = 300
        risk = RuleEngine.assess_risk_level(300, 1000)
        assert risk == RiskLevel.LOW

    def test_low_risk_below_threshold(self):
        """Test low risk below 30% of disposable."""
        # 20% of 1000 = 200
        risk = RuleEngine.assess_risk_level(200, 1000)
        assert risk == RiskLevel.LOW

    def test_medium_risk_at_low_threshold(self):
        """Test medium risk at 31% of disposable."""
        # 31% of 1000 = 310
        risk = RuleEngine.assess_risk_level(310, 1000)
        assert risk == RiskLevel.MEDIUM

    def test_medium_risk_at_high_threshold(self):
        """Test medium risk at exactly 60% of disposable."""
        # 60% of 1000 = 600
        risk = RuleEngine.assess_risk_level(600, 1000)
        assert risk == RiskLevel.MEDIUM

    def test_high_risk_above_medium_threshold(self):
        """Test high risk above 60% of disposable."""
        # 61% of 1000 = 610
        risk = RuleEngine.assess_risk_level(610, 1000)
        assert risk == RiskLevel.HIGH

    def test_high_risk_exceeds_disposable(self):
        """Test high risk when purchase exceeds disposable."""
        risk = RuleEngine.assess_risk_level(1500, 1000)
        assert risk == RiskLevel.HIGH

    def test_high_risk_zero_disposable(self):
        """Test high risk with zero disposable income."""
        risk = RuleEngine.assess_risk_level(100, 0)
        assert risk == RiskLevel.HIGH

    def test_high_risk_negative_disposable(self):
        """Test high risk with negative disposable income."""
        risk = RuleEngine.assess_risk_level(100, -500)
        assert risk == RiskLevel.HIGH

    def test_risk_boundary_cases(self):
        """Test risk assessment at exact boundaries."""
        # Just under low threshold
        risk = RuleEngine.assess_risk_level(299.99, 1000)
        assert risk == RiskLevel.LOW

        # Just over low threshold
        risk = RuleEngine.assess_risk_level(300.01, 1000)
        assert risk == RiskLevel.MEDIUM

        # Just over medium threshold
        risk = RuleEngine.assess_risk_level(600.01, 1000)
        assert risk == RiskLevel.HIGH


class TestEvaluatePurchase:
    """Tests for comprehensive purchase evaluation."""

    def test_low_risk_purchase(self):
        """Test evaluation of low risk purchase."""
        result = RuleEngine.evaluate_purchase(5000, 1500, 500, 500)
        assert result["disposable_income"] == 3000
        assert result["hard_stop_triggered"] is False
        assert result["risk_level"] == RiskLevel.LOW
        assert result["can_afford"] is True
        assert pytest.approx(result["percentage_of_disposable"], 0.01) == 500 / 3000

    def test_medium_risk_purchase(self):
        """Test evaluation of medium risk purchase."""
        result = RuleEngine.evaluate_purchase(5000, 1500, 500, 1500)
        assert result["disposable_income"] == 3000
        assert result["hard_stop_triggered"] is False
        assert result["risk_level"] == RiskLevel.MEDIUM
        assert result["can_afford"] is True

    def test_high_risk_purchase(self):
        """Test evaluation of high risk purchase."""
        result = RuleEngine.evaluate_purchase(5000, 1500, 500, 2500)
        assert result["disposable_income"] == 3000
        assert result["hard_stop_triggered"] is False
        assert result["risk_level"] == RiskLevel.HIGH
        assert result["can_afford"] is True

    def test_hard_stop_negative_disposable(self):
        """Test evaluation with negative disposable income."""
        result = RuleEngine.evaluate_purchase(5000, 4000, 2000, 500)
        assert result["disposable_income"] == -1000
        assert result["hard_stop_triggered"] is True
        assert result["risk_level"] == RiskLevel.HIGH
        assert result["can_afford"] is False
        assert "No disposable income" in result["hard_stop_reason"]

    def test_hard_stop_exceeds_income(self):
        """Test evaluation when purchase exceeds income."""
        result = RuleEngine.evaluate_purchase(5000, 1500, 500, 6000)
        assert result["hard_stop_triggered"] is True
        assert result["risk_level"] == RiskLevel.HIGH
        assert result["can_afford"] is False
        assert "exceeds monthly income" in result["hard_stop_reason"]

    def test_remaining_after_purchase(self):
        """Test calculation of remaining disposable income."""
        result = RuleEngine.evaluate_purchase(5000, 1500, 500, 1000)
        assert result["remaining_after_purchase"] == 2000  # 3000 - 1000

    def test_percentage_calculations(self):
        """Test percentage calculations."""
        result = RuleEngine.evaluate_purchase(10000, 3000, 1000, 1200)
        # Disposable = 10000 - 3000 - 1000 = 6000
        # Percentage = 1200 / 6000 = 0.2 = 20%
        assert pytest.approx(result["percentage_of_disposable"], 0.01) == 0.2
        assert pytest.approx(result["percentage_of_disposable_pct"], 0.1) == 20.0

    def test_realistic_scenario_1(self):
        """Test realistic scenario 1: Student budget."""
        # Student with 2000/month income
        result = RuleEngine.evaluate_purchase(
            monthly_income=2000,
            fixed_expenses=800,  # Rent
            savings_goal=200,  # Savings
            purchase_cost=400,  # Gaming console
        )
        # Disposable = 2000 - 800 - 200 = 1000
        assert result["disposable_income"] == 1000
        assert result["risk_level"] == RiskLevel.MEDIUM  # 400 is 40% of 1000
        assert result["can_afford"] is True

    def test_realistic_scenario_2(self):
        """Test realistic scenario 2: Tight budget."""
        result = RuleEngine.evaluate_purchase(
            monthly_income=3000,
            fixed_expenses=2500,  # Very high fixed costs
            savings_goal=300,  # Savings goal
            purchase_cost=100,  # Modest purchase
        )
        # Disposable = 3000 - 2500 - 300 = 200
        assert result["disposable_income"] == 200
        assert result["hard_stop_triggered"] is False
        assert result["risk_level"] == RiskLevel.MEDIUM  # 100 is 50% of 200

    def test_realistic_scenario_3(self):
        """Test realistic scenario 3: Cannot afford."""
        result = RuleEngine.evaluate_purchase(
            monthly_income=3000,
            fixed_expenses=2500,
            savings_goal=300,
            purchase_cost=1000,
        )
        # Disposable = 3000 - 2500 - 300 = 200
        # Hard stop NOT triggered (1000 < 3000 income), but High Risk (1000 >> 200 disposable)
        assert result["disposable_income"] == 200
        assert result["hard_stop_triggered"] is False
        assert result["risk_level"] == RiskLevel.HIGH
        assert (
            result["can_afford"] is True
        )  # Technically can afford from income, but risky


class TestRiskLevelEnum:
    """Tests for RiskLevel enum."""

    def test_risk_level_values(self):
        """Test that risk level values are as expected."""
        assert RiskLevel.LOW.value == "Low Risk"
        assert RiskLevel.MEDIUM.value == "Medium Risk"
        assert RiskLevel.HIGH.value == "High Risk"

    def test_risk_level_string_comparison(self):
        """Test string comparison with risk levels."""
        assert str(RiskLevel.LOW) == "RiskLevel.LOW"
        assert RiskLevel.LOW.value == "Low Risk"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
