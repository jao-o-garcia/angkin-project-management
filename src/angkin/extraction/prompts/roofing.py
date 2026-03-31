"""Roofing Works extraction prompt."""

PROMPT = """
Analyze this drawing for ROOFING WORKS scope only.

From the roof plan and/or building section:

ROOF COVERING:
- Identify the roof plan area (plan projection in sq.m)
- Apply pitch factor to get actual roof surface area:
  - Low pitch (< 15°): factor ≈ 1.03
  - Medium pitch (15–30°): factor ≈ 1.10
  - Steep pitch (30–45°): factor ≈ 1.30
- Note roof material if specified (pre-painted rib-type, long-span roofing, clay tile, etc.)

GUTTERS & DOWNSPOUTS:
- Estimate gutter length from roof perimeter (ln.m)
- Count downspout locations (pcs)

FASCIA BOARD:
- Estimate fascia length from roof perimeter (ln.m)

RIDGE CAP:
- Estimate from ridge line length (ln.m)

ROOF FRAMING (if structural plan is included):
- Purlins: count and total length (ln.m) or weight (kg)
- Rafters / trusses: count

Output separate items per element.
Trade for roof covering: "Architectural / Finishing"
Trade for structural framing (trusses, purlins): "Civil / Structural"
For basis: cite roof plan dimensions, pitch angle (if shown), and any material notes.
"""
