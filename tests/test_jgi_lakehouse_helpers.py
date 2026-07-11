from __future__ import annotations

import importlib.util
import contextlib
import io
import json
import os
import stat
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


download_img_genomes = load_module(
    "download_img_genomes",
    REPO_ROOT / "skills" / "jgi-lakehouse" / "scripts" / "download_img_genomes.py",
)
rest_client = load_module(
    "jgi_rest_client",
    REPO_ROOT / "skills" / "jgi-lakehouse" / "scripts" / "rest_client.py",
)
find_16s = load_module(
    "jgi_find_16s",
    REPO_ROOT / "skills" / "jgi-lakehouse" / "examples" / "find_16s_rrna_genes.py",
)


class JgiDownloadHelperTests(unittest.TestCase):
    def test_find_genomes_rejects_untrusted_domain_before_query(self) -> None:
        with patch.object(download_img_genomes, "query") as query:
            with self.assertRaises(ValueError):
                download_img_genomes.find_genomes("Bacteria'; DROP TABLE taxon; --")
            query.assert_not_called()

    def test_find_genomes_validates_limit_before_query(self) -> None:
        with patch.object(download_img_genomes, "query") as query:
            with self.assertRaises(ValueError):
                download_img_genomes.find_genomes("Bacteria", limit=0)
            query.assert_not_called()

    def test_safe_extract_tar_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            archive = tmp / "unsafe.tar.gz"
            outside = tmp / "evil.txt"

            data = b"unsafe"
            info = tarfile.TarInfo("../evil.txt")
            info.size = len(data)
            with tarfile.open(archive, "w:gz") as tar:
                tar.addfile(info, io.BytesIO(data))

            with tarfile.open(archive, "r:gz") as tar:
                with self.assertRaises(ValueError):
                    download_img_genomes.safe_extract_tar(tar, tmp / "extract")

            self.assertFalse(outside.exists())

    def test_safe_extract_tar_rejects_special_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            archive = tmp / "special.tar.gz"
            info = tarfile.TarInfo("named-pipe")
            info.type = tarfile.FIFOTYPE
            with tarfile.open(archive, "w:gz") as tar:
                tar.addfile(info)

            with tarfile.open(archive, "r:gz") as tar:
                with self.assertRaisesRegex(ValueError, "special file"):
                    download_img_genomes.safe_extract_tar(tar, tmp / "extract")

    def test_query_has_overall_polling_deadline(self) -> None:
        post_response = Mock()
        post_response.json.return_value = {"id": "job-1"}
        with (
            patch.object(download_img_genomes, "get_token", return_value="test-token"),
            patch.object(download_img_genomes, "DREMIO_JOB_TIMEOUT", 0),
            patch.object(
                download_img_genomes.requests, "post", return_value=post_response
            ) as post,
            patch.object(download_img_genomes.requests, "get") as get,
        ):
            with self.assertRaises(TimeoutError):
                download_img_genomes.query("SELECT 1")
        get.assert_not_called()
        self.assertNotIn("verify", post.call_args.kwargs)

    def test_directory_fallback_fails_when_no_expected_files_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "source"
            source.mkdir()
            with patch.object(
                download_img_genomes,
                "check_file_availability",
                return_value={"available": True, "type": "directory", "path": str(source)},
            ):
                result = download_img_genomes.download_genome("123", root / "output")
        self.assertFalse(result["success"])
        self.assertEqual(result["files_copied"], [])
        self.assertIn("none of the expected", result["error"])

    def test_count_argument_reports_clean_argparse_error(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()) as stderr:
            with self.assertRaises(SystemExit) as error:
                download_img_genomes.main(["--count", "0"])
        self.assertEqual(error.exception.code, 2)
        self.assertIn("limit must be between", stderr.getvalue())


class JgiRestClientTests(unittest.TestCase):
    def test_request_options_keep_requests_tls_verification_default(self) -> None:
        options = rest_client.request_options()
        self.assertNotIn("verify", options)
        self.assertIn("timeout", options)

    def test_wait_for_job_enforces_overall_deadline(self) -> None:
        with (
            patch.object(rest_client.time, "monotonic", side_effect=[10.0, 11.1]),
            patch.object(rest_client, "get_job_status") as get_status,
        ):
            with self.assertRaises(TimeoutError):
                rest_client.wait_for_job("job-1", timeout=1)
        get_status.assert_not_called()

    def test_wait_for_job_caps_status_request_at_remaining_deadline(self) -> None:
        with (
            patch.object(rest_client.time, "monotonic", side_effect=[10.0, 10.25]),
            patch.object(
                rest_client, "get_job_status", return_value={"jobState": "COMPLETED"}
            ) as get_status,
        ):
            rest_client.wait_for_job("job-1", timeout=1)
        self.assertAlmostEqual(get_status.call_args.kwargs["request_timeout"], 0.75)

    def test_cli_does_not_print_token_prefix(self) -> None:
        source = (REPO_ROOT / "skills" / "jgi-lakehouse" / "scripts" / "rest_client.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("token[:", source)
        self.assertIn('print("Token: configured")', source)


class JgiExampleTests(unittest.TestCase):
    def test_find_16s_rejects_sql_metacharacters_before_query(self) -> None:
        with patch.object(find_16s, "query") as query:
            with self.assertRaises(ValueError):
                find_16s.find_16s_by_family_pattern(["Rhodobacter'; DROP TABLE gene; --"])
        query.assert_not_called()


class JgiCredentialHelperTests(unittest.TestCase):
    def test_token_helper_json_encodes_credentials_and_never_prints_token(self) -> None:
        script = REPO_ROOT / "skills" / "jgi-lakehouse" / "scripts" / "get_dremio_token.sh"
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            captured_payload = root / "payload.json"
            fake_curl = fake_bin / "curl"
            fake_curl.write_text(
                """#!/bin/sh
set -eu
output=
payload=
while [ \"$#\" -gt 0 ]; do
  case \"$1\" in
    --output) output=$2; shift 2 ;;
    --data-binary) payload=${2#@}; shift 2 ;;
    --write-out) shift 2 ;;
    *) shift ;;
  esac
done
cp \"$payload\" \"$CAPTURE_PAYLOAD\"
printf '%s' '{\"token\":\"generated-test-token\"}' > \"$output\"
printf '%s' 200
""",
                encoding="utf-8",
            )
            fake_curl.chmod(0o755)
            env = {
                **os.environ,
                "HOME": str(root),
                "PATH": f"{fake_bin}:{os.environ['PATH']}",
                "CAPTURE_PAYLOAD": str(captured_payload),
            }
            username = 'user"name'
            password = 'pass\\word"value'
            result = subprocess.run(
                ["bash", str(script)],
                input=f"{username}\n{password}\n",
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("generated-test-token", result.stdout + result.stderr)
            self.assertEqual(
                json.loads(captured_payload.read_text(encoding="utf-8")),
                {"userName": username, "password": password},
            )
            token_path = root / ".secrets" / "dremio_pat"
            self.assertEqual(token_path.read_text(encoding="utf-8"), "generated-test-token\n")
            self.assertEqual(stat.S_IMODE(token_path.stat().st_mode), 0o600)

    def test_token_helper_rejects_credentials_in_arguments(self) -> None:
        script = REPO_ROOT / "skills" / "jgi-lakehouse" / "scripts" / "get_dremio_token.sh"
        result = subprocess.run(
            ["bash", str(script), "example-user", "example-password"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("credentials are read interactively", result.stderr)
        self.assertNotIn("example-password", result.stdout + result.stderr)

    def test_skill_contains_no_tls_bypass_or_http_lakehouse_endpoint(self) -> None:
        skill_root = REPO_ROOT / "skills" / "jgi-lakehouse"
        corpus = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in skill_root.rglob("*")
            if path.is_file()
        )
        for forbidden in (
            "--insecure",
            "--no-check-certificate",
            "DREMIO_VERIFY_TLS",
            "http://lakehouse",
            "verify=False",
            "verify = False",
            '"tls": False',
            "'tls': False",
        ):
            self.assertNotIn(forbidden, corpus)


if __name__ == "__main__":
    unittest.main()
