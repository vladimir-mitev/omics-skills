import json
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills" / "bio-viromics"
SCRIPT = SKILL / "scripts" / "build_viromics_evidence.py"


def command(out, hypotheses=None):
    fixture = SKILL / "fixtures"
    return ["uv", "run", "--script", str(SCRIPT), str(fixture / "metrics.tsv"), "--resources", str(fixture / "resources.json"), "--hypotheses", str(hypotheses or fixture / "hypotheses.tsv"), "--reflections", str(fixture / "reflections.tsv"), "--comparative-dir", str(fixture / "comparative"), "--out", str(out)]


def test_viromics_bundle_has_pinned_resources_comparative_axes_and_reflections(tmp_path):
    out = tmp_path / "out"
    result = subprocess.run(command(out), text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    expected = {"marker_census.tsv", "family_copy_number_comparison.tsv", "conserved_neighborhoods.tsv", "ncRNA_census.tsv", "hypothesis_register.tsv", "intermediate_reflections.tsv", "genome_size_frontier.tsv", "run_manifest.json"}
    assert expected <= {path.name for path in out.iterdir()}
    manifest = json.loads((out / "run_manifest.json").read_text())
    assert manifest["hypothesis_count"] == 5
    assert manifest["reflection_stages"][0] == "initial" and manifest["reflection_stages"][-1] == "final"
    assert "query\tquery\tfixturevirus\t1200" in (out / "genome_size_frontier.tsv").read_text()


def test_fewer_than_five_hypotheses_is_rejected(tmp_path):
    source = SKILL / "fixtures" / "hypotheses.tsv"
    short = tmp_path / "hypotheses.tsv"
    short.write_text("\n".join(source.read_text().splitlines()[:-1]) + "\n")
    result = subprocess.run(command(tmp_path / "out", short), text=True, capture_output=True)
    assert result.returncode != 0
    assert "at least five" in result.stderr


def test_real_database_directories_are_checksum_supported(tmp_path):
    fixture = SKILL / "fixtures"
    database = tmp_path / "genomad-db"
    database.mkdir()
    (database / "a.txt").write_text("alpha\n")
    (database / "b.txt").write_text("beta\n")
    digest = hashlib.sha256()
    for path in sorted(database.iterdir()):
        digest.update(path.name.encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).hexdigest().encode())
        digest.update(b"\n")
    resources = json.loads((fixture / "resources.json").read_text())
    for name in ("genomad_db", "checkv_db", "gvclass_db", "vcontact3_db"):
        resources["resources"][name].update(
            {"path": str(database), "kind": "directory", "sha256": digest.hexdigest()}
        )
    resource_path = tmp_path / "resources.json"
    resource_path.write_text(json.dumps(resources))
    out = tmp_path / "out"
    args = command(out)
    args[args.index("--resources") + 1] = str(resource_path)
    result = subprocess.run(args, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    manifest = json.loads((out / "run_manifest.json").read_text())
    assert manifest["resources"]["genomad_db"]["kind"] == "directory"
