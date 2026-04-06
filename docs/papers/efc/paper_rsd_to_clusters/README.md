# From RSD to Clusters: A Parameter-Locked Test of Late-Time Structure Growth

## Overview

A cross-probe test of late-time structure growth propagating RSD constraints on effective gravitational coupling into galaxy cluster abundance predictions with zero free parameters fit to cluster data.

**Author:** Morten Magnusson
**Affiliation:** Symbiose Research, Sandnes, Norway
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)
**DOI:** [10.6084/m9.figshare.31292827](https://doi.org/10.6084/m9.figshare.31292827)
**License:** CC-BY-4.0

---

## Key Results

- RSD-locked prediction: N_EFC / N_LCDM = 1.064 (+6.4% more clusters)
- Shape signature: z-dependent tilt dR/dz < 0 in cluster redshift distribution
- Crossover near z ~ 0.3-0.4
- Robust against uniform mass-calibration systematics

---

## Quick Start

```python
from src.rsd_to_clusters import RSDToClusterTest

test = RSDToClusterTest(alpha_L2=0.34)
results = test.predict_abundance()
print(f"N_EFC/N_LCDM = {results['abundance_ratio']:.3f}")
```

---

## License

This work is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
