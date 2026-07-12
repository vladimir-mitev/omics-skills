import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills" / "bio-phylogenomics"
SCRIPT = SKILL / "scripts" / "run_phylogenomics.py"


def test_plan_is_seeded_and_checksummed(tmp_path):
    out = tmp_path / "out"
    result = subprocess.run([sys.executable, str(SCRIPT), str(SKILL / "fixtures" / "markers.tsv"), "--references", str(SKILL / "fixtures" / "references.tsv"), "--out", str(out), "--seed", "41"], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    plan = json.loads((out / "run_manifest.json").read_text())
    assert plan["seed"] == 41
    assert [step["stage"] for step in plan["steps"]] == ["alignment", "trimming", "tree", "normalize_support"]
    assert "41" in plan["steps"][2]["command"]


def test_execute_reuses_complete_outputs_without_calling_tools(tmp_path):
    out = tmp_path / "out"
    args = [sys.executable, str(SCRIPT), str(SKILL / "fixtures" / "markers.tsv"), "--references", str(SKILL / "fixtures" / "references.tsv"), "--out", str(out), "--seed", "41"]
    first = subprocess.run(args, text=True, capture_output=True)
    assert first.returncode == 0, first.stderr
    manifest = json.loads((out / "run_manifest.json").read_text())
    for step in manifest["steps"]:
        for output in step["outputs"]:
            path = Path(output)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("(a:1,b:1)95;\n" if step["stage"] == "tree" else "fixture output\n")
    second = subprocess.run([*args, "--execute"], text=True, capture_output=True)
    assert second.returncode == 0, second.stderr
    rerun = json.loads((out / "run_manifest.json").read_text())
    assert {step["status"] for step in rerun["steps"]} == {"reused"}


def test_supports_are_normalized_to_zero_one(tmp_path):
    out = tmp_path / "support.tsv"
    result = subprocess.run([sys.executable, str(SCRIPT), "--normalize-only", str(SKILL / "fixtures" / "tree.nwk"), "--out", str(out)], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert "95\t0.950000" in out.read_text()


def test_reference_checksum_mismatch_is_rejected(tmp_path):
    refs = tmp_path / "references.tsv"
    refs.write_text(f"accession\tpath\tsha256\nrelative\t{SKILL / 'fixtures' / 'reference.faa'}\tdeadbeef\n")
    result = subprocess.run([sys.executable, str(SCRIPT), str(SKILL / "fixtures" / "markers.tsv"), "--references", str(refs), "--out", str(tmp_path / "out")], text=True, capture_output=True)
    assert result.returncode != 0
    assert "checksum mismatch" in result.stderr
