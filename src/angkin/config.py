"""Application configuration."""

from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "angkin.db"
PAGES_DIR = DATA_DIR / "pages"

DATA_DIR.mkdir(exist_ok=True)
PAGES_DIR.mkdir(exist_ok=True)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Vision model for extraction — use opus for complex structural drawings
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
CLAUDE_MODEL_HEAVY = "claude-opus-4-6"

PH_WORKING_DAYS_PER_WEEK = 6
PH_HOURS_PER_DAY = 8
DEFAULT_EFFICIENCY_RATE = 0.85

TRADES = ["Civil / Structural", "Architectural / Finishing"]

SCOPE_TYPES = [
    "Windows & Doors",
    "Floor Tiles",
    "Wall Tiles",
    "Painting Works",
    "Concrete Works",
    "Masonry / CHB Works",
    "Roofing Works",
    "Waterproofing",
    "Other",
]

DRAWING_TYPES = [
    "Floor Plan",
    "Elevation",
    "Section",
    "Structural Plan",
    "Roof Plan",
    "Site Plan",
    "Detail Drawing",
    "Schedule Sheet",
    "Unknown",
]

# Rasterization DPI — higher = better accuracy, larger file
RASTER_DPI = 150
