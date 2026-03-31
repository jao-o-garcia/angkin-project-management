"""SQLite schema definition and initialization."""

import sqlite3
from pathlib import Path

BASE_SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    description TEXT DEFAULT '',
    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS drawing_pages (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id   INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    page_number  INTEGER NOT NULL,
    drawing_type TEXT DEFAULT 'Unknown',
    image_data   BLOB,
    created_at   TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS scope_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    scope       TEXT NOT NULL DEFAULT '',
    trade       TEXT NOT NULL,
    work_item   TEXT NOT NULL,
    quantity    REAL NOT NULL DEFAULT 0,
    unit        TEXT NOT NULL DEFAULT '',
    basis       TEXT DEFAULT '',
    source      TEXT DEFAULT 'vision',
    confirmed   INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS scope_locks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    scope       TEXT NOT NULL,
    locked_at   TEXT DEFAULT (datetime('now')),
    UNIQUE(project_id, scope)
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
    depends_on  TEXT DEFAULT ''
);
"""

# Additive migrations for existing databases
MIGRATIONS = [
    # (table, column_name, column_definition)
    ("scope_items", "scope", "TEXT NOT NULL DEFAULT ''"),
    ("scope_items", "basis", "TEXT DEFAULT ''"),
]


def init_db(db_path: Path) -> sqlite3.Connection:
    """Create database and tables if they don't exist, apply migrations."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(BASE_SCHEMA)

    for table, column, definition in MIGRATIONS:
        existing_cols = [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]
        if column not in existing_cols:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    conn.commit()
    return conn
