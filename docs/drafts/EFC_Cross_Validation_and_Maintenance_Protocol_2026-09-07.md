# Cross-validation of Energy-Flow Cosmology evidence and maintenance controls

**Status:** Draft for independent review — not peer-reviewed, DOI-issued, committed, or published
**Date:** 2026-09-07
**Repository:** `supertedai/EFC`, commit `5ef8f8a69de625226b31137ef1a2ed34e3a13dc9`
**Author/context:** Symbiose Research / EFC maintenance and validation workflow
**ORCID:** `0009-0002-4860-5095`

## Abstract

We report a repository-level cross-validation of the Energy-Flow Cosmology (EFC) evidence, provenance, public HTML surface, validation ledgers, DOI/ORCID identity records, and automated maintenance controls. The audit does not establish EFC as an empirically confirmed cosmological theory. It establishes a reproducible control result: the repository's distinct machine-evidence, narrative-truth, internal-documentation, and public-presentation artifacts can be checked as separate but linked roles; a DOI identity error was corrected against ORCID and Figshare; false status drift in the KC tables was removed by row-scoped parsing; and placeholder DESI Y1 data were reclassified so that no LCDM or EFC fit is claimed. The final cross-validation gate passes with zero errors and three explicit warnings. The remaining warnings concern pending external data and poor fit quality, not hidden evidence of EFC support.

The updated public-facing scientific interpretation is deliberately bounded. Stage-III values for KiDS Legacy, HSC Y3, and their combined summary are **consistent with** an EFC growth-sector value near `sigma8 ≈ 0.805`, but the audit found no complete readback proving a blind pre-data prediction. The claim therefore remains `PARTIAL SUPPORT / CONSISTENT WITH`, not `CONFIRMED`.

## 1. Scope and epistemic policy

This work audits the chain:

```text
source data → schema → validator → ledger → public HTML → changelog/index
          ↘ DOI / Figshare / ORCID provenance
          ↘ cron maintenance and Kanban control
```

The following distinctions are enforced:

- DOI identity is not evidence that a scientific claim is true.
- An external observation is not an EFC test unless the EFC prediction, observable, likelihood, and falsifier are explicit.
- A sealed prediction is not an observed outcome.
- A placeholder dataset is not a fit.
- A low chi-squared or high chi-squared result must retain its data and model provenance.
- `consistent with` is not equivalent to `confirms EFC`.
- Robust and fragile EFC branches are separate claims.

## 2. Versioned artifact roles

Cross-validation showed that no single file is a global ledger. The artifacts have different roles:

| Artifact | Role | Version/status |
|---|---|---|
| `docs/validation-ledger/data/ledger.json` | Machine test/evidence track used by the cross-validator | v3.0 |
| `docs/validation-ledger/data/ledger_truth.json` | Canonical narrative truth-ring for numbers, status, and DOI corpus | v1.0 |
| `docs/validation-ledger/index.md` | Current internal narrative documentation | v4.2 |
| `docs/public/EFC_Validation_Ledger.html` | Public presentation surface | v3.18; contains historical/internal update marker v4.6 |
| `docs/validation-ledger/data/inference.json` | Inference-module status and fit metadata | current working data |

The repository therefore has both a current internal narrative file version (`index.md` v4.2) and a historical/internal update marker (`v4.6`) embedded in the public ledger's version history. The latter is not silently substituted for the former. Version differences are not treated as drift when the role declaration and truth-ring are present. Silent merging of these artifacts is prohibited.

## 3. Provenance correction

The repository and public surface contained the identifier `10.6084/m9.figshare.31140000`. Cross-validation found that this was an incorrect identifier. The correct work is:

- **DOI:** `10.6084/m9.figshare.31144030`
- **Title:** *Regime-Dependent Growth Enhancement: A Transition Metric Interpretation of the Fugaku–DESI Matter Density Offset*
- **Date:** 2026-01-24
- **Independent checks:** ORCID `0009-0002-4860-5095`, DOI resolver, and Figshare API

The corrected identifier was propagated to the test ledger, machine ledger, internal index, Atlas, and DOI coverage report. The change corrects identity and provenance; it does not upgrade the associated scientific status.

## 4. Stage-III and sigma8 claim

The public ledger records the following summaries:

| Source | Summary | Audit interpretation |
|---|---:|---|
| KiDS Legacy | `S8 = 0.815 ± 0.016` | Current external observation |
| HSC Y3 | `S8 = 0.805 ± 0.022` | Current external observation |
| Stage-III combined | `S8 = 0.813 ± 0.012` | Current combined summary |
| Planck reference | `S8 = 0.834 ± 0.016` | Early-universe/CMB reference |
| EFC growth-sector value | `sigma8 ≈ 0.805` | EFC implication/claim, not blind confirmation |

The audit does **not** establish the complete chain:

```text
BAO locks beta ≈ 0.08
→ beta mathematically yields sigma8 ≈ 0.805
→ value was sealed before Stage-III data
→ independent holdout confirms it
```

Required readback before upgrading the status:

1. pre-data timestamp and hash;
2. explicit `beta → sigma8 → S8` transformation;
3. `Omega_m`, priors, uncertainty, and covariance;
4. O-layer likelihood on shear/clustering/lensing observables;
5. independent holdout evaluation.

Therefore the public status is:

```text
PARTIAL SUPPORT / CONSISTENT WITH — not CONFIRMED
```

## 5. Robustness branches

The audit preserves the branch distinction:

- **Robust branch:** `mu < 1`, `eta → 1`, `Sigma ≈ 0.99`, approximately `S8 ≈ 0.82`.
- **Fragile branch:** eta-boost values such as `S8 ≈ 0.847` and `E_G ≈ 1.086`, classified as dependent on the fragile slip branch and not the main robust prediction.

The fragile branch must not be used to present a stronger EFC result than the robust model supports.

## 6. KC status control

The previous KC cross-check used a document-wide regular expression. Because public pages contain historical and summary text, this could associate an unrelated `DONE` badge with the wrong KC row.

The validator now reads the row identified by `data-kc-id` and extracts the status inside that row. KC1 was also clarified:

- the prediction artifact is sealed;
- the executable full-shape `P(k)` likelihood pipeline is not assembled;
- the correct status is `PIPELINE NEEDED`, not `PREDICTION READY` as a proxy for a completed likelihood.

After this correction:

```text
Roadmap §12 and Gap Analysis KC statuses match (5 KCs)
```

## 7. DESI Y1 placeholder control

`bao_desi_y1` contained placeholder data described as having unphysical `D_H(z)` values and non-DESI redshift bins. It was previously classified as `lcdm_stub`, which caused the gate to report a false critical inference result.

It is now classified as:

```text
pending_placeholder
```

This means:

- placeholder data are rejected;
- no LCDM fit is claimed;
- no EFC fit is claimed;
- no model preference is claimed;
- DOI-anchored real DESI DR1/DR2 data and a native EFC likelihood are required.

## 8. Final verification

The following controls were run against the working tree:

| Control | Result |
|---|---|
| `efc_cross_validate.py` | PASS, 0 errors, 3 warnings |
| `efc_verify.py` | 0 errors, 0 warnings |
| `efc_narrative_consistency.py` | 0 warnings |
| `efc_page_consistency.py` | all invariants hold |
| `efc_rootfile_consistency.py` | public v3.18/internal v4.6 consistent |
| JSON parsing | ledger, tests, inference OK |
| HTML parsing | 14/14 public HTML pages OK |
| `git diff --check` | OK |
| `efc_full_sync.py --verify` | 0 errors, 1 package-completeness warning |

The three cross-validation warnings are explicit:

1. DESI Y1 placeholder pending, no fit claimed;
2. `cluster_core_state`, reduced chi-squared `108.8`;
3. `shear_kids1000`, reduced chi-squared `10.4`.

The package-completeness warning is retained rather than repaired with empty directories or invented metadata.

## 9. Maintenance and cron protocol

Two scheduled jobs are now updated and reference Kanban card `t_79d0e6e3`:

- `c3524cdbdf36` — EFC repository/public HTML maintenance;
- `92c5a50bfc62` — EFC cross-domain model coverage.

The updated control rules require:

1. preserve pre-existing git dirty state;
2. identify artifact roles before comparing versions;
3. verify DOI identity against ORCID, resolver, and Figshare API;
4. parse KC rows structurally by `data-kc-id`;
5. separate sealed prediction from executable likelihood readiness;
6. classify rejected placeholder data as `pending_placeholder`;
7. report `PASS`, `WARN`, or `BLOCK` rather than silently repairing claims;
8. keep robust and fragile EFC branches separate;
9. never create `output/parameters.json` without an entailed source-to-schema path;
10. never push, merge, or publish automatically.

## 10. What this work establishes — and does not establish

### Established by this audit

- repository/public-surface provenance controls are executable;
- the DOI identity error is corrected and independently cross-checked;
- ledger roles are explicit and validator-aware;
- KC status comparison is structurally scoped;
- placeholder data no longer produce a false LCDM/EFC inference claim;
- the public Stage-III interpretation is epistemically bounded;
- the maintenance cronjobs carry the corrected rules;
- the final cross-validation gate passes with explicit warnings.

### Not established by this audit

- a blind EFC prediction of the Stage-III `sigma8` value;
- an externally confirmed EFC cosmological theory;
- a full O-layer joint likelihood;
- an independent holdout success;
- a resolved DESI Y1 native EFC fit;
- a good fit for `cluster_core_state` or `shear_kids1000`;
- peer review or publication acceptance.

## 11. Reproduction

From the repository root:

```bash
python scripts/maintenance/efc_cross_validate.py
python scripts/maintenance/efc_verify.py
python scripts/maintenance/efc_narrative_consistency.py
python scripts/maintenance/efc_page_consistency.py
python scripts/maintenance/efc_rootfile_consistency.py
python scripts/maintenance/efc_full_sync.py --verify
python -m py_compile scripts/maintenance/efc_cross_validate.py \
  scripts/maintenance/efc_verify.py \
  scripts/maintenance/sync_engine/invariants.py
```

## 12. Publication state

This manuscript is a **reviewable working draft**. It is not a DOI-bearing EFC publication, not peer-reviewed, and not published to the public HTML surface. Any future publication must preserve this distinction and add a DOI, version, hash, author approval, and independent review record before entering the EFC publication ledger.
