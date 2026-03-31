# App: Residential Construction Project Scheduler (PH)

## Problem Statement
Project Managers in Philippine residential construction manually compute manhours,
build schedules, and load manpower from PDF plans — with no systematic way to apply
historical site efficiency data. This app automates that entire workflow.

## Users
- Single user, no login required
- Primary user: Project Manager

## Core Workflow

### Step 1 — PDF Ingestion (Hybrid Extraction)

#### Stage A: Structured Parsing (Primary)
- Use pdfplumber / PyMuPDF to extract text and tables from PDF
- If text layer is detected and confidence is high → proceed with structured extraction
- Map extracted text/tables to scope items, quantities, and trades using keyword rules

#### Stage B: LLM Fallback (Secondary)
- Triggered when: PDF is scanned, text layer is missing, or parsing confidence is low
- PDF pages are rasterized to images → sent to LLM (Claude) with a structured prompt
- LLM extracts scope items, quantities, trade classifications from the image
- Output is normalized into the same data structure as Stage A

#### Stage C: PM Review Screen (Mandatory)
- Regardless of which stage was used, PM always sees an editable table of extracted items
- PM can: correct quantities, rename items, reassign trades, add/delete rows
- PM confirms before any computation proceeds
- This is the trust checkpoint — no silent processing

### Step 2 — Historical Efficiency Import
- PM uploads historical project Excel files
- App extracts actual site efficiency rates per trade
  (Civil/Structural, Architectural/Finishing)
- Efficiency rates are stored locally and reused across future projects
- PM can view, edit, and override stored efficiency rates

### Step 3 — Manhour Computation Engine
- Maps each confirmed scope item to its trade
- Applies standard PH labor manhour norms per work item
- Adjusts manhours using historical efficiency rate per trade
- Formula: Adjusted Manhours = Base Manhours ÷ Efficiency Rate
- Output: Manhour summary per trade, per work item

### Step 4 — Schedule & Crew Calculation
- Crew Size = Adjusted Manhours ÷ (Target Duration × Working Hours per Day)
- Activities sequenced with logical dependencies per trade
- Working calendar: PH standard (6-day work week, 8 hrs/day)

### Step 5 — Outputs
- **Gantt Chart** — activity-level schedule with durations and trade swim lanes
- **Manpower Loading Plan** — crew count per trade per week
- **Cost & Manhour Estimate** — total manhours × PH labor rate per trade
- **Export: MS Project (.mpp)** — full Gantt export for MS Project compatibility

## Software Architecture

### PDF Processing Pipeline
- pdfplumber / PyMuPDF → structured text/table extraction
- pdf2image / poppler → rasterize pages for LLM fallback
- Claude API (claude-sonnet) → LLM extraction on scanned/low-confidence PDFs
- Confidence scoring logic → decides which path to take per page

### LLM Prompt Strategy
- Each rasterized page is sent with a structured system prompt
- Prompt instructs Claude to return JSON only:
  { trade, work_item, quantity, unit }
- Output is validated and normalized before hitting the review screen

### Local Data Layer
- SQLite → stores projects, scope items, efficiency rates, manhour norms
- No cloud, no auth, single machine

### Frontend
- Clean, PM-friendly UI (non-technical user)
- PDF upload → extraction progress indicator → review/edit table → compute → outputs

## Trades in Scope
- Civil / Structural
- Architectural / Finishing

## Key Constraints & Assumptions
- PH labor norms are hardcoded as defaults but PM-editable
- Efficiency rates improve over time as more historical Excels are imported
- PM review screen is mandatory — no silent auto-processing
- Claude API key required for LLM fallback feature

## Out of Scope (v1)
- Electrical, Mechanical, Plumbing trades
- Login / user accounts
- Cloud storage or team collaboration
- Cost procurement / materials scheduling