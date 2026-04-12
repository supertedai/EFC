# Regime-Locked Measurement as a General Structural Constraint

**DOI:** [10.6084/m9.figshare.31833076](https://doi.org/10.6084/m9.figshare.31833076)

**Cross-Domain Framework, Operational Meta-Regime Protocol, and Quantitative Regime-Appropriateness Scoring**

| Field | Value |
|-------|-------|
| Author | Morten Magnusson |
| Affiliation | Symbiose Research, Sandnes, Norway |
| ORCID | 0009-0002-4860-5095 |
| Date | March 2026 |

## Quick Start

```python
from src.regime_locked import (
    Regime, RegimeAppropriateness, BlindSetTaxonomy,
    MetaRegimeProtocol, CrossDomainDemos, CDVCAssessment,
)

# Alpha score
alpha = RegimeAppropriateness()
print(f"alpha(phi, R) in [0, 1]: continuous regime-appropriateness")

# Blind set taxonomy
taxonomy = BlindSetTaxonomy()
taxonomy.print_table()

# Six-domain demonstration
demos = CrossDomainDemos()
demos.summary()
```

## Summary

Every measurement system operates within an implicit regime: a bounded domain of validity. Outside this domain, the instrument is not imprecise — it is structurally blind. This paper formalises regime-locked measurement as a general structural constraint across six domains.

### Three Operational Contributions
1. **Alpha-score**: Quantitative regime-appropriateness score alpha(phi, R) in [0, 1]
2. **Blind-set taxonomy**: Three types (ontological, methodological, instrumental) with distinct detection strategies
3. **Meta-regime protocol**: Five-step operational evaluation procedure

### Formal Framework

**Regime**: R = (I, V, B, G) where I = instrument, V = validity domain, B = blind set, G = gradient sensitivity

**Regime-locked measurement**: m in V(R_i) and m not in V(R_j) for i != j

**Alpha-score**: alpha(phi, R_i) = |phi ∩ V(R_i)| / |phi| in [0, 1]

**CDVC**: Signal sigma exhibits Cross-Disciplinary Vector Convergence if sigma in intersection of V(R_k) for N >= 3 domains

**Meta-regime**: R* : (R_i, phi) -> alpha(phi, R_i)

### Blind-Set Taxonomy (Table 2)

| Type | Character | Detection Strategy |
|------|-----------|-------------------|
| B_ont (ontological) | Outside instrument's physical reach | New instrument class |
| B_meth (methodological) | Excluded by framework assumptions | Cross-regime comparison; assumption audit |
| B_inst (instrumental) | Within reach but below sensitivity | Instrument upgrade; residual analysis |

### Six-Domain Demonstration (Table 3)

| Domain | Instrument Sees | Instrument Misses | B Type |
|--------|----------------|-------------------|--------|
| Cosmology | Model-predicted signals | Alternative mechanisms | meth |
| AI Alignment | Deviation from norms | Convergence drift | meth |
| Cyber Security | Known signatures | Regime-boundary exploits | meth |
| Intelligence | In-scope threats | Out-of-doctrine threats | meth |
| Economics | In-regime behaviour | Regime transitions | inst |
| Consciousness | Neural correlates | Subjective experience | ont |

### Meta-Regime Protocol (Algorithm 1)
1. **Regime Identification**: Characterise R = (I, V, B, G)
2. **Blind Set Elicitation**: Enumerate B_known; classify as B_ont/B_meth/B_inst
3. **Cross-Regime Check**: For each b in B_i, test if b in V_j for some j != i
4. **Residual Analysis**: Test residuals for structure -> B_inferred candidates
5. **Alpha-Scoring**: Estimate alpha; flag if below threshold

### S0/S1 Conjecture
At gradient extremes, qualitatively different generative processes may produce observationally indistinguishable outputs (identifiability problem). In AI: deep framework integration (S0) vs superficial linguistic mirroring (S1).

### Falsification Criteria
- **Framework**: B = empty-set demonstrated; or CDVC from shared bias
- **Protocol**: Fails to detect planted blind spots; alpha fails to discriminate
- **Conjecture**: General method reliably distinguishes S0/S1 from output alone

### Epistemic Status (Table 1)
| Level | Status | Content |
|-------|--------|---------|
| Definition | Formal | Regime, regime-locked measurement, CDVC, meta-regime, alpha-score, blind-set taxonomy |
| Hypothesis | Testable | Shared pattern across domains; meta-regime detects blind spots; alpha outperforms binary |
| Conjecture | Open | S0/S1 observational equivalence at gradient extremes |

## Caveats
- Framework applies constraints to itself (R_meta has unknown B_meta)
- CDVC is indicator, not proof (shared cognitive bias possible)
- S0/S1 is conjecture only
- Alpha requires proxy estimation
- No controlled empirical validation yet
- AI convergence drift case is illustrative, not experimental

## File Manifest
| File | Description |
|------|-------------|
| `index.json` | Machine-readable: formal framework, six domains, protocol, falsification |
| `schema.json` | JSON Schema |
| `metadata.json` | Package metadata |
| `EFC-Regime-Locked.jsonld` | Schema.org linked data |
| `citations.bib` | BibTeX references (13 entries) |
| `src/regime_locked.py` | Reference implementation |
| `data/framework.json` | All formal definitions, tables, protocol |
| `examples/regime_locked_demo.py` | Runnable demo |
