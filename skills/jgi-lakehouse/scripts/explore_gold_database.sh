#!/usr/bin/env bash
# Run the Python GOLD explorer with its declared uv environment.

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

if [[ -z "${DREMIO_PAT:-}" && -r "${HOME}/.secrets/dremio_pat" ]]; then
  DREMIO_PAT=$(<"${HOME}/.secrets/dremio_pat")
  export DREMIO_PAT
fi
if [[ -z "${DREMIO_PAT:-}" ]]; then
  echo "Error: DREMIO_PAT is not set and ~/.secrets/dremio_pat is unavailable" >&2
  exit 1
fi

exec uv run --script "$SCRIPT_DIR/../examples/explore_database.py" GOLD
