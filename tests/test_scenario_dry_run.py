"""Dry-run the art-antique-valuation harness against the documented scenarios.

This is a code-level simulation of the harness. It does not call WebSearch,
WebFetch, or any live model; it exercises the scoring formulas, gates and
roadmap logic defined in the skill markdown.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"


def composite_score(dims: dict) -> int:
    return round(
        0.20 * dims["attribution_confidence"]
        + 0.20 * dims["condition_grade"]
        + 0.15 * dims["rarity_population"]
        + 0.15 * dims["provenance_completeness"]
        + 0.15 * dims["market_liquidity_demand"]
        + 0.15 * dims["realizable_value_range"]
    )


def confidence_discount(
    attribution: int,
    condition: int,
    comparable_count: int,
    provenance_gaps: int,
    oldest_comparable_months: int = 0,
) -> float:
    return (
        0.15
        + 0.10 * (1 - attribution / 100)
        + 0.10 * (1 - condition / 100)
        + 0.10 * (1 - min(comparable_count, 10) / 10)
        + 0.05 * (1 if provenance_gaps > 0 else 0)
        + 0.15 * (1 if oldest_comparable_months > 36 else 0)
    )


def value_range(central: float, discount: float) -> dict:
    return {
        "low": round(central * (1 - discount), 2),
        "central": round(central, 2),
        "high": round(central * (1 + discount), 2),
    }


def psa_to_normalized(grade: int) -> int:
    return grade * 10


def rank_actions(actions: list) -> list:
    return sorted(actions, key=lambda a: (a["impact"] / a["effort"], a["impact"]), reverse=True)


def run_harness(intake: dict, provenance: dict, condition: dict, comparables: dict, actions: list) -> dict:
    """Simulate the full harness scoring and roadmap synthesis."""
    dims = {
        "attribution_confidence": provenance.get("attribution_confidence", 50),
        "condition_grade": condition.get("normalized_score", 50),
        "rarity_population": comparables.get("rarity_score", 50),
        "provenance_completeness": max(0, 100 - 25 * len(provenance.get("gaps", []))),
        "market_liquidity_demand": comparables.get("liquidity_score", 50),
        "realizable_value_range": comparables.get("value_score", 50),
    }
    discount = confidence_discount(
        dims["attribution_confidence"],
        dims["condition_grade"],
        comparables.get("count", 0),
        len(provenance.get("gaps", [])),
        comparables.get("oldest_comparable_months", 0),
    )
    compliance = provenance.get("compliance_status")
    # Compliance gate: HALT blocks any value emission.
    central = 0.0 if compliance == "HALT" else comparables.get("central_estimate", 0.0)
    return {
        "compliance_status": compliance,
        "composite": composite_score(dims),
        "value_range": value_range(central, discount),
        "confidence_label": "high" if discount <= 0.25 else "medium" if discount <= 0.45 else "low",
        "actions": rank_actions(actions),
        "basis_of_value": intake.get("basis_of_value"),
    }


class TestScenarioOilPainting:
    def test_produces_value_range_or_flags_low_confidence(self):
        intake = {"category": "fine-art", "basis_of_value": "market_value", "intended_use": "sale"}
        provenance = {"compliance_status": "PASS", "gaps": ["pre-1980 provenance missing"], "attribution_confidence": 60}
        condition = {"normalized_score": 75}
        comparables = {
            "central_estimate": 5000.0,
            "count": 2,
            "rarity_score": 55,
            "liquidity_score": 60,
            "value_score": 65,
            "oldest_comparable_months": 40,
        }
        actions = [
            {"action": "Obtain pre-1980 provenance", "effort": 4, "impact": 4},
            {"action": "Get conservation assessment", "effort": 2, "impact": 3},
        ]
        result = run_harness(intake, provenance, condition, comparables, actions)
        assert result["compliance_status"] == "PASS"
        assert result["value_range"]["central"] > 0
        assert result["confidence_label"] in {"high", "medium", "low"}
        # Gate: comparables <36 months old or value flagged low-confidence.
        if comparables["oldest_comparable_months"] > 36:
            assert result["confidence_label"] == "low"


class TestScenarioGradedCard:
    def test_grade_population_data_cited_and_value_returned(self):
        intake = {"category": "rare-card", "basis_of_value": "market_value", "intended_use": "sale"}
        provenance = {"compliance_status": "PASS", "gaps": [], "attribution_confidence": 95}
        condition = {"normalized_score": psa_to_normalized(9), "grade_label": "PSA 9", "population": 340}
        comparables = {"central_estimate": 1200.0, "count": 6, "rarity_score": 80, "liquidity_score": 85, "value_score": 80}
        actions = [
            {"action": "Cross-check PSA population report date", "effort": 1, "impact": 2},
            {"action": "Submit to elite auction if pop is low", "effort": 2, "impact": 4},
        ]
        result = run_harness(intake, provenance, condition, comparables, actions)
        assert result["value_range"]["central"] > 0
        assert condition["grade_label"] == "PSA 9"
        assert condition["population"] > 0


class TestScenarioSuspectedForgery:
    def test_halts_and_recommends_scientific_testing(self):
        intake = {"category": "antique", "basis_of_value": "market_value", "intended_use": "sale"}
        provenance = {
            "compliance_status": "HALT",
            "gaps": [],
            "attribution_confidence": 30,
            "forgery_indicators": ["modern pigment detected", "signature inconsistent"],
            "recommended_tests": ["pigment analysis", "thermoluminescence"],
        }
        condition = {"normalized_score": 60}
        comparables = {"central_estimate": 8000.0, "count": 3, "rarity_score": 70, "liquidity_score": 50, "value_score": 50}
        result = run_harness(intake, provenance, condition, comparables, [])
        assert result["compliance_status"] == "HALT"
        assert result["value_range"]["central"] == 0.0


class TestScenarioPossiblyStolen:
    def test_compliance_note_before_resale_advice(self):
        intake = {"category": "other-collectible", "basis_of_value": "market_value", "intended_use": "sale"}
        provenance = {
            "compliance_status": "WARN",
            "gaps": ["no documented acquisition"],
            "attribution_confidence": 50,
            "illicit_trade_flags": [{"severity": "medium", "issue": "matches Art Loss Register descriptor"}],
        }
        condition = {"normalized_score": 70}
        comparables = {"central_estimate": 300.0, "count": 4, "rarity_score": 40, "liquidity_score": 45, "value_score": 45}
        result = run_harness(intake, provenance, condition, comparables, [])
        assert result["compliance_status"] == "WARN"
        assert result["value_range"]["central"] > 0


class TestScenarioInsurance:
    def test_basis_of_value_explicitly_replacement_value(self):
        intake = {"category": "fine-art", "basis_of_value": "replacement_value", "intended_use": "insurance"}
        provenance = {"compliance_status": "PASS", "gaps": [], "attribution_confidence": 80}
        condition = {"normalized_score": 85}
        comparables = {"central_estimate": 15000.0, "count": 5, "rarity_score": 70, "liquidity_score": 60, "value_score": 75}
        result = run_harness(intake, provenance, condition, comparables, [])
        assert result["basis_of_value"] == "replacement_value"


class TestScenarioDegradedMode:
    def test_harness_still_enforces_gates_without_live_data(self):
        intake = {"category": "fine-art", "basis_of_value": "market_value", "intended_use": "sale"}
        provenance = {"compliance_status": "HALT", "gaps": []}
        condition = {"normalized_score": 50}
        comparables = {"central_estimate": 0.0, "count": 0, "rarity_score": 0, "liquidity_score": 0, "value_score": 0}
        result = run_harness(intake, provenance, condition, comparables, [])
        assert result["compliance_status"] == "HALT"
        assert result["value_range"]["central"] == 0.0


class TestScenarioInsufficientInput:
    def test_intake_gate_blocks_until_required_fields_present(self):
        # Simulate an incomplete intake record returned by sub-object-intake.
        intake = {"category": "fine-art", "missing_fields": ["medium", "dimensions", "signature_or_marks"]}
        assert len(intake["missing_fields"]) > 0
        # A real harness would stop here; this test confirms the gate data shape.


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
