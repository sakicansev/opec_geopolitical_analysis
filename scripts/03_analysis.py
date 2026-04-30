# scripts/03_analysis.py
# Computes and stores:
# - Daily log returns
# - 14-day rolling volatility
# - Abnormal returns (event study)
# - Cumulative Abnormal Returns (CAR)
# - Pearson correlation matrices per period

import sqlite3
import pandas as pd
import numpy as np
import os

# Configuration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "geopolitical_shock.db")
ASSETS = ["BRENT", "BTC", "GOLD"]

# Event stidy windows (dates are inclusive)
EVENT_DATE          = "2026-04-28"      #UAE OPEC exit announcement
ESTIMATION_START    = "2025-10-01"
ESTIMATION_END      = "2026-03-28"      # 30 dats before event
EVENT_WIN_START     = "2026-03-29"
EVENT_WIN_END       = "2026-04-28"
POST_START          = "2026-04-29"
POST_END            = "2026-05-29"

# Helpers

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def load_prices(conn):
    df = pd.read_sql(
        "SELECT asset, date, close FROM asset_prices ORDER BY asset, date",
        conn
    )
    df["date"] = pd.to_datetime(df["date"])
    return df

def compute_log_returns(df):
    """Add log_return column grouped by asset."""
    df = df.sort_values(["asset","date"]).copy()
    df["log_return"] = df.groupby("asset")["close"].transform(
        lambda x: np.log(x / x.shift(1))
    )
    return df.dropna(subset=["log_return"])

def store_log_returns(conn, df):
    conn.execute("DELETE FROM daily_returns")
    for _, row in df.iterrows():
        conn.execute(
            "INSERT OR REPLACE INTO daily_returns (asset, date, log_return) VALUES (?, ?, ?)",
            (row["asset"], row["date"].strftime("%Y-%m-%d"), row["log_return"])
        )
    conn.commit()
    print(f"  Stored {len(df)} log return rows")

def compute_rolling_volatility(df, window=14):
    df = df.sort_values(["asset", "date"]).copy()
    df["volatility_14d"] = df.groupby("asset")["log_return"].transform(
        lambda x: x.rolling(window).std()
    )
    return df.dropna(subset=["volatility_14d"])

def store_rolling_volatility(conn, df):
    conn.execute("DELETE FROM rolling_volatility")
    for _, row in df.iterrows():
        conn.execute(
            "INSERT OR REPLACE INTO rolling_volatility (asset, date, volatility_14d) Values (?, ?, ?)",
            (row["asset"], row["date"].strftime("%Y-%m-%d"), row["volatility_14d"])
        )
    conn.commit()
    print(f"  Stored {len(df)} volatilty rows")


def compute_abnormal_returns(df):
    """
    For each asset: 
        expected_return = mean log return in the estimation window
        abnormal_return = actual - ecpected (in event window)
        cum_abnormal    = cumulative sum from event window start
    """
    results = []
    
    for asset in ASSETS:
        asset_df = df[df["asset"] == asset].set_index("date").sort_index()

        estimation  = asset_df.loc[ESTIMATION_START:ESTIMATION_END, "log_return"]
        expected    = estimation.mean()

        event_df = asset_df.loc[EVENT_WIN_START:EVENT_WIN_END, "log_return"]

        cum = 0.0
        for date, actual in event_df.items():
            ar = actual - expected
            cum += ar
            results.append({
                "asset":            asset,
                "date":             date.strftime("%Y-%m-%d"),
                "actual_return":    actual,
                "expected_return":  expected,
                "abnormal_return":  ar,
                "cum_abnormal":     cum,
            })

    return pd.DataFrame(results)

def store_abnormal_returns(conn, df):
    conn.execute("DELETE FROM abnormal_returns")
    for _, row in df.iterrows():
        conn.execute(
            """
            INSERT OR REPLACE INTO abnormal_returns
                (asset, date, actual_return, expected_return, abnormal_return, cum_abnormal)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                row["asset"], row["date"],
                row["actual_return"], row["expected_return"], 
                row["abnormal_return"], row["cum_abnormal"], 
            )
        )
    conn.commit()
    print(f"  Stored {len(df)} abnormal return rows")

def compute_correlations(df):
    """
    Compute Pearson correlation matrices for three periods:
      - pre_shock:      estimation window
      - event_window:   30 days before announcement
      - post_event:     30 days after formal exit
    Returns a flat list of (period, asset_a, asset_b, pearson_r) tuples.
    """
    pivot = df.pivot(index="date", columns="asset", values="log_return")
    pivot.index = pd.to_datetime(pivot.index)
    
    periods = {
        "pre_shock":    (ESTIMATION_START, ESTIMATION_END),
        "event_window": (EVENT_WIN_START,  EVENT_WIN_END),
        "post_event":   (POST_START,       POST_END),
    }

    results = []
    for period, (start, end) in periods.items():
        window  = pivot.loc[start:end]
        corr    = window.corr(method="pearson")

        for asset_a in corr.columns:
            for asset_b in corr.columns:
                if asset_a < asset_b :          # store inly upper triangle
                    results.append({
                        "period": period,
                        "asset_a": asset_a,
                        "asset_b": asset_b,
                        "pearson_r": round(corr.loc[asset_a, asset_b], 4),
                    })

    return pd.DataFrame(results)

def store_correlations(conn, df):
    conn.execute("DELETE FROM correlation_summary")
    for _, row in df.iterrows():
        if pd.isna(row["pearson_r"]):
            continue
        conn.execute(
            """
            INSERT INTO correlation_summary (period, asset_a, asset_b, pearson_r)
            VALUES (?, ?, ?, ?)
            """,
            (row["period"], row["asset_a"], row["asset_b"], row["pearson_r"])
        )
    conn.commit()
    print(f"  Stored {len(df)} correlation rows")

def print_summary(conn):
    print("\n-- Cumulative Abnormal Returns (event window) --")
    cursor = conn.execute(
        """
        SELECT asset, date, cum_abnormal
        FROM abnormal_returns
        WHERE date = (SELECT MAX(date) FROM abnormal_returns WHERE asset = abnormal_returns.asset)
        ORDER BY asset
        """
    )
    for row in cursor.fetchall():
        print(f"  {row[0]}: CAR = {row[2]:.4f}")

    print("\n-- Correlation Summary --")
    cursor = conn.execute(
        "SELECT period, asset_a, asset_b, pearson_r FROM correlation_summary ORDER BY period, asset_a"
    )   
    for row in cursor.fetchall():
        print(f"  [{row[0]}] {row[1]} vs {row[2]}: r = {row[3]}")


# Main

def main():
    conn = get_connection()

    print("Loading prices...")
    prices = load_prices(conn)

    print("Computing log returns...")
    returns_df = compute_log_returns(prices)
    store_log_returns(conn, returns_df)

    print("Computing rolling volatility (14 day)...")
    vol_df = compute_rolling_volatility(returns_df)
    store_rolling_volatility(conn, vol_df)

    print("Computing abnormal returns...")
    ar_df = compute_abnormal_returns(returns_df)
    store_abnormal_returns(conn, ar_df)

    print("Computing correlatiosn...")
    corr_df = compute_correlations(returns_df)
    store_correlations(conn, corr_df)

    print_summary(conn)
    conn.close()
    print("\nAnalysis complete.")

if __name__ == "__main__":
    main()
