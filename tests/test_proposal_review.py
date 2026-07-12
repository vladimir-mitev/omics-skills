from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "skills" / "proposal-review" / "scripts" / "score_proposal.py"
SPEC = importlib.util.spec_from_file_location("score_proposal", MODULE_PATH)
score_proposal = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = score_proposal
SPEC.loader.exec_module(score_proposal)


class ProposalReviewTests(unittest.TestCase):
    def test_default_rubric_totals_and_maps_recommendation(self) -> None:
        payload = {"scores": {category: 4 for category in score_proposal.DEFAULT_WEIGHTS}}
        result = score_proposal.score_payload(payload)
        self.assertEqual(result["weights_total"], 100)
        self.assertEqual(result["weighted_mean_1_to_5"], 4.0)
        self.assertEqual(result["recommendation"], "Accept")

    def test_sponsor_rubric_overrides_categories_and_labels(self) -> None:
        payload = {
            "rubric": {
                "weights": {"mission": 70, "feasibility": 30},
                "recommendations": [
                    {"minimum": 4, "label": "Fund"},
                    {"minimum": 1, "label": "Decline"},
                ],
            },
            "scores": {"mission": 5, "feasibility": 3},
        }
        result = score_proposal.score_payload(payload)
        self.assertEqual(result["rubric_source"], "sponsor")
        self.assertEqual(result["recommendation"], "Fund")

    def test_invalid_weight_total_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "expected 100"):
            score_proposal.score_payload(
                {
                    "rubric": {
                        "weights": {"mission": 60, "feasibility": 30},
                        "recommendations": [{"minimum": 1, "label": "Decline"}],
                    },
                    "scores": {"mission": 4, "feasibility": 4},
                }
            )


if __name__ == "__main__":
    unittest.main()
