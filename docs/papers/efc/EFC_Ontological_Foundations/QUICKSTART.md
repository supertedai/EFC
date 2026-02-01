# EFC Ontological Foundations - Quick Start Guide

## 5-Minute Overview

**EFC Ontological Foundations** resolves the circularity problem in physics:
- Does energy-flow cause entropy increase?
- Or does entropy increase drive energy-flow?

**Answer**: Neither is primary. Both emerge from a **co-primary structure**.

## The Circularity Problem

### Hypothesis H1: Energy-Flow Primacy
```
Energy-Flow → Entropy
Problem: Requires entropy to define "flow direction"
Result: CIRCULAR
```

### Hypothesis H2: Entropy Primacy
```
Entropy → Energy-Flow
Problem: Requires energy to define entropy changes
Result: CIRCULAR
```

### Hypothesis H3: Co-Primary Structure ✓
```
Pre-Geometric Potential
        ↓
   Differentiation
        ↓
   ┌────┴────┐
   EF        S
(Energy)  (Entropy)
```

## Quick Implementation

```python
from efc_ontology import OntologicalAnalyzer

analyzer = OntologicalAnalyzer()

# Test a hypothesis for circularity
result = analyzer.test_circularity(
    hypothesis="energy_primacy",
    definitions=["energy", "flow", "direction", "time"]
)

print(f"Circular: {result.is_circular}")
print(f"Cycle: {result.dependency_cycle}")
```

## The Three Phases

| Phase | Description | Physics |
|-------|-------------|---------|
| Pre-Planck | Undifferentiated potential | No spacetime |
| Planck Transition | Differentiation occurs | Emergence |
| Post-Planck | Standard physics | Observable universe |

## Key Insight

The co-primary structure means:
1. **EF and S are aspects**, not separate substances
2. **Neither derives from the other**
3. **Both emerge simultaneously** at the Planck transition

## Epistemic Status

**Layer C**: Coherence argument, not empirical claim.

This is a *methodological* paper that:
- Identifies conceptual problems
- Proposes structural resolution
- Does NOT make testable predictions

## Relationship to EFC

```
Ontological Foundations (this paper)
         ↓
    Core Lock (mathematical engine)
         ↓
    EBE Core Principles (methodology)
         ↓
    RCMP (measurement protocol)
```

## Cross-Domain Evidence

The paper draws parallels from:
- Wheeler's "it from bit"
- Verlinde's entropic gravity
- Prigogine's dissipative structures
- Holographic principle

## Next Steps

1. Read the full paper: `EFC_Ontological_Foundations_v1_0_2-1.pdf`
2. Explore `src/` for analysis tools
3. See `docs/circularity_analysis.md` for detailed breakdown
4. Review relationship to other EFC papers

## Citation

```bibtex
@article{magnusson2026ontology,
  author = {Magnusson, Morten},
  title = {EFC Ontological Foundations v1.0: The Co-Primary Structure},
  year = {2026}
}
```
