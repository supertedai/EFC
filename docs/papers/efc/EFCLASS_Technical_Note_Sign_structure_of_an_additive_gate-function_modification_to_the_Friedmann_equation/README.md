# EFCLASS Technical Note I: Sign Structure of an Additive Gate-Function Modification to the Friedmann Equation

Analytical proof and numerical verification that the EFC background gate under E(0) = 1 normalisation produces strictly non-positive ΔE² at all z > 0, ruling out background-level σ₈ suppression.

**DOI:** 10.6084/m9.figshare.31333414

**Date:** February 13, 2026

## Summary

**Lemma 1 (Sign of ΔE²):** Under closure normalisation E(0) = 1 with A > 0 and monotonically activating gate:

> ΔE²(z) = A[g(z) − g(0)] ≤ 0 for all z > 0

**Corollary:** H_EFC(z) ≤ H_ΛCDM(z), reducing Hubble friction and **enhancing** structure growth. Background-level EFC cannot suppress σ₈.

## Contents

| File | Description |
|------|-------------|
| `efclass_companion_note.pdf` | Authoritative PDF (6 pages) |
| `index.json` | Machine-readable metadata and results |
| `schema.json` | JSON Schema validation |
| `EFCLASS-Sign-Structure.jsonld` | JSON-LD semantic metadata |
| `metadata.json` | Comprehensive project metadata |
| `citations.bib` | BibTeX references |
| `README.md` | This file |

## Core Equations

- **Standard Friedmann:** E²(z) = Ω_r(1+z)⁴ + Ω_m(1+z)³ + Ω_Λ
- **EFC modified:** E²_EFC(z) = Ω_r(1+z)⁴ + Ω_m(1+z)³ + Ω'_Λ + A g(z)
- **Gate function:** g(z) = 1/(1 + (a_t/a)^n)
- **Closure:** Ω'_Λ = Ω_Λ − A g(0)
- **Sign lemma:** ΔE²(z) = A[g(z) − g(0)] ≤ 0

## Numerical Verification (CLASS v3.3.4)

Parameters: A = 0.15, z_t = 1.01, n = 6, h = 0.674, ω_b = 0.02237, ω_cdm = 0.1200

| z | ΔH/H [%] | Sign OK |
|---|----------|---------|
| 0.3 | −0.291 | Yes |
| 0.5 | −0.569 | Yes |
| 1.0 | −1.124 | Yes |
| 2.0 | −0.739 | Yes |
| 5.0 | −0.107 | Yes |

Agreement < 0.3% at all redshift points. Sign is negative everywhere.

## Growth Signature

| z | fσ₈(ΛCDM) | fσ₈(EFC) | Change |
|---|-----------|----------|--------|
| 0.38 | 0.4749 | 0.4773 | +0.50% |
| 0.51 | 0.4731 | 0.4762 | +0.65% |
| 0.61 | 0.4679 | 0.4715 | +0.76% |

Growth is **enhanced** — the opposite direction from S₈ tension amelioration.

## CLASS Patch (77 lines)

| File | Modification | Lines |
|------|-------------|-------|
| `background.h` | Parameters + index | +9 |
| `background.c` | Gate functions + density + output | +35 |
| `input.c` | Parsing + closure adjustment | +33 |

## Citation

```bibtex
@misc{magnusson2026sign,
  author = {Magnusson, Morten},
  title  = {Sign structure of an additive gate-function modification to the Friedmann equation},
  year   = {2026},
  doi    = {10.6084/m9.figshare.31333414}
}
```

Version: 1.0
