from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OCR_SCRIPT = REPO_ROOT / "skills" / "pdf-to-md" / "scripts" / "ocr_api_job.py"
LITEPARSE_SCRIPT = REPO_ROOT / "skills" / "pdf-to-md" / "scripts" / "liteparse_to_md.py"

SPEC = importlib.util.spec_from_file_location("ocr_api_job", OCR_SCRIPT)
ocr_api_job = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(ocr_api_job)


class PdfToMarkdownSafetyTests(unittest.TestCase):
    def test_remote_ocr_requires_explicit_opt_in(self) -> None:
        with self.assertRaises(SystemExit):
            ocr_api_job.resolve_base_url(
                "https://api.example.org/ocr",
                allow_remote=False,
            )
        self.assertEqual(
            ocr_api_job.resolve_base_url(
                "https://api.example.org/ocr",
                allow_remote=True,
            ),
            "https://api.example.org/ocr",
        )

    def test_local_ocr_needs_no_remote_opt_in(self) -> None:
        self.assertEqual(
            ocr_api_job.resolve_base_url(None, allow_remote=False),
            ocr_api_job.LOCAL_BASE_URL,
        )

    def test_secret_values_are_not_cli_options(self) -> None:
        result = subprocess.run(
            [sys.executable, str(OCR_SCRIPT), "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--allow-remote", result.stdout)
        self.assertNotIn("--api-key", result.stdout)

        liteparse_source = LITEPARSE_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"--password-env"', liteparse_source)
        self.assertNotIn('"--password"', liteparse_source)


if __name__ == "__main__":
    unittest.main()
