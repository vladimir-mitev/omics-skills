#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "duckdb==1.5.3",
#   "pydantic==2.13.4",
# ]
# ///
"""Validate sample JSONL before writing normalized Parquet and DuckDB outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from datetime import date
from pathlib import Path
from typing import Literal

import duckdb
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class Sample(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    sample_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
    organism: str = Field(min_length=1)
    collection_date: date
    platform: Literal["ILLUMINA", "PACBIO", "NANOPORE"]
    read_count: int = Field(gt=0)
    mean_coverage: float = Field(ge=0)


def rejection(line_number: int, error_type: str, message: str, location: str = "record") -> dict[str, object]:
    return {
        "line": line_number,
        "errors": [{"location": location, "type": error_type, "message": message}],
    }


def load_samples(path: Path) -> tuple[list[tuple[int, Sample]], list[dict[str, object]]]:
    samples: list[tuple[int, Sample]] = []
    rejected: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
                samples.append((line_number, Sample.model_validate(payload)))
            except json.JSONDecodeError as exc:
                rejected.append(rejection(line_number, "json_invalid", exc.msg))
            except ValidationError as exc:
                errors = [
                    {
                        "location": ".".join(str(part) for part in item["loc"]),
                        "type": item["type"],
                        "message": item["msg"],
                    }
                    for item in exc.errors(include_input=False, include_url=False)
                ]
                rejected.append({"line": line_number, "errors": errors})
    return samples, rejected


def write_rejection_report(project_root: Path, input_path: Path, rejected: list[dict[str, object]]) -> None:
    result_dir = project_root / "results" / "bio-foundation-housekeeping"
    log_dir = result_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "rejected",
        "input_file": input_path.name,
        "rejected_records": rejected,
    }
    (result_dir / "rejections.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    (result_dir / "report.md").write_text(
        "# Metadata validation report\n\n"
        f"Status: rejected before Parquet or DuckDB ingestion.\n\nRejected records: {len(rejected)}.\n",
        encoding="utf-8",
    )
    (log_dir / "run.log").write_text(
        f"validation failed for {len(rejected)} record(s)\n", encoding="utf-8"
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_outputs(project_root: Path, input_path: Path, samples: list[Sample]) -> tuple[Path, Path]:
    normalized_dir = project_root / "data" / "normalized"
    catalog_path = project_root / "data" / "catalog.duckdb"
    parquet_path = normalized_dir / "samples.parquet"
    result_dir = project_root / "results" / "bio-foundation-housekeeping"
    log_dir = result_dir / "logs"

    for target in (catalog_path, parquet_path):
        if target.exists():
            raise FileExistsError(f"refusing to overwrite existing output: {target}")

    project_root.mkdir(parents=True, exist_ok=True)
    normalized_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    temp_dir = Path(tempfile.mkdtemp(prefix="foundation-", dir=project_root))
    temp_catalog = temp_dir / "catalog.duckdb"
    temp_parquet = temp_dir / "samples.parquet"
    rows = [sample.model_dump(mode="json") for sample in samples]

    try:
        connection = duckdb.connect(str(temp_catalog))
        connection.execute(
            """
            CREATE TABLE samples (
                sample_id VARCHAR PRIMARY KEY,
                organism VARCHAR NOT NULL,
                collection_date DATE NOT NULL,
                platform VARCHAR NOT NULL,
                read_count BIGINT NOT NULL CHECK (read_count > 0),
                mean_coverage DOUBLE NOT NULL CHECK (mean_coverage >= 0)
            )
            """
        )
        connection.executemany(
            "INSERT INTO samples VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    row["sample_id"],
                    row["organism"],
                    row["collection_date"],
                    row["platform"],
                    row["read_count"],
                    row["mean_coverage"],
                )
                for row in rows
            ],
        )
        connection.execute("COPY samples TO ? (FORMAT PARQUET, COMPRESSION zstd)", [str(temp_parquet)])
        parquet_digest = sha256(temp_parquet)
        parquet_rows = connection.execute(
            "SELECT COUNT(*) FROM read_parquet(?)", [str(temp_parquet)]
        ).fetchone()[0]
        if parquet_rows != len(samples):
            raise RuntimeError(
                f"Parquet row count mismatch: expected {len(samples)}, found {parquet_rows}"
            )
        connection.execute(
            "CREATE TABLE catalog_sources (table_name VARCHAR PRIMARY KEY, parquet_path VARCHAR, sha256 VARCHAR)"
        )
        connection.execute(
            "INSERT INTO catalog_sources VALUES (?, ?, ?)",
            ["samples", str(parquet_path), parquet_digest],
        )
        loaded = connection.execute("SELECT COUNT(*) FROM samples").fetchone()[0]
        if loaded != len(samples):
            raise RuntimeError(f"catalog row count mismatch: expected {len(samples)}, found {loaded}")
        connection.close()

        temp_parquet.replace(parquet_path)
        temp_catalog.replace(catalog_path)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    (result_dir / "report.md").write_text(
        "# Metadata validation report\n\n"
        "Status: passed.\n\n"
        f"Validated records: {len(samples)}.\n\n"
        f"Input: `{input_path.name}`.\n\n"
        f"Parquet SHA-256: `{sha256(parquet_path)}`.\n",
        encoding="utf-8",
    )
    (log_dir / "run.log").write_text(
        f"validated and ingested {len(samples)} record(s)\n", encoding="utf-8"
    )
    return parquet_path, catalog_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="JSONL sample records")
    parser.add_argument("--project-root", type=Path, required=True)
    args = parser.parse_args(argv)

    input_path = args.input.expanduser().resolve()
    project_root = args.project_root.expanduser().resolve()
    if not input_path.is_file():
        parser.error(f"input does not exist: {input_path}")

    numbered_samples, rejected = load_samples(input_path)
    seen_ids: set[str] = set()
    for line_number, sample in numbered_samples:
        if sample.sample_id in seen_ids:
            rejected.append(
                rejection(
                    line_number,
                    "duplicate_sample_id",
                    "sample_id must be unique",
                    "sample_id",
                )
            )
        seen_ids.add(sample.sample_id)
    if rejected:
        write_rejection_report(project_root, input_path, rejected)
        print(f"Rejected {len(rejected)} record(s) before ingestion")
        return 2
    if not numbered_samples:
        write_rejection_report(project_root, input_path, [rejection(0, "empty_input", "no records")])
        print("Rejected empty input before ingestion")
        return 2

    samples = [sample for _, sample in numbered_samples]
    try:
        parquet_path, catalog_path = build_outputs(project_root, input_path, samples)
    except FileExistsError as exc:
        print(str(exc))
        return 2
    print(f"Validated {len(samples)} record(s): {parquet_path} ; {catalog_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
