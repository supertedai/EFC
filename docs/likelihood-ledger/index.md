# EFC Likelihood Ledger

> **Purpose**: Make every empirical test in the Validation Ledger reproducible
> by declaring its likelihood pipeline explicitly. No test is "evaluated" in
> the global function (see `evaluation-ledger/`) unless it has a row here.

---

## 1. Schema (summary)

Each row binds a `test_id` to:

| Field | Meaning |
|-------|---------|
| `likelihood_type` | `gaussian` \| `gaussian_cov` \| `binned_chi2` \| `mcmc_posterior` \| `analytic` \| `external` |
| `covariance` | path or DOI of covariance matrix; `diagonal` if independent errors |
| `parameter_priors` | dict: param → `{type, range/mean, sigma}` |
| `code` | `cobaya` \| `mgcamb` \| `cosmoSIS` \| `direct_python` \| `external` (with version pin) |
| `entry_point` | repo-relative script or external URL |
| `inputs` | list of dataset DOIs/refs |
| `outputs` | what the run produces (chi2, posterior, evidence) |
| `status` | `declared` \| `runnable` \| `executed` \| `frozen` |

Full JSON Schema in `schema.json`.

---

## 2. Worked example (template)

```json
{
  "test_id": "s8_growth_fsigma8_2026",
  "likelihood_type": "gaussian_cov",
  "covariance": "data/cov/fsigma8_compilation_2026.json",
  "parameter_priors": {
    "Omega_m": {"type": "uniform", "range": [0.20, 0.40]},
    "sigma8":  {"type": "uniform", "range": [0.70, 0.90]},
    "mu_efc":  {"type": "uniform", "range": [0.80, 1.20]}
  },
  "code": "direct_python",
  "entry_point": "pipelines/fsigma8_runner.py",
  "inputs": [
    "doi:10.xxxx/desi-y3-fsigma8",
    "doi:10.xxxx/des-y6-3x2pt"
  ],
  "outputs": ["chi2", "best_fit", "posterior_summary"],
  "status": "declared"
}
```

---

## 3. Pipeline categories (initial scan)

| Category | Suggested likelihood_type | Code | Notes |
|----------|---------------------------|------|-------|
| BAO (DESI, eBOSS) | `gaussian_cov` | `direct_python` (via `reproduce_bao.py`) | already partly wired |
| CMB sanity | `gaussian` | `direct_python` (`reproduce_cmb_sanity.py`) | extend with full CAMB likelihood for KC tests |
| SPARC rotation curves | `binned_chi2` | `direct_python` (`reproduce_sparc.py`) | covariance assumed diagonal — verify |
| fσ8 / S8 | `gaussian_cov` | TBD (Cobaya?) | NOT YET WIRED — gap |
| Lensing (DES, KiDS, Euclid) | `mcmc_posterior` | `cobaya` + `MGCAMB` | NOT YET WIRED — gap |
| ISW | `gaussian` | `direct_python` | NOT YET WIRED |
| GW propagation (KC6) | `gaussian` | `direct_python` | NEW — not in current ledger |

---

## 4. Open questions (to resolve before population)

1. Should likelihood entries live as separate JSON files per test, or as
   array entries inside `data/likelihoods.json`?
   *Validation-ledger uses a single `tests.json` array — propose mirroring.*
2. How are external likelihood codes (Cobaya/MGCAMB) version-pinned? Git SHA?
3. Should `parameter_priors` reference a global parameter registry
   (`validation-ledger/data/parameters.json` already exists) instead of
   inlining? *Recommended: reference, do not duplicate.*

---

## 5. Sync hook (proposed)

`scripts/maintenance/efc_likelihood_sync.py` (NOT YET WRITTEN):

- Reads every `test_id` in `validation-ledger/data/tests.json`
- For each test with `vl_category in {physics_test, phenomenological}` that
  lacks a likelihood row, emits a warning
- Validates that `inputs` DOIs exist in `validation-ledger/data/evidence-register.json`
- Idempotent; mirrors pattern of `efc_ledger_impact_sync.py`

---

## Status

**DRAFT — 2026-04-23.** Skeleton awaiting maintainer review.
Last updated: 2026-04-23.
