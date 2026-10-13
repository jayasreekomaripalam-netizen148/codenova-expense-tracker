import csv
import tempfile
import unittest
from pathlib import Path
from database import ExpenseDatabase


class ExpenseTrackerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = ExpenseDatabase(Path(self.temp.name) / "test.db")

    def tearDown(self):
        self.temp.cleanup()

    def seed(self):
        self.db.add_transaction("income", "1000.00", "Salary", "2026-10-01", "Pay")
        self.db.add_transaction("expense", "12.35", "Food", "2026-10-02", "Lunch")
        self.db.add_transaction("expense", "7.65", "Food", "2026-10-03", "Snack")
        self.db.add_transaction("expense", "20.00", "Travel", "2026-10-05", "Bus")

    def test_money_validation(self):
        with self.assertRaises(ValueError):
            self.db.add_transaction("expense", "-2", "Food", "2026-10-01")
        with self.assertRaises(ValueError):
            self.db.add_transaction("expense", "3", "Food", "not-a-date")

    def test_summary_exact_cents(self):
        self.seed()
        summary = self.db.summary()
        self.assertEqual(summary["income"], "1000.00")
        self.assertEqual(summary["expenses"], "40.00")
        self.assertEqual(summary["balance"], "960.00")
        self.assertEqual(summary["expenses_by_category"]["Food"], "20.00")

    def test_date_and_category_filter(self):
        self.seed()
        rows = self.db.list_transactions("2026-10-02", "2026-10-03", "food")
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row["category"] == "Food" for row in rows))

    def test_reject_reversed_date_range(self):
        with self.assertRaises(ValueError):
            self.db.list_transactions("2026-10-05", "2026-10-01")

    def test_csv_export(self):
        self.seed()
        path = Path(self.temp.name) / "export.csv"
        count = self.db.export_csv(path)
        self.assertEqual(count, 4)
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 4)
        self.assertIn("amount", rows[0])


if __name__ == "__main__":
    unittest.main()
