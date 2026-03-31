# Angkin — Residential Construction Project Scheduler

Automates manhour computation, schedule generation, and manpower loading for Philippine residential construction projects.

## Quick Start

```bash
# Install dependencies
uv sync

# Set your Claude API key
cp .env.example .env
# Edit .env with your key

# Run the app
uv run streamlit run app.py
```

## What It Does

1. **Upload PDF** — Bill of quantities or construction plans
2. **Auto-extract** — Parses scope items, quantities, and trades (structured or LLM fallback)
3. **PM Review** — Editable table for corrections before computation
4. **Compute** — Manhours adjusted by historical site efficiency
5. **Export** — Gantt chart, manpower loading plan, cost estimate, MS Project XML

## Stack

- Python 3.12, managed with uv
- Streamlit (frontend)
- SQLite (local data)
- Claude API (LLM extraction fallback)
- Plotly (charts)
