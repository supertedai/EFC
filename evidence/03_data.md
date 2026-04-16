# EFC Observational Data Sources

## Embedded datasets (verified by reproduce_efc.py)

### fsigma_8 compilation (7 points)

| Survey | z | fsigma_8 | error | Reference |
|--------|---|----------|-------|-----------|
| 6dFGS | 0.02 | 0.360 | 0.040 | Beutler et al. 2012 |
| SDSS MGS | 0.15 | 0.490 | 0.055 | Howlett et al. 2015 |
| BOSS DR12 | 0.38 | 0.430 | 0.054 | Alam et al. 2017 |
| BOSS DR12 | 0.51 | 0.452 | 0.057 | Alam et al. 2017 |
| BOSS DR12 | 0.61 | 0.457 | 0.052 | Alam et al. 2017 |
| VIPERS | 0.77 | 0.420 | 0.060 | de la Torre et al. 2013 |
| FastSound | 0.85 | 0.380 | 0.080 | Okumura et al. 2016 |

Code: `src/efc/perturbation/robustness.py:FSIGMA8_DATA`

### Planck 2018 baseline cosmology

| Parameter | Value | Source |
|-----------|-------|--------|
| Omega_m | 0.3134 | Planck 2018 |
| Omega_r | 9.15e-5 | Planck 2018 |
| H_0 | 67.4 km/s/Mpc | Planck 2018 |
| sigma_8 | 0.811 | Planck 2018 |

Code: `src/efc/perturbation/background.py:DEFAULT_*`

## External datasets (referenced in ledger)

### BAO

| Dataset | Points | z range | Source |
|---------|--------|---------|--------|
| DESI DR2 | 7 | 0.30-2.33 | DESI Collaboration 2025 |
| BOSS DR12 | 6 | 0.32-0.57 | Alam et al. 2017 |

### Supernovae

| Dataset | Points | z range | Source |
|---------|--------|---------|--------|
| Pantheon+ | 16 (binned) | 0.01-1.00 | Brout et al. 2022 |

### Galaxy rotation curves

| Dataset | Galaxies | Source |
|---------|----------|--------|
| SPARC | 175 | Lelli et al. 2016 |

### CMB

| Dataset | Source |
|---------|--------|
| Planck 2018 plik_lite TTTEEE + lowl + lensing | Planck Collaboration 2020 |
| MGCAMB v1.5.2 for mu-Sigma scans | Zhao et al. 2009 |

## Data provenance

All data files live in `docs/papers/efc/*/data/`.
Each paper directory includes `index.json` with DOI and metadata.
The evidence register maps DOIs to categories:
`docs/validation-ledger/data/evidence-register.json`
