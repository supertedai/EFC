# EFC Relativistic Action: Field Equations, Perturbation Theory, and Extraction of mu, Sigma, eta

> **AI-Friendly Paper Package** — structured metadata + reference implementation + runnable demo

## Quick Summary

| Field | Value |
|-------|-------|
| **Authors** | Morten Magnusson |
| **Affiliation** | Energy-Flow Cosmology Initiative |
| **DOI** | 10.6084/m9.figshare.31876324 |
| **Version** | v0.5 (March 2026) |
| **Status** | Working paper |
| **Framework** | EFC (Energy-Flow Cosmology) |
| **Keywords** | EFC action, field equations, perturbation theory, modified gravity, mu-Sigma-eta, gravitational waves, scalar-tensor |

## Core Idea

First self-contained variational derivation of all EFC perturbation-sector predictions from a single action principle. The EFC action couples an entropy-flow scalar field phi non-minimally to gravity via F(phi)R, with density-dependent kinetic stiffness K(rho) and a Lagrange-multiplier flow constraint.

## The EFC Action

```
S_EFC = integral d^4x sqrt(-g) [
    (1/2) M_Pl^2 F(phi) R
  - (1/2) K(rho) g^{mu nu} d_mu phi d_nu phi
  - V(phi)
  - lambda (box phi - Gamma(rho))
]
```

Three departures from GR:
1. **Geometry-information coupling** F(phi)R — entropy field modifies curvature
2. **Kinetic stiffness** K(rho) — cost of moving information diverges at high density (screening)
3. **Flow constraint** lambda(box phi - Gamma) — entropy flow must balance a density ledger

## Key Results

| Quantity | Expression | EFC Prediction | Source |
|----------|-----------|----------------|--------|
| Poisson mu | (1 + eps_F) / [F(1 + R)] | < 1 | K(rho) stiffness |
| Slip eta | 1 + 2(eps_F + eps_lambda + eps_lambda_resp) | > 1 | Flow anisotropy |
| Lensing Sigma | mu(1+eta)/2 | > 1 | Slip compensation |
| GW speed c_T | c (exactly) | = c | No Weyl coupling |
| GW amplitude | d_L^GW != d_L^EM | != 1 | F(phi) friction |

**Typical values**: mu ~ 0.94, Sigma ~ 1.05, eta ~ 1.10

## Key Mechanisms

- **Entropy-stiffness mechanism** (mu < 1): Flow constraint forces delta_phi ~ delta_rho, but large K(rho) makes this costly, creating effective pressure opposing collapse
- **Flow-anisotropy mechanism** (Sigma > 1): Lagrange multiplier generates tensorial stress absent in standard scalar-tensor theories
- **Automatic screening**: K(rho) -> infinity as rho -> rho_crit recovers GR at high densities

## Falsification Conditions

| ID | Condition | Consequence |
|----|-----------|-------------|
| FA1 | R(k,z) < 0 | Stiffness fails; mu > 1 |
| FA2 | Ghost in (delta_phi, delta_lambda) | UV-unstable |
| FA3 | c_T != c | **PASSED**: c_T = c exactly |
| FA4 | eta = 1 identically | No anisotropic stress |
| FA5 | No parameter region for mu in [0.93,0.96], Sigma in [1.03,1.07] | Action doesn't reproduce observations |
| FA6 | |F_dot/F| >= H at z < 2 | GW friction too large |

## Quick Start

```python
from src.efc_relativistic import (
    EFCAction, EFCPerturbations, TensorSector,
    compute_mu, compute_eta, compute_sigma,
    run_perturbation_demo
)

# Run full perturbation demo
run_perturbation_demo()
```

Or run standalone:
```bash
python examples/demo_efc_relativistic.py
```

## Package Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `index.json` | Full machine-readable metadata |
| `schema.json` | JSON Schema for index.json |
| `metadata.json` | Package metadata with AI parsability flags |
| `EFC_Relativistic_Action.jsonld` | Schema.org linked data |
| `citations.bib` | BibTeX references |
| `src/__init__.py` | Package init with exports |
| `src/efc_relativistic.py` | Reference implementation |
| `data/framework.json` | Complete framework data |
| `examples/demo_efc_relativistic.py` | Runnable demo |

## Caveats

- **Working paper** (v0.5): Not peer-reviewed
- All mu, Sigma, eta expressions valid in quasi-static, sub-horizon regime only
- Full ADM Hamiltonian analysis for super-horizon modes remains open
- Reference implementation is pedagogical, not production-ready
- Numerical EFCLASS implementation not yet complete
