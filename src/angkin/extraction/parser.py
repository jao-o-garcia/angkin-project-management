"""Structured PDF text/table extraction using pdfplumber."""

from __future__ import annotations

import io
import re
from dataclasses import dataclass

import pdfplumber


@dataclass
class ExtractedItem:
    trade: str
    work_item: str
    quantity: float
    unit: str
    source: str = "parsed"
    confidence: float = 1.0
    page: int = 0


TRADE_KEYWORDS = {
    "Civil / Structural": [
        "excavation", "footing", "foundation", "column", "beam", "slab",
        "concrete", "rebar", "reinforcement", "formwork", "backfill",
        "gravel", "compaction", "structural", "civil",
    ],
    "Architectural / Finishing": [
        "tile", "tiling", "plaster", "paint", "painting", "finishing",
        "door", "window", "ceiling", "drywall", "masonry", "block",
        "wall", "roofing", "waterproofing", "insulation", "flooring",
    ],
}


def classify_trade(text: str) -> str:
    text_lower = text.lower()
    scores: dict[str, int] = {}
    for trade, keywords in TRADE_KEYWORDS.items():
        scores[trade] = sum(1 for kw in keywords if kw in text_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Civil / Structural"


UNIT_PATTERNS = re.compile(
    r"\b(cu\.?\s*m|sq\.?\s*m|ln\.?\s*m|pcs|sets?|bags?|kg|tons?|lots?|l\.?s\.?)\b",
    re.IGNORECASE,
)

QUANTITY_PATTERN = re.compile(r"[\d,]+\.?\d*")


def extract_from_pdf(pdf_bytes: bytes) -> list[ExtractedItem]:
    """Extract scope items from a digital PDF with text layers."""
    items: list[ExtractedItem] = []

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            if tables:
                items.extend(_parse_tables(tables, page_num))
            else:
                text = page.extract_text() or ""
                items.extend(_parse_text(text, page_num))

    return items


def has_text_layer(pdf_bytes: bytes) -> tuple[bool, float]:
    """Check if the PDF has a usable text layer. Returns (has_text, confidence)."""
    total_chars = 0
    total_pages = 0

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        total_pages = len(pdf.pages)
        for page in pdf.pages:
            text = page.extract_text() or ""
            total_chars += len(text.strip())

    if total_pages == 0:
        return False, 0.0

    avg_chars = total_chars / total_pages
    if avg_chars > 100:
        return True, min(avg_chars / 500, 1.0)
    return False, avg_chars / 500


def _parse_tables(tables: list[list[list[str | None]]], page_num: int) -> list[ExtractedItem]:
    items: list[ExtractedItem] = []
    for table in tables:
        if len(table) < 2:
            continue
        headers = [str(c or "").lower().strip() for c in table[0]]
        for row in table[1:]:
            if not row or all(c is None or str(c).strip() == "" for c in row):
                continue
            cells = [str(c or "").strip() for c in row]
            item = _row_to_item(headers, cells, page_num)
            if item:
                items.append(item)
    return items


def _row_to_item(
    headers: list[str], cells: list[str], page_num: int
) -> ExtractedItem | None:
    if len(cells) < 2:
        return None

    work_item = ""
    quantity = 0.0
    unit = ""

    for i, header in enumerate(headers):
        if i >= len(cells):
            break
        val = cells[i]
        h = header.lower()
        if any(k in h for k in ("item", "description", "work", "scope", "activity")):
            work_item = val
        elif any(k in h for k in ("qty", "quantity", "amount", "vol")):
            nums = QUANTITY_PATTERN.findall(val.replace(",", ""))
            if nums:
                quantity = float(nums[0])
        elif any(k in h for k in ("unit",)):
            unit = val

    if not work_item:
        work_item = cells[0]
    if quantity == 0 and len(cells) > 1:
        for cell in cells[1:]:
            nums = QUANTITY_PATTERN.findall(cell.replace(",", ""))
            if nums:
                quantity = float(nums[0])
                break
    if not unit:
        for cell in cells:
            match = UNIT_PATTERNS.search(cell)
            if match:
                unit = match.group(0)
                break

    if not work_item or quantity == 0:
        return None

    return ExtractedItem(
        trade=classify_trade(work_item),
        work_item=work_item,
        quantity=quantity,
        unit=unit or "lot",
        source="parsed",
        confidence=0.8 if unit else 0.5,
        page=page_num,
    )


def _parse_text(text: str, page_num: int) -> list[ExtractedItem]:
    """Fallback: line-by-line extraction when no tables are found."""
    items: list[ExtractedItem] = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    for line in lines:
        nums = QUANTITY_PATTERN.findall(line.replace(",", ""))
        unit_match = UNIT_PATTERNS.search(line)
        if nums and unit_match:
            quantity = float(nums[0])
            unit = unit_match.group(0)
            description = QUANTITY_PATTERN.sub("", line)
            description = UNIT_PATTERNS.sub("", description).strip(" -–—:,.")
            if description and quantity > 0:
                items.append(ExtractedItem(
                    trade=classify_trade(description),
                    work_item=description,
                    quantity=quantity,
                    unit=unit,
                    source="parsed",
                    confidence=0.4,
                    page=page_num,
                ))

    return items
