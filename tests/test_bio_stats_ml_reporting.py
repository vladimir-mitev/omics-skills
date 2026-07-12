from __future__ import annotations

import csv
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "bio-stats-ml-reporting"
SCRIPT = SKILL_ROOT / "scripts" / "validate_predictions.py"
FIXTURE = SKILL_ROOT / "fixtures" / "predictions.tsv"


class BioStatsMLReportingTests(unittest.TestCase):
    def run_validator(self, source: Path, report: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "uv",
                "run",
                "--no-project",
                "python",
                str(SCRIPT),
                str(source),
                "--report",
                str(report),
                "--require-beats-null",
                *extra,
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_valid_fixture_reports_all_required_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "validation.json"
            result = self.run_validator(FIXTURE, report)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["metrics"]["accuracy"], 1.0)
            self.assertIn("majority_null_accuracy", payload["metrics"])
            self.assertIn("brier_score", payload["metrics"])
            self.assertIn("batch_outcome_prevalence_range", payload["metrics"])

    def test_group_leakage_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "leaky.tsv"
            with FIXTURE.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
                fields = list(rows[0])
            rows[2]["group_id"] = rows[0]["group_id"]
            with source.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
                writer.writeheader()
                writer.writerows(rows)
            report = Path(tmp) / "validation.json"
            result = self.run_validator(source, report)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("group leakage", result.stderr)

    def mutated_fixture(self, directory: Path, mutate) -> Path:
        with FIXTURE.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
            fields = list(rows[0])
        mutate(rows)
        source = directory / "mutated.tsv"
        with source.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)
        return source

    def test_sample_leakage_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            source = self.mutated_fixture(directory, lambda rows: rows[2].update(sample_id=rows[0]["sample_id"]))
            result = self.run_validator(source, directory / "report.json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("sample leakage", result.stderr)

    def test_bad_calibration_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            source = self.mutated_fixture(directory, lambda rows: [row.update(y_score="0.5") for row in rows if row["split"] == "test"])
            result = self.run_validator(source, directory / "report.json", "--max-brier", "0.10")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Brier score", result.stderr)

    def test_batch_outcome_confounding_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            source = self.mutated_fixture(directory, lambda rows: [row.update(batch="case" if row["y_true"] == "1" else "control") for row in rows])
            result = self.run_validator(source, directory / "report.json", "--max-batch-prevalence-range", "0.20")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("outcome prevalence range", result.stderr)

    def test_majority_null_baseline_failure_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            source = self.mutated_fixture(directory, lambda rows: [row.update(y_pred="0") for row in rows if row["split"] == "test"])
            result = self.run_validator(source, directory / "report.json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("does not beat majority baseline", result.stderr)

    def test_single_class_test_split_fails_and_reports_imbalance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            source = self.mutated_fixture(directory, lambda rows: [row.update(y_true="0", y_pred="0", y_score="0.1") for row in rows if row["split"] == "test"])
            result = self.run_validator(source, directory / "report.json")
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads((directory / "report.json").read_text(encoding="utf-8"))
            self.assertIn("test split contains only one class", payload["errors"])
            self.assertTrue(any("class imbalance ratio" in warning for warning in payload["warnings"]))


if __name__ == "__main__":
    unittest.main()
