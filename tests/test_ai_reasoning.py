"""Tests for AI reasoning module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.ai_reasoning import AIReasoning


class TestAIReasoningInitialization:
    """Tests for AIReasoning initialization."""

    def test_initialization(self):
        """Test AIReasoning initializes correctly."""
        reasoner = AIReasoning()
        assert reasoner is not None
        assert reasoner.conversation_history == []

    def test_system_prompt_contains_guardrails(self):
        """Test that system prompt includes necessary guardrails."""
        assert "NOT a financial advisor" in AIReasoning.SYSTEM_PROMPT
        assert "must NOT give investment" in AIReasoning.SYSTEM_PROMPT
        assert "This is not financial advice" in AIReasoning.SYSTEM_PROMPT


class TestBuildAnalysisPrompt:
    """Tests for analysis prompt building."""

    def test_prompt_includes_all_parameters(self):
        """Test that prompt includes all financial parameters."""
        reasoner = AIReasoning()
        prompt = reasoner._build_analysis_prompt(
            purchase_item="Laptop",
            purchase_cost=1000,
            monthly_income=5000,
            fixed_expenses=2000,
            savings_goal=500,
            disposable_income=2500,
            risk_level="Medium Risk",
            confidence_score=0.5,
        )

        assert "Laptop" in prompt
        assert "1000" in prompt
        assert "5000" in prompt
        assert "2000" in prompt
        assert "Medium Risk" in prompt
        assert "JSON" in prompt

    def test_prompt_calculates_percentage(self):
        """Test that prompt includes purchase cost and disposable income."""
        reasoner = AIReasoning()
        prompt = reasoner._build_analysis_prompt(
            purchase_item="Item",
            purchase_cost=500,
            monthly_income=5000,
            fixed_expenses=2000,
            savings_goal=500,
            disposable_income=2500,
            risk_level="Medium Risk",
            confidence_score=0.5,
        )

        assert "500" in prompt
        assert "2500" in prompt
        assert "INPUTS:" in prompt

    def test_prompt_includes_guardrail_reminder(self):
        """Test that prompt requests JSON-only response."""
        reasoner = AIReasoning()
        prompt = reasoner._build_analysis_prompt(
            purchase_item="Item",
            purchase_cost=100,
            monthly_income=5000,
            fixed_expenses=2000,
            savings_goal=500,
            disposable_income=2500,
            risk_level="Low Risk",
            confidence_score=0.1,
        )

        assert "JSON" in prompt
        assert "ONLY valid JSON" in prompt


class TestExtractAlternatives:
    """Tests for fallback alternatives."""

    def test_fallback_json_response_low_risk(self):
        """Test fallback JSON response for low risk."""
        result = AIReasoning._get_fallback_json_response("Low Risk", 100, 1000)
        assert result["decision"] == "Low Risk"
        assert result["confidence_score"] == 0.1
        assert "not financial advice" in result["explanation"].lower()
        assert isinstance(result["alternatives"], list)

    def test_fallback_json_response_medium_risk(self):
        """Test fallback JSON response for medium risk."""
        result = AIReasoning._get_fallback_json_response("Medium Risk", 500, 1000)
        assert result["decision"] == "Medium Risk"
        assert result["confidence_score"] == 0.5
        assert len(result["alternatives"]) >= 2

    def test_fallback_json_response_high_risk(self):
        """Test fallback JSON response for high risk."""
        result = AIReasoning._get_fallback_json_response("High Risk", 800, 1000)
        assert result["decision"] == "High Risk"
        assert result["confidence_score"] == 0.8
        assert len(result["alternatives"]) >= 2

    def test_fallback_json_with_zero_disposable(self):
        """Test fallback JSON response with zero disposable income."""
        result = AIReasoning._get_fallback_json_response("High Risk", 100, 0)
        assert result["decision"] == "High Risk"
        assert result["confidence_score"] == 1.0
        assert "not financial advice" in result["explanation"].lower()


class TestFallbackAlternatives:
    """Tests for fallback response structure."""

    def test_fallback_response_structure_low_risk(self):
        """Test fallback response has correct structure for low risk."""
        result = AIReasoning._get_fallback_json_response("Low Risk", 100, 1000)
        assert "decision" in result
        assert "confidence_score" in result
        assert "explanation" in result
        assert "alternatives" in result
        assert isinstance(result["alternatives"], list)

    def test_fallback_response_structure_medium_risk(self):
        """Test fallback response has correct structure for medium risk."""
        result = AIReasoning._get_fallback_json_response("Medium Risk", 500, 1000)
        assert isinstance(result, dict)
        assert result["decision"] == "Medium Risk"

    def test_fallback_response_structure_high_risk(self):
        """Test fallback response has correct structure for high risk."""
        result = AIReasoning._get_fallback_json_response("High Risk", 800, 1000)
        assert isinstance(result, dict)
        assert result["decision"] == "High Risk"


class TestConversationHistory:
    """Tests for conversation history management."""

    def test_reset_conversation(self):
        """Test that conversation can be reset."""
        reasoner = AIReasoning()
        reasoner.conversation_history.append({"role": "user", "content": "test"})
        assert len(reasoner.conversation_history) > 0

        reasoner.reset_conversation()
        assert reasoner.conversation_history == []

    def test_conversation_history_is_list(self):
        """Test that conversation history is properly initialized."""
        reasoner = AIReasoning()
        assert isinstance(reasoner.conversation_history, list)


class TestGuardrails:
    """Tests for guardrail enforcement."""

    def test_system_prompt_contains_no_investment_advice(self):
        """Test that system prompt forbids investment advice."""
        assert "investment" in AIReasoning.SYSTEM_PROMPT.lower()
        assert (
            "NOT" in AIReasoning.SYSTEM_PROMPT
            or "must not" in AIReasoning.SYSTEM_PROMPT.lower()
        )

    def test_system_prompt_contains_no_credit_advice(self):
        """Test that system prompt forbids credit advice."""
        assert "credit" in AIReasoning.SYSTEM_PROMPT.lower()

    def test_system_prompt_contains_no_tax_advice(self):
        """Test that system prompt forbids tax advice."""
        assert "tax" in AIReasoning.SYSTEM_PROMPT.lower()

    def test_explanation_includes_disclaimer(self):
        """Test that explanations include non-advisory disclaimer."""
        result = AIReasoning._get_fallback_json_response("Low Risk", 100, 1000)
        assert "not financial advice" in result["explanation"].lower()


class TestMockedAPIIntegration:
    """Tests with mocked API calls."""

    @patch("src.ai_reasoning.OpenAI")
    def test_generate_explanation_with_mock_api(self, mock_openai_class):
        """Test explanation generation with mocked OpenAI API."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Mock the response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            '{"decision": "Low Risk", "confidence_score": 0.1, "explanation": "This is safe.", "alternatives": []}'
        )
        mock_client.chat.completions.create.return_value = mock_response

        # Create reasoner with mocked client
        reasoner = AIReasoning()
        reasoner.client = mock_client

        # Generate explanation
        result = reasoner.generate_explanation(
            purchase_item="Test Item",
            purchase_cost=100,
            monthly_income=5000,
            fixed_expenses=2000,
            savings_goal=500,
            disposable_income=2500,
            risk_level="Low Risk",
            confidence_score=0.1,
        )

        # Verify structure
        assert "decision" in result
        assert "confidence_score" in result
        assert "explanation" in result
        assert "alternatives" in result

    @patch("src.ai_reasoning.OpenAI")
    def test_conversation_history_updated(self, mock_openai_class):
        """Test that conversation history is updated after API call."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            '{"decision": "Medium Risk", "confidence_score": 0.5, "explanation": "Consider alternatives.", "alternatives": ["opt1"]}'
        )
        mock_client.chat.completions.create.return_value = mock_response

        reasoner = AIReasoning()
        reasoner.client = mock_client

        result = reasoner.generate_explanation(
            purchase_item="Item",
            purchase_cost=500,
            monthly_income=5000,
            fixed_expenses=2000,
            savings_goal=500,
            disposable_income=2500,
            risk_level="Medium Risk",
            confidence_score=0.5,
        )

        # Verify conversation history updated
        assert len(reasoner.conversation_history) > 0
        assert result["decision"] == "Medium Risk"


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_very_high_cost_percentage(self):
        """Test when purchase cost exceeds disposable income significantly."""
        result = AIReasoning._get_fallback_json_response("High Risk", 5000, 100)
        assert result["confidence_score"] == 1.0  # Clamped at 1.0
        assert result["decision"] == "High Risk"

    def test_very_low_cost_percentage(self):
        """Test when purchase cost is tiny fraction of disposable."""
        result = AIReasoning._get_fallback_json_response("Low Risk", 1, 5000)
        assert result["confidence_score"] == 0.0
        assert result["decision"] == "Low Risk"


class TestResponseContent:
    """Tests for response content structure."""

    def test_fallback_response_includes_all_keys(self):
        """Test that fallback responses have all required keys."""
        result = AIReasoning._get_fallback_json_response("Low Risk", 100, 1000)

        assert "decision" in result
        assert "confidence_score" in result
        assert "explanation" in result
        assert "alternatives" in result
        assert isinstance(result["explanation"], str)
        assert isinstance(result["alternatives"], list)

    def test_explanation_length_reasonable(self):
        """Test that explanations are of reasonable length."""
        result = AIReasoning._get_fallback_json_response("Medium Risk", 500, 1000)
        assert len(result["explanation"]) > 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
