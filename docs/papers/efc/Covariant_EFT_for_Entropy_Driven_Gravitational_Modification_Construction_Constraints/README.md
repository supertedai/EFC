# Covariant Effective Field Theory for Entropy-Driven Gravitational Modification

> **AI-Friendly Paper Package** — structured metadata + reference implementation + runnable demo

## Quick Summary

| Field | Value |
|-------|-------|
| **Authors** | Morten Magnusson |
| **Affiliation** | Independent Researcher, Sola, Norway |
| **ORCID** | 0009-0002-4860-5095 |
| **DOI** | 10.6084/m9.figshare.31878334 |
| **Date** | March 28, 2026 |
| **Status** | Working paper |
| **Framework** | EFC (Energy-Flow Cosmology) |
| **Keywords** | covariant EFT, scalar-tensor, entropy-driven gravity, RAR, Bose-Einstein, gravitational waves, gravitational slip |

## Core Idea

Systematic 17-iteration programme to construct and test a covariant scalar-tensor EFT where gravity is modified by an entropy-like scalar field S via acceleration-dependent response. Five structural results hold independently of the specific mu(g) form. A critical negative result identifies a microphysical gap.

## The Action

```
S = int d^4x sqrt(-g) [ R/(16piG) + (1/2)(dS)^2 - V(S) - beta|dS|_eps S^2 + L_m ]
```

- One scalar field S with parameters: beta (coupling), m_S (mass), epsilon (regulator)
- All combine into one observable scale: a_0 = 1.2 x 10^-10 m/s^2

## Five Structural Results

| # | Result | Status |
|---|--------|--------|
| I | GW speed c_gw = c exactly (theorem) | Shown |
| II | Gravitational slip eta = 1 + O(Phi*mu) | Shown |
| III | Solar-system: exponential amplitude suppression | Shown |
| IV | Ghost-free, tachyon-free, hyperbolic | Shown |
| V | RAR formally identical to Bose-Einstein: mu = 1/(exp(sqrt(g/a_0)) - 1) | Identified |

## Critical Gap

The classical field equation from -beta|dS|S^2 produces a correction that **increases** with acceleration, whereas RAR requires a **decreasing** correction. This identifies a microphysical gap requiring quantum treatment or non-local coupling.

## 17-Iteration Programme

See `data/framework.json` for the complete iteration table with test, result, and status for each of the 17 versions.

## Quick Start

```python
from src.covariant_eft import (
    CovEFTAction, BoseEinsteinRAR, SolarSystemTest,
    StabilityAnalysis, run_eft_demo
)
run_eft_demo()
```

Or run standalone:
```bash
python examples/demo_covariant_eft.py
```

## Package Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `index.json` | Full machine-readable metadata |
| `schema.json` | JSON Schema for index.json |
| `metadata.json` | Package metadata with AI parsability flags |
| `Covariant_EFT.jsonld` | Schema.org linked data |
| `citations.bib` | BibTeX references |
| `src/__init__.py` | Package init with exports |
| `src/covariant_eft.py` | Reference implementation |
| `data/framework.json` | Complete framework data (17 iterations, 5 results, gap) |
| `examples/demo_covariant_eft.py` | Runnable demo |

## Caveats

- **Working paper**: Not peer-reviewed
- mu(g) is postulated as effective relation, not derived from classical action
- Slip result demonstrated only in weak-field spherically symmetric regime
- Not yet tested against CMB, f*sigma_8, Bullet Cluster, or H(z)
- Reference implementation is pedagogical, not production-ready
