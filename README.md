# Python Fundamentals Showcase

I built this small **Personal Expense Tracker CLI** while practising Python fundamentals.

It lets me record daily expenses, check where my money is going, and export the data to CSV. I kept the project simple and used only Python's standard library so I could understand how each part works instead of hiding the logic behind a framework.

This is one of my practice projects and a good example of how I am building my Python skills step by step.

## What I built

- Adds personal expenses with amount, category, description, and date
- Saves records locally in a readable JSON file
- Lists expenses with category and month filters
- Calculates total spending and category totals
- Deletes an expense by ID
- Exports records to CSV for Excel or Google Sheets
- Includes demo data so the project can be tried in seconds
- Includes unit tests and GitHub Actions CI

## Quick start

I intentionally used only Python's standard library, so there are no external packages to install.

```bash
git clone https://github.com/AkashMagare/Python-Fundamentals-Showcase.git
cd Python-Fundamentals-Showcase

python main.py seed-demo
python main.py list
python main.py summary
```

On Windows, use `python` or `py` depending on your installation.

## Example commands

```bash
# Add a new expense. The date is optional and defaults to today.
python main.py add --amount 450 --category Food --description "Dinner" --date 2026-11-03

# View all expenses or filter the list.
python main.py list
python main.py list --category Food
python main.py list --month 2026-11

# View totals.
python main.py summary
python main.py summary --month 2026-11

# Remove an expense by its ID.
python main.py delete 3

# Export the current records for spreadsheet analysis.
python main.py export --output reports/expenses.csv
```

The default data file is `data/expenses.json`. Use a different file without changing the code:

```bash
python main.py --data-file data/demo.json list
```

## Example output

```text
Expense summary (all time)
==============================
Total spent: INR 2,649.00

By category:
- Bills: INR 999.00
- Food: INR 280.00
- Learning: INR 650.00
- Shopping: INR 220.00
- Transport: INR 500.00
```

## What I practised

| Concept | Where to find it | Why it is used |
| --- | --- | --- |
| Variables and constants | `app/cli.py` | Store configuration and command values |
| Functions and return values | `app/models.py`, `app/reports.py` | Split work into small reusable units |
| Arguments and default values | `build_expense()` | Make functions flexible and readable |
| Type hints | All application modules | Explain expected data types |
| Classes and objects | `Expense`, `ExpenseTracker` | Group data with related behaviour |
| Dataclasses | `app/models.py` | Reduce boilerplate for a data model |
| Lists and dictionaries | `app/storage.py`, `app/reports.py` | Hold records and grouped totals |
| Loops and comprehensions | `app/reports.py`, `app/cli.py` | Process collections clearly |
| `if` / `elif` / `else` | Validation and command dispatch | Make decisions in the program |
| Exceptions | `ValidationError`, `StorageError` | Handle invalid input safely |
| File handling | `app/storage.py` | Read and write JSON data |
| CSV handling | `app/reports.py` | Export data for spreadsheets |
| `argparse` | `app/cli.py` | Build a helpful command-line interface |
| `datetime` | `app/models.py`, `app/cli.py` | Validate dates and create timestamps |
| Unit testing | `tests/test_expense_tracker.py` | Verify behaviour automatically |

I added comments next to the parts I was learning. They explain things such as list comprehensions, `defaultdict`, `enumerate`, `argparse`, exceptions, and `if` statements.

## Project structure

```text
Python-Fundamentals-Showcase/
├── app/
│   ├── cli.py          # Commands, argument parsing, and terminal output
│   ├── models.py       # Expense dataclass and validation
│   ├── reports.py      # Filtering, totals, and CSV export
│   ├── storage.py      # JSON file read/write functions
│   └── tracker.py      # Application service
├── data/
│   └── .gitkeep        # Runtime JSON data is ignored by Git
├── tests/
│   └── test_expense_tracker.py
├── .github/workflows/ci.yml
├── .gitignore
├── LICENSE
├── main.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Run the tests

```bash
python -m unittest discover -s tests -v
python -m compileall -q .
```

The tests use temporary directories, so they do not modify your real expense file.

## Why I made these choices

- **JSON instead of a database:** I wanted the first version to be easy to open and understand.
- **Standard library only:** this helped me focus on Python itself before learning a framework.
- **Separate modules:** I split the code into smaller files so each part has one clear job.
- **Input validation:** the program should catch invalid amounts, empty descriptions, and incorrect dates before saving them.

## Future improvements

- Add a SQLite storage option
- Add budgets and budget alerts by category
- Add charts for monthly spending
- Add recurring expenses
- Add a web interface using Flask or FastAPI

## License

This project is available under the MIT License.
