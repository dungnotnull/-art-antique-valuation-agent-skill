# Cluster Integration — `lifestyle-personal` Reuse Interfaces

This document defines the shared interfaces produced by `art-antique-valuation` so
that sibling skills in the `lifestyle-personal` cluster can reuse the intake,
scoring and roadmap patterns without reimplementing them.

## Reusable Sub-Skills

| Sub-skill | Reuse value | Input contract | Output contract |
|-----------|-------------|----------------|-----------------|
| `skills/sub-object-intake.md` | Standardized object capture across collectibles, personal property and lifestyle assets. | Free-form user request + optional images/documents. | JSON `intake_record` with `category`, `basis_of_value`, `intended_use`, `object`, `missing_fields`, `compliance_flags`. |
| `skills/sub-comparables-engine.md` | Sales-comparison scoring for any asset with auction/sale comparables. | `intake_record` + `provenance_record` + `condition_record` + market data. | JSON `comparables_record` with `value_range`, `confidence`, `comparables`, `adjustments`. |
| `skills/sub-valuation-roadmap.md` | Prioritized action planning and sale-channel guidance. | All prior records + optional constraints. | JSON `roadmap_record` with `headline_score`, `actions`, `sale_recommendation`, `compliance_note`. |

## Input Schema (what sibling skills must provide)

```json
{
  "cluster_request_id": "uuid",
  "skill_request": "art-antique-valuation",
  "user_input": "...",
  "attachments": ["url_or_path"],
  "context": {
    "intended_use": "sale | insurance | donation | probate | curiosity | litigation",
    "basis_of_value": "market_value | replacement_value | fair_value",
    "currency": "USD"
  }
}
```

## Output Schema (what sibling skills can consume)

```json
{
  "cluster_request_id": "uuid",
  "skill": "art-antique-valuation",
  "status": "complete | blocked | needs_clarification",
  "deliverable": {
    "composite_score": 0,
    "confidence": "high | medium | low",
    "basis_of_value": "...",
    "value_range": {"low": 0, "central": 0, "high": 0, "currency": "USD"},
    "dimension_scores": { ... },
    "findings": "...",
    "roadmap": [ ... ],
    "sale_recommendation": { ... },
    "sources": [ ... ],
    "assumptions": [ ... ],
    "disclaimer": "..."
  },
  "shared_state": {
    "intake_record": { ... },
    "provenance_record": { ... },
    "condition_record": { ... },
    "comparables_record": { ... },
    "roadmap_record": { ... }
  }
}
```

## Wiring Patterns

### Pattern A — Direct invocation
A sibling skill calls `sub-object-intake` first, then routes to the full
`art-antique-valuation` harness when the object is art/antique/collectible.

### Pattern B — Shared state pass-through
A parent orchestrator runs `art-antique-valuation` once and stores the
`shared_state` objects in cluster context. Other skills read `intake_record` and
`roadmap_record` to avoid re-interviewing the user.

### Pattern C — Roadmap-only reuse
A sibling skill that focuses on insurance, estate planning or sale execution
reuses `sub-valuation-roadmap.md` by injecting its own `value_range` and
constraint set, benefiting from the `impact / effort` ranking formula.

## Quality Gates Inherited by the Cluster
Any skill reusing these sub-skills must enforce:
1. Intake completeness before scoring.
2. Compliance gate (`compliance_status != HALT`) before value emission.
3. Every scored claim cites a source or an explicit assumption.
4. Devil's-advocate review is documented.
5. Roadmap actions are ranked by `impact / effort`.
6. Disclaimer is present for all valuation outputs.

## Maintenance
- Update this doc whenever a sub-skill output schema changes.
- Keep `tests/test_harness.py` green to guarantee cluster consumers can rely on
the documented interfaces.
