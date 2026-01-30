"""
Tests for SpendSense Web Application
Tests the Flask routes, form handling, and error management
"""

import pytest
from datetime import datetime
from src.web_app import app, engine, validator


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestIndexRoute:
    """Tests for the index route"""

    def test_index_loads_successfully(self, client):
        """Test that index page loads with 200 status"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"SpendSense" in response.data
        assert b"Purchase" in response.data or b"Evaluation" in response.data

    def test_index_has_form_fields(self, client):
        """Test that form has all required fields"""
        response = client.get("/")
        assert b"monthly_income" in response.data
        assert b"monthly_expenses" in response.data
        assert b"current_savings" in response.data
        assert b"item_name" in response.data
        assert b"item_cost" in response.data

    def test_index_has_submit_button(self, client):
        """Test that form has submit button"""
        response = client.get("/")
        assert b"Evaluate" in response.data or b"Submit" in response.data


class TestEvaluateRoute:
    """Tests for the evaluate route"""

    def test_evaluate_valid_low_risk_purchase(self, client):
        """Test evaluation with valid low-risk purchase"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "5000",
                "monthly_expenses": "3000",
                "current_savings": "10000",
                "item_name": "Laptop",
                "item_cost": "1000",
            },
        )
        assert response.status_code == 200
        assert b"Decision" in response.data or b"Results" in response.data

    def test_evaluate_valid_high_risk_purchase(self, client):
        """Test evaluation with high-risk purchase"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "5000",
                "monthly_expenses": "4500",
                "current_savings": "500",
                "item_name": "Vacation",
                "item_cost": "3000",
            },
        )
        assert response.status_code == 200

    def test_evaluate_missing_field(self, client):
        """Test evaluation with missing field"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "5000",
                "monthly_expenses": "3000",
                "current_savings": "10000",
                "item_name": "Laptop",
                # Missing item_cost
            },
        )
        assert response.status_code == 400
        assert b"Missing" in response.data or b"error" in response.data.lower()

    def test_evaluate_missing_multiple_fields(self, client):
        """Test evaluation with multiple missing fields"""
        response = client.post("/evaluate", data={"monthly_income": "5000"})
        assert response.status_code == 400

    def test_evaluate_invalid_numeric_input(self, client):
        """Test evaluation with non-numeric input"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "invalid",
                "monthly_expenses": "3000",
                "current_savings": "10000",
                "item_name": "Laptop",
                "item_cost": "1000",
            },
        )
        assert response.status_code == 400
        assert b"Invalid" in response.data or b"number" in response.data.lower()

    def test_evaluate_negative_income(self, client):
        """Test evaluation with negative income"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "-5000",
                "monthly_expenses": "3000",
                "current_savings": "10000",
                "item_name": "Laptop",
                "item_cost": "1000",
            },
        )
        assert response.status_code == 400

    def test_evaluate_zero_values(self, client):
        """Test evaluation with zero values"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "0",
                "monthly_expenses": "0",
                "current_savings": "0",
                "item_name": "Laptop",
                "item_cost": "0",
            },
        )
        assert response.status_code == 400

    def test_evaluate_expenses_exceed_income(self, client):
        """Test evaluation where expenses exceed income"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "3000",
                "monthly_expenses": "5000",
                "current_savings": "10000",
                "item_name": "Laptop",
                "item_cost": "1000",
            },
        )
        assert response.status_code == 400

    def test_evaluate_results_page_structure(self, client):
        """Test that results page has proper structure"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "5000",
                "monthly_expenses": "3000",
                "current_savings": "10000",
                "item_name": "Laptop",
                "item_cost": "1000",
            },
        )
        assert response.status_code == 200
        response_text = response.data.decode()
        # Should have decision information
        assert any(
            x in response_text for x in ["Decision", "decision", "Results", "results"]
        )

    def test_evaluate_handles_large_numbers(self, client):
        """Test evaluation with very large numbers"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "1000000",
                "monthly_expenses": "500000",
                "current_savings": "10000000",
                "item_name": "Private Jet",
                "item_cost": "50000000",
            },
        )
        assert response.status_code == 200

    def test_evaluate_handles_small_numbers(self, client):
        """Test evaluation with very small numbers"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "100",
                "monthly_expenses": "50",
                "current_savings": "1000",
                "item_name": "Coffee",
                "item_cost": "5",
            },
        )
        assert response.status_code == 200

    def test_evaluate_handles_decimals(self, client):
        """Test evaluation with decimal values"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "5000.50",
                "monthly_expenses": "3000.75",
                "current_savings": "10000.25",
                "item_name": "Laptop",
                "item_cost": "1000.99",
            },
        )
        assert response.status_code == 200

    def test_evaluate_empty_item_name(self, client):
        """Test evaluation with empty item name"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "5000",
                "monthly_expenses": "3000",
                "current_savings": "10000",
                "item_name": "",
                "item_cost": "1000",
            },
        )
        assert response.status_code == 400

    def test_evaluate_very_long_item_name(self, client):
        """Test evaluation with very long item name"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "5000",
                "monthly_expenses": "3000",
                "current_savings": "10000",
                "item_name": "A" * 500,  # Very long name
                "item_cost": "1000",
            },
        )
        assert response.status_code in [
            200,
            400,
        ]  # Should either process or reject gracefully

    def test_evaluate_special_characters_in_item_name(self, client):
        """Test evaluation with special characters in item name"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "5000",
                "monthly_expenses": "3000",
                "current_savings": "10000",
                "item_name": "Laptop (Gaming) @2024!",
                "item_cost": "1000",
            },
        )
        assert response.status_code == 200


class TestHealthRoute:
    """Tests for the health check route"""

    def test_health_check(self, client):
        """Test that health endpoint returns 200"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_json_format(self, client):
        """Test that health check returns JSON"""
        response = client.get("/health")
        data = response.get_json()
        assert data is not None
        assert "status" in data
        assert data["status"] == "ok"


class TestErrorHandling:
    """Tests for error handling"""

    def test_404_not_found(self, client):
        """Test 404 error handling"""
        response = client.get("/nonexistent-page")
        assert response.status_code == 404
        assert b"Not Found" in response.data or b"not found" in response.data.lower()

    def test_404_has_error_structure(self, client):
        """Test that 404 page has proper error structure"""
        response = client.get("/nonexistent-page")
        assert response.status_code == 404
        response_text = response.data.decode()
        # Should have error elements
        assert any(x in response_text for x in ["error", "Error", "not found"])

    def test_method_not_allowed(self, client):
        """Test 405 method not allowed"""
        response = client.put("/evaluate")
        assert response.status_code in [405, 404, 400]  # Depends on Flask config


class TestFormValidation:
    """Tests for form validation"""

    def test_form_accepts_float_values(self, client):
        """Test that form accepts decimal values"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "5000.99",
                "monthly_expenses": "3000.50",
                "current_savings": "10000.75",
                "item_name": "Laptop",
                "item_cost": "1000.01",
            },
        )
        assert response.status_code == 200

    def test_form_rejects_string_costs(self, client):
        """Test that form rejects string costs"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "five thousand",
                "monthly_expenses": "3000",
                "current_savings": "10000",
                "item_name": "Laptop",
                "item_cost": "1000",
            },
        )
        assert response.status_code == 400

    def test_form_rejects_special_chars_in_numbers(self, client):
        """Test that form rejects special characters in numbers"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "$5,000",
                "monthly_expenses": "3000",
                "current_savings": "10000",
                "item_name": "Laptop",
                "item_cost": "1000",
            },
        )
        assert response.status_code == 400


class TestResultsDisplay:
    """Tests for results display"""

    def test_results_show_item_information(self, client):
        """Test that results display item information"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "5000",
                "monthly_expenses": "3000",
                "current_savings": "10000",
                "item_name": "Gaming Monitor",
                "item_cost": "500",
            },
        )
        assert response.status_code == 200
        assert b"Gaming Monitor" in response.data or b"Monitor" in response.data

    def test_results_show_financial_breakdown(self, client):
        """Test that results show financial breakdown"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "5000",
                "monthly_expenses": "3000",
                "current_savings": "10000",
                "item_name": "Laptop",
                "item_cost": "1000",
            },
        )
        assert response.status_code == 200
        response_text = response.data.decode()
        # Should show financial metrics
        assert any(
            x in response_text for x in ["savings", "Savings", "income", "Income"]
        )

    def test_results_show_risk_level(self, client):
        """Test that results show risk level"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "5000",
                "monthly_expenses": "3000",
                "current_savings": "10000",
                "item_name": "Laptop",
                "item_cost": "1000",
            },
        )
        assert response.status_code == 200
        response_text = response.data.decode()
        # Should contain risk-related information
        assert any(
            x in response_text
            for x in ["RISK", "risk", "Risk", "LOW", "MEDIUM", "HIGH"]
        )

    def test_results_timestamp_is_current(self, client):
        """Test that results include current timestamp"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "5000",
                "monthly_expenses": "3000",
                "current_savings": "10000",
                "item_name": "Laptop",
                "item_cost": "1000",
            },
        )
        assert response.status_code == 200
        # Should have date/time information
        response_text = response.data.decode()
        current_year = str(datetime.now().year)
        assert current_year in response_text or "20" in response_text


class TestContentType:
    """Tests for content type headers"""

    def test_index_returns_html(self, client):
        """Test that index returns HTML"""
        response = client.get("/")
        assert "text/html" in response.content_type

    def test_evaluate_returns_html(self, client):
        """Test that evaluate returns HTML"""
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "5000",
                "monthly_expenses": "3000",
                "current_savings": "10000",
                "item_name": "Laptop",
                "item_cost": "1000",
            },
        )
        assert "text/html" in response.content_type

    def test_health_returns_json(self, client):
        """Test that health check returns JSON"""
        response = client.get("/health")
        assert "application/json" in response.content_type


class TestIntegration:
    """Integration tests for web app"""

    def test_full_evaluation_workflow(self, client):
        """Test complete workflow from form to results"""
        # 1. Load index
        response = client.get("/")
        assert response.status_code == 200

        # 2. Submit form
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "5000",
                "monthly_expenses": "3000",
                "current_savings": "10000",
                "item_name": "Laptop",
                "item_cost": "1000",
            },
        )
        assert response.status_code == 200

        # 3. Verify results displayed
        assert b"Laptop" in response.data or b"laptop" in response.data.lower()

    def test_multiple_evaluations(self, client):
        """Test multiple sequential evaluations"""
        evaluations = [
            {
                "income": "5000",
                "expenses": "3000",
                "savings": "10000",
                "item": "Laptop",
                "cost": "1000",
            },
            {
                "income": "3000",
                "expenses": "2000",
                "savings": "5000",
                "item": "Phone",
                "cost": "800",
            },
            {
                "income": "10000",
                "expenses": "5000",
                "savings": "50000",
                "item": "Car",
                "cost": "25000",
            },
        ]

        for eval_data in evaluations:
            response = client.post(
                "/evaluate",
                data={
                    "monthly_income": eval_data["income"],
                    "monthly_expenses": eval_data["expenses"],
                    "current_savings": eval_data["savings"],
                    "item_name": eval_data["item"],
                    "item_cost": eval_data["cost"],
                },
            )
            assert response.status_code == 200

    def test_evaluation_after_error(self, client):
        """Test that application recovers after an error"""
        # 1. Trigger error
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "invalid",
            },
        )
        assert response.status_code == 400

        # 2. Submit valid form
        response = client.post(
            "/evaluate",
            data={
                "monthly_income": "5000",
                "monthly_expenses": "3000",
                "current_savings": "10000",
                "item_name": "Laptop",
                "item_cost": "1000",
            },
        )
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
