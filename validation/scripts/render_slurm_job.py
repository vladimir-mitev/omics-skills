#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema==4.25.1"]
# ///
"""Render a validated, checksum-gated Slurm job without submitting it."""

from __future__ import annotations

import argparse
import json
import re
import shlex
from pathlib import Path, PurePosixPath

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "slurm-job.schema.json"
PLACEHOLDERS = {"TBD", "REQUIRED", "CHOOSE_ON_LOGIN_NODE"}


def reject_placeholders(value: object, path: str = "<root>") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            reject_placeholders(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            reject_placeholders(item, f"{path}[{index}]")
    elif isinstance(value, str) and value in PLACEHOLDERS:
        raise ValueError(f"{path} is unresolved")


def load_job(path: Path) -> dict[str, object]:
    job = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(job), key=lambda item: list(item.absolute_path))
    if errors:
        detail = "; ".join(
            f"{'.'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
            for error in errors
        )
        raise ValueError(detail)
    if job["status"] != "ready":
        raise ValueError("job status must be ready before rendering")
    reject_placeholders(job)
    workdir = PurePosixPath(job["workdir"])
    if not workdir.is_absolute():
        raise ValueError("workdir must be an absolute path for a ready job")
    logs_dir = PurePosixPath(job["logs_dir"])
    if logs_dir.is_absolute() or ".." in logs_dir.parts:
        raise ValueError("logs_dir must be relative to workdir and contained within it")
    for output in job["expected_outputs"]:
        candidate = PurePosixPath(output["path"])
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError(f"expected output must be relative and contained: {output['path']}")
    return job


def shell_array(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def render(job: dict[str, object]) -> str:
    scheduler = job["scheduler"]
    hours, minutes = divmod(scheduler["time_minutes"], 60)
    job_name = re.sub(r"[^a-zA-Z0-9_-]", "-", job["validation_id"])[:128]
    absolute_log_dir = str(PurePosixPath(job["workdir"]) / job["logs_dir"])
    log_dir = shlex.quote(absolute_log_dir)
    lines = [
        "#!/usr/bin/env bash",
        f"# Validation cluster: {scheduler['cluster']}",
        f"#SBATCH --job-name={job_name}",
        f"#SBATCH --account={scheduler['account']}",
        f"#SBATCH --partition={scheduler['partition']}",
        f"#SBATCH --qos={scheduler['qos']}",
        f"#SBATCH --cpus-per-task={scheduler['cpus']}",
        f"#SBATCH --mem={scheduler['memory_mb']}M",
        f"#SBATCH --time={hours:02d}:{minutes:02d}:00",
        f"#SBATCH --output={absolute_log_dir}/slurm-%j.out",
        f"#SBATCH --error={absolute_log_dir}/slurm-%j.err",
        "",
        "set -euo pipefail",
        "umask 027",
        f"cd {shlex.quote(job['workdir'])}",
        f"mkdir -p {log_dir}",
        f"receipt={log_dir}/run-receipt.tsv",
        f"versions={log_dir}/tool-versions.txt",
        f"timing={log_dir}/time.txt",
        "",
        "tree_sha256() {",
        "    local target=$1",
        "    (",
        "        cd \"$target\"",
        "        while IFS= read -r -d '' file; do",
        "            [[ -f $file ]] || continue",
        "            printf '%s\\0' \"${file#./}\"",
        "            sha256sum \"$file\" | awk '{print $1}'",
        "        done < <(find . \\( -type f -o -type l \\) -print0 | LC_ALL=C sort -z)",
        "    ) | sha256sum | awk '{print $1}'",
        "}",
        "check_resource() {",
        "    local kind=$1 target=$2 expected=$3 actual",
        "    if [[ $kind == file ]]; then",
        "        [[ -s $target ]] || { echo \"missing resource file: $target\" >&2; exit 1; }",
        "        actual=$(sha256sum \"$target\" | awk '{print $1}')",
        "    else",
        "        [[ -d $target ]] || { echo \"missing resource directory: $target\" >&2; exit 1; }",
        "        actual=$(tree_sha256 \"$target\")",
        "    fi",
        "    [[ $actual == $expected ]] || { echo \"resource checksum mismatch: $target\" >&2; exit 1; }",
        "}",
        "",
    ]
    for resource in [job["environment"], *job["databases"]]:
        lines.append(
            "check_resource "
            f"{shlex.quote(resource['kind'])} {shlex.quote(resource['path'])} {shlex.quote(resource['sha256'])}"
        )
    lines.extend(["", ": > \"$versions\""])
    for command in job["version_commands"]:
        joined = shell_array(command)
        lines.extend(
            [
                f"printf '%s\\n' {shlex.quote('$ ' + shlex.join(command))} >> \"$versions\"",
                f"({joined}) >> \"$versions\" 2>&1",
            ]
        )
    command = shell_array(job["command"])
    lines.extend(
        [
            "",
            "start_epoch=$(date +%s)",
            "set +e",
            "if [[ -x /usr/bin/time ]]; then",
            f"    /usr/bin/time -v -o \"$timing\" -- {command}",
            "    exit_code=$?",
            "else",
            f"    {command}",
            "    exit_code=$?",
            "    printf 'GNU time unavailable; use sacct MaxRSS for peak memory.\\n' > \"$timing\"",
            "fi",
            "set -e",
            "end_epoch=$(date +%s)",
            "printf 'validation_id\\tjob_id\\texit_code\\tstart_epoch\\tend_epoch\\n' > \"$receipt\"",
            f"printf '%s\\t%s\\t%s\\t%s\\t%s\\n' {shlex.quote(job['validation_id'])} \"${{SLURM_JOB_ID:-unknown}}\" \"$exit_code\" \"$start_epoch\" \"$end_epoch\" >> \"$receipt\"",
            "[[ $exit_code -eq 0 ]] || exit \"$exit_code\"",
        ]
    )
    for output in job["expected_outputs"]:
        target = shlex.quote(output["path"])
        lines.append(
            f"[[ -f {target} && $(stat -c %s {target}) -ge {output['min_bytes']} ]] "
            f"|| {{ echo {shlex.quote('missing or undersized output: ' + output['path'])} >&2; exit 1; }}"
        )
    lines.extend(["", "printf 'validation job completed and outputs passed size gates\\n'", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        job = load_job(args.manifest)
        script = render(job)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(script)
        args.output.chmod(0o750)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
