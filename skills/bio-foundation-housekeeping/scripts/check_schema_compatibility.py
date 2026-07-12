#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3"]
# ///
"""Report breaking and compatible changes in a LinkML project-schema extension."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

CONSTRAINTS = ("range", "required", "identifier", "multivalued", "pattern", "minimum_value", "maximum_value")


def load(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("classes"), dict):
        raise ValueError(f"{path}: LinkML schema must contain a classes mapping")
    return value


def compare(base: dict, extension: dict) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    base_classes = base["classes"]
    for class_name, class_spec in extension["classes"].items():
        if class_name not in base_classes:
            changes.append({"location": f"classes.{class_name}", "compatibility": "compatible", "change": "class_added"})
            continue
        old_slots = base_classes[class_name].get("attributes", {})
        for slot_name, new_slot in class_spec.get("attributes", {}).items():
            location = f"classes.{class_name}.attributes.{slot_name}"
            if slot_name not in old_slots:
                compatibility = "breaking" if new_slot.get("required", False) else "compatible"
                changes.append({"location": location, "compatibility": compatibility, "change": "required_slot_added" if compatibility == "breaking" else "optional_slot_added"})
                continue
            old_slot = old_slots[slot_name]
            for key in CONSTRAINTS:
                old_value = old_slot.get(key, False if key in {"required", "identifier", "multivalued"} else None)
                new_value = new_slot.get(key, old_value)
                if new_value != old_value:
                    changes.append({"location": f"{location}.{key}", "compatibility": "breaking", "change": f"constraint_changed:{old_value!r}->{new_value!r}"})
    return changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--extension", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        changes = compare(load(args.base), load(args.extension))
        payload = {"schema_version": "1.0", "compatible": not any(item["compatibility"] == "breaking" for item in changes), "changes": changes}
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Compatibility: {'compatible' if payload['compatible'] else 'breaking'}")
        return 0 if payload["compatible"] else 2
    except (OSError, ValueError, yaml.YAMLError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
