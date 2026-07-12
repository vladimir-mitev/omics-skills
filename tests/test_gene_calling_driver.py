import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills" / "bio-gene-calling"
SCRIPT = SKILL / "scripts" / "run_gene_calling.py"


def test_domain_routes_and_per_assembly_outputs(tmp_path):
    out = tmp_path / "out"
    result = subprocess.run([sys.executable, str(SCRIPT), str(SKILL / "fixtures" / "assemblies.tsv"), "--tool-manifest", str(SKILL / "fixtures" / "tool-manifest.json"), "--out", str(out)], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    manifest = json.loads((out / "run_manifest.json").read_text())
    callers = {step["assembly_id"]: step["caller"] for step in manifest["steps"] if step["stage"] == "gene_calling"}
    assert callers == {"bacterium": "pyrodigal", "virus": "pyrodigal-gv", "eukaryote": "braker4"}
    assert all(f"/{step['assembly_id']}/" in step["outputs"][0] for step in manifest["steps"] if step["stage"] == "gene_calling")
    census = (out / "ncRNA_census.tsv").read_text()
    assert "RF00177\tdefault" in census and "RF00177\trelaxed" in census
    braker = next(step for step in manifest["steps"] if step.get("caller") == "braker4")
    assert braker["command"][0] == "snakemake"
    assert "$BIO_DB_ROOT" not in json.dumps(manifest)
    assert (out / "eukaryote" / "braker4" / "samples.csv").is_file()
    assert (out / "eukaryote" / "braker4" / "config.ini").is_file()


def test_unpinned_braker_revision_is_rejected(tmp_path):
    tools = json.loads((SKILL / "fixtures" / "tool-manifest.json").read_text())
    tools["braker4"]["repository_revision"] = "main"
    manifest = tmp_path / "tools.json"
    manifest.write_text(json.dumps(tools))
    result = subprocess.run([sys.executable, str(SCRIPT), str(SKILL / "fixtures" / "assemblies.tsv"), "--tool-manifest", str(manifest), "--out", str(tmp_path / "out")], text=True, capture_output=True)
    assert result.returncode != 0
    assert "40-character Git commit" in result.stderr
