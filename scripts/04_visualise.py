# scripts/04_visualise.py
# Generates 4 charts and saves them as PNGs to outputs/charts/

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os

# ── Configuration ─────────────────────────────────────────────────────────────

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH    = os.path.join(BASE_DIR, "data", "geopolitical_shock.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "charts")

EVENT_DATE = "2026-04-28"

COLORS = {
    "BRENT": "#E8A838",
    "BTC":   "#4A90D9",
    "GOLD":  "#A8A8A8",
}

STYLE = {
    "figure.facecolor": "#0F1117",
    "axes.facecolor":   "#1A1D27",
    "axes.edgecolor":   "#2E3140",
    "axes.labelcolor":  "#C8CBD8",
    "text.color":       "#C8CBD8",
    "xtick.color":      "#7A7D8C",
    "ytick.color":      "#7A7D8C",
    "grid.color":       "#2E3140",
    "grid.linestyle":   "--",
    "grid.alpha":       0.6,
    "legend.facecolor": "#1A1D27",
    "legend.edgecolor": "#2E3140",
}

# ── Helper ────────────────────────────────────────────────────────────────────

def get_conn():
    return sqlite3.connect(DB_PATH)

# ── Chart 1: Normalised Price Index ───────────────────────────────────────────

def chart_normalised_prices(conn):
    df = pd.read_sql(
        "SELECT asset, date, close FROM asset_prices ORDER BY asset, date",
        conn
    )
    df["date"] = pd.to_datetime(df["date"])
    pivot = df.pivot(index="date", columns="asset", values="close")
    normalised = pivot / pivot.iloc[0] * 100

    with plt.rc_context(STYLE):
        fig, ax = plt.subplots(figsize=(12, 5))
        for asset in ["BRENT", "BTC", "GOLD"]:
            if asset in normalised:
                series = normalised[asset].dropna()
                ax.plot(series.index, series,
                        label=asset, color=COLORS[asset], linewidth=1.8)

        ax.axvline(pd.to_datetime(EVENT_DATE), color="#FF5555",
                   linewidth=1.4, linestyle="--", label="UAE exit announced")
        ax.set_title("Normalised Price Index — Brent, BTC, Gold\n"
                     "(Base = 100 at Oct 1, 2025)", fontsize=13, pad=12)
        ax.set_ylabel("Index (Base = 100)")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=30)
        ax.legend()
        ax.grid(True)
        fig.tight_layout()
        path = os.path.join(OUTPUT_DIR, "01_normalised_prices.png")
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
    print(f"  Saved: {path}")

# ── Chart 2: Rolling Volatility ───────────────────────────────────────────────

def chart_rolling_volatility(conn):
    df = pd.read_sql(
        "SELECT asset, date, volatility_14d FROM rolling_volatility ORDER BY asset, date",
        conn
    )
    df["date"] = pd.to_datetime(df["date"])
    pivot = df.pivot(index="date", columns="asset", values="volatility_14d")

    with plt.rc_context(STYLE):
        fig, ax = plt.subplots(figsize=(12, 5))
        for asset in ["BRENT", "BTC", "GOLD"]:
            if asset in pivot:
                series = pivot[asset].dropna()
                ax.plot(series.index, series,
                        label=asset, color=COLORS[asset], linewidth=1.8)

        ax.axvline(pd.to_datetime(EVENT_DATE), color="#FF5555",
                   linewidth=1.4, linestyle="--", label="UAE exit announced")
        ax.set_title("14-Day Rolling Volatility — Brent, BTC, Gold\n"
                     "(Log Return Std Dev)", fontsize=13, pad=12)
        ax.set_ylabel("Volatility (σ)")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=30)
        ax.legend()
        ax.grid(True)
        fig.tight_layout()
        path = os.path.join(OUTPUT_DIR, "02_rolling_volatility.png")
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
    print(f"  Saved: {path}")

# ── Chart 3: Cumulative Abnormal Returns ──────────────────────────────────────

def chart_car(conn):
    df = pd.read_sql(
        "SELECT asset, date, cum_abnormal FROM abnormal_returns ORDER BY asset, date",
        conn
    )
    df["date"] = pd.to_datetime(df["date"])
    pivot = df.pivot(index="date", columns="asset", values="cum_abnormal")

    with plt.rc_context(STYLE):
        fig, ax = plt.subplots(figsize=(12, 5))
        for asset in ["BRENT", "BTC", "GOLD"]:
            if asset in pivot:
                series = pivot[asset].dropna()
                ax.plot(series.index, series,
                        label=asset, color=COLORS[asset], linewidth=2.0,
                        marker="o", markersize=3)

        ax.axhline(0, color="#555870", linewidth=1.0)
        ax.axvline(pd.to_datetime(EVENT_DATE), color="#FF5555",
                   linewidth=1.4, linestyle="--", label="UAE exit announced")
        ax.set_title("Cumulative Abnormal Returns — Event Window\n"
                     "(30 days before UAE announcement)", fontsize=13, pad=12)
        ax.set_ylabel("CAR (log return)")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.xticks(rotation=30)
        ax.legend()
        ax.grid(True)
        fig.tight_layout()
        path = os.path.join(OUTPUT_DIR, "03_cumulative_abnormal_returns.png")
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
    print(f"  Saved: {path}")

# ── Chart 4: Correlation Heatmaps ─────────────────────────────────────────────

def chart_correlations(conn):
    df = pd.read_sql(
        "SELECT period, asset_a, asset_b, pearson_r FROM correlation_summary",
        conn
    )

    periods    = ["pre_shock", "event_window", "post_event"]
    titles     = ["Pre-Shock\n(Oct '25 – Mar '26)",
                  "Event Window\n(Mar 29 – Apr 28 '26)",
                  "Post-Event\n(Apr 29 – May 29 '26)"]
    asset_list = ["BRENT", "BTC", "GOLD"]

    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        fig.subplots_adjust(right=0.88)
        fig.suptitle("Pearson Correlation Matrices by Period",
                     fontsize=13, y=1.02)

        for ax, period, title in zip(axes, periods, titles):
            period_df = df[df["period"] == period]
            matrix = pd.DataFrame(np.eye(3),
                                  index=asset_list, columns=asset_list)

            for _, row in period_df.iterrows():
                matrix.loc[row["asset_a"], row["asset_b"]] = row["pearson_r"]
                matrix.loc[row["asset_b"], row["asset_a"]] = row["pearson_r"]

            im = ax.imshow(matrix.values, cmap="RdYlGn", vmin=-1, vmax=1)
            ax.set_xticks(range(3))
            ax.set_yticks(range(3))
            ax.set_xticklabels(asset_list, fontsize=9)
            ax.set_yticklabels(asset_list, fontsize=9)
            ax.set_title(title, fontsize=10, pad=8)

            for i in range(3):
                for j in range(3):
                    ax.text(j, i, f"{matrix.values[i, j]:.2f}",
                            ha="center", va="center", fontsize=10,
                            color="black")

        cbar_ax = fig.add_axes([0.91, 0.15, 0.02, 0.7])
        fig.colorbar(im, cax=cbar_ax, label="Pearson r")

        path = os.path.join(OUTPUT_DIR, "04_correlation_heatmaps.png")
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
    print(f"  Saved: {path}")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = get_conn()

    print("Generating charts...")
    chart_normalised_prices(conn)
    chart_rolling_volatility(conn)
    chart_car(conn)
    chart_correlations(conn)

    conn.close()
    print("\nAll charts saved to outputs/charts/")


if __name__ == "__main__":
    main()