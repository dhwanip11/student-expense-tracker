# 💰 Expense Tracker

> A modern, beautiful, and feature-rich expense tracking web application built with FastAPI, Tailwind CSS, and Chart.js

## 🎯 Overview

**Expense Tracker** is a smart personal finance management tool that helps you track, analyze, and visualize your spending habits. With an intuitive dashboard, powerful analytics, and a gorgeous dark-themed UI, managing your finances has never been easier.

### ✨ Key Features

- 🔐 **Secure Authentication** - User registration and login with password hashing
- 📊 **Real-time Analytics** - Interactive charts showing spending patterns
- 💳 **Budget Management** - Set and monitor your monthly budget
- 📋 **Full CRUD Operations** - Add, edit, and delete expenses
- 🏷️ **Smart Categorization** - Organize expenses by category
- 📅 **Date Filtering** - Filter expenses by month
- 📈 **Sorting Options** - Sort by recent, lowest, or highest amount
- 📥 **CSV Export** - Download your expenses as CSV
- 💾 **Data Persistence** - All data stored locally in JSON files
- 🎨 **Beautiful UI** - Modern dark theme with smooth animations

---

## 📁 Project Structure

```
expense-tracker/
├── app.py                 # Main FastAPI application (core logic & routes)
├── requirements.txt       # Python dependencies
├── users.json            # User database (credentials, expenses, budget)
├── expenses.json         # Sample expense data
├── static/               # Static assets (images)
│   ├── bg.jpeg          # Background image for auth pages
│   ├── bg.png           # Background image variant
└── __pycache__/         # Python cache directory
```

---

## 🏗️ Architecture & How It Works

### **Backend Stack**
- **Framework**: FastAPI (modern Python web framework)
- **Server**: Uvicorn (ASGI server for async operations)
- **Authentication**: Session-based with SessionMiddleware
- **Password Security**: bcrypt hashing (via passlib)
- **Templating**: HTML with embedded Tailwind CSS & JavaScript

### **Frontend Stack**
- **Styling**: Tailwind CSS (utility-first CSS framework)
- **Charts**: Chart.js (for data visualization)
- **DOM Effects**: Backdrop blur, smooth transitions, gradient text

### **Data Storage**
- **Format**: JSON files (no database required)
- **Files**:
  - `users.json` - Stores user credentials and personal data
  - `expenses.json` - Sample data reference file

---

## 📊 Data Models

### **User Object** (stored in `users.json`)
```javascript
{
  "username": {
    "password": "bcrypt_hashed_password",
    "expenses": [
      {
        "id": "uuid",
        "name": "Coffee",
        "amount": 5.50,
        "category": "Food",
        "note": "Morning coffee",
        "date": "2026-03-29"
      }
    ],
    "budget": 1000  // Monthly budget limit
  }
}
```

### **Expense Object**
- `id` - Unique identifier (UUID)
- `name` - Expense description
- `amount` - Cost (float)
- `category` - Category type (Food, Health, Travel, Rent, Beauty, Shopping, Other)
- `note` - Optional notes
- `date` - Date in YYYY-MM-DD format

---

## 🔄 Core Workflows

### **1. Authentication Flow**
```
User → Sign Up Page → Create Account → users.json (password hashed)
                           ↓
                       Login Page
                           ↓
                    Verify Credentials
                           ↓
                   Create Session → Dashboard
```

### **2. Expense Management Flow**
```
Add Expense → Form Submission → /add endpoint → Save to users.json
                                                      ↓
                                            Reload Dashboard
                                            
Edit Expense → Click Edit → Pre-fill Form → /edit endpoint → Update JSON
Delete Expense → Click Delete → /delete endpoint → Remove from JSON
```

### **3. Analytics & Visualization**
```
Load Expenses → Calculate Totals → Build Data Sets
                                        ↓
                    Chart.js (Client-side Rendering)
                    ├── Pie Chart (Category Distribution)
                    ├── Line Chart (Spending Over Time)
                    └── Display Insights
```

### **4. Budget Tracking**
```
Set Budget → /set-budget → Save to users.json
                  ↓
        Calculate Remaining = Budget - Total Spent
                  ↓
    Display Progress Bar & Status (Green/Yellow/Red)
```

---

## 🚀 Main Routes

### **Authentication Routes**
| Route | Method | Purpose |
|-------|--------|---------|
| `/login` | GET | Display login page |
| `/login` | POST | Process login credentials |
| `/signup` | GET | Display signup page |
| `/signup` | POST | Create new user account |
| `/logout` | GET | Clear session & redirect to login |

### **Main Application**
| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Main dashboard (requires authentication) |
| `/add` | POST | Add new expense |
| `/edit` | POST | Update existing expense |
| `/delete` | POST | Remove expense |
| `/set-budget` | POST | Set monthly budget |
| `/export` | GET | Download expenses as CSV file |

---

## 💡 Key Features Explained

### **Session Management**
```python
# SessionMiddleware secures user sessions
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

# Store user in session after login
request.session["user"] = username

# Verify user on protected routes
user = request.session.get("user")
```

### **Data Persistence Function**
```python
def load_users():
    # Read users.json and return dict
    # Returns {} if file doesn't exist

def save_users(data):
    # Write/update users.json with new data
```

### **Expense Sorting**
- **Recent**: Sorted by date (newest first)
- **Low → High**: Sorted by amount ascending
- **High → Low**: Sorted by amount descending

### **Budget Tracking**
- Visual progress bar shows usage percentage
- Color coding:
  - 🟢 Green: < 80% used
  - 🟡 Yellow: 80-100% used
  - 🔴 Red: Over 100% (budget exceeded)

### **Analytics & Insights**
- **Top Spending Category**: Shows which category you spend most on
- **Highest Transaction**: Single largest expense
- **Average Spending**: Mean expense amount
- **Visual Charts**: Pie chart for categories, line chart for daily trends

---

## 🎨 UI Components

### **Layout Structure**
```
┌─────────────────────────────────────────┐
│         Expense Tracker Header          │
├──────────────┬──────────────────────────┤
│              │                          │
│  Side Nav    │   Main Dashboard         │
│  (250px)     │   (Responsive)           │
│              │                          │
│ • Expenses   │  • KPI Cards             │
│ • Analytics  │  • Forms/List            │
│ • Logout     │  • Charts                │
│              │                          │
└──────────────┴──────────────────────────┘
```

### **Color Scheme**
- **Bg**: Dark gradient (slate-900 to black)
- **Accents**: Green (#22c55e) & Blue (#3b82f6)
- **Cards**: Semi-transparent slate-800 with backdrop blur
- **Text**: White with gray hierarchy (400-600 opacity)

---

## 🔧 Installation & Setup

### **Prerequisites**
- Python 3.8+
- pip (Python package manager)

### **Steps**

1. **Clone/Navigate to Project**
   ```bash
   cd expense-tracker
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Mac/Linux
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install passlib[bcrypt]  # For password hashing
   ```

4. **Run the Application**
   ```bash
   python -m uvicorn app:app --reload
   ```

5. **Access the App**
   - Open browser: `http://localhost:8000/login`
   - Create account or login with existing credentials

---

## 📝 Example Usage

### **Create a New Account**
1. Go to `/signup`
2. Enter username & password
3. Click "Sign Up"
4. Redirected to login page

### **Add an Expense**
1. Login to dashboard
2. Fill in expense form (left panel)
3. Select category from dropdown
4. Add optional note
5. Click "Add Expense"
6. Expense appears in list immediately

### **View Analytics**
1. Click "📊 Analytics" in sidebar
2. View pie chart (category breakdown)
3. View line chart (spending trend)
4. Read insights panel

### **Export Data**
1. Click "Export CSV" button
2. CSV file downloads with all expenses
3. Open in Excel/Sheets for further analysis

---

## 🔐 Security Features

⚠️ **Current Implementation Notes**:
- Passwords stored with bcrypt hashing
- Session-based authentication
- CSRF protection via SessionMiddleware
- Recommendations for production:
  - Use environment variables for secret key
  - Implement database instead of JSON
  - Add input validation & sanitization
  - Enable HTTPS/SSL
  - Add rate limiting

---

## 📊 File Breakdown

### [app.py](app.py) - 500+ Lines
**Lines 1-15**: Imports & app initialization
**Lines 16-30**: User storage functions (load/save)
**Lines 31-150**: Authentication routes (login, signup, logout)
**Lines 151-350**: Main dashboard route (complex HTML generation)
**Lines 351-450**: CRUD operations (add, edit, delete)
**Lines 451-520**: Export & budget routes

### [requirements.txt](requirements.txt) - 3 Dependencies
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `python-multipart` - Form parsing

### [users.json](users.json) - User Database
Contains all user accounts with encrypted passwords and expense history

### [expenses.json](expenses.json) - Sample Data
Reference file with sample expenses (not actively used in app)

### [static/](static/) - Assets
- Background images for authentication pages

---

## 🚀 Future Enhancement Ideas

- [ ] Database integration (PostgreSQL/SQLite)
- [ ] Email receipts & notifications
- [ ] Recurring expenses
- [ ] Shared budgets with multiple users
- [ ] Mobile app version
- [ ] Advanced filters & search
- [ ] Spending predictions with ML
- [ ] Multi-currency support
- [ ] Receipt image upload
- [ ] Dark/Light theme toggle
- [ ] API authentication (JWT)
- [ ] Two-factor authentication

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 already in use | `python -m uvicorn app:app --reload --port 8001` |
| Module not found errors | Install requirements: `pip install -r requirements.txt` |
| Session not persisting | Ensure SessionMiddleware is registered |
| CSS not loading | Check static files are served correctly |
| JSON decode errors | Verify JSON files have valid syntax |

---

## 📖 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Chart.js Guide](https://www.chartjs.org/docs/latest/)
- [Python JSON Module](https://docs.python.org/3/library/json.html)

---

## 📄 License

Free to use for personal & educational purposes

---

## 💬 Summary

This expense tracker is a **full-stack application** that demonstrates:
- ✅ Backend: FastAPI, routing, authentication, session management
- ✅ Frontend: HTML templating, Tailwind CSS, Chart.js
- ✅ Data: JSON persistence, CRUD operations
- ✅ Features: All core expense tracking functionality

**Ready to track your finances? Start the app and begin managing your money smartly!** 💸
