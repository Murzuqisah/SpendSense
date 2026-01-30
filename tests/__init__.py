"""Test suite for SpendSense."""

import pytest
from datetime import datetime
from src.agents import agent
from src.models import Transaction, TransactionType, TransactionCategory


@pytest.fixture
def test_user_id():
    """Test user ID fixture."""
    return "test_user_123"


@pytest.fixture
def sample_transaction(test_user_id):
    """Sample transaction fixture."""
    return Transaction(
        user_id=test_user_id,
        description="Grocery store purchase",
        amount=75.50,
        transaction_type=TransactionType.EXPENSE,
        category=TransactionCategory.FOOD,
        date=datetime.now(),
    )


class TestAgent:
    """Test cases for SpendSense Agent."""

    def test_agent_initialization(self):
        """Test agent initialization."""
        assert agent is not None
        assert agent.api_key is not None or agent.api_key == ""

    def test_add_transaction(self, test_user_id, sample_transaction):
        """Test adding a transaction."""
        result = agent.add_transaction(test_user_id, sample_transaction)
        assert result is True

    def test_set_budget(self, test_user_id):
        """Test setting a budget."""
        result = agent.set_budget(test_user_id, TransactionCategory.FOOD, 500.0)
        assert result is True

    def test_spending_analysis(self, test_user_id, sample_transaction):
        """Test spending analysis."""
        agent.add_transaction(test_user_id, sample_transaction)
        analysis = agent.analyze_spending(test_user_id, "monthly")

        assert "total_spent" in analysis
        assert "spending_by_category" in analysis
        assert analysis["total_spent"] > 0

    def test_recommendations_generation(self, test_user_id, sample_transaction):
        """Test recommendations generation."""
        agent.add_transaction(test_user_id, sample_transaction)
        recommendations = agent.get_recommendations(test_user_id)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
