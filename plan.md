# SAX-Gruppe Demo: Intelligent Market-Sourcing Engine
## Project Plan — V1 Batch Pipeline

> **Goal:** A working demo ready to show Bernd Ruck / Bastian Bort at SAX-Gruppe.
> Two screens: (A) raw document chaos → (B) clean AI-structured acquisition target.
> No Kafka, no Spark, no cloud infra. Fast, focused, impressive.

---

## Stage Overview

```
Stage 1: Schema Design      (~1 day)   Define what "structured" looks like
Stage 2: Mock Corpus        (~2 days)  Collect/write 20-30 real-feeling documents
Stage 3: Extraction Engine  (~2 days)  Instructor + LLM parses docs into schema
Stage 4: DuckDB Storage     (~1 day)   Persist and query extracted records
Stage 5: Streamlit UI       (~2 days)  The actual demo interface
Stage 6: Demo Polish        (~1 day)   Hardcode best results, rehearse narrative
```

**Total: ~9 days to a demo-ready build**

---

## Project Structure

```
sax-sourcing-engine/
│
├── plan.md                        # This file
├── README.md                      # Setup instructions (pip install, how to run)
├── .env                           # OPENAI_API_KEY or ANTHROPIC_API_KEY — never commit
├── requirements.txt               # All Python deps pinned
│
├── corpus/                        # Stage 2: Raw input documents
│   ├── README.md                  # Explains what each subfolder contains and sources
│   ├── insolvency_notices/        # German Insolvenzbekanntmachungen (plaintext .txt)
│   │   ├── insolvenz_01.txt
│   │   ├── insolvenz_02.txt
│   │   └── ...
│   ├── zoning_filings/            # Bebauungsplan excerpts and municipal notices (.txt or .pdf)
│   │   ├── bplan_tuebingen_01.txt
│   │   └── ...
│   └── property_listings/         # Scraped or manually copied commercial listings (.txt)
│       ├── listing_immoscout_01.txt
│       └── ...
│
├── schemas/                       # Stage 1: Pydantic data models
│   ├── __init__.py
│   └── asset_profile.py           # The core AssetProfile schema — every field the dashboard shows
│                                  # Includes: location, asset_class, plot_size_sqm, estimated_value,
│                                  # conversion_potential, zoning_flags, distress_signals,
│                                  # sax_fit_score, raw_source_text
│
├── pipeline/                      # Stage 3 + 4: The extraction and storage logic
│   ├── __init__.py
│   ├── loader.py                  # Walks the corpus/ folder, reads all .txt files into memory
│   │                              # Returns list of (filename, raw_text) tuples
│   ├── extractor.py               # Calls LLM via Instructor with AssetProfile schema
│   │                              # Takes raw_text → returns validated AssetProfile object
│   │                              # Handles retry logic and partial extraction failures
│   ├── scorer.py                  # Post-extraction scoring logic (no LLM needed here)
│   │                              # Computes sax_fit_score from: value > €20M, zoning flags,
│   │                              # distress signals, conversion potential match to SAX portfolio
│   └── storage.py                 # DuckDB read/write layer
│                                  # Creates asset_profiles table on first run
│                                  # Upserts records by source filename (idempotent)
│                                  # Provides query helpers: get_all(), get_top_n(), filter_by_class()
│
├── database/
│   └── sax_pipeline.duckdb        # Local DuckDB file — auto-created, gitignored
│                                  # Single table: asset_profiles
│                                  # Queryable with DBeaver or any SQL client for debugging
│
├── app/                           # Stage 5: Streamlit demo interface
│   ├── main.py                    # Entry point: `streamlit run app/main.py`
│   │                              # Two-tab layout: "Pipeline" tab and "Targets" tab
│   ├── views/
│   │   ├── screen_a_raw.py        # Screen A: "The Problem"
│   │   │                          # Shows the raw unstructured text from a selected document
│   │   │                          # Styled to look messy/overwhelming on purpose
│   │   ├── screen_b_profile.py    # Screen B: "The Solution"
│   │   │                          # Renders the AssetProfile as a clean parameter table
│   │   │                          # Green ✅ / Red ❌ SAX investment rule checks inline
│   │   │                          # Shows sax_fit_score as a prominent metric
│   │   └── dashboard.py           # Main acquisition targets table
│   │                              # Sorted by sax_fit_score descending
│   │                              # Filterable by asset class, minimum value, zoning risk
│   │                              # Each row expandable to show full AssetProfile
│   └── components/
│       ├── rule_checker.py        # Renders the ✅/❌ investment rule check table
│       │                          # Rules: value > €20M, region match, conversion potential,
│       │                          # no blocking zoning, distress signal present
│       └── styles.py              # Custom CSS injected via st.markdown()
│                                  # SAX brand colors (dark/neutral), clean table styling
│
├── scripts/
│   ├── run_pipeline.py            # One-shot script: load corpus → extract → score → store
│   │                              # Run this once to populate the database before the demo
│   │                              # Prints progress per document, logs failures gracefully
│   └── reset_db.py                # Drops and recreates the DuckDB table
│                                  # Use when iterating on the schema
│
└── tests/
    ├── test_schema.py             # Validates AssetProfile Pydantic model with sample data
    ├── test_extractor.py          # Runs extractor against one fixture document
    │                              # Checks all required fields are populated
    └── fixtures/
        └── sample_listing.txt     # One clean example document for fast testing
                                   # without burning API tokens
```

---

## Stage 1 — Schema Design (`schemas/asset_profile.py`)

**What you're deciding:** Every field the CEO will see on screen. Design this first because everything else derives from it.

Key fields to include in `AssetProfile`:

| Field | Type | Notes |
|---|---|---|
| `source_file` | str | Filename — traceability |
| `location_city` | str | e.g. "Tübingen" |
| `location_address` | str | Street-level if extractable |
| `asset_class` | Enum | Retail / Office / Hotel / Logistics / Residential / Mixed / Denkmal |
| `plot_size_sqm` | float \| None | Extracted from text |
| `building_size_sqm` | float \| None | GFA if mentioned |
| `estimated_value_eur` | float \| None | LLM estimate or extracted figure |
| `conversion_potential` | list[Enum] | ["Micro-Apartments", "Boutique Hotel", "Assisted Living", "Logistics"] |
| `zoning_flags` | list[str] | e.g. ["B-Plan §34", "Denkmalschutz", "Bebauungsplan pending"] |
| `distress_signals` | list[str] | e.g. ["Insolvency filing", "Balance sheet restructuring", "Vacancy >24 months"] |
| `sax_fit_score` | float | 0.0–1.0, computed post-extraction by scorer.py |
| `value_threshold_met` | bool | estimated_value_eur >= 20_000_000 |
| `summary` | str | 2–3 sentence LLM-generated acquisition rationale |
| `raw_source_text` | str | Full original text — shown in Screen A |
| `extracted_at` | datetime | Pipeline run timestamp |

---

## Stage 2 — Mock Corpus (`corpus/`)

**The goal:** 20–30 documents that feel like real German real estate intelligence. Mix of document types.

**Where to actually get them:**

- **Insolvency notices:** `www.insolvenzbekanntmachungen.de` — public, searchable by state. Filter for Baden-Württemberg commercial cases. Copy plaintext.
- **Zoning filings:** Tübingen, Stuttgart, Reutlingen municipal portals publish Bebauungsplan notices as PDFs. Extract text with `pdfplumber`.
- **Property listings:** ImmobilienScout24 and Immowelt commercial section. Manually copy 8–10 listings for BaWü commercial properties. No scraping needed.
- **Corporate registry hints:** `www.handelsregister.de` — search for GmbH liquidations in target cities. Copy the notice text.

**Distribution to aim for:**

```
8  × insolvency / distress notices       ← SAX RETurn angle
7  × commercial property listings        ← direct acquisition targets
5  × zoning / municipal filings          ← development potential signals
4  × mixed / ambiguous documents         ← shows the AI handles edge cases
2  × clearly out-of-scope documents      ← shows the filter working (low sax_fit_score)
```

---

## Stage 3 — Extraction Engine (`pipeline/extractor.py`)

**What it does:** Takes one raw text string, sends it to an LLM via Instructor, returns a validated `AssetProfile` object.

**Key implementation notes:**
- Use `instructor` library with `openai` or `anthropic` client — both work
- Set `response_model=AssetProfile` — Instructor handles the schema enforcement and retries
- Use a system prompt that frames the LLM as a "German real estate analyst" with context on SAX's investment criteria (>€20M, all asset classes, growth markets)
- Wrap in try/except — some documents will yield partial extractions; store them anyway with `None` fields rather than skipping

---

## Stage 4 — Storage (`pipeline/storage.py` + `database/`)

**What it does:** Persists extracted profiles to a local DuckDB file. Zero setup — DuckDB is an embedded database, no server needed.

**Key implementation notes:**
- Use `duckdb` Python library — `pip install duckdb`
- Serialize `list` fields (conversion_potential, zoning_flags, distress_signals) as JSON strings in DuckDB, deserialize on read
- Make writes idempotent: `INSERT OR REPLACE` keyed on `source_file`
- This means you can re-run the pipeline after tweaking the extractor without duplicates

---

## Stage 5 — Streamlit UI (`app/`)

**The demo flow — what you show in the room:**

**Tab 1: "Live Pipeline"**
1. Dropdown to select any document from the corpus
2. Screen A appears: raw messy text in a styled grey box
3. Button: "Extract with AI" → calls extractor live (or loads from DB if already extracted)
4. Screen B appears below: clean parameter table with ✅/❌ rule checks
5. Let the CEO read the transformation. Say nothing. Let it land.

**Tab 2: "Acquisition Targets"**
1. Full table of all extracted profiles sorted by `sax_fit_score`
2. Filter sidebar: asset class, minimum value, zoning risk level
3. Click any row → expands to full AssetProfile detail view
4. Top 3 highlighted with a "Priority Target" badge
5. One metric bar at the top: "X of Y documents flagged as viable targets above €20M"

---

## Stage 6 — Demo Polish

- **Hardcode the best result** as the default selection in the dropdown — the one with the most impressive transformation
- **Pre-run the pipeline** before the meeting so all 30 docs are already in DuckDB — no waiting, no API calls during the demo
- **Prepare the narrative:** "This would normally take your analysts 2–3 weeks. This ran in 4 minutes."
- **Prepare the "where this goes" slide:** V2 adds Kafka for real-time ingestion of new filings. V3 adds Kubernetes for continuous operation. But the business logic is identical to what you're seeing now.
- **Have the `.duckdb` file queryable** — if Bastian Bort (Investments/Acquisitions) is in the room, offer to open it in a SQL client and run a live filter query. Engineers respect that.

---

## Running the Project

```bash
# Install dependencies
pip install -r requirements.txt

# Add your API key to .env
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Run the full pipeline (populate the database)
python scripts/run_pipeline.py

# Launch the demo UI
streamlit run app/main.py
```

---

## Key Dependencies (`requirements.txt`)

```
instructor          # LLM structured extraction with Pydantic validation
anthropic           # LLM client (or use openai — extractor.py supports both)
pydantic            # Schema definition and validation
duckdb              # Embedded database — no server required
streamlit           # Demo UI
python-dotenv       # Load .env API keys
pdfplumber          # Extract text from zoning PDF filings in corpus/
```

---

## What This Demonstrates to SAX-Gruppe

| Their Problem | Your Solution |
|---|---|
| Analysts spend weeks reading municipal filings | Pipeline processes 30 docs in minutes |
| Off-market deals found too late | Distress signals flagged automatically before listing |
| Underwriting based on gut feel | Structured risk fields with zoning and ESG flags |
| No systematic coverage of insolvency pipeline | Insolvency notice corpus ingested and ranked daily |
| >€20M filter applied manually | `value_threshold_met` field enforced at extraction time |

> The demo is not about the technology. It is about showing Bernd Ruck a property in Baden-Württemberg he didn't know about, structured exactly the way his team would structure it, produced in seconds.