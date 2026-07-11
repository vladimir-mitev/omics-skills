#!/usr/bin/env python3
"""Validate every skills/<name>/SKILL.md: frontmatter name matches the
directory, name is a valid slug, required sections are present, and the file
stays within the length budget.

Importable (validate_skill / validate_all) so the checks are unit-testable, and
runnable as a CLI for CI and the install smoke test."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skill_index  # noqa: E402  (reuse the single frontmatter parser)

REQUIRED_SECTIONS = [
    "## Instructions",
    "## Quick Reference",
    "## Input Requirements",
    "## Output",
    "## Quality Gates",
    "## Examples",
    "## Troubleshooting",
]
MAX_LINES = 500
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 400
MAX_TOTAL_DESCRIPTION_LENGTH = 6500
SLUG_PATTERN = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
TRIGGER_PATTERN = re.compile(r"\b(?:use when|use for|trigger when)\b", re.IGNORECASE)
MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def local_link_targets(text: str) -> list[str]:
    """Return relative Markdown link targets that should exist on disk."""
    targets: list[str] = []
    for raw_target in MARKDOWN_LINK_PATTERN.findall(text):
        target = raw_target.strip()
        if target.startswith("<") and ">" in target:
            target = target[1 : target.index(">")]
        else:
            target = target.split(maxsplit=1)[0]
        target = unquote(target).split("#", 1)[0]
        if not target or target.startswith(("#", "/", "http://", "https://", "mailto:", "data:")):
            continue
        targets.append(target)
    return targets


def validate_skill(skill_dir: Path) -> list[str]:
    """Return a list of human-readable validation errors for one skill dir."""
    name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [f"{name}: missing SKILL.md"]

    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return [f"{name}: missing frontmatter"]

    errors: list[str] = []
    frontmatter, _ = skill_index.split_frontmatter(text)
    fm_name = (frontmatter.get("name") or "").strip()
    if fm_name != name:
        errors.append(f"{name}: frontmatter name mismatch ({fm_name})")
    if not SLUG_PATTERN.fullmatch(fm_name):
        errors.append(f"{name}: frontmatter name invalid ({fm_name})")
    if len(fm_name) > MAX_NAME_LENGTH:
        errors.append(f"{name}: frontmatter name too long ({len(fm_name)})")
    description = (frontmatter.get("description") or "").strip()
    if not description:
        errors.append(f"{name}: missing frontmatter description")
    elif len(description) > MAX_DESCRIPTION_LENGTH:
        errors.append(
            f"{name}: frontmatter description over {MAX_DESCRIPTION_LENGTH} characters "
            f"({len(description)})"
        )
    elif not TRIGGER_PATTERN.search(description):
        errors.append(f"{name}: frontmatter description must say when to use the skill")
    missing = [section for section in REQUIRED_SECTIONS if section not in text]
    if missing:
        errors.append(f"{name}: missing sections {missing}")
    line_count = len(text.splitlines())
    if line_count > MAX_LINES:
        errors.append(f"{name}: SKILL.md over {MAX_LINES} lines ({line_count})")
    for target in local_link_targets(text):
        if not (skill_md.parent / target).resolve().exists():
            errors.append(f"{name}: broken local Markdown link ({target})")
    return errors


def validate_all(skills_dir: Path) -> list[str]:
    """Validate every skill directory under ``skills_dir``."""
    errors: list[str] = []
    total_description_length = 0
    for entry in sorted(skills_dir.iterdir()):
        if entry.is_dir():
            errors.extend(validate_skill(entry))
            skill_md = entry / "SKILL.md"
            if skill_md.exists():
                frontmatter, _ = skill_index.split_frontmatter(
                    skill_md.read_text(encoding="utf-8")
                )
                total_description_length += len(
                    (frontmatter.get("description") or "").strip()
                )
    if total_description_length > MAX_TOTAL_DESCRIPTION_LENGTH:
        errors.append(
            "skill descriptions exceed the repository discovery budget "
            f"({total_description_length}/{MAX_TOTAL_DESCRIPTION_LENGTH} characters)"
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    skills_dir = Path(__file__).resolve().parent.parent / "skills"
    errors = validate_all(skills_dir)
    if errors:
        print("Skill validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Skill validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
