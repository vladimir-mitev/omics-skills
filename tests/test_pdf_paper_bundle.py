import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills" / "pdf-to-md"
POPULATE = SKILL / "scripts" / "populate_article_json.py"
VALIDATE = SKILL / "scripts" / "validate_article_json.py"


def populate(source, tmp_path):
    markdown = tmp_path / source.name
    shutil.copyfile(source, markdown)
    result = subprocess.run([sys.executable, str(POPULATE), str(markdown)], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    return markdown.with_suffix(".article.json"), markdown.with_suffix(".section_audit.json")


def test_complete_paper_bundle_audits_sections_figures_and_article(tmp_path):
    article, audit = populate(SKILL / "fixtures" / "paper.md", tmp_path)
    populated = json.loads(article.read_text())
    populated["figure_interpretation"] = "Not assessed by the text-only fixture; review the source pages."
    article.write_text(json.dumps(populated, indent=2) + "\n")
    result = subprocess.run([sys.executable, str(VALIDATE), str(article), "--scientific-paper", "--section-audit", str(audit)], text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(article.read_text())
    section_data = json.loads(audit.read_text())
    assert data["title"] == "A fixture study of reproducible extraction"
    assert data["methods"] and data["references"]
    assert data["figure_legends"] == ["Figure 1. Deterministic paper-bundle test. The panel represents the complete local evidence path."]
    assert section_data["field_audit"]["figure_legends"]["count"] == 1


def test_missing_authors_are_not_fabricated_and_fail_paper_validation(tmp_path):
    article, audit = populate(SKILL / "fixtures" / "paper-missing-authors.md", tmp_path)
    assert json.loads(article.read_text())["authors"] == ""
    result = subprocess.run([sys.executable, str(VALIDATE), str(article), "--scientific-paper", "--section-audit", str(audit)], text=True, capture_output=True)
    assert result.returncode == 1
    assert "authors is empty" in result.stdout
