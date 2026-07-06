---
name: bio-gene-calling
description: Call genes and annotate basic features for prokaryotes, viruses, and eukaryotes.
---

# Bio Gene Calling

Call genes and annotate basic features for prokaryotes, viruses, and eukaryotes.

## Instructions

1. Select gene caller by organism class:
   - Prokaryotes and viruses (including giant viruses): **pyrodigal-gv** v0.3+ (SIMD-accelerated Cython bindings around prodigal-gv; same model set, much faster, actively maintained).
   - Eukaryotes: **BRAKER3** (*Genome Research* 2024, DOI: 10.1101/gr.278090.123) as the fully-automated pipeline. BRAKER3 invokes AUGUSTUS internally; do not run AUGUSTUS as a standalone caller.
2. For eukaryotic/protist drafts with ONT cDNA or other transcriptome reads, build a transcript evidence bundle before gene calling:
   - Orient/filter full-length ONT cDNA reads with the `Pychopper` guidance in `/bio-reads-qc-mapping`, including plain `.fastq` output handling and resume from existing classified reads after report-plotting failures.
   - Map transcript reads splice-aware to each candidate draft genome with minimap2 (`-ax splice` family settings appropriate to the organism/data), sort/index BAMs, and compute a per-genome mapped fraction table.
   - Use the best-supported draft genome as the primary evidence target, but keep the full mapping table because it documents sample/genome assignment and cross-sample ambiguity.
   - Produce StringTie long-read GTF/transcript FASTA and, when useful, a reference-free transcript assembly such as RNA-Bloom. Summarize these paths in a `gene_calling_evidence.tsv` bundle with columns: sample_id, evidence_type, genome_id, path, notes. The bundle should be directly usable by BRAKER3 or another eukaryote-aware caller.
3. Run gene calling and produce GFF/FAA/FNA.
4. Always run tRNA detection and rRNA detection on every assembly, and report counts per class. Negative findings (zero hits at default and relaxed thresholds) are required results — never leave ncRNA presence/absence unstated.
   - tRNA: tRNAscan-SE v2.0.12+ (preferred; isotype-specific covariance models) or ARAGORN v1.2.41+ for tmRNA where appropriate.
   - rRNA: Infernal v1.1.5+ `cmsearch` against the relevant Rfam covariance models. Pick the model set by domain of life:
     - Bacteria: RF00177 (SSU 16S), RF02541 (LSU 23S), RF00001 (5S).
     - Archaea: RF01959 (SSU 16S), RF02540 (LSU 23S), RF00001 (5S).
     - Eukaryotes: RF01960 (SSU 18S), RF02543 (LSU 28S), RF00002 (5.8S), RF00001 (5S).
     - Metazoan mitochondria, when applicable: RF02555 (12S), RF02546 (16S).
     `cmsearch --rfam --cut_ga --nohmmonly` is a sensible default; if no hits, rerun without `--cut_ga` and record both results.
5. For viral or otherwise specialized genomes, choose the gene caller and mode from tool documentation and the literature-derived analysis playbook for the inferred group; record the rationale.
6. Summarize gene count, gene density, coding fraction, ORF length distribution, unusually long ORFs, overlapping genes, tRNAs, rRNAs, and other features that may affect downstream discovery.
7. Flag gene-calling anomalies relative to the inferred group and data type, including patterns that could hide interesting biology or indicate artifacts.
8. Produce a `ncRNA_census.tsv` with columns: assembly, class (tRNA/rRNA/tmRNA/other), tool, model (Rfam accession when applicable), threshold (default/relaxed), count, notes. This file is required even when all counts are zero.

## Quick Reference

| Task | Action |
|------|--------|
| Run workflow | Follow the steps in this skill and capture outputs. |
| Validate inputs | Confirm required inputs and reference data exist. |
| Review outputs | Inspect reports and QC gates before proceeding. |
| Tool docs | See `docs/README.md`. |

## Input Requirements

Prerequisites:
- Tools available in the active environment (Pixi/conda/system). See `docs/README.md` for expected tools.
- Input contigs or bins are available.
Inputs:
- contigs.fasta or bins/*.fasta
- Optional transcript evidence: ONT cDNA/long-read RNA FASTQ, RNA-Bloom transcript FASTA, splice-aware BAM/BAI, StringTie GTF/transcript FASTA, and `gene_calling_evidence.tsv`.

## Output

- results/bio-gene-calling/genes.gff3
- results/bio-gene-calling/proteins.faa
- results/bio-gene-calling/cds.fna
- results/bio-gene-calling/gene_metrics.tsv
- results/bio-gene-calling/gene_calling_discovery_flags.tsv
- results/bio-gene-calling/ncRNA_census.tsv
- results/bio-gene-calling/gene_calling_evidence.tsv (when transcript evidence is used)
- results/bio-gene-calling/logs/

## Quality Gates

- [ ] Gene count sanity checks pass.
- [ ] Start/stop codon checks pass.
- [ ] On failure: retry with alternative parameters; if still failing, record in report and exit non-zero.
- [ ] Verify contigs are non-empty and DNA alphabet.
- [ ] Verify outputs contain expected feature types.
- [ ] Specialized inputs use a literature/tool-supported gene-calling mode or document why not.
- [ ] Gene metrics include discovery-relevant flags for unusual ORFs, gene density, coding fraction, and tRNA/RNA features.
- [ ] `ncRNA_census.tsv` exists and records both default-threshold and relaxed-threshold results for tRNA and rRNA, including explicit zero counts.
- [ ] For eukaryotic/protist transcript evidence, mapping summaries show which draft genome is supported and whether competing drafts have negligible, ambiguous, or substantial mapping.
- [ ] Transcript evidence paths are recorded in a bundle with enough detail for BRAKER3 or another caller to consume them reproducibly.

## Examples

### Example 1: Expected input layout

```text
contigs.fasta or bins/*.fasta
```

## Troubleshooting

**Issue**: Missing inputs or reference databases
**Solution**: Verify paths and permissions before running the workflow.

**Issue**: Low-quality results or failed QC gates
**Solution**: Review reports, adjust parameters, and re-run the affected step.

**Issue**: ONT cDNA evidence workflow failed after `Pychopper` but classified reads exist
**Solution**: Follow `/bio-reads-qc-mapping` recovery guidance: verify/rename plain FASTQ outputs, run lightweight stats, resume mapping/StringTie/RNA-Bloom, and keep the failure plus resume command in the methods record.
