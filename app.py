from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path
from datetime import date, datetime

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "expenses.db"

app = Flask(__name__)

# ---------- DB helpers ----------
def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            note TEXT,
            payment_method TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- Categories with icons and multilingual names ----------
CATEGORIES = [
    {"id":"milk","en":"Milk","hi":"दूध","te":"పాలు","icon":"🥛"},
    {"id":"coffee","en":"Coffee/Tea","hi":"चाय/कॉफ़ी","te":"టీ/కాఫీ","icon":"☕"},
    {"id":"groceries","en":"Groceries","hi":"किराना","te":"కిరాణా","icon":"🛒"},
    {"id":"vegetables","en":"Vegetables","hi":"सब्ज़ियाँ","te":"కూరగాయలు","icon":"🥦"},
    {"id":"water","en":"Water","hi":"पानी","te":"నీరు","icon":"💧"},
    {"id":"gas","en":"Cooking Gas","hi":"गैस","te":"గ్యాస్","icon":"🔥"},
    {"id":"travel","en":"Travel","hi":"यात्रा","te":"ప్రయాణం","icon":"🛵"},
    {"id":"rent","en":"Rent","hi":"किराया","te":"ఇంటి అద్దె","icon":"🏠"},
    {"id":"electricity","en":"Electricity","hi":"बिजली","te":"కరెంట్","icon":"⚡"},
    {"id":"internet","en":"Internet","hi":"इंटरनेट","te":"ఇంటర్నెట్","icon":"📶"},
    {"id":"education","en":"Education","hi":"शिक्षा","te":"విద్య","icon":"🎓"},
    {"id":"medical","en":"Medical","hi":"चिकित्सा","te":"వైద్యం","icon":"⚕"},
    {"id":"others","en":"Others","hi":"अन्य","te":"ఇతర","icon":"📋"}
]

# ---------- Routes ----------
@app.route("/")
def index():
    today = date.today().isoformat()
    month = datetime.now().strftime("%Y-%m")

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM expenses ORDER BY date DESC, id DESC")
    expenses = cur.fetchall()

    total_all = sum(row['amount'] for row in expenses) if expenses else 0

    daily_total = conn.execute(
        "SELECT SUM(amount) FROM expenses WHERE date=?", (today,)
    ).fetchone()[0] or 0

    monthly_total = conn.execute(
        "SELECT SUM(amount) FROM expenses WHERE strftime('%Y-%m', date)=?", (month,)
    ).fetchone()[0] or 0

    conn.close()

    return render_template(
        "index.html",
        expenses=expenses,
        total=total_all,
        daily_total=daily_total,
        monthly_total=monthly_total,
        categories=CATEGORIES,
        today=today
    )

@app.route("/add", methods=["POST"])
def add_expense():
    dt = request.form.get("date") or date.today().isoformat()
    category = request.form.get("category")
    amount = request.form.get("amount", "0")
    note = request.form.get("note")
    payment = request.form.get("payment")

    try:
        amt = float(amount)
    except:
        amt = 0.0

    if not category or amt <= 0:
        return "Category and positive amount required", 400

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO expenses (date, category, amount, note, payment_method) VALUES (?, ?, ?, ?, ?)",
        (dt, category, amt, note, payment)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
