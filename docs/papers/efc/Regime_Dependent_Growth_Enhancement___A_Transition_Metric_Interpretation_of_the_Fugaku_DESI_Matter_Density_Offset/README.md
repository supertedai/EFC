# Regime-Dependent Growth Enhancement: A Transition Metric Interpretation of the Fugaku-DESI Matter Density Offset

## Overview

Reinterprets the ~10% matter density offset in Fugaku N-body simulations as a transition estimator Delta_F measuring integrated regime transition strength rather than a fundamental density parameter.

**Author:** Morten Magnusson
**Affiliation:** Symbiose Research, Sandnes, Norway
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)
**DOI:** [10.6084/m9.figshare.31140000](https://doi.org/10.6084/m9.figshare.31140000)
**License:** CC-BY-4.0

---

## Key Results

- Delta_F ~ 0.1 from integrated transition kernel
- Consistent with CMB (mu ~ 1 at recombination), DESI/Fugaku (transition band), and galaxy scales (mu > 1 asymptotically)
- Reinterpretation: density offset = integrated transition strength, not fundamental parameter shift

---

## Quick Start

```python
from src.transition_metric import TransitionMetric

tm = TransitionMetric(delta_mu=0.1)
delta_F = tm.compute_delta_F()
print(f"Delta_F = {delta_F:.3f}")
```

---

## License

This work is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
