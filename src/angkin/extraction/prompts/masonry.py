"""Masonry / CHB Works extraction prompt."""

PROMPT = """
Analyze this drawing for MASONRY / CHB (Concrete Hollow Block) WORKS scope only.

For each wall in the floor plan:
- Identify which walls are CHB / masonry (vs. drywall, concrete wall, or glass partition)
- Compute the wall area: wall length × wall height
- Deduct door and window openings
- Note CHB size if specified (4" or 6" thick)

Expected output items:
- "CHB wall — 4" thick [location/description]" → quantity: wall area in sq.m, unit: sq.m
- "CHB wall — 6" thick [location/description]" → quantity: wall area in sq.m, unit: sq.m
- "Plastering — [location]" → quantity: area to be plastered in sq.m, unit: sq.m
  (typically both faces of CHB wall = wall area × 2)

Group by CHB size. If size is not indicated, use 4" as default for interior and 6" for exterior.

Trade for all items: "Civil / Structural"
For basis: cite the wall location (e.g., "between Bedroom 1 and hallway"), length, and height used.
"""
