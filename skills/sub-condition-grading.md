---
name: art-antique-valuation__sub-condition-grading
description: Apply the relevant grading rubric (PSA/BGS/CGC for cards; conservation condition reports for art/antiques) to a normalized condition score.
---

## Purpose
Normalize object condition into a 0–100 score and, where applicable, an industry-standard grade, using recognized rubrics. The score feeds directly into the comparables engine and the composite valuation score.

## Inputs
- `intake_record` from `sub-object-intake`.
- Images, grader reports, user notes.
- Relevant rubric entries from `SECOND-KNOWLEDGE-BRAIN.md`.

## Procedure
1. Branch by `category`.

### Rare cards / comics (PSA / BGS / CGC)
- If already professionally graded on a 1–10 scale, map it linearly:
  ```
  normalized_score = numeric_grade * 10
  ```
  (PSA 10 → 100, PSA 9 → 90, …, PSA 1 → 10).
- For BGS, use the overall grade; if subgrades exist, the overall grade takes precedence and subgrades provide component detail.
- For ungraded cards, score the four standard sub-categories (centering, corners, edges, surface) out of 25 each, then convert to an estimated numeric grade.

| Sub-category | Max points | What to evaluate |
|--------------|------------|------------------|
| Centering    | 25         | Border symmetry front/back. |
| Corners      | 25         | Tip wear, whitening, fraying. |
| Edges        | 25         | Chipping, wear, print defects. |
| Surface      | 25         | Scratches, print lines, holofoil damage, stains. |

### Fine art / antiques (conservation condition)
Score the four categories below out of 25 each. Deduct for damage, fading, oxidation, prior repairs, instability or surface dirt.

| Category | Max points | What to evaluate |
|----------|------------|------------------|
| Structure / support | 25 | Canvas, panel, bronze armature, ceramic body, joinery. |
| Surface / ground layer | 25 | Paint layer, glaze, gilding, patina, varnish. |
| Restoration / retouching | 25 | Extent, quality and reversibility of previous intervention. |
| Aesthetic appearance | 25 | Visual integrity, color stability, presentation. |

2. Cross-check with supplied images and notes. If image quality is insufficient or evidence conflicts, lower confidence and add a caveat.
3. Convert the numeric score to a textual band:
   - 90–100: Excellent / Mint+
   - 75–89: Good / NM
   - 50–74: Fair
   - 25–49: Poor
   - 0–24: Severely compromised / Poor
4. Record the grade label from the original grader when applicable.

## Output schema (JSON)
```json
{
  "category": "fine-art | antique | rare-card | other-collectible",
  "normalized_score": 0,
  "grade_label": "PSA 9 | BGS 9.5 | CGC 8.0 | ungraded-estimated 7 | ...",
  "components": [
    {"name": "centering", "score": 0, "max": 25, "notes": "..."},
    {"name": "corners",   "score": 0, "max": 25, "notes": "..."}
  ],
  "condition_statement": "Excellent | Good | Fair | Poor",
  "confidence": "high | medium | low",
  "caveats": ["..."],
  "evidence": [{"field": "...", "value": "...", "source": "...", "confidence": "..."}],
  "assumptions": ["..."]
}
```

## Quality Gate (must all pass)
- [ ] Score is derived from a named rubric, not guessed.
- [ ] Component scores sum to and explain the total.
- [ ] Poor image quality, conflicting evidence or missing subgrades are flagged as caveats.
- [ ] Grade label, when present, matches a recognized 1–10 industry scale.
