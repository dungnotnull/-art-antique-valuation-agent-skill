---
name: art-antique-valuation__sub-comparables-engine
description: Assemble and adjust auction/sale comparables (sales-comparison approach) into a defensible value range with confidence band, per USPAP and IVS.
---

## Purpose
Derive a realizable value range for the object using the **Sales-Comparison Approach** (USPAP / IVS). Select comparable lots, adjust for differences, reject outliers, and compute a confidence band.

## Inputs
- `intake_record` from `sub-object-intake`.
- `provenance_record` from `sub-provenance-research`.
- `condition_record` from `sub-condition-grading` (optional at this stage but preferred).
- Relevant market data from `SECOND-KNOWLEDGE-BRAIN.md` and live `WebSearch` / `WebFetch` results.

## Procedure
1. **Source comparables** from authoritative auction archives (Heritage Auctions, Christie's, Sotheby's, Bonhams) and specialist databases. When public archives are unavailable, use the knowledge brain and state the fallback as an assumption.
2. **Filter** by category, attribution, medium/set, grade/condition and approximate dimensions. Prefer arm's-length sales within the last 36 months. If no recent comparable exists, retain older sales and flag low-confidence.
3. **Normalize** each comparable: convert hammer + buyer's premium to total realized price, normalize currency to USD (or the requested valuation currency), convert units, record date/venue/lot URL.
4. **Adjust** each comparable for differences from the subject. Document every adjustment. Adjustment categories:
   - **Condition / grade**: percentage adjustment derived from the condition score delta. One PSA grade step ≈ 10% of value for cards; analogous condition bands for art/antiques.
   - **Provenance**: premium/penalty for documented exhibition/literature or gaps.
   - **Rarity / population**: scarcity multiplier when population data exists.
   - **Size / material**: small scaling factor for materially different dimensions or medium.
   - **Market timing**: price-index adjustment when the comparable sale is >12 months old.
5. **Reject outliers** beyond ±2 standard deviations from the peer group, or inconsistent with attribution. Record excluded lots.
6. **Compute central estimate** as the weighted mean of adjusted comparable values. Weight = similarity score (0–1) based on attribution, grade/condition, date proximity and provenance match.
7. **Compute confidence band** using the formula below. The discount widens with uncertainty.

```
confidence_discount = 0.15
  + 0.10 * (1 - attribution_confidence / 100)
  + 0.10 * (1 - condition_score / 100)
  + 0.10 * (1 - min(comparable_count, 10) / 10)
  + 0.05 * (1 if provenance_gaps > 0 else 0)
  + 0.15 * (1 if oldest_comparable_months > 36 else 0)

value_low    = central_estimate * (1 - confidence_discount)
value_high   = central_estimate * (1 + confidence_discount)
```

8. **Assign confidence label**: `high` if discount ≤ 0.25, `medium` if ≤ 0.45, otherwise `low`.
9. If `provenance_record.compliance_status == HALT`, do not emit a value range; return only an explanatory placeholder.

## Output schema (JSON)
```json
{
  "method": "sales-comparison",
  "basis_of_value": "market_value | replacement_value | fair_value",
  "currency": "USD",
  "value_range": {
    "low": 0,
    "central": 0,
    "high": 0
  },
  "confidence": "high | medium | low",
  "confidence_discount": 0.0,
  "comparable_count": 0,
  "comparables": [
    {
      "source": "Heritage Auctions Lot 12345",
      "date": "2026-02-15",
      "venue": "Heritage Auctions",
      "url": "https://...",
      "realized_total": 0,
      "adjusted_value": 0,
      "similarity": 0.0,
      "adjustments": [{"factor": "condition", "direction": "+|-", "magnitude": 0.0}]
    }
  ],
  "outliers_excluded": [{"source": "...", "reason": "..."}],
  "adjustment_summary": [{"factor": "...", "average_magnitude": 0.0}],
  "evidence": [{"field": "...", "value": "...", "source": "...", "confidence": "..."}],
  "assumptions": ["..."]
}
```

## Quality Gate (must all pass)
- [ ] At least one comparable is sourced, or a documented fallback assumption is used.
- [ ] Every comparable is arm's-length or explicitly flagged.
- [ ] Every adjustment is explicit, justified and direction-signed.
- [ ] Confidence discount is computed from the documented risk factors.
- [ ] No value range is emitted when the compliance gate is `HALT`.
- [ ] All sources respect the evidence hierarchy.
