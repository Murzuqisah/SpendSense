"""
SpendSense Web Application
Flask-based web interface for the SpendSense decision engine
"""

import os
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for
from src.decision_engine import DecisionEngine
from src.validation import InputValidator, ValidationError

# Get the absolute path to the project root
PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"

# Initialize Flask app with absolute paths
app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(STATIC_DIR))
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-change-in-production")

# Initialize decision engine
# Use AI only if API key is available, otherwise fall back to rule-based engine
use_ai = bool(os.environ.get("ANTHROPIC_API_KEY"))
engine = DecisionEngine(use_ai=use_ai)
validator = InputValidator()

if not use_ai:
    print(
        "Warning: ANTHROPIC_API_KEY not set. Running in fallback mode (rule-based decisions only)"
    )


@app.route("/")
def index():
    """Display the main evaluation form"""
    return render_template("index.html")


@app.route("/evaluate", methods=["POST"])
def evaluate():
    """
    Process the evaluation form and return decision results
    """
    try:
        # Extract form data
        monthly_income = request.form.get("monthly_income")
        fixed_expenses = request.form.get("fixed_expenses")
        savings_goal = request.form.get("savings_goal")
        item_name = request.form.get("item_name")
        item_cost = request.form.get("item_cost")

        # Validate inputs
        if not all(
            [monthly_income, fixed_expenses, savings_goal, item_name, item_cost]
        ):
            return (
                render_template(
                    "error.html",
                    error_title="Missing Information",
                    error_message="Please fill in all fields",
                    suggestions=[
                        "All fields are required to make an evaluation",
                        "Please provide income, expenses, savings goal, and item details",
                    ],
                ),
                400,
            )

        # Convert to appropriate types
        try:
            monthly_income = float(monthly_income)
            fixed_expenses = float(fixed_expenses)
            savings_goal = float(savings_goal)
            item_cost = float(item_cost)
        except ValueError:
            return (
                render_template(
                    "error.html",
                    error_title="Invalid Input Format",
                    error_message="Please enter valid numbers",
                    suggestions=[
                        "All monetary values must be numbers",
                        "Do not use commas or currency symbols",
                    ],
                ),
                400,
            )

        # Make decision
        result = engine.evaluate(
            {
                "monthly_income": monthly_income,
                "fixed_expenses": fixed_expenses,
                "savings_goal": savings_goal,
                "planned_purchase": {"item": item_name, "cost": item_cost},
            }
        )

        # Check for errors
        if result.get("status") == "validation_error":
            return (
                render_template(
                    "error.html",
                    error_title="Validation Error",
                    error_message=result.get("error", "Invalid input data"),
                    suggestions=[
                        "Check that all values are positive",
                        "Monthly income should be greater than fixed expenses",
                        "Savings goal should be positive",
                    ],
                ),
                400,
            )

        if result.get("status") == "error":
            return (
                render_template(
                    "error.html",
                    error_title="Evaluation Error",
                    error_message=result.get("error", "An error occurred"),
                    suggestions=[
                        "Please try again with different values",
                        "Contact support if the problem persists",
                    ],
                ),
                500,
            )

        # Extract decision information
        final_decision = result.get("final_decision", {})
        risk_assessment = result.get("risk_assessment", {})
        financial_analysis = result.get("financial_analysis", {})
        ai_reasoning = result.get("ai_reasoning", {})

        # Prepare context for results template
        context = {
            # Purchase info
            "item_name": item_name,
            "purchase_item": item_name,
            "item_cost": item_cost,
            "purchase_cost": item_cost,
            # Decision info
            "decision": final_decision.get("recommendation", "UNCERTAIN"),
            "decision_summary": final_decision.get("summary", "Analysis complete"),
            "recommendation": final_decision.get(
                "recommendation", "See analysis above"
            ),
            # Risk and confidence
            "risk_level": risk_assessment.get("risk_level", "UNKNOWN"),
            "confidence": risk_assessment.get("confidence_score", 0),
            "confidence_score": risk_assessment.get("confidence_score", 0),
            "percentage_of_disposable": risk_assessment.get(
                "percentage_of_disposable", 0
            ),
            # Financial info
            "timestamp": result.get("timestamp", ""),
            "monthly_income": monthly_income,
            "fixed_expenses": fixed_expenses,
            "savings_goal": savings_goal,
            "disposable_income": financial_analysis.get("disposable_income", 0),
            "remaining_after_purchase": financial_analysis.get(
                "remaining_after_purchase", 0
            ),
            # Hard stop info
            "hard_stop_triggered": financial_analysis.get("hard_stop_triggered", False),
            "hard_stop_reason": financial_analysis.get("hard_stop_reason"),
            "can_afford": financial_analysis.get("can_afford", False),
            # AI/Fallback reasoning
            "ai_reasoning": ai_reasoning.get("explanation", "Analysis complete"),
            "alternatives": ai_reasoning.get("alternatives", []),
            "next_steps": final_decision.get("next_steps", []),
            "mode": ai_reasoning.get("mode", "unknown"),
        }

        return render_template("results.html", **context)

    except Exception as e:
        return (
            render_template(
                "error.html",
                error_title="Evaluation Error",
                error_message=str(e),
                suggestions=[
                    "There was an unexpected error during evaluation",
                    "Please try again with different values",
                    "Contact support if the problem persists",
                ],
            ),
            500,
        )


@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "SpendSense Web API"})


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return (
        render_template(
            "error.html",
            error_title="Page Not Found",
            error_message="The page you requested does not exist",
            suggestions=[
                "Check the URL in your browser",
                "Return to the home page and try again",
            ],
        ),
        404,
    )


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return (
        render_template(
            "error.html",
            error_title="Server Error",
            error_message="Something went wrong on our end",
            suggestions=[
                "Please try again later",
                "Clear your browser cache and refresh",
                "Contact support if the problem persists",
            ],
        ),
        500,
    )


def run_app(host="127.0.0.1", port=5000, debug=False):
    """Run the Flask application"""
    print(f"Starting SpendSense Web Application")
    print(f"Server: http://{host}:{port}")
    print(f"Debug mode: {debug}")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_app(debug=True)
