"""Confidence and risk scoring for SpendSense Agent."""

from typing import Tuple


class ConfidenceScorer:
    """
    Calculates confidence and risk scores based on purchase affordability.

    Formula from implementation guide:
    confidence = min(1.0, purchase_cost / max(disposable, 1))

    Mapped to risk levels:
    - 0.0–0.4 → Low Risk
    - 0.4–0.7 → Medium Risk
    - 0.7–1.0 → High Risk
    """

    # Score boundaries for risk levels
    LOW_RISK_UPPER_BOUND = 0.4
    MEDIUM_RISK_UPPER_BOUND = 0.7
    HIGH_RISK_UPPER_BOUND = 1.0

    @staticmethod
    def calculate_confidence_score(
        purchase_cost: float, disposable_income: float
    ) -> float:
        """
        Calculate confidence score based on purchase cost vs disposable income.

        Confidence represents how much of the disposable income the purchase consumes.
        - Lower confidence = safer purchase
        - Higher confidence = riskier purchase

        Formula: confidence = min(1.0, purchase_cost / max(disposable_income, 1))

        Args:
            purchase_cost: Cost of the planned purchase
            disposable_income: Available disposable income

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        # Avoid division by zero - use max(disposable_income, 1)
        denominator = max(disposable_income, 1.0)

        # Calculate raw score
        raw_score = purchase_cost / denominator

        # Cap at 1.0
        confidence_score = min(1.0, raw_score)

        return round(confidence_score, 3)

    @staticmethod
    def get_risk_level_from_score(score: float) -> str:
        """
        Map confidence score to risk level.

        Mapping:
        - 0.0–0.4 → Low Risk
        - 0.4–0.7 → Medium Risk
        - 0.7–1.0 → High Risk

        Args:
            score: Confidence score (0.0 to 1.0)

        Returns:
            str: Risk level ("Low Risk", "Medium Risk", or "High Risk")
        """
        if score <= ConfidenceScorer.LOW_RISK_UPPER_BOUND:
            return "Low Risk"
        elif score <= ConfidenceScorer.MEDIUM_RISK_UPPER_BOUND:
            return "Medium Risk"
        else:
            return "High Risk"

    @staticmethod
    def score_purchase(
        purchase_cost: float, disposable_income: float
    ) -> Tuple[float, str]:
        """
        Score a purchase and get risk level.

        Args:
            purchase_cost: Cost of the planned purchase
            disposable_income: Available disposable income

        Returns:
            Tuple of (confidence_score, risk_level_str)
        """
        score = ConfidenceScorer.calculate_confidence_score(
            purchase_cost, disposable_income
        )
        risk_level = ConfidenceScorer.get_risk_level_from_score(score)
        return score, risk_level

    @staticmethod
    def score_with_breakdown(purchase_cost: float, disposable_income: float) -> dict:
        """
        Score a purchase with detailed breakdown.

        Args:
            purchase_cost: Cost of the planned purchase
            disposable_income: Available disposable income

        Returns:
            Dictionary with score details
        """
        score = ConfidenceScorer.calculate_confidence_score(
            purchase_cost, disposable_income
        )
        risk_level = ConfidenceScorer.get_risk_level_from_score(score)

        # Calculate percentage for reference
        percentage = (purchase_cost / max(disposable_income, 1)) * 100

        # Determine color coding for display (useful for UI)
        if score <= ConfidenceScorer.LOW_RISK_UPPER_BOUND:
            color = "green"
        elif score <= ConfidenceScorer.MEDIUM_RISK_UPPER_BOUND:
            color = "yellow"
        else:
            color = "red"

        return {
            "confidence_score": score,
            "risk_level": risk_level,
            "percentage_of_disposable": percentage,
            "color": color,
        }
