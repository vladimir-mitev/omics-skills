import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills" / "bio-protein-clustering-pangenome"
SCRIPT = SKILL / "scripts" / "build_pangenome_artifacts.py"


def test_small_multigenome_fixture_persists_all_comparison_axes(tmp_path):
    fixture = SKILL / "fixtures"
    out = tmp_path / "out"
    result = subprocess.run(["uv", "run", "--script", str(SCRIPT), str(fixture / "orthogroups.tsv"), "--genomes", str(fixture / "genomes.tsv"), "--marker-catalog", str(fixture / "marker_catalog.tsv"), "--marker-hits", str(fixture / "marker_hits.tsv"), "--ncrna", str(fixture / "ncRNA_census.tsv"), "--out", str(out)], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    expected = {"presence_absence.parquet", "copy_number_matrix.parquet", "relative_genome_metrics.tsv", "family_copy_number_comparison.tsv", "conserved_neighborhoods.tsv", "marker_census.tsv", "ncRNA_census.tsv"}
    assert expected <= {path.name for path in out.iterdir()}
    assert "query\tstructural\tOG4\tstructural protein\t0\texplicit_absence" in (out / "marker_census.tsv").read_text()
    assert "qctg:OG1-OG2\trelative_a\tactg:OG1-OG2" in (out / "conserved_neighborhoods.tsv").read_text()
    assert "OG3\tquery\t1\t0\tinf\tquery_specific" in (out / "family_copy_number_comparison.tsv").read_text()
