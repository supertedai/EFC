# Energy-Flow Cosmology: Empirical Validation of the EFC Screening Model Against the Radial Acceleration Relation

**Author:** Morten Magnusson  
**Affiliation:** Symbiose Research, Sandnes, Norway  
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)  
**DOI:** [10.6084/m9.figshare.31940469](https://doi.org/10.6084/m9.figshare.31940469)  
**Date:** March 2026 (Version 2.0)  
**Framework:** Energy-Flow Cosmology (EFC)

## Summary

Multi-scale empirical validation of the EFC screening model across four observational domains:

1. **SPARC RAR** (174 galaxies, 3264 points): ln mu = k ln(1 + g†/g_bar) with k = 0.415 +/- 0.029, g† = (2.51 +/- 0.60) x 10^-10 m/s^2, sigma_int ~ 0.14 dex
2. **Cross-scale consistency**: Phase-gain C = k/a_G = 4.4 +/- 0.6 connects galactic and cosmological scales
3. **KiDS-1000 lensing**: Regime-activated response improves fit by Delta(-2 ln L) = -50.9 vs LCDM
4. **Bullet Cluster**: Entropy-gradient interpretation produces correct lensing offset direction (qualitative)
5. **Hubble tension**: a_G = 0.094 independently derived from both k (galactic) and H0 (cosmological)

## Key Equations

| Equation | Formula | Source |
|----------|---------|--------|
| Screening form | ln mu = k ln(1 + g†/g_bar) | Eq. (1) |
| Lensing power | P_EFC = P_LCDM x Sigma^2(k,z) | Eq. (4) |
| Effective potential | Phi_eff = Phi_N + alpha nabla S | Eq. (5) |
| Hubble coupling | a_H0 = (1/2) a_G | Eq. (7) |
| Closure: g† | g† = c H0 / e | Eq. (11) |
| Closure: C | C = 2e - 1 ~ 4.44 | Eq. (12) |

## Falsification Criteria

1. k outside [0.30, 0.55] from independent SPARC re-analysis
2. g† inconsistent with cH0/e at >3 sigma
3. No lensing response Sigma(k,z) in Stage-IV data (Euclid, LSST)
4. C = k/a_G inconsistent with 2e-1 at >3 sigma
5. Bullet Cluster offset explained without entropy-gradient coupling

## File Structure

```
├── README.md                 # This file
├── index.json                # Machine-readable index
├── schema.json               # Validation schema
├── metadata.json             # Structured metadata
├── efc_screening.jsonld      # JSON-LD linked data
├── citations.bib             # BibTeX references
├── src/
│   ├── __init__.py
│   └── efc_screening.py      # Python implementation
├── data/
│   └── results.json          # Fitted parameters and cross-scale results
└── examples/
    └── demo_screening.py     # Executable demonstration
```
