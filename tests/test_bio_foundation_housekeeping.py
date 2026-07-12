from __future__ import annotations

import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "bio-foundation-housekeeping"
SCRIPT = SKILL_ROOT / "scripts" / "build_sample_catalog.py"


class BioFoundationHousekeepingTests(unittest.TestCase):
    def run_pipeline(self, fixture: str, project_root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "uv",
                "run",
                "--script",
                str(SCRIPT),
                "--input",
                str(SKILL_ROOT / "fixtures" / fixture),
                "--project-root",
                str(project_root),
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_valid_fixture_writes_nonempty_parquet_and_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir) / "project"
            result = self.run_pipeline("valid-samples.jsonl", project)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Validated 2 record(s)", result.stdout)
            self.assertGreater((project / "data" / "normalized" / "samples.parquet").stat().st_size, 0)
            self.assertGreater((project / "data" / "catalog.duckdb").stat().st_size, 0)
            report = project / "results" / "bio-foundation-housekeeping" / "report.md"
            self.assertIn("Status: passed", report.read_text(encoding="utf-8"))

    def test_invalid_fixture_stops_before_parquet_or_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir) / "project"
            result = self.run_pipeline("invalid-samples.jsonl", project)

            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("before ingestion", result.stdout)
            self.assertFalse((project / "data" / "normalized" / "samples.parquet").exists())
            self.assertFalse((project / "data" / "catalog.duckdb").exists())
            rejections = project / "results" / "bio-foundation-housekeeping" / "rejections.json"
            rejection_text = rejections.read_text(encoding="utf-8")
            self.assertIn('"unexpected"', rejection_text)
            self.assertNotIn("must fail", rejection_text)

    def test_duplicate_identifier_stops_before_ingestion(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            fixture = tmp / "duplicates.jsonl"
            record = (
                '{"sample_id":"S001","organism":"Test organism",'
                '"collection_date":"2026-05-01","platform":"ILLUMINA",'
                '"read_count":100,"mean_coverage":1.0}\n'
            )
            fixture.write_text(record + record, encoding="utf-8")
            project = tmp / "project"
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "--script",
                    str(SCRIPT),
                    "--input",
                    str(fixture),
                    "--project-root",
                    str(project),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 2, result.stderr)
            rejections = project / "results" / "bio-foundation-housekeeping" / "rejections.json"
            self.assertIn("duplicate_sample_id", rejections.read_text(encoding="utf-8"))
            self.assertFalse((project / "data" / "catalog.duckdb").exists())

    def test_existing_outputs_are_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir) / "project"
            first = self.run_pipeline("valid-samples.jsonl", project)
            self.assertEqual(first.returncode, 0, first.stderr)
            artifacts = [
                project / "data" / "normalized" / "samples.parquet",
                project / "data" / "catalog.duckdb",
            ]
            before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in artifacts]

            second = self.run_pipeline("valid-samples.jsonl", project)

            after = [hashlib.sha256(path.read_bytes()).hexdigest() for path in artifacts]
            self.assertEqual(second.returncode, 2, second.stderr)
            self.assertIn("refusing to overwrite", second.stdout)
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
