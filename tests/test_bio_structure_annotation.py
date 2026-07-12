from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "bio-structure-annotation"
SCRIPT = SKILL_ROOT / "scripts" / "run_structure_annotation.py"
BOLTZ = SKILL_ROOT / "fixtures" / "boltz-complex.yaml"


class BioStructureAnnotationTests(unittest.TestCase):
    def run_plan(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["uv", "run", "--script", str(SCRIPT), *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_boltz_fixture_uses_current_nested_yaml_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_plan("--boltz-yaml", str(BOLTZ), "--out-dir", tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            command = json.loads(result.stdout)["commands"][0]["command"]
            self.assertIn("--out_dir", command)

    def test_public_msa_upload_requires_explicit_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_plan(
                "--boltz-yaml",
                str(BOLTZ),
                "--use-msa-server",
                "--out-dir",
                tmp,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("approve-public-msa-upload", result.stderr)

    def test_gpu_foldseek_requires_padded_database_option(self) -> None:
        query = SKILL_ROOT / "fixtures" / "query.faa"
        with tempfile.TemporaryDirectory() as tmp:
            database = Path(tmp) / "targetDB"
            database.write_text("fixture", encoding="utf-8")
            result = self.run_plan(
                "--foldseek-query",
                str(query),
                "--foldseek-db",
                str(database),
                "--gpu",
                "--out-dir",
                tmp,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--foldseek-padded-db", result.stderr)

    def test_tmvec_plan_uses_maintained_cli(self) -> None:
        query = SKILL_ROOT / "fixtures" / "query.faa"
        with tempfile.TemporaryDirectory() as tmp:
            database = Path(tmp) / "database.npz"
            database.write_bytes(b"fixture")
            result = self.run_plan(
                "--tmvec-query",
                str(query),
                "--tmvec-db",
                str(database),
                "--out-dir",
                tmp,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            command = json.loads(result.stdout)["commands"][0]["command"]
            self.assertEqual(command[:2], ["tmvec", "search"])


if __name__ == "__main__":
    unittest.main()
