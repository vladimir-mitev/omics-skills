# Skill Quality

This page records the strongest verified improvement made or still needed for every checked-in skill. It is a maintainer reference, not a claim that every workflow has a complete executable implementation.

## Repository-Wide Findings

The repository has 34 skills. Their frontmatter names match their directories, all required sections are present, and all local Markdown links resolve. Each description states when to use the skill, stays below 400 characters, and fits the repository-wide discovery budget.

The largest remaining gap is executable depth. Several bioinformatics skills choose appropriate tools and define outputs but still need restartable drivers, fixture-backed tests, and persisted artifacts for the hypothesis loop and five comparative axes. Tool documentation should not be treated as proof that an end-to-end workflow exists.

## Per-Skill Priorities

| Skill | Verified in this audit | Next concrete improvement |
|---|---|---|
| `ai-scientist-evaluator` | Fixed script paths and shortened its trigger description. | Validate each review against `evaluation_schema.json`, recompute weighted totals instead of trusting submitted scores, and add a routing case for an AI-generated notebook. |
| `arxiv-search` | Fixed the broken summary call and plain queries misclassified by `ORF`, punctuation, or parentheses; added offline tests. | Add cache expiry for recent searches and a cross-process pacing lock. Extend routing cases to physics, CS, and direct arXiv IDs. |
| `beautiful-data-viz` | Made helper imports independent of the current working directory. | Make annotation helpers inherit dark-theme colors, declare a pinned plotting environment, and add one fixture that exports PNG, SVG, and PDF. |
| `bio-annotation` | Replaced login-node computation with a debug `sbatch` smoke test and stopped TaxonKit processing from dropping the first DIAMOND row. | Add a restartable driver that emits normalized annotation, marker-census, family-copy, routing, and discovery artifacts with schemas. |
| `bio-assembly-qc` | Standardized the primary environment contract on Pixi. | Add an executable short-read, long-read, and metagenome driver with read-QC prerequisites, normalized assembler outputs, QUAST/MetaQUAST gates, and post-run checks. |
| `bio-binning-qc` | Standardized the environment and CheckM2 upgrade guidance on Pixi. | Restrict GUNC to prokaryotic bins, replace the literal-FASTA EukCC classifier, and implement QuickClade/GTDB-Tk routing plus the promised output tables. |
| `bio-fasta-database-curator` | Confirmed its structure and links. | Replace randomized `hash()` deduplication with SHA-256, validate raw headers before Biopython truncation, handle empty databases, and ship one CLI that writes the mapping and deduplication reports. |
| `bio-foundation-housekeeping` | Generates importable Pydantic models from a pinned LinkML schema and validates sample, run, file, result, and provenance relationships before publishing six Parquet tables and DuckDB. | Add schema-version migration fixtures and a compatibility report for project-specific schema extensions. |
| `bio-gene-calling` | Standardized its tool environment on Pixi. | Route prokaryotes to Pyrodigal and viruses to pyrodigal-gv, make BRAKER4 the current eukaryotic default, pin containers/databases, and write per-assembly outputs. |
| `bioinformatics-project` | Renders canonical or numbered layouts and can add a dated first-experiment README plus refusing driver while preserving conflict detection and clean reruns. | Add opt-in LICENSE and CITATION templates with explicit author and license inputs. |
| `bio-interdomain-hgt` | Tightened discovery text and removed its leakage into ordinary marker-tree routing. | Implement the RBH, direction, context, normalization, and per-gene tree workflow as a versioned driver with database manifests and per-gate hypothesis revisions. |
| `bio-logic` | Clarified its trigger. | Add study-type profiles so computational and evolutionary studies do not inherit intervention-centric GRADE rules; correct Spearman to monotonic association and broaden causal-design guidance. |
| `bio-phylogenomics` | Corrected IQ-TREE checkpoint versus `-redo` behavior and normalized VeryFastTree support thresholds. | Add a restartable marker extraction, alignment, trimming, model, and tree driver with fixed seeds, reference checksums, and normalized support values. |
| `bio-prefect-dask-nextflow` | Clarified its trigger and scope. | Move Dask cluster creation into flow runtime with guaranteed close, fix compound FASTQ output naming, and provide an `sbatch` Nextflow driver with post-run checks. |
| `bio-protein-clustering-pangenome` | Defined per-genome input mapping, fixed `*` absence handling and OrthoFinder `-S`, and requires MMseqs2 v16+ for GPU use. | Persist marker-gene and ncRNA censuses alongside copy-number and synteny matrices, with a tested small multi-genome fixture. |
| `bio-reads-qc-mapping` | Corrected minimap2 `-I` and `-p` semantics. | Define a sample-sheet schema and make mapping gates conditional on a supplied reference; add an executable paired-, single-, and long-read fixture. |
| `bio-stats-ml-reporting` | Moved scaling inside CV folds and corrected current XGBoost GPU and early-stopping examples. | Add grouped-split, leakage, confounding, calibration, imbalance, and null-baseline gates; replace references to nonexistent scripts with tested entry points. |
| `bio-structure-annotation` | Standardized the primary environment contract on Pixi. | Fix and smoke-test the Boltz v2 YAML/CLI, Foldseek padded-database path, and TM-Vec wrapper. Require approval before sending sequences to public MSA services. |
| `bio-viromics` | Standardized the primary environment contract on Pixi. | Add the required marker, family-copy, synteny, and ncRNA artifacts; pin GVClass/vConTACT3/geNomad resources and implement the hypothesis/reflection loop. |
| `bio-workflow-methods-docwriter` | Added PEP 723 dependencies, installed-path commands, stricter manifest semantics, and tested redaction for keys, tokens, bearer headers, and personal-access tokens. | Add Snakemake and CWL extractors plus a real Nextflow trace fixture that proves the complete evidence path. |
| `biorxiv-search` | Fixed 30-record API pagination with an offline 65-record, three-page regression test. | Separate author-variant match groups, define latest-version semantics, and add bounded retry/backoff for 429 and transient 5xx responses. |
| `crossref-lookup` | Confirmed its structure and links. | Remove its hidden dependency on `scientific-writing`, normalize trailing BibTeX punctuation, distinguish 404 from transient failures, and add a strict nonzero-exit audit mode. |
| `csag-extraction` | Confirmed its structure and links. | Load and validate against the authoritative schema before semantic checks, standardize JSON versus YAML guidance, and make missing text grounding fail strict mode. |
| `exploratory-data-analysis` | Replaced the 200+ claim with measured coverage, added PEP 723 dependencies and CLI help, recognizes compound suffixes, labels CSV sampling, and emits text-only reports. | Add format-family fixtures and content analyzers for the remaining recognized formats; use streaming or memory mapping for large arrays, FASTA, and FASTQ. |
| `jgi-lakehouse` | Removed insecure transport and credential-handling paths, added bounded polling, safe archive checks, zero-file failure tests, and scheduler guidance. | Consolidate contradictory Phytozome query guidance and add a mocked success path spanning token acquisition, paginated query execution, and download verification. |
| `manuscript-review-council` | Clarified its trigger description. | Separate scientific critique from prose editing and rebuttal drafting in routing, then define deterministic artifact paths and a machine-readable issue schema. |
| `notebooks` | Provisioned marimo/Jupyter helpers with PEP 723, uses strict checks and output-inclusive sandboxed export, and fixed invalid Python quotes. | Pin template dependencies and replace the generic Jupyter kernel name with a project placeholder; add conversion fixtures in both directions. |
| `pdf-to-md` | Made local parsing the default, requires explicit remote-upload opt-in, removed secret/password CLI values, fixed installed paths and the LinkML key, and added safety tests. | Add a fixture-backed paper bundle test that checks section audit, article validation, figure handling, and credible missing-field behavior. |
| `plotly-dashboard-skill` | Replaced removed `app.run_server` with `app.run`. | Link the runnable example and QA checklist from `SKILL.md`, pin Dash dependencies, add an app-start smoke test, and enforce the documented callback-latency budget. |
| `polars-dovmed` | Removed undeclared Polars readback, resolves Pixi from `PATH`, bounds local scans, keeps API keys out of argv, and restricts authenticated remotes to HTTPS or loopback. | Add a fixture that exercises the complete processed-output fallback and records the upstream corpus revision. |
| `proposal-review` | Confirmed its structure and links. | Let sponsor rubrics override defaults; otherwise define weights totaling 100% and map normalized scores to recommendation categories. |
| `scientific-impact-assessment` | Uses the DOI resolved from OpenAlex for Altmetric, removes API keys from command examples, and uses a real DOI in the live example. | Add explicit cache and rate-limit behavior for repeated OpenAlex calls. |
| `scientific-writing` | Tightened its trigger description. | Remove bare `write` routing, distinguish prose revision from scientific critique, and replace stale supporting-skill aliases with installed names. |
| `tracking-taxonomy-updates` | Removed references to the deleted skill-local environment, requires an existing QuickClade reference, and emits machine-format output. | Put GTDB-Tk, EukCC, vConTACT3, and GVClass examples behind scheduler jobs and add a tested transformation from QuickClade output to `domain_routing.tsv`. |

## Acceptance Criteria for the Next Round

A skill should move from documented workflow to executable workflow only when it has:

1. A pinned Pixi environment or a PEP 723 helper with no system-Python mutation.
2. A small fixture that exercises the real command path and verifies non-empty outputs.
3. A restartable driver with recorded commands, versions, seeds, database releases, and checksums.
4. Persisted hypothesis, reflection, literature, comparison, and discovery artifacts when the skill performs exploratory omics analysis.
5. A routing benchmark with both a natural-language positive case and a nearby negative case.
