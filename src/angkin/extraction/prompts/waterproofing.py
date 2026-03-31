"""Waterproofing extraction prompt."""

PROMPT = """
Analyze this drawing for WATERPROOFING scope only.

Identify all areas where waterproofing is required or implied:

WET AREAS (standard waterproofing zones in PH residential):
- Toilet & bath floor areas — floor area + 300mm up the wall (perimeter × 0.3m)
- Roof deck (if flat or low-slope) — full deck area
- Balcony / terrace — floor area
- Kitchen floor (if explicitly noted)

BELOW-GRADE:
- Retaining walls (if any) — area in sq.m
- Basement floor/walls (if any)

PLANTERS / WATER FEATURES:
- If visible and labeled

For each waterproofed area, output:
- "Waterproofing — [location]" → quantity: area in sq.m, unit: sq.m
- Specify material if noted (e.g., "crystalline waterproofing", "torch-applied membrane")

Trade for all items: "Architectural / Finishing"
For basis: cite the room/area, floor dimensions, and any wall upturn dimensions used.
"""
