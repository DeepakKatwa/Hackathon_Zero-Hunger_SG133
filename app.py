from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import copy
import random

app = Flask(__name__)
DB = "foodlink.db"

def get_db():
    return sqlite3.connect(DB)

def init_db():
    conn = get_db()
    c = conn.cursor()

    # entries table
    c.execute("""
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        type TEXT,
        qty INTEGER,
        expiry INTEGER,
        location TEXT,
        trust INTEGER,
        created_at TEXT
    )
    """)

    # matches table
    c.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor TEXT,
        receiver TEXT,
        qty INTEGER,
        status TEXT,
        location TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template("index.html")

# 🔥 DEMO DATA
@app.route('/demo')
def demo():
    conn = get_db()
    c = conn.cursor()

    c.execute("DELETE FROM entries")
    c.execute("DELETE FROM matches")

    data = [
        ("Spice Garden", "surplus", 25, 2, "Bangalore", 100),
        ("Urban Bites", "surplus", 40, 5, "Whitefield", 100),
        ("Green Leaf Kitchen", "surplus", 18, 1, "Indiranagar", 100),
        ("Royal Dine", "surplus", 55, 4, "Marathahalli", 100),
        ("Food Fiesta", "surplus", 30, 3, "BTM", 100),

        ("Helping Hands NGO", "demand", 50, 0, "KR Puram", 100),
        ("Care Foundation", "demand", 60, 0, "Electronic City", 100)
    ]

    for d in data:
        c.execute("""
        INSERT INTO entries (name, type, qty, expiry, location, trust, created_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, d)

    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

# 🔥 SUBMIT
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    type_ = request.form.get('type')
    qty = int(request.form.get('qty'))
    expiry = int(request.form.get('expiry') or 999)
    location = request.form.get('location') or "N/A"

    conn = get_db()
    c = conn.cursor()

    c.execute("""
    INSERT INTO entries (name, type, qty, expiry, location, trust, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, type_, qty, expiry, location, 100, datetime.now().isoformat()))

    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

# 🔥 DASHBOARD
@app.route('/dashboard')
def dashboard():
    conn = get_db()
    c = conn.cursor()

    # clear old matches
    c.execute("DELETE FROM matches")

    c.execute("SELECT * FROM entries")
    rows = c.fetchall()

    surplus = []
    demand = []

    for r in rows:
        item = {
            "name": r[1],
            "type": r[2],
            "qty": r[3],
            "expiry": r[4],
            "location": r[5]
        }

        if item["type"] == "surplus":
            surplus.append(item)
        else:
            demand.append(item)

    # copies (important)
    surplus_copy = copy.deepcopy(surplus)
    demand_copy = copy.deepcopy(demand)

    # smart sorting
    surplus_copy.sort(key=lambda x: x["expiry"])
    demand_copy.sort(key=lambda x: x["qty"], reverse=True)

    matches = []
    total = 0

    for d in demand_copy:
        original = d["qty"]
        fulfilled = 0

        for s in surplus_copy:
            if s["qty"] <= 0:
                continue
            if d["qty"] <= 0:
                break

            m = min(s["qty"], d["qty"])

            s["qty"] -= m
            d["qty"] -= m

            fulfilled += m
            total += m

            # save match
            c.execute("""
            INSERT INTO matches (donor, receiver, qty, status, location, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                s["name"],
                d["name"],
                m,
                "Assigned",
                d["location"],
                datetime.now().isoformat()
            ))

        matches.append({
            "to": d["name"],
            "location": d["location"],
            "requested": original,
            "matched": fulfilled,
            "remaining": original - fulfilled
        })

    conn.commit()

    # fetch matches
    c.execute("SELECT donor, receiver, qty, status FROM matches")
    db_matches = c.fetchall()
    conn.close()

    # simulate status
    status_list = ["Assigned", "Picked Up", "In Transit", "Delivered"]
    enriched_matches = []

    for m in matches:
        m["status"] = random.choice(status_list)
        enriched_matches.append(m)

    predicted = int(sum(d["qty"] for d in demand) / len(demand)) if demand else 0

    return render_template(
        "dashboard.html",
        surplus=surplus,
        demand=demand,
        matches=enriched_matches,
        total=total,
        predicted=predicted
    )

if __name__ == '__main__':
    app.run(debug=True)