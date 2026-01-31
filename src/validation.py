"""Input validation layer for SpendSense Agent."""

from typing import Dict, Any, Tuple


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


class InputValidator:
    """Validates and sanitizes user input for the spending decision engine."""

    @staticmethod
    def validate_amount(value: Any, field_name: str, allow_zero: bool = False) -> float:
        """
        Validate that a value is a valid monetary amount.

        Args:
            value: The value to validate
            field_name: Name of the field (for error messages)
            allow_zero: Whether zero is an acceptable value

        Returns:
            float: The validated amount

        Raises:
            ValidationError: If value is invalid
        """
        # Check for None or missing
        if value is None:
            raise ValidationError(f"{field_name} is required")

        # Try to convert to float
        try:
            amount = float(value)
        except (TypeError, ValueError):
            raise ValidationError(
                f"{field_name} must be a number, got {type(value).__name__}"
            )

        # Check for negative values
        if amount < 0:
            raise ValidationError(f"{field_name} cannot be negative (got {amount})")

        # Check for zero if not allowed
        if amount == 0 and not allow_zero:
            raise ValidationError(f"{field_name} must be greater than 0 (got {amount})")

        return amount

    @staticmethod
    def validate_monthly_income(income: Any) -> float:
        """
        Validate monthly income.

        Args:
            income: Monthly income value

        Returns:
            float: Validated income

        Raises:
            ValidationError: If income is invalid
        """
        return InputValidator.validate_amount(
            income, "Monthly income", allow_zero=False
        )

    @staticmethod
    def validate_fixed_expenses(expenses: Any) -> float:
        """
        Validate fixed monthly expenses.

        Args:
            expenses: Fixed expenses value

        Returns:
            float: Validated expenses

        Raises:
            ValidationError: If expenses are invalid
        """
        return InputValidator.validate_amount(
            expenses, "Fixed expenses", allow_zero=True
        )

    @staticmethod
    def validate_savings_goal(savings: Any) -> float:
        """
        Validate savings goal.

        Args:
            savings: Savings goal value

        Returns:
            float: Validated savings goal

        Raises:
            ValidationError: If savings goal is invalid
        """
        return InputValidator.validate_amount(savings, "Savings goal", allow_zero=True)

    @staticmethod
    def validate_purchase_cost(cost: Any) -> float:
        """
        Validate planned purchase cost.

        Args:
            cost: Purchase cost value

        Returns:
            float: Validated cost

        Raises:
            ValidationError: If cost is invalid
        """
        return InputValidator.validate_amount(cost, "Purchase cost", allow_zero=False)

    @staticmethod
    def validate_purchase_item(item: Any) -> str:
        """
        Validate purchase item description.

        Args:
            item: Item description

        Returns:
            str: Validated item description

        Raises:
            ValidationError: If item is invalid
        """
        if item is None or item == "":
            raise ValidationError("Purchase item description is required")

        if not isinstance(item, str):
            raise ValidationError(
                f"Purchase item must be a string, got {type(item).__name__}"
            )

        item_clean = item.strip()
        if not item_clean:
            raise ValidationError(
                "Purchase item description cannot be empty or whitespace"
            )

        if len(item_clean) > 200:
            raise ValidationError(
                "Purchase item description is too long (max 200 characters)"
            )

        return item_clean

    @staticmethod
    def validate_input(
        input_data: Dict[str, Any],
    ) -> Tuple[float, float, float, float, str]:
        """
        Validate complete input data.

        Args:
            input_data: Dictionary with keys: monthly_income, fixed_expenses,
                       savings_goal, planned_purchase (dict with 'item' and 'cost')

        Returns:
            Tuple of (income, fixed_expenses, savings_goal, purchase_cost, purchase_item)

        Raises:
            ValidationError: If any input is invalid
        """
        # Validate top-level keys
        required_keys = {
            "monthly_income",
            "fixed_expenses",
            "savings_goal",
            "planned_purchase",
        }
        missing_keys = required_keys - set(input_data.keys())

        if missing_keys:
            raise ValidationError(
                f"Missing required fields: {', '.join(sorted(missing_keys))}"
            )

        # Validate monetary amounts
        income = InputValidator.validate_monthly_income(input_data["monthly_income"])
        fixed_expenses = InputValidator.validate_fixed_expenses(
            input_data["fixed_expenses"]
        )
        savings_goal = InputValidator.validate_savings_goal(input_data["savings_goal"])

        # Validate planned purchase
        purchase = input_data.get("planned_purchase")
        if not isinstance(purchase, dict):
            raise ValidationError("planned_purchase must be a dictionary")

        if "item" not in purchase or "cost" not in purchase:
            raise ValidationError(
                "planned_purchase must contain 'item' and 'cost' fields"
            )

        purchase_item = InputValidator.validate_purchase_item(purchase["item"])
        purchase_cost = InputValidator.validate_purchase_cost(purchase["cost"])

        return income, fixed_expenses, savings_goal, purchase_cost, purchase_item
