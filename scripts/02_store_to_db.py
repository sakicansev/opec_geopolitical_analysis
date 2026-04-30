# scripts/02_store_to_db.py
# Reads the CSV files produced by 01_fetching_data.py and loads them
# into the SQLite database, applying the schema from sql/schema.sql

import sqlite3
import pandas as pd
import os
# Configuration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SCHEMA_SQL = os.path.join(BASE_DIR, "sql", "schema.sql")
DB_PATH = os.path.join(BASE_DIR, "data", "geopolitical_shock.db")

ASSETS = ["BRENT", "BTC", "GOLD"]

# Helpers


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def apply_schema(conn):
    with open(SCHEMA_SQL, "r") as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()
    print("Schema applied.")


def load_prices(conn, asset):
    csv_path = os.path.join(DATA_DIR, f"{asset.lower()}_prices.csv")

    if not os.path.exists(csv_path):
        print(f"  WARNING: {csv_path} not found. Run 01_fetcch_data.py first.")
        return

    df = pd.read_csv(csv_path)

    rows_inserted = 0
    rows_skipped = 0

    for _, row in df.iterrows():
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO asset_prices
                    (asset, ticker, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                (
                    row["asset"], row["ticker"], row["date"],
                    row.get("open"), row.get("high"),
                    row.get("low"), row.get("close"),
                    row.get("volume"),
                )
            )
            if conn.execute("SELECT changes()").fetchone()[0]:
                rows_inserted += 1
            else:
                rows_skipped += 1
        except Exception as e:
            print(f"  ERROR inserting row {row['date']}: {e}")

    conn.commit()
    print(f"  {asset}: {rows_inserted} insterted, {rows_skipped} skipped")


# Main

def main():
    conn = get_connection()
    apply_schema(conn)

    print("\nLoading price data into database...")
    for asset in ASSETS:
        load_prices(conn, asset)

    print("\nRow counts per asset:")
    cursor = conn.execute(
        "SELECT asset, COUNT(*) FROM asset_prices GROUP BY asset"
    )
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} rows")

    conn.close()
    print(f"\nDatabase ready at: {DB_PATH}")


if __name__ == "__main__":
    main()
