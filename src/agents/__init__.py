"""Main AI Agent for SpendSense - Personal Budgeting Assistant."""

import logging
from typing import Optional, Dict, List, Any
import json
from datetime import datetime
from src.config import config
from src.models import (
    Transaction,
    Budget,
    FinancialGoal,
    FinancialInsight,
    TransactionType,
    TransactionCategory,
)
from src.utils import categorize_transaction, calculate_spending_summary, get_date_range

# Configure logging
logger = logging.getLogger(__name__)


class SpendSenseAgent:
    """
    Main AI Agent for personal budgeting and financial decision making.
    """

    def __init__(self):
        """Initialize the SpendSense AI Agent."""
        self.api_key = config.ANTHROPIC_API_KEY
        self.user_data = {}  # In-memory storage for demo
        logger.info("SpendSense Agent initialized")

    def analyze_spending(self, user_id: str, period: str = "monthly") -> Dict[str, Any]:
        """
        Analyze user spending patterns.

        Args:
            user_id: User ID
            period: Analysis period (daily, weekly, monthly, yearly)

        Returns:
            Dictionary with spending analysis
        """
        try:
            # Get transactions for period
            start_date, end_date = get_date_range(period)
            transactions = self._get_user_transactions(user_id, start_date, end_date)

            # Calculate spending summary
            spending_summary = calculate_spending_summary(transactions)
            total_spent = sum(spending_summary.values())

            # Get budgets
            budgets = self._get_user_budgets(user_id)

            analysis = {
                "period": period,
                "total_spent": total_spent,
                "spending_by_category": spending_summary,
                "budget_status": self._check_budget_status(spending_summary, budgets),
                "transaction_count": len(transactions),
                "average_transaction": (
                    total_spent / len(transactions) if transactions else 0
                ),
            }

            logger.info(f"Spending analysis completed for user {user_id}")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing spending: {str(e)}")
            return {"error": str(e)}

    def get_recommendations(self, user_id: str) -> List[str]:
        """
        Generate personalized financial recommendations.

        Args:
            user_id: User ID

        Returns:
            List of recommendations
        """
        try:
            # Get spending analysis
            analysis = self.analyze_spending(user_id)
            spending_by_category = analysis.get("spending_by_category", {})

            recommendations = []

            # Analyze spending patterns
            if spending_by_category.get("Food & Dining", 0) > 500:
                recommendations.append(
                    "Your food and dining expenses are high. Consider meal planning and cooking at home."
                )

            if spending_by_category.get("Entertainment", 0) > 300:
                recommendations.append(
                    "Entertainment spending is significant. Review subscription services you may not use."
                )

            if spending_by_category.get("Shopping", 0) > spending_by_category.get(
                "Savings", 0
            ):
                recommendations.append(
                    "Consider increasing your savings. Try setting a percentage of income to save automatically."
                )

            # Check budget adherence
            budget_status = analysis.get("budget_status", {})
            for category, status in budget_status.items():
                if status.get("exceeded", False):
                    recommendations.append(
                        f"You've exceeded your {category} budget. "
                        f"Review transactions and adjust spending."
                    )

            if not recommendations:
                recommendations.append(
                    "Great job! Your spending patterns look healthy. Keep maintaining your budget!"
                )

            logger.info(
                f"Generated {len(recommendations)} recommendations for user {user_id}"
            )
            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return [f"Error generating recommendations: {str(e)}"]

    def add_transaction(self, user_id: str, transaction: Transaction) -> bool:
        """
        Add a new transaction.

        Args:
            user_id: User ID
            transaction: Transaction object

        Returns:
            Success status
        """
        try:
            if user_id not in self.user_data:
                self.user_data[user_id] = {"transactions": [], "budgets": []}

            self.user_data[user_id]["transactions"].append(transaction)
            logger.info(f"Transaction added for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error adding transaction: {str(e)}")
            return False

    def set_budget(self, user_id: str, category: str, limit: float) -> bool:
        """
        Set or update a budget for a category.

        Args:
            user_id: User ID
            category: Budget category
            limit: Monthly budget limit

        Returns:
            Success status
        """
        try:
            if user_id not in self.user_data:
                self.user_data[user_id] = {"transactions": [], "budgets": []}

            budget = Budget(user_id=user_id, category=category, limit=limit)
            self.user_data[user_id]["budgets"].append(budget)
            logger.info(f"Budget set for user {user_id}: {category} = ${limit}")
            return True

        except Exception as e:
            logger.error(f"Error setting budget: {str(e)}")
            return False

    # Helper methods
    def _get_user_transactions(
        self, user_id: str, start_date, end_date
    ) -> List[Transaction]:
        """Get user transactions for date range."""
        if user_id not in self.user_data:
            return []

        transactions = self.user_data[user_id].get("transactions", [])
        return [t for t in transactions if start_date <= t.date.date() <= end_date]

    def _get_user_budgets(self, user_id: str) -> List[Budget]:
        """Get user budgets."""
        if user_id not in self.user_data:
            return []

        return self.user_data[user_id].get("budgets", [])

    def _check_budget_status(
        self, spending: Dict[str, float], budgets: List[Budget]
    ) -> Dict[str, Dict[str, Any]]:
        """Check budget adherence."""
        status = {}

        for budget in budgets:
            spent = spending.get(budget.category, 0)
            exceeded = spent > budget.limit
            percentage = (spent / budget.limit * 100) if budget.limit > 0 else 0

            status[budget.category] = {
                "limit": budget.limit,
                "spent": spent,
                "exceeded": exceeded,
                "percentage": percentage,
                "remaining": max(0, budget.limit - spent),
            }

        return status


# Create global agent instance
agent = SpendSenseAgent()
