# Expense Tracker — CodeNova Task 2

An interactive command-line income and expense tracker built with Python and SQLite.

## Features
- Record income and expenses with amount, date, category, and description.
- Calculate total income, expenses, net balance, and expense totals by category.
- Filter history by inclusive date range and category.
- Export filtered transactions to CSV.
- Reject non-positive amounts, invalid transaction types, malformed dates, and reversed date ranges.
- Persistent SQLite storage and automated unit tests.
- Uses integer cents internally to avoid common floating-point money calculation errors.

## Requirements
Python 3.9 or later. No third-party packages or API keys are required.

## Run in Termux
```bash
cd ~/codenova-internship/expense-tracker
python main.py
```

Load demonstration data:
```bash
python sample_data.py
```
The `expenses.db` file is created automatically.

## Run tests
```bash
python -m unittest discover -s tests -v
```

## Calculation logic
Transaction amounts are validated as positive decimal values and converted to integer cents for storage. Balance equals total income minus total expenses. Category totals include expenses only. Date filters are inclusive: both the start date and end date are included. CSV exports contain the transaction ID, type, amount, category, date, and description.

## Screenshots for submission
Capture:
1. Main menu.
2. Adding an income and an expense.
3. Summary with totals and category breakdown.
4. Filtering transactions by dates/category.
5. Successful CSV export (optionally open the CSV in a text viewer).
6. Automated tests passing.

Use only sample or fictional data in screenshots.

## GitHub publishing
Create a **public** repository named `codenova-expense-tracker` on GitHub, then run:
```bash
git init
git add main.py database.py sample_data.py requirements.txt README.md tests
git commit -m "Build SQLite Expense Tracker"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/codenova-expense-tracker.git
git push -u origin main
```
Replace `YOUR_USERNAME` with your GitHub username. Do not commit a database containing private financial data; `.gitignore` excludes the default database.
