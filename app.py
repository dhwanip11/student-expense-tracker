from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import json
from datetime import datetime

app = FastAPI()


# ---------- DATA ----------
def load_expenses():
    try:
        with open("expenses.json", "r") as f:
            return json.load(f)
    except:
        return []


def save_expenses(data):
    import os

FILE = "expenses.json"

def load_expenses():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r") as f:
        return json.load(f)

def save_expenses(data):
    with open(FILE, "w") as f:
        json.dump(data, f)
        json.dump(data, f, indent=4)


# ---------- MAIN ----------
@app.get("/", response_class=HTMLResponse)
def home(view: str = "expenses", month: str = ""):

    expenses = load_expenses()

    # Filter by month
    if month:
        expenses = [e for e in expenses if e["date"].startswith(month)]

    total = sum(e["amount"] for e in expenses)
    count = len(expenses)

    categories = {}
    dates = {}

    for e in expenses:
        categories[e["category"]] = categories.get(e["category"], 0) + e["amount"]
        dates[e["date"]] = dates.get(e["date"], 0) + e["amount"]

    # Sort dates for clean graph
    sorted_dates = sorted(dates.items())
    date_labels = json.dumps([d[0] for d in sorted_dates])
    date_values = json.dumps([d[1] for d in sorted_dates])

    top_category = max(categories, key=categories.get) if categories else "N/A"

    cat_labels = json.dumps(list(categories.keys()))
    cat_values = json.dumps(list(categories.values()))

    # Expense list
    expense_html = ""
    for i, e in enumerate(expenses):
        expense_html += f"""
        <div class="flex justify-between items-center bg-slate-800 p-4 rounded-xl hover:scale-[1.02] transition duration-200">
            <div>
                <p class="font-semibold text-lg">{e['name']}</p>
                <p class="text-xs text-gray-400">{e['category']} • {e['date']}</p>
            </div>
            <div class="text-right">
                <p class="text-green-400 font-bold">€{round(e['amount'], 2)}</p>
                <form method="post" action="/delete">
                    <input type="hidden" name="index" value="{i}">
                    <button class="text-red-400 text-xs hover:text-red-300">Delete</button>
                </form>
            </div>
        </div>
        """

    if not expense_html:
        expense_html = """
        <div class="text-center py-10">
            <p class="text-xl text-gray-300">No expenses yet</p>
            <p class="text-sm text-gray-500">Start tracking to unlock insights 📊</p>
        </div>
        """

    return f"""
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>

    <body class="bg-gradient-to-br from-slate-900 via-slate-800 to-black text-white flex">

        <!-- SIDEBAR -->
        <div class="w-64 bg-black/40 backdrop-blur-xl p-6 min-h-screen border-r border-gray-800">

            <div class="mb-10">
                <h1 class="text-3xl font-extrabold bg-gradient-to-r from-green-400 to-blue-500 text-transparent bg-clip-text">
                    Expense Tracker
                </h1>
                <p class="text-xs text-gray-400 mt-1 tracking-widest">
                    SMART FINANCE DASHBOARD
                </p>
            </div>

            <a href="/?view=expenses"
            class="block mb-3 px-4 py-2 rounded-lg {'bg-green-500/20' if view=='expenses' else 'hover:bg-green-500/20'}">
            📋 Expenses</a>

            <a href="/?view=analytics"
            class="block mb-3 px-4 py-2 rounded-lg {'bg-blue-500/20' if view=='analytics' else 'hover:bg-blue-500/20'}">
            📊 Analytics</a>

            <div class="mt-10 text-gray-400 text-sm">
                Total<br>
                <span class="text-white text-xl font-bold">€{round(total,2)}</span>
            </div>

        </div>

        <!-- MAIN -->
        <div class="flex-1 p-10">

            <!-- HEADER -->
            <div class="flex justify-between items-center mb-8">
                <div>
                    <h2 class="text-3xl font-bold">Dashboard</h2>
                    <p class="text-gray-400">Track your spending smartly</p>
                </div>

                <form method="get">
                    <input type="month" name="month"
                    class="bg-slate-800 p-2 rounded border border-gray-600">
                    <button class="ml-2 px-4 py-2 bg-blue-500 rounded hover:bg-blue-400">Filter</button>
                </form>
            </div>

            <!-- KPI -->
            <div class="grid grid-cols-3 gap-6 mb-6">
                <div class="bg-slate-800 p-5 rounded-xl">
                    <p class="text-gray-400">Total</p>
                    <h3 class="text-xl text-green-400 font-bold">€{round(total,2)}</h3>
                </div>
                <div class="bg-slate-800 p-5 rounded-xl">
                    <p class="text-gray-400">Transactions</p>
                    <h3 class="text-xl font-bold">{count}</h3>
                </div>
                <div class="bg-slate-800 p-5 rounded-xl">
                    <p class="text-gray-400">Top Category</p>
                    <h3 class="text-xl font-bold">{top_category}</h3>
                </div>
            </div>

            <!-- INSIGHT -->
            <div class="mb-8 text-sm text-gray-400">
                You spent most on <span class="text-white font-semibold">{top_category}</span>
                with total spending of <span class="text-green-400">€{round(total,2)}</span>
            </div>

            {" " if view != "expenses" else f"""

            <div class="grid grid-cols-2 gap-8">

                <!-- ADD -->
                <div class="bg-slate-800 p-6 rounded-xl">
                    <h3 class="text-xl mb-4">Add Expense</h3>

                    <form method="post" action="/add" class="space-y-4">

                        <input name="name" placeholder="Name"
                        class="w-full p-3 rounded bg-slate-700 focus:ring-2 focus:ring-green-400" required>

                        <input name="amount" type="number" placeholder="Amount"
                        class="w-full p-3 rounded bg-slate-700 focus:ring-2 focus:ring-green-400" required>

                        <input name="category" placeholder="Category"
                        class="w-full p-3 rounded bg-slate-700 focus:ring-2 focus:ring-green-400" required>

                        <button class="w-full py-3 bg-green-500 rounded hover:bg-green-400 transition">
                            Add Expense
                        </button>

                    </form>
                </div>

                <!-- LIST -->
                <div class="space-y-4 max-h-[500px] overflow-y-auto">
                    {expense_html}
                </div>

            </div>
            """}

            {" " if view != "analytics" else f"""

            <div class="grid grid-cols-2 gap-8">

                <div class="bg-slate-800 p-6 rounded-xl">
                    <h3 class="mb-4">Category Breakdown</h3>
                    <canvas id="pieChart"></canvas>
                </div>

                <div class="bg-slate-800 p-6 rounded-xl">
                    <h3 class="mb-4">Spending Trend</h3>
                    <canvas id="lineChart"></canvas>
                </div>

            </div>

            <script>
            new Chart(document.getElementById('pieChart'), {{
                type: 'doughnut',
                data: {{
                    labels: {cat_labels},
                    datasets: [{{
                        data: {cat_values},
                        backgroundColor: ['#22c55e','#3b82f6','#f59e0b','#ef4444','#a855f7']
                    }}]
                }}
            }});

            new Chart(document.getElementById('lineChart'), {{
                type: 'line',
                data: {{
                    labels: {date_labels},
                    datasets: [{{
                        data: {date_values},
                        borderColor: '#22c55e',
                        tension: 0.4,
                        fill: true,
                        backgroundColor: 'rgba(34,197,94,0.2)'
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