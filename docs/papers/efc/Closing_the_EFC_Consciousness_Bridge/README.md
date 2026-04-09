# Closing the EFC Consciousness Bridge

**Report ID:** EFC-VAL-2026-007
**DOI:** [10.6084/m9.figshare.31969983](https://doi.org/10.6084/m9.figshare.31969983)
**Author:** Morten Magnusson (ORCID 0009-0002-4860-5095)
**Affiliation:** Symbiose Research, Sandnes, Norway
**Date:** April 2026
**License:** CC-BY-4.0

## TL;DR

Closes the open bridge between the cosmological entropy field S (EFC field
equation) and the EFC-C cognitive variables (spectral differentiation Omega,
causal integration kappa). Three structural problems resolved:

| Problem | Resolution | Equation |
|---------|-----------|----------|
| C = Omega*kappa is separable | Non-separable functional C = Omega_hat * kappa_hat * (1 - exp(-gamma * Omega_hat * kappa_hat)) | (III) |
| No dynamics for Omega_dot, kappa_dot | Coupled ODEs: entropic drift + diffusion for Omega_hat; energy-flow source + suppression for kappa_hat | (I), (II) |
| No dimensional connection S <-> (Omega, kappa) | Regime-indexed dimensionless variables Omega_hat_l = S(rho)/S_l, kappa_hat_l = (alpha_l/rho_l)|grad(delta S/delta rho)| | Eqs 3-4 |

## Three-Equation System

```
(I)   d Omega_hat / dt = -lambda_Omega * grad(delta S / delta rho) + D_Omega * Laplacian(Omega_hat)
(II)  d kappa_hat / dt = J_flow - mu * kappa_hat * Omega_hat
(III) C = Omega_hat * kappa_hat * (1 - exp(-gamma * Omega_hat * kappa_hat))
```

## Parameter Count

| Symbol | Meaning | Source | Status |
|--------|---------|--------|--------|
| alpha_l | Entropy coupling | EFC field eq. | Constrained |
| K | Cross-domain constant | SPARC / B1* | 4.4 +/- 0.6 |
| gamma | Non-separable coupling | New | **Free** |
| lambda_Omega | Drift strength (= alpha_l) | Inherited | Inherited |
| D_Omega | Diffusion coefficient | System-specific | Measurable |
| mu | Damping rate | System-specific | Measurable |

**One genuinely free parameter** (gamma). All others inherited from existing
EFC constraints or measurable from data.

## Existing Empirical Support (Propofol Sedation EEG)

| Observable | Model predicts | Observed | Status |
|-----------|---------------|----------|--------|
| Omega waking > sedated | Omega_hat increases with \|grad S\| | d = 1.50 | Supported |
| kappa waking < sedated | kappa_hat proportional to 1/Omega_hat | Anti-corr. r = -0.27 | Supported |
| C = Omega*kappa (global) | Separable product fails | F1 falsified, p = 0.43 | Supported |
| C_parietal | Regional C > 0 | d = 2.10, p = 0.018 | Supported |
| Double dissociation | Omega tracks awareness | Resp. +0.054, drowsy -0.063 | Supported |

Five out of five directional predictions consistent with existing data. These
do not constitute a direct test of the full model but confirm qualitative
structure.

## Kill Conditions

1. corr(Omega_hat, kappa_hat) > 0 in confirmed conscious states
2. C increases monotonically with Omega_hat without kappa_hat-suppression
3. Cortical entropy gradient shows no correlation with consciousness level
   across anaesthesia depths
4. Cross-domain constant K inconsistent between galactic and neural data at > 3 sigma

## Files

| File | Description |
|------|-------------|
| `Closing_the_EFC_Consciousness_Bridge.pdf` | Full paper (9 pages) |
| `index.json` | Machine-readable structured summary |
| `metadata.json` | Domain, equations, parameters, links |
| `schema.json` | JSON schema for result objects |
| `closing-the-efc-consciousness-bridge.jsonld` | Schema.org linked data |
| `citations.bib` | BibTeX references |
| `data/regime_mapping.json` | Table 1: regime characteristic scales |
| `data/propofol_consistency.json` | Table 4: empirical vs model predictions |
| `src/consciousness_bridge.py` | Three-equation system implementation |
| `examples/evaluate_bridge.py` | Demo: evaluate C across regimes and states |

## Reproduction

```bash
cd docs/papers/efc/Closing_the_EFC_Consciousness_Bridge
python examples/evaluate_bridge.py
```

## Related Artifacts

- EFC-C Consciousness Field Resonance: [10.6084/m9.figshare.31289806](https://doi.org/10.6084/m9.figshare.31289806)
- CEM-Cosmos: [10.6084/m9.figshare.30275947](https://doi.org/10.6084/m9.figshare.30275947)
- EFC Field Equations: [10.6084/m9.figshare.30421807](https://doi.org/10.6084/m9.figshare.30421807)
- SPARC Mass Models (Lelli et al. 2016): AJ 152, 157

## Language Discipline

This package uses "consistent with" and "supported" to describe the
relationship between model predictions and propofol sedation data. The
existing EEG results are partial support for qualitative structure, not a
direct test of the full three-equation model. The construction is
falsifiable via the kill conditions above. No claim of "confirmation" or
"proof" is made.
