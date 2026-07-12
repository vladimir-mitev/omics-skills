import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills" / "manuscript-review-council"
SCRIPT = SKILL / "scripts" / "validate_review_bundle.py"


def test_fixture_has_deterministic_paths_and_machine_readable_issues():
    result = subprocess.run(["uv", "run", "--script", str(SCRIPT), str(SKILL / "fixtures" / "review-bundle.json")], text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_wrong_artifact_path_is_rejected(tmp_path):
    bundle = json.loads((SKILL / "fixtures" / "review-bundle.json").read_text())
    bundle["editor_path"] = "editor.json"
    path = tmp_path / "bundle.json"
    path.write_text(json.dumps(bundle))
    result = subprocess.run(["uv", "run", "--script", str(SCRIPT), str(path)], text=True, capture_output=True)
    assert result.returncode != 0
    assert "editor_path must be reviews/" in result.stderr
