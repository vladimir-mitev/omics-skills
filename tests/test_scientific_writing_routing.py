from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "scientific-writing"
AGENT = REPO_ROOT / "agents" / "science-writer.md"


class ScientificWritingRoutingTests(unittest.TestCase):
    def test_supporting_skill_names_are_installed_names(self) -> None:
        text = (SKILL_ROOT / "references" / "supporting-skills.md").read_text(encoding="utf-8")
        names = set(re.findall(r"`([a-z][a-z0-9-]+)`", text))
        expected = {
            "crossref-lookup",
            "scientific-impact-assessment",
            "polars-dovmed",
            "arxiv-search",
            "biorxiv-search",
            "manuscript-review-council",
            "proposal-review",
            "bio-workflow-methods-docwriter",
            "bio-logic",
        }
        self.assertTrue(expected <= names)
        for name in expected:
            self.assertTrue((REPO_ROOT / "skills" / name / "SKILL.md").is_file(), name)

    def test_agent_has_no_bare_write_trigger(self) -> None:
        text = AGENT.read_text(encoding="utf-8")
        pattern_lines = [line for line in text.splitlines() if line.startswith("- **")]
        self.assertFalse(any(re.search(r'(^|, )"write"(,|\*\*)', line) for line in pattern_lines))
        self.assertIn('"critique manuscript"', text)
        self.assertIn('"rewrite scientific prose"', text)


if __name__ == "__main__":
    unittest.main()
