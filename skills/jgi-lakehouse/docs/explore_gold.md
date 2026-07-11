# How to Explore GOLD Database

**Last verified:** 2026-05-30
**Tool version/release checked:** GOLD Release v.10 public site; JGI Lakehouse live service (not versioned); local exploration script has no upstream release.
**Official docs/manual:** https://gold.jgi.doe.gov/index ; https://gold.jgi.doe.gov/resources/project_help_doc.pdf ; https://docs.dremio.com/current/reference/api/sql/
**Release/source:** `"gold-db-2 postgresql".gold.*`; `skills/jgi-lakehouse/scripts/explore_gold_database.sh`.

## Current Limitation

Current off-network workstations may not be able to access the internal Dremio API directly. On 2026-05-30, direct access from this workspace failed with "No route to host" for `lakehouse-1.jgi.lbl.gov:9047`, while the public HTTPS endpoint remains behind Cloudflare Access:
- Port 9047 is blocked/firewalled
- Public HTTPS endpoint has Cloudflare Access protection

## Run from an LBNL compute allocation

Use a scheduler allocation with Lakehouse network access. Do not run the scan on a
login node.

### Step 1: Confirm the installed skill and token

```bash
test -x ~/.agents/skills/jgi-lakehouse/scripts/explore_gold_database.sh
test -s ~/.secrets/dremio_pat || \
  ~/.agents/skills/jgi-lakehouse/scripts/get_dremio_token.sh
```

### Step 2: SSH to the LBNL login host

```bash
ssh <lbnl-server>
```

### Step 3: Submit the exploration

```bash
# Select the site's small-job account and partition. Avoid Dori high-memory nodes.
export SLURM_ACCOUNT=<small-job-account>
export SLURM_PARTITION=<small-job-partition>
sbatch -A "$SLURM_ACCOUNT" -p "$SLURM_PARTITION" \
  --time=00:10:00 --cpus-per-task=1 --mem=2G \
  --output=gold_exploration_results.txt \
  --wrap='bash ~/.agents/skills/jgi-lakehouse/scripts/explore_gold_database.sh'
```

## What the Script Does

The script will:

1. **List all available schemas** in the lakehouse
2. **Find the GOLD database** (or similar)
3. **List all tables** in GOLD
4. **For the first three tables**, show:
   - Column names and data types
   - Row count
   - Sample data (first 2 rows)

## Alternative: Manual Exploration

Use the verified HTTPS client for manual queries:

```bash
export DREMIO_PAT=$(<~/.secrets/dremio_pat)
uv run --with requests python - <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".agents/skills/jgi-lakehouse/scripts"))
from rest_client import query

for sql in (
    "SHOW SCHEMAS",
    "SHOW TABLES IN GOLD",
    "DESCRIBE GOLD.PROJECT",
    "SELECT * FROM GOLD.PROJECT LIMIT 5",
):
    print(sql)
    print(query(sql))
PY
```

## Expected Output

You should see something like:

```
════════════════════════════════════════════════════════════════
JGI GOLD Database Explorer
════════════════════════════════════════════════════════════════

1. Listing all available schemas...
────────────────────────────────────────────────────────────────
Found 15 schemas:
  - GOLD
  - Phytozome
  - Mycocosm
  - JDP
  - IMG
  ...

GOLD schema found

2. Listing tables in GOLD schema...
────────────────────────────────────────────────────────────────
Found 12 tables in GOLD:
  - PROJECT
  - BIOSAMPLE
  - ORGANISM
  - SEQUENCING_PROJECT
  - ANALYSIS_PROJECT
  ...

3. Exploring GOLD tables...
────────────────────────────────────────────────────────────────

Table: GOLD.PROJECT
  ──────────────────────────────────────────────────────────
  Columns: 25
    - PROJECT_ID: VARCHAR
    - PROJECT_NAME: VARCHAR
    - ORGANISM_NAME: VARCHAR
    - ECOSYSTEM: VARCHAR
    - HABITAT: VARCHAR
    ...
  Row count: 125,431
  Sample data (2 rows):
    Row 1:
      PROJECT_ID: Gp0123456
      PROJECT_NAME: Marine metagenome sequencing
      ORGANISM_NAME: Marine microbial communities
      ...
```

## Common GOLD Tables

Based on typical GOLD structure, you might find:

- **PROJECT** - Research projects
- **BIOSAMPLE** - Biological samples
- **ORGANISM** - Organism information
- **SEQUENCING_PROJECT** - Sequencing efforts
- **ANALYSIS_PROJECT** - Analysis workflows
- **STUDY** - Study metadata

## Saving Results

To save the results for later analysis:

```bash
# Run and save
bash ~/explore_gold_database.sh > ~/gold_data_catalog.txt 2>&1

# Copy back to your workstation
# From your workstation:
scp <lbnl-server>:~/gold_data_catalog.txt ~/

# Then analyze locally
cat ~/gold_data_catalog.txt
```

## Troubleshooting

**Error: "No route to host"**
: Use a compute allocation with LBNL network access.

**Error: "Unauthorized" or "401"**
: The token may be expired. Generate a new token with the helper.

**Error: "GOLD schema not found"**
: Check the schema list for variations such as `Gold` or `gold`.

**No output**
: Check that `uv` is available in the scheduler allocation.

## Next Steps

After exploring the GOLD database:

1. **Identify tables of interest** for your analysis
2. **Document the schema** for the tables you need
3. **Create queries** to extract specific data
4. **Consider setting up** an SSH tunnel or scheduled exports if you need regular access

---

**Script Location**: `scripts/explore_gold_database.sh`
**Token**: Stored in `~/.secrets/dremio_pat` (30 hour lifetime)
