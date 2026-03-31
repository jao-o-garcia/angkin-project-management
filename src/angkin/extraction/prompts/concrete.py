"""Concrete Works extraction prompt."""

PROMPT = """
Analyze this drawing for CONCRETE WORKS scope only.

Extract all concrete elements visible in structural or foundation plans:

FOOTINGS:
- Identify footing schedule or detail (footing dimensions and depth)
- Count number of footings of each type
- Compute volume: footing plan area × depth (in cu.m)

COLUMNS:
- Read column schedule (size and height)
- Count columns per floor
- Compute volume: column cross-section × height (in cu.m)

BEAMS:
- Read beam schedule (width × depth, span)
- Compute volume: cross-section × total length (in cu.m)

SLABS:
- Ground floor slab: plan area × thickness
- Roof deck / upper floor slab: plan area × thickness
- Compute in cu.m

GRADE BEAMS / TIE BEAMS:
- Compute volume: cross-section × total length (in cu.m)

STAIRS:
- Estimate concrete volume per stair (approximate)

Output separate line items per element type.
Trade for all items: "Civil / Structural"
For basis: cite the element label/tag, count, and dimensions used for the volume calculation.
"""
