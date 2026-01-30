"""Configuration management for SpendSense application."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""

    # API Configuration
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    PORT = int(os.getenv("PORT", 8000))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # AI Provider
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./spendsense.db")

    # Application Settings
    MAX_TRANSACTIONS_PER_MONTH = 5000
    BUDGET_CATEGORIES = [
        "Housing",
        "Food & Dining",
        "Transportation",
        "Utilities",
        "Entertainment",
        "Shopping",
        "Healthcare",
        "Education",
        "Savings",
        "Investments",
        "Other",
    ]


config = Config()
