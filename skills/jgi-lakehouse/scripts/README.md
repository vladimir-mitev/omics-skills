# Lakehouse helper scripts

Run these helpers from an LBNL-connected host or through an approved tunnel. All
REST calls use `https://lakehouse-1.jgi.lbl.gov:9047`; certificate verification
remains enabled.

## Authentication

`get_dremio_token.sh` reads the username and password from an interactive prompt.
It never accepts credentials as command-line arguments or prints the token. The
default output is `~/.secrets/dremio_pat`.

```bash
./get_dremio_token.sh

# Choose a different token file when needed.
./get_dremio_token.sh --output ~/.secrets/jgi/dremio_pat
```

The helper creates the token file atomically with mode `0600`. Set
`DREMIO_CA_BUNDLE` to the JGI CA file if the internal endpoint is not covered by
the system trust store.

Load an existing token before using the clients:

```bash
export DREMIO_PAT=$(<~/.secrets/dremio_pat)
```

## REST client

`rest_client.py` declares `requests` in PEP 723 metadata, so `uv` creates the
required environment:

```bash
uv run scripts/rest_client.py
```

For a custom query from the skill directory:

```bash
uv run --with requests python - <<'PY'
import sys

sys.path.insert(0, "scripts")
from rest_client import query

rows = query("SELECT * FROM GOLD.PROJECT LIMIT 10")
print(f"rows: {len(rows)}")
PY
```

The client reads `DREMIO_PAT` when each request starts. Its relevant settings are:

| Variable | Meaning | Default |
|---|---|---|
| `DREMIO_HOST` | Dremio host | `lakehouse-1.jgi.lbl.gov` |
| `DREMIO_PORT` | HTTPS port | `9047` |
| `DREMIO_REQUEST_TIMEOUT` | Timeout for one HTTP request | `60` seconds |
| `REQUESTS_CA_BUNDLE` | CA bundle used by Requests | System trust store |

`query()` and `query_all()` also enforce an overall polling timeout, which defaults
to 300 seconds and can be changed with their `timeout` argument.

## GOLD explorer

`explore_gold_database.sh` loads the token from the environment or the default
token file and runs the PEP 723-enabled Python explorer.

```bash
bash scripts/explore_gold_database.sh > gold_catalog.txt
```

Submit catalog scans through the site's small-job scheduler allocation. Do not run
them on a login node.

## IMG genome downloader

`download_img_genomes.py` queries metadata, locates IMG packages on the JGI
filesystem, checks archive members, and copies selected files.

```bash
uv run scripts/download_img_genomes.py \
  --domain Bacteria \
  --count 5 \
  --output-dir ./genomes
```

Run multi-genome copy and extraction work in a scheduler allocation. The helper
uses these settings in addition to the REST variables above:

| Variable | Meaning | Default |
|---|---|---|
| `DREMIO_JOB_TIMEOUT` | Whole metadata-query polling deadline | `300` seconds |
| `IMG_DOWNLOAD_DIR` | IMG package root | `/clusterfs/jgi/img_merfs-ro/img_web/img_web_data/download` |
| `IMG_DATA_DIR` | Per-taxon IMG data root | `/clusterfs/jgi/img_merfs-ro/img_web_data_merfs` |

The directory fallback reports failure unless it copies at least one expected
file. A completed process therefore does not imply that an output package exists;
check the returned metadata and output files.

## Troubleshooting

`No route to host`
: Run from the LBNL network or use an approved SSH tunnel.

`401` or `Unauthorized`
: Generate a new token and reload `DREMIO_PAT`.

`SSLCertVerificationError`
: Set `REQUESTS_CA_BUNDLE` for Python helpers or `DREMIO_CA_BUNDLE` for the token
  helper to the JGI CA file. Do not disable certificate verification.

`ModuleNotFoundError: requests`
: Start the helper with `uv run`; the Python scripts declare their dependencies.
