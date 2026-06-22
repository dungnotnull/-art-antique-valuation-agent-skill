"""Harness-level tests for the art-antique-valuation skill.

These tests do not require live WebSearch/WebFetch; they validate the documented
scoring formulas, rubric mappings, gate checklists and scenario catalog.
"""
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"


def _read(name: str) -> str:
    return (SKILLS_DIR / name).read_text(encoding="utf-8")


def composite_score(dims: dict) -> int:
    """Mirror the documented composite-score formula from main.md and sub-valuation-roadmap.md."""
    return round(
        0.20 * dims["attribution_confidence"]
        + 0.20 * dims["condition_grade"]
        + 0.15 * dims["rarity_population"]
        + 0.15 * dims["provenance_completeness"]
        + 0.15 * dims["market_liquidity_demand"]
        + 0.15 * dims["realizable_value_range"]
    )


def confidence_discount(attribution: int, condition: int, comparable_count: int, provenance_gaps: int) -> float:
    """Mirror the confidence-discount formula from sub-comparables-engine.md."""
    return round(
        0.15
        + 0.10 * (1 - attribution / 100)
        + 0.10 * (1 - condition / 100)
        + 0.10 * (1 - min(comparable_count, 10) / 10)
        + 0.05 * (1 if provenance_gaps > 0 else 0),
        3,
    )


class TestScoringFormulas:
    def test_composite_score_matches_documented_weights(self):
        dims = {
            "attribution_confidence": 70,
            "condition_grade": 80,
            "rarity_population": 60,
            "provenance_completeness": 50,
            "market_liquidity_demand": 75,
            "realizable_value_range": 65,
        }
        expected = round(0.20 * 70 + 0.20 * 80 + 0.15 * 60 + 0.15 * 50 + 0.15 * 75 + 0.15 * 65)
        assert composite_score(dims) == expected
        assert 0 <= expected <= 100

    def test_confidence_discount_widens_with_uncertainty(self):
        low = confidence_discount(90, 90, 8, 0)
        high = confidence_discount(40, 40, 1, 2)
        assert high > low
        assert 0 < low < 1
        assert 0 < high < 1


class TestConditionGrading:
    def test_psa_grade_linear_mapping(self):
        assert psa_to_normalized(10) == 100
        assert psa_to_normalized(9) == 90
        assert psa_to_normalized(1) == 10

    def test_ungraded_card_components_sum(self):
        components = [
            {"name": "centering", "score": 20, "max": 25},
            {"name": "corners", "score": 18, "max": 25},
            {"name": "edges", "score": 22, "max": 25},
            {"name": "surface", "score": 19, "max": 25},
        ]
        total = sum(c["score"] for c in components)
        assert total == 79
        assert all(c["score"] <= c["max"] for c in components)

    def test_art_condition_components_sum(self):
        components = [
            {"name": "structure", "score": 22, "max": 25},
            {"name": "surface", "score": 20, "max": 25},
            {"name": "restoration", "score": 18, "max": 25},
            {"name": "aesthetic", "score": 21, "max": 25},
        ]
        assert sum(c["score"] for c in components) == 81


def psa_to_normalized(grade: int) -> int:
    return grade * 10


class TestRoadmapRanking:
    def test_roi_score_prefers_high_impact_low_effort(self):
        actions = [
            {"action": "Easy win", "effort": 1, "impact": 5},
            {"action": "Hard win", "effort": 5, "impact": 5},
            {"action": "Low value", "effort": 1, "impact": 1},
        ]
        ranked = sorted(actions, key=lambda a: a["impact"] / a["effort"], reverse=True)
        assert ranked[0]["action"] == "Easy win"
        assert ranked[-1]["action"] == "Low value"


class TestMarkdownGateCoverage:
    def test_main_md_contains_all_quality_gates(self):
        text = _read("main.md")
        required = [
            "Intake complete",
            "Compliance check passed",
            "Every dimension cites a source",
            "Devil's-advocate review",
            "Roadmap is prioritized",
            "Evidence hierarchy respected",
            "Disclaimer present",
        ]
        for phrase in required:
            assert phrase in text, f"Missing gate phrase: {phrase}"

    def test_main_md_has_composite_formula(self):
        text = _read("main.md")
        assert "0.20 * attribution_confidence" in text
        assert "0.20 * condition_grade" in text

    def test_all_sub_skills_have_output_schema_and_gate(self):
        for path in SKILLS_DIR.glob("sub-*.md"):
            text = path.read_text(encoding="utf-8")
            assert "## Output schema" in text, f"{path.name} missing output schema"
            assert "## Quality Gate" in text, f"{path.name} missing quality gate"

    def test_comparables_engine_has_confidence_formula(self):
        text = _read("sub-comparables-engine.md")
        assert "confidence_discount =" in text
        assert "value_low" in text
        assert "value_high" in text

    def test_provenance_has_halt_triggers(self):
        text = _read("sub-provenance-research.md")
        assert "HALT triggers" in text
        assert "compliance_status == HALT" not in text  # this rule lives in main.md
        assert "compliance_status" in text


class TestScenarioCatalog:
    def test_at_least_five_scenarios(self):
        text = (ROOT / "tests" / "test-scenarios.md").read_text(encoding="utf-8")
        scenarios = re.findall(r"### Scenario \d+:", text)
        assert len(scenarios) >= 5

    def test_regression_checklist_present(self):
        text = (ROOT / "tests" / "test-scenarios.md").read_text(encoding="utf-8")
        assert "## Regression Checklist" in text
        for item in ["All gates enforced", "Scores trace to citations", "Devil's-advocate review present"]:
            assert item in text


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
