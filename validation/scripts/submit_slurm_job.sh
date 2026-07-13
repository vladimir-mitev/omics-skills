#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 || ( $1 != --dry-run && $1 != --submit ) ]]; then
    echo "Usage: $0 (--dry-run|--submit) MANIFEST RENDERED_SCRIPT" >&2
    exit 2
fi

mode=$1
manifest=$(realpath "$2")
rendered=$(realpath -m "$3")
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
rendered_dir=$(dirname "$rendered")
mkdir -p "$rendered_dir"
candidate_dir=$(mktemp -d "$rendered_dir/.validation-render.XXXXXX")
candidate="$candidate_dir/job.sbatch"
trap 'rm -rf "$candidate_dir"' EXIT

uv run --script "$script_dir/render_slurm_job.py" "$manifest" --output "$candidate" >/dev/null
if [[ -e $rendered ]]; then
    cmp -s "$candidate" "$rendered" || {
        echo "Existing rendered job differs from the current manifest: $rendered" >&2
        exit 1
    }
else
    mv "$candidate" "$rendered"
fi
echo "Rendered: $rendered"

if [[ $mode == --dry-run ]]; then
    exit 0
fi

: "${OMICS_VALIDATION_SUBMIT_APPROVED:?Set OMICS_VALIDATION_SUBMIT_APPROVED=1 only after the exact rendered job is approved}"
[[ $OMICS_VALIDATION_SUBMIT_APPROVED == 1 ]] || { echo "OMICS_VALIDATION_SUBMIT_APPROVED must equal 1" >&2; exit 2; }
command -v sbatch >/dev/null || { echo "sbatch is unavailable on this host" >&2; exit 127; }
exec sbatch --parsable "$rendered"
