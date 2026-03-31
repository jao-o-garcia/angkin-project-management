"""Scope-specific extraction prompts."""

from __future__ import annotations

from angkin.extraction.prompts.windows_doors import PROMPT as WINDOWS_DOORS
from angkin.extraction.prompts.floor_tiles import PROMPT as FLOOR_TILES
from angkin.extraction.prompts.wall_tiles import PROMPT as WALL_TILES
from angkin.extraction.prompts.painting import PROMPT as PAINTING
from angkin.extraction.prompts.concrete import PROMPT as CONCRETE
from angkin.extraction.prompts.masonry import PROMPT as MASONRY
from angkin.extraction.prompts.roofing import PROMPT as ROOFING
from angkin.extraction.prompts.waterproofing import PROMPT as WATERPROOFING

_PROMPTS: dict[str, str] = {
    "Windows & Doors": WINDOWS_DOORS,
    "Floor Tiles": FLOOR_TILES,
    "Wall Tiles": WALL_TILES,
    "Painting Works": PAINTING,
    "Concrete Works": CONCRETE,
    "Masonry / CHB Works": MASONRY,
    "Roofing Works": ROOFING,
    "Waterproofing": WATERPROOFING,
}

_DEFAULT_PROMPT = (
    "Extract all quantifiable construction scope items visible in this drawing. "
    "Include work item descriptions, quantities with units, trade classification, "
    "and a brief basis note for each quantity."
)


def get_prompt(scope: str) -> str:
    return _PROMPTS.get(scope, _DEFAULT_PROMPT)
