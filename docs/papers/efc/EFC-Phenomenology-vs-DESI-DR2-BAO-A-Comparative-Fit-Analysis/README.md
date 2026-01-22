# EFC DESI Technical Note

**EFC Phenomenology vs DESI DR2 BAO: A Comparative Fit Analysis**

## Overview

This repository contains the technical note comparing an Energy-Flow Cosmology (EFC) inspired dark energy parameterization against DESI DR2 BAO measurements.

## Key Results

| Model | χ² | Δχ² vs ΛCDM | Assessment |
|-------|-----|-------------|------------|
| ΛCDM | 23.71 | — | Poor fit |
| w₀wₐCDM (DESI) | 4.49 | −19.22 | Good fit |
| EFC (best-fit) | 3.60 | −20.11 | Best fit* |

*Within the models tested.

## EFC Best-Fit Parameters

- `w_late = −0.80` (dark energy equation of state today)
- `w_early = −1.41` (at high z)
- `z_trans = 1.07` (transition redshift)

## EFC w(z) Form

```
w(z) = w_late + (w_early − w_late) · tanh[(z − z_trans)/Δz]
```

## Files

- `EFC_DESI_Technical_Note.tex` — LaTeX source
- `metadata.json` — Machine-readable metadata
- `codemeta.json` — CodeMeta for software/data citation
- `schema.jsonld` — JSON-LD structured data (Schema.org)
- `CITATION.cff` — Citation File Format

## Author

**Morten Magnusson**  
ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)

## Data Sources

- DESI DR2: [doi:10.5281/zenodo.14733025](https://doi.org/10.5281/zenodo.14733025)

## License

CC-BY-4.0
