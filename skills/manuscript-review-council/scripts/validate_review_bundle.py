#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema==4.26.0"]
# ///
"""Validate issue records and deterministic artifact paths for a council review."""

import argparse
import json
from pathlib import Path

import jsonschema


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    schema = json.loads((Path(__file__).parents[1] / "schemas" / "review-bundle.schema.json").read_text())
    bundle = json.loads(args.bundle.read_text())
    try:
        jsonschema.validate(bundle, schema)
    except jsonschema.ValidationError as error:
        parser.error(f"schema validation failed at {'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}")
    root = f"reviews/{bundle['manuscript_slug']}/{bundle['run_id']}"
    expected = {"packet_path": f"{root}/packet.json", "conflicts_path": f"{root}/conflicts.json", "editor_path": f"{root}/editor.json"}
    for field, path in expected.items():
        if bundle[field] != path:
            parser.error(f"{field} must be {path}")
    roles = [report["role"] for report in bundle["reviewer_reports"]]
    if len(roles) != len(set(roles)):
        parser.error("reviewer roles must be unique")
    for report in bundle["reviewer_reports"]:
        expected_path = f"{root}/reviewers/{report['role']}.json"
        if report["path"] != expected_path:
            parser.error(f"reviewer path must be {expected_path}")
    issue_ids = [issue["issue_id"] for issue in bundle["issues"]]
    if len(issue_ids) != len(set(issue_ids)):
        parser.error("issue_id values must be unique")
    print("Review bundle validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
