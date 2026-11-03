"""Application service that connects models, storage, and reports."""

from __future__ import annotations

from pathlib import Path

from .models import Expense, build_expense
from .reports import export_csv, filter_expenses, total_amount, totals_by_category
from .storage import load_expenses, save_expenses


class ExpenseTracker:
    """Manage expense records stored in a JSON file."""

    def __init__(self, data_file: Path) -> None:
        self.data_file = data_file
        # The list is the main in-memory collection used by the application.
        self.expenses = load_expenses(data_file)

    def _save(self) -> None:
        """Save the current list after a change."""

        save_expenses(self.data_file, self.expenses)

    def add(
        self,
        *,
        amount: float,
        category: str,
        description: str,
        spent_on: str | None = None,
    ) -> Expense:
        """Create, store, and return a new expense."""

        # ``max`` finds the largest existing ID; ``default`` handles an empty list.
        next_id = max((expense.id for expense in self.expenses), default=0) + 1
        expense = build_expense(
            expense_id=next_id,
            amount=amount,
            category=category,
            description=description,
            spent_on=spent_on,
        )
        self.expenses.append(expense)
        self._save()
        return expense

    def list_expenses(
        self,
        *,
        category: str | None = None,
        month: str | None = None,
    ) -> list[Expense]:
        """Return matching expenses in newest-first order."""

        return filter_expenses(self.expenses, category=category, month=month)

    def delete(self, expense_id: int) -> Expense:
        """Delete one expense and return it, or raise ``KeyError``."""

        for index, expense in enumerate(self.expenses):
            # ``enumerate`` provides both a position and its item.
            if expense.id == expense_id:
                removed = self.expenses.pop(index)
                self._save()
                return removed
        raise KeyError(f"expense {expense_id} was not found")

    def total(self, *, month: str | None = None) -> float:
        """Return total spending, optionally limited to a month."""

        return total_amount(self.list_expenses(month=month))

    def category_totals(self, *, month: str | None = None) -> dict[str, float]:
        """Return spending grouped by category."""

        return totals_by_category(self.list_expenses(month=month))

    def export(self, output_file: Path, *, month: str | None = None) -> None:
        """Export matching records as CSV."""

        export_csv(output_file, self.list_expenses(month=month))
