-- schema.sql

CREATE TABLE IF NOT EXISTS asset_prices (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    asset   TEXT    NOT NULL,
    ticker  TEXT    NOT NULL,
    date    TEXT    NOT NULL,
    open    REAL,
    high    REAL,
    low     REAL,
    close   REAL    NOT NULL,
    volume  REAL,
    UNIQUE(asset, date)
);

CREATE TABLE IF NOT EXISTS daily_returns (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    asset      TEXT    NOT NULL,
    date       TEXT    NOT NULL,
    log_return REAL    NOT NULL,
    UNIQUE(asset, date)
);

CREATE TABLE IF NOT EXISTS rolling_volatility (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    asset          TEXT    NOT NULL,
    date           TEXT    NOT NULL,
    volatility_14d REAL,
    UNIQUE(asset, date)
);

CREATE TABLE IF NOT EXISTS abnormal_returns (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    asset           TEXT    NOT NULL,
    date            TEXT    NOT NULL,
    actual_return   REAL    NOT NULL,
    expected_return REAL    NOT NULL,
    abnormal_return REAL    NOT NULL,
    cum_abnormal    REAL,
    UNIQUE(asset, date)
);

CREATE TABLE IF NOT EXISTS correlation_summary (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    period      TEXT    NOT NULL,
    asset_a     TEXT    NOT NULL,
    asset_b     TEXT    NOT NULL,
    pearson_r   REAL    NOT NULL
);

CREATE TABLE IF NOT EXISTS event_timeline (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT    NOT NULL    UNIQUE,
    label       TEXT    NOT NULL,
    category    TEXT    NOT NULL
);

INSERT OR IGNORE INTO event_timeline (date, label, category) VALUES
('2025-10-01', 'US-Israel military operations on Iran begin', 'conflict'),
('2026-02-01', 'Strait of Hormuz near-closure, Brent ~$119', 'market'),
('2026-04-27', 'UAE diplomat publicly criticises GCC', 'opec'),
('2026-04-28', 'UAE announces OPEC exit effevtive May 1', 'opec'),
('2026-05-01', 'UAE formally leaved OPEC and OPEC+', 'opec');