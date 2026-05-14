"""
Synthetic Retail Data Generator
Generates realistic 500K+ transaction records for the Retail Analytics Dashboard
"""

import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

# ── Config ───────────────────────────────────────────────────────────────────
NUM_CUSTOMERS   = 10_000
NUM_PRODUCTS    = 500
NUM_STORES      = 25
NUM_TRANSACTIONS = 500_000
START_DATE      = datetime(2022, 1, 1)
END_DATE        = datetime(2025, 12, 31)

# ── Reference Data ───────────────────────────────────────────────────────────
CATEGORIES = {
    "Electronics":    ["Laptops", "Phones", "Tablets", "Accessories", "Cameras"],
    "Clothing":       ["Men's Wear", "Women's Wear", "Kids", "Footwear", "Sportswear"],
    "Home & Kitchen": ["Appliances", "Furniture", "Decor", "Cookware", "Bedding"],
    "Books":          ["Fiction", "Non-Fiction", "Academic", "Children's", "Comics"],
    "Beauty":         ["Skincare", "Haircare", "Makeup", "Fragrances", "Tools"],
}

STATES = [
    "CA", "TX", "FL", "NY", "IL", "PA", "OH", "GA", "NC", "MI",
    "NJ", "VA", "WA", "AZ", "MA", "TN", "IN", "MD", "MO", "CO",
]

CITIES_BY_STATE = {
    "CA": ["Los Angeles", "San Francisco", "San Diego"],
    "TX": ["Houston", "Dallas", "Austin"],
    "FL": ["Miami", "Orlando", "Tampa"],
    "NY": ["New York", "Buffalo", "Albany"],
    "IL": ["Chicago", "Aurora", "Naperville"],
    "PA": ["Philadelphia", "Pittsburgh", "Allentown"],
    "OH": ["Columbus", "Cleveland", "Cincinnati"],
    "GA": ["Atlanta", "Augusta", "Savannah"],
    "NC": ["Charlotte", "Raleigh", "Durham"],
    "MI": ["Detroit", "Grand Rapids", "Warren"],
    "NJ": ["Newark", "Jersey City", "Paterson"],
    "VA": ["Virginia Beach", "Norfolk", "Richmond"],
    "WA": ["Seattle", "Spokane", "Tacoma"],
    "AZ": ["Phoenix", "Tucson", "Scottsdale"],
    "MA": ["Boston", "Worcester", "Springfield"],
    "TN": ["Nashville", "Memphis", "Knoxville"],
    "IN": ["Indianapolis", "Fort Wayne", "Evansville"],
    "MD": ["Baltimore", "Frederick", "Rockville"],
    "MO": ["Kansas City", "St. Louis", "Springfield"],
    "CO": ["Denver", "Colorado Springs", "Aurora"],
}

CHANNELS   = ["Online", "In-Store", "Mobile App"]
SEGMENTS   = ["Premium", "Regular", "Budget"]
STORE_NAMES = [f"Store_{str(i).zfill(3)}" for i in range(1, NUM_STORES + 1)]

# ── Generate Customers ────────────────────────────────────────────────────────
def generate_customers():
    print("Generating customers...")
    first_names = ["Emma","Liam","Olivia","Noah","Ava","William","Isabella","James",
                   "Sophia","Oliver","Mia","Benjamin","Charlotte","Elijah","Amelia",
                   "Lucas","Harper","Mason","Evelyn","Logan","Abigail","Ethan","Emily",
                   "Aiden","Elizabeth","Caden","Mila","Jackson","Ella","Grayson"]
    last_names  = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller",
                   "Davis","Wilson","Taylor","Moore","Anderson","Thomas","Jackson",
                   "White","Harris","Martin","Thompson","Lewis","Robinson","Walker"]

    states   = np.random.choice(STATES, NUM_CUSTOMERS)
    segments = np.random.choice(SEGMENTS, NUM_CUSTOMERS, p=[0.2, 0.55, 0.25])
    join_dates = [
        START_DATE + timedelta(days=int(x))
        for x in np.random.randint(0, (END_DATE - START_DATE).days, NUM_CUSTOMERS)
    ]

    customers = pd.DataFrame({
        "customer_id":  [f"CUST_{str(i).zfill(6)}" for i in range(1, NUM_CUSTOMERS + 1)],
        "first_name":   np.random.choice(first_names, NUM_CUSTOMERS),
        "last_name":    np.random.choice(last_names,  NUM_CUSTOMERS),
        "email":        [f"user{i}@email.com" for i in range(1, NUM_CUSTOMERS + 1)],
        "state":        states,
        "city":         [random.choice(CITIES_BY_STATE[s]) for s in states],
        "segment":      segments,
        "join_date":    [d.strftime("%Y-%m-%d") for d in join_dates],
        "age":          np.random.randint(18, 70, NUM_CUSTOMERS),
    })
    return customers


# ── Generate Products ────────────────────────────────────────────────────────
def generate_products():
    print("Generating products...")
    records = []
    pid = 1
    per_cat = NUM_PRODUCTS // len(CATEGORIES)

    price_ranges = {
        "Electronics":    (49,  1500),
        "Clothing":       (15,  300),
        "Home & Kitchen": (20,  800),
        "Books":          (8,   60),
        "Beauty":         (10,  200),
    }

    for cat, subcats in CATEGORIES.items():
        lo, hi = price_ranges[cat]
        for _ in range(per_cat):
            price = round(np.random.uniform(lo, hi), 2)
            cost  = round(price * np.random.uniform(0.35, 0.65), 2)
            records.append({
                "product_id":   f"PROD_{str(pid).zfill(5)}",
                "product_name": f"{cat} Item {pid}",
                "category":     cat,
                "subcategory":  np.random.choice(subcats),
                "price":        price,
                "cost":         cost,
            })
            pid += 1

    return pd.DataFrame(records)


# ── Generate Transactions ────────────────────────────────────────────────────
def generate_transactions(customers, products):
    print("Generating 500K transactions (this may take ~30 seconds)...")

    total_days  = (END_DATE - START_DATE).days
    cust_ids    = customers["customer_id"].values
    prod_ids    = products["product_id"].values

    # Seasonal multipliers by month (holiday spikes in Nov/Dec)
    month_weights = np.array([0.7, 0.65, 0.8, 0.85, 0.9, 0.95,
                               0.9, 0.85, 0.9, 0.95, 1.3, 1.5])
    month_weights /= month_weights.sum()

    # Build date pool weighted by seasonality
    date_pool = []
    for _ in range(NUM_TRANSACTIONS):
        month = np.random.choice(range(1, 13), p=month_weights)
        year  = np.random.choice([2022, 2023, 2024, 2025])
        day   = np.random.randint(1, 29)
        try:
            date_pool.append(datetime(year, month, day))
        except ValueError:
            date_pool.append(datetime(year, month, 1))

    transactions = pd.DataFrame({
        "transaction_id": [f"TXN_{str(i).zfill(8)}" for i in range(1, NUM_TRANSACTIONS + 1)],
        "customer_id":    np.random.choice(cust_ids, NUM_TRANSACTIONS),
        "product_id":     np.random.choice(prod_ids, NUM_TRANSACTIONS),
        "quantity":       np.random.choice([1, 2, 3, 4, 5], NUM_TRANSACTIONS, p=[0.55, 0.25, 0.12, 0.05, 0.03]),
        "store_id":       np.random.choice(STORE_NAMES, NUM_TRANSACTIONS),
        "channel":        np.random.choice(CHANNELS, NUM_TRANSACTIONS, p=[0.45, 0.40, 0.15]),
        "transaction_date": [d.strftime("%Y-%m-%d") for d in date_pool],
        "discount_pct":   np.random.choice([0, 5, 10, 15, 20, 25], NUM_TRANSACTIONS, p=[0.50, 0.15, 0.15, 0.10, 0.07, 0.03]),
    })

    # Merge price info to compute revenue
    transactions = transactions.merge(
        products[["product_id", "price", "cost"]], on="product_id", how="left"
    )
    transactions["unit_price"]    = transactions["price"]
    transactions["revenue"]       = (
        transactions["unit_price"] * transactions["quantity"]
        * (1 - transactions["discount_pct"] / 100)
    ).round(2)
    transactions["cogs"]          = (transactions["cost"] * transactions["quantity"]).round(2)
    transactions["gross_profit"]  = (transactions["revenue"] - transactions["cogs"]).round(2)

    transactions.drop(columns=["price", "cost"], inplace=True)
    return transactions


# ── Save to CSV & SQLite ─────────────────────────────────────────────────────
def save_data(customers, products, transactions):
    os.makedirs("data", exist_ok=True)

    customers.to_csv("data/customers.csv",         index=False)
    products.to_csv("data/products.csv",           index=False)
    transactions.to_csv("data/transactions.csv",   index=False)
    print("✅ CSVs saved.")

    db_path = "data/retail.db"
    conn    = sqlite3.connect(db_path)
    customers.to_sql("customers",     conn, if_exists="replace", index=False)
    products.to_sql("products",       conn, if_exists="replace", index=False)
    transactions.to_sql("transactions", conn, if_exists="replace", index=False)
    conn.close()
    print(f"✅ SQLite database saved → {db_path}")


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    customers    = generate_customers()
    products     = generate_products()
    transactions = generate_transactions(customers, products)
    save_data(customers, products, transactions)

    print("\n📊 Data Summary:")
    print(f"   Customers:    {len(customers):,}")
    print(f"   Products:     {len(products):,}")
    print(f"   Transactions: {len(transactions):,}")
    print(f"   Total Revenue: ${transactions['revenue'].sum():,.2f}")
    print("\nDone! Run the dashboard next: streamlit run dashboard/app.py")
