# Double-Slit as Grid-Resolution Phenomenon in Grid-Rendering Cosmology

**Ontological Extension, UV-Cutoff Analysis, and Open Gaps toward Quantum Testability**

| Field | Value |
|-------|-------|
| Author | Morten Magnusson |
| ORCID | 0009-0002-4860-5095 |
| Version | Working Note v0.2 (Revised) |
| Date | March 8, 2026 |
| Status | Preprint. Not peer-reviewed. |
| Scope | Ontological and minimal-model extension of GRC to sub-L0 quantum regime |

## Quick Start

```python
from src.grc_double_slit import (
    GRCAxioms, UVCutoffModel, EntropyClarity, PredictionStatus, OpenGaps,
)

# UV cutoff deviation
uv = UVCutoffModel(l_g=1e-35, sigma=1e-6)
print(f"Deviation: |delta A| ~ {uv.deviation_bound():.2e}")  # ~0 for sub-Planck l_g

# Entropy-clarity function
C = EntropyClarity(S_max=1.0)
print(f"C(S=0.1) = {C(0.1):.4f}")  # High clarity
print(f"C(S=0.9) = {C(0.9):.4f}")  # Low clarity
```

## Summary

GRC treats quantum uncertainty as a grid-resolution phenomenon: Delta x >= l_g, where l_g is the fundamental node scale of a discrete geometric substrate. This note derives consequences for the double-slit experiment within the GRC triad:

```
Psi_manifest = G(x) ⊗ E(x,t) · C(S(x,t))
```

### Six Axioms
| ID | Axiom | Content |
|----|-------|---------|
| A1 | Grid (G) | Discrete geometric substrate with node scale l_g |
| A2 | Energy Flow (E) | Energy as distributed flow through G |
| A3 | Clarity Function C(S) | C(S) = exp(-S/S_max); low S = high clarity |
| A4 | Manifest Structure | Psi_manifest = G(x) ⊗ E(x,t) · C(S(x,t)) |
| A5 | Grid-Resolution Limit | Position limited by l_g |
| A6 | Registration as Local Selection | Measurement = local stabilization of Psi_manifest |

### Key Result: UV-Cutoff Derivation (Section 7)

The exact GRC amplitude with UV cutoff:
```
A_GRC(x) = integral[-kmax,kmax] a-tilde(k) e^{ikx} dk,  kmax = pi/l_g
```

Deviation from standard QM:
```
Delta A(x) = integral[|k|>pi/l_g] a-tilde(k) e^{ikx} dk
```

For Gaussian slit profiles (width sigma):
```
|Delta A| ~ (l_g / pi*sigma^2) * exp(-pi^2 sigma^2 / 2*l_g^2)
```

**Conclusion**: Deviation is exponentially suppressed for sigma >> l_g. The polynomial ansatz O((l_g/d)^2) from v0.1 is withdrawn.

### Five Predictions
| ID | Prediction | Status |
|----|-----------|--------|
| P1 | Backward compatibility (recover QM as C->1, l_g/d->0) | Required (analytic) |
| P2 | Geometric cutoff deviation | Downgraded: principled but inaccessible |
| P3 | S-sensitive decoherence (primary candidate) | Open — blocked by G2 |
| P4 | Gradual which-path suppression (higher-order stats) | Open — secondary candidate |
| P5 | No new prediction for d >> l_g | Explicit no-claim |

### Six Falsification Points
| ID | Falsification condition |
|----|----------------------|
| F1 | Backward compatibility fails |
| F2 | No scale-deviation where GRC predicts one (principled, not operative) |
| F3 | Decoherence fully reduced to T + environment (no S-component) |
| F4 | Higher-order statistics identical to QM under partial measurement |
| F5 | Delta P(x) doesn't decrease with d/l_g |
| F6 | Standard QM results at d >> l_g do NOT falsify GRC |

### Open Gaps (Table 1)
| Priority | Gap | Description | Blocks |
|----------|-----|-------------|--------|
| 1 | G2 | Operational definition of local S | P3 testability |
| 2 | P3 | Formal decoherence model via C(S) | Main test candidate |
| 3 | P4 | Concrete higher-order observable | Secondary test |
| 4 | G3 | Explicit P(x) for concrete geometry | Numerical check |
| 5 | G5 | Closure Condition 3 vs mode basis | Internal consistency |

### G2 Candidates for Operational S
- **A**: von Neumann entropy (weakest; likely reduces to standard QM)
- **B**: Entanglement entropy against environment
- **C**: Free-energy or structural complexity proxy (most EFC-native; hardest)

## Caveats
- Working note, not completed derivation
- Geometric cutoff test (P2) is practically inaccessible for sub-Planckian l_g
- Theory's quantum distinction lies in measurement as entropy process (P3/P4), not interference geometry
- G2 (operational S) is the critical blocking gap

## File Manifest
| File | Description |
|------|-------------|
| `index.json` | Machine-readable metadata, axioms, equations, predictions |
| `schema.json` | JSON Schema for validation |
| `metadata.json` | Package metadata |
| `EFC-GRC-DoubleSlit.jsonld` | Schema.org linked data |
| `citations.bib` | BibTeX references (13 entries) |
| `src/grc_double_slit.py` | Reference implementation |
| `data/model_parameters.json` | All parameters and status tables |
| `examples/double_slit_demo.py` | Runnable demo |
