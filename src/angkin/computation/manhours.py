"""Manhour computation engine."""

from __future__ import annotations

from angkin.config import DEFAULT_EFFICIENCY_RATE


def compute_manhours(
    scope_items: list[dict],
    norms: list[dict],
    efficiency_rates: dict[str, float],
) -> list[dict]:
    """Compute adjusted manhours for each scope item.

    Formula: adjusted_manhours = (quantity × manhours_per_unit) / efficiency_rate

    Returns list of dicts with original scope item data plus computed fields.
    """
    norm_lookup = _build_norm_lookup(norms)
    results: list[dict] = []

    for item in scope_items:
        key = _norm_key(item["trade"], item["work_item"])
        norm = norm_lookup.get(key)

        if norm is None:
            norm = _fuzzy_match_norm(item, norm_lookup)

        if norm is None:
            results.append({
                **item,
                "base_manhours": 0,
                "efficiency_rate": 0,
                "adjusted_manhours": 0,
                "labor_rate_per_hour": 0,
                "estimated_cost": 0,
                "norm_matched": False,
            })
            continue

        base_mh = item["quantity"] * norm["manhours_per_unit"]
        eff_rate = efficiency_rates.get(item["trade"], DEFAULT_EFFICIENCY_RATE)
        adjusted_mh = base_mh / eff_rate if eff_rate > 0 else base_mh
        labor_rate = norm.get("labor_rate_per_hour", 0)

        results.append({
            **item,
            "base_manhours": round(base_mh, 2),
            "efficiency_rate": eff_rate,
            "adjusted_manhours": round(adjusted_mh, 2),
            "labor_rate_per_hour": labor_rate,
            "estimated_cost": round(adjusted_mh * labor_rate, 2),
            "norm_matched": True,
        })

    return results


def _build_norm_lookup(norms: list[dict]) -> dict[str, dict]:
    lookup: dict[str, dict] = {}
    for n in norms:
        key = _norm_key(n["trade"], n["work_item"])
        lookup[key] = n
    return lookup


def _norm_key(trade: str, work_item: str) -> str:
    return f"{trade.lower().strip()}::{work_item.lower().strip()}"


def _fuzzy_match_norm(item: dict, norm_lookup: dict[str, dict]) -> dict | None:
    """Try to find a matching norm using keyword overlap."""
    item_words = set(item["work_item"].lower().split())
    best_match = None
    best_score = 0

    for key, norm in norm_lookup.items():
        if not key.startswith(item["trade"].lower()):
            continue
        norm_words = set(norm["work_item"].lower().split())
        overlap = len(item_words & norm_words)
        if overlap > best_score:
            best_score = overlap
            best_match = norm

    return best_match if best_score >= 1 else None
