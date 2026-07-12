from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills" / "csag-extraction" / "scripts" / "validate_paper_extraction.py"


def minimal_extraction() -> dict:
    return {
        "id": "doi:10.1000/fixture",
        "title": "Fixture paper",
        "schema_version": "0.6.0",
        "validator_version": "0.6.0",
        "assertions": [
            {
                "id": "doi:10.1000/fixture/assertion/A0001",
                "assertion_text": "The fixture supports the claim.",
                "claim_role": "result_claim",
                "normalization_status": "raw",
                "contexts": [{"context_type": "other", "description": "fixture"}],
            }
        ],
        "evidence_items": [
            {
                "id": "doi:10.1000/fixture/evidence/E0001",
                "evidence_type": "experimental_result",
                "evidence_text": "The measured value increased.",
            }
        ],
        "evidence_links": [
            {
                "id": "doi:10.1000/fixture/elink/L0001",
                "evidence_item": "doi:10.1000/fixture/evidence/E0001",
                "assertion": "doi:10.1000/fixture/assertion/A0001",
                "polarity": "supports",
            }
        ],
        "extraction_activities": [
            {
                "id": "doi:10.1000/fixture/activity/ACT0001",
                "activity_type": "machine extraction",
                "parameters": [
                    {"key": "doi_status", "value": "resolved"},
                    {"key": "pmid_status", "value": "unresolved"},
                ],
            }
        ],
    }


class CsagSchemaValidationTests(unittest.TestCase):
    def run_validator(self, payload: dict, strict: bool = False) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "paper.json"
            report = root / "report.json"
            source.write_text(json.dumps(payload), encoding="utf-8")
            command = [
                "uv",
                "run",
                "--script",
                str(SCRIPT),
                str(source),
                "--report-out",
                str(report),
            ]
            if strict:
                command.append("--strict")
            return subprocess.run(
                command,
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

    def test_authoritative_linkml_schema_rejects_unknown_field(self) -> None:
        payload = minimal_extraction()
        payload["made_up_field"] = "not in schema"
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("LinkML schema validation failed", result.stdout + result.stderr)

    def test_strict_mode_rejects_missing_text_grounding(self) -> None:
        result = self.run_validator(minimal_extraction(), strict=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing strict text grounding", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
