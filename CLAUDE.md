# CLAUDE.md — Art / Antique / Rare Card Valuation

**Skill name:** `art-antique-valuation`
**Source idea:** #189 (ideas.md)
**Cluster:** Lifestyle & Personal (`lifestyle-personal`)
**Tagline:** Evidence-based appraisal of fine art, antiques and rare collectible cards against auction comparables and grading standards.
**Current phase:** Phase 5 — Integration & Cross-Skill Wiring (complete)

## Problem This Skill Solves
Collectors and small dealers routinely over- or under-value pieces because they lack access to auction comparables, provenance verification, and standardized condition grading. This skill produces a defensible valuation range with a confidence band, grounded in international auction history and recognized authentication and grading criteria.

## Harness Flow Summary
1. **Intake** → `sub-object-intake` gathers structured inputs.
2. **Research / evidence sync** → consult `SECOND-KNOWLEDGE-BRAIN.md`; refresh via WebSearch/WebFetch when available.
3. **Gate** → compliance check (`sub-provenance-research`) runs before analysis.
4. **Analysis / scoring** → `sub-comparables-engine` scores against the named frameworks.
5. **Challenge** → devil's-advocate review stress-tests assumptions and evidence.
6. **Synthesize** → `sub-valuation-roadmap` produces the scored deliverable + prioritized roadmap.

**Compliance gate:** `sub-compliance-check` (or the embedded compliance step) MUST pass before the final deliverable is emitted. Output is informational, not professional/legal/financial advice.

## Sub-skills
- `skills/sub-object-intake.md` — Capture object type, attribution, dimensions, medium, marks/signatures, condition notes and supplied photos/documents into a structured record.
- `skills/sub-provenance-research.md` — Trace ownership history, exhibition/literature references and authenticity markers; flag illicit-trade and forgery risk using Getty/Object ID standards and stolen-art registries.
- `skills/sub-comparables-engine.md` — Assemble and adjust auction/sale comparables (sales-comparison approach) into a defensible value range with confidence band.
- `skills/sub-condition-grading.md` — Apply the relevant grading rubric (PSA/BGS/CGC for cards; conservation condition reports for art/antiques) to a normalized condition score.
- `skills/sub-valuation-roadmap.md` — Produce prioritized actions to raise realizable value (conservation, grading submission, provenance documentation, optimal sale channel/timing).

## Evaluation Frameworks (world-renowned, citable)
- **USPAP (Uniform Standards of Professional Appraisal Practice)** — The authoritative US appraisal standard; defines scope of work, the three valuation approaches (sales-comparison, cost, income) and the duty of impartiality.
- **IVS (International Valuation Standards, IVSC)** — Global valuation framework defining bases of value (market value, fair value), premise of value and disclosure requirements.
- **Sales-Comparison Approach** — Primary method: derive value from recent arm's-length sales of comparable lots, adjusted for condition, provenance, rarity and market timing.
- **PSA / BGS / CGC Grading Scales** — Industry-standard 1-10 condition grading rubrics for trading cards and comics (centering, corners, edges, surface).
- **Object ID / Getty Provenance Standards** — International documentation standard for describing and tracing the ownership history of cultural objects, key to authenticity and anti-illicit-trade checks.

## Tools Required
- `WebSearch`, `WebFetch` — live evidence and trend updates (graceful degradation to the knowledge brain when unavailable).
- `Read`, `Write` — load the knowledge brain; emit the deliverable.
- `Bash` — run `tools/knowledge_updater.py` (crawl4ai pipeline).

## Knowledge Sources
- **ArXiv / academic categories:** econ.GN, cs.CY, stat.AP
- [Heritage Auctions results archive](https://www.ha.com/) — Public auction realized-price comparables across art, antiques and cards.
- [Christie's / Sotheby's results](https://www.christies.com/en/results) — Blue-chip art and antique hammer prices and provenance notes.
- [Art Loss Register](https://www.artloss.com/) — World's largest private database of stolen and looted art for due-diligence checks.
- [PSA Price Guide / Population Report](https://www.psacard.com/priceguide) — Graded-card population and realized values.
- [Getty Provenance Index](https://www.getty.edu/research/tools/provenance/) — Authoritative provenance and sales records for fine art.

## Supporting Tools
- `tools/knowledge_updater.py` — crawl4ai + WebSearch pipeline that grows `SECOND-KNOWLEDGE-BRAIN.md` (recommended weekly cron).

## Active Development Tasks
- [x] Scaffold all required deliverables
- [x] Define frameworks, sub-skills and scoring dimensions
- [x] Author knowledge brain v1 and crawl pipeline
- [x] Expand knowledge brain via first scheduled crawl
- [x] Add adversarial/edge-case test scenarios beyond the initial 5

## Related Root Docs
- `PROJECT-detail.md` — full technical spec
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — phase roadmap
- `SECOND-KNOWLEDGE-BRAIN.md` — living domain knowledge base
