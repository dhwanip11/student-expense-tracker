import json
import matplotlib.pyplot as plt
from datetime import datetime

expenses = []

# Load existing data
try:
    with open("expenses.json", "r") as file:
        expenses = json.load(file)
except FileNotFoundError:
    expenses = []

while True:
    print("\n--- Expense Tracker ---")
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Delete Expense")
    print("4. Filter by Month")
    print("5. Show Graph")
    print("6. Exit")

    choice = input("Enter your choice: ")

    # ADD EXPENSE
    if choice == "1":
        name = input("Enter expense name: ")

        while True:
            try:
                amount = float(input("Enter amount: "))
                break
            except ValueError:
                print("Please enter a valid number!")

        category = input("Enter category (Food/Travel/Rent/etc): ")

        # Auto date (better than manual)
        date = datetime.today().strftime("%Y-%m-%d")

        expenses.append({
            "name": name,
            "amount": amount,
            "category": category,
            "date": date
        })

        with open("expenses.json", "w") as file:
            json.dump(expenses, file, indent=4)

        print(f"Expense added with date: {date}")

    # VIEW EXPENSES
    elif choice == "2":
        if not expenses:
            print("\nNo expenses added yet.")
            continue

        total = 0
        category_total = {}

        print("\n--- Your Expenses ---")

        for i, expense in enumerate(expenses):
            print(f"{i}. {expense['name']} ({expense['category']}) - €{expense['amount']:.2f} | Date: {expense.get('date', 'N/A')}")
            total += expense["amount"]

            cat = expense["category"]
            category_total[cat] = category_total.get(cat, 0) + expense["amount"]

        print(f"\nTotal: €{total:.2f}")

        print("\nCategory-wise spending:")
        for cat, amt in category_total.items():
            print(f"{cat}: €{amt:.2f}")

    # DELETE EXPENSE
    elif choice == "3":
        if not expenses:
            print("\nNo expenses to delete.")
            continue

        print("\nSelect expense number to delete:")

        for i, expense in enumerate(expenses):
            print(f"{i}. {expense['name']} ({expense['category']}) - €{expense['amount']:.2f} | Date: {expense.get('date', 'N/A')}")

        try:
            index = int(input("Enter index: "))
            deleted = expenses.pop(index)

            with open("expenses.json", "w") as file:
                json.dump(expenses, file, indent=4)

            print(f"Deleted: {deleted['name']}")

        except (ValueError, IndexError):
            print("Invalid index!")

    # FILTER BY MONTH
    elif choice == "4":
        month = input("Enter month (YYYY-MM): ")

        found = False
        total = 0

        print(f"\n--- Expenses for {month} ---")

        for expense in expenses:
            date = expense.get("date", "")
            if date.startswith(month):
                print(f"{expense['name']} ({expense['category']}) - €{expense['amount']:.2f} | Date: {date}")
                total += expense["amount"]
                found = True

        if not found:
            print("No expenses found for this month.")
        else:
            print(f"\nTotal for {month}: €{total:.2f}")

    

        # SHOW GRAPH
    elif choice == "5":
        if not expenses:
            print("\nNo expenses to show.")
            continue

        category_total = {}

        for expense in expenses:
            cat = expense["category"]
            category_total[cat] = category_total.get(cat, 0) + expense["amount"]

        labels = list(category_total.keys())
        values = list(category_total.values())

        plt.figure()
        plt.pie(values, labels=labels, autopct="%1.1f%%")
        plt.title("Category-wise Expense Distribution")

        plt.show()

    # EXIT
    elif choice == "6":
        print("Goodbye!")
        break

    else:
        print("Invalid choice")