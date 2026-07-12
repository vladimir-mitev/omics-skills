from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


class PluginManifestTests(unittest.TestCase):
    def load_json(self, relative_path: str) -> dict[str, object]:
        path = REPO_ROOT / relative_path
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsInstance(payload, dict)
        return payload

    def test_codex_manifest_is_complete_and_version_aligned(self) -> None:
        codex = self.load_json(".codex-plugin/plugin.json")
        claude = self.load_json(".claude-plugin/plugin.json")
        self.assertEqual(codex["name"], "omics-skills")
        self.assertEqual(codex["version"], claude["version"])
        self.assertRegex(str(codex["version"]), SEMVER)
        notes = REPO_ROOT / ".github" / "releases" / f"v{codex['version']}.md"
        self.assertTrue(notes.is_file(), f"missing release notes for {codex['version']}")
        self.assertTrue(
            notes.read_text(encoding="utf-8").startswith(
                f"# omics-skills {codex['version']}\n"
            )
        )
        self.assertEqual(codex["skills"], "./skills/")
        interface = codex["interface"]
        self.assertIsInstance(interface, dict)
        for key in (
            "displayName",
            "shortDescription",
            "longDescription",
            "developerName",
            "category",
            "capabilities",
            "defaultPrompt",
        ):
            self.assertTrue(interface.get(key), f"missing interface.{key}")

    def test_repo_marketplace_points_to_repo_plugin(self) -> None:
        marketplace = self.load_json(".agents/plugins/marketplace.json")
        plugins = marketplace["plugins"]
        self.assertEqual(len(plugins), 1)
        plugin = plugins[0]
        self.assertEqual(plugin["name"], "omics-skills")
        self.assertEqual(plugin["source"], {"source": "local", "path": "./"})
        self.assertEqual(plugin["policy"]["installation"], "AVAILABLE")
        self.assertEqual(plugin["policy"]["authentication"], "ON_INSTALL")

    def test_readme_agent_skill_counts_match_generated_catalog(self) -> None:
        catalog = self.load_json("catalog/catalog.json")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        agents = catalog["agents"]
        self.assertIsInstance(agents, list)
        for agent in agents:
            skill_sections = agent["skill_sections"]
            skill_names = {
                skill_name
                for section_skills in skill_sections.values()
                for skill_name in section_skills
            }
            row_prefix = f"| `{agent['name']}` |"
            matching = [line for line in readme.splitlines() if line.startswith(row_prefix)]
            self.assertEqual(len(matching), 1, f"missing README row for {agent['name']}")
            self.assertTrue(
                matching[0].endswith(f"| {len(skill_names)} |"),
                f"stale README skill count for {agent['name']}",
            )


if __name__ == "__main__":
    unittest.main()
