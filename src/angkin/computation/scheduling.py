"""Schedule generation and crew size calculation."""

from __future__ import annotations

import math

from angkin.config import PH_HOURS_PER_DAY


TRADE_SEQUENCE = ["Civil / Structural", "Architectural / Finishing"]

# Within-trade activity ordering hints (lower = earlier)
ACTIVITY_ORDER: dict[str, int] = {
    "excavation": 1,
    "backfill": 2,
    "gravel": 3,
    "footing": 4,
    "foundation": 5,
    "column": 6,
    "beam": 7,
    "slab": 8,
    "rebar": 5,
    "formwork": 5,
    "structural steel": 9,
    "chb": 10,
    "wall": 11,
    "plaster": 12,
    "roofing": 13,
    "waterproof": 14,
    "ceiling": 15,
    "tiling": 16,
    "tile": 16,
    "door": 17,
    "window": 17,
    "painting": 18,
    "paint": 18,
}


def generate_schedule(
    computed_items: list[dict],
    target_crew_size: int = 8,
) -> list[dict]:
    """Generate a construction schedule from computed manhour items.

    Args:
        computed_items: Output from manhours.compute_manhours().
        target_crew_size: Desired crew size per activity (PM can adjust).

    Returns:
        List of schedule items with start_day, end_day, duration_days, crew_size.
    """
    schedule: list[dict] = []
    current_day = 1

    for trade in TRADE_SEQUENCE:
        trade_items = [
            it for it in computed_items
            if it["trade"] == trade and it["adjusted_manhours"] > 0
        ]
        trade_items.sort(key=lambda it: _activity_priority(it["work_item"]))

        for item in trade_items:
            crew = min(target_crew_size, max(1, _ideal_crew(item["adjusted_manhours"])))
            duration = math.ceil(
                item["adjusted_manhours"] / (crew * PH_HOURS_PER_DAY)
            )
            duration = max(duration, 1)

            schedule.append({
                "scope_item_id": item.get("id"),
                "trade": trade,
                "work_item": item["work_item"],
                "adjusted_manhours": item["adjusted_manhours"],
                "crew_size": crew,
                "duration_days": duration,
                "start_day": current_day,
                "end_day": current_day + duration - 1,
                "depends_on": "",
            })
            current_day += duration

    _set_dependencies(schedule)
    return schedule


def _activity_priority(work_item: str) -> int:
    text = work_item.lower()
    for keyword, priority in ACTIVITY_ORDER.items():
        if keyword in text:
            return priority
    return 50


def _ideal_crew(manhours: float) -> int:
    """Suggest a reasonable crew size based on manhour volume."""
    if manhours <= 16:
        return 2
    if manhours <= 80:
        return 4
    if manhours <= 320:
        return 8
    return 12


def _set_dependencies(schedule: list[dict]) -> None:
    """Simple sequential dependency: each activity depends on the previous one."""
    for i in range(1, len(schedule)):
        schedule[i]["depends_on"] = str(i - 1)


def compute_manpower_loading(schedule: list[dict]) -> list[dict]:
    """Compute weekly crew counts per trade.

    Returns list of {week, trade, crew_count} dicts.
    """
    if not schedule:
        return []

    max_day = max(it["end_day"] for it in schedule)
    weeks: list[dict] = []

    week_num = 1
    day = 1
    while day <= max_day:
        week_end = day + 5  # 6-day work week
        for trade in TRADE_SEQUENCE:
            crew = sum(
                it["crew_size"]
                for it in schedule
                if it["trade"] == trade
                and it["start_day"] <= week_end
                and it["end_day"] >= day
            )
            weeks.append({"week": week_num, "trade": trade, "crew_count": crew})
        week_num += 1
        day = week_end + 1

    return weeks
