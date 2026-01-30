"""AI Reasoning module for SpendSense Agent - OpenAI integration."""

import json
import logging
import os
from typing import Optional, List, Dict
from openai import OpenAI

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
- Focus on risk analysis, not recommendations

Your role is to:
1. Explain why a purchase is Low/Medium/High risk in 2-3 clear sentences
2. Provide 2-3 specific, actionable alternatives
3. Keep responses concise and structured

Format your response as:

RISK ANALYSIS:
[2-3 sentences explaining the risk level and why]

KEY CONSIDERATIONS:
- [Point 1]
- [Point 2]
- [Point 3]

ALTERNATIVES:
1. [Specific alternative option]
2. [Specific alternative option]
3. [Specific alternative option]

Be clear, concise, and avoid jargon."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Reasoning with OpenAI API.

        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
        """
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        self.conversation_history = []
        logger.info("AIReasoning initialized with OpenAI API")

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
        prompt = f"""Analyze this purchase decision:

FINANCIAL SITUATION:
- Monthly Income: KSH {monthly_income:.2f}
- Disposable Income: KSH {disposable_income:.2f}
- Purchase Item: {purchase_item}
- Purchase Cost: KSH {purchase_cost:.2f}
- Risk Level: {risk_level}
- Percentage of Disposable: {(purchase_cost/max(disposable_income, 1))*100:.1f}%

Provide a structured analysis following the format specified in your instructions."""

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
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=800,
                temperature=0.7,
                messages=messages
            )

            # Extract response
            explanation = response.choices[0].message.content

            # Store conversation
            self.conversation_history = messages + [{"role": "assistant", "content": explanation}]

            # Format the explanation with better structure
            formatted_explanation = self._format_explanation(explanation)

            logger.info(f"AI explanation generated for {purchase_item}")

            return {
                "explanation": formatted_explanation,
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

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=512,
                messages=self.conversation_history
            )

            # Extract response
            answer = response.choices[0].message.content

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
    def _format_explanation(explanation: str) -> str:
        """Format the AI explanation with better structure."""
        # Add disclaimer at the end
        formatted = f"""{explanation}

---
DISCLAIMER: This analysis is for informational purposes only and is not financial advice. Make your own informed decision based on your complete financial situation."""
        return formatted

    @staticmethod
    def _extract_alternatives(explanation: str) -> List[str]:
        """Extract suggested alternatives from explanation."""
        alternatives = []
        lines = explanation.split("\n")

        in_alternatives = False
        for line in lines:
            line = line.strip()
            
            # Check if we're in the alternatives section
            if "ALTERNATIVES:" in line.upper() or "ALTERNATIVE" in line.upper():
                in_alternatives = True
                continue
            
            # Stop if we hit another section
            if in_alternatives and line.endswith(":") and line.isupper():
                break
                
            # Extract numbered or bulleted items
            if in_alternatives and line:
                for prefix in ["1.", "2.", "3.", "4.", "5.", "-", "•", "*"]:
                    if line.startswith(prefix):
                        alt = line.lstrip("123456.-•*").strip()
                        if alt and len(alt) > 10:
                            alternatives.append(alt)
                        break

        return alternatives[:5]

    @staticmethod
    def _get_fallback_explanation(
        risk_level: str, cost: float, disposable: float
    ) -> str:
        """Provide fallback explanation if API fails."""
        percentage = (cost / max(disposable, 1)) * 100

        if risk_level == "Low Risk":
            return f"""RISK ANALYSIS:
This KSH {cost:.2f} purchase represents {percentage:.1f}% of your disposable income, which falls within a comfortable spending range. The purchase is unlikely to significantly impact your financial flexibility.

KEY CONSIDERATIONS:
- Purchase amount is manageable within your budget
- Leaves adequate funds for other expenses
- Low impact on savings goals

ALTERNATIVES:
1. Wait for seasonal sales to get a better price
2. Compare prices across different retailers
3. Consider if a lower-cost version meets your needs

---
DISCLAIMER: This analysis is for informational purposes only and is not financial advice. Make your own informed decision based on your complete financial situation."""

        elif risk_level == "Medium Risk":
            return f"""RISK ANALYSIS:
This KSH {cost:.2f} purchase represents {percentage:.1f}% of your disposable income, which is a moderate portion of your available funds. This purchase will noticeably reduce your financial flexibility for the month.

KEY CONSIDERATIONS:
- Significant portion of discretionary spending
- May limit other purchases this month
- Could impact emergency fund contributions

ALTERNATIVES:
1. Delay purchase and save over 2-3 months
2. Look for certified refurbished or gently used options
3. Consider a payment plan if available with no interest

---
DISCLAIMER: This analysis is for informational purposes only and is not financial advice. Make your own informed decision based on your complete financial situation."""

        else:  # High Risk
            return f"""RISK ANALYSIS:
This KSH {cost:.2f} purchase represents {percentage:.1f}% of your disposable income, which is a very substantial portion of your available funds. This purchase would significantly limit your financial flexibility and could impact your ability to handle unexpected expenses.

KEY CONSIDERATIONS:
- Consumes majority of discretionary spending
- Severely limits financial flexibility
- High risk to emergency preparedness

ALTERNATIVES:
1. Save for 3-6 months before purchasing
2. Explore budget-friendly alternatives in lower price range
3. Consider if this is a need vs. want at this time

---
DISCLAIMER: This analysis is for informational purposes only and is not financial advice. Make your own informed decision based on your complete financial situation."""

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
