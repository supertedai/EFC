# Regime-Bound Measurement in Complex Systems: Proxy, Placement, and Validity

| Field | Value |
|-------|-------|
| Author | Morten Magnusson |
| Affiliation | Symbiose Research, Sandnes, Norway |
| ORCID | 0009-0002-4860-5095 |
| Date | Working paper — March 7, 2026 |
| Keywords | regime-bound measurement, proxy validity, epistemic placement, complex systems, EFC/WP3, AI evaluation |

## Quick Start

```python
from src.regime_measurement import (
    CoreConcepts, PredictionRegister, AxiomZeroResults,
    StructuralChain, ValidityProfile,
)

# Five core concepts
concepts = CoreConcepts()
concepts.print_reference_table()

# Prediction register (13 predictions)
register = PredictionRegister()
register.summary()

# Axiom 0 test results
ax0 = AxiomZeroResults()
print(f"Sign coherence p = {ax0.sign_coherence_p}")
```

## Summary

This paper formalises a general measurement framework where analysis is **cartography** — mapping outputs as coordinates on a structured response surface — rather than verdict. Observed outputs are regime-conditioned products of proxy choice, instrument logic, observer placement, and interpretive compression.

### Five Core Concepts

| Concept | Definition | Failure Mode | Test |
|---------|-----------|--------------|------|
| **Regime** | Bounded domain where consistent inferential rules hold | Conflation: pooling across boundaries | Residuals differ by regime |
| **Proxy** | Mediating variable with defined visibility and blindness | Opacity: treating proxy as direct read | Proxy substitution produces drift |
| **Placement** | Position across physical, instrument, interpretive space | Incompatibility: comparing across dimensions | Placement-matching reduces conflict |
| **Episenter** | Weighted privileged variables organising what appears central | Universalism: undeclared single episenter | Episenter shift redistributes structure |
| **Compression** | Structural reduction from phenomenon to output | Neglect: scalar treated as complete | Lost dimensions have predictable footprint |

### Structural Chain
```
regime → proxy + placement → episenter → compression → output
(scope)   (access)           (organisation) (reduction)  (observed datum)
```

### Nine Theses
1. Measurement is not direct readout
2. Proxy creates both visibility and blindness
3. Measurement placement is a primary question
4. Episenter is produced, not given
5. Conflicts may be regime conflicts
6. Validity is regime-conditioned
7. Analysis of the analysis is part of the analysis
8. Measurement is compression
9. A fragment carries holistic structure under four conditions

### Five Derived Predictions
- **P1**: Consistent response at shared coordinates
- **P2**: Systematic proxy-substitution drift
- **P3**: Regime-resolution of conflicts
- **P4**: Cartographic null results
- **P5**: Episenter-shift redistribution

### Case 1: Cosmology (WP3 / R(k, S))
- Three EFC structural regimes: FLOW, TRANSITION, LATENT (over S-hat(z))
- Proxy: S-hat(z) = log10(rho_SFR(z)) + log10(f_gas(z)) + C0
- Axiom 0 test: sign coherence p = 0.020 (N=10, secondary), primary p=1.0 (degenerate)
- DESI z=1.0 sits exactly on FLOW/TRANSITION boundary (dist=0.000)
- Hubble tension reframed as regime mismatch (Table 4)

### Case 2: AI Evaluation (Validity-Aware AI)
- Four regime dimensions: input distribution, task structure, annotation regime, deployment context
- Explainability is not validity (proxy conflation)
- Five proxy metrics analysed (Table 6): BLEU/ROUGE, Accuracy/F1, Perplexity, Human preference, SHAP/attention
- Validity-aware evaluation requires five declarations

### Prediction Register (13 predictions)
| ID | Domain | Prediction | Status |
|----|--------|-----------|--------|
| C1 | Cosm. | Probe consistency at (k,S) | PARTIAL |
| C2 | Cosm. | Proxy substitution drift | Pending |
| C3 | Cosm. | Boundary clustering | ACTIVE |
| C4 | Cosm. | H0 within-regime variance | ACTIVE |
| C5 | Cosm. | LATENT sign coherence | PARTIAL |
| C6 | Cosm. | Proxy divergence at TRANSITION | Pending |
| A1 | AI | Boundary variance increase | Meth. |
| A2 | AI | Episenter shift redistribution | Meth. |
| A3 | AI | Cross-regime rank correlation | ACTIVE |
| A4 | AI | Explainability-validity decoupling | Meth. |
| A5 | AI | Validity profile utility | Pending |
| F1 | Both | Proxy drift directionality | ACTIVE |
| F2 | Both | Regime-ID resolution frequency | Meth. |

### Framework-Breaking Outcomes (F-BREAK)
1. Regime-random residuals
2. Proxy-substitution drift is random
3. Episenter shift produces random redistribution
4. Hubble tension survives full regime-compatibility test
5. Null results are regime-random

## Caveats
- Working paper status
- Axiom 0 results are preliminary (N=10, secondary statistic)
- DESI z=1.0 boundary coincidence is anecdotal at current sample size
- AI predictions are methodological — testable but not yet run

## File Manifest
| File | Description |
|------|-------------|
| `index.json` | Machine-readable metadata, concepts, predictions |
| `schema.json` | JSON Schema for validation |
| `metadata.json` | Package metadata |
| `EFC-Regime-Measurement.jsonld` | Schema.org linked data |
| `citations.bib` | BibTeX references (14 entries) |
| `src/regime_measurement.py` | Reference implementation |
| `data/predictions.json` | Full prediction register with evidence status |
| `data/tables.json` | All paper tables in machine-readable form |
| `examples/regime_demo.py` | Runnable demo |
