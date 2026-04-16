# EFC Key Results with Ledger Bindings

Each result below links to the specific ledger entry, code function,
and DOI that produced it.

**Significance disclaimer:** The strongest historical signal was 2.2 sigma
(fsigma_8 growth suppression, pre-DESI DR2).  Following DESI DR2, the
background coupling collapsed to 0.68 sigma.  The perturbation-sector
Variant H test gives DAIC = +4.05 (LCDM preferred).  All results should
be read as *suggestive indications*, not established claims.  Decisive
tests require Stage-IV lensing data (Euclid DR1, Rubin LSST).

## R1: fsigma_8 growth suppression

| Metric | Value |
|--------|-------|
| alpha (pre-DESI DR2) | -1.00 +/- 0.46 |
| Significance (pre-DESI DR2) | 2.20 sigma |
| **alpha (DESI DR2)** | **-0.14 +/- 0.21** |
| **Significance (DESI DR2)** | **0.68 sigma** |
| DAIC (pre-DESI DR2) | -2.91 |
| DBIC | -0.91 |
| p-value (one-sided, pre-DESI DR2) | 0.028 |

- **Ledger:** `robustness.py:REFERENCE_FIT`
- **DOI:** 10.6084/m9.figshare.31332730
- **Reproduce:** `python reproduce_efc.py` -> test "reference_fit_significance"

## R2: Leave-One-Out robustness

| Metric | Value |
|--------|-------|
| Pass rate | 7/7 (100%) |
| alpha range | [-1.11, -0.88] |
| alpha spread | 0.23 |
| Criterion | abs(alpha)/sigma >= 1.7 AND DAIC <= 0 |

- **Ledger:** `robustness.py:LOO_RESULTS`
- **DOI:** 10.6084/m9.figshare.31332730, Table 1
- **Reproduce:** `python reproduce_efc.py` -> test "loo_all_pass"

## R3: WP1a sigma_8 suppression

| Metric | Value |
|--------|-------|
| sigma_8 (LCDM) | 0.811 |
| sigma_8 (EFC WP1a) | 0.773 |
| S_8 gap closure | 73% |
| mu_0 | 0.85 |
| B | 0.187 |

- **Ledger:** `mu.py:WP1A_REFERENCE`
- **DOI:** 10.6084/m9.figshare.31333600, Eq. 6
- **Reproduce:** `python reproduce_efc.py` -> test "wp1a_gap_closed"

## R4: Sign lemma (analytical + numerical)

| Metric | Value |
|--------|-------|
| DE^2(z) | <= 0 for all z > 0 |
| Tested A values | 0.01, 0.1, 1.0, 5.0 |
| Verification | Passed for all |

- **Ledger:** `background.py:verify_sign_lemma()`
- **DOI:** 10.6084/m9.figshare.31333414, Lemma 1
- **Reproduce:** `python reproduce_efc.py` -> test "sign_lemma_A=*"

## R5: Unified multi-probe analysis

| Probe | N_data | chi^2_LCDM | chi^2_EFC | Dchi^2 |
|-------|--------|-----------|----------|--------|
| BAO (DESI DR2) | 6 | - | - | - |
| SN Ia (Pantheon+) | 16 | - | - | - |
| RSD (BOSS+eBOSS+DESI) | 11 | - | - | - |
| **Total** | **33** | **49.35** | **50.07** | **+1.72** |

- **Ledger:** `docs/validation-ledger/data/inference.json`
- **DOI:** Unified Analysis paper (figshare)
- **Reproduce:** `python reproduce_bao.py` (diagonal covariance; direction matches published)
- **Note:** Full reproduction with covariance matrix requires DESI DR2 data from Zenodo

## R6: SPARC 175 rotation curves

| Metric | Value |
|--------|-------|
| Galaxies fitted | 175 |
| Screening parameter k | 0.415 +/- 0.029 |
| Cross-scale consistency C | 4.4 |
| EFC win rate | 60.2% |

- **Ledger:** Kill-Test v6 papers
- **DOI:** 10.6084/m9.figshare.31986762
- **Reproduce:** `python reproduce_sparc.py` (loads 175 galaxies, fits 5 representative, verifies kill-test stats)
- **Note:** Full 175-galaxy re-fit takes ~60s; kill-test results verified from archived JSON

## R7: Variant H MCMC (NEGATIVE RESULT)

| Metric | Value |
|--------|-------|
| S_0 | 0.210 +/- 0.141 |
| beta_0 | 2.98 +/- 1.30 |
| DAIC | +4.05 |
| DBIC | +3.94 |
| sigma_8 shift | -1.2% |
| Interpretation | **LCDM preferred** |

- **DOI:** 10.6084/m9.figshare.32037990, Result 4
- **Data:** DESI DR2 BAO (13 pts) + fsigma_8 (7 pts, BOSS DR12 cov) + H(z) (9 pts) + SNIa (40 bins)
- **Interpretation:** Current data show no preference for the entropy-gradient
  growth mechanism.  S_0 is consistent with zero at 1.5 sigma.  This does NOT
  falsify EFC (signal may be below current sensitivity) but establishes a
  quantitative baseline.

## R8: Lensing crossover prediction (UNTESTED)

| z | Sigma_eff | Deviation |
|---|-----------|-----------|
| 0.10 | 1.026 | +2.6% |
| 0.29 | 1.008 | +0.8% |
| 0.44 | 1.000 | crossover |
| 0.58 | 0.994 | -0.6% |
| 0.87 | 0.988 | -1.2% |
| 1.21 | 0.985 | -1.5% |

- **DOI:** 10.6084/m9.figshare.32037990, Result 3, Fig. 1
- **Prediction:** Non-monotonic, sign-changing lensing response.
  Enhanced at z < 0.4, suppressed at z > 0.5, crossover at z ~ 0.44.
  Absent in LCDM and most modified gravity models.
- **Testable by:** Euclid DR1 / Rubin LSST tomographic cosmic shear
- **Sensitivity needed:** Percent-level in Sigma_eff per tomographic bin

## R9: Horndeski no-go (STRUCTURAL)

Standard QS Horndeski with alpha_T = 0 and c_s^2 > 0 cannot produce
mu < 1 and Sigma > 1 simultaneously (Sigma <= mu universally).
EFC breaks this via the Lagrange-multiplier flow constraint.

- **DOI:** 10.6084/m9.figshare.32037990, Result 1
- **Verified by:** Full numerical scan of (alpha_B, alpha_M) parameter space

## Summary: reproduce_efc.py output hash

Run `python reproduce_efc.py` and verify the content hash in
`reproduce_efc_output.json` matches the expected value.
This confirms deterministic reproduction of all results above.
