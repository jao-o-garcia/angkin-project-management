"""SQLite schema definition and initialization."""

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    description TEXT DEFAULT '',
    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS scope_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    trade       TEXT NOT NULL,
    work_item   TEXT NOT NULL,
    quantity    REAL NOT NULL DEFAULT 0,
    unit        TEXT NOT NULL DEFAULT '',
    source      TEXT DEFAULT 'parsed',  -- 'parsed' | 'llm' | 'manual'
    confirmed   INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS efficiency_rates (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    trade       TEXT NOT NULL,
    rate        REAL NOT NULL DEFAULT 0.85,
    source_file TEXT DEFAULT '',
    notes       TEXT DEFAULT '',
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS manhour_norms (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    trade       TEXT NOT NULL,
    work_item   TEXT NOT NULL,
    unit        TEXT NOT NULL,
    manhours_per_unit REAL NOT NULL,
    labor_rate_per_hour REAL NOT NULL DEFAULT 0,
    notes       TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS schedule_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    scope_item_id INTEGER REFERENCES scope_items(id),
    trade       TEXT NOT NULL,
    work_item   TEXT NOT NULL,
    duration_days REAL NOT NULL DEFAULT 0,
    crew_size   INTEGER NOT NULL DEFAULT 1,
    adjusted_manhours REAL NOT NULL DEFAULT 0,
    start_day   INTEGER DEFAULT 0,
    end_day     INTEGER DEFAULT 0,
    depends_on  TEXT DEFAULT ''  -- comma-separated schedule_item ids
);
"""


def init_db(db_path: Path) -> sqlite3.Connection:
    """Create database and tables if they don't exist."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA)
    conn.commit()
    return conn
