# Covariance-Aware BAO Consistency Test of EFC Using the BOSS DR12 Consensus Likelihood

## Overview

Fixed-parameter consistency test of EFC modified background expansion against precision BAO data using the official BOSS DR12 consensus likelihood with full 6x6 covariance matrix. EFC yields Delta_chi2 = -2.4 without parameter retuning.

**Author:** Morten Magnusson
**Affiliation:** Symbiose Research, Sandnes, Norway
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)
**DOI:** [10.6084/m9.figshare.31314922](https://doi.org/10.6084/m9.figshare.31314922)
**Date:** February 2026
**License:** CC-BY-4.0

---

## Key Results

| Dataset | chi2_LCDM | chi2_EFC | Delta_chi2 |
|---------|-----------|----------|------------|
| BOSS BAO | 5.79 | 3.43 | -2.36 |
| Cosmic Chronometers | 13.49 | 12.86 | -0.63 |
| Combined | -- | -- | -2.99 |

- Fixed-parameter test (no retuning)
- Uses official Cobaya/CosmoMC consensus covariance
- EFC modification amplitude: ~3.4% at z=0.38, ~1.1% at z=1.01, ~0 at z>2

---

## Quick Start

```python
from src.bao_cobaya_test import BAOCobayaTest

test = BAOCobayaTest(alpha_L2=0.045, z_L1L2=1.01)
results = test.run_boss_test()
print(f"Delta_chi2 = {results['delta_chi2']:.2f}")
```

---

## License

This work is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
