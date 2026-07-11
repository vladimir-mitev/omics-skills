# Arrow Flight (Python)

**Last verified:** 2026-05-30
**Tool version/release checked:** `dremio_flight` wheel v1.1.0; Dremio documentation current [26.x].
**Official docs/manual:** https://docs.dremio.com/current/developer/python/ ; https://docs.dremio.com/current/developer/arrow-flight/
**Release/source:** https://github.com/dremio-hub/arrow-flight-client-examples ; https://github.com/dremio-hub/arrow-flight-client-examples/releases/download/dremio-flight-python-v1.1.0/dremio_flight-1.1.0-py3-none-any.whl

This guide documents the JGI Lakehouse Arrow Flight Python setup described by Georg Rath (Nov 26, 2025), and a local connectivity pattern. Re-run the `SELECT 1` check in the target network environment before production use.

## Purpose

Use Arrow Flight for fast programmatic query access to Dremio/Lakehouse when you want lower-overhead retrieval than REST.

## Prerequisites

- Network access to `lakehouse-1.jgi.lbl.gov`
- Valid lakehouse credentials
- `uv`

## Quick Start (Username/Password)

Create `example.py`:

```python
import logging
import os
from dremio.flight.connection import DremioFlightEndpointConnection

logging.basicConfig(level=logging.INFO)

conn = DremioFlightEndpointConnection({
    "hostname": "lakehouse-1.jgi.lbl.gov",
    "username": os.environ["DREMIO_USERNAME"],
    "password": os.environ["DREMIO_PASSWORD"],
})
df = conn.query("SELECT 1")
print(df)
```

Run:

```bash
read -r -p "Dremio username: " DREMIO_USERNAME
read -r -s -p "Dremio password: " DREMIO_PASSWORD
printf '\n'
export DREMIO_USERNAME DREMIO_PASSWORD
uv run \
  --with "dremio-flight @ https://github.com/dremio-hub/arrow-flight-client-examples/releases/download/dremio-flight-python-v1.1.0/dremio_flight-1.1.0-py3-none-any.whl" \
  example.py
unset DREMIO_USERNAME DREMIO_PASSWORD
```

Expected output shape:

```text
INFO:root:Authentication was successful
INFO:root:GetFlightInfo was successful
   EXPR$0
0       1
```

## PAT/Token Note

If your environment uses Personal Access Tokens (`DREMIO_PAT`) for REST, keep in mind this example is username/password-based. If token auth is required for Flight in your deployment, adapt connection parameters according to the installed package API.

## Operational Notes

- Default Flight port in this package flow is `32010` unless overridden.
- Keep credentials out of files and git. Read them interactively or load them from the approved secret store.
- Prefer short-lived or scoped credentials where possible.

## References

- Arrow Flight client examples: https://github.com/dremio-hub/arrow-flight-client-examples
- Dremio Arrow Flight docs: https://docs.dremio.com/current/developer/arrow-flight/
