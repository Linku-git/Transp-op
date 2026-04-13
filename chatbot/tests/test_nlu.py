"""NLU classification tests for Transpop chatbot -- Session 127.

Validates NLU training data structure, intent coverage (50+ examples each),
and entity annotations.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pytest
import yaml

logger = logging.getLogger(__name__)

NLU_PATH = Path(__file__).parent.parent / "data" / "nlu.yml"


@pytest.fixture(scope="module")
def nlu_data() -> dict:
    """Load and parse nlu.yml."""
    assert NLU_PATH.exists(), f"NLU file not found: {NLU_PATH}"
    with open(NLU_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert "nlu" in data, "NLU file must contain 'nlu' key"
    return data


def _get_examples_for_intent(nlu_data: dict, intent: str) -> list[str]:
    """Extract training examples for a given intent."""
    examples: list[str] = []
    for item in nlu_data["nlu"]:
        if item.get("intent") == intent:
            raw = item.get("examples", "")
            for line in raw.strip().split("\n"):
                line = line.strip()
                if line.startswith("- "):
                    examples.append(line[2:])
    return examples


class TestNLUData:
    """Validate NLU training data structure and coverage."""

    def test_fleet_status_intent_has_50_examples(self, nlu_data: dict) -> None:
        """fleet_status intent must have 50+ training examples."""
        examples = _get_examples_for_intent(nlu_data, "fleet_status")
        assert len(examples) >= 50, (
            f"fleet_status has {len(examples)} examples, need 50+"
        )

    def test_trip_info_intent_has_50_examples(self, nlu_data: dict) -> None:
        """trip_info intent must have 50+ training examples."""
        examples = _get_examples_for_intent(nlu_data, "trip_info")
        assert len(examples) >= 50, (
            f"trip_info has {len(examples)} examples, need 50+"
        )

    def test_kpi_query_intent_has_50_examples(self, nlu_data: dict) -> None:
        """kpi_query intent must have 50+ training examples."""
        examples = _get_examples_for_intent(nlu_data, "kpi_query")
        assert len(examples) >= 50, (
            f"kpi_query has {len(examples)} examples, need 50+"
        )

    def test_ligne_id_entity_annotated(self, nlu_data: dict) -> None:
        """trip_info examples must include ligne_id entity annotations."""
        examples = _get_examples_for_intent(nlu_data, "trip_info")
        entity_examples = [e for e in examples if "(ligne_id)" in e]
        assert len(entity_examples) >= 5, (
            f"Only {len(entity_examples)} trip_info examples have ligne_id entity, need 5+"
        )
