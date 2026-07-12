import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills" / "beautiful-data-viz"
EXPORT = SKILL / "scripts" / "export_fixture.py"


def test_fixture_exports_png_svg_and_pdf(tmp_path):
    target = tmp_path / "growth"
    result = subprocess.run(["uv", "run", "--script", str(EXPORT), str(SKILL / "fixtures" / "growth_curve.csv"), "--out", str(target), "--background", "dark"], text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    for suffix in ("png", "svg", "pdf"):
        path = target.with_suffix(f".{suffix}")
        assert path.is_file() and path.stat().st_size > 100
    metadata = json.loads(target.with_suffix(".json").read_text())
    assert metadata["annotation_colors"]
    assert set(metadata["annotation_colors"]) == {metadata["text_color"]}
