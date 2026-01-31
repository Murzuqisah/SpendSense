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
    SYSTEM_PROMPT = """You are SpendSense, a budgeting decision-support agent.

Your purpose:
- Help users evaluate everyday spending decisions
- Use simple, deterministic budgeting rules
- Explain financial risk clearly and conservatively
- Suggest safer alternatives when risk is medium or high

IMPORTANT CONSTRAINTS:
- You are NOT a financial advisor
- You must NOT give investment, tax, loan, credit, or debt advice
- You must NOT tell the user what action to take
- You only explain risk, trade-offs, and possible options

BUDGET LOGIC (MUST FOLLOW EXACTLY):
1. disposable_income = monthly_income - fixed_expenses - savings_goal

2. Risk rules:
- If disposable_income <= 0 → decision = "High Risk"
- If purchase_cost > disposable_income → decision = "High Risk"
- Else if purchase_cost <= 0.3 * disposable_income → decision = "Low Risk"
- Else if purchase_cost <= 0.6 * disposable_income → decision = "Medium Risk"
- Else → decision = "High Risk"

CONFIDENCE SCORE:
- confidence_score = purchase_cost / max(disposable_income, 1)
- Clamp value to a maximum of 1.0
- Round to two decimal places

OUTPUT RULES (STRICT):
- Respond ONLY with valid JSON
- Do NOT include any text outside JSON
- Do NOT include markdown
- Do NOT include commentary

OUTPUT FORMAT:
{
  "decision": "Low Risk | Medium Risk | High Risk",
  "confidence_score": number,
  "explanation": string,
  "alternatives": string[]
}

EXPLANATION RULES:
- Plain language
- Non-judgmental
- Explain WHY the risk level was assigned
- Mention disposable income and trade-offs
- Always include a short disclaimer:
  "This is not financial advice."

ALTERNATIVES RULES:
- If decision is Low Risk → alternatives may be empty
- If Medium or High Risk → provide 2–3 safer options
- Alternatives may include:
  - Delaying the purchase
  - Choosing a lower-cost option
  - Adjusting savings timing
- Do NOT recommend investments or loans

FAILURE HANDLING:
- If any input is missing or invalid, do NOT guess
- Return:
{
  "decision": "High Risk",
  "confidence_score": 1.0,
  "explanation": "Insufficient or invalid data to assess this decision. This is not financial advice.",
  "alternatives": []
}"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Reasoning with OpenAI API.

        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.conversation_history = []
        logger.info("AIReasoning initialized with OpenAI API")

    def _build_analysis_prompt(
        self,
        purchase_item: str,
        purchase_cost: float,
        monthly_income: float,
        fixed_expenses: float,
        savings_goal: float,
        disposable_income: float,
        risk_level: str,
        confidence_score: float,
    ) -> str:
        """
        Build the analysis prompt for OpenAI.

        Args:
            purchase_item: Item being purchased
            purchase_cost: Cost of purchase
            monthly_income: Monthly income
            fixed_expenses: Fixed monthly expenses
            savings_goal: Monthly savings goal
            disposable_income: Available disposable income
            risk_level: Risk level assessment
            confidence_score: Confidence score

        Returns:
            Formatted prompt for OpenAI
        """
        prompt = f"""Analyze this purchase decision and respond ONLY with valid JSON:

INPUTS:
- monthly_income: {monthly_income}
- fixed_expenses: {fixed_expenses}
- savings_goal: {savings_goal}
- purchase_item: {purchase_item}
- purchase_cost: {purchase_cost}
- calculated_disposable_income: {disposable_income}
- risk_level: {risk_level}
- confidence_score: {confidence_score}

You MUST respond with ONLY valid JSON in this exact format, with no additional text:
{{
  "decision": "Low Risk | Medium Risk | High Risk",
  "confidence_score": number,
  "explanation": string,
  "alternatives": string[]
}}

Do NOT include markdown, commentary, or any text outside the JSON."""

        return prompt

    def generate_explanation(
        self,
        purchase_item: str,
        purchase_cost: float,
        monthly_income: float,
        fixed_expenses: float,
        savings_goal: float,
        disposable_income: float,
        risk_level: str,
        confidence_score: float,
    ) -> Dict[str, any]:
        """
        Generate AI-powered explanation for a purchase decision using OpenAI API.

        Args:
            purchase_item: Item being purchased
            purchase_cost: Cost of purchase
            monthly_income: Monthly income
            fixed_expenses: Fixed monthly expenses
            savings_goal: Monthly savings goal
            disposable_income: Available disposable income
            risk_level: Risk level assessment
            confidence_score: Confidence score

        Returns:
            Dictionary with decision, confidence_score, explanation and alternatives
        """
        try:
            # Build the prompt
            prompt = self._build_analysis_prompt(
                purchase_item,
                purchase_cost,
                monthly_income,
                fixed_expenses,
                savings_goal,
                disposable_income,
                risk_level,
                confidence_score,
            )

            # Prepare messages for OpenAI API
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]

            # Call OpenAI API with gpt-4o-mini model
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", max_tokens=500, temperature=0.5, messages=messages
            )

            # Extract response text
            response_text = response.choices[0].message.content.strip()

            # Parse JSON response
            result = json.loads(response_text)

            # Store conversation
            self.conversation_history = messages + [
                {"role": "assistant", "content": response_text}
            ]

            logger.info(f"AI explanation generated for {purchase_item}")

            return {
                "decision": result.get("decision", risk_level),
                "confidence_score": min(
                    1.0, round(result.get("confidence_score", confidence_score), 2)
                ),
                "explanation": result.get("explanation", ""),
                "alternatives": result.get("alternatives", []),
            }

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response from OpenAI: {str(e)}")
            return self._get_fallback_json_response(
                risk_level, purchase_cost, disposable_income
            )
        except Exception as e:
            logger.error(f"Error generating AI explanation: {str(e)}")
            return self._get_fallback_json_response(
                risk_level, purchase_cost, disposable_income
            )

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
                model="gpt-4o-mini", max_tokens=512, messages=self.conversation_history
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
    def _get_fallback_json_response(
        risk_level: str, cost: float, disposable: float
    ) -> Dict[str, any]:
        """Provide fallback JSON response if API fails."""
        percentage = (cost / max(disposable, 1)) * 100
        confidence_score = min(1.0, round(cost / max(disposable, 1), 2))

        if risk_level == "Low Risk":
            explanation = f"This {cost:.2f} purchase represents {percentage:.1f}% of your disposable income, which falls within a comfortable spending range. The purchase is unlikely to significantly impact your financial flexibility. This is not financial advice."
            alternatives = []
        elif risk_level == "Medium Risk":
            explanation = f"This {cost:.2f} purchase represents {percentage:.1f}% of your disposable income, which is a moderate portion of your available funds. This purchase will noticeably reduce your financial flexibility for the month. Consider whether delaying or finding alternatives would better support your financial goals. This is not financial advice."
            alternatives = [
                "Delay the purchase and save over 2-3 months",
                "Look for a certified refurbished or gently used option",
                "Consider if a lower-cost version meets your needs",
            ]
        else:  # High Risk
            explanation = f"This {cost:.2f} purchase represents {percentage:.1f}% of your disposable income, which is a very substantial portion of your available funds. This purchase would significantly limit your financial flexibility and could impact your ability to handle unexpected expenses. This is not financial advice."
            alternatives = [
                "Save for 3-6 months before purchasing",
                "Explore budget-friendly alternatives in a lower price range",
                "Consider if this is a need versus a want at this time",
            ]

        return {
            "decision": risk_level,
            "confidence_score": confidence_score,
            "explanation": explanation,
            "alternatives": alternatives,
        }
