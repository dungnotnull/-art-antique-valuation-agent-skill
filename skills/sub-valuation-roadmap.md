---
name: art-antique-valuation__sub-valuation-roadmap
description: Produce prioritized actions to raise realizable value (conservation, grading submission, provenance documentation, optimal sale channel/timing).
---

## Purpose
Convert the intake, provenance, condition and comparables results into a final, prioritized, actionable roadmap that maximizes realizable value while respecting compliance constraints.

## Inputs
- `intake_record` from `sub-object-intake`.
- `provenance_record` from `sub-provenance-research`.
- `condition_record` from `sub-condition-grading`.
- `comparables_record` from `sub-comparables-engine`.
- Relevant best-practice entries from `SECOND-KNOWLEDGE-BRAIN.md`.

## Procedure
1. **Identify candidate actions** from the list below, selecting only those relevant to the object and compliance state:
   - Authentication / attribution upgrade (scholar opinion, catalogue raisonné entry, scientific testing).
   - Grading submission (cards/comics) to PSA/BGS/CGC/SGC.
   - Conservation / stabilization by a qualified conservator.
   - Provenance documentation (bills of sale, exhibition records, import/export licenses).
   - Compliance clearance (CITES permit, cultural-property export certificate, stolen-art check clearance).
   - Sale-channel optimization (specialist auction, private sale, marketplace, consignment timing).
2. For each action, estimate:
   - `effort` (1 = low, 5 = very high).
   - `impact` (1 = minimal, 5 = transformative uplift to realizable value).
   - `cost` estimate if known.
   - `dependencies` on other actions or external approvals.
3. **Compute priority** using an efficiency score that rewards high impact and low effort:
   ```
   roi_score = impact / effort
   ```
   Rank descending by `roi_score`; tie-break by higher `impact`. If a blocked dependency exists, flag the action as `blocked_until`.
4. Estimate the **expected value uplift** for each action, either as a percentage of the current value range or as a qualitative band.
5. Provide a **sale recommendation** with:
   - Best channels (auction house, dealer network, marketplace, direct sale).
   - Timing guidance (seasonality, auction calendar, liquidity cycles).
   - Caveats tied to compliance flags.
6. Include a **compliance note** if `provenance_record.compliance_status` is `WARN` or `HALT`, and a fixed legal/financial disclaimer.

## Output schema (JSON)
```json
{
  "headline_score": {
    "composite": 0,
    "confidence": "high | medium | low",
    "basis_of_value": "..."
  },
  "value_range": {
    "low": 0,
    "central": 0,
    "high": 0,
    "currency": "USD"
  },
  "dimension_scores": {
    "attribution_confidence":  {"score": 0, "weight": 0.20, "rationale": "...", "source": "..."},
    "condition_grade":         {"score": 0, "weight": 0.20, "rationale": "...", "source": "..."},
    "rarity_population":       {"score": 0, "weight": 0.15, "rationale": "...", "source": "..."},
    "provenance_completeness": {"score": 0, "weight": 0.15, "rationale": "...", "source": "..."},
    "market_liquidity_demand": {"score": 0, "weight": 0.15, "rationale": "...", "source": "..."},
    "realizable_value_range":  {"score": 0, "weight": 0.15, "rationale": "...", "source": "..."}
  },
  "actions": [
    {
      "rank": 1,
      "action": "...",
      "category": "authentication | grading | conservation | provenance | compliance | sale-channel",
      "effort": 1,
      "impact": 5,
      "roi_score": 5.0,
      "dependencies": ["..."],
      "blocked_until": "...",
      "expected_value_uplift": "...",
      "rationale": "...",
      "citation": "..."
    }
  ],
  "sale_recommendation": {
    "channels": ["..."],
    "timing": "...",
    "caveats": "..."
  },
  "compliance_note": "...",
  "disclaimer": "This analysis is informational only and is not professional legal, financial, tax or accounting advice. Verify with a licensed professional before acting."
}
```

### Composite score calculation
```
composite = round(
  0.20 * attribution_confidence
  + 0.20 * condition_grade
  + 0.15 * rarity_population
  + 0.15 * provenance_completeness
  + 0.15 * market_liquidity_demand
  + 0.15 * realizable_value_range
)
```
Weights are fixed and disclosed. Adjust only if the user explicitly requests a different IVS/USPAP premise; document any change.

## Quality Gate (must all pass)
- [ ] Every action has `effort`, `impact`, `roi_score`, `rationale` and `citation`.
- [ ] Ranking is justified by the documented `roi_score` formula.
- [ ] `compliance_note` is present if any `WARN` or `HALT` exists.
- [ ] Roadmap items are actionable and tied to the specific object, not generic copy.
- [ ] The disclaimer is included verbatim or by reference.
