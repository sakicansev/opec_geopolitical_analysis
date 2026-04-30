# Cross-Asset Geopolitical Shock Analysis: UAE–OPEC Exit (2026)

**Author:** Saki Cansev  
**GitHub:** github.com/sakicansev  
**Tools:** Python, pandas, matplotlib, scipy, SQLite  
**Status:** In Progress

---

## Overview

On April 28, 2026, the United Arab Emirates announced its withdrawal from OPEC and OPEC+,
effective May 1 — ending nearly 60 years of membership. The announcement came amid an
active US-Israel war on Iran, a near-closure of the Strait of Hormuz, and Brent crude
trading above $110/barrel.

This project examines how three asset classes responded to this geopolitical shock:

- **Brent Crude Oil** — the directly affected commodity
- **Bitcoin (BTC-USD)** — a decentralised, geopolitical-risk-sensitive asset
- **Gold (GC=F)** — the traditional safe-haven benchmark

The analysis applies an event study framework to measure abnormal returns, volatility
shifts, and correlation changes around the key event window.

---

## Research Questions

1. Did Brent, BTC, and Gold exhibit abnormal returns around the UAE exit announcement?
2. How did cross-asset correlations change before vs. during the shock period?
3. Did volatility (rolling std) spike simultaneously across all three assets?
4. Which asset reacted fastest and most strongly to the geopolitical event?

---

## Key Event Timeline

| Date       | Event                                                  |
|------------|--------------------------------------------------------|
| 2025-10-01 | US-Israel military operations against Iran begin       |
| 2026-02-01 | Strait of Hormuz near-closure, Brent peaks at ~$119    |
| 2026-04-27 | UAE diplomat publicly criticises GCC response to Iran  |
| 2026-04-28 | UAE announces OPEC exit, effective May 1               |
| 2026-05-01 | UAE formally leaves OPEC and OPEC+                     |

---

## Project Structure

```
opec_geopolitical_analysis/
│
├── data/                    # Raw CSV exports from yfinance
├── scripts/
│   ├── 01_fetch_data.py     # Download price data via yfinance
│   ├── 02_store_to_db.py    # Load CSVs into SQLite database
│   ├── 03_analysis.py       # Returns, volatility, correlations
│   └── 04_visualise.py      # Generate charts
├── sql/
│   └── schema.sql           # SQLite table definitions
├── outputs/
│   ├── charts/              # PNG chart exports
│   └── tables/              # CSV summary tables
├── notebooks/               # Optional: Jupyter exploration
├── requirements.txt
└── README.md
```

---

## Methodology

### Event Study Window
- **Estimation window:** 180 days before the event (baseline behaviour)
- **Event window:** 30 days centred on April 28, 2026
- **Post-event window:** 30 days after May 1, 2026

### Metrics
- **Daily log returns** — `ln(P_t / P_{t-1})`
- **Abnormal return** — actual return minus mean return from estimation window
- **Cumulative Abnormal Return (CAR)** — sum of abnormal returns over event window
- **Rolling volatility** — 14-day rolling standard deviation of log returns
- **Pearson correlation matrix** — pre-shock vs. shock period

---

## Setup

```bash
git clone https://github.com/sakicansev/opec_geopolitical_analysis
cd opec_geopolitical_analysis
pip install -r requirements.txt
```

Run in order:
```bash
python scripts/01_fetch_data.py
python scripts/02_store_to_db.py
python scripts/03_analysis.py
python scripts/04_visualise.py
```

---

## Requirements

See `requirements.txt`:
- yfinance
- pandas
- matplotlib
- scipy
- sqlite3 (built-in)

---

## Results Summary

*(To be updated as analysis is completed)*

---

## Context & Motivation

This project is part of a broader portfolio focused on crypto and commodity market
responses to geopolitical events. It builds on a prior analysis of Bitcoin and Ethereum
price behaviour during conflict events (see: btc_eth_conflict_analysis).

The UAE-OPEC case is particularly interesting because it involves a simultaneous:
- Supply coordination shock (OPEC structural weakening)
- Geopolitical risk shock (Iran war, Hormuz closure)
- Institutional credibility shock (cartel fragmentation risk)

Each of these forces pull asset prices in different directions, making cross-asset
comparison analytically rich.
