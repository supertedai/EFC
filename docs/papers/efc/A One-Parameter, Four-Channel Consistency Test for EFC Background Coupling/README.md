# A One-Parameter, Four-Channel Consistency Test for EFC Background Coupling

## Overview

Consistency test of EFC's background coupling against four independent cosmological probes: BAO distances, redshift-space distortions, CMB lensing, and Type Ia supernovae. Demonstrates that Poisson-channel modification is excluded while background coupling shows mild preference.

**Author:** Morten Magnusson
**Affiliation:** Symbiose Research, Sandnes, Norway
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)
**DOI:** [10.6084/m9.figshare.31304980](https://doi.org/10.6084/m9.figshare.31304980)
**Date:** February 2026
**License:** CC-BY-4.0

---

## Key Results

### Channel Comparison

| Channel | Parameter | chi2_RSD | sigma_8 | Status |
|---------|-----------|----------|---------|--------|
| Poisson | alpha=0.34 | 18.2 | 0.879 | Excluded |
| Background | beta=0.08 | 1.09 | 0.805 | Favoured |
| LCDM | -- | 1.34 | 0.811 | Baseline |

### Four-Channel Results (beta = 0.08)

| Channel | Data | Delta_chi2 | Status |
|---------|------|------------|--------|
| BAO distances | BOSS DR12 | -3.65 | PASS |
| Growth rate | BOSS DR12 fsigma8 | -0.25 | PASS |
| CMB lensing | ACT+SPT+Planck | -0.71sigma | PASS |
| SN Ia | Pantheon+ | delta_mu < 0.032 | PASS |

### Combined Result

- BAO + RSD combined: Delta_chi2 = -3.89 (~2sigma preference)
- Four channels, one parameter, zero kills

---

## Core Equations

### Modified Friedmann Equation

```
H^2(a) = H0^2 [Omega_m a^{-3} + Omega_Lambda (1 + beta * T(a))]
```

### Transition Function

```
g_D(z) = (1 - Omega_m(z)) / (1+z) * ln(1+z)
T(z) = g_D(z) / g_D(z_peak)
```

---

## Quick Start

```python
from src.four_channel_test import FourChannelTest

test = FourChannelTest(beta=0.08)
results = test.run_all_channels()
for channel, result in results.items():
    print(f"{channel}: status={result['status']}, Delta_chi2={result.get('delta_chi2', 'N/A')}")
```

---

## File Structure

```
.
├── README.md
├── index.json
├── schema.json
├── metadata.json
├── four_channel_test.jsonld
├── citations.bib
├── src/
│   ├── __init__.py
│   └── four_channel_test.py
├── data/
│   └── channel_results.json
└── examples/
    └── demo_four_channel.py
```

---

## References

1. Alam et al. (2017), MNRAS 470, 2617 (BOSS DR12)
2. Brout et al. (2022), ApJ 938, 110 (Pantheon+)
3. Qu et al. (2025), arXiv:2504.20038 (CMB lensing)
4. Planck Collaboration (2020), A&A 641, A6

---

## License

This work is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
