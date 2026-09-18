---
title: SPARC 175 Galaxy Database + EFC-R Analysis
type: foundational
date: '2026-01-10'
tags:
- analysis
- database
- efc
- galaxy
- model
source_path: docs/data/sparc-175/README.md
---

# SPARC 175 Galaxy Database + EFC-R Analysis

## Overview

Complete dataset from the SPARC database (175 galaxies) with integrated EFC-R methodology for rotation-curve analysis.

## Sources

| Source | Reference |
|-------|-----------|
| SPARC Database | https://astroweb.case.edu/SPARC/ |
| SPARC Paper | Lelli+2016 (DOI: 10.3847/0004-6256/152/6/157) |
| EFC-R Paper | Magnusson 2026 (DOI: 10.6084/m9.figshare.31007248) |

## Contents

### Dataset (from SPARC)
```
rotation_models/     # 175 rotation curves (.dat)
photometry/          # 219 photometry profiles
bulge_disk/          # 177 bulge/disk decompositions
archives/            # Original zip files
```

### Main tables
| File | Description |
|-----|-------------|
| Table1_Galaxy_Sample.mrt | 175 galaxies with properties |
| Table2_Mass_Models.mrt | Rotation curves + baryonic contributions |
| Radial_Acceleration_Relation_*.mrt | RAR data (2630 points) |
| Baryonic_Tully_Fisher_*.mrt | BTFR data |

### Analyses
| File | Content |
|-----|---------|
| EFC-R_METHOD.md | EFC-R methodology |
| efc_r_n20_results.json | Results from the N=20 analysis |
| N175_ANALYSIS_PLAN.md | Plan for the extended analysis |
| ANALYSIS_REPORT.md | Complete analysis report |

## EFC-R Status

| Metric | N=20 | Expected N=175 |
|---------|------|-----------------|
| Success rate | 80% | 75-85% |
| Mean ∇S | 0.082 kpc⁻¹ | ~0.08 kpc⁻¹ |
| Overlap with N=175 | - | 19 galaxies |
| New galaxies | - | 156 galaxies |

## Usage

```python
# Read rotation curve
import numpy as np
data = np.loadtxt('rotation_models/NGC2403_rotmod.dat')
r, v_obs, v_err, v_gas, v_disk, v_bul, sb = data.T
```

## Related projects

- **sparc-n20**: Original EFC-R analysis (published)
- **sparc-n175**: Extended analysis (in progress)
- **halo-model**: Entropy-halo predictions

---
*Last updated: 2026-01-10*
