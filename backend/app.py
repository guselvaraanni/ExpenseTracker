from flask import Flask, render_template, request, redirect, url_for,jsonify,session
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for
from datetime import datetime,timedelta
from collections import defaultdict


app = Flask(__name__)
app.secret_key = "dev-secret-123"


# Authentication
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Home Page
@app.route('/')
def home():
    return redirect(url_for('login'))

users = {
    "test@example.com": "1234"   # existing demo user
}

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check user exists and password matches
        if username in users and users[username] == password:
            session['user_id'] = username
            return redirect(url_for('dashboard'))

        return render_template(
            'login.html',
            error="Invalid email or password"
        )

    return render_template('login.html')


@app.route('/signup' , methods=['GET','POST'])
def signup():
    if request.method == "POST":
        username = request.form['email']
        password = request.form['password']

        if username in users:
            return render_template(
                "signup.html",
                error="User already exists. Please login."
            )

        # Save user (later → DB + hashing)
        users[username] = password

        # Redirect to login page after successful signup
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard_dark.html')



# In-memory data for demo purposes
categories = ["Food", "Transport", "Bills"]
# expenses = [
    # {"date": "2025-09-01", "desc": "Salary", "category": "Income", "amount": 4500, "type": "Income"},
    # {"date": "2025-09-05", "desc": "Rent", "category": "Housing", "amount": 1500, "type": "Expense"},
    # {"date": "2025-09-10", "desc": "Groceries", "category": "Food", "amount": 200, "type": "Expense"},
    # {"date": "2025-09-12", "desc": "Electricity Bill", "category": "Bills", "amount": 100, "type": "Expense"},
# ]



# Add new expense
# @app.route('/add_expense', methods=['POST'])
# def add_expense():
#     data = request.form
#     expense = {
#         "date": data.get("date") or datetime.now().strftime("%Y-%m-%d"),
#         "desc": data.get("desc"),
#         "category": data.get("category"),
#         "amount": float(data.get("amount")),
#         "type": data.get("type")
#     }
#     expenses.append(expense)
#     if expense["category"] not in categories:
#         categories.append(expense["category"])
#     return jsonify(success=True, expense=expense)

# Get dashboard data - Responsible for getting Expense Distribution and Recent Transactions
# @app.route('/dashboard_data')
# def dashboard_data():
#     total_balance = sum(e["amount"] for e in expenses)
#     income = sum(e["amount"] for e in expenses if e["type"] == "Income")
#     expense_total = sum(e["amount"] for e in expenses if e["type"] == "Expense")
    
#     # Prepare category-wise expense
#     category_expense = {}
#     for e in expenses:
#         if e["type"] == "Expense":
#             category_expense[e["category"]] = category_expense.get(e["category"], 0) + abs(e["amount"])
    
#     return jsonify({
#         "total_balance": total_balance,
#         "income": income,
#         "expense_total": expense_total,
#         "category_expense": category_expense,
#         "recent_transactions": expenses[-10:][::-1]  # Last 10 expenses
#     })

# Settings
transactions = [
        {"date": "2025-09-01", "desc": "Salary", "category": "Income", "amount": 4500, "type": "Income"},
    {"date": "2025-09-05", "desc": "Rent", "category": "Housing", "amount": 1500, "type": "Expense"},
    {"date": "2025-09-10", "desc": "Groceries", "category": "Food", "amount": 200, "type": "Expense"},
    {"date": "2025-09-12", "desc": "Electricity Bill", "category": "Bills", "amount": 100, "type": "Expense"}
]
user_profile = {}


@app.route("/dashboard_data")
@login_required
def dashboard_data():
    income = sum(t["amount"] for t in transactions if t["type"] == "Income")
    expense = sum(t["amount"] for t in transactions if t["type"] == "Expense")

    category_expense = {}
    for t in transactions:
        if t["type"] == "Expense":
            category_expense[t["category"]] = category_expense.get(t["category"], 0) + t["amount"]

    return jsonify({
        "total_balance": income - expense,
        "income": income,
        "expense_total": expense,
        "category_expense": category_expense,
        "recent_transactions": transactions[-5:][::-1]
    })




@app.route('/settings')
def settings():
    return render_template('settings.html')

# @app.route("/signup")
# def signup():
#     return render_template('signup.html')

@app.route('/expense')
def expense():
    return render_template('expense.html')

@app.route('/report')
def report():
    return render_template('report.html')

# Add Expense
# @app.route('/save_expense', methods=['POST'])
# def save_expense():
#     return "saved successfully"
@app.route('/save_expense', methods=['POST'])
@login_required
def save_expense():
    print("SAVE EXPENSE HIT")   # 👈 add this
    print("DATA:", request.json)

    data = request.json
    expense = {
        "date": data["date"],
        "desc": data["desc"],
        "category": data["category"],
        "amount": float(data["amount"]),
        "type": data["type"]
    }

    transactions.append(expense)
    print("TRANSACTIONS:", transactions)

    return jsonify(success=True)







@app.route("/update_info", methods=["POST"])
def update_info():
    salary = float(request.form["salary"])

    user_profile["salary"] = salary

    transactions.append({
        "amount": salary,
        "type": "Income",
        "category": "Salary",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "desc": "Monthly Salary"
    })

    return jsonify(success=True, message="Salary updated")



@app.route('/add_category', methods=['POST'])
def add_category(): 
    new_category = request.form.get("new-category")
    if new_category and new_category not in categories:
        categories.append(new_category)
        return jsonify(success=True, category=new_category, message=f"Category '{new_category}' added successfully")
    else:
        return jsonify(success=False, message="Category already exists or invalid input")
    
# Dashboard data
@app.route("/dashboard_chart_data")
@login_required
def dashboard_chart_data():
    monthly_income = [0] * 12
    monthly_expenses = [0] * 12
    category_expense = defaultdict(float)

    for e in transactions:
        month = datetime.fromisoformat(e["date"]).month - 1

        if e["type"] == "Income":
            monthly_income[month] += e["amount"]
        else:
            monthly_expenses[month] += e["amount"]
            category_expense[e["category"]] += e["amount"]

    return jsonify({
        "months": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "income": monthly_income,
        "expenses": monthly_expenses,
        "category_expense": category_expense
    })



# report data

@app.route("/report_data")
@login_required
def report_data():
    range_days = request.args.get("range", "30")
    category = request.args.get("category", "All")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=int(range_days))

    filtered = []
    for t in transactions:
        t_date = datetime.fromisoformat(t["date"])
        if t_date >= start_date:
            if category == "All" or t["category"] == category:
                filtered.append(t)

    monthly_income = [0] * 12
    monthly_expenses = [0] * 12
    category_expense = defaultdict(float)

    for t in filtered:
        month = datetime.fromisoformat(t["date"]).month - 1
        if t["type"] == "Income":
            monthly_income[month] += t["amount"]
        else:
            monthly_expenses[month] += t["amount"]
            category_expense[t["category"]] += t["amount"]

    return jsonify({
        "months": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "income": monthly_income,
        "expenses": monthly_expenses,
        "category_expense": category_expense,
        "transactions": filtered[::-1]
    })


if __name__ == '__main__':
    app.run(debug=True)
