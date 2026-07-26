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

## Oversikt

Komplett datasett fra SPARC-databasen (175 galakser) med integrert EFC-R metodikk for rotasjonskurve-analyse.

## Kilder

| Kilde | Referanse |
|-------|-----------|
| SPARC Database | https://astroweb.case.edu/SPARC/ |
| SPARC Paper | Lelli+2016 (DOI: 10.3847/0004-6256/152/6/157) |
| EFC-R Paper | Magnusson 2026 (DOI: 10.6084/m9.figshare.31007248) |

## Innhold

### Datasett (fra SPARC)
```
rotation_models/     # 175 rotasjonskurver (.dat)
photometry/          # 219 fotometri-profiler
bulge_disk/          # 177 bulge/disk-dekomposisjoner
archives/            # Original zip-filer
```

### Hovedtabeller
| Fil | Beskrivelse |
|-----|-------------|
| Table1_Galaxy_Sample.mrt | 175 galakser med egenskaper |
| Table2_Mass_Models.mrt | Rotasjonskurver + baryoniske bidrag |
| Radial_Acceleration_Relation_*.mrt | RAR data (2630 punkter) |
| Baryonic_Tully_Fisher_*.mrt | BTFR data |

### Analyser
| Fil | Innhold |
|-----|---------|
| EFC-R_METHOD.md | EFC-R metodikk |
| efc_r_n20_results.json | Resultater fra N=20 analyse |
| N175_ANALYSIS_PLAN.md | Plan for utvidet analyse |
| ANALYSIS_REPORT.md | Komplett analyserapport |

## EFC-R Status

| Metrikk | N=20 | Forventet N=175 |
|---------|------|-----------------|
| Suksessrate | 80% | 75-85% |
| Mean ∇S | 0.082 kpc⁻¹ | ~0.08 kpc⁻¹ |
| Overlapp med N=175 | - | 19 galakser |
| Nye galakser | - | 156 galakser |

## Bruk

```python
# Les rotasjonskurve
import numpy as np
data = np.loadtxt('rotation_models/NGC2403_rotmod.dat')
r, v_obs, v_err, v_gas, v_disk, v_bul, sb = data.T
```

## Relaterte prosjekter

- **sparc-n20**: Original EFC-R analyse (publisert)
- **sparc-n175**: Utvidet analyse (pågående)
- **halo-model**: Entropi-halo prediksjoner

---
*Sist oppdatert: 2026-01-10*
