from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills" / "bioinformatics-project" / "scripts" / "scaffold_project.py"


def tree_digest(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


class BioinformaticsProjectScaffoldTests(unittest.TestCase):
    def run_scaffold(self, project: Path, *extra: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(project),
                "--name",
                "Coastal metagenomes",
                "--objective",
                "Recover and compare metagenome-assembled genomes.",
                *extra,
            ],
            text=True,
            capture_output=True,
            check=check,
        )

    def test_scaffold_is_complete_idempotent_and_checkable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir) / "coastal-metagenomes"
            first = self.run_scaffold(project)
            before = tree_digest(project)
            second = self.run_scaffold(project)
            after = tree_digest(project)
            checked = self.run_scaffold(project, "--check")

            self.assertIn("15 created, 0 unchanged", first.stdout)
            self.assertIn("0 created, 15 unchanged", second.stdout)
            self.assertIn("Scaffold valid", checked.stdout)
            self.assertEqual(before, after)
            self.assertTrue((project / "results" / "runall.example").stat().st_mode & 0o111)
            self.assertIn('[workspace]', (project / "pixi.toml").read_text(encoding="utf-8"))
            project_text = "\n".join(
                path.read_text(encoding="utf-8")
                for path in project.rglob("*")
                if path.is_file()
            )
            self.assertNotIn("arctic", project_text.lower())

    def test_scaffold_refuses_to_overwrite_a_changed_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir) / "coastal-metagenomes"
            self.run_scaffold(project)
            readme = project / "README.md"
            readme.write_text("user-owned content\n", encoding="utf-8")

            result = self.run_scaffold(project, check=False)

            self.assertEqual(result.returncode, 2)
            self.assertIn("README.md", result.stdout)
            self.assertEqual(readme.read_text(encoding="utf-8"), "user-owned content\n")

    def test_check_reports_an_incomplete_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir) / "coastal-metagenomes"
            project.mkdir()

            result = self.run_scaffold(project, "--check", check=False)

            self.assertEqual(result.returncode, 1)
            self.assertIn("Scaffold is incomplete", result.stdout)
            self.assertIn("README.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
