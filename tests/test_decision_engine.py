"""Integration tests for the decision engine."""

import pytest
from unittest.mock import MagicMock, patch
from src.decision_engine import DecisionEngine


class TestDecisionEngineInitialization:
    """Tests for DecisionEngine initialization."""

    def test_initialization_with_ai(self):
        """Test initialization with AI enabled."""
        engine = DecisionEngine(use_ai=True)
        assert engine.use_ai is True
        assert engine.ai_reasoner is not None

    def test_initialization_without_ai(self):
        """Test initialization without AI."""
        engine = DecisionEngine(use_ai=False)
        assert engine.use_ai is False
        assert engine.ai_reasoner is None


class TestDecisionEngineEvaluation:
    """Tests for complete evaluation flow."""

    def test_valid_low_risk_evaluation(self):
        """Test evaluation of valid low risk purchase."""
        engine = DecisionEngine(use_ai=False)

        input_data = {
            "monthly_income": 5000,
            "fixed_expenses": 1500,
            "savings_goal": 500,
            "planned_purchase": {"item": "Coffee Maker", "cost": 100},
        }

        report = engine.evaluate(input_data)

        assert report["status"] == "success"
        assert report["input_validation"]["status"] == "valid"
        assert report["input_validation"]["purchase_item"] == "Coffee Maker"
        assert report["financial_analysis"]["can_afford"] is True
        assert report["risk_assessment"]["risk_level"] == "Low Risk"
        assert report["ai_reasoning"]["mode"] == "fallback"

    def test_valid_medium_risk_evaluation(self):
        """Test evaluation of medium risk purchase."""
        engine = DecisionEngine(use_ai=False)

        input_data = {
            "monthly_income": 5000,
            "fixed_expenses": 1500,
            "savings_goal": 500,
            "planned_purchase": {"item": "Gaming Laptop", "cost": 1500},
        }

        report = engine.evaluate(input_data)

        assert report["status"] == "success"
        assert report["risk_assessment"]["risk_level"] == "Medium Risk"
        assert report["financial_analysis"]["hard_stop_triggered"] is False

    def test_valid_high_risk_evaluation(self):
        """Test evaluation of high risk purchase."""
        engine = DecisionEngine(use_ai=False)

        input_data = {
            "monthly_income": 5000,
            "fixed_expenses": 1500,
            "savings_goal": 500,
            "planned_purchase": {"item": "High-end Monitor", "cost": 2800},
        }

        report = engine.evaluate(input_data)

        assert report["status"] == "success"
        assert report["risk_assessment"]["risk_level"] == "High Risk"
        assert report["financial_analysis"]["hard_stop_triggered"] is False
        assert report["financial_analysis"]["can_afford"] is True

    def test_hard_stop_evaluation(self):
        """Test evaluation when hard stop is triggered."""
        engine = DecisionEngine(use_ai=False)

        input_data = {
            "monthly_income": 3000,
            "fixed_expenses": 2500,
            "savings_goal": 500,
            "planned_purchase": {"item": "Expensive Item", "cost": 100},
        }

        report = engine.evaluate(input_data)

        assert report["status"] == "success"
        assert report["financial_analysis"]["hard_stop_triggered"] is True
        assert report["financial_analysis"]["can_afford"] is False
        assert "CANNOT AFFORD" in report["final_decision"]["summary"]

    def test_invalid_input_evaluation(self):
        """Test evaluation with invalid input."""
        engine = DecisionEngine(use_ai=False)

        input_data = {
            "monthly_income": -5000,  # Invalid: negative
            "fixed_expenses": 1500,
            "savings_goal": 500,
            "planned_purchase": {"item": "Item", "cost": 100},
        }

        report = engine.evaluate(input_data)

        assert report["status"] == "validation_error"
        assert report["error"] is not None


class TestDecisionEngineReportStructure:
    """Tests for report structure and content."""

    def test_report_has_all_required_fields(self):
        """Test that report contains all required fields."""
        engine = DecisionEngine(use_ai=False)

        input_data = {
            "monthly_income": 5000,
            "fixed_expenses": 1500,
            "savings_goal": 500,
            "planned_purchase": {"item": "Item", "cost": 500},
        }

        report = engine.evaluate(input_data)

        required_fields = [
            "timestamp",
            "status",
            "input_validation",
            "financial_analysis",
            "risk_assessment",
            "ai_reasoning",
            "final_decision",
        ]

        for field in required_fields:
            assert field in report

    def test_final_decision_structure(self):
        """Test final decision has correct structure."""
        engine = DecisionEngine(use_ai=False)

        input_data = {
            "monthly_income": 5000,
            "fixed_expenses": 1500,
            "savings_goal": 500,
            "planned_purchase": {"item": "Item", "cost": 500},
        }

        report = engine.evaluate(input_data)
        final = report["final_decision"]

        assert "summary" in final
        assert "recommendation" in final
        assert "key_metrics" in final
        assert "next_steps" in final
        assert isinstance(final["next_steps"], list)

    def test_key_metrics_calculations(self):
        """Test that key metrics are calculated correctly."""
        engine = DecisionEngine(use_ai=False)

        income = 5000
        expenses = 1500
        savings = 500
        cost = 1000

        input_data = {
            "monthly_income": income,
            "fixed_expenses": expenses,
            "savings_goal": savings,
            "planned_purchase": {"item": "Item", "cost": cost},
        }

        report = engine.evaluate(input_data)
        metrics = report["final_decision"]["key_metrics"]

        # Disposable = 5000 - 1500 - 500 = 3000
        # Remaining = 3000 - 1000 = 2000
        # Percentage = 1000 / 3000 * 100 = 33.33%

        assert metrics["monthly_income"] == income
        assert metrics["disposable_income"] == 3000
        assert metrics["purchase_cost"] == cost
        assert metrics["remaining_after_purchase"] == 2000
        assert pytest.approx(metrics["percentage_of_disposable"], 0.1) == 33.33


class TestDecisionEngineJsonOutput:
    """Tests for JSON output."""

    def test_json_report_is_valid(self):
        """Test that JSON report can be parsed."""
        engine = DecisionEngine(use_ai=False)

        input_data = {
            "monthly_income": 5000,
            "fixed_expenses": 1500,
            "savings_goal": 500,
            "planned_purchase": {"item": "Item", "cost": 500},
        }

        json_str = engine.get_json_report(input_data)
        import json

        report = json.loads(json_str)

        assert report["status"] == "success"
        assert "final_decision" in report


class TestDecisionEngineFallbackMode:
    """Tests for fallback reasoning mode."""

    def test_fallback_low_risk_summary(self):
        """Test fallback summary for low risk."""
        engine = DecisionEngine(use_ai=False)

        input_data = {
            "monthly_income": 5000,
            "fixed_expenses": 1500,
            "savings_goal": 500,
            "planned_purchase": {"item": "Item", "cost": 100},
        }

        report = engine.evaluate(input_data)
        summary = report["final_decision"]["summary"]

        assert "LOW RISK" in summary
        assert "✅" in summary

    def test_fallback_medium_risk_summary(self):
        """Test fallback summary for medium risk."""
        engine = DecisionEngine(use_ai=False)

        input_data = {
            "monthly_income": 5000,
            "fixed_expenses": 1500,
            "savings_goal": 500,
            "planned_purchase": {"item": "Item", "cost": 1500},
        }

        report = engine.evaluate(input_data)
        summary = report["final_decision"]["summary"]

        assert "MEDIUM RISK" in summary
        assert "⚠️" in summary

    def test_fallback_high_risk_summary(self):
        """Test fallback summary for high risk."""
        engine = DecisionEngine(use_ai=False)

        input_data = {
            "monthly_income": 5000,
            "fixed_expenses": 1500,
            "savings_goal": 500,
            "planned_purchase": {"item": "Item", "cost": 2800},
        }

        report = engine.evaluate(input_data)
        summary = report["final_decision"]["summary"]

        assert "HIGH RISK" in summary
        assert "🚨" in summary

    def test_fallback_hard_stop_summary(self):
        """Test fallback summary when hard stop triggered."""
        engine = DecisionEngine(use_ai=False)

        input_data = {
            "monthly_income": 3000,
            "fixed_expenses": 2500,
            "savings_goal": 500,
            "planned_purchase": {"item": "Item", "cost": 100},
        }

        report = engine.evaluate(input_data)
        summary = report["final_decision"]["summary"]

        assert "CANNOT AFFORD" in summary


class TestDecisionEngineEdgeCases:
    """Tests for edge cases."""

    def test_zero_expenses_and_savings(self):
        """Test with zero expenses and savings."""
        engine = DecisionEngine(use_ai=False)

        input_data = {
            "monthly_income": 5000,
            "fixed_expenses": 0,
            "savings_goal": 0,
            "planned_purchase": {"item": "Item", "cost": 1000},
        }

        report = engine.evaluate(input_data)

        assert report["status"] == "success"
        assert report["financial_analysis"]["disposable_income"] == 5000

    def test_very_large_numbers(self):
        """Test with very large numbers."""
        engine = DecisionEngine(use_ai=False)

        input_data = {
            "monthly_income": 100000,
            "fixed_expenses": 30000,
            "savings_goal": 10000,
            "planned_purchase": {"item": "Luxury Item", "cost": 50000},
        }

        report = engine.evaluate(input_data)

        # Disposable = 100000 - 30000 - 10000 = 60000
        # 50000 / 60000 = 0.833 = 83.3% = High Risk
        assert report["status"] == "success"
        assert report["risk_assessment"]["risk_level"] == "High Risk"

    def test_missing_required_field(self):
        """Test with missing required field."""
        engine = DecisionEngine(use_ai=False)

        input_data = {
            "monthly_income": 5000,
            "fixed_expenses": 1500,
            # Missing savings_goal
            "planned_purchase": {"item": "Item", "cost": 500},
        }

        report = engine.evaluate(input_data)

        assert report["status"] == "validation_error"


class TestResetConversation:
    """Tests for conversation reset."""

    def test_reset_conversation_with_ai(self):
        """Test that conversation can be reset."""
        engine = DecisionEngine(use_ai=True)
        engine.reset_ai_conversation()

        # Should not raise an error
        assert engine.ai_reasoner is not None

    def test_reset_conversation_without_ai(self):
        """Test reset when AI is disabled."""
        engine = DecisionEngine(use_ai=False)
        engine.reset_ai_conversation()  # Should not raise error

        assert engine.ai_reasoner is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
