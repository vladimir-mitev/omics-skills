from __future__ import annotations

import csv
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "tracking-taxonomy-updates"
CONVERTER = SKILL_ROOT / "scripts" / "quickclade_to_routing.py"
FIXTURE = SKILL_ROOT / "fixtures" / "quickclade-machine.tsv"


class TrackingTaxonomyUpdatesTests(unittest.TestCase):
    def test_quickclade_fixture_routes_all_domains(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "domain_routing.tsv"
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "--no-project",
                    "python",
                    str(CONVERTER),
                    str(FIXTURE),
                    "--sample-id",
                    "sample-1",
                    "--output",
                    str(output),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with output.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual([row["downstream_tool"] for row in rows], ["gtdbtk", "eukcc", "gvclass", ""])
            self.assertEqual(rows[-1]["review_flag"], "true")

    def test_scheduler_wrapper_requires_and_forwards_account(self) -> None:
        wrapper = SKILL_ROOT / "scripts" / "submit_taxonomy.sh"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_dir = root / "bins"
            input_dir.mkdir()
            fake_bin = root / "bin"
            fake_bin.mkdir()
            sbatch = fake_bin / "sbatch"
            sbatch.write_text('#!/usr/bin/env bash\nprintf "%s\\n" "$@"\n', encoding="utf-8")
            sbatch.chmod(sbatch.stat().st_mode | stat.S_IXUSR)
            env = os.environ | {
                "PATH": f"{fake_bin}:{os.environ['PATH']}",
                "SLURM_ACCOUNT": "test-account",
            }
            result = subprocess.run(
                [str(wrapper), "gtdbtk", str(input_dir), str(root / "out")],
                cwd=REPO_ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("test-account", result.stdout)
            self.assertIn("taxonomy-tool.sbatch", result.stdout)


if __name__ == "__main__":
    unittest.main()
