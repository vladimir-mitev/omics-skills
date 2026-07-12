#!/usr/bin/env bash
#SBATCH --job-name=taxonomy-route
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=24:00:00

set -euo pipefail
: "${TAXONOMY_TOOL:?Missing TAXONOMY_TOOL}"
: "${TAXONOMY_INPUT:?Missing TAXONOMY_INPUT}"
: "${TAXONOMY_OUTPUT:?Missing TAXONOMY_OUTPUT}"
mkdir -p "$TAXONOMY_OUTPUT"

case "$TAXONOMY_TOOL" in
    gtdbtk)
        : "${GTDBTK_DATA_PATH:?Set GTDBTK_DATA_PATH}"
        gtdbtk check_install
        gtdbtk classify_wf --genome_dir "$TAXONOMY_INPUT" --out_dir "$TAXONOMY_OUTPUT" --cpus "${SLURM_CPUS_PER_TASK:-16}" -x fa
        ;;
    eukcc)
        : "${EUKCC2_DB:?Set EUKCC2_DB}"
        eukcc folder --db "$EUKCC2_DB" --out "$TAXONOMY_OUTPUT" --threads "${SLURM_CPUS_PER_TASK:-16}" "$TAXONOMY_INPUT"
        ;;
    vcontact3)
        vcontact3 run --nucleotide "$TAXONOMY_INPUT" --output "$TAXONOMY_OUTPUT"
        ;;
    gvclass)
        gvclass "$TAXONOMY_INPUT" -o "$TAXONOMY_OUTPUT" -t "${SLURM_CPUS_PER_TASK:-16}"
        ;;
esac

find "$TAXONOMY_OUTPUT" -type f -size +0c -print -quit | grep -q .
