---
name: bio-foundation-housekeeping
description: Add schema-backed metadata validation, normalized Parquet tables, and a DuckDB catalog to a bioinformatics project. Use when an analysis needs LinkML/Pydantic records or a queryable data catalog.
---

# Bio Foundation Housekeeping

Add validated metadata models and a queryable catalog to an existing bioinformatics project. This is an independent entry point when the layout already exists; if it does not, complete `bioinformatics-project` as a separate setup task.

## Instructions

1. Confirm `bioinformatics-project` has established input/output boundaries, project records, and a pinned environment. Do not create a competing project layout.
2. Add LinkML schemas for the sample, run, file, result, and provenance records the project actually needs.
3. Generate or hand-write Pydantic models from the LinkML schema. Put fields referenced by field validators before the validated field, or use a model validator when order should not matter.
4. Validate and normalize raw records through LinkML/Pydantic before writing Parquet. Reject unexpected fields unless the schema explicitly permits them.
5. Register validated Parquet tables in DuckDB. Keep raw CSV, TSV, JSON, and YAML as immutable inputs or clearly marked staging tables that downstream queries cannot mistake for normalized data.
6. Add a fixture that proves one valid record loads and representative invalid records fail before catalog ingestion.
7. Start from `scripts/build_sample_catalog.py` and the bundled JSONL fixtures when implementing a project-specific record model. Keep validation ahead of every Parquet or DuckDB write.

## Quick Reference

| Task | Action |
|------|--------|
| Project structure is missing | Stop catalog work and run `bioinformatics-project` as a separate setup task. |
| Define records | Author LinkML schemas and generate or maintain Pydantic models. |
| Normalize metadata | Adapt and run `scripts/build_sample_catalog.py` through `uv run --script`. |
| Build catalog | Register validated Parquet only, then run integrity queries. |
| Tool docs | See `docs/README.md`. |

## Input Requirements

Prerequisites:
- Tools declared in the project's pinned Pixi environment. See `docs/README.md` for expected tools.
- Target project root is writable.
Inputs:
- A project root already organized by `bioinformatics-project`.
- Representative valid and invalid metadata records.
- Required identifiers, fields, types, enumerations, and cross-record constraints.

## Output

- schemas/
- data/catalog.duckdb
- data/normalized/*.parquet validated against schemas/
- tests/metadata/ fixtures and validation checks
- results/bio-foundation-housekeeping/report.md
- results/bio-foundation-housekeeping/logs/

## Quality Gates

- [ ] Schema generation succeeds and models are importable.
- [ ] Raw metadata validates against LinkML and Pydantic before DuckDB ingestion.
- [ ] The existing `pixi.lock` includes the schema/catalog dependencies.
- [ ] DuckDB catalog is readable and points at validated Parquet tables.
- [ ] Invalid fixtures fail before Parquet or DuckDB ingestion.
- [ ] On failure: record the rejected record and validation error without exposing private values, then exit non-zero.
- [ ] Verify project root exists and is writable.
- [ ] Validate generated schemas against expected fields.
- [ ] The valid fixture produces non-empty Parquet and DuckDB files; the invalid fixture exits non-zero with neither artifact present.

## Examples

### Example 1: Expected input layout

```text
project root: ./coastal-metagenomes
records: sample, sequencing_run, file, provenance
identifiers: sample_id and run_id
normalized output: data/normalized/
```

### Example 2: Exercise the validation boundary

```bash
SKILL_ROOT=~/.agents/skills/bio-foundation-housekeeping

uv run --script "$SKILL_ROOT/scripts/build_sample_catalog.py" \
  --input "$SKILL_ROOT/fixtures/valid-samples.jsonl" \
  --project-root ./coastal-metagenomes
```

Adapt the Pydantic model and fixture fields to the project schema before using the helper with study metadata. The bundled invalid fixture demonstrates that malformed dates, invalid ranges, empty required fields, and unexpected keys fail before ingestion.

## Troubleshooting

**Issue**: Missing inputs or reference databases
**Solution**: Verify paths and permissions before running the workflow.

**Issue**: A Pydantic field validator cannot see another field
**Solution**: Pydantic validates fields in declaration order. Declare the dependency first or move the cross-field rule to `@model_validator(mode="after")`.

**Issue**: A constructed model is accepted without validation
**Solution**: Do not use `model_construct()` for external input. Parse raw records with `model_validate()`, or configure `revalidate_instances="always"` when existing model instances must be checked again.
