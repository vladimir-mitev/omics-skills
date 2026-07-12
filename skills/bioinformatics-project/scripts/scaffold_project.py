#!/usr/bin/env python3
"""Create or verify a minimal reproducible bioinformatics project scaffold."""

from __future__ import annotations

import argparse
import re
import stat
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
GITIGNORE_TEMPLATE = SKILL_ROOT / "examples" / "gitignore.example"


def pixi_name(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-")
    if not normalized:
        raise ValueError("project name must contain at least one letter or number")
    return normalized


def scaffold_files(project_name: str, objective: str) -> dict[Path, tuple[str, bool]]:
    pixi_project_name = pixi_name(project_name)
    return {
        Path("README.md"): (
            f"# {project_name}\n\n"
            f"## Objective\n\n{objective}\n\n"
            "## Reproduce\n\n"
            "1. Put immutable inputs under `data/raw/` and record their provenance in `data/README.md`.\n"
            "2. Resolve the environment with `pixi install` and commit `pixi.lock`.\n"
            "3. Fill `tasks/hypotheses.md` before exploratory analysis.\n"
            "4. Add one dated `results/YYYY-MM-DD_topic/runall` driver per experiment.\n",
            False,
        ),
        Path("SUMMARY.md"): (
            "# Project status\n\n"
            "No analysis has run. Record current counts, passed QC gates, and deliverables here.\n",
            False,
        ),
        Path("pixi.toml"): (
            "[workspace]\n"
            'channels = ["conda-forge", "bioconda"]\n'
            f'name = "{pixi_project_name}"\n'
            'platforms = ["linux-64"]\n'
            'version = "0.1.0"\n\n'
            "[tasks]\n\n"
            "[dependencies]\n",
            False,
        ),
        Path(".gitignore"): (GITIGNORE_TEMPLATE.read_text(encoding="utf-8"), False),
        Path("tasks/todo.md"): (
            "# Tasks\n\n- [ ] Define the first verifiable analysis outcome and its proof.\n",
            False,
        ),
        Path("tasks/METHODS.md"): (
            "# Methods\n\nRecord exact commands, versions, parameters, seeds, databases, checksums, and job IDs.\n",
            False,
        ),
        Path("tasks/lessons.md"): ("# Lessons\n\n", False),
        Path("tasks/hypotheses.md"): (
            "# Hypothesis register\n\n"
            "Replace each placeholder before exploratory analysis and keep ruled-out entries visible.\n\n"
            "| ID | Type | Working explanation | Status | Discriminating check |\n"
            "|---|---|---|---|---|\n"
            "| H1 | biological | Define a biological mechanism. | unresolved | Define a test. |\n"
            "| H2 | technical | Define a pipeline or measurement artifact. | unresolved | Define a control. |\n"
            "| H3 | null | Define the no-effect explanation. | unresolved | Define a null comparison. |\n"
            "| H4 | sampling | Define a sampling or batch explanation. | unresolved | Define a stratified check. |\n"
            "| H5 | database | Define a reference/database explanation. | unresolved | Define a database comparison. |\n",
            False,
        ),
        Path("data/README.md"): (
            "# Data provenance\n\n"
            "For each input, record its source, version, retrieval command, checksum, and license.\n",
            False,
        ),
        Path("data/samples.tsv"): ("sample_id\tinput_path\n", False),
        Path("results/lab_notebook.md"): (
            "# Lab notebook\n\n"
            "Add dated entries with the goal, command or driver, QC result, interpretation, and next check.\n",
            False,
        ),
        Path("results/runall.example"): (
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n\n"
            'printf "Replace results/runall.example with a dated experiment driver.\\n" >&2\n'
            "exit 1\n",
            True,
        ),
        Path("src/.gitkeep"): ("", False),
        Path("bin/.gitkeep"): ("", False),
        Path("doc/.gitkeep"): ("", False),
    }


def conflicts(project_root: Path, files: dict[Path, tuple[str, bool]]) -> list[Path]:
    return [
        relative
        for relative, (content, _) in files.items()
        if (project_root / relative).exists()
        and (project_root / relative).read_text(encoding="utf-8") != content
    ]


def apply_scaffold(project_root: Path, files: dict[Path, tuple[str, bool]]) -> tuple[int, int]:
    created = 0
    unchanged = 0
    for relative, (content, executable) in files.items():
        target = project_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            unchanged += 1
            continue
        target.write_text(content, encoding="utf-8")
        if executable:
            target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        created += 1
    return created, unchanged


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--name", help="Project display name; defaults to the directory name")
    parser.add_argument("--objective", required=True, help="One-sentence project objective")
    parser.add_argument("--check", action="store_true", help="Verify the scaffold without writing")
    args = parser.parse_args(argv)

    project_root = args.project_dir.expanduser().resolve()
    project_name = args.name or project_root.name
    try:
        files = scaffold_files(project_name, args.objective.strip())
    except ValueError as exc:
        parser.error(str(exc))

    mismatches = conflicts(project_root, files) if project_root.exists() else []
    if mismatches:
        print("Scaffold conflicts; no files changed:")
        for path in mismatches:
            print(f"  {path}")
        return 2

    if args.check:
        missing = [relative for relative in files if not (project_root / relative).exists()]
        if missing:
            print("Scaffold is incomplete:")
            for path in missing:
                print(f"  {path}")
            return 1
        print(f"Scaffold valid: {project_root}")
        return 0

    project_root.mkdir(parents=True, exist_ok=True)
    created, unchanged = apply_scaffold(project_root, files)
    print(f"Scaffold ready: {project_root} ({created} created, {unchanged} unchanged)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
