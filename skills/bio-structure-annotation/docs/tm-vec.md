# TM-Vec

Fast protein structure embedding and similarity search using transformer-based vector representations.

Last verified: 2026-05-30
Tool version/release checked: TM-Vec 1.0.2
Official docs/manual: https://github.com/tymor22/tm-vec; https://github.com/valentynbez/tmvec
Release/source: https://github.com/tymor22/tm-vec/releases/tag/1.0.2

## Installation

Pin the maintained fork in the project's Pixi environment. The original
`tymor22/tm-vec` repository points users to `valentynbez/tmvec` for continued
maintenance.

### Download Model Weights
Required for embedding generation:
```bash
mkdir Rostlab && cd Rostlab
wget https://zenodo.org/record/4644188/files/prot_t5_xl_uniref50.zip
unzip prot_t5_xl_uniref50.zip
cd ..
```

## Available Models

| Model | Max Length | Training Set | Use Case |
|-------|-----------|--------------|----------|
| `tmvec_swiss_model` | 300 residues | SWISS-PROT | Base model for short sequences |
| `tmvec_swiss_model_large` | 1000 residues | SWISS-PROT | Long sequences, Swiss-Prot searches |
| `tm_vec_cath_model` | 300 residues | CATH S40 | Base model for domain searches |
| `tm_vec_cath_model_large` | 1000 residues | CATH S100 | Long domains, CATH searches |

Models available at: https://figshare.com/s/e414d6a52fd471d86d69

## Pre-built Databases

Download from Zenodo: https://zenodo.org/records/11199459

- **CATH domains database** - Use with `tm_vec_cath_model_large`
- **SWISS-PROT sequences** - Use with `tmvec_swiss_model_large`

Embeddings stored as numpy arrays (.npy format):
```python
import numpy as np
embeddings = np.load('database.npy', allow_pickle=True)
```

## Common Usage

### Build a database

```bash
tmvec build-db --input-fasta references.faa --output tmvec_db/references
```

### Search a database

```bash
tmvec search \
  --query queries.faa \
  --database tmvec_db/references.npz \
  --output tmvec_hits.tsv
```

## Input/Output Formats

- **Input**: Protein sequences in FASTA format
- **Output**:
  - Vector embeddings (numpy arrays)
  - Similarity scores for homology detection
  - Position-indexed metadata linking embeddings to sequences

## Performance Tips

- Use GPU for embedding generation on large datasets
- GPU users may need to reinstall PyTorch separately for optimal compatibility
- Choose model size based on maximum sequence length in dataset
- Pre-embed large databases for repeated searches

## Typical Workflow

1. Pin the maintained TM-Vec fork and model/cache paths.
2. Build or obtain a versioned database.
3. Search queries with `tmvec search`.
4. Preserve the database checksum and filter thresholds with the results.
