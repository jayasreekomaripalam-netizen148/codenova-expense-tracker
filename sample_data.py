"""Insert sample income and expense records for screenshots and demonstrations."""
from database import ExpenseDatabase

SAMPLE_TRANSACTIONS = [
    ("income", "15000.00", "Salary", "2026-10-01", "Monthly stipend"),
    ("expense", "1250.50", "Food", "2026-10-02", "Groceries"),
    ("expense", "799.00", "Utilities", "2026-10-03", "Internet and phone"),
    ("expense", "450.00", "Travel", "2026-10-04", "Bus fare"),
    ("expense", "1200.00", "Education", "2026-10-05", "Books"),
    ("income", "2500.00", "Other", "2026-10-06", "Freelance work"),
]


def main():
    db = ExpenseDatabase()
    for transaction in SAMPLE_TRANSACTIONS:
        item = db.add_transaction(*transaction)
        print(f"Added transaction ID {item['id']}: {item['kind']} {item['amount']} ({item['category']})")


if __name__ == "__main__":
    main()
