"""Application configuration."""

from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "angkin.db"

DATA_DIR.mkdir(exist_ok=True)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-20250514"

PH_WORKING_DAYS_PER_WEEK = 6
PH_HOURS_PER_DAY = 8
DEFAULT_EFFICIENCY_RATE = 0.85

TRADES = ["Civil / Structural", "Architectural / Finishing"]
