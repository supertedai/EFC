# EFC Key Results with Ledger Bindings

Each result below links to the specific ledger entry, code function,
and DOI that produced it.

**Significance disclaimer:** The strongest current signal is 2.2 sigma
(fsigma_8 growth suppression).  This is below the 3-sigma threshold
for a firm detection.  All results should be read as *suggestive
indications*, not established claims.  Decisive tests require Stage-IV
data (DESI DR3, Euclid DR1, CMB-S4).

## R1: fsigma_8 growth suppression

| Metric | Value |
|--------|-------|
| alpha | -1.00 +/- 0.46 |
| Significance | 2.20 sigma |
| DAIC | -2.91 |
| DBIC | -0.91 |
| p-value (one-sided) | 0.028 |

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

## Summary: reproduce_efc.py output hash

Run `python reproduce_efc.py` and verify the content hash in
`reproduce_efc_output.json` matches the expected value.
This confirms deterministic reproduction of all results above.
