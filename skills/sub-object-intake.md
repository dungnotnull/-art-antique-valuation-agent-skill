---
name: art-antique-valuation__sub-object-intake
description: Capture object type, attribution, dimensions, medium, marks/signatures, condition notes and supplied photos/documents into a structured, evidence-linked record.
---

## Purpose
Capture object type, attribution, dimensions, medium, marks/signatures, condition notes and supplied photos/documents into a structured record. Classify the object into one of the supported categories and determine the intended **basis of value** (market value, replacement value, fair value) per IVS.

## Inputs
- Raw user description, uploaded images/documents, prior harness outputs.
- Relevant entries from `SECOND-KNOWLEDGE-BRAIN.md`.

## Required fields by category
All material fields must be either provided by the user, derived from an image/document, or explicitly marked as an assumption.

| Category | Required fields |
|----------|-----------------|
| `fine-art` | `object_type`, `attribution`, `medium`, `dimensions`, `date_or_period`, `signature_or_marks`, `condition_notes`, `provenance_summary`, `images`, `intended_use`, `basis_of_value` |
| `antique` | `object_type`, `attribution`, `materials`, `dimensions`, `period_or_style`, `maker_marks`, `condition_notes`, `provenance_summary`, `images`, `intended_use`, `basis_of_value` |
| `rare-card` | `object_type`, `card_name`, `year`, `manufacturer`, `set`, `card_number`, `grader` (PSA/BGS/CGC), `numeric_grade`, `population` (if known), `condition_notes`, `images`, `intended_use`, `basis_of_value` |
| `other-collectible` | `object_type`, `description`, `materials`, `dimensions`, `condition_notes`, `provenance_summary`, `images`, `intended_use`, `basis_of_value` |

## Procedure
1. Parse the free-form request; do not hallucinate missing fields. For every material field, either extract a value or add it to `missing_fields`.
2. Classify `category` using explicit keywords (painting, print, sculpture, vase, card, comic, coin, etc.). If ambiguous, ask a disambiguation question and add `category` to `missing_fields`.
3. Normalize units: dimensions to `cm` and `in`; currency to ISO-4217 if supplied; grade scale to the recognized grader's 1-10 scale.
4. Build an `intake_record` where every field has a `value`, a `source` (`user` / `image` / `document` / `web` / `assumption`), and a `confidence` (`high` / `medium` / `low`).
5. If `basis_of_value` is missing, default to `market_value` and flag it as an assumption.
6. If `intended_use` is `insurance`, record that the premise is **replacement value** per IVS.
7. Raise immediate `compliance_flags` for high-risk categories (e.g., suspected looted antiquity, CITES-listed biological material, cultural-property export restrictions).
8. Return the record together with `clarifying_questions` for any `missing_fields`. Do not pass an incomplete record downstream.

## Output schema (JSON)
```json
{
  "category": "fine-art | antique | rare-card | other-collectible",
  "basis_of_value": "market_value | replacement_value | fair_value",
  "intended_use": "sale | insurance | donation | probate | curiosity | litigation",
  "object": {
    "type": "...",
    "attribution": {"artist_or_maker": "...", "attribution_method": "signed | attributed | unattributed", "confidence": "high|medium|low"},
    "medium": "...",
    "materials": ["..."],
    "dimensions": {"value": "60 x 80", "unit": "cm", "converted_in": "23.6 x 31.5"},
    "date_or_period": "...",
    "signature_or_marks": ["..."],
    "maker_marks": ["..."],
    "condition_notes": "...",
    "images": ["url_or_path"],
    "documents": ["url_or_path"]
  },
  "card": {
    "card_name": "...",
    "year": 0,
    "manufacturer": "...",
    "set": "...",
    "card_number": "...",
    "grader": "PSA | BGS | CGC | SGC | ungraded",
    "numeric_grade": 0,
    "population": 0
  },
  "provenance_summary": {"known": true, "chain": ["..."], "gaps": ["..."], "source": "user|assumption"},
  "compliance_flags": [{"severity": "high|medium|low", "issue": "...", "recommended_action": "..."}],
  "missing_fields": ["..."],
  "clarifying_questions": ["..."],
  "assumptions": ["..."],
  "evidence": [{"field": "...", "value": "...", "source": "...", "confidence": "..."}]
}
```

## Quality Gate (must all pass before the record is accepted)
- [ ] `category` and `basis_of_value` are set.
- [ ] No required field is silently assumed; any assumed field is tagged `assumption` with `low` confidence.
- [ ] Every material claim in `evidence` has a source or an explicit assumption.
- [ ] If `missing_fields` is non-empty, the output contains targeted clarifying questions and the harness must not proceed to scoring.
- [ ] High-severity `compliance_flags` are escalated before scoring.
