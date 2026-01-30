# Energy-Flow Cosmology: Unified Analysis of BAO, SN Ia, and RSD

**First regime-consistency check with derived effective gravitational coupling**

---

## Overview

Unified cosmological analysis testing EFC against combined BAO, SN Ia, and RSD observations. The effective gravitational coupling μ(a) is **derived** from EFC field equations, not phenomenologically fitted.

**DOI**: [10.6084/m9.figshare.31215613](https://doi.org/10.6084/m9.figshare.31215613)

---

## Core Equations

**EFC Field Equation:**
```
G_μν = 8πG(T_μν + T^(Ef)_μν) + Λ_eff g_μν
```

**Effective Gravitational Coupling:**
```
μ(a) = G_eff/G = 1 + βS(a)
```

**Entropy Field Evolution:**
```
S(a) = (S_∞/2)[1 + tanh((ln a - ln a_t)/σ)]
```

---

## Key Results

| Model | BAO χ² | SN χ² | RSD χ² | Total χ² |
|-------|--------|-------|--------|----------|
| ΛCDM | 9.81 | 28.98 | 10.56 | 49.35 |
| EFC (β=0.16) | 9.81 | 28.98 | 12.28 | 51.06 |
| **Δχ²** | 0.00 | 0.00 | +1.72 | +1.71 |

**Interpretation**: EFC achieves identical BAO/SN fits, slightly worse RSD (within statistical fluctuations). No internal tension between geometry and growth probes.

---

## EFC Parameters

| Parameter | Value | Meaning |
|-----------|-------|---------|
| β | 0.16 | 16% late-time gravity enhancement |
| a_t | 0.55 (z=0.82) | Transition epoch (~7 Gyr ago) |
| σ | 0.10 | Sharp L1→L2 transition |
| γ | 0 | No background modification |

---

## Data Sources

- **BAO**: DESI DR2 (6 points, z = 0.51–2.33)
- **SN Ia**: Pantheon+ (16 binned points, z = 0.01–1.00)
- **RSD**: BOSS DR12 + eBOSS DR16 + DESI Y1 (11 points, z = 0.30–1.52)

---

## Files

| File | Description |
|------|-------------|
| `Energy-Flow-Cosmology-Unified-Analysis-of-BAO.pdf` | Authoritative PDF |
| `efc_unified_preprint.tex` | LaTeX source |
| `EFC_unified_analysis.png` | Combined analysis figure |
| `EFC_mu_theoretical_derivation.png` | μ(a) derivation figure |

---

**Version**: 1.0 | **Date**: January 2026 | **Author**: Morten Magnusson
