# JGI Lakehouse Skill

Query and explore the JGI Lakehouse (Dremio + Apache Iceberg) using safe SQL patterns.

## Quick Start

### 1. Setup Authentication

```bash
# Generate token from LBNL server (one-time)
ssh <lbnl-server>
cd ~/.agents/skills/jgi-lakehouse/scripts
./get_dremio_token.sh

# Auto-load token
echo 'export DREMIO_PAT=$(cat ~/.secrets/dremio_pat 2>/dev/null)' >> ~/.bashrc
source ~/.bashrc
```

See `docs/authentication.md` for details.

### 2. Explore Databases

```bash
# List all schemas
uv run examples/explore_database.py

# Explore GOLD database
uv run examples/explore_database.py GOLD

# Inside a small-job scheduler allocation on the LBNL network
bash scripts/explore_gold_database.sh > catalog.txt
```

### 3. Query Data

```bash
uv run --with requests python - <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".agents/skills/jgi-lakehouse/scripts"))

from rest_client import query

# Simple query
results = query("SELECT * FROM GOLD.PROJECT LIMIT 10")

# With context
results = query(
    "SELECT * FROM genomics LIMIT 10",
    context=["Phytozome"]
)
print(f"rows: {len(results)}")
PY
```

### 4. Optional: Arrow Flight (Python)

```bash
uv run \
  --with "dremio-flight @ https://github.com/dremio-hub/arrow-flight-client-examples/releases/download/dremio-flight-python-v1.1.0/dremio_flight-1.1.0-py3-none-any.whl" \
  --with pyyaml \
  example.py
```

See `docs/arrow-flight-python.md` for the connection example and test query.

### 5. Link an IMG assembly to reads

Use this sequence for JGI metagenomes:

1. Start from the assembly taxon OID:

```bash
/clusterfs/jgi/img_merfs-ro/img_web_data_merfs/{taxon_oid}/assembled/
```

2. Pull linkage fields from Lakehouse metadata:

- `img_jgi_project_id`
- `sequencing_gold_id`
- `sample_gold_id`
- `study_gold_id`
- `gold_project_id`
- `gold_pmo_project_id`
- `gold_its_spid`

3. Query JAMO, preferring `pmoid`:

```bash
apptainer run docker://doejgi/jamo-dori:latest jamo info all pmoid <img_jgi_project_id>
```

4. If needed, also try direct taxon lookup:

```bash
apptainer run docker://doejgi/jamo-dori:latest \
  jamo info all custom '{"metadata.gold_data.img_oid": 3300000030, "file_name": {"$regex": ".*fastq(\\\\.gz)?$"}}'
```

5. Only treat `spid` as a fallback, not the primary key:

```bash
apptainer run docker://doejgi/jamo-dori:latest jamo info raw_normal spid <gold_its_spid>
```

6. Fetch a selected file:

```bash
apptainer run docker://doejgi/jamo-dori:latest \
  jamo fetch -s dori all filename <file_name>
```

7. Inspect one record in detail:

```bash
apptainer run docker://doejgi/jamo-dori:latest jamo show <metadata_id>
```

Important restore note:

- `jamo fetch` may return a staged scratch path even when the underlying file was `PURGED`
- in that case, wait until the staged file exists and has non-zero size before starting downstream work
- only treat the file as ready once the staged path is actually restored

## File Structure

```
.
├── SKILL.md                        # Skill definition
├── README.md                       # This file
│
├── scripts/
│   ├── get_dremio_token.sh        # Token generation
│   ├── rest_client.py             # REST API client
│   ├── explore_gold_database.sh   # GOLD exploration (bash)
│   └── README.md                  # Scripts documentation
│
├── examples/
│   └── explore_database.py        # Interactive database explorer
│
├── docs/
│   ├── authentication.md          # Token setup
│   ├── arrow-flight-python.md     # Arrow Flight Python access
│   └── explore_gold.md            # GOLD exploration guide
│
└── references/
    ├── tools.json                 # Tool definitions
    └── ...                        # Additional references
```

## Network Requirements

**Public HTTPS Endpoint** (`https://lakehouse.jgi.lbl.gov`)
- Protected by Cloudflare Access and requires browser authentication

**Internal HTTPS Endpoint** (`https://lakehouse-1.jgi.lbl.gov:9047`)
- Direct API access with a token
- Accessible from the LBNL network; certificate verification stays enabled

## Available Databases

- **GOLD** - Genomes OnLine Database
- **Phytozome** - Plant genomics
- **Mycocosm** - Fungal genomics
- **IMG** - Integrated Microbial Genomes
- **JDP** - JGI Data Portal

## Operational Rules

1. Prefer VDS (views) over physical tables
2. Never run SELECT * without LIMIT (default: 100)
3. Always inspect schema before complex joins
4. Check reflections if performance issues arise
5. Use Iceberg time travel for historical queries

Additional practical rules:
- For function IDs in `gene_ko_terms`, include `KO:` prefix (example: `KO:K00025`).
- For isolate benchmark counts, include `obsolete_flag = 'No'`.
- If `IMG.gene_feature` view expansion fails, query `img_core_v400` tables directly.
- For NUMG domain+sequence joins, use both `oid` and `gene_oid` keys.

## Documentation

- **Setup**: `docs/setup_guide.md`
- **Authentication**: `docs/authentication.md`
- **Arrow Flight (Python)**: `docs/arrow-flight-python.md`
- **NUMG Workflow Example**: `examples/05-query-numg-metagenome-proteins.md`
- **GOLD Database**: `docs/explore_gold.md`
- **API Reference**: https://docs.dremio.com/current/reference/api/

## Examples

### List Schemas
```python
from rest_client import show_schemas
schemas = show_schemas(limit=2000)
```

### Query with Time Travel
```sql
SELECT * FROM GOLD.PROJECT
AT TIMESTAMP '2026-01-20 12:00:00'
LIMIT 10
```

### Describe Table
```python
from rest_client import query
schema = query("DESCRIBE GOLD.PROJECT")
```

## Token Management

- **Lifetime**: 30 hours
- **Storage**: `~/.secrets/dremio_pat` (gitignored)
- **Refresh**: Re-run `get_dremio_token.sh` from LBNL server

## Troubleshooting

**"No route to host"**
: Port 9047 is blocked. Run from the LBNL network or use an approved tunnel that
  preserves HTTPS hostname verification.

**"HTTP 302 redirect"**
→ Cloudflare Access blocking. Use internal endpoint.

**"Token expired"**
→ Regenerate token (30 hour lifetime).

## Support

- **Skill docs**: `SKILL.md`
- **Dremio API**: https://docs.dremio.com/
- **Admin contact**: Georg Rath (JGI Slack)
