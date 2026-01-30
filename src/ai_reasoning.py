"""AI Reasoning module for SpendSense Agent - Claude integration."""

import json
import logging
from typing import Optional, List, Dict
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class AIReasoning:
    """
    Integrates Claude API for AI-powered explanations and alternatives.

    Responsible for:
    - Generating natural language explanations for purchase decisions
    - Suggesting safer alternatives
    - Adding contextual reasoning
    - Enforcing guardrails to prevent financial advice
    """

    # System prompt with guardrails
    SYSTEM_PROMPT = """You are a budgeting decision assistant helping users understand financial decisions.

IMPORTANT GUARDRAILS:
- You must NOT provide financial, tax, investment, or credit advice
- You must NOT recommend buying or not buying - only explain risks and suggest alternatives
- You must NOT make assumptions about user's future income or circumstances
- You must ALWAYS include a disclaimer that this is not financial advice
- Be conservative and cautious in your explanations
- Focus on risk analysis, not recommendations

Your role is to:
1. Explain why a purchase is Low/Medium/High risk
2. Suggest safer alternatives or ways to reduce risk
3. Provide context and reasoning
4. Always remind the user to make their own decision

Be clear, concise, and avoid jargon."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Reasoning with Claude API.

        Args:
            api_key: Anthropic API key (uses ANTHROPIC_API_KEY env var if not provided)
        """
        self.client = Anthropic()
        self.conversation_history = []
        logger.info("AIReasoning initialized with Claude API")

    def _build_analysis_prompt(
        self,
        purchase_item: str,
        purchase_cost: float,
        monthly_income: float,
        disposable_income: float,
        risk_level: str,
        confidence_score: float,
    ) -> str:
        """
        Build the analysis prompt for Claude.

        Args:
            purchase_item: Item being purchased
            purchase_cost: Cost of purchase
            monthly_income: Monthly income
            disposable_income: Available disposable income
            risk_level: Risk level assessment
            confidence_score: Confidence score

        Returns:
            Formatted prompt for Claude
        """
        prompt = f"""User Financial Situation:
- Monthly Income: ${monthly_income:.2f}
- Available for Discretionary Spending (Disposable Income): ${disposable_income:.2f}
- Purchase: {purchase_item}
- Cost: ${purchase_cost:.2f}

Risk Assessment:
- Risk Level: {risk_level}
- Confidence Score: {confidence_score:.1%}
- Percentage of Disposable Income: {(purchase_cost/max(disposable_income, 1))*100:.1f}%

Task:
1. Explain why this purchase is classified as {risk_level}
2. List the key financial risks or benefits
3. Suggest 2-3 safer alternatives or ways to reduce risk (e.g., waiting, buying used, finding cheaper options)
4. Provide any additional financial context

Important: Remember NOT to tell them to buy or not buy. Explain the situation and empower them to decide."""

        return prompt

    def generate_explanation(
        self,
        purchase_item: str,
        purchase_cost: float,
        monthly_income: float,
        disposable_income: float,
        risk_level: str,
        confidence_score: float,
    ) -> Dict[str, str]:
        """
        Generate AI-powered explanation for a purchase decision.

        Args:
            purchase_item: Item being purchased
            purchase_cost: Cost of purchase
            monthly_income: Monthly income
            disposable_income: Available disposable income
            risk_level: Risk level assessment
            confidence_score: Confidence score

        Returns:
            Dictionary with explanation and alternatives
        """
        try:
            # Build the prompt
            prompt = self._build_analysis_prompt(
                purchase_item,
                purchase_cost,
                monthly_income,
                disposable_income,
                risk_level,
                confidence_score,
            )

            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})

            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=self.SYSTEM_PROMPT,
                messages=self.conversation_history,
            )

            # Extract response
            explanation = response.content[0].text

            # Add to conversation history
            self.conversation_history.append(
                {"role": "assistant", "content": explanation}
            )

            # Add disclaimer
            explanation_with_disclaimer = f"""{explanation}

---
[DISCLAIMER] This analysis is for informational purposes only and is not financial advice. You should make your own informed decision based on your complete financial situation. Consider consulting with a financial advisor if needed."""

            logger.info(f"AI explanation generated for {purchase_item}")

            return {
                "explanation": explanation_with_disclaimer,
                "alternatives": self._extract_alternatives(explanation),
            }

        except Exception as e:
            logger.error(f"Error generating AI explanation: {str(e)}")
            return {
                "explanation": self._get_fallback_explanation(
                    risk_level, purchase_cost, disposable_income
                ),
                "alternatives": self._get_fallback_alternatives(risk_level),
            }

    def generate_follow_up_response(self, user_question: str) -> str:
        """
        Generate a follow-up response based on user question about the analysis.

        Args:
            user_question: User's follow-up question

        Returns:
            AI-generated response
        """
        try:
            # Add user question to history
            self.conversation_history.append({"role": "user", "content": user_question})

            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
                system=self.SYSTEM_PROMPT,
                messages=self.conversation_history,
            )

            # Extract response
            answer = response.content[0].text

            # Add to history
            self.conversation_history.append({"role": "assistant", "content": answer})

            return answer

        except Exception as e:
            logger.error(f"Error generating follow-up response: {str(e)}")
            return "I apologize, but I encountered an error processing your question. Please try again."

    def reset_conversation(self):
        """Reset conversation history for a new user."""
        self.conversation_history = []
        logger.info("Conversation history reset")

    @staticmethod
    def _extract_alternatives(explanation: str) -> List[str]:
        """
        Extract suggested alternatives from explanation.

        Args:
            explanation: AI-generated explanation

        Returns:
            List of alternatives
        """
        # Look for numbered or bulleted alternatives
        alternatives = []
        lines = explanation.split("\n")

        in_alternatives_section = False
        for line in lines:
            if "alternative" in line.lower() or "instead" in line.lower():
                in_alternatives_section = True

            if in_alternatives_section and line.strip():
                # Look for numbered items (1., 2., etc.) or bullets
                if any(
                    line.strip().startswith(prefix)
                    for prefix in ["1.", "2.", "3.", "4.", "5.", "-", "•"]
                ):
                    alt = line.strip().lstrip("123456.-•").strip()
                    if alt and len(alt) > 10:  # Only include substantial suggestions
                        alternatives.append(alt)

        return alternatives[:3]  # Return up to 3 alternatives

    @staticmethod
    def _get_fallback_explanation(
        risk_level: str, cost: float, disposable: float
    ) -> str:
        """
        Provide fallback explanation if API fails.

        Args:
            risk_level: Risk level
            cost: Purchase cost
            disposable: Disposable income

        Returns:
            Fallback explanation
        """
        percentage = (cost / max(disposable, 1)) * 100

        if risk_level == "Low Risk":
            return f"""This {cost:.2f} purchase represents {percentage:.1f}% of your available disposable income.

Based on the rule-based assessment, this is a Low Risk purchase - it's small relative to your available funds.
However, this doesn't mean you should buy it automatically. Consider:
- Do you need this item?
- Is there a more affordable alternative?
- Could you wait and save for it?

Make the decision that's right for your financial situation."""

        elif risk_level == "Medium Risk":
            return f"""This ${cost:.2f} purchase represents {percentage:.1f}% of your available disposable income.

Based on the rule-based assessment, this is a Medium Risk purchase - it's a noticeable portion of your available funds.
Before making this purchase, consider:
- Is this a need or a want?
- Have you budgeted for this category?
- Could you find the item at a lower cost?
- Would it impact other financial goals?

Make a careful, informed decision."""

        else:  # High Risk
            return f"""This ${cost:.2f} purchase represents {percentage:.1f}% of your available disposable income.

Based on the rule-based assessment, this is a High Risk purchase - it's a very significant portion of your available funds.
This suggests the purchase could materially impact your financial flexibility.
Consider:
- Is this a critical need right now?
- Could you delay this purchase?
- Can you find a more affordable alternative?
- What would it mean for your savings and other goals?

Think carefully before committing to this purchase."""

    @staticmethod
    def _get_fallback_alternatives(risk_level: str) -> List[str]:
        """
        Provide fallback alternatives if API fails.

        Args:
            risk_level: Risk level

        Returns:
            List of alternatives
        """
        general_alternatives = [
            "Wait 30 days and see if you still want it",
            "Search for used or refurbished versions at lower cost",
            "Look for sales, coupons, or discount codes",
        ]

        if risk_level in ["Medium Risk", "High Risk"]:
            additional = [
                "Consider a budget-friendly alternative brand",
                "Explore rental or subscription options instead of buying",
                "Set a savings goal and purchase later",
            ]
            return general_alternatives + additional

        return general_alternatives
