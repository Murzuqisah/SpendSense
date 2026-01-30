"""Tests for input validation layer."""

import pytest
from src.validation import InputValidator, ValidationError


class TestValidateAmount:
    """Tests for validate_amount method."""

    def test_valid_amount(self):
        """Test validation of valid amount."""
        result = InputValidator.validate_amount(100.50, "Test")
        assert result == 100.50

    def test_valid_integer(self):
        """Test validation of integer amount."""
        result = InputValidator.validate_amount(100, "Test")
        assert result == 100.0

    def test_valid_string_number(self):
        """Test validation of string-formatted number."""
        result = InputValidator.validate_amount("100.50", "Test")
        assert result == 100.50

    def test_none_value(self):
        """Test that None raises error."""
        with pytest.raises(ValidationError, match="is required"):
            InputValidator.validate_amount(None, "Test Amount")

    def test_negative_value(self):
        """Test that negative values raise error."""
        with pytest.raises(ValidationError, match="cannot be negative"):
            InputValidator.validate_amount(-50, "Test Amount")

    def test_negative_string(self):
        """Test that negative string values raise error."""
        with pytest.raises(ValidationError, match="cannot be negative"):
            InputValidator.validate_amount("-50", "Test Amount")

    def test_non_numeric_string(self):
        """Test that non-numeric strings raise error."""
        with pytest.raises(ValidationError, match="must be a number"):
            InputValidator.validate_amount("abc", "Test Amount")

    def test_invalid_type(self):
        """Test that invalid types raise error."""
        with pytest.raises(ValidationError, match="must be a number"):
            InputValidator.validate_amount([100], "Test Amount")

    def test_zero_not_allowed(self):
        """Test that zero raises error when not allowed."""
        with pytest.raises(ValidationError, match="must be greater than 0"):
            InputValidator.validate_amount(0, "Test Amount", allow_zero=False)

    def test_zero_allowed(self):
        """Test that zero is accepted when allowed."""
        result = InputValidator.validate_amount(0, "Test Amount", allow_zero=True)
        assert result == 0.0


class TestValidateMonthlyIncome:
    """Tests for validate_monthly_income method."""

    def test_valid_income(self):
        """Test validation of valid income."""
        result = InputValidator.validate_monthly_income(5000)
        assert result == 5000.0

    def test_income_string(self):
        """Test validation of string income."""
        result = InputValidator.validate_monthly_income("5000.50")
        assert result == 5000.50

    def test_zero_income_rejected(self):
        """Test that zero income is rejected."""
        with pytest.raises(ValidationError):
            InputValidator.validate_monthly_income(0)

    def test_negative_income_rejected(self):
        """Test that negative income is rejected."""
        with pytest.raises(ValidationError):
            InputValidator.validate_monthly_income(-5000)

    def test_none_income_rejected(self):
        """Test that None income is rejected."""
        with pytest.raises(ValidationError, match="Monthly income is required"):
            InputValidator.validate_monthly_income(None)


class TestValidateFixedExpenses:
    """Tests for validate_fixed_expenses method."""

    def test_valid_expenses(self):
        """Test validation of valid expenses."""
        result = InputValidator.validate_fixed_expenses(1500)
        assert result == 1500.0

    def test_zero_expenses_allowed(self):
        """Test that zero expenses are allowed."""
        result = InputValidator.validate_fixed_expenses(0)
        assert result == 0.0

    def test_negative_expenses_rejected(self):
        """Test that negative expenses are rejected."""
        with pytest.raises(ValidationError):
            InputValidator.validate_fixed_expenses(-1500)

    def test_none_expenses_rejected(self):
        """Test that None expenses are rejected."""
        with pytest.raises(ValidationError):
            InputValidator.validate_fixed_expenses(None)


class TestValidateSavingsGoal:
    """Tests for validate_savings_goal method."""

    def test_valid_savings(self):
        """Test validation of valid savings goal."""
        result = InputValidator.validate_savings_goal(500)
        assert result == 500.0

    def test_zero_savings_allowed(self):
        """Test that zero savings goal is allowed."""
        result = InputValidator.validate_savings_goal(0)
        assert result == 0.0

    def test_negative_savings_rejected(self):
        """Test that negative savings are rejected."""
        with pytest.raises(ValidationError):
            InputValidator.validate_savings_goal(-500)


class TestValidatePurchaseCost:
    """Tests for validate_purchase_cost method."""

    def test_valid_cost(self):
        """Test validation of valid purchase cost."""
        result = InputValidator.validate_purchase_cost(299.99)
        assert result == 299.99

    def test_zero_cost_rejected(self):
        """Test that zero cost is rejected."""
        with pytest.raises(ValidationError):
            InputValidator.validate_purchase_cost(0)

    def test_negative_cost_rejected(self):
        """Test that negative cost is rejected."""
        with pytest.raises(ValidationError):
            InputValidator.validate_purchase_cost(-299.99)


class TestValidatePurchaseItem:
    """Tests for validate_purchase_item method."""

    def test_valid_item(self):
        """Test validation of valid item description."""
        result = InputValidator.validate_purchase_item("Laptop")
        assert result == "Laptop"

    def test_item_with_spaces(self):
        """Test that spaces are trimmed."""
        result = InputValidator.validate_purchase_item("  Gaming Laptop  ")
        assert result == "Gaming Laptop"

    def test_empty_string_rejected(self):
        """Test that empty strings are rejected."""
        with pytest.raises(ValidationError, match="is required"):
            InputValidator.validate_purchase_item("")

    def test_whitespace_only_rejected(self):
        """Test that whitespace-only strings are rejected."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            InputValidator.validate_purchase_item("   ")

    def test_none_rejected(self):
        """Test that None is rejected."""
        with pytest.raises(ValidationError, match="is required"):
            InputValidator.validate_purchase_item(None)

    def test_non_string_rejected(self):
        """Test that non-string types are rejected."""
        with pytest.raises(ValidationError, match="must be a string"):
            InputValidator.validate_purchase_item(123)

    def test_long_item_rejected(self):
        """Test that very long descriptions are rejected."""
        long_item = "a" * 201
        with pytest.raises(ValidationError, match="too long"):
            InputValidator.validate_purchase_item(long_item)

    def test_long_item_accepted_at_limit(self):
        """Test that item at 200 char limit is accepted."""
        item_at_limit = "a" * 200
        result = InputValidator.validate_purchase_item(item_at_limit)
        assert result == item_at_limit


class TestValidateInput:
    """Tests for complete input validation."""

    def test_valid_complete_input(self):
        """Test validation of complete valid input."""
        input_data = {
            "monthly_income": 5000,
            "fixed_expenses": 1500,
            "savings_goal": 500,
            "planned_purchase": {"item": "Laptop", "cost": 1000},
        }

        income, expenses, savings, cost, item = InputValidator.validate_input(
            input_data
        )

        assert income == 5000.0
        assert expenses == 1500.0
        assert savings == 500.0
        assert cost == 1000.0
        assert item == "Laptop"

    def test_missing_top_level_field(self):
        """Test that missing top-level fields are detected."""
        input_data = {
            "monthly_income": 5000,
            "fixed_expenses": 1500,
            "savings_goal": 500,
            # Missing planned_purchase
        }

        with pytest.raises(ValidationError, match="Missing required fields"):
            InputValidator.validate_input(input_data)

    def test_missing_purchase_item(self):
        """Test that missing purchase item is detected."""
        input_data = {
            "monthly_income": 5000,
            "fixed_expenses": 1500,
            "savings_goal": 500,
            "planned_purchase": {
                "cost": 1000
                # Missing item
            },
        }

        with pytest.raises(ValidationError, match="must contain 'item' and 'cost'"):
            InputValidator.validate_input(input_data)

    def test_invalid_purchase_dict_structure(self):
        """Test that invalid purchase structure is rejected."""
        input_data = {
            "monthly_income": 5000,
            "fixed_expenses": 1500,
            "savings_goal": 500,
            "planned_purchase": "Laptop",  # Should be a dict
        }

        with pytest.raises(ValidationError, match="must be a dictionary"):
            InputValidator.validate_input(input_data)

    def test_invalid_amounts_in_input(self):
        """Test that invalid amounts are caught."""
        input_data = {
            "monthly_income": "abc",
            "fixed_expenses": 1500,
            "savings_goal": 500,
            "planned_purchase": {"item": "Laptop", "cost": 1000},
        }

        with pytest.raises(ValidationError):
            InputValidator.validate_input(input_data)

    def test_string_amounts_converted(self):
        """Test that string amounts are properly converted."""
        input_data = {
            "monthly_income": "5000.50",
            "fixed_expenses": "1500.25",
            "savings_goal": "500",
            "planned_purchase": {"item": "Laptop", "cost": "1000.99"},
        }

        income, expenses, savings, cost, item = InputValidator.validate_input(
            input_data
        )

        assert income == 5000.50
        assert expenses == 1500.25
        assert savings == 500.0
        assert cost == 1000.99
        assert item == "Laptop"

    def test_zero_expenses_and_savings(self):
        """Test that zero expenses and savings are accepted."""
        input_data = {
            "monthly_income": 5000,
            "fixed_expenses": 0,
            "savings_goal": 0,
            "planned_purchase": {"item": "Laptop", "cost": 1000},
        }

        income, expenses, savings, cost, item = InputValidator.validate_input(
            input_data
        )

        assert expenses == 0.0
        assert savings == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
