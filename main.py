"""Interactive CLI for the SQLite Expense Tracker."""
from datetime import date
from database import ExpenseDatabase, CATEGORIES


def show_transactions(rows):
    if not rows:
        print("\nNo transactions found.")
        return
    print("\n{:<5} {:<10} {:>12} {:<14} {:<12} {}".format(
        "ID", "Type", "Amount", "Category", "Date", "Description"))
    print("-" * 83)
    for t in rows:
        print("{:<5} {:<10} {:>12} {:<14} {:<12} {}".format(
            t["id"], t["kind"], t["amount"], t["category"][:14],
            t["txn_date"], t["description"][:25]))


def read_filters():
    start = input("Start date YYYY-MM-DD (blank for none): ").strip() or None
    end = input("End date YYYY-MM-DD (blank for none): ").strip() or None
    category = input("Category (blank for all): ").strip() or None
    return start, end, category


def main():
    db = ExpenseDatabase()
    while True:
        print("\n=== CodeNova Expense Tracker ===")
        print("1. Add income/expense")
        print("2. View all transactions")
        print("3. Filter transactions")
        print("4. Show financial summary")
        print("5. Export transactions to CSV")
        print("0. Exit")
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                kind = input("Type (income/expense): ").strip().lower()
                amount = input("Amount (e.g. 250.50): ").strip()
                print("Suggested categories:", ", ".join(CATEGORIES))
                category = input("Category: ").strip()
                txn_date = input(f"Date YYYY-MM-DD [today {date.today().isoformat()}]: ").strip()
                txn_date = txn_date or date.today().isoformat()
                description = input("Description (optional): ").strip()
                item = db.add_transaction(kind, amount, category, txn_date, description)
                print(f"Saved transaction ID {item['id']}.")
            elif choice == "2":
                show_transactions(db.list_transactions())
            elif choice == "3":
                show_transactions(db.list_transactions(*read_filters()))
            elif choice == "4":
                summary = db.summary(*read_filters())
                print("\nTransactions:", summary["count"])
                print("Total income:   ", summary["income"])
                print("Total expenses: ", summary["expenses"])
                print("Net balance:    ", summary["balance"])
                print("Expenses by category:")
                if not summary["expenses_by_category"]:
                    print("  No expenses in this selection.")
                for category, amount in summary["expenses_by_category"].items():
                    print(f"  {category}: {amount}")
            elif choice == "5":
                start, end, category = read_filters()
                filename = input("CSV filename [transactions_export.csv]: ").strip()
                filename = filename or "transactions_export.csv"
                count = db.export_csv(filename, start, end, category)
                print(f"Exported {count} transaction(s) to {filename}.")
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Choose one of the listed options.")
        except (ValueError, OSError) as exc:
            print(f"Input/export error: {exc}")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
