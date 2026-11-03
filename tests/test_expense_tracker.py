import csv
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from app.cli import main
from app.models import ValidationError, build_expense
from app.storage import load_expenses
from app.tracker import ExpenseTracker


class ExpenseTrackerTests(unittest.TestCase):
    """Test the main user workflows using temporary files."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temporary_directory.name) / "expenses.json"
        self.tracker = ExpenseTracker(self.data_file)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_add_persists_and_loads_expense(self) -> None:
        expense = self.tracker.add(
            amount=250.50,
            category="Food",
            description="Lunch",
            spent_on="2026-11-03",
        )

        self.assertEqual(expense.id, 1)
        self.assertEqual(load_expenses(self.data_file)[0].description, "Lunch")
        with self.data_file.open(encoding="utf-8") as file:
            self.assertEqual(json.load(file)[0]["amount"], 250.5)

    def test_filters_and_summarises_expenses(self) -> None:
        self.tracker.add(
            amount=100,
            category="Food",
            description="Breakfast",
            spent_on="2026-11-01",
        )
        self.tracker.add(
            amount=400,
            category="Travel",
            description="Train ticket",
            spent_on="2026-10-20",
        )
        self.tracker.add(
            amount=200,
            category="Food",
            description="Dinner",
            spent_on="2026-11-02",
        )

        self.assertEqual(len(self.tracker.list_expenses(category="food")), 2)
        self.assertEqual(self.tracker.total(month="2026-11"), 300)
        self.assertEqual(self.tracker.category_totals(), {"Food": 300, "Travel": 400})

    def test_delete_removes_requested_expense(self) -> None:
        expense = self.tracker.add(amount=50, category="Food", description="Tea")

        removed = self.tracker.delete(expense.id)

        self.assertEqual(removed.description, "Tea")
        self.assertEqual(self.tracker.list_expenses(), [])
        with self.assertRaises(KeyError):
            self.tracker.delete(expense.id)

    def test_csv_export_has_header_and_rows(self) -> None:
        self.tracker.add(amount=99.99, category="Learning", description="Course")
        output_file = Path(self.temporary_directory.name) / "exports" / "expenses.csv"

        self.tracker.export(output_file)

        with output_file.open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["category"], "Learning")
        self.assertEqual(rows[0]["amount"], "99.99")

    def test_invalid_amount_and_date_are_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            build_expense(
                expense_id=1,
                amount=0,
                category="Food",
                description="Invalid",
            )
        with self.assertRaises(ValidationError):
            build_expense(
                expense_id=1,
                amount=10,
                category="Food",
                description="Invalid date",
                spent_on="not-a-date",
            )
        with self.assertRaises(ValidationError):
            build_expense(
                expense_id=1,
                amount=float("nan"),
                category="Food",
                description="Not a real amount",
            )

    def test_cli_can_seed_and_show_summary(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            result = main(["--data-file", str(self.data_file), "seed-demo"])
            result = main(["--data-file", str(self.data_file), "summary"])

        self.assertEqual(result, 0)
        self.assertIn("Total spent:", output.getvalue())
        self.assertIn("Learning", output.getvalue())


if __name__ == "__main__":
    unittest.main()
