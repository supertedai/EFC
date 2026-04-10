# Scale-Localised Modified Gravity from the EFC Action

**A Single-Parameter Forecast via E_G(k,z)**

Author: Morten Magnusson (ORCID [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095))
Symbiose Research, Sandnes, Norway | April 2026 — v1.1
DOI: [10.6084/m9.figshare.31985313](https://doi.org/10.6084/m9.figshare.31985313)
License: CC-BY-4.0

---

## TL;DR

| Aspect | Value |
|--------|-------|
| **Model** | Band-pass stiffness response R(k,a) localises gravity modification to k ~ k_c |
| **Free parameter** | eps_tot in [0.38, 0.42] (slip amplitude from delta-Lambda counter-term) |
| **Characteristic scale** | k_c = 0.05 h/Mpc |
| **Key observables** | mu < 1 (suppressed growth), eta > 1 (anisotropic potentials), Sigma > 1 (enhanced lensing) |
| **Reference point** | (k_c, z=0): mu=0.940, eta=1.200, Sigma=1.034 |
| **Definitive test** | E_G(k) bump of ~7% at k ~ k_c, testable at 2.5-3.5 sigma with DESI x Planck |
| **Joint chi-squared** | Delta-chi^2 = +1.4 (EFC marginal preference) |
| **Category** | Structural / forecast (not a validation report) |

## Abstract

Single-parameter, directly falsifiable test of scale-localised modified gravity derived from
the EFC relativistic action. The model modifies perturbation growth and lensing through a
band-pass stiffness response R(k) that peaks at k_c = 0.05 h/Mpc and vanishes in IR and UV
limits, recovering GR on super-horizon and galactic scales. Combined with gravitational slip
from the delta-Lambda counter-term, this yields mu < 1, eta > 1, and Sigma > 1 — simultaneously
satisfying the No-Go constraint on background modifications, BOSS full-shape P(k), CMB ISW
limits, and Planck perturbation-sector tests. The entire model reduces to a single effective
parameter eps_tot controlling slip amplitude, with a viable window eps_tot in [0.38, 0.42].

## Key Equations

1. **Stiffness response:** R(k,a) = R_0 * (k/k_c)^2 / (1 + (k/k_c)^2)^3 * a^4
2. **Effective coupling:** mu(k,z) = 1 / (F * (1 + R(k,a)))
3. **Gravitational slip:** eta(k,z) = 1 + 2 * eps_tot * (k/k_c)^2 / (1 + (k/k_c)^2)^2 * a^2
4. **Lensing combination:** Sigma(k,z) = mu * (1 + eta) / 2
5. **E_G statistic:** E_G(k,z) = (Omega_m,0 / f(z)) * (Sigma(k,z) / mu(k,z))

## Observational Tests (Table 1)

| Test | Delta-chi^2 | Precision | Status |
|------|------------|-----------|--------|
| BOSS P(k) shape | -0.07 | ~3%/bin | PASS |
| CMB ISW (low-l) | — | ~10% | PASS (8%) |
| CMB lensing A_lens | +3.3 | 5.5% | EFC better |
| KiDS shear S_WL | +0.04 | 2.5% | Neutral |
| E_G (current) | -1.9 | ~15% | GR preferred |
| **Joint (net)** | **+1.4** | — | **EFC marginal** |

## AI-Friendly Package Contents

- `index.json` — Machine-readable structured metadata
- `metadata.json` — Extended metadata
- `schema.json` — JSON Schema for key data objects
- `*.jsonld` — Schema.org linked data
- `citations.bib` — BibTeX references
- `data/` — Observational tests and E_G predictions as JSON
- `src/` — Python implementation of band-pass model
- `examples/` — Demo script reproducing key results
