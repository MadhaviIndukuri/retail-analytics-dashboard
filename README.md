# 🛍️ Retail Sales & Customer Intelligence Dashboard

> **End-to-end retail analytics solution** analyzing 500K+ transactions to surface revenue drivers, customer segments, and retention insights — built with Python, SQL (SQLite), and Streamlit.

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey?logo=sqlite)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-orange?logo=scikit-learn)
![Plotly](https://img.shields.io/badge/Plotly-Visualization-3F4F75?logo=plotly)

---

## 📌 Project Overview

This project simulates a real-world retail analytics platform built for a multi-channel retailer operating across 20 US states. The pipeline ingests raw transactional data, performs customer intelligence analysis, and surfaces insights through an interactive dashboard.

**Key business questions answered:**
- Which products, categories, and regions drive the most revenue and margin?
- How are customer retention rates trending over time (cohort analysis)?
- Which customers are Champions, Loyal, At-Risk, or Lost (RFM segmentation)?
- What does the next 6-month revenue forecast look like?

---

## 🏗️ Architecture

```
Raw Data (CSV)
     │
     ▼
SQLite Database  ←──  SQL Schema & Queries
     │
     ▼
Python Analysis Layer
  ├── EDA & KPI Aggregations
  ├── RFM Segmentation (Pandas + Scikit-learn)
  ├── Cohort Retention Analysis
  └── Revenue Forecasting (Linear Regression)
     │
     ▼
Streamlit Interactive Dashboard
  ├── 7 KPI Cards
  ├── Monthly Revenue & Profit Trend
  ├── Category & Channel Performance
  ├── Top 15 Products (with Margin)
  ├── Regional Choropleth Map (USA)
  ├── RFM Scatter + Segment Charts
  └── Cohort Retention Heatmap
```

---

## 📁 Project Structure

```
retail-analytics-dashboard/
├── data/
│   └── generate_data.py       # Synthetic data generator (500K transactions)
├── sql/
│   ├── schema.sql             # Database schema (customers, products, transactions)
│   └── queries.sql            # Key analytical SQL queries
├── analysis/
│   ├── rfm_segmentation.py    # RFM scoring + cohort analysis
│   └── forecasting.py         # Revenue forecasting model
├── dashboard/
│   └── app.py                 # Streamlit interactive dashboard
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/MadhaviIndukuri/retail-analytics-dashboard.git
cd retail-analytics-dashboard
```

### 2. Create a Virtual Environment & Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
pip install -r requirements.txt
```

### 3. Generate Synthetic Data (~30 seconds)
```bash
python data/generate_data.py
```
This creates `data/retail.db` (SQLite) and CSV files with:
- 10,000 customers across 20 US states
- 500 products across 5 categories
- 500,000 transactions from 2022–2025

### 4. Run the Dashboard
```bash
streamlit run dashboard/app.py
```
Opens at **http://localhost:8501** in your browser.

### 5. (Optional) Run Analysis Scripts
```bash
python analysis/rfm_segmentation.py   # RFM + cohort charts → data/outputs/
python analysis/forecasting.py        # Revenue forecast  → data/outputs/
```

---

## 📊 Dashboard Features

| Section | KPIs / Visuals |
|---------|---------------|
| **KPI Cards** | Total Revenue, Orders, AOV, Unique Customers, Gross Profit, Margin %, Repeat Rate |
| **Revenue Trend** | Monthly bar + line chart (Revenue + Gross Profit) |
| **Category & Channel** | Horizontal bar by category, Donut chart by channel |
| **Top Products** | Bar chart with margin color coding |
| **Regional Map** | USA choropleth — revenue by state |
| **RFM Segmentation** | Pie, bar, and scatter plot by segment |
| **Cohort Analysis** | Retention heatmap (last 18 cohorts × 12 months) |

All charts have **sidebar filters** for Year, Channel, Category, and Customer Segment.

---

## 🧠 Technical Highlights

- **RFM Segmentation**: Quintile-based scoring (Recency, Frequency, Monetary) to classify customers into Champions, Loyal, At-Risk, and Lost segments
- **Cohort Analysis**: Month-over-month retention rates by acquisition cohort
- **Revenue Forecasting**: Linear Regression with lag features (3-month lags + rolling mean) for 6-month forward projection
- **SQL Analytics**: Window functions, CTEs, aggregations for KPI generation
- **Data Pipeline**: Automated cleaning, transformation, and aggregation with Pandas

---

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| Language | Python 3.13 |
| Database | SQLite (via Python `sqlite3`) |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Visualization | Plotly, Matplotlib, Seaborn |
| Dashboard | Streamlit |
| Version Control | Git, GitHub |

---

## 👩‍💻 Author

**Madhavi Indukuri** — Data Analyst  
📍 Charlotte, NC  
🔗 [LinkedIn](https://linkedin.com/in/madhavi-indukuri) | [GitHub](https://github.com/MadhaviIndukuri)
