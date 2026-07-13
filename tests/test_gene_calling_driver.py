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


def test_plan_is_idempotent_and_execute_reuses_complete_outputs(tmp_path):
    out = tmp_path / "out"
    args = [sys.executable, str(SCRIPT), str(SKILL / "fixtures" / "assemblies.tsv"), "--tool-manifest", str(SKILL / "fixtures" / "tool-manifest.json"), "--out", str(out)]
    first = subprocess.run(args, text=True, capture_output=True)
    assert first.returncode == 0, first.stderr
    second = subprocess.run(args, text=True, capture_output=True)
    assert second.returncode == 0, second.stderr
    manifest = json.loads((out / "run_manifest.json").read_text())
    for step in manifest["steps"]:
        for output in step["outputs"]:
            path = Path(output)
            path.parent.mkdir(parents=True, exist_ok=True)
            if step["stage"] == "trna":
                path.write_text("Sequence tRNA # Begin End Type Codon IntronBegin IntronEnd Score\nseq 1 1 70 Ala TGC 0 0 55.0\n")
            elif step["stage"] == "rrna":
                path.write_text("# cmsearch tblout\nseq model query cm 1 10 1 10 + no 1 0.5 0.0 42.0 1e-10 ! description\n")
            else:
                path.write_text("fixture output\n")
    executed = subprocess.run([*args, "--execute"], text=True, capture_output=True)
    assert executed.returncode == 0, executed.stderr
    rerun = json.loads((out / "run_manifest.json").read_text())
    assert {step["status"] for step in rerun["steps"]} == {"reused"}
    census = (out / "ncRNA_census.tsv").read_text()
    assert "\t1\tcompleted" in census
