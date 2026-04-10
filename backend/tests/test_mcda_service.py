"""Tests for MCDA scoring engine (CDC SOTREG v5.0 6-criteria weighted sum)."""
from __future__ import annotations

import pytest

from app.services.sotreg.mcda_service import (
    CDC_DEFAULT_WEIGHTS,
    CRITERIA_DIRECTION,
    compute_mcda_scores,
    compute_mcfadden_logit,
    compute_sensitivity_analysis,
    normalize_value,
)


# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------

DIESEL_ALT = {
    "name": "Diesel",
    "capex": 180000.0,
    "opex": 120000.0,
    "co2": 90.0,
    "risk": 3.0,
    "comfort": 3.0,
    "maturity": 5.0,
}

ELECTRIC_ALT = {
    "name": "Electric",
    "capex": 300000.0,
    "opex": 60000.0,
    "co2": 10.0,
    "risk": 2.0,
    "comfort": 4.5,
    "maturity": 3.0,
}

HYBRID_ALT = {
    "name": "Hybrid",
    "capex": 250000.0,
    "opex": 80000.0,
    "co2": 45.0,
    "risk": 2.5,
    "comfort": 4.0,
    "maturity": 4.0,
}

CNG_ALT = {
    "name": "CNG",
    "capex": 220000.0,
    "opex": 95000.0,
    "co2": 60.0,
    "risk": 3.5,
    "comfort": 3.5,
    "maturity": 3.5,
}

THREE_ALTERNATIVES = [DIESEL_ALT, ELECTRIC_ALT, HYBRID_ALT]
FOUR_ALTERNATIVES = [DIESEL_ALT, ELECTRIC_ALT, HYBRID_ALT, CNG_ALT]


# ---------------------------------------------------------------------------
# Normalization tests
# ---------------------------------------------------------------------------


class TestNormalizeValue:
    """Verify 1-5 scale normalization for cost and benefit criteria."""

    def test_cost_best_value_maps_to_5(self) -> None:
        """For cost criteria, the minimum value should map to 5.0."""
        assert normalize_value(10.0, 10.0, 100.0, "cost") == 5.0

    def test_cost_worst_value_maps_to_1(self) -> None:
        """For cost criteria, the maximum value should map to 1.0."""
        assert normalize_value(100.0, 10.0, 100.0, "cost") == 1.0

    def test_cost_midpoint(self) -> None:
        """For cost criteria, midpoint should map to 3.0."""
        result = normalize_value(55.0, 10.0, 100.0, "cost")
        assert abs(result - 3.0) < 0.01

    def test_benefit_best_value_maps_to_5(self) -> None:
        """For benefit criteria, the maximum value should map to 5.0."""
        assert normalize_value(100.0, 10.0, 100.0, "benefit") == 5.0

    def test_benefit_worst_value_maps_to_1(self) -> None:
        """For benefit criteria, the minimum value should map to 1.0."""
        assert normalize_value(10.0, 10.0, 100.0, "benefit") == 1.0

    def test_benefit_midpoint(self) -> None:
        """For benefit criteria, midpoint should map to 3.0."""
        result = normalize_value(55.0, 10.0, 100.0, "benefit")
        assert abs(result - 3.0) < 0.01

    def test_equal_values_return_midpoint(self) -> None:
        """When v_min == v_max, normalized score is 3.0."""
        assert normalize_value(42.0, 42.0, 42.0, "cost") == 3.0
        assert normalize_value(42.0, 42.0, 42.0, "benefit") == 3.0

    def test_invalid_direction_raises(self) -> None:
        with pytest.raises(ValueError, match="direction must be"):
            normalize_value(50.0, 10.0, 100.0, "invalid")

    def test_cost_quarter_value(self) -> None:
        """25% from min in cost direction => 5 - 4*0.25 = 4.0."""
        result = normalize_value(32.5, 10.0, 100.0, "cost")
        assert abs(result - 4.0) < 0.01

    def test_benefit_quarter_value(self) -> None:
        """25% from min in benefit direction => 1 + 4*0.25 = 2.0."""
        result = normalize_value(32.5, 10.0, 100.0, "benefit")
        assert abs(result - 2.0) < 0.01


# ---------------------------------------------------------------------------
# MCDA scoring tests
# ---------------------------------------------------------------------------


class TestComputeMCDAScores:
    """Verify MCDA weighted sum scoring engine."""

    def test_three_alternatives_returns_ranked_list(self) -> None:
        """Basic ranking of 3 alternatives with default CDC weights."""
        result = compute_mcda_scores(THREE_ALTERNATIVES)
        assert len(result["ranked_alternatives"]) == 3
        assert result["ranked_alternatives"][0]["rank"] == 1
        assert result["ranked_alternatives"][1]["rank"] == 2
        assert result["ranked_alternatives"][2]["rank"] == 3

    def test_scores_are_between_1_and_5(self) -> None:
        """All scores should fall in [1.0, 5.0]."""
        result = compute_mcda_scores(FOUR_ALTERNATIVES)
        for alt in result["ranked_alternatives"]:
            assert 1.0 <= alt["score"] <= 5.0

    def test_normalized_values_between_1_and_5(self) -> None:
        """Each normalized value should be in [1.0, 5.0]."""
        result = compute_mcda_scores(FOUR_ALTERNATIVES)
        for alt in result["ranked_alternatives"]:
            for criterion, val in alt["normalized_values"].items():
                assert 1.0 <= val <= 5.0, (
                    f"{alt['name']}.{criterion} = {val}"
                )

    def test_default_weights_used_when_none(self) -> None:
        result = compute_mcda_scores(THREE_ALTERNATIVES)
        assert result["weights_used"] == CDC_DEFAULT_WEIGHTS

    def test_custom_weights_applied(self) -> None:
        """Custom weights overriding CDC defaults."""
        custom = {
            "capex": 0.10,
            "opex": 0.10,
            "co2": 0.50,
            "risk": 0.10,
            "comfort": 0.10,
            "maturity": 0.10,
        }
        result = compute_mcda_scores(THREE_ALTERNATIVES, weights=custom)
        assert result["weights_used"] == custom
        # With 50% weight on CO2, Electric (lowest CO2) should rank first
        assert result["best_alternative"] == "Electric"

    def test_best_and_worst_identified(self) -> None:
        result = compute_mcda_scores(THREE_ALTERNATIVES)
        assert result["best_alternative"] == result["ranked_alternatives"][0]["name"]
        assert result["worst_alternative"] == result["ranked_alternatives"][-1]["name"]

    def test_criteria_ranges_correct(self) -> None:
        result = compute_mcda_scores(THREE_ALTERNATIVES)
        ranges = result["criteria_ranges"]
        assert ranges["capex"]["min"] == 180000.0
        assert ranges["capex"]["max"] == 300000.0
        assert ranges["co2"]["min"] == 10.0
        assert ranges["co2"]["max"] == 90.0

    def test_ranking_is_descending_by_score(self) -> None:
        result = compute_mcda_scores(FOUR_ALTERNATIVES)
        scores = [a["score"] for a in result["ranked_alternatives"]]
        assert scores == sorted(scores, reverse=True)

    def test_single_alternative_score_is_3(self) -> None:
        """A single alternative: all criteria equal min==max, normalized=3.0.

        S(a) = sum(w_k * 3.0) = 3.0 * sum(w_k) = 3.0.
        """
        result = compute_mcda_scores([DIESEL_ALT])
        assert len(result["ranked_alternatives"]) == 1
        alt = result["ranked_alternatives"][0]
        assert abs(alt["score"] - 3.0) < 0.01
        assert alt["rank"] == 1
        for val in alt["normalized_values"].values():
            assert abs(val - 3.0) < 0.01

    def test_two_identical_alternatives_same_score(self) -> None:
        """Two identical alternatives should have equal scores."""
        alt1 = dict(DIESEL_ALT, name="Diesel A")
        alt2 = dict(DIESEL_ALT, name="Diesel B")
        result = compute_mcda_scores([alt1, alt2])
        scores = [a["score"] for a in result["ranked_alternatives"]]
        assert scores[0] == scores[1]

    # ---- Validation error cases ------------------------------------------

    def test_empty_alternatives_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty list"):
            compute_mcda_scores([])

    def test_missing_criterion_raises(self) -> None:
        bad = {"name": "Bad", "capex": 1.0}
        with pytest.raises(ValueError, match="missing criterion"):
            compute_mcda_scores([bad])

    def test_missing_name_raises(self) -> None:
        bad = {
            "capex": 1.0, "opex": 1.0, "co2": 1.0,
            "risk": 1.0, "comfort": 1.0, "maturity": 1.0,
        }
        with pytest.raises(ValueError, match="missing 'name'"):
            compute_mcda_scores([bad])

    def test_non_numeric_criterion_raises(self) -> None:
        bad = dict(DIESEL_ALT, capex="not_a_number")
        with pytest.raises(ValueError, match="must be numeric"):
            compute_mcda_scores([bad])

    def test_weights_not_summing_to_one_raises(self) -> None:
        bad_weights = {
            "capex": 0.20, "opex": 0.20, "co2": 0.25,
            "risk": 0.15, "comfort": 0.10, "maturity": 0.20,
        }
        with pytest.raises(ValueError, match="sum to 1.0"):
            compute_mcda_scores(THREE_ALTERNATIVES, weights=bad_weights)

    def test_missing_weight_key_raises(self) -> None:
        bad_weights = {
            "capex": 0.25, "opex": 0.25, "co2": 0.25, "risk": 0.25,
        }
        with pytest.raises(ValueError, match="Missing"):
            compute_mcda_scores(THREE_ALTERNATIVES, weights=bad_weights)

    def test_negative_weight_raises(self) -> None:
        bad_weights = {
            "capex": -0.10, "opex": 0.30, "co2": 0.25,
            "risk": 0.25, "comfort": 0.15, "maturity": 0.15,
        }
        with pytest.raises(ValueError, match="non-negative"):
            compute_mcda_scores(THREE_ALTERNATIVES, weights=bad_weights)

    # ---- Known-input/output correctness test -----------------------------

    def test_manual_calculation_two_alternatives(self) -> None:
        """Hand-computed MCDA with 2 alternatives and equal weights.

        Alternatives:
            A: capex=100, opex=200, co2=50, risk=3, comfort=4, maturity=5
            B: capex=200, opex=100, co2=100, risk=1, comfort=2, maturity=3

        Ranges: capex=[100,200], opex=[100,200], co2=[50,100],
                risk=[1,3], comfort=[2,4], maturity=[3,5]

        Normalized (cost: 5-4*(v-min)/(max-min), benefit: 1+4*(v-min)/(max-min)):
            A: capex=5, opex=1, co2=5, risk=1, comfort=5, maturity=5
            B: capex=1, opex=5, co2=1, risk=5, comfort=1, maturity=1

        With equal weights (1/6 each):
            S(A) = (5+1+5+1+5+5)/6 = 22/6 = 3.6667
            S(B) = (1+5+1+5+1+1)/6 = 14/6 = 2.3333
        """
        a = {
            "name": "A", "capex": 100.0, "opex": 200.0, "co2": 50.0,
            "risk": 3.0, "comfort": 4.0, "maturity": 5.0,
        }
        b = {
            "name": "B", "capex": 200.0, "opex": 100.0, "co2": 100.0,
            "risk": 1.0, "comfort": 2.0, "maturity": 3.0,
        }
        equal_weights = {k: 1.0 / 6.0 for k in CDC_DEFAULT_WEIGHTS}
        # Adjust to sum exactly to 1.0 (floating point)
        total = sum(equal_weights.values())
        equal_weights["capex"] += 1.0 - total

        result = compute_mcda_scores([a, b], weights=equal_weights)
        ranked = result["ranked_alternatives"]

        assert ranked[0]["name"] == "A"
        assert ranked[1]["name"] == "B"
        assert abs(ranked[0]["score"] - 3.67) < 0.02
        assert abs(ranked[1]["score"] - 2.33) < 0.02

    def test_all_same_values_on_one_criterion(self) -> None:
        """When all alternatives have the same value on a criterion,
        that criterion's normalized score is 3.0 for all."""
        a = dict(DIESEL_ALT, name="A", co2=50.0)
        b = dict(ELECTRIC_ALT, name="B", co2=50.0)
        result = compute_mcda_scores([a, b])
        for alt in result["ranked_alternatives"]:
            assert abs(alt["normalized_values"]["co2"] - 3.0) < 0.01


# ---------------------------------------------------------------------------
# Sensitivity analysis tests
# ---------------------------------------------------------------------------


class TestComputeSensitivityAnalysis:
    """Verify sensitivity analysis perturbation logic."""

    def test_returns_expected_structure(self) -> None:
        result = compute_sensitivity_analysis(THREE_ALTERNATIVES)
        assert "base_ranking" in result
        assert "sensitivity_results" in result
        assert "critical_criteria" in result
        assert "stability_score" in result

    def test_six_criteria_analyzed(self) -> None:
        """Should produce one result per criterion."""
        result = compute_sensitivity_analysis(THREE_ALTERNATIVES)
        assert len(result["sensitivity_results"]) == 6

    def test_base_ranking_matches_mcda(self) -> None:
        """Base ranking should match a fresh MCDA computation."""
        mcda = compute_mcda_scores(THREE_ALTERNATIVES)
        sens = compute_sensitivity_analysis(THREE_ALTERNATIVES)
        mcda_names = [a["name"] for a in mcda["ranked_alternatives"]]
        sens_names = [a["name"] for a in sens["base_ranking"]]
        assert mcda_names == sens_names

    def test_stability_score_range(self) -> None:
        """Stability score should be between 0 and 100."""
        result = compute_sensitivity_analysis(THREE_ALTERNATIVES)
        assert 0.0 <= result["stability_score"] <= 100.0

    def test_weight_perturbation_values(self) -> None:
        """Weight plus/minus should be original +/- 20%."""
        result = compute_sensitivity_analysis(
            THREE_ALTERNATIVES, delta_pct=20.0,
        )
        for sr in result["sensitivity_results"]:
            w_orig = sr["weight_original"]
            expected_plus = min(w_orig * 1.2, 1.0)
            expected_minus = max(w_orig * 0.8, 0.0)
            assert abs(sr["weight_plus"] - expected_plus) < 0.01
            assert abs(sr["weight_minus"] - expected_minus) < 0.01

    def test_critical_criteria_subset_of_all(self) -> None:
        result = compute_sensitivity_analysis(FOUR_ALTERNATIVES)
        all_criteria = {sr["criterion"] for sr in result["sensitivity_results"]}
        critical = set(result["critical_criteria"])
        assert critical.issubset(all_criteria)

    def test_is_critical_matches_ranking_changed(self) -> None:
        """is_critical flag should match ranking_changed."""
        result = compute_sensitivity_analysis(THREE_ALTERNATIVES)
        for sr in result["sensitivity_results"]:
            assert sr["is_critical"] == sr["ranking_changed"]

    def test_zero_delta_raises(self) -> None:
        with pytest.raises(ValueError, match="delta_pct must be positive"):
            compute_sensitivity_analysis(THREE_ALTERNATIVES, delta_pct=0.0)

    def test_negative_delta_raises(self) -> None:
        with pytest.raises(ValueError, match="delta_pct must be positive"):
            compute_sensitivity_analysis(THREE_ALTERNATIVES, delta_pct=-5.0)

    def test_empty_alternatives_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty list"):
            compute_sensitivity_analysis([])

    def test_very_large_delta_still_valid(self) -> None:
        """Even with 100% delta, weights are clamped and redistributed."""
        result = compute_sensitivity_analysis(
            THREE_ALTERNATIVES, delta_pct=100.0,
        )
        assert 0.0 <= result["stability_score"] <= 100.0

    def test_single_alternative_all_stable(self) -> None:
        """With 1 alternative, ranking can never change."""
        result = compute_sensitivity_analysis([DIESEL_ALT])
        assert result["stability_score"] == 100.0
        assert result["critical_criteria"] == []


# ---------------------------------------------------------------------------
# McFadden logit tests
# ---------------------------------------------------------------------------


class TestComputeMcFaddenLogit:
    """Verify McFadden multinomial logit choice probabilities."""

    LOGIT_ALTERNATIVES = [
        {"name": "Bus", "cost": 500.0, "time_minutes": 45.0, "comfort": 3.0},
        {"name": "Shuttle", "cost": 800.0, "time_minutes": 25.0, "comfort": 4.5},
        {"name": "Carpool", "cost": 300.0, "time_minutes": 35.0, "comfort": 2.5},
    ]

    def test_probabilities_sum_to_one(self) -> None:
        result = compute_mcfadden_logit(self.LOGIT_ALTERNATIVES)
        assert abs(result["probabilities_sum"] - 1.0) < 0.02

    def test_returns_all_alternatives(self) -> None:
        result = compute_mcfadden_logit(self.LOGIT_ALTERNATIVES)
        names = {p["name"] for p in result["probabilities"]}
        assert names == {"Bus", "Shuttle", "Carpool"}

    def test_probabilities_between_0_and_1(self) -> None:
        result = compute_mcfadden_logit(self.LOGIT_ALTERNATIVES)
        for p in result["probabilities"]:
            assert 0.0 <= p["probability"] <= 1.0

    def test_dominant_mode_has_highest_probability(self) -> None:
        result = compute_mcfadden_logit(self.LOGIT_ALTERNATIVES)
        probs = result["probabilities"]
        assert probs[0]["name"] == result["dominant_mode"]
        if len(probs) > 1:
            assert probs[0]["probability"] >= probs[1]["probability"]

    def test_sorted_by_probability_desc(self) -> None:
        result = compute_mcfadden_logit(self.LOGIT_ALTERNATIVES)
        probs = [p["probability"] for p in result["probabilities"]]
        assert probs == sorted(probs, reverse=True)

    def test_single_alternative_probability_one(self) -> None:
        """Single alternative should have P=1.0."""
        result = compute_mcfadden_logit([self.LOGIT_ALTERNATIVES[0]])
        assert len(result["probabilities"]) == 1
        assert abs(result["probabilities"][0]["probability"] - 1.0) < 0.01

    def test_two_identical_alternatives_equal_probability(self) -> None:
        """Two identical alternatives should have P=0.5 each."""
        alt = {"name": "A", "cost": 500.0, "time_minutes": 30.0, "comfort": 3.0}
        alt2 = {"name": "B", "cost": 500.0, "time_minutes": 30.0, "comfort": 3.0}
        result = compute_mcfadden_logit([alt, alt2])
        p1 = result["probabilities"][0]["probability"]
        p2 = result["probabilities"][1]["probability"]
        assert abs(p1 - 0.5) < 0.01
        assert abs(p2 - 0.5) < 0.01

    def test_cheaper_faster_more_comfortable_dominates(self) -> None:
        """An alternative that is cheaper, faster, and more comfortable should
        have the highest probability."""
        dominant = {"name": "Best", "cost": 100.0, "time_minutes": 10.0, "comfort": 5.0}
        inferior = {"name": "Worst", "cost": 1000.0, "time_minutes": 60.0, "comfort": 1.0}
        result = compute_mcfadden_logit([dominant, inferior])
        assert result["dominant_mode"] == "Best"
        assert result["probabilities"][0]["probability"] > 0.9

    def test_custom_betas(self) -> None:
        """Adjusting betas should change the outcome."""
        # With high beta_comfort, the most comfortable option should dominate
        result = compute_mcfadden_logit(
            self.LOGIT_ALTERNATIVES,
            beta_cost=0.0,
            beta_time=0.0,
            beta_comfort=2.0,
        )
        # Shuttle has comfort=4.5 (highest)
        assert result["dominant_mode"] == "Shuttle"

    def test_empty_alternatives_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty list"):
            compute_mcfadden_logit([])

    def test_missing_field_raises(self) -> None:
        bad = [{"name": "Bad", "cost": 100.0}]
        with pytest.raises(ValueError, match="missing fields"):
            compute_mcfadden_logit(bad)

    def test_utility_values_present(self) -> None:
        """Each probability entry should have a utility value."""
        result = compute_mcfadden_logit(self.LOGIT_ALTERNATIVES)
        for p in result["probabilities"]:
            assert "utility" in p
            assert isinstance(p["utility"], float)

    def test_numerical_stability_large_utilities(self) -> None:
        """Large cost differences should not cause overflow."""
        alts = [
            {"name": "Cheap", "cost": 1.0, "time_minutes": 1.0, "comfort": 5.0},
            {"name": "Expensive", "cost": 100000.0, "time_minutes": 120.0, "comfort": 1.0},
        ]
        result = compute_mcfadden_logit(alts)
        # Should not raise, probabilities should still sum to ~1.0
        assert abs(result["probabilities_sum"] - 1.0) < 0.02
        assert result["dominant_mode"] == "Cheap"
