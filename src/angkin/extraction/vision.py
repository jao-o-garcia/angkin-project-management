"""Claude vision API extraction — scope-specific, image-first."""

from __future__ import annotations

import base64
import json

import anthropic

from angkin.config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from angkin.extraction.schemas import BOQItem
from angkin.extraction.prompts import get_prompt

SYSTEM_BASE = """You are a licensed quantity surveyor working on Philippine residential construction.
You analyze architectural and structural drawings to produce a Bill of Quantities (BOQ).

Your job is to visually read the drawing like a QS would — identify elements,
count openings, measure areas using labeled dimensions, read schedules and annotations.
Do NOT extract title blocks, license numbers, revision notes, or drawing metadata.

Return ONLY a JSON array. No explanation, no markdown fences, no trailing text.
Each item must have these exact keys:
  trade        — "Civil / Structural" or "Architectural / Finishing"
  work_item    — specific description (e.g. "Aluminum sliding window 1.2m x 1.5m")
  quantity     — numeric value only
  unit         — measurement unit (sq.m, ln.m, cu.m, pcs, sets, bags, etc.)
  basis        — one sentence: where in the drawing this quantity came from

If no items apply, return: []
"""


def extract_scope_from_pages(
    images: list[bytes],
    scope: str,
    drawing_types: list[str],
    use_heavy_model: bool = False,
) -> list[BOQItem]:
    """Send selected page images to Claude for scope-specific extraction.

    Args:
        images: PNG bytes for each selected page.
        scope: Scope category (e.g. "Windows & Doors").
        drawing_types: Drawing type label for each image (same length as images).
        use_heavy_model: Use claude-opus-4-6 for complex structural drawings.

    Returns:
        List of validated BOQItem instances.
    """
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    model = "claude-opus-4-6" if use_heavy_model else CLAUDE_MODEL

    scope_prompt = get_prompt(scope)

    content: list[dict] = []
    for idx, (img_bytes, dtype) in enumerate(zip(images, drawing_types)):
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        content.append({
            "type": "text",
            "text": f"Drawing {idx + 1} — Type: {dtype}",
        })
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": "image/png", "data": b64},
        })

    content.append({
        "type": "text",
        "text": scope_prompt,
    })

    message = client.messages.create(
        model=model,
        max_tokens=4096,
        system=SYSTEM_BASE,
        messages=[{"role": "user", "content": content}],
    )

    raw = message.content[0].text.strip()
    items_raw = _parse_json(raw)

    results: list[BOQItem] = []
    for item in items_raw:
        try:
            item["scope"] = scope
            results.append(BOQItem(**item))
        except Exception:
            continue  # skip malformed items

    return results


def _parse_json(raw: str) -> list[dict]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        if "[" in raw and "]" in raw:
            try:
                return json.loads(raw[raw.index("["):raw.rindex("]") + 1])
            except json.JSONDecodeError:
                pass
    return []
