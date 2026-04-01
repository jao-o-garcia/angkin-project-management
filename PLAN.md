# App: Residential Construction Project Scheduler (PH)

## Problem Statement
Project Managers in Philippine residential construction manually compute manhours,
build schedules, and load manpower from architectural/structural PDF drawings — with no
systematic way to apply historical site efficiency data. This app automates that workflow
by using AI vision to read the drawings the same way a quantity surveyor would.

## Users
- Single user, no login required
- Primary user: Project Manager

## What the AI Actually Does
The input is architectural drawings — floor plans, elevations, sections, structural plans.
These are visual documents, not text tables. The AI looks at each drawing and identifies
quantifiable scope items the same way a QS would: counting openings for door/window
schedules, measuring room areas for tile works, computing wall and ceiling surface areas
for painting, identifying footings and slabs from structural plans.

The output is a Bill of Quantities (BOQ), Scope of Works, and Cost Estimate — generated
from scratch from the drawings, not extracted from a text layer.

## Core Workflow

### Step 1 — PDF Upload & Page Preview
- PM uploads one or more architectural/structural PDF files
- App rasterizes each page to a high-resolution image
- PM sees a thumbnail grid of all pages and assigns a drawing type label to each
  (Floor Plan, Elevation, Section, Structural Plan, Site Plan, etc.)
- This labeling helps the AI understand the context of each drawing before analysis

### Step 2 — Scope-by-Scope Extraction (Incremental, PM-Controlled)

This is the core extraction loop. The PM controls the order and pace of analysis.

#### 2a. PM Selects a Scope to Analyze
- PM picks a trade scope from a predefined list:
  - Windows & Doors (count openings, compute areas from floor plans/elevations)
  - Floor Tiles (measure room dimensions, compute floor areas)
  - Wall Tiles (identify tiled areas from floor plans/elevations)
  - Painting Works (compute wall and ceiling surface areas)
  - Concrete Works (footings, columns, slabs, beams from structural plans)
  - Masonry / CHB Works (wall lengths and heights)
  - Roofing Works (roof area from roof plan/section)
  - Waterproofing (wet area identification)
  - Other (PM defines the scope label manually)

#### 2b. PM Selects Which Pages to Analyze for This Scope
- PM selects from the page thumbnail grid which drawings are relevant for this scope
  (e.g., for Windows & Doors, select Floor Plan and Elevation pages)
- This avoids sending irrelevant pages to the LLM

#### 2c. LLM Vision Extraction
- Selected pages are sent to Claude (claude-opus-4-5 or claude-sonnet-4-5) with a
  scope-specific system prompt
- Prompt instructs Claude to act as a quantity surveyor analyzing the drawing
- Prompt specifies: extract only items relevant to the selected scope
- Claude returns structured JSON:
  ```json
  [
    {
      "trade": "Architectural / Finishing",
      "scope": "Windows & Doors",
      "work_item": "Aluminum Sliding Window",
      "quantity": 4,
      "unit": "sets",
      "basis": "counted from floor plan, 4 openings labeled W1"
    }
  ]
  ```
- The `basis` field is critical — it forces the LLM to explain its measurement source,
  making it easier for the PM to verify against the drawing

#### 2d. PM Reviews and Confirms This Scope
- App shows a split-pane screen: drawing image (left) + extracted items table (right)
- PM can: correct quantities, rename items, reassign trades, add/delete rows
- PM clicks "Confirm & Lock" to finalize this scope
- Locked scopes cannot be edited without explicitly unlocking

#### 2e. Next Scope
- PM proceeds to the next scope (e.g., Floor Tiles after Windows & Doors)
- Confirmed scopes accumulate in the BOQ
- PM can see a running total of confirmed BOQ items at any time

### Step 3 — Historical Efficiency Import
- PM uploads historical project Excel files
- App extracts actual site efficiency rates per trade
  (Civil/Structural, Architectural/Finishing)
- Efficiency rates are stored locally and reused across future projects
- PM can view, edit, and override stored efficiency rates

### Step 4 — Manhour Computation Engine
- Maps each confirmed scope item to its trade
- Applies standard PH labor manhour norms per work item
- Adjusts manhours using historical efficiency rate per trade
- Formula: Adjusted Manhours = Base Manhours ÷ Efficiency Rate
- Output: Manhour summary per trade, per work item


### Step 5 — Schedule & Crew Calculation
- Crew Size = Adjusted Manhours ÷ (Target Duration × Working Hours per Day)
- Activities sequenced with logical dependencies per trade
- Working calendar: PH standard (6-day work week, 8 hrs/day)

### Step 6 — Outputs
- **Gantt Chart** — activity-level schedule with durations and trade swim lanes
- **Manpower Loading Plan** — crew count per trade per week
- **Cost & Manhour Estimate** — total manhours × PH labor rate per trade
- **Export: MS Project XML (.xml)** — full Gantt export for MS Project compatibility

## Software Architecture

### Stack
- **Language:** Python 3.12
- **Package Manager:** uv
- **Backend:** FastAPI (async API layer between frontend and compute engine)
- **Frontend:** Streamlit (v1 — single user, fast to ship)
  - streamlit-pdf-viewer for in-app PDF preview
  - st.data_editor for PM review/edit table
- **Database:** SQLite (local, no cloud, no auth)
- **LLM:** Claude API (anthropic SDK) — vision-first structured extraction
- **Charts:** Plotly (Gantt chart, manpower loading)
- **Export:** MS Project XML format (.xml)

### PDF Processing Pipeline
There is no text extraction step. The pipeline is purely vision-based:

1. **Rasterize** — pypdfium2 converts each PDF page to a high-resolution PNG (≥150 DPI)
2. **Label** — PM assigns drawing type to each page (stored in SQLite)
3. **Extract** — selected pages are base64-encoded and sent to Claude API as image content
4. **Parse** — Claude returns JSON; app validates and normalizes the response
5. **Review** — PM sees extracted items and confirms or corrects them
6. **Lock** — confirmed items are written to the BOQ table in SQLite

No pdfplumber. No PyMuPDF text extraction. No confidence scoring or hybrid fallback.
Text on architectural drawings (room labels, dimension annotations) is read by the LLM
vision model as part of understanding the drawing — not extracted separately.

### LLM Prompt Strategy
- Each rasterized page is sent with a scope-specific system prompt
- System prompt establishes Claude's role: "You are a licensed quantity surveyor..."
- User prompt specifies the scope: "Analyze this floor plan for Windows & Doors..."
- Output format is enforced: JSON array with trade, scope, work_item, quantity, unit, basis
- `basis` field is required — Claude must cite where each quantity came from in the drawing
- Output is validated (Pydantic) before hitting the review screen
- No agent framework — single-shot extraction per scope per page batch

### Scope Prompt Library
Each scope has a dedicated prompt in `src/angkin/extraction/prompts/`:
- `windows_doors.py` — instructs LLM to count and schedule openings
- `floor_tiles.py` — instructs LLM to measure room areas and identify tile specifications
- `wall_tiles.py` — wet areas, kitchen splashbacks, tiled elevations
- `painting.py` — wall heights × lengths, ceiling areas, deduct openings
- `concrete.py` — footing dimensions, column schedules, slab thicknesses
- `masonry.py` — CHB wall lengths and heights
- `roofing.py` — roof plan area, pitch factor
- `waterproofing.py` — wet area identification

### Local Data Layer
- SQLite → stores projects, pages, page labels, scope extractions, confirmed BOQ items,
  efficiency rates, manhour norms
- No cloud, no auth, single machine

### Frontend
- Clean, PM-friendly UI (non-technical user)
- **Upload page:** drag-and-drop PDF → page thumbnail grid → drawing type labeling
- **Extraction page:** scope selector → page selector → extract → split-pane review →
  confirm & lock → repeat
- **BOQ summary:** running view of all confirmed scopes
- **Compute page:** manhour calculation and schedule generation
- **Outputs page:** Gantt, manpower loading, cost estimate, export

### Project Structure
```
angkin-project-management/
├── pyproject.toml
├── .python-version
├── .env.example
├── .gitignore
├── PLAN.md / README.md
├── app.py                          # Streamlit entry point
├── pages/                          # Streamlit multipage
│   ├── 1_Upload.py                 # PDF upload + page labeling
│   ├── 2_Extract.py                # Scope-by-scope extraction loop
│   ├── 3_BOQ_Summary.py            # Confirmed items overview
│   ├── 4_History.py                # Historical efficiency import
│   ├── 5_Compute.py                # Manhour + schedule computation
│   └── 6_Export.py                 # Gantt, manpower, cost, XML
├── src/angkin/
│   ├── config.py
│   ├── db/                         # SQLite models + CRUD
│   ├── extraction/
│   │   ├── rasterizer.py           # PDF → PNG (pypdfium2)
│   │   ├── vision.py               # Claude API image call + response parser
│   │   ├── schemas.py              # Pydantic models for LLM output
│   │   └── prompts/                # One prompt file per scope
│   │       ├── windows_doors.py
│   │       ├── floor_tiles.py
│   │       ├── wall_tiles.py
│   │       ├── painting.py
│   │       ├── concrete.py
│   │       ├── masonry.py
│   │       ├── roofing.py
│   │       └── waterproofing.py
│   ├── computation/                # Manhours, scheduling, PH norms
│   └── export/                     # Gantt, manpower, MS Project XML
├── data/                           # SQLite DB storage
└── tests/
```

## Trades in Scope
- Civil / Structural
- Architectural / Finishing

## Key Constraints & Assumptions
- PH labor norms are hardcoded as defaults but PM-editable
- Efficiency rates improve over time as more historical Excels are imported
- PM review and confirmation is mandatory per scope — no silent auto-processing
- Claude API key required (vision model — claude-sonnet-4-6 for speed, claude-opus-4-5
  for complex structural drawings)
- Drawings must be legible at ≥150 DPI rasterization — heavily compressed or low-res
  scans may produce inaccurate extractions; PM is expected to verify against source

## Out of Scope (v1)
- Electrical, Mechanical, Plumbing trades
- Login / user accounts
- Cloud storage or team collaboration
- Cost procurement / materials scheduling
- Scale bar calibration (quantities are estimated from drawing proportions + labeled
  dimensions; precise scale-to-real-world measurement is a v2 feature)
