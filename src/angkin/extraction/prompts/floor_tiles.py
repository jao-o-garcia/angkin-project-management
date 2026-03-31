"""Floor Tiles extraction prompt."""

PROMPT = """
Analyze this drawing for FLOOR TILES scope only.

For each room or area visible in the floor plan:
- Identify the room label (bedroom, living, toilet, etc.)
- Read labeled dimensions (length × width) if shown
- Estimate the net floor area in sq.m, deducting wall thickness if dimensions are exterior
- Note the tile specification if indicated (size, material, finish)

Expected output items:
- Floor tiles — [room name] → quantity: floor area in sq.m, unit: sq.m
- If tile type/size is specified: use that as the work_item description
  (e.g., "300x300 ceramic floor tile — toilet & bath")

For toilet/bathroom areas, note these separately as they may use different tile specifications.
For areas with no tile indication (e.g., garage, service area), skip them.
Do not include wall tiles here — those are a separate scope.

Trade for all items: "Architectural / Finishing"
For basis: cite the room label and dimensions used (e.g., "Living Room 4.5m × 5.0m = 22.5 sq.m").
"""
