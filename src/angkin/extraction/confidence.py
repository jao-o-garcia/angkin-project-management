"""Confidence scoring and extraction routing."""

from __future__ import annotations

from angkin.extraction.parser import ExtractedItem, extract_from_pdf, has_text_layer
from angkin.extraction.llm_fallback import extract_from_images, rasterize_pdf

CONFIDENCE_THRESHOLD = 0.5
MIN_ITEMS_THRESHOLD = 2


def extract_scope_items(pdf_bytes: bytes) -> tuple[list[dict], str]:
    """Main extraction entry point. Routes between structured and LLM extraction.

    Returns:
        (items, method) where method is 'structured', 'llm', or 'hybrid'.
    """
    has_text, text_confidence = has_text_layer(pdf_bytes)

    if has_text and text_confidence >= CONFIDENCE_THRESHOLD:
        parsed_items = extract_from_pdf(pdf_bytes)
        avg_confidence = (
            sum(it.confidence for it in parsed_items) / len(parsed_items)
            if parsed_items
            else 0
        )

        if len(parsed_items) >= MIN_ITEMS_THRESHOLD and avg_confidence >= CONFIDENCE_THRESHOLD:
            return [_item_to_dict(it) for it in parsed_items], "structured"

        llm_items = _run_llm_extraction(pdf_bytes)
        all_items = [_item_to_dict(it) for it in parsed_items] + llm_items
        return _deduplicate(all_items), "hybrid"

    llm_items = _run_llm_extraction(pdf_bytes)
    return llm_items, "llm"


def _run_llm_extraction(pdf_bytes: bytes) -> list[dict]:
    images = rasterize_pdf(pdf_bytes)
    return extract_from_images(images)


def _item_to_dict(item: ExtractedItem) -> dict:
    return {
        "trade": item.trade,
        "work_item": item.work_item,
        "quantity": item.quantity,
        "unit": item.unit,
        "source": item.source,
    }


def _deduplicate(items: list[dict]) -> list[dict]:
    """Remove near-duplicate items, preferring parsed over LLM."""
    seen: dict[str, dict] = {}
    for item in items:
        key = f"{item['work_item'].lower().strip()}_{item['unit'].lower()}"
        if key not in seen:
            seen[key] = item
        elif item["source"] == "parsed":
            seen[key] = item
    return list(seen.values())
