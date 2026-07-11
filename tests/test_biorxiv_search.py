import contextlib
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "biorxiv-search" / "scripts" / "search.py"


def load_search_module():
    spec = importlib.util.spec_from_file_location("biorxiv_search_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class BioRxivPaginationTests(unittest.TestCase):
    def test_follows_api_totals_across_thirty_record_pages(self):
        module = load_search_module()
        records = [
            {
                "doi": f"10.1101/{index:06d}",
                "title": f"Preprint {index}",
                "abstract": "",
                "authors": "A. Author",
                "date": "2026-07-01",
                "version": "1",
            }
            for index in range(65)
        ]
        requested_cursors = []

        def fake_fetch(url, _timeout):
            cursor = int(url.rsplit("/", 2)[-2])
            requested_cursors.append(cursor)
            page = records[cursor : cursor + 30]
            return {
                "messages": [
                    {
                        "status": "ok",
                        "cursor": cursor,
                        "count": len(page),
                        "total": len(records),
                    }
                ],
                "collection": page,
            }

        stdout = io.StringIO()
        argv = [str(SCRIPT), "--days", "7", "--scan-limit", "100"]
        with mock.patch.object(module, "fetch_json", side_effect=fake_fetch), mock.patch.object(
            sys, "argv", argv
        ), contextlib.redirect_stdout(stdout):
            exit_code = module.main()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(requested_cursors, [0, 30, 60])
        self.assertEqual(payload["api"]["pages_fetched"], 3)
        self.assertEqual(payload["api"]["records_scanned"], 65)
        self.assertEqual(payload["api"]["total_available"], 65)
        self.assertFalse(payload["result_summary"]["reached_scan_limit"])


if __name__ == "__main__":
    unittest.main()
