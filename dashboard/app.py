"""
Retail Sales & Customer Intelligence Dashboard
Streamlit interactive dashboard — run with: streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, sys

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = "data/retail.db"

# ── Data Loader ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading data...")
def load_data():
    conn = sqlite3.connect(DB_PATH)
    txn  = pd.read_sql("SELECT * FROM transactions", conn, parse_dates=["transaction_date"])
    cust = pd.read_sql("SELECT * FROM customers",    conn)
    prod = pd.read_sql("SELECT * FROM products",     conn)
    conn.close()
    txn = txn.merge(cust[["customer_id","state","city","segment"]], on="customer_id", how="left")
    txn = txn.merge(prod[["product_id","category","subcategory"]], on="product_id",  how="left")
    return txn, cust, prod


# ── RFM ───────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def compute_rfm(_txn):
    snapshot = _txn["transaction_date"].max() + pd.Timedelta(days=1)
    rfm = _txn.groupby("customer_id").agg(
        recency   = ("transaction_date", lambda x: (snapshot - x.max()).days),
        frequency = ("transaction_id",   "count"),
        monetary  = ("revenue",          "sum"),
    ).reset_index()
    rfm["r_score"] = pd.qcut(rfm["recency"],   5, labels=[5,4,3,2,1], duplicates="drop").astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"], 5, labels=[1,2,3,4,5], duplicates="drop").astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"],  5, labels=[1,2,3,4,5], duplicates="drop").astype(int)
    rfm["rfm_score"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]
    def seg(s):
        if s >= 12: return "Champions"
        if s >= 9:  return "Loyal Customers"
        if s >= 6:  return "At Risk"
        return "Lost"
    rfm["segment"] = rfm["rfm_score"].apply(seg)
    return rfm


# ── Sidebar ───────────────────────────────────────────────────────────────────
def sidebar_filters(txn):
    st.sidebar.title("🔍 Filters")

    years = sorted(txn["transaction_date"].dt.year.unique())
    sel_years = st.sidebar.multiselect("Year", years, default=years)

    channels = txn["channel"].unique().tolist()
    sel_chan  = st.sidebar.multiselect("Channel", channels, default=channels)

    cats = txn["category"].unique().tolist()
    sel_cat = st.sidebar.multiselect("Category", cats, default=cats)

    segs = txn["segment"].unique().tolist()
    sel_seg = st.sidebar.multiselect("Customer Segment", segs, default=segs)

    mask = (
        txn["transaction_date"].dt.year.isin(sel_years) &
        txn["channel"].isin(sel_chan) &
        txn["category"].isin(sel_cat) &
        txn["segment"].isin(sel_seg)
    )
    return txn[mask]


# ── KPI Cards ─────────────────────────────────────────────────────────────────
def show_kpis(txn):
    total_rev   = txn["revenue"].sum()
    total_ord   = len(txn)
    aov         = txn["revenue"].mean()
    uniq_cust   = txn["customer_id"].nunique()
    total_profit= txn["gross_profit"].sum()
    margin      = total_profit / total_rev * 100 if total_rev else 0
    repeat_rate = txn.groupby("customer_id")["transaction_id"].count()
    repeat_pct  = (repeat_rate > 1).sum() / len(repeat_rate) * 100

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    c1.metric("💰 Total Revenue",   f"${total_rev/1e6:.1f}M")
    c2.metric("🛒 Total Orders",    f"{total_ord:,}")
    c3.metric("📦 Avg Order Value", f"${aov:.2f}")
    c4.metric("👥 Unique Customers",f"{uniq_cust:,}")
    c5.metric("📈 Gross Profit",    f"${total_profit/1e6:.1f}M")
    c6.metric("🎯 Gross Margin",    f"{margin:.1f}%")
    c7.metric("🔁 Repeat Rate",     f"{repeat_pct:.1f}%")


# ── Revenue Trend ─────────────────────────────────────────────────────────────
def revenue_trend(txn):
    monthly = (
        txn.set_index("transaction_date")
        .resample("ME")[["revenue","gross_profit"]]
        .sum()
        .reset_index()
    )
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=monthly["transaction_date"], y=monthly["revenue"],
        name="Revenue", marker_color="#3498db", opacity=0.8
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=monthly["transaction_date"], y=monthly["gross_profit"],
        name="Gross Profit", line=dict(color="#e74c3c", width=2)
    ), secondary_y=True)
    fig.update_layout(
        title="Monthly Revenue & Gross Profit Trend",
        hovermode="x unified", height=380,
        legend=dict(orientation="h", y=1.1)
    )
    fig.update_yaxes(title_text="Revenue ($)", secondary_y=False)
    fig.update_yaxes(title_text="Gross Profit ($)", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)


# ── Category & Channel ─────────────────────────────────────────────────────────
def category_channel(txn):
    col1, col2 = st.columns(2)

    with col1:
        cat_rev = txn.groupby("category")["revenue"].sum().sort_values(ascending=True)
        fig = px.bar(
            cat_rev, orientation="h",
            title="Revenue by Category",
            labels={"value": "Revenue ($)", "index": "Category"},
            color=cat_rev.values,
            color_continuous_scale="Blues",
        )
        fig.update_layout(height=350, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        chan_rev = txn.groupby("channel").agg(
            revenue=("revenue","sum"),
            orders=("transaction_id","count")
        ).reset_index()
        fig = px.pie(
            chan_rev, values="revenue", names="channel",
            title="Revenue by Channel",
            color_discrete_sequence=["#3498db","#2ecc71","#e67e22"],
            hole=0.4,
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)


# ── Top Products ───────────────────────────────────────────────────────────────
def top_products(txn):
    top = (
        txn.groupby("product_id")
        .agg(revenue=("revenue","sum"), orders=("transaction_id","count"),
             margin=("gross_profit","sum"))
        .nlargest(15, "revenue")
        .reset_index()
    )
    top["margin_pct"] = (top["margin"] / top["revenue"] * 100).round(1)
    fig = px.bar(
        top, x="revenue", y="product_id", orientation="h",
        color="margin_pct", color_continuous_scale="RdYlGn",
        title="Top 15 Products by Revenue (color = Margin %)",
        labels={"revenue": "Revenue ($)", "product_id": "Product", "margin_pct": "Margin %"},
    )
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)


# ── Regional Map ───────────────────────────────────────────────────────────────
def regional_map(txn):
    state_rev = txn.groupby("state").agg(
        revenue=("revenue","sum"),
        orders=("transaction_id","count"),
        customers=("customer_id","nunique")
    ).reset_index()

    fig = px.choropleth(
        state_rev,
        locations="state",
        locationmode="USA-states",
        color="revenue",
        scope="usa",
        color_continuous_scale="Blues",
        title="Revenue by State",
        hover_data={"orders": True, "customers": True},
        labels={"revenue": "Revenue ($)"},
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


# ── RFM Dashboard ─────────────────────────────────────────────────────────────
def rfm_dashboard(txn):
    rfm = compute_rfm(txn)

    col1, col2 = st.columns(2)
    with col1:
        seg_cnt = rfm["segment"].value_counts().reset_index()
        seg_cnt.columns = ["segment", "count"]
        fig = px.pie(
            seg_cnt, values="count", names="segment",
            title="Customer Segments (Count)",
            color_discrete_sequence=["#2ecc71","#3498db","#e67e22","#e74c3c"],
            hole=0.4,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        seg_rev = rfm.groupby("segment")["monetary"].sum().reset_index()
        fig = px.bar(
            seg_rev.sort_values("monetary", ascending=False),
            x="segment", y="monetary",
            title="Revenue by Customer Segment",
            color="segment",
            color_discrete_sequence=["#2ecc71","#3498db","#e67e22","#e74c3c"],
            labels={"monetary": "Total Revenue ($)", "segment": "Segment"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Scatter: Recency vs Monetary
    rfm_sample = rfm.sample(min(2000, len(rfm)), random_state=42)
    fig = px.scatter(
        rfm_sample, x="recency", y="monetary",
        color="segment", size="frequency",
        title="RFM Scatter: Recency vs Revenue (size = Frequency)",
        labels={"recency": "Recency (days)", "monetary": "Total Revenue ($)"},
        color_discrete_sequence=["#2ecc71","#3498db","#e67e22","#e74c3c"],
        opacity=0.7,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Cohort Analysis ───────────────────────────────────────────────────────────
def cohort_heatmap(txn):
    t = txn.copy()
    t["order_month"] = t["transaction_date"].dt.to_period("M")
    first            = t.groupby("customer_id")["order_month"].min().rename("cohort_month")
    t                = t.join(first, on="customer_id")
    t["cohort_idx"]  = (t["order_month"] - t["cohort_month"]).apply(lambda x: x.n)

    cohort_pivot = (
        t.groupby(["cohort_month","cohort_idx"])["customer_id"]
        .nunique()
        .unstack()
    )
    sizes     = cohort_pivot.iloc[:,0]
    retention = cohort_pivot.divide(sizes, axis=0).round(3) * 100

    plot_data = retention.iloc[-18:, :12].astype(float)
    plot_data.index = plot_data.index.astype(str)

    fig = px.imshow(
        plot_data,
        color_continuous_scale="YlOrRd_r",
        title="Cohort Retention Rate (%) — Last 18 Cohorts",
        labels={"x": "Months Since First Purchase", "y": "Cohort", "color": "Retention %"},
        aspect="auto",
        text_auto=".0f",
    )
    fig.update_layout(height=550)
    st.plotly_chart(fig, use_container_width=True)


# ── Main App ───────────────────────────────────────────────────────────────────
def main():
    if not os.path.exists(DB_PATH):
        st.error("⚠️ Database not found. Please run `python data/generate_data.py` first.")
        st.stop()

    txn, cust, prod = load_data()
    filtered         = sidebar_filters(txn)

    st.title("🛍️ Retail Sales & Customer Intelligence Dashboard")
    st.caption(f"Analyzing {len(filtered):,} transactions | {filtered['customer_id'].nunique():,} customers | {filtered['transaction_date'].min().date()} → {filtered['transaction_date'].max().date()}")

    # ── KPIs
    st.subheader("📊 Key Performance Indicators")
    show_kpis(filtered)
    st.divider()

    # ── Trend
    st.subheader("📈 Revenue Trend")
    revenue_trend(filtered)
    st.divider()

    # ── Category & Channel
    st.subheader("🏷️ Category & Channel Performance")
    category_channel(filtered)
    st.divider()

    # ── Top Products
    st.subheader("🏆 Top Products")
    top_products(filtered)
    st.divider()

    # ── Regional
    st.subheader("🗺️ Regional Performance")
    regional_map(filtered)
    st.divider()

    # ── RFM
    st.subheader("🎯 RFM Customer Segmentation")
    rfm_dashboard(filtered)
    st.divider()

    # ── Cohort
    st.subheader("🔁 Cohort Retention Analysis")
    cohort_heatmap(filtered)

    st.sidebar.divider()
    st.sidebar.caption("Built by Madhavi Indukuri | Data Analyst Portfolio")


if __name__ == "__main__":
    main()
