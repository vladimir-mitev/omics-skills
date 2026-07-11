from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "bio-workflow-methods-docwriter"
VALIDATOR = SKILL_ROOT / "scripts" / "validate_run_manifest.py"
EXTRACTOR = SKILL_ROOT / "scripts" / "extract_nextflow_run.py"
EXAMPLE = SKILL_ROOT / "examples" / "run_manifest.example.yaml"
SCHEMA = SKILL_ROOT / "schemas" / "run-manifest.schema.json"


class WorkflowMethodsDocwriterTests(unittest.TestCase):
    def run_validator(self, manifest: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["uv", "run", str(VALIDATOR), str(manifest)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_complete_example_passes_schema_and_semantic_checks(self) -> None:
        result = self.run_validator(EXAMPLE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Manifest validation passed", result.stdout)

    def test_required_placeholder_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "incomplete.yaml"
            manifest.write_text(
                EXAMPLE.read_text(encoding="utf-8").replace(
                    "engine_version: 25.10.3",
                    "engine_version: NOT CAPTURED",
                    1,
                ),
                encoding="utf-8",
            )
            result = self.run_validator(manifest)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("workflow.engine_version is incomplete", result.stdout)

    def test_step_schema_requires_reproducibility_fields(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        required = set(schema["properties"]["steps"]["items"]["required"])
        self.assertTrue(
            {"tool", "tool_version", "command", "inputs", "outputs"} <= required
        )

    def test_extractor_redacts_common_credentials(self) -> None:
        spec = importlib.util.spec_from_file_location("extract_nextflow_run", EXTRACTOR)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        with patch.dict(sys.modules, {"yaml": object()}):
            spec.loader.exec_module(module)
        redacted = module.redact_command(
            'export API_KEY="sensitive"\nexport DREMIO_PAT=another-secret\n'
            'curl -H "Authorization: Bearer token-value" url'
        )
        self.assertNotIn("sensitive", redacted)
        self.assertNotIn("another-secret", redacted)
        self.assertNotIn("token-value", redacted)
        self.assertGreaterEqual(redacted.count("$REDACTED"), 3)


if __name__ == "__main__":
    unittest.main()
