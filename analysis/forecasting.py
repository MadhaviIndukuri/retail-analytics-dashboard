"""
Monthly Revenue Forecasting
Uses linear regression + moving average for short-term sales forecasting
"""

import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
import os

DB_PATH = "data/retail.db"
os.makedirs("data/outputs", exist_ok=True)


def load_monthly_revenue():
    conn = sqlite3.connect(DB_PATH)
    txn  = pd.read_sql(
        "SELECT transaction_date, revenue FROM transactions",
        conn, parse_dates=["transaction_date"]
    )
    conn.close()

    monthly = (
        txn.set_index("transaction_date")
        .resample("M")["revenue"]
        .sum()
        .reset_index()
    )
    monthly.columns = ["month", "revenue"]
    return monthly


def build_features(monthly: pd.DataFrame) -> pd.DataFrame:
    df = monthly.copy()
    df["month_num"]   = np.arange(len(df))
    df["month_of_yr"] = df["month"].dt.month
    df["lag_1"]       = df["revenue"].shift(1)
    df["lag_2"]       = df["revenue"].shift(2)
    df["lag_3"]       = df["revenue"].shift(3)
    df["rolling_3"]   = df["revenue"].rolling(3).mean()
    return df.dropna()


def train_forecast(monthly: pd.DataFrame):
    df    = build_features(monthly)
    TRAIN = int(len(df) * 0.8)

    features = ["month_num", "month_of_yr", "lag_1", "lag_2", "lag_3", "rolling_3"]
    X_train, y_train = df[features].iloc[:TRAIN], df["revenue"].iloc[:TRAIN]
    X_test,  y_test  = df[features].iloc[TRAIN:], df["revenue"].iloc[TRAIN:]

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae    = mean_absolute_error(y_test, y_pred)
    r2     = r2_score(y_test, y_pred)

    print(f"Model MAE: ${mae:,.0f}  |  R²: {r2:.3f}")

    # Forecast next 6 months
    last_row  = df.iloc[-1]
    forecasts = []
    rev_hist  = list(df["revenue"].values)

    for i in range(1, 7):
        next_month_num = last_row["month_num"] + i
        next_month_dt  = monthly["month"].max() + pd.DateOffset(months=i)
        lag1 = rev_hist[-1]
        lag2 = rev_hist[-2]
        lag3 = rev_hist[-3]
        roll = np.mean(rev_hist[-3:])
        pred = model.predict([[next_month_num, next_month_dt.month, lag1, lag2, lag3, roll]])[0]
        forecasts.append({"month": next_month_dt, "revenue": pred, "type": "Forecast"})
        rev_hist.append(pred)

    forecast_df = pd.DataFrame(forecasts)
    return df, forecast_df, y_test, y_pred, r2, mae


def plot_forecast(monthly, df, forecast_df, y_test, y_pred):
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle("Revenue Forecasting Analysis", fontsize=15, fontweight="bold")

    # Plot 1: Full history + forecast
    axes[0].plot(monthly["month"], monthly["revenue"] / 1e6,
                 label="Actual", color="#2c3e50", linewidth=2)
    axes[0].plot(forecast_df["month"], forecast_df["revenue"] / 1e6,
                 label="6-Month Forecast", color="#e74c3c",
                 linewidth=2, linestyle="--", marker="o")
    axes[0].fill_between(
        forecast_df["month"],
        forecast_df["revenue"] * 0.92 / 1e6,
        forecast_df["revenue"] * 1.08 / 1e6,
        alpha=0.2, color="#e74c3c", label="Confidence Band (±8%)"
    )
    axes[0].set_title("Monthly Revenue + 6-Month Forecast")
    axes[0].set_ylabel("Revenue ($ millions)")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    # Plot 2: Actual vs Predicted on test set
    test_months = df["month"].iloc[int(len(df) * 0.8):]
    axes[1].plot(test_months.values, y_test.values / 1e6,
                 label="Actual", color="#2c3e50", linewidth=2)
    axes[1].plot(test_months.values, y_pred / 1e6,
                 label="Predicted", color="#3498db", linewidth=2, linestyle="--")
    axes[1].set_title("Model Validation: Actual vs Predicted (Test Set)")
    axes[1].set_ylabel("Revenue ($ millions)")
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("data/outputs/revenue_forecast.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Forecast chart saved → data/outputs/revenue_forecast.png")
    return forecast_df


if __name__ == "__main__":
    print("Loading monthly revenue data...")
    monthly = load_monthly_revenue()

    print("Training forecast model...")
    df, forecast_df, y_test, y_pred, r2, mae = train_forecast(monthly)
    plot_forecast(monthly, df, forecast_df, y_test, y_pred)

    forecast_df.to_csv("data/outputs/revenue_forecast.csv", index=False)
    print("\n📈 6-Month Revenue Forecast:")
    print(forecast_df[["month", "revenue"]].to_string(index=False))
