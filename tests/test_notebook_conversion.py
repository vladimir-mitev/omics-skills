import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills" / "notebooks"
SCRIPT = SKILL / "scripts" / "convert_notebook.py"


def test_marimo_to_jupyter_and_jupyter_to_marimo(tmp_path):
    ipynb = tmp_path / "from_marimo.ipynb"
    result = subprocess.run(["uv", "run", "--script", str(SCRIPT), str(SKILL / "fixtures" / "simple_marimo.py"), "--to", "jupyter", "--out", str(ipynb)], text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(ipynb.read_text())["cells"]

    marimo = tmp_path / "from_jupyter.py"
    result = subprocess.run(["uv", "run", "--script", str(SCRIPT), str(SKILL / "fixtures" / "simple_jupyter.ipynb"), "--to", "marimo", "--out", str(marimo)], text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "marimo.App" in marimo.read_text()


def test_template_has_bounded_dependencies_and_kernel_placeholder():
    pixi = (SKILL / "templates" / "pixi.toml").read_text()
    assert '= "*"' not in pixi
    template = (SKILL / "templates" / "jupyter_kiss_template.py").read_text()
    assert "name: <PIXI_PROJECT_KERNEL>" in template
    assert "name: python" not in template
