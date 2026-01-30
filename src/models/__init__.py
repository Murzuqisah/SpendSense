"""Data models for SpendSense application."""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class TransactionType(str, Enum):
    """Transaction types."""

    EXPENSE = "expense"
    INCOME = "income"


class TransactionCategory(str, Enum):
    """Expense categories."""

    HOUSING = "Housing"
    FOOD = "Food & Dining"
    TRANSPORTATION = "Transportation"
    UTILITIES = "Utilities"
    ENTERTAINMENT = "Entertainment"
    SHOPPING = "Shopping"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    SAVINGS = "Savings"
    INVESTMENTS = "Investments"
    OTHER = "Other"


class Transaction(BaseModel):
    """Transaction data model."""

    model_config = ConfigDict(use_enum_values=True)

    id: Optional[int] = None
    user_id: str
    description: str
    amount: float = Field(gt=0, description="Transaction amount in KSH")
    transaction_type: TransactionType
    category: TransactionCategory
    date: datetime
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class Budget(BaseModel):
    """Budget data model."""

    model_config = ConfigDict(use_enum_values=True)

    id: Optional[int] = None
    user_id: str
    category: TransactionCategory
    limit: float = Field(gt=0)
    current_spending: float = Field(default=0, ge=0)
    period: str = "monthly"  # monthly, weekly, yearly
    created_at: datetime = Field(default_factory=datetime.now)


class FinancialGoal(BaseModel):
    """Financial goal data model."""

    id: Optional[int] = None
    user_id: str
    name: str
    target_amount: float = Field(gt=0)
    current_amount: float = Field(default=0, ge=0)
    deadline: datetime
    category: str
    priority: int = Field(default=1, ge=1, le=5)
    created_at: datetime = Field(default_factory=datetime.now)


class FinancialInsight(BaseModel):
    """AI-generated financial insight."""

    id: Optional[int] = None
    user_id: str
    insight_type: str  # trend, anomaly, recommendation, alert
    title: str
    description: str
    confidence_score: float = Field(ge=0, le=1)
    actionable: bool = True
    created_at: datetime = Field(default_factory=datetime.now)


class UserProfile(BaseModel):
    """User profile data model."""

    user_id: str
    name: str
    email: str
    currency: str = "KSH"
    timezone: str = "UTC"
    monthly_income: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)
