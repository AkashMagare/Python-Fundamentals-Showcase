"""Data models for the expense tracker.

This module is intentionally small so the basic Python concepts are easy to
see: a class, a dataclass, type hints, validation, and conversion to/from a
dictionary that can be written as JSON.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import math
from typing import Any


class ValidationError(ValueError):
    """Raised when a user supplies invalid expense information."""


def validate_date(value: str) -> str:
    """Return an ISO date string after checking that it is valid.

    ``datetime.date.fromisoformat`` is a useful standard-library function for
    validating dates without writing a long regular expression ourselves.
    """

    try:
        parsed_date = date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError("date must use YYYY-MM-DD format") from exc
    return parsed_date.isoformat()


@dataclass(slots=True)
class Expense:
    """One expense record stored by the application."""

    id: int
    amount: float
    category: str
    description: str
    spent_on: str
    created_at: str

    def __post_init__(self) -> None:
        """Validate and normalise fields whenever an object is created."""

        # ``if`` statements enforce business rules before data is saved.
        if self.id < 1:
            raise ValidationError("id must be a positive integer")
        try:
            self.amount = round(float(self.amount), 2)
        except (TypeError, ValueError) as exc:
            raise ValidationError("amount must be a number") from exc
        if not math.isfinite(self.amount) or self.amount <= 0:
            raise ValidationError("amount must be greater than zero")

        # ``strip`` removes accidental spaces from user input.
        self.category = self.category.strip()
        self.description = self.description.strip()
        if not self.category:
            raise ValidationError("category cannot be empty")
        if not self.description:
            raise ValidationError("description cannot be empty")

        self.spent_on = validate_date(self.spent_on)

    def to_dict(self) -> dict[str, Any]:
        """Convert the object into a JSON-friendly dictionary."""

        # A dictionary stores related values by readable keys.
        return {
            "id": self.id,
            "amount": round(self.amount, 2),
            "category": self.category,
            "description": self.description,
            "spent_on": self.spent_on,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Expense":
        """Build an ``Expense`` object from data loaded from JSON."""

        try:
            return cls(
                id=int(data["id"]),
                amount=float(data["amount"]),
                category=str(data["category"]),
                description=str(data["description"]),
                spent_on=str(data["spent_on"]),
                created_at=str(data.get("created_at", "")),
            )
        except (KeyError, TypeError, ValueError) as exc:
            # Convert low-level parsing errors into one clear application error.
            raise ValidationError("expense record has an invalid format") from exc


def build_expense(
    *,
    expense_id: int,
    amount: float,
    category: str,
    description: str,
    spent_on: str | None = None,
) -> Expense:
    """Create a new expense with sensible defaults.

    This function demonstrates a reusable function with keyword-only
    arguments, a default value, and a standard-library timestamp.
    """

    selected_date = spent_on or date.today().isoformat()
    created_at = datetime.now().astimezone().isoformat(timespec="seconds")
    return Expense(
        id=expense_id,
        amount=round(float(amount), 2),
        category=category,
        description=description,
        spent_on=selected_date,
        created_at=created_at,
    )
