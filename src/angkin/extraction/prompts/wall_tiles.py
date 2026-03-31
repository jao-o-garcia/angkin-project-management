"""Wall Tiles extraction prompt."""

PROMPT = """
Analyze this drawing for WALL TILES scope only.

Identify all areas where wall tiles are specified or implied:
- Toilet & bath walls (standard: floor-to-ceiling or to 1.8m height)
- Kitchen splash back (standard: 0.6m height above counter)
- Service area / laundry walls
- Any wall tile notation visible on elevation or floor plan

For each tiled wall area:
- Compute the gross wall area (wall length × tile height)
- Deduct any doors or windows in that wall
- Note the tile specification if shown

Expected output items:
- Wall tiles — toilet & bath [room] → quantity: net wall area in sq.m, unit: sq.m
- Wall tiles — kitchen splashback → quantity: area in sq.m, unit: sq.m
- If tile spec is shown: use as work_item (e.g., "200x300 ceramic wall tile — T&B 1")

Trade for all items: "Architectural / Finishing"
For basis: cite the room, wall dimensions, and tile height assumption used.
"""
