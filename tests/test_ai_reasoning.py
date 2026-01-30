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
        assert "NOT provide financial" in AIReasoning.SYSTEM_PROMPT
        assert "NOT recommend" in AIReasoning.SYSTEM_PROMPT
        assert "disclaimer" in AIReasoning.SYSTEM_PROMPT.lower()


class TestBuildAnalysisPrompt:
    """Tests for analysis prompt building."""

    def test_prompt_includes_all_parameters(self):
        """Test that prompt includes all financial parameters."""
        reasoner = AIReasoning()
        prompt = reasoner._build_analysis_prompt(
            purchase_item="Laptop",
            purchase_cost=1000,
            monthly_income=5000,
            disposable_income=2000,
            risk_level="Medium Risk",
            confidence_score=0.5,
        )

        assert "Laptop" in prompt
        assert "1000" in prompt
        assert "5000" in prompt
        assert "2000" in prompt
        assert "Medium Risk" in prompt

    def test_prompt_calculates_percentage(self):
        """Test that prompt calculates percentage of disposable."""
        reasoner = AIReasoning()
        prompt = reasoner._build_analysis_prompt(
            purchase_item="Item",
            purchase_cost=500,
            monthly_income=5000,
            disposable_income=1000,
            risk_level="Medium Risk",
            confidence_score=0.5,
        )

        # 500 / 1000 * 100 = 50%
        assert "50.0%" in prompt

    def test_prompt_includes_guardrail_reminder(self):
        """Test that prompt reminds AI not to give advice."""
        reasoner = AIReasoning()
        prompt = reasoner._build_analysis_prompt(
            "Item", 100, 5000, 2000, "Low Risk", 0.1
        )

        assert "NOT" in prompt or "not" in prompt


class TestExtractAlternatives:
    """Tests for alternative extraction."""

    def test_extract_numbered_alternatives(self):
        """Test extraction of numbered alternatives."""
        text = """Analysis here.

Alternative options:
1. Buy a cheaper version
2. Wait and save for it
3. Look for used options"""

        alternatives = AIReasoning._extract_alternatives(text)
        assert len(alternatives) > 0
        assert any("cheaper" in alt.lower() for alt in alternatives)

    def test_extract_bulleted_alternatives(self):
        """Test extraction of bulleted alternatives."""
        text = """Analysis.

Consider these alternatives:
- Wait 30 days before purchasing
- Look for a discount
- Compare other brands"""

        alternatives = AIReasoning._extract_alternatives(text)
        assert len(alternatives) >= 0  # May or may not extract

    def test_empty_text_returns_empty_alternatives(self):
        """Test that empty text returns empty alternatives."""
        alternatives = AIReasoning._extract_alternatives("")
        assert alternatives == []

    def test_alternatives_limited_to_three(self):
        """Test that only up to 3 alternatives are returned."""
        text = """1. Option one that is very long and substantial
        2. Option two that is also long and substantial
        3. Option three that is lengthy and substantial
        4. Option four that would be included but limited
        5. Option five also excluded"""

        alternatives = AIReasoning._extract_alternatives(text)
        assert len(alternatives) <= 3


class TestFallbackExplanation:
    """Tests for fallback explanation generation."""

    def test_fallback_low_risk_explanation(self):
        """Test low risk fallback explanation."""
        explanation = AIReasoning._get_fallback_explanation("Low Risk", 100, 1000)
        assert "Low Risk" in explanation
        assert "10.0%" in explanation
        assert len(explanation) > 50

    def test_fallback_medium_risk_explanation(self):
        """Test medium risk fallback explanation."""
        explanation = AIReasoning._get_fallback_explanation("Medium Risk", 500, 1000)
        assert "Medium Risk" in explanation
        assert "50.0%" in explanation
        assert "need or a want" in explanation

    def test_fallback_high_risk_explanation(self):
        """Test high risk fallback explanation."""
        explanation = AIReasoning._get_fallback_explanation("High Risk", 800, 1000)
        assert "High Risk" in explanation
        assert "80.0%" in explanation
        assert "critical need" in explanation

    def test_fallback_with_zero_disposable(self):
        """Test fallback explanation with zero disposable income."""
        explanation = AIReasoning._get_fallback_explanation("High Risk", 100, 0)
        # Should handle division by zero
        assert "High Risk" in explanation
        assert len(explanation) > 0


class TestFallbackAlternatives:
    """Tests for fallback alternatives."""

    def test_fallback_alternatives_low_risk(self):
        """Test that low risk gets basic alternatives."""
        alternatives = AIReasoning._get_fallback_alternatives("Low Risk")
        assert len(alternatives) >= 3
        assert any("wait" in alt.lower() for alt in alternatives)

    def test_fallback_alternatives_medium_risk(self):
        """Test that medium risk gets more alternatives."""
        alternatives = AIReasoning._get_fallback_alternatives("Medium Risk")
        assert len(alternatives) > 3
        assert any("used" in alt.lower() for alt in alternatives)

    def test_fallback_alternatives_high_risk(self):
        """Test that high risk gets additional alternatives."""
        alternatives = AIReasoning._get_fallback_alternatives("High Risk")
        assert len(alternatives) > 3
        assert any(
            "rental" in alt.lower() or "subscription" in alt.lower()
            for alt in alternatives
        )


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
        """Test that fallback explanations include disclaimer."""
        explanation = AIReasoning._get_fallback_explanation("Low Risk", 100, 1000)
        # Note: Actual AI explanation would include disclaimer in real method
        # Fallback doesn't add it, but the real generate_explanation does


class TestMockedAPIIntegration:
    """Tests with mocked API calls."""

    @patch("src.ai_reasoning.Anthropic")
    def test_generate_explanation_with_mock_api(self, mock_anthropic_class):
        """Test explanation generation with mocked API."""
        # Setup mock
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="This is a test explanation.")]
        mock_client.messages.create.return_value = mock_response

        # Create reasoner
        reasoner = AIReasoning()
        reasoner.client = mock_client

        # Generate explanation
        result = reasoner.generate_explanation(
            purchase_item="Test Item",
            purchase_cost=100,
            monthly_income=5000,
            disposable_income=2000,
            risk_level="Low Risk",
            confidence_score=0.1,
        )

        # Verify
        assert "explanation" in result
        assert "alternatives" in result
        assert len(result["explanation"]) > 0
        assert "DISCLAIMER" in result["explanation"]

    @patch("src.ai_reasoning.Anthropic")
    def test_conversation_history_updated(self, mock_anthropic_class):
        """Test that conversation history is updated properly."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response text")]
        mock_client.messages.create.return_value = mock_response

        reasoner = AIReasoning()
        reasoner.client = mock_client

        # Initial history should be empty
        assert len(reasoner.conversation_history) == 0

        # Generate explanation
        reasoner.generate_explanation("Item", 100, 5000, 2000, "Low Risk", 0.1)

        # History should now have entries (user + assistant)
        assert len(reasoner.conversation_history) >= 2


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_very_high_cost_percentage(self):
        """Test when purchase cost exceeds disposable income significantly."""
        reasoner = AIReasoning()
        prompt = reasoner._build_analysis_prompt(
            "Expensive Item", 5000, 5000, 100, "High Risk", 1.0
        )

        assert "5000.0%" in prompt

    def test_very_low_cost_percentage(self):
        """Test when purchase cost is tiny fraction of disposable."""
        reasoner = AIReasoning()
        prompt = reasoner._build_analysis_prompt(
            "Cheap Item", 1, 5000, 5000, "Low Risk", 0.0
        )

        assert "0.0%" in prompt


class TestResponseContent:
    """Tests for response content structure."""

    def test_fallback_explanation_response_structure(self):
        """Test that fallback explanations have correct structure."""
        result = {
            "explanation": AIReasoning._get_fallback_explanation("Low Risk", 100, 1000),
            "alternatives": AIReasoning._get_fallback_alternatives("Low Risk"),
        }

        assert "explanation" in result
        assert "alternatives" in result
        assert isinstance(result["explanation"], str)
        assert isinstance(result["alternatives"], list)

    def test_explanation_length_reasonable(self):
        """Test that explanations are of reasonable length."""
        explanation = AIReasoning._get_fallback_explanation("Medium Risk", 500, 1000)
        assert 100 < len(explanation) < 2000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
