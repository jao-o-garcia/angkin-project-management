"""Default Philippine residential construction labor norms.

These are baseline estimates per unit of work. PMs can override via the app.
Sources: DPWH standards, typical PH residential rates.
"""

DEFAULT_NORMS: list[dict] = [
    # ── Civil / Structural ──────────────────────────────────
    {"trade": "Civil / Structural", "work_item": "Excavation (common soil)",      "unit": "cu.m", "manhours_per_unit": 1.5,  "labor_rate_per_hour": 75,  "notes": "Manual excavation"},
    {"trade": "Civil / Structural", "work_item": "Backfilling & compaction",      "unit": "cu.m", "manhours_per_unit": 0.8,  "labor_rate_per_hour": 75,  "notes": ""},
    {"trade": "Civil / Structural", "work_item": "Gravel bedding",                "unit": "cu.m", "manhours_per_unit": 0.5,  "labor_rate_per_hour": 75,  "notes": ""},
    {"trade": "Civil / Structural", "work_item": "Concrete works (footing/slab)", "unit": "cu.m", "manhours_per_unit": 8.0,  "labor_rate_per_hour": 85,  "notes": "Includes mixing, pouring, vibrating"},
    {"trade": "Civil / Structural", "work_item": "Concrete works (columns)",      "unit": "cu.m", "manhours_per_unit": 10.0, "labor_rate_per_hour": 85,  "notes": "Vertical pours"},
    {"trade": "Civil / Structural", "work_item": "Concrete works (beams)",        "unit": "cu.m", "manhours_per_unit": 9.0,  "labor_rate_per_hour": 85,  "notes": ""},
    {"trade": "Civil / Structural", "work_item": "Rebar works",                   "unit": "kg",   "manhours_per_unit": 0.08, "labor_rate_per_hour": 80,  "notes": "Cutting, bending, tying"},
    {"trade": "Civil / Structural", "work_item": "Formworks",                     "unit": "sq.m", "manhours_per_unit": 1.2,  "labor_rate_per_hour": 80,  "notes": "Fabrication + installation"},
    {"trade": "Civil / Structural", "work_item": "Structural steel",              "unit": "kg",   "manhours_per_unit": 0.12, "labor_rate_per_hour": 90,  "notes": "Welding + installation"},

    # ── Architectural / Finishing ───────────────────────────
    {"trade": "Architectural / Finishing", "work_item": "CHB wall laying",         "unit": "sq.m", "manhours_per_unit": 1.8,  "labor_rate_per_hour": 75,  "notes": "4\" or 6\" CHB"},
    {"trade": "Architectural / Finishing", "work_item": "Plastering",              "unit": "sq.m", "manhours_per_unit": 0.8,  "labor_rate_per_hour": 75,  "notes": "Two-coat plaster"},
    {"trade": "Architectural / Finishing", "work_item": "Floor tiling",            "unit": "sq.m", "manhours_per_unit": 1.5,  "labor_rate_per_hour": 80,  "notes": "600x600 tiles"},
    {"trade": "Architectural / Finishing", "work_item": "Wall tiling",             "unit": "sq.m", "manhours_per_unit": 2.0,  "labor_rate_per_hour": 80,  "notes": ""},
    {"trade": "Architectural / Finishing", "work_item": "Painting (interior)",     "unit": "sq.m", "manhours_per_unit": 0.3,  "labor_rate_per_hour": 70,  "notes": "Two-coat latex"},
    {"trade": "Architectural / Finishing", "work_item": "Painting (exterior)",     "unit": "sq.m", "manhours_per_unit": 0.4,  "labor_rate_per_hour": 70,  "notes": "Two-coat elastomeric"},
    {"trade": "Architectural / Finishing", "work_item": "Ceiling installation",    "unit": "sq.m", "manhours_per_unit": 0.7,  "labor_rate_per_hour": 75,  "notes": "Fiber cement board"},
    {"trade": "Architectural / Finishing", "work_item": "Door installation",       "unit": "pcs",  "manhours_per_unit": 4.0,  "labor_rate_per_hour": 80,  "notes": "Flush door w/ jamb"},
    {"trade": "Architectural / Finishing", "work_item": "Window installation",     "unit": "pcs",  "manhours_per_unit": 3.0,  "labor_rate_per_hour": 80,  "notes": "Aluminum sliding"},
    {"trade": "Architectural / Finishing", "work_item": "Roofing (long-span)",     "unit": "sq.m", "manhours_per_unit": 0.6,  "labor_rate_per_hour": 80,  "notes": "Pre-painted metal"},
    {"trade": "Architectural / Finishing", "work_item": "Waterproofing",           "unit": "sq.m", "manhours_per_unit": 0.5,  "labor_rate_per_hour": 75,  "notes": "Membrane application"},
]
