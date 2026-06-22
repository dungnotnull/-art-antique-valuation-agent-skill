# tests/test-scenarios.md — Art / Antique / Rare Card Valuation

Scenario-based tests for `art-antique-valuation` (idea #189). Minimum 5; 7 provided (incl. degraded-mode and insufficient-input edge cases).

### Scenario 1: Single oil painting appraisal
- **User input:** "I inherited an oil painting signed 'J. Smith' 60x80cm, want its value"
- **Expected harness behavior:** Runs intake, provenance research, comparables and condition grading; returns a market-value range with confidence band and provenance caveats.
- **Frameworks exercised:** USPAP (Uniform Standards of Professional Appraisal Practice), IVS (International Valuation Standards, IVSC), Sales-Comparison Approach
- **Quality gate under test:** Comparables must be arm's-length sales <36 months old or value flagged low-confidence.
- **Pass criteria:** scored output produced, gate enforced, every dimension evidence-linked or assumption-marked, prioritized roadmap included.
### Scenario 2: Graded rookie card
- **User input:** "What is my PSA 9 1986 rookie card worth?"
- **Expected harness behavior:** Pulls PSA population + realized-price comparables, normalizes for grade, returns range and best sale channel.
- **Frameworks exercised:** USPAP (Uniform Standards of Professional Appraisal Practice), IVS (International Valuation Standards, IVSC), Sales-Comparison Approach
- **Quality gate under test:** Grade-population data must be cited with date stamp.
- **Pass criteria:** scored output produced, gate enforced, every dimension evidence-linked or assumption-marked, prioritized roadmap included.
### Scenario 3: Suspected forgery
- **User input:** "This 'antique' vase may be a reproduction"
- **Expected harness behavior:** Runs provenance + authenticity-marker checks, flags forgery indicators, recommends scientific testing before valuation.
- **Frameworks exercised:** USPAP (Uniform Standards of Professional Appraisal Practice), IVS (International Valuation Standards, IVSC), Sales-Comparison Approach
- **Quality gate under test:** No firm value emitted while authenticity is unresolved.
- **Pass criteria:** scored output produced, gate enforced, every dimension evidence-linked or assumption-marked, prioritized roadmap included.
### Scenario 4: Possibly stolen item
- **User input:** "Bought a sculpture cheap at a flea market"
- **Expected harness behavior:** Cross-checks Art Loss Register descriptors, warns on illicit-trade risk and legal exposure.
- **Frameworks exercised:** USPAP (Uniform Standards of Professional Appraisal Practice), IVS (International Valuation Standards, IVSC), Sales-Comparison Approach
- **Quality gate under test:** Compliance note required before any resale advice.
- **Pass criteria:** scored output produced, gate enforced, every dimension evidence-linked or assumption-marked, prioritized roadmap included.
### Scenario 5: Insurance vs market value
- **User input:** "I need a value for insurance"
- **Expected harness behavior:** Distinguishes replacement value (insurance) from market value (IVS bases of value) and documents the premise used.
- **Frameworks exercised:** USPAP (Uniform Standards of Professional Appraisal Practice), IVS (International Valuation Standards, IVSC), Sales-Comparison Approach
- **Quality gate under test:** Basis-of-value and intended-use must be explicitly stated.
- **Pass criteria:** scored output produced, gate enforced, every dimension evidence-linked or assumption-marked, prioritized roadmap included.
### Scenario 6: Degraded mode (offline)
- **User input:** any of the above with WebSearch/WebFetch unavailable.
- **Expected behavior:** skill falls back to `SECOND-KNOWLEDGE-BRAIN.md`, explicitly signals degraded mode, and still enforces all gates.
- **Pass criteria:** no fabricated live data; degradation disclosed.

### Scenario 7: Insufficient input
- **User input:** a vague one-line request missing key fields.
- **Expected behavior:** intake sub-skill asks targeted clarifying questions instead of assuming.
- **Pass criteria:** no scored output until required inputs are gathered.


## Regression Checklist
- [x] All gates enforced on every path (compliance).
- [x] Scores trace to citations or explicit assumptions.
- [x] Devil's-advocate review present.
- [x] Roadmap prioritized by impact × effort.
- [x] Disclaimer present where applicable.
