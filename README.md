# 🌾 Zero Hunger — FoodLink

> **Hackathon Project | Epoch '26 | Team SG133**
> A smart food surplus matching platform that connects food donors with NGOs and communities in need — reducing waste and fighting hunger at the same time.

---

## 📌 Table of Contents

- [Project Overview](#-project-overview)
- [Problem Statement](#-problem-statement)
- [Solution](#-solution)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [How It Works — System Architecture](#-how-it-works--system-architecture)
- [Core Features](#-core-features)
- [Database Schema](#-database-schema)
- [Matching Algorithm](#-matching-algorithm)
- [API Routes](#-api-routes)
- [Setup & Installation](#-setup--installation)
- [Running the App](#-running-the-app)
- [Demo Mode](#-demo-mode)
- [Screenshots / UI](#-screenshots--ui)
- [Future Improvements](#-future-improvements)
- [Team](#-team)

---

## 🌍 Project Overview

**FoodLink** is a web-based food redistribution platform built during **Epoch '26 Hackathon**. It bridges the gap between restaurants/hotels with surplus food and NGOs/communities that need it — using a smart matching algorithm that prioritizes food expiry, quantity, and location.

---

## 🚨 Problem Statement

Every day, thousands of kilograms of food are wasted by restaurants, hotels, and catering services — while millions of people go hungry. The challenge is:

- **No efficient channel** exists to connect food donors with receivers in real-time.
- **Expiring food** often gets thrown away rather than redistributed.
- **NGOs** don't know which donors have surplus and how much.

---

## ✅ Solution

FoodLink creates a live **dashboard** where:

1. **Donors** (restaurants, kitchens) submit surplus food entries with quantity and expiry.
2. **Receivers** (NGOs, shelters) submit their demand.
3. A **smart matching engine** automatically pairs donors with receivers, prioritizing the most urgent (soonest-expiring) food first.
4. Both parties can track **delivery status** in real-time.

---

## 🛠 Tech Stack

| Layer        | Technology                        |
|--------------|-----------------------------------|
| Backend      | Python, Flask                     |
| Database     | SQLite (`foodlink.db`)            |
| Frontend     | HTML, Jinja2 Templates            |
| Matching     | Custom Python Algorithm           |
| Deployment   | GitHub Actions (CI/CD workflow)   |

---

## 📁 Project Structure

```
Hackathon_Zero-Hunger_SG133/
│
├── app.py              # Main Flask application — routes, logic, matching
├── matching.py         # (Optional) Standalone matching utilities
├── utils.py            # Helper functions
├── foodlink.db         # SQLite database (auto-created on first run)
│
├── templates/          # HTML templates (Jinja2)
│   ├── index.html      # Home / landing page
│   └── dashboard.html  # Live matching dashboard
│
├── .github/
│   └── workflows/      # GitHub Actions CI/CD configuration
│
└── README.md           # Project documentation
```

---

## 🏗 How It Works — System Architecture

```
User (Donor / Receiver)
        │
        ▼
  [index.html] ──── Submit Form ────▶ /submit (POST)
                                          │
                                          ▼
                                    SQLite DB (entries)
                                          │
                                          ▼
                                   /dashboard (GET)
                                          │
                              ┌───────────┴────────────┐
                              ▼                         ▼
                        Surplus List               Demand List
                              │                         │
                              └──────── Matching ───────┘
                                        Algorithm
                                            │
                                            ▼
                                  Matches Table (DB)
                                            │
                                            ▼
                               dashboard.html (rendered)
```

**Step-by-step flow:**

1. A restaurant visits `/` and fills in the food submission form (name, type = surplus, quantity, expiry in days, location).
2. An NGO visits `/` and fills in the form (type = demand, quantity needed).
3. Both entries are stored in the `entries` table of `foodlink.db`.
4. When `/dashboard` is loaded, the matching algorithm runs automatically:
   - Surplus items are sorted by **expiry (ascending)** — most urgent first.
   - Demand items are sorted by **quantity (descending)** — largest need first.
   - The algorithm greedily assigns surplus to demand until quantities are exhausted.
   - Match records are saved to the `matches` table.
5. The dashboard renders all surplus entries, demand entries, and match results with a simulated delivery status.

---

## ⭐ Core Features

### 1. Food Submission Form
- Any donor or receiver can register by submitting a simple form.
- Fields: Name, Type (surplus/demand), Quantity (meals), Expiry (days), Location.

### 2. Smart Matching Dashboard
- Automatically runs on every `/dashboard` visit.
- Shows live list of all surplus entries, demand entries, and computed matches.
- Displays how much food each NGO received vs. how much they still need.

### 3. Expiry-Prioritized Matching
- Food expiring soonest is always matched first, reducing waste.
- A single surplus donor can partially fulfill multiple receivers.

### 4. Delivery Status Simulation
- Each match is assigned a simulated status: `Assigned`, `Picked Up`, `In Transit`, or `Delivered`.
- In production, this would connect to a real logistics or volunteer tracking system.

### 5. Demo Mode (`/demo`)
- One-click endpoint that wipes the database and loads realistic test data.
- 5 donor restaurants + 2 NGOs are auto-inserted with varied quantities and locations.
- Instantly demonstrates the full matching pipeline.

### 6. Predicted Demand
- A simple average-based prediction is shown on the dashboard to give an idea of future demand.

---

## 🗄 Database Schema

### `entries` table

| Column       | Type     | Description                                 |
|--------------|----------|---------------------------------------------|
| `id`         | INTEGER  | Auto-incremented primary key                |
| `name`       | TEXT     | Name of donor or receiver                   |
| `type`       | TEXT     | `"surplus"` or `"demand"`                   |
| `qty`        | INTEGER  | Quantity of meals                           |
| `expiry`     | INTEGER  | Days until expiry (0 = today)               |
| `location`   | TEXT     | Area/city name                              |
| `trust`      | INTEGER  | Trust score (default: 100)                  |
| `created_at` | TEXT     | Timestamp of submission                     |

### `matches` table

| Column       | Type     | Description                                 |
|--------------|----------|---------------------------------------------|
| `id`         | INTEGER  | Auto-incremented primary key                |
| `donor`      | TEXT     | Name of surplus donor                       |
| `receiver`   | TEXT     | Name of demand receiver                     |
| `qty`        | INTEGER  | Matched quantity                            |
| `status`     | TEXT     | Delivery status                             |
| `location`   | TEXT     | Receiver's location                         |
| `created_at` | TEXT     | Timestamp of match                          |

---

## 🔄 Matching Algorithm

The matching logic lives inside the `/dashboard` route in `app.py`:

```python
# Step 1: Sort surplus by expiry (soonest first)
surplus_copy.sort(key=lambda x: x["expiry"])

# Step 2: Sort demand by quantity (largest need first)
demand_copy.sort(key=lambda x: x["qty"], reverse=True)

# Step 3: Greedy matching loop
for each demand_entry:
    for each surplus_entry (with qty > 0):
        matched_qty = min(surplus_entry["qty"], demand_entry["qty"])
        surplus_entry["qty"] -= matched_qty
        demand_entry["qty"] -= matched_qty
        save match to DB
```

**Key design decisions:**
- Deep copies of the data are used so the original displayed data is unaffected.
- The algorithm is greedy — it maximizes the number of fulfilled demands per run.
- Matches are cleared and re-computed on each dashboard refresh for accuracy.

---

## 🌐 API Routes

| Route        | Method | Description                                              |
|--------------|--------|----------------------------------------------------------|
| `/`          | GET    | Home page with submission form                           |
| `/submit`    | POST   | Accepts form data and saves a new entry to the database  |
| `/dashboard` | GET    | Runs matching algorithm and renders the results dashboard|
| `/demo`      | GET    | Clears DB and loads sample data, then redirects to dashboard |

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.8 or higher
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/DeepakKatwa/Hackathon_Zero-Hunger_SG133.git
cd Hackathon_Zero-Hunger_SG133
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install flask
```

> No additional packages are required — the project uses only Flask and Python's standard library (`sqlite3`, `datetime`, `copy`, `random`).

---

## ▶️ Running the App

```bash
python app.py
```

By default, Flask runs on `http://127.0.0.1:5000`. Open this in your browser.

The database (`foodlink.db`) is created automatically on the first run via `init_db()`.

---

## 🎬 Demo Mode

To instantly populate the app with realistic test data, visit:

```
http://127.0.0.1:5000/demo
```

This will:
1. Clear all existing entries and matches.
2. Insert 5 donor restaurants (Spice Garden, Urban Bites, Green Leaf Kitchen, Royal Dine, Food Fiesta) across Bangalore.
3. Insert 2 NGO receivers (Helping Hands NGO, Care Foundation).
4. Automatically redirect to `/dashboard` and run the matching algorithm.

---

## 🚀 Future Improvements

- **Real-time notifications** — Email/SMS alerts to NGOs when food is matched.
- **Geolocation-based matching** — Prioritize donors closest to receivers.
- **Volunteer tracking** — Live status updates via a mobile app for delivery volunteers.
- **Trust scoring** — Dynamically adjust trust scores based on fulfillment history.
- **Admin panel** — Manage all entries, matches, and users from one place.
- **Login/Auth system** — Separate portals for donors and receivers.
- **Production database** — Migrate from SQLite to PostgreSQL for scalability.
- **AI Demand Forecasting** — Predict NGO demand based on historical trends.

---

## 👥 Team

**Team ID:** SG133
**Hackathon:** Epoch '26

| Contributor     | GitHub                                                         |
|-----------------|----------------------------------------------------------------|
| Deepak Katwa    | [@DeepakKatwa](https://github.com/DeepakKatwa)                |

---

## 📄 License

This project was built for a hackathon and is open for educational use.

---

> *"No one should go to bed hungry while food is being thrown away."*
> — FoodLink, Zero Hunger Initiative
