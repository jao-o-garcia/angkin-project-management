"""PDF rasterization using pypdfium2."""

from __future__ import annotations

import io
import pypdfium2 as pdfium

from angkin.config import RASTER_DPI


def rasterize_pdf(pdf_bytes: bytes, dpi: int = RASTER_DPI) -> list[bytes]:
    """Convert each PDF page to a PNG image.

    Returns:
        List of PNG image bytes, one per page.
    """
    pdf = pdfium.PdfDocument(pdf_bytes)
    scale = dpi / 72  # pypdfium2 uses 72 DPI as base

    png_pages: list[bytes] = []
    for page in pdf:
        bitmap = page.render(scale=scale, rotation=0)
        pil_image = bitmap.to_pil()
        buf = io.BytesIO()
        pil_image.save(buf, format="PNG")
        png_pages.append(buf.getvalue())
        page.close()

    pdf.close()
    return png_pages


def page_count(pdf_bytes: bytes) -> int:
    pdf = pdfium.PdfDocument(pdf_bytes)
    n = len(pdf)
    pdf.close()
    return n
