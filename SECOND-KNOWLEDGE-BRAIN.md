# SECOND-KNOWLEDGE-BRAIN.md — Art / Antique / Rare Card Valuation

> Self-improving domain knowledge base for `art-antique-valuation` (idea #189). Grown by `tools/knowledge_updater.py`.

## Core Concepts & Frameworks
### USPAP (Uniform Standards of Professional Appraisal Practice)
The authoritative US appraisal standard; defines scope of work, the three valuation approaches (sales-comparison, cost, income) and the duty of impartiality.

### IVS (International Valuation Standards, IVSC)
Global valuation framework defining bases of value (market value, fair value), premise of value and disclosure requirements.

### Sales-Comparison Approach
Primary method: derive value from recent arm's-length sales of comparable lots, adjusted for condition, provenance, rarity and market timing.

### PSA / BGS / CGC Grading Scales
Industry-standard 1-10 condition grading rubrics for trading cards and comics (centering, corners, edges, surface).

### Object ID / Getty Provenance Standards
International documentation standard for describing and tracing the ownership history of cultural objects, key to authenticity and anti-illicit-trade checks.


## Key Research Papers
| Title | Authors | Year | Venue | Link | Relevance |
|-------|---------|------|-------|------|-----------|
| _(seed — populate via first crawl)_ | — | — | — | — | Foundational references for Lifestyle & Personal |

The crawl pipeline will populate this table from the sources below, ranked by recency × relevance.

## State-of-the-Art Methods & Tools
- Apply the frameworks above as the scoring backbone.
- Prefer the highest available evidence tier (systematic review > meta-analysis > RCT/standard > expert opinion > blog).
- Refresh trend-sensitive figures (prices, thresholds, benchmarks) at analysis time via WebSearch.

## Authoritative Data Sources
| Source | Why it matters |
|--------|----------------|
| [Heritage Auctions results archive](https://www.ha.com/) | Public auction realized-price comparables across art, antiques and cards. |
| [Christie's / Sotheby's results](https://www.christies.com/en/results) | Blue-chip art and antique hammer prices and provenance notes. |
| [Art Loss Register](https://www.artloss.com/) | World's largest private database of stolen and looted art for due-diligence checks. |
| [PSA Price Guide / Population Report](https://www.psacard.com/priceguide) | Graded-card population and realized values. |
| [Getty Provenance Index](https://www.getty.edu/research/tools/provenance/) | Authoritative provenance and sales records for fine art. |

## Analytical Frameworks (used for scoring)
- **USPAP (Uniform Standards of Professional Appraisal Practice)**
- **IVS (International Valuation Standards, IVSC)**
- **Sales-Comparison Approach**
- **PSA / BGS / CGC Grading Scales**
- **Object ID / Getty Provenance Standards**

Scoring dimensions derived from these frameworks: Attribution confidence, Condition/Grade, Rarity & population, Provenance completeness, Market liquidity & demand, Realizable value range.

## Self-Update Protocol
- **Crawl sources:** ArXiv (econ.GN, cs.CY, stat.AP) + the authoritative domain sources above.
- **Search queries:**
- `auction price index fine art 2026`
- `trading card grading population report trends`
- `provenance research methodology cultural property`
- `art market liquidity downturn report`
- **Frequency:** weekly (cron).
- **Append format:** `### [YYYY-MM-DD] <title>` with Authors, Venue, Link, Key finding, Relevance score (0–1), Source-hash (dedupe).
- **Dedupe:** skip entries whose DOI/URL hash already exists.

## Knowledge Update Log
- **2026-06-18** — Knowledge brain v1 seeded with core frameworks, sources and crawl config for idea #189.
- **2026-06-22** — Knowledge pipeline hardened to production-grade CLI with ArXiv/domain fetchers, WebSearch backend abstraction, deduplication and dry-run mode. Live crawl deferred per resource-saving directive; pipeline is ready for scheduled production runs.
