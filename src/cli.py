#!/usr/bin/env python
"""Command-line interface for SpendSense Agent."""

import json
import sys
import argparse
from src.decision_engine import DecisionEngine
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def print_banner():
    """Print SpendSense banner."""
    print("""
╔════════════════════════════════════════╗
║          SPENDSENSE AGENT              ║
║   Personal Budgeting Decision Tool     ║
╚════════════════════════════════════════╝
""")


def interactive_mode():
    """Run SpendSense in interactive mode."""
    print_banner()
    print("Welcome to SpendSense! Let's analyze your purchase decision.\n")
    print("Press Ctrl+C to exit at any time.\n")

    engine = DecisionEngine(use_ai=True)

    try:
        while True:
            print("-" * 60)
            print("PURCHASE EVALUATION")
            print("-" * 60)

            # Collect input
            try:
                monthly_income = float(input("Monthly Income (KSH): "))
                fixed_expenses = float(input("Fixed Monthly Expenses ($): "))
                savings_goal = float(input("Monthly Savings Goal ($): "))
                purchase_item = input("What do you want to buy?: ")
                purchase_cost = float(input("Purchase Cost ($): "))

            except ValueError:
                print("[STOP] Invalid input. Please enter numbers for amounts.\n")
                continue
            except KeyboardInterrupt:
                print("\n\nThank you for using SpendSense!")
                sys.exit(0)

            # Prepare input data
            input_data = {
                "monthly_income": monthly_income,
                "fixed_expenses": fixed_expenses,
                "savings_goal": savings_goal,
                "planned_purchase": {"item": purchase_item, "cost": purchase_cost},
            }

            # Evaluate
            print("\n[PROCESSING] Analyzing your purchase...\n")
            report = engine.evaluate(input_data)

            # Display results
            if report["status"] == "success":
                display_report(report)
            else:
                print(f"[STOP] Error: {report['error']}\n")

            # Ask if user wants to continue
            print("\n" + "=" * 60)
            continue_choice = (
                input("Evaluate another purchase? (yes/no): ").lower().strip()
            )
            if continue_choice not in ["yes", "y"]:
                print("\nThank you for using SpendSense!")
                break

            print("\n")

    except KeyboardInterrupt:
        print("\n\nThank you for using SpendSense!")
        sys.exit(0)


def display_report(report: dict):
    """Display evaluation report in a user-friendly format."""
    # Final decision
    final = report["final_decision"]
    print("\n" + "=" * 60)
    print("DECISION SUMMARY")
    print("=" * 60)
    print(f"\n{final['summary']}\n")

    # Risk assessment
    risk = report["risk_assessment"]
    print("-" * 60)
    print("RISK ASSESSMENT")
    print("-" * 60)
    print(f"Risk Level: {risk['risk_level']}")
    print(f"Confidence Score: {risk['confidence_score']:.1%}")
    print(f"Percentage of Disposable Income: {risk['percentage_of_disposable']:.1f}%")

    # Financial analysis
    finance = report["financial_analysis"]
    print("\n" + "-" * 60)
    print("FINANCIAL ANALYSIS")
    print("-" * 60)
    metrics = final["key_metrics"]
    print(f"Monthly Income: KSH {metrics['monthly_income']:.2f}")
    print(f"Disposable Income: ${metrics['disposable_income']:.2f}")
    print(f"Purchase Cost: ${metrics['purchase_cost']:.2f}")
    if metrics["remaining_after_purchase"] is not None:
        print(f"Remaining After Purchase: ${metrics['remaining_after_purchase']:.2f}")

    if finance.get("hard_stop_triggered"):
        print(f"\n[ALERT] Hard Stop: {finance['hard_stop_reason']}")

    # AI Reasoning
    print("\n" + "-" * 60)
    print("ANALYSIS & INSIGHTS")
    print("-" * 60)
    ai = report["ai_reasoning"]
    print(f"\n{ai['explanation']}\n")

    if ai["alternatives"]:
        print("Suggested Alternatives:")
        for i, alt in enumerate(ai["alternatives"], 1):
            print(f"  {i}. {alt}")

    # Next steps
    print("\n" + "-" * 60)
    print("RECOMMENDED NEXT STEPS")
    print("-" * 60)
    for step in final["next_steps"]:
        print(f"• {step}")


def json_mode(input_file: str = None):
    """Run SpendSense with JSON input/output."""
    engine = DecisionEngine(use_ai=True)

    if input_file:
        try:
            with open(input_file, "r") as f:
                input_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File '{input_file}' not found")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in '{input_file}'")
            sys.exit(1)
    else:
        # Read from stdin
        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            print("Error: Invalid JSON from stdin")
            sys.exit(1)

    # Evaluate
    report = engine.evaluate(input_data)

    # Output JSON
    print(json.dumps(report, indent=2))


def quick_evaluate(
    income: float, expenses: float, savings: float, item: str, cost: float
):
    """Quick evaluation with command-line arguments."""
    engine = DecisionEngine(use_ai=True)

    input_data = {
        "monthly_income": income,
        "fixed_expenses": expenses,
        "savings_goal": savings,
        "planned_purchase": {"item": item, "cost": cost},
    }

    report = engine.evaluate(input_data)

    if report["status"] == "success":
        display_report(report)
    else:
        print(f"[STOP] Error: {report['error']}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SpendSense: Personal Budgeting Decision Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (recommended)
  python -m src.cli

  # Quick evaluation
  python -m src.cli --quick --income 5000 --expenses 1500 --savings 500 \\
                            --item "Laptop" --cost 1000

  # JSON mode (read from file)
  python -m src.cli --json input.json > output.json

  # JSON mode (read from stdin)
  cat input.json | python -m src.cli --json
        """,
    )

    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode (default)",
    )

    parser.add_argument(
        "--quick",
        "-q",
        action="store_true",
        help="Quick evaluation mode with command-line arguments",
    )

    parser.add_argument(
        "--json",
        "-j",
        nargs="?",
        const="-",
        metavar="FILE",
        help="JSON input/output mode (FILE or stdin if not specified)",
    )

    # Quick mode arguments
    parser.add_argument("--income", type=float, help="Monthly income")
    parser.add_argument("--expenses", type=float, help="Fixed monthly expenses")
    parser.add_argument("--savings", type=float, help="Monthly savings goal")
    parser.add_argument("--item", help="Item to purchase")
    parser.add_argument("--cost", type=float, help="Purchase cost")

    args = parser.parse_args()

    try:
        # Determine mode
        if args.quick:
            if not all(
                [
                    args.income,
                    args.expenses is not None,
                    args.savings is not None,
                    args.item,
                    args.cost,
                ]
            ):
                parser.error(
                    "Quick mode requires: --income, --expenses, --savings, --item, --cost"
                )
            quick_evaluate(
                args.income, args.expenses, args.savings, args.item, args.cost
            )

        elif args.json is not None:
            input_file = None if args.json == "-" else args.json
            json_mode(input_file)

        else:
            # Default to interactive mode
            interactive_mode()

    except KeyboardInterrupt:
        print("\n\nExiting SpendSense.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
