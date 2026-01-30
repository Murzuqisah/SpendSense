"""Decision Engine - Orchestrates all SpendSense components."""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from src.validation import InputValidator, ValidationError
from src.rule_engine import RuleEngine
from src.scoring import ConfidenceScorer
from src.ai_reasoning import AIReasoning

logger = logging.getLogger(__name__)


class DecisionEngine:
    """
    Main orchestrator that combines all SpendSense components.

    Flow:
    1. Validate input
    2. Calculate disposable income and check hard stops
    3. Generate confidence score
    4. Use AI to generate explanation and alternatives
    5. Return comprehensive decision report
    """

    def __init__(self, use_ai: bool = True):
        """
        Initialize the Decision Engine.

        Args:
            use_ai: Whether to use AI for explanations (False for fallback mode)
        """
        self.use_ai = use_ai
        self.ai_reasoner = AIReasoning() if use_ai else None
        logger.info(f"DecisionEngine initialized (AI: {use_ai})")

    def evaluate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a purchase decision end-to-end.

        Args:
            input_data: Dictionary with monthly_income, fixed_expenses,
                       savings_goal, and planned_purchase

        Returns:
            Comprehensive decision report
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": None,
            "input_validation": None,
            "financial_analysis": None,
            "risk_assessment": None,
            "ai_reasoning": None,
            "final_decision": None,
        }

        try:
            # Step 1: Validate Input
            logger.info("Step 1: Validating input...")
            income, expenses, savings, cost, item = InputValidator.validate_input(
                input_data
            )

            report["input_validation"] = {
                "status": "valid",
                "monthly_income": income,
                "fixed_expenses": expenses,
                "savings_goal": savings,
                "purchase_item": item,
                "purchase_cost": cost,
            }

            # Step 2: Rule-based Analysis
            logger.info("Step 2: Running rule engine...")
            rule_result = RuleEngine.evaluate_purchase(income, expenses, savings, cost)

            report["financial_analysis"] = {
                "disposable_income": rule_result["disposable_income"],
                "remaining_after_purchase": rule_result.get("remaining_after_purchase"),
                "hard_stop_triggered": rule_result["hard_stop_triggered"],
                "hard_stop_reason": rule_result.get("hard_stop_reason"),
                "can_afford": rule_result["can_afford"],
            }

            # Step 3: Confidence Scoring
            logger.info("Step 3: Calculating risk score...")
            confidence_score, risk_level = ConfidenceScorer.score_purchase(
                cost, rule_result["disposable_income"]
            )

            report["risk_assessment"] = {
                "risk_level": risk_level,
                "confidence_score": confidence_score,
                "percentage_of_disposable": (
                    cost / max(rule_result["disposable_income"], 1)
                )
                * 100,
            }

            # Step 4: AI-Powered Explanation
            logger.info("Step 4: Generating AI explanation...")

            if self.use_ai and self.ai_reasoner:
                try:
                    ai_result = self.ai_reasoner.generate_explanation(
                        item,
                        cost,
                        income,
                        rule_result["disposable_income"],
                        risk_level,
                        confidence_score,
                    )
                    report["ai_reasoning"] = {
                        "explanation": ai_result["explanation"],
                        "alternatives": ai_result["alternatives"],
                        "mode": "claude",
                    }
                except Exception as e:
                    logger.warning(f"AI explanation failed, using fallback: {str(e)}")
                    report["ai_reasoning"] = self._get_fallback_reasoning(
                        risk_level, cost, rule_result["disposable_income"]
                    )
            else:
                report["ai_reasoning"] = self._get_fallback_reasoning(
                    risk_level, cost, rule_result["disposable_income"]
                )

            # Step 5: Final Decision Summary
            logger.info("Step 5: Generating final decision...")
            report["final_decision"] = self._generate_final_decision(
                report, item, cost, rule_result["disposable_income"]
            )

            report["status"] = "success"

        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            report["error"] = str(e)
            report["status"] = "validation_error"

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            report["error"] = f"Unexpected error: {str(e)}"
            report["status"] = "error"

        return report

    def _get_fallback_reasoning(
        self, risk_level: str, cost: float, disposable: float
    ) -> Dict[str, Any]:
        """
        Generate fallback AI reasoning when API is unavailable.

        Args:
            risk_level: Risk level from scoring
            cost: Purchase cost
            disposable: Disposable income

        Returns:
            Dictionary with fallback explanation and alternatives
        """
        explanation = AIReasoning._get_fallback_explanation(
            risk_level, cost, disposable
        )
        alternatives = AIReasoning._get_fallback_alternatives(risk_level)

        return {
            "explanation": explanation,
            "alternatives": alternatives,
            "mode": "fallback",
        }

    def _generate_final_decision(
        self, report: Dict[str, Any], item: str, cost: float, disposable: float
    ) -> Dict[str, Any]:
        """
        Generate the final decision summary.

        Args:
            report: Full report being generated
            item: Purchase item
            cost: Cost of item
            disposable: Disposable income

        Returns:
            Final decision dictionary
        """
        risk = report["risk_assessment"]["risk_level"]
        hard_stop = report["financial_analysis"]["hard_stop_triggered"]
        remaining = report["financial_analysis"].get("remaining_after_purchase")

        # Determine recommendation (remember: NOT financial advice)
        if hard_stop:
            summary = "⚠️ CANNOT AFFORD - This purchase would exceed your income or eliminate all disposable funds."
        elif risk == "Low Risk":
            summary = "✅ LOW RISK - This purchase is a small portion of your available funds."
        elif risk == "Medium Risk":
            summary = "⚠️ MEDIUM RISK - This purchase is a significant portion of your available funds. Consider carefully."
        else:  # High Risk
            summary = "🚨 HIGH RISK - This purchase would consume most or all of your available funds. Proceed with caution."

        return {
            "summary": summary,
            "recommendation": "This analysis is for informational purposes only. Make your own informed decision.",
            "key_metrics": {
                "monthly_income": report["input_validation"]["monthly_income"],
                "disposable_income": disposable,
                "purchase_cost": cost,
                "remaining_after_purchase": remaining,
                "percentage_of_disposable": report["risk_assessment"][
                    "percentage_of_disposable"
                ],
            },
            "next_steps": (
                [
                    "Review the analysis and alternatives",
                    "Consider your personal financial goals",
                    "Make an informed decision that's right for you",
                    "Update your budget if you decide to purchase",
                ]
                if not hard_stop
                else [
                    "Focus on increasing income or reducing expenses first",
                    "Consider waiting until you have more financial flexibility",
                    "Explore the suggested alternatives",
                ]
            ),
        }

    def get_json_report(self, input_data: Dict[str, Any]) -> str:
        """
        Evaluate and return report as JSON string.

        Args:
            input_data: Purchase evaluation input

        Returns:
            JSON string of complete report
        """
        report = self.evaluate(input_data)
        return json.dumps(report, indent=2)

    def reset_ai_conversation(self):
        """Reset AI conversation history for new user."""
        if self.ai_reasoner:
            self.ai_reasoner.reset_conversation()
            logger.info("AI conversation reset")
