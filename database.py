"""SQLite persistence and exact-to-cents money handling for Expense Tracker."""
import csv
import sqlite3
from contextlib import contextmanager
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

DEFAULT_DB = Path(__file__).with_name("expenses.db")
CATEGORIES = ("Food", "Utilities", "Travel", "Education", "Health", "Shopping", "Salary", "Other")


def money_to_cents(value):
    try:
        amount = Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError):
        raise ValueError("Amount must be a valid number.") from None
    if not amount.is_finite():
        raise ValueError("Amount must be a finite number.")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    rounded = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(rounded * 100)


def validate_transaction(kind, amount, category, txn_date, description=""):
    kind = str(kind).strip().lower()
    if kind not in ("income", "expense"):
        raise ValueError("Type must be income or expense.")
    cents = money_to_cents(amount)
    category = str(category).strip()
    if not category:
        raise ValueError("Category cannot be empty.")
    try:
        parsed = date.fromisoformat(str(txn_date).strip())
    except (ValueError, TypeError):
        raise ValueError("Date must be a valid date in YYYY-MM-DD format.") from None
    if parsed.isoformat() != str(txn_date).strip():
        raise ValueError("Date must use YYYY-MM-DD format.")
    return kind, cents, category, parsed.isoformat(), str(description).strip()


class ExpenseDatabase:
    def __init__(self, db_path=DEFAULT_DB):
        self.db_path = str(db_path)
        self._create_table()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def _connection(self):
        conn = self._connect()
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def _create_table(self):
        with self._connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL CHECK(kind IN ('income', 'expense')),
                    amount_cents INTEGER NOT NULL CHECK(amount_cents > 0),
                    category TEXT NOT NULL,
                    txn_date TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

    @staticmethod
    def _row(row):
        if row is None:
            return None
        result = dict(row)
        result["amount"] = f"{result.pop('amount_cents') / 100:.2f}"
        return result

    def add_transaction(self, kind, amount, category, txn_date, description=""):
        values = validate_transaction(kind, amount, category, txn_date, description)
        with self._connection() as conn:
            cursor = conn.execute(
                """INSERT INTO transactions(kind, amount_cents, category, txn_date, description)
                   VALUES (?, ?, ?, ?, ?)""", values
            )
            txn_id = cursor.lastrowid
        return self.get_transaction(txn_id)

    def get_transaction(self, txn_id):
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM transactions WHERE id=?", (txn_id,)).fetchone()
        return self._row(row)

    def list_transactions(self, start_date=None, end_date=None, category=None):
        conditions, params = [], []
        if start_date:
            self._validate_date(start_date)
            conditions.append("txn_date >= ?")
            params.append(start_date)
        if end_date:
            self._validate_date(end_date)
            conditions.append("txn_date <= ?")
            params.append(end_date)
        if start_date and end_date and start_date > end_date:
            raise ValueError("Start date must be on or before end date.")
        if category:
            conditions.append("category = ? COLLATE NOCASE")
            params.append(category.strip())
        sql = "SELECT * FROM transactions"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY txn_date DESC, id DESC"
        with self._connection() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [self._row(row) for row in rows]

    @staticmethod
    def _validate_date(value):
        try:
            date.fromisoformat(str(value))
        except (ValueError, TypeError):
            raise ValueError("Date must be in YYYY-MM-DD format.") from None

    def summary(self, start_date=None, end_date=None, category=None):
        transactions = self.list_transactions(start_date, end_date, category)
        income = sum(int(round(float(t["amount"]) * 100)) for t in transactions if t["kind"] == "income")
        expenses = sum(int(round(float(t["amount"]) * 100)) for t in transactions if t["kind"] == "expense")
        by_category = {}
        for t in transactions:
            if t["kind"] == "expense":
                key = t["category"]
                by_category[key] = by_category.get(key, 0) + int(round(float(t["amount"]) * 100))
        return {
            "income": f"{income / 100:.2f}",
            "expenses": f"{expenses / 100:.2f}",
            "balance": f"{(income - expenses) / 100:.2f}",
            "expenses_by_category": {k: f"{v / 100:.2f}" for k, v in sorted(by_category.items())},
            "count": len(transactions),
        }

    def export_csv(self, filepath, start_date=None, end_date=None, category=None):
        transactions = self.list_transactions(start_date, end_date, category)
        columns = ("id", "kind", "amount", "category", "txn_date", "description")
        with open(filepath, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            for transaction in transactions:
                writer.writerow({key: transaction[key] for key in columns})
        return len(transactions)
