"""Windows & Doors extraction prompt."""

PROMPT = """
Analyze this drawing for WINDOWS & DOORS scope only.

Extract every window and door opening you can identify. For each:
- Read the window/door tag (e.g., W1, W2, D1, D2) and count how many times it appears
- Find the corresponding schedule or elevation that shows the size (width × height)
- Compute the opening area (width × height in sq.m) and note the quantity

Expected output items include:
- Aluminum sliding window [type] [size] → quantity: count of openings, unit: sets
- Casement window [type] [size] → quantity: count, unit: sets
- Solid panel door [type] [size] → quantity: count, unit: sets
- Flush door [type] [size] → quantity: count, unit: sets
- Roller shutter / garage door → quantity: count, unit: sets
- Total window area (for glazing works) → quantity: area in sq.m, unit: sq.m
- Total door area (for painting/finishing) → quantity: area in sq.m, unit: sq.m

For basis: note the tag label (e.g., "W1"), the count from plan, and size from schedule.
Do not include structural openings that are not window or door frames.
Trade for all items: "Architectural / Finishing"
"""
