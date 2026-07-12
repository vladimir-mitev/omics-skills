import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills" / "bio-interdomain-hgt"
SCRIPT = SKILL / "scripts" / "run_hgt_evidence.py"


def command(out, context=None):
    f = SKILL / "fixtures"
    return ["uv", "run", "--script", str(SCRIPT), str(f / "forward_hits.tsv"), "--arbiter-hits", str(f / "arbiter_hits.tsv"), "--reciprocal", str(f / "reciprocal.tsv"), "--context", str(context or f / "context.tsv"), "--trees", str(f / "trees.tsv"), "--sampling-depth", str(f / "sampling_depth.tsv"), "--databases", str(f / "databases.json"), "--hypotheses", str(f / "hypotheses.tsv"), "--reflections", str(f / "reflections.tsv"), "--query-domain", "ncldv", "--out", str(out)]


def test_fixture_confirms_direction_with_all_gates_and_normalization(tmp_path):
    out = tmp_path / "out"
    result = subprocess.run(command(out), text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    candidates = (out / "hgt_candidates.tsv").read_text()
    assert "recipient_to_query\ttrue\ttrue\t0.97\ttrue\tconfirmed" in candidates
    assert "EukFixture\t1\t20\t5.000000" in (out / "lineage_sampling_normalization.tsv").read_text()
    manifest = json.loads((out / "run_manifest.json").read_text())
    assert manifest["confirmed_count"] == 1
    assert manifest["gates"] == ["database", "forward", "reciprocal", "context", "phylogeny", "final"]


def test_eukaryotic_context_must_be_frame_aware(tmp_path):
    source = SKILL / "fixtures" / "context.tsv"
    context = tmp_path / "context.tsv"
    context.write_text(source.read_text().replace("diamond_blastx", "pyrodigal"))
    out = tmp_path / "out"
    result = subprocess.run(command(out, context), text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert "recipient_to_query\tfalse\tfalse\t0.97\ttrue\tcandidate" in (out / "hgt_candidates.tsv").read_text()
