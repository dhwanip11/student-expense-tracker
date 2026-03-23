from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import json
import os
from datetime import datetime

app = FastAPI()

FILE = "expenses.json"

# ---------- DATA ----------
def load_expenses():
    try:
        if not os.path.exists(FILE):
            return []
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_expenses(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------- MAIN ----------
@app.get("/", response_class=HTMLResponse)
def home(view: str = "expenses", month: str = ""):

    expenses = load_expenses()

    if month:
        expenses = [e for e in expenses if e["date"].startswith(month)]

    total = sum(e["amount"] for e in expenses)
    count = len(expenses)

    categories = {}
    dates = {}

    for e in expenses:
        categories[e["category"]] = categories.get(e["category"], 0) + e["amount"]
        dates[e["date"]] = dates.get(e["date"], 0) + e["amount"]

    sorted_dates = sorted(dates.items())
    date_labels = json.dumps([d[0] for d in sorted_dates])
    date_values = json.dumps([d[1] for d in sorted_dates])

    top_category = max(categories, key=categories.get) if categories else "N/A"

    cat_labels = json.dumps(list(categories.keys()))
    cat_values = json.dumps(list(categories.values()))

    expense_html = ""
    for i, e in enumerate(expenses):
        expense_html += f"""
        <div class="flex justify-between items-center bg-slate-800 p-4 rounded-xl">
            <div>
                <p class="font-semibold">{e['name']}</p>
                <p class="text-xs text-gray-400">{e['category']} • {e['date']}</p>
            </div>
            <div class="text-right">
                <p class="text-green-400 font-bold">€{round(e['amount'], 2)}</p>
                <form method="post" action="/delete">
                    <input type="hidden" name="index" value="{i}">
                    <button class="text-red-400 text-xs">Delete</button>
                </form>
            </div>
        </div>
        """

    if not expense_html:
        expense_html = "<p>No expenses yet</p>"

    return f"""
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>

    <body class="bg-slate-900 text-white flex">

        <div class="w-64 bg-black p-6 min-h-screen">
            <h1 class="text-2xl font-bold mb-6">Expense Tracker</h1>
            <a href="/?view=expenses" class="block mb-3">Expenses</a>
            <a href="/?view=analytics" class="block mb-3">Analytics</a>
            <p class="mt-6">Total: €{round(total,2)}</p>
        </div>

        <div class="flex-1 p-8">

            <h2 class="text-2xl mb-4">Dashboard</h2>

            {" " if view != "expenses" else f"""
            <div class="grid grid-cols-2 gap-6">

                <form method="post" action="/add" class="space-y-4">
                    <input name="name" placeholder="Name" class="w-full p-2 bg-gray-700">
                    <input name="amount" type="number" placeholder="Amount" class="w-full p-2 bg-gray-700">
                    <input name="category" placeholder="Category" class="w-full p-2 bg-gray-700">
                    <button class="bg-green-500 px-4 py-2">Add</button>
                </form>

                <div class="space-y-3">
                    {expense_html}
                </div>

            </div>
            """}

            {" " if view != "analytics" else f"""
            <div class="grid grid-cols-2 gap-6">

                <canvas id="pieChart"></canvas>
                <canvas id="lineChart"></canvas>

            </div>

            <script>
            new Chart(document.getElementById('pieChart'), {{
                type: 'doughnut',
                data: {{
                    labels: {cat_labels},
                    datasets: [{{
                        data: {cat_values}
                    }}]
                }}
            }});

            new Chart(document.getElementById('lineChart'), {{
                type: 'line',
                data: {{
                    labels: {date_labels},
                    datasets: [{{
                        data: {date_values}
                    }}]
                }}
            }});
            </script>
            """}

        </div>
    </body>
    </html>
    """


# ---------- ADD ----------
@app.post("/add")
def add(name: str = Form(...), amount: float = Form(...), category: str = Form(...)):
    expenses = load_expenses()
    expenses.append({
        "name": name,
        "amount": amount,
        "category": category,
        "date": datetime.today().strftime("%Y-%m-%d")
    })
    save_expenses(expenses)
    return RedirectResponse("/", status_code=303)


# ---------- DELETE ----------
@app.post("/delete")
def delete(index: int = Form(...)):
    expenses = load_expenses()
    if 0 <= index < len(expenses):
        expenses.pop(index)
    save_expenses(expenses)
    return RedirectResponse("/", status_code=303)