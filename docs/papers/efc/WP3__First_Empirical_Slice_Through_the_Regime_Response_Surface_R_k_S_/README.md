# WP3: First Empirical Slice Through the Regime Response Surface R(k,S)

**First empirical mapping of gravitational response along the RSD trajectory**

---

## Overview

First entry in the EFC Response Atlas. Maps one trajectory through R(k,S) space using fσ₈ measurements from BOSS, eBOSS, and DESI.

**DOI**: [10.6084/m9.figshare.31215259](https://doi.org/10.6084/m9.figshare.31215259)

---

## Key Result

```
R(k ≈ 0.13 h/Mpc, S ≈ 0.30) ≈ +0.30
```

| Model | χ² | AIC | Verdict |
|-------|-----|-----|---------|
| ΛCDM (R=0) | 9.36 | 15.4 | **Preferred** |
| R(k,S) slice | 9.12 | 19.1 | Allowed but penalized |

**Interpretation**: Data consistent with zero response within complexity penalty. This is cartography, not validation.

---

## Data Used

- **BOSS DR12**: z = 0.38, 0.51, 0.61
- **eBOSS DR16**: z = 0.70, 0.85, 1.48
- **DESI Y1**: z = 0.295, 0.510, 0.706, 0.930, 1.184, 1.491
- **Total**: N = 12 measurements

---

## WP3 Trajectory Coverage

| Parameter | Range |
|-----------|-------|
| k (wavenumber) | 0.1 – 0.13 h/Mpc |
| S (structural maturity) | 0.3 – 0.7 |
| z (redshift) | 0.3 – 1.5 |

---

## Response Atlas Roadmap

| Probe | k window | S range | Status |
|-------|----------|---------|--------|
| RSD / fσ₈ | ~0.1 h/Mpc | [0.3, 0.7] | **WP3 (this work)** |
| Weak lensing | different k | overlapping S | WP4 (ready) |
| Clusters | smaller k | higher S | Planned |
| CMB | large scales | S ≈ 0 | Boundary condition |

---

## Dependencies

- [R(k,S) Framework Paper](https://doi.org/10.6084/m9.figshare.31211437)

---

## Files

| File | Description |
|------|-------------|
| `wp3_rks_article.pdf` | Authoritative PDF |
| `wp3_rks_article.tex` | LaTeX source |
| `wp3_rks_final.png` | Main results figure |
| `rks_wp3_trajectory.png` | Trajectory visualization |
| `wp3_v1_clean.png` | Clean data plot |

---

**Version**: 1.0 | **Date**: 30 January 2026 | **Author**: Morten Magnusson
