# Minimal EFC Effective Field Theory Ansatz

**Scalar-Tensor and Vector-Tensor Formulations with Gravitational Slip from Entropy Gradients**

| Field | Value |
|-------|-------|
| Author | Morten Magnusson |
| ORCID | 0009-0002-4860-5095 |
| Version | Research Note v6 — March 6, 2026 |
| DOI | 10.6084/m9.figshare.31368433 |
| Status | Proposed EFT completion (not canonical baseline EFC-D) |

## Quick Start

```python
from src.efc_eft_ansatz import EntropyField, ScalarTensorEFT, VectorTensorEFT, TargetSignature

# Entropy sigmoid
S = EntropyField(a_t=0.30, Delta=0.3)
print(f"S(a=0.5) = {S(0.5):.4f}")

# Scalar-tensor alpha functions
st = ScalarTensorEFT(B0=1.0, M0=1.0, a_t=0.30, Delta=0.3)
print(f"alpha_B(0.5) = {st.alpha_B(0.5):.4f}")
print(f"alpha_M(0.5) = {st.alpha_M(0.5):.4f}")

# Target signature
target = TargetSignature()
print(f"Required slip: eta > {target.eta_required:.2f}")
```

## Summary

This note constructs two minimal EFT ansatze for Energy-Flow Cosmology:

### EFC Target Signature
All three conditions must hold simultaneously in the transition regime (0.5 < z < 1.5):

| Observable | GR value | EFC target | Mechanism |
|------------|----------|------------|-----------|
| mu(a) | 1 | ~0.925 | Weakened gravity (growth suppression) |
| eta(a) = Phi/Psi | 1 | >1.2 | Gravitational slip from entropy gradients |
| Sigma(a) | 1 | >1 | Enhanced lensing; Sigma = mu(1+eta)/2 |

### Ansatz I: Scalar-Tensor (Horndeski)
- Maps EFC to Bellini-Sawicki alpha-parameter basis
- alpha_T = 0 (GW170817 constraint)
- alpha_B(a) proportional to dS/d(ln a) (braiding from entropy gradient)
- alpha_M(a) proportional to S(a) (running Planck mass)
- Free parameters: {B0, M0, a_t, Delta}
- Immediately testable via hi_class

### Ansatz II: Vector-Tensor (Energy Flow)
- Dynamical 4-vector J^mu represents physical energy flow
- Anisotropic stress: pi ~ beta^2 (nabla S)^2 generates Phi != Psi
- Slip estimate: eta - 1 ~ C_eta beta^2 (nabla S_bar)^2 / (k^2 rho_eff)
- Free parameters: {beta, m^2, a_t, Delta}
- Ontologically natural EFC completion

### EFC Entropy Field
Sigmoid in log scale-factor:

```
S(a) = [1 + exp(-(ln a - ln a_t) / Delta)]^{-1}
```

- a_t ≈ 0.30 (z_t ≈ 2.3)
- Delta ≈ 0.3
- S → 0 at high z (GR recovery)
- S → 1 today (maximum modification)

### Key Equations

| Eq | Expression | Description |
|----|-----------|-------------|
| (5) | eta = Phi/Psi | Gravitational slip (GR: eta=1) |
| (7) | Sigma = mu(1+eta)/2 | Lensing function |
| (8) | eta > 2*Sigma/mu - 1 | Constraint for Sigma > 1 with mu < 1 |
| (13) | mu(a) = 1 + delta_mu * S(a) | Growth-function ansatz (delta_mu ~ -0.075) |
| (14) | L_EFC^(S) = M_Pl^2/2 R + K(S,X) + G3(S,X) box S | Scalar-tensor action |
| (18) | L_EFC^(J) = M_Pl^2/2 R - F^2/4 - m^2 J^2/2 + beta J.nabla S | Vector-tensor action |
| (21) | eta-1 ~ C_eta beta^2 (nabla S_bar)^2 / (k^2 rho_eff) | Slip from entropy gradient |
| (24) | eta > 2*Sigma/mu - 1 ~ 1.24 | Required slip for mu=0.925, Sigma=1.05 |

### Stability Conditions
- Scalar-tensor: Q_S = alpha_K + 3/2 alpha_B^2 > 0 (no ghost), c_S^2 > 0 (no gradient instability)
- Vector-tensor: m^2 > 0 (no tachyon), beta^2 < beta_max^2 (no ghost)

### Falsification Criterion
If no parameter region {B0, M0, a_t, Delta} exists with mu < 1, eta > 1, Sigma > 1 simultaneously under stability + CMB + LSS constraints in hi_class, the scalar-tensor ansatz is falsified.

### Open Numerical Questions
1. Does {B0, M0} region exist with mu < 1, eta > 1, Sigma > 1 simultaneously?
2. Are stability conditions satisfied across the sigmoid transition?
3. What is the precise coefficient C_eta in the vector-tensor slip?
4. Does J^mu action reduce to scalar EFT in isotropic quasi-static limit?

## Caveats
- This is a *proposed* EFT completion, not canonical baseline EFC-D
- mu(k,z) and Sigma(k,z) remain outside canonical baseline pending derivation
- Numerical verification via hi_class/Boltzmann code is required
- Vector-tensor requires new Boltzmann code implementation

## File Manifest
| File | Description |
|------|-------------|
| `index.json` | Machine-readable metadata and equations |
| `schema.json` | JSON Schema for validation |
| `metadata.json` | Package metadata |
| `EFC-EFT-Ansatz.jsonld` | Schema.org linked data |
| `citations.bib` | BibTeX references |
| `src/efc_eft_ansatz.py` | Reference implementation |
| `data/eft_parameters.json` | Parameter tables and comparison |
| `examples/eft_demo.py` | Runnable demo |
