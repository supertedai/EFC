# EFC public-surface truth policy

**Scope:** all 14 files under `docs/public/`
**Control card:** `t_79d0e6e3`
**Canonical truth layers:** `ledger_truth.json` → machine/evidence ledger → generated/public views

## Rule

The 14 public HTML pages are one public truth surface, not 14 independent documents. A material finding must be impact-mapped across all pages before publication. Pages that do not require a content change must still be checked and recorded as `no-change`.

## Public surface inventory

1. `EFC_Atlas.html`
2. `EFC_Changelog.html`
3. `EFC_Elevator_Pitch.html`
4. `EFC_Evaluation_Ledger.html`
5. `EFC_External_Research_Ledger.html`
6. `EFC_Gap_Analysis.html`
7. `EFC_Likelihood_Ledger.html`
8. `EFC_Master_v1.1.html`
9. `EFC_Model_Comparison.html`
10. `EFC_Predictions.html`
11. `EFC_Stage-IV_Data_Roadmap.html`
12. `EFC_System_Health.html`
13. `EFC_Validation_Ledger.html`
14. `EFC_White_Paper_Series.html`

## Propagation matrix

| Finding type | Pages that must be checked | Typical update surfaces |
|---|---|---|
| New external evidence | all 14; especially External Research, Validation, Gap, Predictions, Changelog | source/status/provenance |
| Prediction/status change | all 14; especially Predictions, Validation, Roadmap, Gap, Model Comparison, Changelog | status, branch, falsifier, holdout |
| DOI/provenance correction | all pages containing the identifier plus Atlas, Validation, External Research, Changelog | exact identifier and source link |
| Ledger/count/schema change | all pages showing counts/status/version plus System Health and Changelog | generated count/version/readback |
| New or revised model/parameter | all 14; especially Master, Model Comparison, Likelihood, Validation, Roadmap, White Paper | Tier C unless human-approved |
| Maintenance/navigation change | all 14 | navbar, local links, visible update marker |

## Update-facing pages

The following pages must remain current because they are the visible update/control surfaces:

- `EFC_Changelog.html`
- `EFC_System_Health.html`
- `EFC_Validation_Ledger.html`
- `EFC_Gap_Analysis.html`
- `EFC_Stage-IV_Data_Roadmap.html`
- `EFC_Predictions.html`
- `EFC_External_Research_Ledger.html`

A run must record their current status even when the correct result is `no-change`.

## Required run output

Every maintenance/adjudication run must report:

```text
public_surface_count: 14
pages_scanned: 14
pages_changed: [...]
pages_no_change: [...]
update_surfaces_checked: 7
local_links_broken: 0
truth_source:
claim_status_changes:
provenance_changes:
rollback:
publication_readback:
```

A run is not complete if it updates one page while leaving a contradictory status, count, DOI, branch, version, or update marker on another page.

## Publication gate

Before Tier A/B auto-publication:

1. scan all 14 pages;
2. compare claims/counts/statuses against the truth layers;
3. update every affected page and generated changelog/index;
4. keep unaffected pages explicitly recorded as `no-change`;
5. run HTML parse, local-link, navbar, page/root/narrative, ledger and cross-validation gates;
6. read back the exact published target and verify the update marker/changelog.

Do not invent a public update merely to make all pages contain identical prose. A shared truth surface means consistent claims and provenance, not identical content on every page.
