"""Reports and CSV export for the expense tracker."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from .models import Expense


def filter_expenses(
    expenses: list[Expense],
    *,
    category: str | None = None,
    month: str | None = None,
) -> list[Expense]:
    """Return expenses matching optional category and month filters."""

    # A list comprehension is a concise way to build a filtered list.
    filtered = [
        expense
        for expense in expenses
        if (category is None or expense.category.lower() == category.lower())
        and (month is None or expense.spent_on.startswith(month))
    ]

    # ``sorted`` returns a new list, keeping the original data unchanged.
    return sorted(filtered, key=lambda expense: (expense.spent_on, expense.id), reverse=True)


def total_amount(expenses: list[Expense]) -> float:
    """Calculate the total amount in a list of expenses."""

    # ``sum`` combines values from a generator expression.
    return round(sum(expense.amount for expense in expenses), 2)


def totals_by_category(expenses: list[Expense]) -> dict[str, float]:
    """Group spending by category and return alphabetical results."""

    totals: defaultdict[str, float] = defaultdict(float)
    for expense in expenses:
        # ``defaultdict`` creates a zero value for a new category automatically.
        totals[expense.category] += expense.amount

    # A dictionary comprehension creates a clean rounded result.
    return {
        category: round(amount, 2)
        for category, amount in sorted(totals.items(), key=lambda item: item[0].lower())
    }


def export_csv(file_path: Path, expenses: list[Expense]) -> None:
    """Export expense records to a CSV file for spreadsheet use."""

    file_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["id", "amount", "category", "description", "spent_on", "created_at"]
    with file_path.open("w", newline="", encoding="utf-8") as file:
        # ``DictWriter`` maps dictionary keys to CSV columns.
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for expense in expenses:
            writer.writerow(expense.to_dict())
