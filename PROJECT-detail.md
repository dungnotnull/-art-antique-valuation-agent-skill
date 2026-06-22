# PROJECT-detail.md — Art / Antique / Rare Card Valuation

## Executive Summary
`art-antique-valuation` is a harness skill in the **Lifestyle & Personal** cluster (idea #189). Evidence-based appraisal of fine art, antiques and rare collectible cards against auction comparables and grading standards. It executes a research-first, framework-grounded workflow that ends in a multi-dimensional score and a prioritized, effort/impact-ranked improvement roadmap.

> **Disclaimer:** This skill provides informational analysis only and is **not** professional legal, financial, tax or accounting advice. Verify with a licensed professional before acting.

## Problem Statement
Collectors and small dealers routinely over- or under-value pieces because they lack access to auction comparables, provenance verification, and standardized condition grading. This skill produces a defensible valuation range with a confidence band, grounded in international auction history and recognized authentication and grading criteria.

## Target Users & Use Cases
- Practitioners, learners and small teams who need an expert-grade, evidence-based analysis without hiring a specialist.
- Trigger examples:
  - "I inherited an oil painting signed 'J. Smith' 60x80cm, want its value" → the skill runs its full harness and returns a scored deliverable.
  - "What is my PSA 9 1986 rookie card worth?" → the skill runs its full harness and returns a scored deliverable.
  - "This 'antique' vase may be a reproduction" → the skill runs its full harness and returns a scored deliverable.
  - "Bought a sculpture cheap at a flea market" → the skill runs its full harness and returns a scored deliverable.
  - "I need a value for insurance" → the skill runs its full harness and returns a scored deliverable.

## Harness Architecture
```
User input
   │
   ▼
[Stage 1 Intake]  sub-object-intake
   │
   ▼
[Stage 2 Research]  SECOND-KNOWLEDGE-BRAIN.md + WebSearch/WebFetch
   │
   ▼
[Stage 3 Gate]  sub-provenance-research
   │
   ▼
[Stage 4 Scoring]  sub-comparables-engine  → score vs frameworks
   │
   ▼
[Stage 5 Challenge]  devil's-advocate review
   │
   ▼
[Stage 6 Synthesis]  sub-valuation-roadmap  → scored report + roadmap
```

## Full Sub-Skill Catalog
### `sub-object-intake`
- **Purpose:** Capture object type, attribution, dimensions, medium, marks/signatures, condition notes and supplied photos/documents into a structured record.
- **Inputs:** structured fields from prior stages / user.
- **Outputs:** structured record consumed by the next stage.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** outputs are complete, evidence-linked, and assumptions are explicit.
### `sub-provenance-research`
- **Purpose:** Trace ownership history, exhibition/literature references and authenticity markers; flag illicit-trade and forgery risk using Getty/Object ID standards and stolen-art registries.
- **Inputs:** structured fields from prior stages / user.
- **Outputs:** structured record consumed by the next stage.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** outputs are complete, evidence-linked, and assumptions are explicit.
### `sub-comparables-engine`
- **Purpose:** Assemble and adjust auction/sale comparables (sales-comparison approach) into a defensible value range with confidence band.
- **Inputs:** structured fields from prior stages / user.
- **Outputs:** structured record consumed by the next stage.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** outputs are complete, evidence-linked, and assumptions are explicit.
### `sub-condition-grading`
- **Purpose:** Apply the relevant grading rubric (PSA/BGS/CGC for cards; conservation condition reports for art/antiques) to a normalized condition score.
- **Inputs:** structured fields from prior stages / user.
- **Outputs:** structured record consumed by the next stage.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** outputs are complete, evidence-linked, and assumptions are explicit.
### `sub-valuation-roadmap`
- **Purpose:** Produce prioritized actions to raise realizable value (conservation, grading submission, provenance documentation, optimal sale channel/timing).
- **Inputs:** structured fields from prior stages / user.
- **Outputs:** structured record consumed by the next stage.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** outputs are complete, evidence-linked, and assumptions are explicit.

## Evaluation Frameworks
1. **USPAP (Uniform Standards of Professional Appraisal Practice)** — The authoritative US appraisal standard; defines scope of work, the three valuation approaches (sales-comparison, cost, income) and the duty of impartiality.
2. **IVS (International Valuation Standards, IVSC)** — Global valuation framework defining bases of value (market value, fair value), premise of value and disclosure requirements.
3. **Sales-Comparison Approach** — Primary method: derive value from recent arm's-length sales of comparable lots, adjusted for condition, provenance, rarity and market timing.
4. **PSA / BGS / CGC Grading Scales** — Industry-standard 1-10 condition grading rubrics for trading cards and comics (centering, corners, edges, surface).
5. **Object ID / Getty Provenance Standards** — International documentation standard for describing and tracing the ownership history of cultural objects, key to authenticity and anti-illicit-trade checks.

## Scoring Dimensions
- Attribution confidence
- Condition/Grade
- Rarity & population
- Provenance completeness
- Market liquidity & demand
- Realizable value range

Each dimension is scored 0–100 (or 1–5) with an explicit rationale and at least one cited source or stated assumption. The composite score is a transparent weighted aggregate; weights are disclosed.

## Skill File Format Specification
- Frontmatter: `name` (= `art-antique-valuation`), `description` (one line).
- Required sections: Role & Persona, Workflow (Harness Flow), Sub-skills Available, Tools, Output Format, Quality Gates.

## E2E Execution Flow
1. Parse request; classify the task and detect missing inputs (ask targeted questions).
2. Run intake sub-skill → structured profile.
3. Sync evidence from the knowledge brain; refresh via WebSearch/WebFetch when available; otherwise signal degraded mode.
4. Run the compliance gate — **halt and route out** on red flags.
5. Score against frameworks; record evidence per dimension.
6. Devil's-advocate pass: challenge weakest assumptions, seek disconfirming evidence.
7. Synthesize the deliverable: scored report + prioritized roadmap (effort × impact).
8. Run quality gates; only then present output.

## SECOND-KNOWLEDGE-BRAIN Integration
- Sources: ArXiv (econ.GN, cs.CY, stat.AP) + the authoritative domain sources listed in `CLAUDE.md`.
- Crawl config and append format are defined in `tools/knowledge_updater.py` and `SECOND-KNOWLEDGE-BRAIN.md`.

## Supporting Tools Spec — `knowledge_updater.py`
- **Inputs:** crawl query list (below), source URLs, last-run timestamp.
- **Outputs:** appended, de-duplicated, date-stamped entries in `SECOND-KNOWLEDGE-BRAIN.md`.
- **Schedule:** weekly cron.
- **Crawl queries:** `auction price index fine art 2026`, `trading card grading population report trends`, `provenance research methodology cultural property`, `art market liquidity downturn report`

## Quality Gates (must all pass before output)
- Every scored dimension cites a source or states an assumption.
- The applicable safety/compliance gate has passed.
- The devil's-advocate review has been performed and its objections addressed.
- The roadmap items are prioritized by effort × impact and are actionable.
- Evidence hierarchy respected (systematic review > meta-analysis > RCT/standard > expert opinion > blog).

## Test Scenarios
1. **Single oil painting appraisal** — *User:* "I inherited an oil painting signed 'J. Smith' 60x80cm, want its value" → *Skill:* Runs intake, provenance research, comparables and condition grading; returns a market-value range with confidence band and provenance caveats. (**Gate:** Comparables must be arm's-length sales <36 months old or value flagged low-confidence.)
2. **Graded rookie card** — *User:* "What is my PSA 9 1986 rookie card worth?" → *Skill:* Pulls PSA population + realized-price comparables, normalizes for grade, returns range and best sale channel. (**Gate:** Grade-population data must be cited with date stamp.)
3. **Suspected forgery** — *User:* "This 'antique' vase may be a reproduction" → *Skill:* Runs provenance + authenticity-marker checks, flags forgery indicators, recommends scientific testing before valuation. (**Gate:** No firm value emitted while authenticity is unresolved.)
4. **Possibly stolen item** — *User:* "Bought a sculpture cheap at a flea market" → *Skill:* Cross-checks Art Loss Register descriptors, warns on illicit-trade risk and legal exposure. (**Gate:** Compliance note required before any resale advice.)
5. **Insurance vs market value** — *User:* "I need a value for insurance" → *Skill:* Distinguishes replacement value (insurance) from market value (IVS bases of value) and documents the premise used. (**Gate:** Basis-of-value and intended-use must be explicitly stated.)

## Key Design Decisions
1. Research-first: no scored claim without a citation or explicit assumption.
2. Framework-grounded: scoring uses only the named world-renowned frameworks above.
3. Composable sub-skills (≥3) with explicit gates between stages.
4. Self-improving knowledge brain via the crawl pipeline.
5. Graceful degradation when WebSearch/WebFetch are unavailable.
