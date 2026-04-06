# Observed Galaxy Abundances at z > 6 Exceed Halo-Limited Predictions in COSMOS-Web

**DOI:** 10.6084/m9.figshare.31059964
**Author:** Morten Magnusson (ORCID: 0009-0002-4860-5095)
**Affiliation:** Symbiose Research, Sandnes, Norway
**License:** CC-BY-4.0

---

## Overview

This paper reports that 8,447 massive galaxies (log M*/Msun > 9) at z > 5 from the JWST COSMOS-Web survey exceed LCDM halo-limited predictions, providing tension with standard cosmology at early cosmic times. The analysis uses the COSMOS2025 catalog (Shuntov et al. 2025).

**Key Finding:** Observed galaxy abundances at z > 6 significantly exceed halo mass function predictions, with excess factors growing monotonically with redshift.

---

## Data

- **Source:** COSMOS2025 catalog (Shuntov et al. 2025) from JWST COSMOS-Web DR1
- **Sample:** 8,447 massive galaxies with log M*/Msun > 9 at z > 5
- **Redshift range:** z > 5 (photometric redshifts from LePhare)

### Columns

| Column | Description |
|--------|-------------|
| id | COSMOS2025 source identifier |
| ra | Right ascension (J2000, degrees) |
| dec | Declination (J2000, degrees) |
| z_phot | Photometric redshift (LePhare) |
| mass_med | Stellar mass, median (log Msun) |
| sfr_med | Star formation rate, median (log Msun/yr) |
| log_ssfr | Specific SFR = SFR/M* (log Gyr^-1) |

---

## Key Results

- Galaxy abundances exceed LCDM predictions at z > 6
- Excess factor increases with redshift
- Tension is strongest at z > 10 where observed counts are orders of magnitude above halo-limited predictions
- Results are consistent with EFC framework predictions of enhanced structure formation at high redshift

---

## Files

```
cosmos-web/
+-- README.md                          # This file
+-- index.json                         # Paper metadata
+-- schema.json                        # Data schema
+-- cosmos-galaxy-abundances.jsonld    # Linked data
+-- citations.bib                      # Bibliography
+-- metadata.json                      # Structured metadata
+-- Magnusson_2026_COSMOS_Galaxy_Excess.pdf  # Main paper
+-- analysis_code.py                   # Original analysis code
+-- figure1_stress_test.png            # Main figure
+-- src/
|   +-- __init__.py                    # Module init
|   +-- cosmos_abundances.py           # Core classes
+-- data/
|   +-- cosmos_abundance_data.json     # Summary data
+-- examples/
    +-- demo_cosmos.py                 # Demonstrations
```

---

## Citation

```bibtex
@misc{magnusson2026cosmos,
  author = {Magnusson, Morten},
  title = {Observed Galaxy Abundances at z > 6 Exceed Halo-Limited Predictions in COSMOS-Web},
  year = {2026},
  doi = {10.6084/m9.figshare.31059964}
}
```

---

## Contact

**Morten Magnusson**
ORCID: 0009-0002-4860-5095
Affiliation: Symbiose Research, Sandnes, Norway

---

## License

This work is licensed under Creative Commons Attribution 4.0 International (CC-BY-4.0).
