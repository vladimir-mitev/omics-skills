import importlib.util
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills" / "exploratory-data-analysis"
SCRIPT = SKILL / "scripts" / "eda_analyzer.py"

spec = importlib.util.spec_from_file_location("eda_v15", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_representative_chemistry_spectrometry_and_proteomics_fixtures():
    fixture = SKILL / "fixtures"
    pdb = module.analyze_file(fixture / "structure.pdb")["data_analysis"]
    mgf = module.analyze_file(fixture / "spectra.mgf")["data_analysis"]
    mztab = module.analyze_file(fixture / "results.mztab")["data_analysis"]
    assert pdb["atom_records"] == 2 and pdb["heteroatom_records"] == 1
    assert mgf == {"analysis_scope": "streaming_full_file", "spectra": 1, "peak_rows": 2}
    assert mztab["protein_rows"] == 1 and mztab["psm_rows"] == 1


def test_large_format_paths_are_streaming_or_memory_mapped():
    source = SCRIPT.read_text()
    assert "np.load(filepath, mmap_mode='r')" in source
    assert "'analysis_scope': 'streaming_full_file'" in source
    assert "sequences = list(SeqIO.parse" not in source
