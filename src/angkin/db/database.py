"""Database connection management and CRUD operations."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Any

from angkin.config import DB_PATH
from angkin.db.models import init_db


def get_connection() -> sqlite3.Connection:
    return init_db(DB_PATH)


@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

def create_project(name: str, description: str = "") -> int:
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO projects (name, description) VALUES (?, ?)",
            (name, description),
        )
        return cur.lastrowid


def get_project(project_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        return dict(row) if row else None


def list_projects() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM projects ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Scope Items
# ---------------------------------------------------------------------------

def insert_scope_items(project_id: int, items: list[dict]) -> None:
    with get_db() as conn:
        conn.executemany(
            """INSERT INTO scope_items
               (project_id, trade, work_item, quantity, unit, source)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [
                (
                    project_id,
                    it["trade"],
                    it["work_item"],
                    it["quantity"],
                    it["unit"],
                    it.get("source", "parsed"),
                )
                for it in items
            ],
        )


def get_scope_items(project_id: int) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM scope_items WHERE project_id = ? ORDER BY id",
            (project_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def update_scope_items(items: list[dict]) -> None:
    """Bulk-update scope items from the PM review table."""
    with get_db() as conn:
        for it in items:
            conn.execute(
                """UPDATE scope_items
                   SET trade = ?, work_item = ?, quantity = ?, unit = ?, confirmed = 1
                   WHERE id = ?""",
                (it["trade"], it["work_item"], it["quantity"], it["unit"], it["id"]),
            )


def delete_scope_item(item_id: int) -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM scope_items WHERE id = ?", (item_id,))


# ---------------------------------------------------------------------------
# Efficiency Rates
# ---------------------------------------------------------------------------

def upsert_efficiency_rate(trade: str, rate: float, source_file: str = "", notes: str = "") -> None:
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM efficiency_rates WHERE trade = ?", (trade,)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE efficiency_rates SET rate = ?, source_file = ?, notes = ? WHERE id = ?",
                (rate, source_file, notes, existing["id"]),
            )
        else:
            conn.execute(
                "INSERT INTO efficiency_rates (trade, rate, source_file, notes) VALUES (?, ?, ?, ?)",
                (trade, rate, source_file, notes),
            )


def get_efficiency_rates() -> dict[str, float]:
    """Return {trade: rate} mapping."""
    with get_db() as conn:
        rows = conn.execute("SELECT trade, rate FROM efficiency_rates").fetchall()
        return {r["trade"]: r["rate"] for r in rows}


# ---------------------------------------------------------------------------
# Manhour Norms
# ---------------------------------------------------------------------------

def get_manhour_norms() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM manhour_norms ORDER BY trade, work_item").fetchall()
        return [dict(r) for r in rows]


def seed_default_norms(norms: list[dict]) -> None:
    """Insert default PH labor norms if table is empty."""
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) as c FROM manhour_norms").fetchone()["c"]
        if count > 0:
            return
        conn.executemany(
            """INSERT INTO manhour_norms
               (trade, work_item, unit, manhours_per_unit, labor_rate_per_hour, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [
                (n["trade"], n["work_item"], n["unit"],
                 n["manhours_per_unit"], n.get("labor_rate_per_hour", 0),
                 n.get("notes", ""))
                for n in norms
            ],
        )


# ---------------------------------------------------------------------------
# Schedule Items
# ---------------------------------------------------------------------------

def save_schedule(project_id: int, items: list[dict]) -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM schedule_items WHERE project_id = ?", (project_id,))
        conn.executemany(
            """INSERT INTO schedule_items
               (project_id, scope_item_id, trade, work_item,
                duration_days, crew_size, adjusted_manhours, start_day, end_day, depends_on)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    project_id,
                    it.get("scope_item_id"),
                    it["trade"],
                    it["work_item"],
                    it["duration_days"],
                    it["crew_size"],
                    it["adjusted_manhours"],
                    it.get("start_day", 0),
                    it.get("end_day", 0),
                    it.get("depends_on", ""),
                )
                for it in items
            ],
        )


def get_schedule(project_id: int) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM schedule_items WHERE project_id = ? ORDER BY start_day, id",
            (project_id,),
        ).fetchall()
        return [dict(r) for r in rows]
