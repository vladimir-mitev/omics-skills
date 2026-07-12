#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "biopython>=1.83",
#   "h5py>=3.10",
#   "numpy>=1.26",
#   "pandas>=2.0",
#   "pillow>=10.0",
# ]
# ///
"""Inspect supported scientific files and write a bounded Markdown report."""

import argparse
import gzip
import sys
from datetime import datetime
import json
from pathlib import Path


CSV_SAMPLE_LIMIT = 10_000

COMPOUND_EXTENSION_MAP = {
    'ome.tif': ('microscopy_imaging', 'OME-TIFF'),
    'ome.tiff': ('microscopy_imaging', 'OME-TIFF'),
    'ome.zarr': ('microscopy_imaging', 'OME-Zarr'),
    'nii.gz': ('microscopy_imaging', 'Compressed NIfTI'),
    'fastq.gz': ('bioinformatics_genomics', 'Compressed FASTQ Format'),
    'fq.gz': ('bioinformatics_genomics', 'Compressed FASTQ Format'),
    'fasta.gz': ('bioinformatics_genomics', 'Compressed FASTA Format'),
    'fa.gz': ('bioinformatics_genomics', 'Compressed FASTA Format'),
    'fna.gz': ('bioinformatics_genomics', 'Compressed FASTA Format'),
    'vcf.gz': ('bioinformatics_genomics', 'Compressed Variant Call Format'),
    'gff.gz': ('bioinformatics_genomics', 'Compressed General Feature Format'),
    'gff3.gz': ('bioinformatics_genomics', 'Compressed General Feature Format'),
    'bed.gz': ('bioinformatics_genomics', 'Compressed Browser Extensible Data'),
    'pep.xml': ('proteomics_metabolomics', 'Trans-Proteomic Pipeline Peptide XML'),
    'prot.xml': ('proteomics_metabolomics', 'Protein Inference Results'),
}


def detect_file_type(filepath):
    """
    Detect the file type from its simple or bounded compound suffix.

    Returns:
        tuple: (extension, file_category, reference_file)
    """
    file_path = Path(filepath)
    name = file_path.name.lower()

    for extension, (category, description) in COMPOUND_EXTENSION_MAP.items():
        if name.endswith(f'.{extension}'):
            return extension, category, description

    extension = file_path.suffix.lower()

    # Map extensions to categories and reference files
    extension_map = {
        # Chemistry/Molecular
        'pdb': ('chemistry_molecular', 'Protein Data Bank'),
        'cif': ('chemistry_molecular', 'Crystallographic Information File'),
        'mol': ('chemistry_molecular', 'MDL Molfile'),
        'mol2': ('chemistry_molecular', 'Tripos Mol2'),
        'sdf': ('chemistry_molecular', 'Structure Data File'),
        'xyz': ('chemistry_molecular', 'XYZ Coordinates'),
        'smi': ('chemistry_molecular', 'SMILES String'),
        'smiles': ('chemistry_molecular', 'SMILES String'),
        'pdbqt': ('chemistry_molecular', 'AutoDock PDBQT'),
        'mae': ('chemistry_molecular', 'Maestro Format'),
        'gro': ('chemistry_molecular', 'GROMACS Coordinate File'),
        'log': ('chemistry_molecular', 'Gaussian Log File'),
        'out': ('chemistry_molecular', 'Quantum Chemistry Output'),
        'wfn': ('chemistry_molecular', 'Wavefunction Files'),
        'wfx': ('chemistry_molecular', 'Wavefunction Files'),
        'fchk': ('chemistry_molecular', 'Gaussian Formatted Checkpoint'),
        'cube': ('chemistry_molecular', 'Gaussian Cube File'),
        'dcd': ('chemistry_molecular', 'Binary Trajectory'),
        'xtc': ('chemistry_molecular', 'Compressed Trajectory'),
        'trr': ('chemistry_molecular', 'GROMACS Trajectory'),
        'nc': ('chemistry_molecular', 'Amber NetCDF Trajectory'),
        'netcdf': ('chemistry_molecular', 'Amber NetCDF Trajectory'),

        # Bioinformatics/Genomics
        'fasta': ('bioinformatics_genomics', 'FASTA Format'),
        'fa': ('bioinformatics_genomics', 'FASTA Format'),
        'fna': ('bioinformatics_genomics', 'FASTA Format'),
        'fastq': ('bioinformatics_genomics', 'FASTQ Format'),
        'fq': ('bioinformatics_genomics', 'FASTQ Format'),
        'sam': ('bioinformatics_genomics', 'Sequence Alignment/Map'),
        'bam': ('bioinformatics_genomics', 'Binary Alignment/Map'),
        'cram': ('bioinformatics_genomics', 'CRAM Format'),
        'bed': ('bioinformatics_genomics', 'Browser Extensible Data'),
        'bedgraph': ('bioinformatics_genomics', 'BED with Graph Data'),
        'bigwig': ('bioinformatics_genomics', 'Binary BigWig'),
        'bw': ('bioinformatics_genomics', 'Binary BigWig'),
        'bigbed': ('bioinformatics_genomics', 'Binary BigBed'),
        'bb': ('bioinformatics_genomics', 'Binary BigBed'),
        'gff': ('bioinformatics_genomics', 'General Feature Format'),
        'gff3': ('bioinformatics_genomics', 'General Feature Format'),
        'gtf': ('bioinformatics_genomics', 'Gene Transfer Format'),
        'vcf': ('bioinformatics_genomics', 'Variant Call Format'),
        'bcf': ('bioinformatics_genomics', 'Binary VCF'),
        'gvcf': ('bioinformatics_genomics', 'Genomic VCF'),

        # Microscopy/Imaging
        'tif': ('microscopy_imaging', 'Tagged Image File Format'),
        'tiff': ('microscopy_imaging', 'Tagged Image File Format'),
        'nd2': ('microscopy_imaging', 'Nikon NIS-Elements'),
        'lif': ('microscopy_imaging', 'Leica Image Format'),
        'czi': ('microscopy_imaging', 'Carl Zeiss Image'),
        'oib': ('microscopy_imaging', 'Olympus Image Format'),
        'oif': ('microscopy_imaging', 'Olympus Image Format'),
        'vsi': ('microscopy_imaging', 'Olympus VSI'),
        'ims': ('microscopy_imaging', 'Imaris Format'),
        'lsm': ('microscopy_imaging', 'Zeiss LSM'),
        'stk': ('microscopy_imaging', 'MetaMorph Stack'),
        'dv': ('microscopy_imaging', 'DeltaVision'),
        'mrc': ('microscopy_imaging', 'Medical Research Council'),
        'dm3': ('microscopy_imaging', 'Gatan Digital Micrograph'),
        'dm4': ('microscopy_imaging', 'Gatan Digital Micrograph'),
        'dcm': ('microscopy_imaging', 'DICOM'),
        'nii': ('microscopy_imaging', 'NIfTI'),
        'nrrd': ('microscopy_imaging', 'Nearly Raw Raster Data'),
        'png': ('microscopy_imaging', 'Portable Network Graphics'),
        'jpg': ('microscopy_imaging', 'JPEG Image'),
        'jpeg': ('microscopy_imaging', 'JPEG Image'),

        # Spectroscopy/Analytical
        'fid': ('spectroscopy_analytical', 'NMR Free Induction Decay'),
        'mzml': ('spectroscopy_analytical', 'Mass Spectrometry Markup Language'),
        'mzxml': ('spectroscopy_analytical', 'Mass Spectrometry XML'),
        'raw': ('spectroscopy_analytical', 'Vendor Raw Files'),
        'd': ('spectroscopy_analytical', 'Agilent Data Directory'),
        'mgf': ('spectroscopy_analytical', 'Mascot Generic Format'),
        'spc': ('spectroscopy_analytical', 'Galactic SPC'),
        'jdx': ('spectroscopy_analytical', 'JCAMP-DX'),
        'jcamp': ('spectroscopy_analytical', 'JCAMP-DX'),

        # Proteomics/Metabolomics
        'pepxml': ('proteomics_metabolomics', 'Trans-Proteomic Pipeline Peptide XML'),
        'protxml': ('proteomics_metabolomics', 'Protein Inference Results'),
        'mzid': ('proteomics_metabolomics', 'Peptide Identification Format'),
        'mztab': ('proteomics_metabolomics', 'Proteomics/Metabolomics Tabular Format'),

        # General Scientific
        'npy': ('general_scientific', 'NumPy Array'),
        'npz': ('general_scientific', 'Compressed NumPy Archive'),
        'csv': ('general_scientific', 'Comma-Separated Values'),
        'tsv': ('general_scientific', 'Tab-Separated Values'),
        'xlsx': ('general_scientific', 'Excel Spreadsheets'),
        'xls': ('general_scientific', 'Excel Spreadsheets'),
        'json': ('general_scientific', 'JavaScript Object Notation'),
        'xml': ('general_scientific', 'Extensible Markup Language'),
        'hdf5': ('general_scientific', 'Hierarchical Data Format 5'),
        'h5': ('general_scientific', 'Hierarchical Data Format 5'),
        'h5ad': ('bioinformatics_genomics', 'Anndata Format'),
        'zarr': ('general_scientific', 'Chunked Array Storage'),
        'parquet': ('general_scientific', 'Apache Parquet'),
        'mat': ('general_scientific', 'MATLAB Data'),
        'fits': ('general_scientific', 'Flexible Image Transport System'),
    }

    ext_clean = extension.lstrip('.')
    if ext_clean in extension_map:
        category, description = extension_map[ext_clean]
        return ext_clean, category, description

    return ext_clean, 'unknown', 'Unknown Format'


def get_file_basic_info(filepath):
    """Get basic file information."""
    file_path = Path(filepath)
    stat = file_path.stat()

    extension, _, _ = detect_file_type(filepath)
    return {
        'filename': file_path.name,
        'path': str(file_path.absolute()),
        'size_bytes': stat.st_size,
        'size_human': format_bytes(stat.st_size),
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'extension': f'.{extension}' if extension else '',
    }


def format_bytes(size):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def load_reference_info(category, extension):
    """
    Load reference information for the file type.

    Args:
        category: File category (e.g., 'chemistry_molecular')
        extension: File extension

    Returns:
        dict: Reference information
    """
    # Map categories to reference files
    category_files = {
        'chemistry_molecular': 'chemistry_molecular_formats.md',
        'bioinformatics_genomics': 'bioinformatics_genomics_formats.md',
        'microscopy_imaging': 'microscopy_imaging_formats.md',
        'spectroscopy_analytical': 'spectroscopy_analytical_formats.md',
        'proteomics_metabolomics': 'proteomics_metabolomics_formats.md',
        'general_scientific': 'general_scientific_formats.md',
    }

    if category not in category_files:
        return None

    # Get the reference file path
    script_dir = Path(__file__).parent
    ref_file = script_dir.parent / 'references' / category_files[category]

    if not ref_file.exists():
        return None

    # Parse the reference file for the specific extension
    # This is a simplified parser - could be more sophisticated
    try:
        with open(ref_file, 'r') as f:
            content = f.read()

        # Compound suffixes share the reference entry for their base format.
        import re
        base_extension = extension.removesuffix('.gz')
        reference_extension = {
            'fa': 'fasta',
            'fna': 'fasta',
            'fq': 'fastq',
            'h5': 'hdf5',
            'jpeg': 'jpg',
            'tiff': 'tif',
            'ome.tiff': 'ome.tif',
            'prot.xml': 'protxml',
            'pep.xml': 'pepxml',
        }.get(base_extension, base_extension)
        pattern = rf'### \.{re.escape(reference_extension)}[^#]*?(?=###|\Z)'
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)

        if match:
            section = match.group(0)
            return {
                'raw_section': section,
                'reference_file': category_files[category]
            }
    except Exception as e:
        print(f"Error loading reference: {e}", file=sys.stderr)

    return None


def analyze_file(filepath):
    """
    Main analysis function that routes to specific analyzers.

    Returns:
        dict: Analysis results
    """
    basic_info = get_file_basic_info(filepath)
    extension, category, description = detect_file_type(filepath)

    analysis = {
        'basic_info': basic_info,
        'file_type': {
            'extension': extension,
            'category': category,
            'description': description
        },
        'reference_info': load_reference_info(category, extension),
        'data_analysis': {}
    }

    # Try to perform data-specific analysis based on file type
    try:
        if category == 'general_scientific':
            analysis['data_analysis'] = analyze_general_scientific(filepath, extension)
        elif category == 'bioinformatics_genomics':
            analysis['data_analysis'] = analyze_bioinformatics(filepath, extension)
        elif category == 'microscopy_imaging':
            analysis['data_analysis'] = analyze_imaging(filepath, extension)
        elif category == 'chemistry_molecular':
            analysis['data_analysis'] = analyze_chemistry(filepath, extension)
        elif category in {'spectroscopy_analytical', 'proteomics_metabolomics'}:
            analysis['data_analysis'] = analyze_spectrometry(filepath, extension)
    except Exception as e:
        analysis['data_analysis']['error'] = str(e)

    if not analysis['data_analysis']:
        analysis['data_analysis'] = {
            'analysis_scope': 'reference_only',
            'note': 'The bundled analyzer recognizes this suffix but has no content parser for it.',
        }

    return analysis


def analyze_general_scientific(filepath, extension):
    """Analyze general scientific data formats."""
    results = {}

    try:
        if extension in ['npy']:
            import numpy as np
            data = np.load(filepath, mmap_mode='r')
            results = {
                'analysis_scope': 'memory_mapped',
                'shape': data.shape,
                'dtype': str(data.dtype),
                'size': data.size,
                'ndim': data.ndim,
                'statistics': {
                    'min': float(np.min(data)) if np.issubdtype(data.dtype, np.number) else None,
                    'max': float(np.max(data)) if np.issubdtype(data.dtype, np.number) else None,
                    'mean': float(np.mean(data)) if np.issubdtype(data.dtype, np.number) else None,
                    'std': float(np.std(data)) if np.issubdtype(data.dtype, np.number) else None,
                }
            }

        elif extension in ['npz']:
            import numpy as np
            data = np.load(filepath)
            results = {
                'arrays': list(data.files),
                'array_count': len(data.files),
                'array_shapes': {name: data[name].shape for name in data.files}
            }

        elif extension in ['csv', 'tsv']:
            import pandas as pd
            sep = '\t' if extension == 'tsv' else ','
            loaded = pd.read_csv(filepath, sep=sep, nrows=CSV_SAMPLE_LIMIT + 1)
            sample_truncated = len(loaded) > CSV_SAMPLE_LIMIT
            df = loaded.iloc[:CSV_SAMPLE_LIMIT].copy()

            results = {
                'analysis_scope': 'sample',
                'sampling': {
                    'method': 'first_rows',
                    'row_limit': CSV_SAMPLE_LIMIT,
                    'rows_sampled': len(df),
                    'more_rows_present': sample_truncated,
                },
                'sample_shape': df.shape,
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'missing_values': df.isnull().sum().to_dict(),
                'summary_statistics': df.describe().to_dict() if len(df.select_dtypes(include='number').columns) > 0 else {}
            }

        elif extension in ['json']:
            with open(filepath, 'r') as f:
                data = json.load(f)

            results = {
                'type': type(data).__name__,
                'keys': list(data.keys()) if isinstance(data, dict) else None,
                'length': len(data) if isinstance(data, (list, dict)) else None
            }

        elif extension in ['h5', 'hdf5']:
            import h5py
            with h5py.File(filepath, 'r') as f:
                def get_structure(group, prefix=''):
                    items = {}
                    for key in group.keys():
                        path = f"{prefix}/{key}"
                        if isinstance(group[key], h5py.Dataset):
                            items[path] = {
                                'type': 'dataset',
                                'shape': group[key].shape,
                                'dtype': str(group[key].dtype)
                            }
                        elif isinstance(group[key], h5py.Group):
                            items[path] = {'type': 'group'}
                            items.update(get_structure(group[key], path))
                    return items

                results = {
                    'structure': get_structure(f),
                    'attributes': dict(f.attrs)
                }

    except ImportError as e:
        results['error'] = f"Required library not installed: {e}"
    except Exception as e:
        results['error'] = f"Analysis error: {e}"

    return results


def analyze_bioinformatics(filepath, extension):
    """Analyze bioinformatics/genomics formats."""
    results = {}
    logical_extension = extension.removesuffix('.gz')
    open_text = gzip.open if extension.endswith('.gz') else open

    try:
        if logical_extension in ['fasta', 'fa', 'fna']:
            from Bio import SeqIO
            sequence_count = 0
            total_length = 0
            min_length = None
            max_length = 0
            sequence_ids = []
            with open_text(filepath, 'rt') as source:
                for sequence in SeqIO.parse(source, 'fasta'):
                    length = len(sequence)
                    sequence_count += 1
                    total_length += length
                    min_length = length if min_length is None else min(min_length, length)
                    max_length = max(max_length, length)
                    if len(sequence_ids) < 10:
                        sequence_ids.append(sequence.id)

            results = {
                'analysis_scope': 'streaming_full_file',
                'sequence_count': sequence_count,
                'total_length': total_length,
                'mean_length': total_length / sequence_count if sequence_count else 0,
                'min_length': min_length or 0,
                'max_length': max_length,
                'sequence_ids': sequence_ids,
            }

        elif logical_extension in ['fastq', 'fq']:
            from Bio import SeqIO
            sequences = []
            with open_text(filepath, 'rt') as source:
                for i, seq in enumerate(SeqIO.parse(source, 'fastq')):
                    sequences.append(seq)
                    if i >= 9999:  # Sample first 10k
                        break

            lengths = [len(seq) for seq in sequences]
            qualities = [sum(seq.letter_annotations['phred_quality']) / len(seq) for seq in sequences]

            results = {
                'analysis_scope': 'streaming_sample',
                'sampling': {'method': 'first_records', 'record_limit': 10_000},
                'read_count_sampled': len(sequences),
                'mean_length': sum(lengths) / len(lengths) if lengths else 0,
                'mean_quality': sum(qualities) / len(qualities) if qualities else 0,
                'min_length': min(lengths) if lengths else 0,
                'max_length': max(lengths) if lengths else 0,
            }

    except ImportError as e:
        results['error'] = f"Required library not installed: {e}"
    except Exception as e:
        results['error'] = f"Analysis error: {e}"

    return results


def analyze_chemistry(filepath, extension):
    """Analyze bounded text structure formats without loading full trajectories."""
    if extension == 'pdb':
        atoms = heteroatoms = models = residues = 0
        residue_ids = set()
        with open(filepath, 'rt', errors='replace') as handle:
            for line in handle:
                record = line[:6].strip()
                if record == 'ATOM':
                    atoms += 1
                elif record == 'HETATM':
                    heteroatoms += 1
                elif record == 'MODEL':
                    models += 1
                if record in {'ATOM', 'HETATM'}:
                    residue_ids.add((line[21:22], line[22:26].strip(), line[26:27]))
        residues = len(residue_ids)
        return {'analysis_scope': 'streaming_full_file', 'atom_records': atoms, 'heteroatom_records': heteroatoms, 'models': models or 1, 'residue_positions': residues}
    if extension in {'sdf', 'mol'}:
        records = 0
        with open(filepath, 'rt', errors='replace') as handle:
            for line in handle:
                records += line.rstrip() == '$$$$'
        return {'analysis_scope': 'streaming_full_file', 'molecule_records': records or 1}
    if extension in {'smi', 'smiles', 'xyz'}:
        with open(filepath, 'rt', errors='replace') as handle:
            lines = sum(bool(line.strip()) for line in handle)
        return {'analysis_scope': 'streaming_full_file', 'nonempty_lines': lines}
    return {}


def analyze_spectrometry(filepath, extension):
    """Analyze representative open text/XML mass-spectrometry formats."""
    logical = extension.lower()
    if logical == 'mgf':
        spectra = peaks = 0
        in_spectrum = False
        with open(filepath, 'rt', errors='replace') as handle:
            for line in handle:
                stripped = line.strip()
                if stripped == 'BEGIN IONS':
                    spectra += 1
                    in_spectrum = True
                elif stripped == 'END IONS':
                    in_spectrum = False
                elif in_spectrum and stripped and stripped[0].isdigit() and '=' not in stripped:
                    peaks += 1
        return {'analysis_scope': 'streaming_full_file', 'spectra': spectra, 'peak_rows': peaks}
    if logical == 'mztab':
        counts = {'metadata_rows': 0, 'protein_rows': 0, 'peptide_rows': 0, 'psm_rows': 0, 'small_molecule_rows': 0}
        prefixes = {'MTD': 'metadata_rows', 'PRT': 'protein_rows', 'PEP': 'peptide_rows', 'PSM': 'psm_rows', 'SML': 'small_molecule_rows'}
        with open(filepath, 'rt', errors='replace') as handle:
            for line in handle:
                key = prefixes.get(line[:3])
                if key:
                    counts[key] += 1
        return {'analysis_scope': 'streaming_full_file', **counts}
    if logical in {'mzml', 'mzxml'}:
        import xml.etree.ElementTree as ET
        spectra = chromatograms = 0
        for _, element in ET.iterparse(filepath, events=('end',)):
            tag = element.tag.rsplit('}', 1)[-1].lower()
            spectra += tag in {'spectrum', 'scan'}
            chromatograms += tag == 'chromatogram'
            element.clear()
        return {'analysis_scope': 'streaming_xml', 'spectra': spectra, 'chromatograms': chromatograms}
    return {}


def analyze_imaging(filepath, extension):
    """Analyze microscopy/imaging formats."""
    results = {}

    try:
        if extension in ['tif', 'tiff', 'ome.tif', 'ome.tiff', 'png', 'jpg', 'jpeg']:
            from PIL import Image
            import numpy as np

            img = Image.open(filepath)
            img_array = np.array(img)

            results = {
                'size': img.size,
                'mode': img.mode,
                'format': img.format,
                'shape': img_array.shape,
                'dtype': str(img_array.dtype),
                'value_range': [int(img_array.min()), int(img_array.max())],
                'mean_intensity': float(img_array.mean()),
            }

            # Check for multi-page TIFF
            if extension in ['tif', 'tiff', 'ome.tif', 'ome.tiff']:
                try:
                    frame_count = 0
                    while True:
                        img.seek(frame_count)
                        frame_count += 1
                except EOFError:
                    results['page_count'] = frame_count

    except ImportError as e:
        results['error'] = f"Required library not installed: {e}"
    except Exception as e:
        results['error'] = f"Analysis error: {e}"

    return results


def generate_markdown_report(analysis, output_path=None):
    """
    Generate a bounded markdown report from analysis results.

    Args:
        analysis: Analysis results dictionary
        output_path: Path to save the report (if None, prints to stdout)
    """
    lines = []

    # Title
    filename = analysis['basic_info']['filename']
    lines.append(f"# Exploratory Data Analysis Report: {filename}\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append("---\n")

    # Basic Information
    lines.append("## Basic Information\n")
    basic = analysis['basic_info']
    lines.append(f"- **Filename:** `{basic['filename']}`")
    lines.append(f"- **Full Path:** `{basic['path']}`")
    lines.append(f"- **File Size:** {basic['size_human']} ({basic['size_bytes']:,} bytes)")
    lines.append(f"- **Last Modified:** {basic['modified']}")
    lines.append(f"- **Extension:** `.{analysis['file_type']['extension']}`\n")

    # File Type Information
    lines.append("## File Type\n")
    ft = analysis['file_type']
    lines.append(f"- **Category:** {ft['category'].replace('_', ' ').title()}")
    lines.append(f"- **Description:** {ft['description']}\n")

    # Reference Information
    if analysis.get('reference_info'):
        lines.append("## Format Reference\n")
        ref = analysis['reference_info']
        if 'raw_section' in ref:
            lines.append(ref['raw_section'])
            lines.append(f"\n*Reference: {ref['reference_file']}*\n")

    # Data Analysis
    if analysis.get('data_analysis'):
        lines.append("## Data Analysis\n")
        data = analysis['data_analysis']

        if 'error' in data:
            lines.append(f"**Analysis error:** {data['error']}\n")
        else:
            # Format the data analysis based on what's present
            lines.append("### Summary Statistics\n")
            lines.append("```json")
            lines.append(json.dumps(data, indent=2, default=str))
            lines.append("```\n")

    # Recommendations
    lines.append("## Recommendations for Further Analysis\n")
    lines.append(f"Based on the file type (`.{analysis['file_type']['extension']}`), consider the following analyses:\n")

    # Add specific recommendations based on category
    category = analysis['file_type']['category']
    if category == 'general_scientific':
        lines.append("- Statistical distribution analysis")
        lines.append("- Missing value imputation strategies")
        lines.append("- Correlation analysis between variables")
        lines.append("- Outlier detection and handling")
        lines.append("- Dimensionality reduction (PCA, t-SNE)")
    elif category == 'bioinformatics_genomics':
        lines.append("- Sequence quality control and filtering")
        lines.append("- GC content analysis")
        lines.append("- Read alignment and mapping statistics")
        lines.append("- Variant calling and annotation")
        lines.append("- Differential expression analysis")
    elif category == 'microscopy_imaging':
        lines.append("- Image quality assessment")
        lines.append("- Background correction and normalization")
        lines.append("- Segmentation and object detection")
        lines.append("- Colocalization analysis")
        lines.append("- Intensity measurements and quantification")

    lines.append("")

    # Footer
    lines.append("---")
    lines.append("*This report was generated by the exploratory-data-analysis skill.*")

    report = '\n'.join(lines)

    if output_path:
        with open(output_path, 'w') as f:
            f.write(report)
        print(f"Report saved to: {output_path}")
    else:
        print(report)

    return report


def build_parser():
    parser = argparse.ArgumentParser(
        description='Inspect a supported scientific data file and write a Markdown report.'
    )
    parser.add_argument('filepath', type=Path, help='Scientific data file to inspect')
    parser.add_argument('output', nargs='?', type=Path, help='Markdown output path')
    return parser


def main(argv=None):
    """Run the command-line interface."""
    args = build_parser().parse_args(argv)
    filepath = args.filepath
    output_path = args.output

    if not filepath.is_file():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return 1

    # If no output path specified, use the input filename
    if output_path is None:
        extension, _, _ = detect_file_type(filepath)
        suffix = f'.{extension}' if extension else ''
        report_stem = filepath.name[:-len(suffix)] if suffix else filepath.name
        output_path = filepath.parent / f"{report_stem}_eda_report.md"

    print(f"Analyzing: {filepath}")
    analysis = analyze_file(filepath)

    print("\nGenerating report...")
    generate_markdown_report(analysis, output_path)

    print("\nAnalysis complete.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
