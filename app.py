from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from starlette.middleware.sessions import SessionMiddleware

import json
import os
from datetime import datetime
import uuid
import csv
from io import StringIO
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")
app.mount("/static", StaticFiles(directory="static"), name="static")

USERS_FILE = "users.json"

# ---------- LOCALIZATION ----------
TRANSLATIONS = {
    "en": {
        "welcome_back": "Welcome back 👋",
        "create_account": "Create your account 🚀",
        "username": "Username",
        "password": "Password",
        "login": "Login",
        "signup": "Sign Up",
        "dont_have_account": "Don't have an account?",
        "create_one": "Create one",
        "already_have_account": "Already have an account?",
        "invalid_credentials": "Invalid username or password ❌",
        "account_created": "Account created successfully 🎉",
        "user_exists": "User already exists ⚠️",
        "logout": "Logout",
        "dashboard": "Dashboard",
        "track_spending": "Track your spending smartly",
        "expenses": "Expenses",
        "analytics": "Analytics",
        "total": "Total",
        "smart_finance": "SMART FINANCE DASHBOARD",
        "set_budget": "Set Monthly Budget",
        "enter_budget": "Enter budget",
        "set": "Set",
        "add_expense": "Add Expense",
        "recent_expenses": "Recent Expenses",
        "budget": "Budget",
        "remaining": "Remaining",
        "transactions": "Transactions",
        "top_category": "Top Category",
        "name": "Name",
        "amount": "Amount",
        "category": "Category",
        "note": "Note (optional)",
        "edit": "Edit",
        "delete": "Delete",
        "save": "Save",
        "recent": "Recent",
        "low_high": "Low → High",
        "high_low": "High → Low",
        "apply": "Apply",
        "export_csv": "Export CSV",
        "no_expenses": "No expenses yet",
        "no_expenses_msg": "Start adding expenses to see insights 📊",
        "insights": "Insights",
        "budget_updated": "Budget updated successfully",
        "expense_added": "Expense added successfully",
        "expense_updated": "Expense updated successfully",
        "expense_deleted": "Expense deleted successfully",
        "profile": "Profile",
        "settings": "Settings",
        "theme": "Theme",
        "language": "Language",
        "light": "Light",
        "dark": "Dark",
        "built_with": "Built with ❤️ | Expense Tracker"
    },
    "de": {
        "welcome_back": "Willkommen zurück 👋",
        "create_account": "Erstelle dein Konto 🚀",
        "username": "Benutzername",
        "password": "Passwort",
        "login": "Anmelden",
        "signup": "Registrieren",
        "dont_have_account": "Hast du kein Konto?",
        "create_one": "Erstelle eines",
        "already_have_account": "Hast du bereits ein Konto?",
        "invalid_credentials": "Ungültiger Benutzername oder Passwort ❌",
        "account_created": "Konto erfolgreich erstellt 🎉",
        "user_exists": "Benutzer existiert bereits ⚠️",
        "logout": "Abmelden",
        "dashboard": "Dashboard",
        "track_spending": "Verwalte deine Ausgaben intelligent",
        "expenses": "Ausgaben",
        "analytics": "Analyse",
        "total": "Gesamt",
        "smart_finance": "INTELLIGENTES FINANZ-DASHBOARD",
        "set_budget": "Monatsbudget festlegen",
        "enter_budget": "Budget eingeben",
        "set": "Festlegen",
        "add_expense": "Ausgabe hinzufügen",
        "recent_expenses": "Letzte Ausgaben",
        "budget": "Budget",
        "remaining": "Verbleibend",
        "transactions": "Transaktionen",
        "top_category": "Top Kategorie",
        "name": "Name",
        "amount": "Betrag",
        "category": "Kategorie",
        "note": "Notiz (optional)",
        "edit": "Bearbeiten",
        "delete": "Löschen",
        "save": "Speichern",
        "recent": "Aktuell",
        "low_high": "Niedrig → Hoch",
        "high_low": "Hoch → Niedrig",
        "apply": "Anwenden",
        "export_csv": "CSV exportieren",
        "no_expenses": "Noch keine Ausgaben",
        "no_expenses_msg": "Füge Ausgaben hinzu, um Einblicke zu erhalten 📊",
        "insights": "Einblicke",
        "budget_updated": "Budget erfolgreich aktualisiert",
        "expense_added": "Ausgabe erfolgreich hinzugefügt",
        "expense_updated": "Ausgabe erfolgreich aktualisiert",
        "expense_deleted": "Ausgabe erfolgreich gelöscht",
        "profile": "Profil",
        "settings": "Einstellungen",
        "theme": "Thema",
        "language": "Sprache",
        "light": "Hell",
        "dark": "Dunkel",
        "built_with": "Erstellt mit ❤️ | Expense Tracker"
    }
}

def get_translation(lang, key):
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


# ---------- EXCHANGE RATES ----------
# Based on 1 EUR = X currency
EXCHANGE_RATES = {
    "EUR": 1.0,
    "USD": 1.10,      # 1 EUR ≈ 1.10 USD
    "GBP": 0.86,      # 1 EUR ≈ 0.86 GBP
    "INR": 90.0,      # 1 EUR ≈ 90 INR
    "JPY": 130.0      # 1 EUR ≈ 130 JPY
}

def convert_currency(amount, from_currency, to_currency):
    """Convert amount from one currency to another"""
    if from_currency == to_currency:
        return amount
    # Convert to EUR first, then to target currency
    eur_amount = amount / EXCHANGE_RATES.get(from_currency, 1.0)
    return eur_amount * EXCHANGE_RATES.get(to_currency, 1.0)


# ---------- USER STORAGE ----------
def load_users():
    try:
        if not os.path.exists(USERS_FILE):
            return {}
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------- LOGIN ----------
@app.get("/login", response_class=HTMLResponse)
def login_page():
    return """
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
</head>

<body class="relative min-h-screen flex items-center justify-center text-white overflow-hidden">

    <!-- BACKGROUND IMAGE -->
    <div class="absolute inset-0">
        <img src="/static/bg.jpeg"
        class="w-full h-full object-cover opacity-70 blur-[2px]" />
    </div>

    <!-- OVERLAY -->
    <div class="absolute inset-0 bg-slate-900/60"></div>

    <!-- LOGIN CARD -->
    <div class="relative z-10 bg-slate-900/80 backdrop-blur-xl p-10 rounded-2xl w-96 shadow-2xl border border-gray-700">

        <h1 class="text-3xl font-extrabold text-center mb-2
        bg-gradient-to-r from-green-400 to-blue-500 text-transparent bg-clip-text">
            Expense Tracker
        </h1>

        <p class="text-center text-gray-400 mb-6">Welcome back 👋</p>

        <form method="post" action="/login" class="space-y-4">

            <input name="username" placeholder="Username"
            class="w-full p-3 rounded-lg bg-slate-800 border border-gray-600 focus:ring-2 focus:ring-green-400 outline-none">

            <input name="password" type="password" placeholder="Password"
            class="w-full p-3 rounded-lg bg-slate-800 border border-gray-600 focus:ring-2 focus:ring-green-400 outline-none">

            <button class="w-full py-3 rounded-lg font-semibold
            bg-green-500 hover:bg-green-400 transition transform hover:scale-[1.02]">
                Login
            </button>

        </form>

        <p class="text-sm text-gray-400 text-center mt-4">
            Don't have an account?
            <a href="/signup" class="text-blue-400 hover:underline">Create one</a>
        </p>

    </div>

    <!-- TOAST -->
    <div id="toast" class="fixed top-5 right-5 hidden px-4 py-3 rounded-lg shadow-lg text-white"></div>

    <script>
window.onload = function() {

    function showToast(message, type="success") {
        const toast = document.getElementById("toast");
        toast.innerText = message;

        toast.className = "fixed top-5 right-5 px-4 py-3 rounded-lg shadow-lg text-white";

        if (type === "success") {
            toast.classList.add("bg-green-500");
        } else {
            toast.classList.add("bg-red-500");
        }

        toast.classList.remove("hidden");

        setTimeout(() => {
            toast.classList.add("hidden");
        }, 3000);
    }

    const params = new URLSearchParams(window.location.search);

    if (params.get("error")) {
        showToast("Invalid username or password ❌", "error");
    }

    if (params.get("success")) {
        showToast("Account created successfully 🎉", "success");
    }

};
</script>

</body>
</html>
"""


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    users = load_users()
    if username in users:
        stored_password = users[username]["password"]
        # Check if it's a bcrypt hash (starts with $2a$, $2b$, or $2y$)
        if stored_password.startswith(('$2a$', '$2b$', '$2y$', '$pbkdf2-sha256$')):
            if pwd_context.verify(password, stored_password):
                request.session["user"] = username
                return RedirectResponse("/", status_code=303)
        else:
            # Fallback for plain text passwords - convert to hash on next login
            if password == stored_password:
                users[username]["password"] = pwd_context.hash(password)
                save_users(users)
                request.session["user"] = username
                return RedirectResponse("/", status_code=303)
    return RedirectResponse("/login?error=1", status_code=303)


# ---------- SIGNUP ----------
@app.get("/signup", response_class=HTMLResponse)
def signup_page():
    return """
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
</head>

<body class="relative min-h-screen flex items-center justify-center text-white overflow-hidden">

    <!-- BACKGROUND IMAGE -->
    <div class="absolute inset-0">
        <img src="/static/bg.jpeg"
        class="w-full h-full object-cover opacity-70 blur-[2px]" />
    </div>

    <!-- OVERLAY -->
    <div class="absolute inset-0 bg-slate-900/60"></div>

    <!-- CARD -->
    <div class="relative z-10 bg-slate-900/80 backdrop-blur-xl p-10 rounded-2xl w-96 shadow-2xl border border-gray-700">

        <h1 class="text-3xl font-extrabold text-center mb-2
        bg-gradient-to-r from-green-400 to-blue-500 text-transparent bg-clip-text">
            Expense Tracker
        </h1>

        <p class="text-center text-gray-400 mb-6">Create your account 🚀</p>

        <form method="post" action="/signup" class="space-y-4">

            <input name="username" placeholder="Username"
            class="w-full p-3 rounded-lg bg-slate-800 border border-gray-600 focus:ring-2 focus:ring-green-400 outline-none">

            <input name="password" type="password" placeholder="Password"
            class="w-full p-3 rounded-lg bg-slate-800 border border-gray-600 focus:ring-2 focus:ring-green-400 outline-none">

            <button class="w-full py-3 rounded-lg font-semibold
            bg-green-500 hover:bg-green-400 transition transform hover:scale-[1.02]">
                Sign Up
            </button>

        </form>

        <p class="text-sm text-gray-400 text-center mt-4">
            Already have an account?
            <a href="/login" class="text-blue-400 hover:underline">Login</a>
        </p>

    </div>

    <!-- TOAST -->
    <div id="toast" class="fixed top-5 right-5 hidden px-4 py-3 rounded-lg shadow-lg text-white"></div>

    <script>
    window.onload = function() {

        function showToast(message, type="error") {
            const toast = document.getElementById("toast");
            toast.innerText = message;

            toast.className = "fixed top-5 right-5 px-4 py-3 rounded-lg shadow-lg text-white";

            if (type === "error") {
                toast.classList.add("bg-red-500");
            }

            toast.classList.remove("hidden");

            setTimeout(() => {
                toast.classList.add("hidden");
            }, 3000);
        }

        const params = new URLSearchParams(window.location.search);

        if (params.get("error")) {
            showToast("User already exists ⚠️");
        }

    };
    </script>

</body>
</html>
"""


@app.post("/signup")
def signup(username: str = Form(...), password: str = Form(...)):
    users = load_users()

    if username in users:
        # ✅ THIS WAS WRONG BEFORE
        return RedirectResponse("/signup?error=1", status_code=303)

    hashed_password = pwd_context.hash(password)
    users[username] = {
        "password": hashed_password,
        "expenses": [],
        "budget": 0,
        "theme": "dark",
        "language": "en",
        "currency": "EUR"
    }

    save_users(users)

    return RedirectResponse("/login?success=1", status_code=303)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


# ---------- PREFERENCES ----------
@app.post("/set-theme")
def set_theme(request: Request, theme: str = Form(...)):
    users = load_users()
    user = request.session.get("user")

    if not user:
        return RedirectResponse("/login", status_code=303)

    if "theme" not in users[user]:
        users[user]["theme"] = "dark"
    
    users[user]["theme"] = theme
    save_users(users)
    return RedirectResponse("/?view=expenses", status_code=303)


@app.post("/set-currency")
def set_currency(request: Request, currency: str = Form(...)):
    users = load_users()
    user = request.session.get("user")

    if not user:
        return RedirectResponse("/login", status_code=303)

    if "currency" not in users[user]:
        users[user]["currency"] = "EUR"
    
    users[user]["currency"] = currency
    save_users(users)
    return RedirectResponse("/?view=expenses", status_code=303)


# ---------- COLORS ----------
def generate_colors(n):
    colors = []
    for i in range(n):
        hue = int((360 / max(n, 1)) * i)
        colors.append(f"hsl({hue}, 70%, 60%)")
    return colors


# ---------- MAIN ----------
@app.get("/", response_class=HTMLResponse)
def home(request: Request, view: str = "expenses", month: str = "", sort: str = "recent", edit_id: str = "", msg: str = ""):

    users = load_users()
    user = request.session.get("user")

    if not user or user not in users:
        return RedirectResponse("/login")

    if "expenses" not in users[user]:
        users[user]["expenses"] = []
    
    # Get user preferences
    theme = users[user].get("theme", "dark")
    language = users[user].get("language", "en")
    currency = users[user].get("currency", "EUR")
    
    # Currency symbols
    currency_symbols = {"EUR": "€", "USD": "$", "GBP": "£", "INR": "₹", "JPY": "¥"}
    currency_symbol = currency_symbols.get(currency, "€")
    
    # Helper function for translations
    def t(key):
        return get_translation(language, key)

    expenses = users[user]["expenses"]

    if sort == "low":
        expenses = sorted(expenses, key=lambda x: x["amount"])
    elif sort == "high":
        expenses = sorted(expenses, key=lambda x: x["amount"], reverse=True)
    else:
        expenses = sorted(expenses, key=lambda x: x["date"], reverse=True)

    if month:
        expenses = [e for e in expenses if e["date"].startswith(month)]

    # Calculate total with currency conversion
    total = 0
    for e in expenses:
        original_currency = e.get("original_currency", "EUR")
        display_amount = convert_currency(e["amount"], original_currency, currency)
        total += display_amount
    
    budget = users[user].get("budget", 0)
    remaining = budget - total
    usage_percent = int((total / budget) * 100) if budget > 0 else 0
    usage_percent = min(usage_percent, 100)
    count = len(expenses)

    categories = {}
    dates = {}

    for e in expenses:
        # Convert amount to current currency if it was stored in a different currency
        original_currency = e.get("original_currency", "EUR")
        display_amount = convert_currency(e["amount"], original_currency, currency)
        
        categories[e["category"]] = categories.get(e["category"], 0) + display_amount
        dates[e["date"]] = dates.get(e["date"], 0) + display_amount

    sorted_dates = sorted(dates.items())
    date_labels = json.dumps([d[0] for d in sorted_dates])
    date_values = json.dumps([d[1] for d in sorted_dates])

    top_category = max(categories, key=categories.get) if categories else "N/A"
    top_percent = 0
    if categories and total > 0:
        top_percent = round((categories[top_category] / total) * 100)

    if expenses:
        highest_converted = convert_currency(max(expenses, key=lambda x: x["amount"])["amount"], 
                                            max(expenses, key=lambda x: x["amount"]).get("original_currency", "EUR"), 
                                            currency)
        avg = round(total / count, 2)
        insight = f"Top spending: {top_category} ({top_percent}%) | Highest: {currency_symbol}{highest_converted} | Avg: {currency_symbol}{avg}"
    else:
        insight = t("no_expenses_msg")

    cat_labels = json.dumps(list(categories.keys()))
    cat_values = json.dumps(list(categories.values()))
    cat_colors = json.dumps(generate_colors(len(categories)))
    
    # Theme colors
    theme_bg = "bg-white" if theme == "light" else "bg-gradient-to-br from-slate-900 via-slate-800 to-black"
    theme_text = "text-slate-900" if theme == "light" else "text-white"
    theme_card = "bg-slate-100 border-gray-300" if theme == "light" else "bg-slate-800 border-gray-800"
    theme_secondary_text = "text-slate-600" if theme == "light" else "text-gray-400"
    theme_sidebar = "bg-slate-200/40 border-gray-300" if theme == "light" else "bg-black/40 border-gray-800"
    theme_input = "bg-slate-200 border-gray-400 text-slate-900" if theme == "light" else "bg-slate-700 border-gray-600 text-white"

    expense_html = ""
    for e in expenses:
        # Convert amount to current currency
        original_currency = e.get("original_currency", "EUR")
        display_amount = convert_currency(e["amount"], original_currency, currency)

        if edit_id == e.get("id"):
            expense_html += f"""
            <div class="flex justify-between items-center {theme_card} p-4 rounded-xl border">
                <form method="post" action="/edit" class="w-full space-y-2">
                    <input type="hidden" name="id" value="{e.get('id','')}">

                    <input name="name" value="{e['name']}" class="w-full p-2 {theme_input} rounded border">
                    <input name="amount" type="number" value="{e['amount']}" class="w-full p-2 {theme_input} rounded border">
                    <input name="category" value="{e['category']}" class="w-full p-2 {theme_input} rounded border">
                    <input name="note" value="{e.get('note','')}" class="w-full p-2 {theme_input} rounded border">

                    <button class="text-green-400 text-xs hover:text-green-300 transition transform hover:scale-[1.02]">{t('save')}</button>
                </form>
            </div>
            """
        else:
            note_html = f"<p class='text-xs {theme_secondary_text} mt-1'>{e.get('note','')}</p>" if e.get("note") else ""

            expense_html += f"""
            <div class="flex justify-between items-center {theme_card} p-4 rounded-xl border hover:scale-[1.02] transition duration-200">
                <div>
                    <p class="font-semibold text-lg {theme_text}">{e['name']}</p>
                    <p class="text-xs {theme_secondary_text}">{e['category']} • {e['date']}</p>
                    {note_html}
                </div>
                <div class="text-right">
                    <p class="text-green-400 font-bold">{currency_symbol}{round(display_amount, 2)}</p>

                    <a href="/?edit_id={e.get('id','')}&view={view}&month={month}&sort={sort}" 
                    class="text-blue-400 text-xs hover:text-blue-300">{t('edit')}</a>

                    <form method="post" action="/delete">
                        <input type="hidden" name="id" value="{e.get('id','')}">
                        <button class="text-red-400 text-xs hover:text-red-300">{t('delete')}</button>
                    </form>
                </div>
            </div>
            """

    if not expense_html:
        expense_html = f"""
        <div class="text-center py-10">
            <p class="text-xl {theme_text}">{t('no_expenses')}</p>
            <p class="text-sm {theme_secondary_text} mt-2">{t('no_expenses_msg')}</p>
        </div>
        """

    return f"""
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            [data-theme="light"] {{ color-scheme: light; }}
            [data-theme="dark"] {{ color-scheme: dark; }}
        </style>
    </head>

    <body class="{theme_text} {theme_bg} flex flex-col md:flex-row" data-theme="{theme}">

        <!-- SIDEBAR -->
        <div class="w-full md:w-64 {theme_sidebar} backdrop-blur-xl md:p-6 p-4 border-b md:border-b-0 md:border-r border-gray-600 flex flex-row md:flex-col" id="sidebar">

            <!-- HEADER -->
            <div class="mb-4 md:mb-10 flex items-center gap-2">
                <div class="flex items-center gap-2 md:gap-3 flex-1">
                    <div class="w-8 h-8 md:w-9 md:h-9 rounded-lg bg-gradient-to-r from-green-400 to-blue-500 flex items-center justify-center text-white font-bold text-sm">
                        💰
                    </div>
                    <div>
                        <h1 class="text-lg md:text-2xl font-extrabold bg-gradient-to-r from-green-400 to-blue-500 text-transparent bg-clip-text leading-tight">
                            Expense Tracker
                        </h1>
                        <p class="text-xs {theme_secondary_text} tracking-widest hidden md:block mt-0.5">
                            {t('smart_finance')}
                        </p>
                    </div>
                </div>
                <button onclick="document.getElementById('mobileMenu').classList.toggle('hidden')" class="md:hidden ml-auto text-white">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
                    </svg>
                </button>
            </div>

            <!-- MOBILE MENU -->
            <div id="mobileMenu" class="hidden md:flex flex-col flex-1 md:block">
                <!-- NAVIGATION -->
                <div class="mt-4 md:mt-0">
                    <a href="/?view=expenses"
                    class="block mb-2 px-3 md:px-4 py-2 rounded-lg text-sm md:text-base {'bg-green-500/20 ' + theme_text if view=='expenses' else 'hover:bg-green-500/20 ' + theme_secondary_text}">
                    📋 {t('expenses')}</a>

                    <a href="/?view=analytics"
                    class="block mb-2 px-3 md:px-4 py-2 rounded-lg text-sm md:text-base {'bg-blue-500/20 ' + theme_text if view=='analytics' else 'hover:bg-blue-500/20 ' + theme_secondary_text}">
                    📊 {t('analytics')}</a>
                </div>

                <!-- TOTAL SECTION -->
                <div class="mt-4 md:mt-6 {theme_secondary_text} text-sm hidden md:block">
                    {t('total')}<br>
                    <span class="{theme_text} text-xl font-bold">{currency_symbol}{round(total,2)}</span>
                </div>

                <!-- BUDGET FORM -->
                <div class="mt-4 md:mt-8 {theme_card} p-3 md:p-4 rounded-lg border hidden md:block">
                    <h3 class="text-xs md:text-sm font-semibold {theme_text} mb-2 md:mb-3">{t('set_budget')}</h3>
                    <form method="post" action="/set-budget" class="flex flex-col gap-2">
                        <input name="amount" type="number" placeholder="{t('enter_budget')}"
                        class="p-2 rounded {theme_input} text-xs md:text-sm w-full border" required>
                        <button type="submit" class="px-3 md:px-4 py-1 md:py-2 bg-blue-500 rounded hover:bg-blue-400 text-xs md:text-sm transition transform hover:scale-[1.02] text-white">{t('set')}</button>
                    </form>
                </div>

                <!-- PROFILE SECTION -->
                <div class="mt-auto md:mt-auto pt-4 md:pt-6 border-t border-gray-600 hidden md:block">
                    <button onclick="document.getElementById('profileDropdown').classList.toggle('hidden')" class="w-full flex items-center gap-3 px-3 md:px-4 py-2 md:py-3 {theme_card} rounded-lg border transition hover:shadow-lg text-left">
                        <div class="w-8 h-8 md:w-9 md:h-9 rounded-full bg-gradient-to-r from-green-400 to-blue-500 flex items-center justify-center text-white text-xs md:text-sm font-bold flex-shrink-0">
                            {user[0].upper()}
                        </div>
                        <div class="flex-1 min-w-0">
                            <p class="text-xs md:text-sm font-semibold {theme_text} truncate">{user}</p>
                            <p class="text-xs {theme_secondary_text}">Account</p>
                        </div>
                        <svg class="w-4 h-4 {theme_secondary_text} flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                    </button>

                    <!-- DROPDOWN MENU -->
                    <div id="profileDropdown" class="hidden mt-2 {theme_card} border rounded-lg shadow-lg overflow-hidden">
                        
                        <!-- THEME SECTION -->
                        <div class="px-3 md:px-4 py-3 border-b border-gray-600">
                            <p class="text-xs font-bold {theme_text} uppercase tracking-wider mb-3">⚙️ Appearance</p>
                            <form method="post" action="/set-theme" class="space-y-2">
                                <label class="flex items-center gap-3 p-2 hover:rounded cursor-pointer transition text-sm">
                                    <input type="radio" name="theme" value="light" {'checked' if theme == 'light' else ''} class="w-4 h-4" onchange="this.form.submit()">
                                    <span class="{theme_text}">☀️ Light</span>
                                </label>
                                <label class="flex items-center gap-3 p-2 hover:rounded cursor-pointer transition text-sm">
                                    <input type="radio" name="theme" value="dark" {'checked' if theme == 'dark' else ''} class="w-4 h-4" onchange="this.form.submit()">
                                    <span class="{theme_text}">🌙 Dark</span>
                                </label>
                            </form>
                        </div>

                        <!-- CURRENCY SECTION -->
                        <div class="px-3 md:px-4 py-3">
                            <p class="text-xs font-bold {theme_text} uppercase tracking-wider mb-3">💱 Currency</p>
                            <form method="post" action="/set-currency" class="space-y-2">
                                <label class="flex items-center gap-3 p-2 hover:rounded cursor-pointer transition text-sm">
                                    <input type="radio" name="currency" value="EUR" {'checked' if currency == 'EUR' else ''} class="w-4 h-4" onchange="this.form.submit()">
                                    <span class="{theme_text}">€ Euro</span>
                                </label>
                                <label class="flex items-center gap-3 p-2 hover:rounded cursor-pointer transition text-sm">
                                    <input type="radio" name="currency" value="USD" {'checked' if currency == 'USD' else ''} class="w-4 h-4" onchange="this.form.submit()">
                                    <span class="{theme_text}">$ Dollar</span>
                                </label>
                                <label class="flex items-center gap-3 p-2 hover:rounded cursor-pointer transition text-sm">
                                    <input type="radio" name="currency" value="GBP" {'checked' if currency == 'GBP' else ''} class="w-4 h-4" onchange="this.form.submit()">
                                    <span class="{theme_text}">£ Pound</span>
                                </label>
                                <label class="flex items-center gap-3 p-2 hover:rounded cursor-pointer transition text-sm">
                                    <input type="radio" name="currency" value="INR" {'checked' if currency == 'INR' else ''} class="w-4 h-4" onchange="this.form.submit()">
                                    <span class="{theme_text}">₹ Rupee</span>
                                </label>
                                <label class="flex items-center gap-3 p-2 hover:rounded cursor-pointer transition text-sm">
                                    <input type="radio" name="currency" value="JPY" {'checked' if currency == 'JPY' else ''} class="w-4 h-4" onchange="this.form.submit()">
                                    <span class="{theme_text}">¥ Yen</span>
                                </label>
                            </form>
                        </div>
                    </div>

                    <!-- LOGOUT BUTTON -->
                    <a href="/logout" class="w-full block mt-3 px-3 md:px-4 py-2 md:py-3 rounded-lg text-white bg-gradient-to-r from-red-500 to-red-600 hover:from-red-400 hover:to-red-500 transition transform hover:scale-[1.02] font-semibold text-xs md:text-sm text-center">
                    🚪 {t('logout')}
                    </a>
                </div>
            </div>
        </div>

        <!-- MOBILE FOOTER PROFILE -->
        <div class="md:hidden w-full {theme_card} border-t border-gray-600 p-3 flex gap-2">
            <button onclick="document.getElementById('mobileProfileDropdown').classList.toggle('hidden')" class="flex-1 flex items-center gap-2 px-3 py-2 {theme_card} rounded border transition hover:shadow text-left">
                <div class="w-8 h-8 rounded-full bg-gradient-to-r from-green-400 to-blue-500 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                    {user[0].upper()}
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-xs font-semibold {theme_text} truncate">{user}</p>
                    <p class="text-xs {theme_secondary_text}">Account</p>
                </div>
            </button>
            <a href="/logout" class="px-4 py-2 rounded bg-red-500 text-white text-sm hover:bg-red-600 transition">🚪</a>
        </div>

        <!-- MOBILE PROFILE DROPDOWN -->
        <div id="mobileProfileDropdown" class="hidden md:hidden w-full {theme_card} border-t border-gray-600 p-3">
            <div class="mb-3 border-b border-gray-600 pb-3">
                <p class="text-xs font-bold {theme_text} uppercase mb-2">⚙️ Theme</p>
                <form method="post" action="/set-theme" class="space-y-2">
                    <label class="flex items-center gap-2 p-2 text-sm">
                        <input type="radio" name="theme" value="light" {'checked' if theme == 'light' else ''} class="w-4 h-4" onchange="this.form.submit()">
                        <span class="{theme_text}">☀️ Light</span>
                    </label>
                    <label class="flex items-center gap-2 p-2 text-sm">
                        <input type="radio" name="theme" value="dark" {'checked' if theme == 'dark' else ''} class="w-4 h-4" onchange="this.form.submit()">
                        <span class="{theme_text}">🌙 Dark</span>
                    </label>
                </form>
            </div>
            <div>
                <p class="text-xs font-bold {theme_text} uppercase mb-2">💱 Currency</p>
                <form method="post" action="/set-currency" class="space-y-2">
                    <label class="flex items-center gap-2 p-2 text-sm">
                        <input type="radio" name="currency" value="EUR" {'checked' if currency == 'EUR' else ''} class="w-4 h-4" onchange="this.form.submit()">
                        <span class="{theme_text}">€ EUR</span>
                    </label>
                    <label class="flex items-center gap-2 p-2 text-sm">
                        <input type="radio" name="currency" value="USD" {'checked' if currency == 'USD' else ''} class="w-4 h-4" onchange="this.form.submit()">
                        <span class="{theme_text}">$ USD</span>
                    </label>
                    <label class="flex items-center gap-2 p-2 text-sm">
                        <input type="radio" name="currency" value="GBP" {'checked' if currency == 'GBP' else ''} class="w-4 h-4" onchange="this.form.submit()">
                        <span class="{theme_text}">£ GBP</span>
                    </label>
                    <label class="flex items-center gap-2 p-2 text-sm">
                        <input type="radio" name="currency" value="INR" {'checked' if currency == 'INR' else ''} class="w-4 h-4" onchange="this.form.submit()">
                        <span class="{theme_text}">₹ INR</span>
                    </label>
                    <label class="flex items-center gap-2 p-2 text-sm">
                        <input type="radio" name="currency" value="JPY" {'checked' if currency == 'JPY' else ''} class="w-4 h-4" onchange="this.form.submit()">
                        <span class="{theme_text}">¥ JPY</span>
                    </label>
                </form>
            </div>
        </div>

        </div>

        <!-- MAIN CONTENT -->
        <div class="flex-1 p-3 md:p-6 overflow-y-auto">
        {f'''
<div class="mb-4 p-3 rounded-lg bg-green-500/20 text-green-300 border border-green-500/30">
    {msg}
</div>
''' if msg else ''}
		

            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 md:gap-0 mb-4">
                <div>
                    <h2 class="text-2xl md:text-3xl font-bold {theme_text}">{t('dashboard')}</h2>
                    <p class="text-xs md:text-base {theme_secondary_text} mt-1">{t('track_spending')}</p>
                </div>

                <form method="get" class="w-full md:w-auto flex flex-wrap gap-2">
                    <input type="month" name="month"
                    class="{theme_card} p-2 rounded border text-xs md:text-base">

                    <select name="sort" class="{theme_card} p-2 rounded border text-xs md:text-base">
                        <option value="recent">{t('recent')}</option>
                        <option value="low">{t('low_high')}</option>
                        <option value="high">{t('high_low')}</option>
                    </select>

                    <button type="submit" class="px-2 md:px-4 py-2 bg-blue-500 rounded hover:bg-blue-400 transition transform hover:scale-[1.02] text-white font-semibold text-xs md:text-base">{t('apply')}</button>

                    <a href="/export" class="px-2 md:px-4 py-2 bg-green-500 rounded hover:bg-green-400 transition transform hover:scale-[1.02] inline-block text-white font-semibold text-xs md:text-base">{t('export_csv')}</a>
                </form>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-6 mb-6">
            <div class="{theme_card} p-4 md:p-5 rounded-xl border">
    <p class="text-xs md:text-base {theme_secondary_text}">{t('budget')}</p>
    <h3 class="text-lg md:text-xl font-bold {theme_text}">{currency_symbol}{budget}</h3>
    <p class="text-xs md:text-sm {f'text-red-400' if remaining < 0 else 'text-green-400'}">
        {t('remaining')}: {currency_symbol}{remaining}
    </p>
    <div class="w-full bg-slate-700 rounded-full h-2 mt-2">
    <div class="h-2 rounded-full 
        {f'bg-green-500' if usage_percent < 80 else 'bg-yellow-400' if usage_percent < 100 else 'bg-red-500'}"
        style="width: {usage_percent}%">
    </div>
</div>
<p class="text-xs {theme_secondary_text} mt-1">{usage_percent}% used</p>
</div>
                <div class="{theme_card} p-4 md:p-5 rounded-xl border">
                    <p class="text-xs md:text-base {theme_secondary_text}">{t('total')}</p>
                    <h3 class="text-lg md:text-xl text-green-400 font-bold">{currency_symbol}{round(total,2)}</h3>
                </div>
                <div class="{theme_card} p-4 md:p-5 rounded-xl border">
                    <p class="text-xs md:text-base {theme_secondary_text}">{t('transactions')}</p>
                    <h3 class="text-lg md:text-xl font-bold {theme_text}">{count}</h3>
                </div>
                <div class="{theme_card} p-4 md:p-5 rounded-xl border">
                    <p class="text-xs md:text-base {theme_secondary_text}">{t('top_category')}</p>
                    <h3 class="text-lg md:text-xl font-bold {theme_text}">{top_category}</h3>
                </div>
            </div>

            {" " if view != "analytics" else f'''
<div class="{theme_card} p-4 rounded-xl mb-8 border">
    <p class="{theme_secondary_text} text-sm">{t('insights')}</p>
    <p class="{theme_text}">{insight}</p>
</div>
'''}

            {" " if view != "expenses" else f'''
<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">

    <!-- ADD EXPENSE FORM -->
    <div class="{theme_card} p-4 md:p-6 rounded-xl h-fit border">
        <h3 class="text-lg md:text-xl mb-4 {theme_text}">{t('add_expense')}</h3>
        <form method="post" action="/add" class="space-y-4">
            <input name="name" placeholder="{t('name')}" class="{theme_input} w-full p-3 rounded border text-sm" required>
            <input name="amount" type="number" placeholder="{t('amount')}" class="{theme_input} w-full p-3 rounded border text-sm" required>
            <input name="category" list="catlist" placeholder="{t('category')}" class="{theme_input} w-full p-3 rounded border text-sm" required>

            <datalist id="catlist">
                <option value="Food">
                <option value="Health">
                <option value="Beauty">
                <option value="Travel">
                <option value="Rent">
                <option value="Other">
            </datalist>

            <input name="note" placeholder="{t('note')}" class="{theme_input} w-full p-3 rounded border text-sm">

            <button type="submit" class="w-full py-3 bg-green-500 rounded hover:bg-green-400 transition transform hover:scale-[1.02] text-white font-semibold text-sm">{t('add_expense')}</button>
        </form>
    </div>

    <!-- EXPENSES LIST -->
    <div class="{theme_card} p-4 md:p-6 rounded-xl h-fit border">
        <h3 class="text-lg md:text-xl mb-4 {theme_text}">{t('recent_expenses')}</h3>
        <div class="space-y-4 max-h-[500px] overflow-y-auto">
            {expense_html}
        </div>
    </div>

</div>
'''}

            {" " if view != "analytics" else f'''
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
                <div class="{theme_card} p-4 md:p-6 rounded-xl h-[300px] md:h-[350px] flex items-center justify-center border shadow-lg">
                    <div class="w-full h-full flex items-center justify-center">
                        <canvas id="pieChart"></canvas>
                    </div>
                </div>

                <div class="{theme_card} p-4 md:p-6 rounded-xl h-[300px] md:h-[350px] flex items-center justify-center border shadow-lg">
                    <canvas id="lineChart" class="w-full"></canvas>
                </div>
            </div>

            <script>
            new Chart(document.getElementById('pieChart'), {{
                type: 'doughnut',
                data: {{
                    labels: {cat_labels},
                    datasets: [{{
                        data: {cat_values},
                        backgroundColor: {cat_colors}
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {{
                        legend: {{
                            labels: {{
                                color: "{'#1e293b' if theme == 'light' else 'white'}",
                                padding: 15,
                                font: {{
                                    size: 12
                                }}
                            }}
                        }}
                    }}
                }}
            }});

            new Chart(document.getElementById('lineChart'), {{
                type: 'line',
                data: {{
                    labels: {date_labels},
                    datasets: [{{
                        data: {date_values},
                        borderColor: '#22c55e',
                        backgroundColor: 'rgba(34, 197, 94, 0.1)',
                        fill: true,
                        tension: 0.4,
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {{
                        legend: {{
                            display: false
                        }}
                    }},
                    scales: {{
                        y: {{
                            ticks: {{
                                color: "{'#475569' if theme == 'light' else '#9CA3AF'}"
                            }},
                            grid: {{
                                color: "{'#E2E8F0' if theme == 'light' else '#374151'}"
                            }}
                        }},
                        x: {{
                            ticks: {{
                                color: "{'#475569' if theme == 'light' else '#9CA3AF'}"
                            }},
                            grid: {{
                                color: "{'#E2E8F0' if theme == 'light' else '#374151'}"
                            }}
                        }}
                    }}
                }}
            }});
            </script>
            '''}

            <div class="text-center text-xs {theme_secondary_text} mt-10">
                {t('built_with')}
            </div>
        </div>

    </body>
    </html>
    """
# ---------- ADD ----------
@app.post("/add")
def add(request: Request, name: str = Form(...), amount: float = Form(...), category: str = Form(...), note: str = Form("")):
    users = load_users()
    user = request.session.get("user")

    if not user:
        return RedirectResponse("/login", status_code=303)

    # Store the original currency with the expense
    original_currency = users[user].get("currency", "EUR")
    
    users[user]["expenses"].append({
        "id": str(uuid.uuid4()),
        "name": name,
        "amount": amount,
        "original_currency": original_currency,
        "category": category,
        "note": note,
        "date": datetime.today().strftime("%Y-%m-%d")
    })

    save_users(users)
    return RedirectResponse("/?msg=Expense added successfully", status_code=303)


# ---------- EDIT ----------
@app.post("/edit")
def edit(request: Request, id: str = Form(...), name: str = Form(...), amount: float = Form(...), category: str = Form(...), note: str = Form("")):
    users = load_users()
    user = request.session.get("user")

    if not user:
        return RedirectResponse("/login", status_code=303)

    for e in users[user]["expenses"]:
        if e["id"] == id:
            e["name"] = name
            e["amount"] = amount
            e["category"] = category
            e["note"] = note
            # Preserve the original currency
            if "original_currency" not in e:
                e["original_currency"] = users[user].get("currency", "EUR")

    save_users(users)
    return RedirectResponse("/?msg=Expense updated successfully", status_code=303)


# ---------- DELETE ----------
@app.post("/delete")
def delete(request: Request, id: str = Form(...)):
    users = load_users()
    user = request.session.get("user")

    if not user:
        return RedirectResponse("/login", status_code=303)

    users[user]["expenses"] = [e for e in users[user]["expenses"] if e["id"] != id]

    save_users(users)
    return RedirectResponse("/?msg=Expense deleted successfully", status_code=303)


# ---------- EXPORT ----------
@app.get("/export")
def export_csv(request: Request):
    users = load_users()
    user = request.session.get("user")

    if not user:
        return RedirectResponse("/login", status_code=303)

    expenses = users[user]["expenses"]
    currency = users[user].get("currency", "EUR")

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["Name", "Amount", "Original Currency", f"Amount in {currency}", "Category", "Note", "Date"])

    for e in expenses:
        original_currency = e.get("original_currency", "EUR")
        converted_amount = convert_currency(e.get("amount", 0), original_currency, currency)
        writer.writerow([
            e.get("name"),
            e.get("amount"),
            original_currency,
            round(converted_amount, 2),
            e.get("category"),
            e.get("note"),
            e.get("date")
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=expenses.csv"}
    )
@app.post("/set-budget")
def set_budget(request: Request, amount: float = Form(...)):
    users = load_users()
    user = request.session.get("user")

    if not user:
        return RedirectResponse("/login", status_code=303)

    users[user]["budget"] = amount
    save_users(users)

    return RedirectResponse("/?msg=Budget updated successfully", status_code=303)