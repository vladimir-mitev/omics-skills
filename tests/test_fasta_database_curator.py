from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "bio-fasta-database-curator"
SCRIPT = SKILL_ROOT / "scripts" / "curate_fasta.py"
FIXTURE = SKILL_ROOT / "fixtures" / "mixed-headers.fasta"


class FastaDatabaseCuratorTests(unittest.TestCase):
    def test_curator_writes_deterministic_mapping_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "curated.fasta"
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "--no-project",
                    "python",
                    str(SCRIPT),
                    str(FIXTURE),
                    "--output",
                    str(output),
                    "--prefix",
                    "REF",
                    "--deduplicate",
                    "both",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            mapping = output.with_suffix(".fasta.mapping.tsv")
            report_path = output.with_suffix(".fasta.report.json")
            with mapping.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["input_records"], 3)
            self.assertEqual(report["retained_records"], 2)
            self.assertEqual(rows[1]["duplicate_reason"], "duplicate_sequence")
            expected = hashlib.sha256(b"MSTNPKPQR").hexdigest()
            self.assertEqual(rows[0]["sequence_sha256"], expected)
            self.assertNotIn(" ", output.read_text(encoding="utf-8").splitlines()[0])

    def test_empty_fasta_fails_without_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "empty.fasta"
            source.write_text("", encoding="utf-8")
            output = Path(tmp) / "curated.fasta"
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "--no-project",
                    "python",
                    str(SCRIPT),
                    str(source),
                    "--output",
                    str(output),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("contain no records", result.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
