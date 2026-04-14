# Sign structure of an additive gate-function modification to the Friedmann equation

## AI-Friendly Package

- **DOI:** [10.6084/m9.figshare.31333414](https://doi.org/10.6084/m9.figshare.31333414)
- **Version:** 1.0
- **Author:** Morten Magnusson (ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095))
- **Date:** 2026-02-13
- **License:** CC-BY-4.0

---

## Overview

Analytical proof and numerical verification (in CLASS v3.3.4) that an additive, monotonically activating EFC gate g(z) with positive amplitude A, when closed by enforcing E(0)=1 via Ω'Λ=ΩΛ−Ag(0), yields a strictly non-positive ΔE²(z)=A[g(z)−g(0)] for all z>0. The sign-lock reduces Hubble friction and necessarily enhances structure growth, implying background-only EFC cannot suppress σ8; CLASS results agree with the analytical prediction at the <0.3% level across nine redshifts.

## Key Result

Under E(0)=1 closure with A>0 and a monotonically activating gate, ΔE²(z)≤0 for all z>0, reducing Hubble friction and increasing fσ8; CLASS verifies the analytic ΔH²=A[g(z)−g(0)]H0² with ≤0.3% discrepancy across nine redshifts.

## Sealed Predictions

| ID | Prediction | Falsifiable by |
|---|---|---|
| P1 | For any positive A and monotonically non-decreasing gate g(a) closed by Ω'Λ=ΩΛ−Ag(0), the background-only EFC model necessarily yields Δfσ8(z)>0 relative to ΛCDM over late times (z≈0.3–1), independent of (A, z_t, n) values. | Independent Boltzmann/ODE implementation (e.g., CAMB or custom solver) showing Δfσ8≤0 for A>0, monotone g, and μ=1 under E(0)=1 closure. |
| P2 | With E(0)=1 closure, ΔE²(z)=A[g(z)−g(0)] must be non-positive for all z>0 when A>0 and g is monotone in a. | Direct numerical evaluation of H(z) from the modified background equations producing any ΔE²(z)>0 at z>0 under the stated conditions. |
