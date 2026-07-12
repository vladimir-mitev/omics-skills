#!/usr/bin/env bash
#SBATCH --job-name=nextflow-launch
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=24:00:00

set -euo pipefail
: "${NXF_PIPELINE:?Missing NXF_PIPELINE}"
: "${NXF_READS:?Missing NXF_READS}"
: "${NXF_RESULTS:?Missing NXF_RESULTS}"

mkdir -p "$NXF_RESULTS" "$NXF_RESULTS/run-metadata"
nextflow run "$NXF_PIPELINE" \
    -profile slurm \
    -resume \
    --reads "$NXF_READS" \
    --outdir "$NXF_RESULTS" \
    -with-trace "$NXF_RESULTS/run-metadata/trace.tsv" \
    -with-report "$NXF_RESULTS/run-metadata/report.html" \
    -with-timeline "$NXF_RESULTS/run-metadata/timeline.html"

test -s "$NXF_RESULTS/run-metadata/trace.tsv"
find "$NXF_RESULTS" -type f -size +0c ! -path '*/run-metadata/*' -print -quit | grep -q .
