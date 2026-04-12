# Natural and Mechanical Entropy: Intention Detection via Episenter–Resonance Analysis in Information Systems

**DOI:** [10.6084/m9.figshare.31864993](https://doi.org/10.6084/m9.figshare.31864993)

> **AI-Friendly Paper Package** — structured metadata + reference implementation + runnable demo

## Quick Summary

| Field | Value |
|-------|-------|
| **Authors** | Morten Magnusson |
| **Affiliation** | Independent Researcher, Sandnes, Norway |
| **ORCID** | 0009-0002-4860-5095 |
| **Version** | v2 (March 26, 2026) |
| **Status** | Working paper |
| **Framework** | EFC / Regime-Bound Measurement |
| **Keywords** | natural entropy, mechanical entropy, intention detection, episenter analysis, regime-bound measurement, information manipulation, AI alignment bias |

## Core Idea

Information systems produce outputs blending emergent signal with constructed bias. This paper formalises a distinction between:

- **Natural entropy (S_N)**: emergent, intention-free, distributed episenter, organic resonance
- **Mechanical entropy (S_M)**: constructed, intention-bearing, localised episenter, imposed resonance

**Structural intention** is defined operationally as KL-divergence between observed output and the system's baseline dynamics — no agent-theoretic assumptions required.

## Key Equations

| Equation | Description |
|----------|-------------|
| `I = D_KL(q(x) ∥ p(x\|D))` | Structural intention (KL-divergence from baseline) |
| `S_N = H(X\|D)` | Natural entropy (conditional on dynamics) |
| `S_M = H(X\|D,I) + λ·I(X;I)` | Mechanical entropy (with intervention coupling) |
| `ΔS = S_observed − S_N_predicted` | Entropy class residual |
| `E = max_k I(X_k;X) / Σ_k I(X_k;X)` | Episenter concentration index |
| `R(ω) = P_observed(ω) / P_null(ω)` | Resonance spectrum ratio |
| `A = max_{r,s} \|ΔS(T_r(X)) − ΔS(T_s(X))\|` | Cross-regime asymmetry |

## Three Diagnostics

1. **Episenter Concentration (E)**: High E → mechanical (concentrated source); Low E → natural (distributed)
2. **Resonance Spectrum Ratio (R)**: R(ω) ≫ 1 at specific frequencies → imposed periodicity
3. **Cross-Regime Asymmetry (A)**: A ≈ 0 → natural; A ≫ 0 → mechanical

**Combined criterion**: All three must exceed critical thresholds simultaneously.

## Case Studies

1. **LLM Alignment Bias** — alignment mechanisms inject detectable mechanical entropy
2. **Academic Paradigm-Guarding** — institutional review creates concentrated episenters
3. **Information Warfare** — state-level operations show non-native resonance frequencies

## 13 Falsifiable Predictions

See `data/framework.json` for the complete list with domains (LLM, Academia, Psyops, General, EFC-C).

## Quick Start

```python
from src.entropy_intention import (
    StructuralIntention,
    NaturalEntropy,
    MechanicalEntropy,
    EpisenterConcentration,
    ResonanceSpectrum,
    CrossRegimeAsymmetry,
    DetectionCriterion,
    run_detection_demo
)

# Run full detection demo
run_detection_demo()
```

Or run the standalone demo:
```bash
python examples/demo_entropy_intention.py
```

## Package Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `index.json` | Full machine-readable metadata |
| `schema.json` | JSON Schema for index.json validation |
| `metadata.json` | Package metadata with AI parsability flags |
| `Natural_and_Mechanical_Entropy.jsonld` | Schema.org linked data |
| `citations.bib` | BibTeX references |
| `src/__init__.py` | Package init with exports |
| `src/entropy_intention.py` | Reference implementation |
| `data/framework.json` | Complete framework data (definitions, diagnostics, predictions) |
| `examples/demo_entropy_intention.py` | Runnable demo script |

## Caveats

- **Working paper**: Not peer-reviewed
- **Empirical protocol proposed but not yet executed** (Section 5 of paper)
- **Thresholds (E_crit, R_crit, A_crit) must be calibrated empirically per domain**
- Reference implementation is pedagogical, not production-ready
- Natural/mechanical distinction is not always binary — hybrid cases exist
