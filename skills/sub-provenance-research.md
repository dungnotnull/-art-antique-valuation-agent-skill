---
name: art-antique-valuation__sub-provenance-research
description: Trace ownership history, exhibition/literature references and authenticity markers; flag illicit-trade and forgery risk using Getty/Object ID standards and stolen-art registries.
---

## Purpose
Trace ownership history, exhibition/literature references and authenticity markers; flag illicit-trade and forgery risk using Getty/Object ID standards and stolen-art registries. This sub-skill is the **compliance gate**: on a hard red flag it must halt the harness before any valuation is emitted.

## Inputs
- `intake_record` from `sub-object-intake`.
- Relevant entries from `SECOND-KNOWLEDGE-BRAIN.md`.
- `WebSearch` / `WebFetch` results for live stolen-art, auction-catalogue and literature checks (graceful degradation if unavailable).

## Procedure
1. **Ownership chain** — Reconstruct provenance from the intake record, documents and external sources. Each link must have a party, date or date range, event (acquisition, sale, inheritance), and supporting evidence. Mark any gaps explicitly.
2. **Exhibition / literature** — Search catalogues raisonnés, museum exhibition histories, auction-house catalogues and scholarly databases. Record matches, near-matches and absence.
3. **Authenticity markers** — Verify consistency between the object's medium, materials, marks, signature, style and period. Flag anachronisms, mismatched signatures or modern materials in purportedly older objects.
4. **Illicit-trade checks** — Query, where data is accessible:
   - Art Loss Register descriptors (artist/title/dimensions).
   - INTERPOL Works of Art database public notices.
   - FBI Art Crime Team / NSAF stolen-art resources.
   - UNESCO 1970 Convention threshold for antiquities lacking documented export before 1970.
   - CITES / endangered-species material checks for ivory, rhino horn, tortoiseshell, coral, etc.
   - Source-country export restrictions for cultural property.
5. **Forgery / reproduction checks** — Compare against known auction records and published examples. Flag repeated warning signs (modern pigments, laser-printed signatures, anachronistic materials, inconsistent patina). Recommend scientific testing when unresolved.
6. **Compliance status** — Assign exactly one of:
   - `PASS`: no material concerns.
   - `WARN`: concerns exist but valuation may proceed with caveats and mandatory next steps.
   - `HALT`: do not produce a value; route to compliance-first response.

### HALT triggers (non-exhaustive)
- Object matches a reported stolen or looted work.
- CITES-listed biological material without valid documentation.
- Antiquity with no documented lawful export and likely source-country claim.
- Unresolved authenticity combined with intent to sell.
- User requests valuation of an object whose lawful ownership cannot be established.

## Output schema (JSON)
```json
{
  "compliance_status": "PASS | WARN | HALT",
  "status_rationale": "...",
  "ownership_chain": [
    {"party": "...", "date_range": "...", "event": "...", "evidence": "...", "confidence": "high|medium|low"}
  ],
  "provenance_gaps": ["..."],
  "exhibition_literature": [
    {"reference": "...", "source": "...", "date": "...", "match_type": "exact | possible | none"}
  ],
  "authenticity_markers": [
    {"marker": "...", "status": "consistent | inconsistent | unknown", "evidence": "...", "confidence": "..."}
  ],
  "illicit_trade_check": {
    "sources_checked": ["..."],
    "flags": [{"severity": "high|medium|low", "issue": "...", "recommended_action": "..."}]
  },
  "forgery_indicators": {
    "risk_score": 0,
    "indicators": ["..."],
    "recommended_tests": ["..."]
  },
  "compliance_note": "...",
  "evidence": [{"field": "...", "value": "...", "source": "...", "confidence": "..."}],
  "assumptions": ["..."]
}
```

## Quality Gate (must all pass)
- [ ] `compliance_status` is set and justified by evidence.
- [ ] Every flag links to a named source or an explicit assumption.
- [ ] HALT conditions stop downstream scoring and valuation; the harness emits a compliance-only response.
- [ ] WARN conditions include mandatory next steps and a compliance note in the final report.
- [ ] Evidence hierarchy is respected (systematic review / meta-analysis > authoritative standard > expert opinion > blog).
