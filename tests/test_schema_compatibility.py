import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills" / "bio-foundation-housekeeping"
SCRIPT = SKILL / "scripts" / "check_schema_compatibility.py"
BASE = SKILL / "schemas" / "project-metadata.yaml"


def run(extension, out):
    return subprocess.run(["uv", "run", "--script", str(SCRIPT), "--base", str(BASE), "--extension", str(extension), "--out", str(out)], text=True, capture_output=True)


def test_optional_project_extension_is_compatible(tmp_path):
    out = tmp_path / "report.json"
    result = run(SKILL / "fixtures" / "schema-extension-compatible.yaml", out)
    assert result.returncode == 0, result.stderr
    report = json.loads(out.read_text())
    assert report["compatible"] is True
    assert report["changes"] == [{"location": "classes.Sample.attributes.collection_site", "compatibility": "compatible", "change": "optional_slot_added"}]
    migration = json.loads((SKILL / "fixtures" / "schema-migration-v1-to-v1.1.json").read_text())
    assert migration["expected"]["collection_site"] is None


def test_required_or_retyped_extension_is_breaking(tmp_path):
    out = tmp_path / "report.json"
    result = run(SKILL / "fixtures" / "schema-extension-breaking.yaml", out)
    assert result.returncode == 2
    changes = {item["change"] for item in json.loads(out.read_text())["changes"]}
    assert changes == {"required_slot_added", "constraint_changed:None->'integer'"}
