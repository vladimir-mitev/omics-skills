---
name: bio-prefect-dask-nextflow
description: Design reproducible bioinformatics pipelines with Prefect plus Dask or Nextflow. Use when scaffolding local, distributed, or scheduler-backed workflows.
---

# Bio Prefect + Dask + Nextflow

Choose and scaffold the right workflow engine for local, distributed, or HPC bioinformatics pipelines.

Supplementary docs last verified: 2026-05-30. Current source checks cover Prefect 3.7.2, Dask/distributed 2026.3.0, prefect-dask v0.2.6 (archived repository; install through `prefect[dask]`), and Nextflow v26.04.3.

## Instructions

1. Collect requirements (scheduler, container policy, data location, scale).
2. Choose engine: Prefect+Dask, Nextflow, or Hybrid.
3. Generate a runnable scaffold with clear data layout and resources.
4. Validate with a small test and resume/retry checks.

## Quick Reference

| Task | Action |
|------|--------|
| Engine choice | See `decision-matrix.md` |
| Prefect+Dask scaffold | See `prefect-dask.md` |
| Prefect on Slurm | See `prefect-hpc-slurm.md` |
| Nextflow on HPC | See `nextflow-hpc.md` |
| Submit Nextflow through Slurm | `SLURM_ACCOUNT=... scripts/submit_nextflow.sh main.nf 'data/*.fastq.gz' results` |
| Examples | See `examples.md` |

## Input Requirements

- Workflow requirements and steps
- Target environment (local, cluster, cloud)
- Scheduler and container constraints
- Data locations and expected volumes

## Output

- Engine recommendation with rationale
- Runnable scaffold (files + commands)
- Resource plan per step
- Validation plan and checkpoints

## Quality Gates

- [ ] Tiny test run completes end-to-end
- [ ] Resume/retry behavior verified
- [ ] Resource plan matches cluster limits
- [ ] Temporary Dask clusters are created by the task runner at flow runtime and closed with the flow
- [ ] Compound FASTQ suffixes do not leak into sample output names
- [ ] Nextflow launch runs through `sbatch` and verifies trace and non-empty result artifacts

## Examples

### Example 1: Engine recommendation

```text
Choice: Nextflow
Why: CLI-heavy pipeline, HPC scheduler required, reproducible cache/resume needed.
```

## Troubleshooting

**Issue**: Workflow fails on HPC due to environment mismatch
**Solution**: Pin container/conda versions and validate with a minimal test dataset.
