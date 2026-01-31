"""Utility functions for SpendSense application."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict
from src.models import Transaction, TransactionCategory


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def categorize_transaction(description: str, amount: float) -> TransactionCategory:
    """
    Categorize a transaction based on description and amount.

    Args:
        description: Transaction description
        amount: Transaction amount

    Returns:
        TransactionCategory: Categorized transaction
    """
    description_lower = description.lower()

    category_keywords = {
        TransactionCategory.HOUSING: [
            "rent",
            "mortgage",
            "apartment",
            "house",
            "property",
        ],
        TransactionCategory.FOOD: [
            "restaurant",
            "cafe",
            "grocery",
            "food",
            "pizza",
            "burger",
            "dinner",
        ],
        TransactionCategory.TRANSPORTATION: [
            "gas",
            "uber",
            "taxi",
            "parking",
            "bus",
            "train",
            "car",
        ],
        TransactionCategory.UTILITIES: [
            "electric",
            "water",
            "internet",
            "phone",
            "gas bill",
        ],
        TransactionCategory.ENTERTAINMENT: [
            "movie",
            "netflix",
            "spotify",
            "game",
            "concert",
            "theater",
        ],
        TransactionCategory.SHOPPING: [
            "amazon",
            "mall",
            "store",
            "shopping",
            "clothes",
            "shoes",
        ],
        TransactionCategory.HEALTHCARE: [
            "doctor",
            "pharmacy",
            "hospital",
            "medical",
            "dental",
        ],
        TransactionCategory.EDUCATION: [
            "school",
            "course",
            "tuition",
            "book",
            "university",
        ],
        TransactionCategory.SAVINGS: ["savings", "deposit"],
        TransactionCategory.INVESTMENTS: ["stock", "crypto", "investment", "broker"],
    }

    for category, keywords in category_keywords.items():
        if any(keyword in description_lower for keyword in keywords):
            return category

    return TransactionCategory.OTHER


def calculate_spending_summary(transactions: List[Transaction]) -> Dict[str, float]:
    """
    Calculate spending summary by category.

    Args:
        transactions: List of transactions

    Returns:
        Dictionary with category spending totals
    """
    summary = {category.value: 0.0 for category in TransactionCategory}

    for transaction in transactions:
        if transaction.transaction_type == "expense":
            summary[transaction.category] += transaction.amount

    return summary


def get_date_range(period: str) -> tuple:
    """
    Get date range for specified period.

    Args:
        period: Period type (daily, weekly, monthly, yearly)

    Returns:
        Tuple of (start_date, end_date)
    """
    today = datetime.now().date()

    if period == "daily":
        return today, today
    elif period == "weekly":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return start, end
    elif period == "monthly":
        start = today.replace(day=1)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = start.replace(month=start.month + 1, day=1) - timedelta(days=1)
        return start, end
    elif period == "yearly":
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
        return start, end
    else:
        return today, today


logger.info("Utility functions initialized")
