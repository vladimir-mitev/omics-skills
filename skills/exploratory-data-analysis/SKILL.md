---
name: exploratory-data-analysis
description: Inspect scientific data and generate a Markdown structure-and-quality report. Use when triaging tabular, array, sequence, HDF5, JSON, or raster files before downstream analysis.
---

# Exploratory Data Analysis

## Overview

Inspect scientific files before downstream analysis. The bundled script recognizes more than 100 simple and compound suffixes and writes a bounded Markdown report. It performs content-level analysis only for the common formats listed below; other recognized formats receive file metadata and a reference-catalog entry.

The six reference files contain 239 format entries. Some entries describe the same suffix in different domain contexts, so this is not a count of unique formats or implemented parsers.

**Bundled content parsers:**
- NumPy arrays (`.npy`, `.npz`), CSV/TSV samples, JSON, and HDF5
- FASTA and FASTQ, including common gzip-compressed suffixes
- TIFF/OME-TIFF, PNG, and JPEG raster images
- Reference-only metadata for every other recognized suffix

## When to Use This Skill

Use this skill when:
- User provides a path to a scientific data file for analysis
- User asks to "explore", "analyze", or "summarize" a data file
- User wants to understand the structure and content of scientific data
- User needs a structure-and-quality report before analysis
- User wants to assess data quality or completeness
- User asks what type of analysis is appropriate for a file

## Quick Reference

| Task | Action |
|------|--------|
| Unknown file | Detect extension and load the matching reference file before analyzing content. |
| Tabular data | Summarize dimensions, types, missingness, ranges, outliers, duplicates, and candidate keys. |
| Sequence data | Count records, length distribution, GC content, quality scores when available, and format issues. |
| Imaging or arrays | Report shape, channels/axes, dtype, value range, metadata, and scale/calibration when present. |
| Final report | Write a concise Markdown EDA report with findings, caveats, and next analysis options. |

## Supported File Categories

The reference catalog is organized into six categories. These entries guide custom analysis; they do not imply that `eda_analyzer.py` parses every listed format.

### 1. Chemistry and Molecular Formats (43 reference entries)
Structure files, computational chemistry outputs, molecular dynamics trajectories, and chemical databases.

**File types include:** `.pdb`, `.cif`, `.mol`, `.mol2`, `.sdf`, `.xyz`, `.smi`, `.gro`, `.log`, `.fchk`, `.cube`, `.dcd`, `.xtc`, `.trr`, `.prmtop`, `.psf`, and more.

**Reference file:** `references/chemistry_molecular_formats.md`

### 2. Bioinformatics and Genomics Formats (44 reference entries)
Sequence data, alignments, annotations, variants, and expression data.

**File types include:** `.fasta`, `.fastq`, `.sam`, `.bam`, `.vcf`, `.bed`, `.gff`, `.gtf`, `.bigwig`, `.h5ad`, `.loom`, `.counts`, `.mtx`, and more.

**Reference file:** `references/bioinformatics_genomics_formats.md`

### 3. Microscopy and Imaging Formats (41 reference entries)
Microscopy images, medical imaging, whole slide imaging, and electron microscopy.

**File types include:** `.tif`, `.nd2`, `.lif`, `.czi`, `.ims`, `.dcm`, `.nii`, `.mrc`, `.dm3`, `.vsi`, `.svs`, `.ome.tiff`, and more.

**Reference file:** `references/microscopy_imaging_formats.md`

### 4. Spectroscopy and Analytical Chemistry Formats (43 reference entries)
NMR, mass spectrometry, IR/Raman, UV-Vis, X-ray, chromatography, and other analytical techniques.

**File types include:** `.fid`, `.mzML`, `.mzXML`, `.raw`, `.mgf`, `.spc`, `.jdx`, `.xy`, `.cif` (crystallography), `.wdf`, and more.

**Reference file:** `references/spectroscopy_analytical_formats.md`

### 5. Proteomics and Metabolomics Formats (36 reference entries)
Mass spec proteomics, metabolomics, lipidomics, and multi-omics data.

**File types include:** `.mzML`, `.pepXML`, `.protXML`, `.mzid`, `.mzTab`, `.sky`, `.mgf`, `.msp`, `.h5ad`, and more.

**Reference file:** `references/proteomics_metabolomics_formats.md`

### 6. General Scientific Data Formats (32 reference entries)
Arrays, tables, hierarchical data, compressed archives, and common scientific formats.

**File types include:** `.npy`, `.npz`, `.csv`, `.xlsx`, `.json`, `.hdf5`, `.zarr`, `.parquet`, `.mat`, `.fits`, `.nc`, `.xml`, and more.

**Reference file:** `references/general_scientific_formats.md`

## Instructions

### Step 1: File Type Detection

When a user provides a file path, first identify the file type:

1. Extract the file extension
2. Look up the extension in the appropriate reference file
3. Identify the file category and format description
4. Load format-specific information

**Example:**
```
User: "Analyze data.fastq"
→ Extension: .fastq
→ Category: bioinformatics_genomics
→ Format: FASTQ Format (sequence data with quality scores)
→ Reference: references/bioinformatics_genomics_formats.md
```

### Step 2: Load Format-Specific Information

Based on the file type, read the corresponding reference file to understand:
- **Typical Data:** What kind of data this format contains
- **Use Cases:** Common applications for this format
- **Python Libraries:** How to read the file in Python
- **EDA Approach:** What analyses are appropriate for this data type

Search the reference file for the specific extension (e.g., search for "### .fastq" in `bioinformatics_genomics_formats.md`).

### Step 3: Perform Data Analysis

Use the bundled script for its supported parsers, or implement a domain-specific analysis after reading the relevant reference entry.

**Option A: Run the analyzer from the checkout**
```bash
uv run skills/exploratory-data-analysis/scripts/eda_analyzer.py <filepath> [output.md]
```

**Option B: Run the installed analyzer**
```bash
uv run ~/.agents/skills/exploratory-data-analysis/scripts/eda_analyzer.py <filepath> [output.md]
```

PEP 723 metadata in the script creates an isolated environment with the libraries used by its content parsers.

**Option C: Custom analysis in the conversation**
Based on the format information from the reference file, perform appropriate analysis:

For tabular data (CSV, TSV, Excel):
- Load with pandas
- Check dimensions, data types
- Analyze missing values
- Calculate summary statistics
- Identify outliers
- Check for duplicates

For sequence data (FASTA, FASTQ):
- Count sequences
- Analyze length distributions
- Calculate GC content
- Assess quality scores (FASTQ)

For images (TIFF, ND2, CZI):
- Check dimensions (X, Y, Z, C, T)
- Analyze bit depth and value range
- Extract metadata (channels, timestamps, spatial calibration)
- Calculate intensity statistics

For arrays (NPY, HDF5):
- Check shape and dimensions
- Analyze data type
- Calculate statistical summaries
- Check for missing/invalid values

### Step 4: Generate the Report

The bundled script reports file metadata, the matching reference entry, sampled or full content statistics, parser errors, and format-level follow-up options. Label every sample explicitly. For a custom analysis, use the following sections:

#### Required Sections:
1. **Title and Metadata**
   - Filename and timestamp
   - File size and location

2. **Basic Information**
   - File properties
   - Format identification

3. **File Type Details**
   - Format description from reference
   - Typical data content
   - Common use cases
   - Python libraries for reading

4. **Data Analysis**
   - Structure and dimensions
   - Statistical summaries
   - Quality assessment
   - Data characteristics

5. **Key Findings**
   - Notable patterns
   - Potential issues
   - Quality metrics

6. **Recommendations**
   - Preprocessing steps
   - Appropriate analyses
   - Tools and methods
   - Visualization approaches

#### Template Location
Use `assets/report_template.md` as a guide for report structure.

### Step 5: Save Report

Save the markdown report with a descriptive filename:
- Pattern: `{original_filename}_eda_report.md`
- Example: `experiment_data.fastq` → `experiment_data_eda_report.md`

## Detailed Format References

Each reference file contains short entries for dozens of file types. To find information about a specific format:

1. Identify the category from the extension
2. Read the appropriate reference file
3. Search for the section heading matching the extension (e.g., "### .pdb")
4. Extract the format information

### Reference File Structure

Each format entry includes:
- **Description:** What the format is
- **Typical Data:** What it contains
- **Use Cases:** Common applications
- **Python Libraries:** How to read it (with code examples)
- **EDA Approach:** Specific analyses to perform

**Example lookup:**
```markdown
### .pdb - Protein Data Bank
**Description:** Standard format for 3D structures of biological macromolecules
**Typical Data:** Atomic coordinates, residue information, secondary structure
**Use Cases:** Protein structure analysis, molecular visualization, docking
**Python Libraries:**
- `Biopython`: `Bio.PDB`
- `MDAnalysis`: `MDAnalysis.Universe('file.pdb')`
**EDA Approach:**
- Structure validation (bond lengths, angles)
- B-factor distribution
- Missing residues detection
- Ramachandran plots
```

## Input Requirements

- One or more local scientific data files.
- Permission to read the files and enough disk/RAM for the requested inspection.
- Domain context when available, such as assay type, organism, instrument, or expected sample count.
- Optional output path for the Markdown report.

## Output

- Markdown EDA report next to the input file or at the requested output path.
- Basic file metadata: path, size, modified time, detected format, and relevant parser.
- Data structure summary, quality observations, likely issues, and downstream recommendations.
- Any generated figures, tables, or temporary summaries needed to support the report.

## Quality Gates

- [ ] File type detection and selected reference file are stated.
- [ ] The report distinguishes observed facts from downstream recommendations.
- [ ] Missing values, malformed records, parser failures, or unreadable sections are reported explicitly.
- [ ] Large-file sampling is labeled as sampling and does not imply full-file statistics.
- [ ] Suggested downstream analyses match the detected format and available metadata.

## Best Practices

### Reading Reference Files

Reference files are large (10,000+ words each). To efficiently use them:

1. **Search by extension:** Use grep to find the specific format
   ```python
   import re
   with open('references/chemistry_molecular_formats.md', 'r') as f:
       content = f.read()
       pattern = r'### \.pdb[^#]*?(?=###|\Z)'
       match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
   ```

2. **Extract relevant sections:** Don't load entire reference files into context unnecessarily

3. **Cache format info:** If analyzing multiple files of the same type, reuse the format information

### Data Analysis

1. **Sample large files:** For files with millions of records, analyze a representative sample
2. **Handle errors gracefully:** Many scientific formats require specific libraries; provide clear installation instructions
3. **Validate metadata:** Cross-check metadata consistency (e.g., stated dimensions vs actual data)
4. **Consider data provenance:** Note instrument, software versions, processing steps

### Report Generation

1. **Cover the evidence:** Include the observations needed to choose the next analysis
2. **Be specific:** Provide concrete recommendations based on the file type
3. **Be actionable:** Suggest specific next steps and tools
4. **Include code examples:** Show how to load and work with the data

## Examples

### Example 1: Analyzing a FASTQ file

```python
# User provides: "Analyze reads.fastq"

# 1. Detect file type
extension = '.fastq'
category = 'bioinformatics_genomics'

# 2. Read reference info
# Search references/bioinformatics_genomics_formats.md for "### .fastq"

# 3. Perform analysis
from Bio import SeqIO
sequences = list(SeqIO.parse('reads.fastq', 'fastq'))
# Calculate: read count, length distribution, quality scores, GC content

# 4. Generate report
# Include: format description, analysis results, QC recommendations

# 5. Save as: reads_eda_report.md
```

### Example 2: Analyzing a CSV dataset

```python
# User provides: "Explore experiment_results.csv"

# 1. Detect: .csv → general_scientific

# 2. Load reference for CSV format

# 3. Analyze
import pandas as pd
df = pd.read_csv('experiment_results.csv')
# Dimensions, dtypes, missing values, statistics, correlations

# 4. Generate report with:
# - Data structure
# - Missing value patterns
# - Statistical summaries
# - Correlation matrix
# - Outlier detection results

# 5. Save report
```

### Example 3: Analyzing microscopy data

```python
# User provides: "Analyze cells.nd2"

# 1. Detect: .nd2 → microscopy_imaging (Nikon format)

# 2. Read reference for ND2 format
# Learn: multi-dimensional (XYZCT), requires nd2reader

# 3. Analyze
from nd2reader import ND2Reader
with ND2Reader('cells.nd2') as images:
    # Extract: dimensions, channels, timepoints, metadata
    # Calculate: intensity statistics, frame info

# 4. Generate report with:
# - Image dimensions (XY, Z-stacks, time, channels)
# - Channel wavelengths
# - Pixel size and calibration
# - Recommendations for image analysis

# 5. Save report
```

## Troubleshooting

### Missing Libraries

Custom analysis of formats outside the bundled parsers may require specialized libraries:

**Problem:** Import error when trying to read a file

**Solution:** Add the parser to the project environment with `uv`, or run a one-off command with `uv run --with`.
```bash
uv run --with biopython python analysis.py
```

Common requirements by category:
- **Bioinformatics:** `biopython`, `pysam`, `pyBigWig`
- **Chemistry:** `rdkit`, `mdanalysis`, `cclib`
- **Microscopy:** `tifffile`, `nd2reader`, `aicsimageio`, `pydicom`
- **Spectroscopy:** `nmrglue`, `pymzml`, `pyteomics`
- **General:** `pandas`, `numpy`, `h5py`, `scipy`

### Unknown File Types

If a file extension is not in the references:

1. Ask the user about the file format
2. Check if it's a vendor-specific variant
3. Attempt generic analysis based on file structure (text vs binary)
4. Provide general recommendations

### Large Files

For very large files:

1. Use sampling strategies (first N records)
2. Use memory-mapped access (for HDF5, NPY)
3. Process in chunks (for CSV, FASTQ)
4. Provide estimates based on samples

## Script Usage

The `scripts/eda_analyzer.py` can be used directly:

```bash
# From this repository
uv run skills/exploratory-data-analysis/scripts/eda_analyzer.py data.csv

# From an installed skill, with an explicit output file
uv run ~/.agents/skills/exploratory-data-analysis/scripts/eda_analyzer.py \
  data.csv output_report.md

# The script will:
# 1. Auto-detect file type
# 2. Load format references
# 3. Perform appropriate analysis
# 4. Generate markdown report
```

The script performs content analysis for NumPy, CSV/TSV, JSON, HDF5, FASTA/FASTQ, and common raster images. It emits a `reference_only` scope for recognized formats without a bundled parser.

## Advanced Usage

### Multi-File Analysis

When analyzing multiple related files:
1. Perform individual EDA on each file
2. Create a summary comparison report
3. Identify relationships and dependencies
4. Suggest integration strategies

### Quality Control

For data quality assessment:
1. Check format compliance
2. Validate metadata consistency
3. Assess completeness
4. Identify outliers and anomalies
5. Compare to expected ranges/distributions

### Preprocessing Recommendations

Based on data characteristics, recommend:
1. Normalization strategies
2. Missing value imputation
3. Outlier handling
4. Batch correction
5. Format conversions

## Resources

### scripts/
- `eda_analyzer.py`: Bounded analyzer for the supported common formats

### references/
- `chemistry_molecular_formats.md`: 43 chemistry/molecular reference entries
- `bioinformatics_genomics_formats.md`: 44 bioinformatics reference entries
- `microscopy_imaging_formats.md`: 41 imaging reference entries
- `spectroscopy_analytical_formats.md`: 43 spectroscopy reference entries
- `proteomics_metabolomics_formats.md`: 36 omics reference entries
- `general_scientific_formats.md`: 32 general-data reference entries

### assets/
- `report_template.md`: Markdown template for EDA reports
