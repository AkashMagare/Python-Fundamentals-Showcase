"""Command-line interface for the expense tracker."""

from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path
import sys
from typing import Sequence

from .models import Expense, ValidationError
from .storage import StorageError
from .tracker import ExpenseTracker


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_FILE = PROJECT_ROOT / "data" / "expenses.json"


def positive_float(value: str) -> float:
    """Convert command-line text to a positive floating-point number."""

    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("amount must be a number") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("amount must be greater than zero")
    return round(number, 2)


def valid_month(value: str) -> str:
    """Validate a month argument in ``YYYY-MM`` format."""

    if len(value) != 7 or value[4] != "-" or not value.replace("-", "").isdigit():
        raise argparse.ArgumentTypeError("month must use YYYY-MM format")
    try:
        date.fromisoformat(f"{value}-01")
    except ValueError as exc:
        raise argparse.ArgumentTypeError("month must be a real calendar month") from exc
    return value


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser and all available subcommands."""

    # ``argparse`` is part of the standard library and creates useful --help text.
    parser = argparse.ArgumentParser(
        prog="expense-tracker",
        description="Track personal expenses using a simple JSON file.",
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        default=DEFAULT_DATA_FILE,
        help="JSON file used for storage (default: data/expenses.json)",
    )

    # Subparsers let one Python program expose several related commands.
    commands = parser.add_subparsers(dest="command", required=True)

    add_parser = commands.add_parser("add", help="add a new expense")
    add_parser.add_argument("--amount", required=True, type=positive_float)
    add_parser.add_argument("--category", required=True, help="for example Food or Travel")
    add_parser.add_argument("--description", required=True)
    add_parser.add_argument("--date", dest="spent_on", help="YYYY-MM-DD (default: today)")

    list_parser = commands.add_parser("list", help="list saved expenses")
    list_parser.add_argument("--category")
    list_parser.add_argument("--month", type=valid_month)

    summary_parser = commands.add_parser("summary", help="show spending totals")
    summary_parser.add_argument("--month", type=valid_month)

    delete_parser = commands.add_parser("delete", help="delete an expense by ID")
    delete_parser.add_argument("id", type=int)

    export_parser = commands.add_parser("export", help="export expenses as CSV")
    export_parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data" / "expenses.csv")
    export_parser.add_argument("--month", type=valid_month)

    commands.add_parser("seed-demo", help="add five sample expenses for a quick demo")
    return parser


def format_amount(amount: float) -> str:
    """Format a number as Indian rupees for readable terminal output."""

    # Some Windows terminals use encodings that cannot print the rupee symbol.
    currency_symbol = "₹"
    output_encoding = sys.stdout.encoding or "utf-8"
    try:
        currency_symbol.encode(output_encoding)
    except UnicodeEncodeError:
        currency_symbol = "INR "
    return f"{currency_symbol}{amount:,.2f}"


def print_expenses(expenses: list[Expense]) -> None:
    """Print a small table without using an external table library."""

    if not expenses:
        print("No expenses found.")
        return

    print(f"{'ID':<4} {'Date':<12} {'Category':<16} {'Amount':>12}  Description")
    print("-" * 78)
    for expense in expenses:
        # Formatted strings align values into predictable columns.
        print(
            f"{expense.id:<4} {expense.spent_on:<12} "
            f"{expense.category[:16]:<16} {format_amount(expense.amount):>12}  "
            f"{expense.description}"
        )


def handle_add(tracker: ExpenseTracker, args: argparse.Namespace) -> None:
    """Handle the add command."""

    expense = tracker.add(
        amount=args.amount,
        category=args.category,
        description=args.description,
        spent_on=args.spent_on,
    )
    print(f"Added expense #{expense.id}: {format_amount(expense.amount)} for {expense.category}.")


def handle_list(tracker: ExpenseTracker, args: argparse.Namespace) -> None:
    """Handle the list command."""

    expenses = tracker.list_expenses(category=args.category, month=args.month)
    print_expenses(expenses)
    if expenses:
        print(f"\nTotal shown: {format_amount(sum(item.amount for item in expenses))}")


def handle_summary(tracker: ExpenseTracker, args: argparse.Namespace) -> None:
    """Handle the summary command."""

    label = args.month or "all time"
    print(f"Expense summary ({label})")
    print("=" * 30)
    print(f"Total spent: {format_amount(tracker.total(month=args.month))}")

    category_totals = tracker.category_totals(month=args.month)
    if not category_totals:
        print("No expenses found.")
        return
    print("\nBy category:")
    for category, amount in category_totals.items():
        print(f"- {category}: {format_amount(amount)}")


def handle_delete(tracker: ExpenseTracker, args: argparse.Namespace) -> None:
    """Handle the delete command."""

    removed = tracker.delete(args.id)
    print(f"Deleted expense #{removed.id}: {removed.description}.")


def handle_export(tracker: ExpenseTracker, args: argparse.Namespace) -> None:
    """Handle the export command."""

    expenses = tracker.list_expenses(month=args.month)
    tracker.export(args.output, month=args.month)
    print(f"Exported {len(expenses)} expense(s) to {args.output}.")


def handle_seed_demo(tracker: ExpenseTracker) -> None:
    """Add sample records so a recruiter can try the project immediately."""

    if tracker.expenses:
        print("Demo data was skipped because the data file already contains expenses.")
        return

    today = date.today()
    demo_records = [
        ("Food", "Lunch with the team", 280.0),
        ("Transport", "Metro recharge", 500.0),
        ("Learning", "Python book", 650.0),
        ("Bills", "Internet bill", 999.0),
        ("Shopping", "Notebook and stationery", 220.0),
    ]
    for days_ago, (category, description, amount) in enumerate(demo_records):
        tracker.add(
            amount=amount,
            category=category,
            description=description,
            spent_on=(today - timedelta(days=days_ago)).isoformat(),
        )
    print(f"Added {len(demo_records)} demo expenses.")


def run_command(args: argparse.Namespace) -> None:
    """Create the service and dispatch to the selected command."""

    tracker = ExpenseTracker(args.data_file)

    # A simple conditional dispatcher makes the command flow easy to follow.
    if args.command == "add":
        handle_add(tracker, args)
    elif args.command == "list":
        handle_list(tracker, args)
    elif args.command == "summary":
        handle_summary(tracker, args)
    elif args.command == "delete":
        handle_delete(tracker, args)
    elif args.command == "export":
        handle_export(tracker, args)
    elif args.command == "seed-demo":
        handle_seed_demo(tracker)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code.

    Keeping ``main`` parameterised with ``argv`` makes it straightforward to
    test commands without launching a separate process.
    """

    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run_command(args)
    except (ValidationError, StorageError, KeyError, OSError) as exc:
        # User-facing errors get a short message instead of a traceback.
        print(f"Error: {exc}")
        return 1
    return 0
