from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "bio-prefect-dask-nextflow"


class PrefectDaskNextflowTests(unittest.TestCase):
    def test_prefect_example_defers_cluster_creation_to_task_runner(self) -> None:
        text = (SKILL_ROOT / "prefect-hpc-slurm.md").read_text(encoding="utf-8")
        self.assertIn('cluster_class="dask_jobqueue.SLURMCluster"', text)
        self.assertNotIn("address=build_cluster()", text)

    def test_compound_fastq_suffix_has_explicit_normalizer(self) -> None:
        text = (SKILL_ROOT / "prefect-dask.md").read_text(encoding="utf-8")
        self.assertIn('(".fastq.gz", ".fq.gz", ".fastq", ".fq")', text)
        self.assertNotIn("sample_out = outdir / reads.stem", text)

    def test_slurm_wrapper_passes_account_and_template_to_sbatch(self) -> None:
        wrapper = SKILL_ROOT / "scripts" / "submit_nextflow.sh"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pipeline = root / "main.nf"
            pipeline.write_text("nextflow.enable.dsl=2\n", encoding="utf-8")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            sbatch = fake_bin / "sbatch"
            sbatch.write_text('#!/usr/bin/env bash\nprintf "%s\\n" "$@"\n', encoding="utf-8")
            sbatch.chmod(sbatch.stat().st_mode | stat.S_IXUSR)
            env = os.environ | {
                "PATH": f"{fake_bin}:{os.environ['PATH']}",
                "SLURM_ACCOUNT": "test-account",
            }
            result = subprocess.run(
                [str(wrapper), str(pipeline), "data/*.fastq.gz", str(root / "results")],
                cwd=REPO_ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("test-account", result.stdout)
            self.assertIn("nextflow-run.sbatch", result.stdout)


if __name__ == "__main__":
    unittest.main()
