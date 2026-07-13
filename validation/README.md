# Biological validation assets

See [Biological Validation Reference](../docs/biological-validation.md) for the evidence levels, truth-set registry, Slurm contract, and run-evidence format.

Run the local contract checks with:

```bash
uv run --script validation/scripts/validate_registry.py
uv run --no-project --with pytest --with requests pytest -q tests/test_biological_validation.py
```
