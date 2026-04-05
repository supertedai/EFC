# Cross-Domain Bridge Equations for the EFC Framework: Connecting Cosmology, Neural Entropy, and RLHF

**Author:** Morten Magnusson  
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)  
**DOI:** [10.6084/m9.figshare.31940547](https://doi.org/10.6084/m9.figshare.31940547)  
**Date:** April 2026 (v0.2)

## Summary

Two formal bridge equations connect EFC's three tracks via dissipative gradient-flow dynamics. Bridge B1 maps cosmological entropy-production density onto a neural analogue using local degree heterogeneity. Bridge B2 maps the neural entropy tensor onto RLHF reward-landscape curvature. Both instantiate a single universal dynamics: dF/dt = -integral |nabla s_dot|^2 dV + B, with dF/dt <= 0.

## Unified Dynamical Postulate (Eq. 2)

dF/dt = -integral_Omega |nabla s_dot(x,t)|^2 dV + B[s_dot]

F = Helmholtz free energy (Lyapunov functional for all three regimes).

## Bridge B1: Cosmology -> Neural (Revised B1**)

eta = C_eff / D_ratio^gamma

- D_ratio = <k_hub> / <k_periph> (hub-to-periphery degree ratio)
- C_eff = kappa * C = kappa * k / a_G ~ 1.9-2.2
- gamma ~ 0.5-0.6 (empirical)
- Replaces Fiedler eigenvalue (r~0.16) with degree ratio (r~-0.97)

## Bridge B2: Neural -> RLHF (Eq. 10-11)

nabla S_neural  <->  nabla^2 R(s,a)
S_neural / (k_B * T_cog)  <->  H(pi_theta | s)

## Three Cross-Domain Predictions

1. **P4**: eta = C_eff / D_ratio^gamma; no free parameters (HCP SC + MSE test)
2. **P5**: T_cog from fMRI calibrates optimal beta_KL without grid search
3. **P6**: DMN entropy-gradient topology <-> reward landscape curvature in trained LLMs

## File Structure

```
├── README.md, index.json, schema.json, metadata.json
├── bridge_equations.jsonld, citations.bib
├── src/bridge_equations.py    # Python implementation
├── data/bridge_mappings.json  # Observable dictionary and mappings
└── examples/demo_bridge.py    # Executable demonstration
```
