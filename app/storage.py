"""JSON file storage for expense records."""

from __future__ import annotations

import json
from pathlib import Path

from .models import Expense, ValidationError


class StorageError(RuntimeError):
    """Raised when the expense file cannot be read or written."""


def load_expenses(file_path: Path) -> list[Expense]:
    """Load expenses from a JSON file.

    A missing file is treated as an empty list, which makes first-time use
    convenient. Other file errors are reported instead of being hidden.
    """

    if not file_path.exists():
        return []

    try:
        with file_path.open("r", encoding="utf-8") as file:
            raw_records = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise StorageError(f"could not read {file_path}: {exc}") from exc

    if not isinstance(raw_records, list):
        raise StorageError("expense file must contain a JSON list")

    expenses: list[Expense] = []
    for record in raw_records:
        if not isinstance(record, dict):
            raise StorageError("each expense record must be a JSON object")
        try:
            expenses.append(Expense.from_dict(record))
        except ValidationError as exc:
            raise StorageError(f"invalid expense record: {exc}") from exc
    return expenses


def save_expenses(file_path: Path, expenses: list[Expense]) -> None:
    """Write expense objects to a formatted JSON file."""

    # ``mkdir`` with ``parents=True`` creates missing folders safely.
    file_path.parent.mkdir(parents=True, exist_ok=True)
    payload = [expense.to_dict() for expense in expenses]
    try:
        with file_path.open("w", encoding="utf-8") as file:
            # ``indent`` makes the data easy for a human to inspect on GitHub.
            json.dump(payload, file, indent=2)
            file.write("\n")
    except OSError as exc:
        raise StorageError(f"could not write {file_path}: {exc}") from exc
