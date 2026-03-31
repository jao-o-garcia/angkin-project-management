"""LLM-based extraction using Claude API for scanned/image PDFs."""

from __future__ import annotations

import base64
import json
import io

from angkin.config import ANTHROPIC_API_KEY, CLAUDE_MODEL

SYSTEM_PROMPT = """You are a construction document extraction assistant for Philippine residential construction.

Given an image of a construction document page (bill of quantities, scope of work, etc.),
extract ALL line items you can identify.

For each item, return:
- trade: Either "Civil / Structural" or "Architectural / Finishing"
- work_item: Description of the work (e.g. "Footing excavation", "Floor tiling")
- quantity: Numeric quantity
- unit: Unit of measurement (e.g. "cu.m", "sq.m", "pcs", "ln.m", "lot")

Return ONLY a JSON array. No explanation, no markdown fences.

Example output:
[
  {"trade": "Civil / Structural", "work_item": "Footing excavation", "quantity": 45, "unit": "cu.m"},
  {"trade": "Architectural / Finishing", "work_item": "Floor tiles", "quantity": 280, "unit": "sq.m"}
]

If you cannot extract any items from the page, return an empty array: []
"""


def extract_from_images(images: list[bytes]) -> list[dict]:
    """Send rasterized PDF page images to Claude for extraction.

    Args:
        images: List of PNG image bytes, one per page.

    Returns:
        List of extracted scope item dicts.
    """
    if not ANTHROPIC_API_KEY:
        raise ValueError(
            "ANTHROPIC_API_KEY is not set. Add it to your .env file to use LLM extraction."
        )

    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    all_items: list[dict] = []

    for page_idx, img_bytes in enumerate(images):
        b64 = base64.b64encode(img_bytes).decode("utf-8")

        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": f"Extract all construction scope items from this page (page {page_idx + 1}).",
                        },
                    ],
                }
            ],
        )

        raw = message.content[0].text.strip()
        try:
            items = json.loads(raw)
        except json.JSONDecodeError:
            if "[" in raw and "]" in raw:
                bracket_content = raw[raw.index("["):raw.rindex("]") + 1]
                try:
                    items = json.loads(bracket_content)
                except json.JSONDecodeError:
                    items = []
            else:
                items = []

        for item in items:
            item["source"] = "llm"
            item["page"] = page_idx + 1
        all_items.extend(items)

    return all_items


def rasterize_pdf(pdf_bytes: bytes, dpi: int = 200) -> list[bytes]:
    """Convert PDF pages to PNG images using pdf2image."""
    from pdf2image import convert_from_bytes

    pil_images = convert_from_bytes(pdf_bytes, dpi=dpi, fmt="png")
    png_bytes_list: list[bytes] = []
    for img in pil_images:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        png_bytes_list.append(buf.getvalue())
    return png_bytes_list
