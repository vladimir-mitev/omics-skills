import contextlib
import importlib.util
import io
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "exploratory-data-analysis" / "scripts" / "eda_analyzer.py"


def load_eda_module():
    spec = importlib.util.spec_from_file_location("eda_analyzer_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class _NullCounts:
    def sum(self):
        return self

    def to_dict(self):
        return {"value": 0}


class _FakeFrame:
    def __init__(self, rows):
        self._rows = rows
        self.columns = ["value"]
        self.dtypes = {"value": "int64"}

    def __len__(self):
        return self._rows

    @property
    def shape(self):
        return (self._rows, 1)

    @property
    def iloc(self):
        return self

    def __getitem__(self, row_slice):
        return _FakeFrame(min(self._rows, row_slice.stop))

    def copy(self):
        return self

    def isnull(self):
        return _NullCounts()

    def select_dtypes(self, include=None):
        return types.SimpleNamespace(columns=[])


class ExploratoryDataAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.module = load_eda_module()

    def test_detects_bounded_compound_suffixes(self):
        self.assertEqual(
            self.module.detect_file_type("image.ome.tiff"),
            ("ome.tiff", "microscopy_imaging", "OME-TIFF"),
        )
        self.assertEqual(
            self.module.detect_file_type("reads.fastq.gz"),
            ("fastq.gz", "bioinformatics_genomics", "Compressed FASTQ Format"),
        )
        reference = self.module.load_reference_info("bioinformatics_genomics", "fq.gz")
        self.assertIsNotNone(reference)
        self.assertIn("FASTQ Format", reference["raw_section"])

    def test_csv_analysis_labels_first_row_sampling(self):
        def read_csv(_filepath, *, sep, nrows):
            self.assertEqual(sep, ",")
            self.assertEqual(nrows, self.module.CSV_SAMPLE_LIMIT + 1)
            return _FakeFrame(nrows)

        fake_pandas = types.SimpleNamespace(read_csv=read_csv)
        with mock.patch.dict(sys.modules, {"pandas": fake_pandas}):
            result = self.module.analyze_general_scientific("unused.csv", "csv")

        self.assertEqual(result["analysis_scope"], "sample")
        self.assertEqual(result["sampling"]["method"], "first_rows")
        self.assertEqual(result["sampling"]["rows_sampled"], 10_000)
        self.assertTrue(result["sampling"]["more_rows_present"])
        self.assertEqual(result["sample_shape"], (10_000, 1))

    def test_cli_default_name_and_generated_output_have_no_emoji(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "records.json"
            input_path.write_text('{"records": []}', encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = self.module.main([str(input_path)])

            report_path = Path(directory) / "records_eda_report.md"
            report = report_path.read_text(encoding="utf-8")

        self.assertEqual(exit_code, 0)
        self.assertTrue(report_path.name.endswith("_eda_report.md"))
        self.assertNotIn("✓", stdout.getvalue())
        self.assertNotIn("⚠", report)

    def test_script_declares_pep_723_dependencies(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("# /// script", source)
        self.assertIn('"pandas>=2.0"', source)
        self.assertIn('"biopython>=1.83"', source)


if __name__ == "__main__":
    unittest.main()
