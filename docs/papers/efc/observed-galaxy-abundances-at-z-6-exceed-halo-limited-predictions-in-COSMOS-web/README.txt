================================================================================
SUPPLEMENTARY MATERIAL
Observed Galaxy Abundances at z > 6 Exceed Halo-Limited Predictions in COSMOS-Web
Magnusson (2026)
DOI: 10.6084/m9.figshare.31059964
================================================================================

CONTENTS
--------
1. Magnusson_2026_COSMOS_Galaxy_Excess.pdf  - Main manuscript
2. cover_letter.pdf                          - Cover letter to editor
3. figure1_stress_test.png                   - Figure 1 (stress test visualization)
4. supplementary_data.csv                    - Analyzed galaxy sample
5. analysis_code.py                          - Reproducible analysis script
6. README.txt                                - This file

DATA DESCRIPTION
----------------
supplementary_data.csv contains 8,447 massive galaxies (log M*/Msun > 9) at z > 5
from the COSMOS2025 catalog (Shuntov et al. 2025).

Columns:
  id        - COSMOS2025 source identifier
  ra        - Right ascension (J2000, degrees)
  dec       - Declination (J2000, degrees)
  z_phot    - Photometric redshift (LePhare)
  mass_med  - Stellar mass, median (log Msun)
  mass_l68  - Stellar mass, lower 68% confidence (log Msun)
  mass_u68  - Stellar mass, upper 68% confidence (log Msun)
  sfr_med   - Star formation rate, median (log Msun/yr)
  sfr_l68   - SFR, lower 68% confidence (log Msun/yr)
  sfr_u68   - SFR, upper 68% confidence (log Msun/yr)
  log_ssfr  - Specific SFR = SFR/M* (log Gyr^-1)

SOURCE DATA
-----------
Parent catalog: COSMOS2025 (COSMOS-Web DR1)
URL: https://cosmos2025.iap.fr/
Reference: Shuntov et al. 2025, A&A, submitted

REPRODUCIBILITY
---------------
Run analysis_code.py with Python 3.10+ and dependencies:
  pip install pandas numpy scipy matplotlib

CONTACT
-------
Morten Magnusson
Energy-Flow Cosmology Initiative
https://energyflow-cosmology.com
morten@magnusson.as
ORCID: 0009-0002-4860-5095
