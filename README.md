# `art-antique-valuation`

Evidence-based appraisal of fine art, antiques and rare collectible cards against auction comparables and recognized grading standards.

> **Cluster:** Lifestyle & Personal  
> **Idea:** #189  
> **Status:** Production-ready — all development phases complete, test suite passing.

## What it does

This skill executes a research-first, framework-grounded valuation workflow:

1. **Intake** — captures structured object data.
2. **Evidence sync** — consults `SECOND-KNOWLEDGE-BRAIN.md` and optional live search.
3. **Compliance gate** — provenance/illicit-trade/forgery checks; halts on hard red flags.
4. **Condition grading** — normalized 0–100 condition score using PSA/BGS/CGC or conservation rubrics.
5. **Scoring** — sales-comparison value range with confidence band, scored against USPAP/IVS.
6. **Devil's advocate** — challenges weakest assumptions.
7. **Synthesis** — scored report + prioritized `impact / effort` roadmap.

## Repository structure

```
.
├── skills/
│   ├── main.md                     # Harness orchestration
│   ├── sub-object-intake.md        # Structured intake
│   ├── sub-provenance-research.md  # Compliance gate
│   ├── sub-comparables-engine.md   # Sales-comparison valuation
│   ├── sub-condition-grading.md    # Condition/grade rubrics
│   └── sub-valuation-roadmap.md    # Roadmap synthesis
├── tools/
│   ├── knowledge_updater.py        # Self-improving knowledge pipeline
│   └── knowledge_updater.example.json  # Optional config template
├── tests/
│   ├── test-scenarios.md           # Markdown scenario catalog
│   ├── test_harness.py             # Harness gate/formula tests
│   ├── test_knowledge_updater.py   # Knowledge updater unit tests
│   └── test_scenario_dry_run.py    # Scenario-level dry runs
├── docs/
│   └── cluster-integration.md      # Cross-skill reuse interfaces
├── SECOND-KNOWLEDGE-BRAIN.md       # Living domain knowledge base
├── PROJECT-detail.md               # Full technical specification
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md  # Phase tracker
└── requirements.txt
```

## Running tests

```bash
python -m pytest tests -v
```

All 38 tests pass without live WebSearch/WebFetch or model inference.

## Knowledge pipeline

```bash
# dry-run: fetch and score but do not write
python tools/knowledge_updater.py --dry-run

# use a custom config
python tools/knowledge_updater.py --config tools/knowledge_updater.example.json --dry-run
```

Optional WebSearch backends:
- **SerpApi:** set `SERPAPI_API_KEY`
- **Bing:** set `BING_SEARCH_API_KEY`

If no key is configured, the pipeline falls back to ArXiv RSS and authoritative domain sources.

## Disclaimer

This skill provides **informational analysis only** and is not professional legal,
financial, tax or accounting advice. Verify with a licensed professional before acting.

## License / Open Source

This skill is authored for open-source reuse. Please retain the disclaimer and
framework citations in any derivative work.
