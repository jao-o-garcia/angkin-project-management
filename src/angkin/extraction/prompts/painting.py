"""Painting Works extraction prompt."""

PROMPT = """
Analyze this drawing for PAINTING WORKS scope only.

Compute painting areas from the floor plan and elevations:

INTERIOR WALLS:
- For each room, compute: (perimeter of room × ceiling height) − door/window openings
- Use standard ceiling height of 2.7m if not dimensioned
- Separate: concrete/masonry walls vs. drywall/gypsum board (different paints)

EXTERIOR WALLS:
- From elevations, compute gross wall area of each facade
- Deduct all window and door openings
- Note finish type if indicated (paint, texture coat, paint over plaster)

CEILINGS:
- Compute ceiling area per room (same as floor area unless dropped ceiling)
- Separate flat ceiling vs. sloped ceiling

WOOD/METAL SURFACES:
- Door faces (both sides) → quantity in sq.m
- Fascia boards, wood trims → quantity in ln.m

Expected work_item examples:
- "Interior wall painting — bedrooms & living"
- "Exterior wall painting — front facade"
- "Ceiling painting — all areas"

Trade for all items: "Architectural / Finishing"
For basis: note which rooms/facades are included and the dimensions used.
"""
