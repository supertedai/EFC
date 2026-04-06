# Regime Consistency of an Entropy-Gradient Coupling: Lya, BAO and RSD Tests within a Structural Coherence Framework

## Overview

Structural regime consistency test of EFC's coupling function T(z) across three independent cosmological probes (Lya P1D, BOSS BAO, BOSS RSD), evaluated using the Structural Coherence Evaluation (SCE) framework against LCDM.

**Author:** Morten Magnusson
**Affiliation:** Symbiose Research, Sandnes, Norway
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)
**DOI:** [10.6084/m9.figshare.31304995](https://doi.org/10.6084/m9.figshare.31304995)
**Date:** February 10, 2026
**License:** CC-BY-4.0

---

## Key Results

| Regime | z | T(z) | Prediction | Result |
|--------|---|------|------------|--------|
| Growth (BAO) | 0.38-0.61 | 0.95-1.0 | Enhanced H, suppressed growth | PASS |
| Lya P1D | 3.0 | 0.107 | Near-null effect | PASS |
| CMB | 1100 | ~1e-10 | GR recovery | PASS |

- BAO + RSD combined: Delta_chi2 = -3.89 (~2sigma preference for EFC)
- Single coupling function T(z) consistent across all three regimes
- Five pre-registered forbidden patterns, none triggered
- SCE evaluation: neither framework dominates; LCDM wins on compression, EFC wins on structural discipline

---

## Quick Start

```python
from src.regime_consistency import RegimeConsistencyTest

test = RegimeConsistencyTest(beta=0.08)
results = test.run_all_tests()
for regime, outcome in results['regime_summary'].items():
    print(f"{regime}: {outcome['status']}")
```

---

## License

This work is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
