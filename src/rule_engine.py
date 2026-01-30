"""Rule engine for SpendSense Agent - deterministic budgeting rules."""

from enum import Enum
from typing import Dict, Tuple


class RiskLevel(str, Enum):
    """Risk levels for purchase decisions."""

    LOW = "Low Risk"
    MEDIUM = "Medium Risk"
    HIGH = "High Risk"


class RuleEngine:
    """
    Deterministic rule-based engine for budget and risk assessment.

    Implements the rules defined in the SpendSense implementation guide:
    - Disposable income calculation
    - Risk threshold levels (30%, 60%)
    - Hard stops (negative disposable, cost > income)
    """

    # Risk threshold percentages
    LOW_RISK_THRESHOLD = 0.30  # Purchase <= 30% of disposable
    MEDIUM_RISK_THRESHOLD = 0.60  # Purchase <= 60% of disposable
    # Anything above 60% is HIGH_RISK

    @staticmethod
    def calculate_disposable_income(
        monthly_income: float, fixed_expenses: float, savings_goal: float
    ) -> float:
        """
        Calculate disposable income available for discretionary spending.

        Formula: disposable = income - fixed_expenses - savings_goal

        Args:
            monthly_income: Total monthly income
            fixed_expenses: Monthly fixed expenses
            savings_goal: Monthly savings goal

        Returns:
            float: Disposable income (can be negative)
        """
        return monthly_income - fixed_expenses - savings_goal

    @staticmethod
    def check_hard_stops(
        monthly_income: float, disposable_income: float, purchase_cost: float
    ) -> Tuple[bool, str]:
        """
        Check for hard stop conditions that automatically trigger High Risk.

        Hard stops:
        1. If disposable income <= 0 → auto High Risk
        2. If purchase cost > monthly income → auto High Risk (cannot be afforded)

        Args:
            monthly_income: Total monthly income
            disposable_income: Available disposable income
            purchase_cost: Cost of planned purchase

        Returns:
            Tuple of (is_hard_stop_triggered, reason_if_triggered)
        """
        if disposable_income <= 0:
            return (
                True,
                f"No disposable income available (income: ${monthly_income:.2f}, "
                f"expenses + savings: ${monthly_income - disposable_income:.2f})",
            )

        if purchase_cost >= monthly_income:
            return (
                True,
                f"Purchase cost (${purchase_cost:.2f}) exceeds monthly income "
                f"(${monthly_income:.2f}). Cannot afford this purchase.",
            )

        return (False, "")

    @staticmethod
    def assess_risk_level(purchase_cost: float, disposable_income: float) -> RiskLevel:
        """
        Assess risk level based on purchase cost vs disposable income.

        Risk thresholds:
        - purchase <= 30% of disposable → Low Risk
        - 30% < purchase <= 60% of disposable → Medium Risk
        - purchase > 60% of disposable → High Risk

        Args:
            purchase_cost: Cost of planned purchase
            disposable_income: Available disposable income

        Returns:
            RiskLevel: Assessed risk level
        """
        if disposable_income <= 0:
            return RiskLevel.HIGH

        percentage = purchase_cost / disposable_income

        if percentage <= RuleEngine.LOW_RISK_THRESHOLD:
            return RiskLevel.LOW
        elif percentage <= RuleEngine.MEDIUM_RISK_THRESHOLD:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH

    @staticmethod
    def evaluate_purchase(
        monthly_income: float,
        fixed_expenses: float,
        savings_goal: float,
        purchase_cost: float,
    ) -> Dict[str, any]:
        """
        Comprehensive purchase evaluation using rules.

        Returns detailed assessment including:
        - Disposable income
        - Hard stop status
        - Risk level
        - Percentage of disposable income
        - Recommendation message

        Args:
            monthly_income: Total monthly income
            fixed_expenses: Monthly fixed expenses
            savings_goal: Monthly savings goal
            purchase_cost: Cost of planned purchase

        Returns:
            Dictionary with evaluation results
        """
        # Calculate disposable income
        disposable = RuleEngine.calculate_disposable_income(
            monthly_income, fixed_expenses, savings_goal
        )

        # Check hard stops
        hard_stop_triggered, hard_stop_reason = RuleEngine.check_hard_stops(
            monthly_income, disposable, purchase_cost
        )

        if hard_stop_triggered:
            return {
                "disposable_income": disposable,
                "hard_stop_triggered": True,
                "hard_stop_reason": hard_stop_reason,
                "risk_level": RiskLevel.HIGH,
                "percentage_of_disposable": (
                    float("inf") if disposable <= 0 else (purchase_cost / disposable)
                ),
                "can_afford": False,
            }

        # Assess risk level
        risk_level = RuleEngine.assess_risk_level(purchase_cost, disposable)
        percentage = (purchase_cost / disposable) * 100 if disposable > 0 else 0

        return {
            "disposable_income": disposable,
            "hard_stop_triggered": False,
            "risk_level": risk_level,
            "percentage_of_disposable": (
                (purchase_cost / disposable) if disposable > 0 else 0
            ),
            "percentage_of_disposable_pct": percentage,
            "remaining_after_purchase": disposable - purchase_cost,
            "can_afford": True,
        }
