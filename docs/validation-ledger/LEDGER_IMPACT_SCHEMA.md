# `ledger_impact` schema

## Purpose

Each empirical / sealed paper declares, in a machine-readable block inside
its own `index.json`, exactly how it should affect the Validation Ledger
and Gap Analysis once its DOI is registered. `scripts/maintenance/efc_ledger_impact_sync.py`
reads that block and mutates `tests.json`, `stats.json`, and the Gap
Analysis HTML **deterministically and idempotently** — no LLM judgment,
no HTML regex dancing, no silent drift.

## Lifecycle

```
  PDF uploaded
       │
       ▼
  efc_auto_metadata.py            index.json skeleton created
       │                          ledger_impact: absent
       ▼
  efc_ai_brain.py (LLM)           key_results, kill_criteria, paper_type
       │                          ledger_impact: suggested (status=draft)
       ▼
  human review + commit           ledger_impact finalized (status=ready)
       │
       ▼
  DOI registered                  index.json["doi"] populated
       │
       ▼
  efc_sync_dois.py                DOI propagated into per-paper files
       │
       ▼
  efc_ledger_impact_sync.py       PICKS IT UP HERE:
                                    - reads ledger_impact from index.json
                                    - only fires if doi + status=ready
                                    - mutates tests.json / stats.json /
                                      Gap_Analysis.html
                                    - stamps applied_at + applied_by_doi
                                    - idempotent: re-runs are no-ops
```

If `doi` is missing → script skips, paper stays in "maintainer mode"
(no ledger mutations). If `ledger_impact` is missing on an empirical
paper with a DOI → `efc_precommit_gate.py` warns (and eventually blocks).

## Schema

```jsonc
{
  "doi": "10.6084/m9.figshare.32029704",
  "ledger_impact": {
    "status": "ready",          // "draft" | "ready" | "applied"
    "applied_at": null,         // ISO8601; set by sync script
    "applied_by_doi": null,     // bare DOI; idempotence guard

    // NEW test rows to add to tests.json
    "tests_added": [
      {
        "test_id": "sparc175_local_multiplicative_elimination",
        "category": "physics_test",     // must match tests.json categories
        "name": "SPARC 175: local-multiplicative gravity elimination",
        "description": "...",
        "result": "COLLAPSED",          // matches existing result vocabulary
        "status": "success",            // success | partial | failed | pending | unknown
        "data_source": "SPARC 175 rotation curves (3391 radial points)",
        "prediction": "..."
      }
    ],

    // EXISTING test rows to patch (by test_id)
    "tests_updated": [
      {
        "test_id": "conv_kt_3_locked_transfer_universality_sparc_clusters_f_8_bullet_",
        "new_result": "MARGINAL",
        "new_status": "partial",
        "evidence_summary": "Partial: SPARC leg confirmed but Bullet-cluster leg pending."
      }
    ],

    // Gap rows in Gap_Analysis.html to mark CLOSED (by data-gap-id)
    "gaps_closed": [
      "theory-multicomponent-sparc-universality"
    ],

    // Free-text cross-references — not machine-consumed, just
    // for human reviewers and LLM context
    "kill_criteria_addressed": ["KC1", "KC2"]
  }
}
```

## Result vocabulary (`tests.json`)

Concrete set observed in current tests.json (keep new entries inside this
vocabulary — extend only with human review):

- `PASS` — test passed
- `MARGINAL` — partially confirmed
- `COLLAPSED` — falsified
- `Planned` — not executed yet
- `REQUIRES_EXTERNAL_TOOL` — blocked on tooling
- `PIPELINE_NOT_READY` — blocked on pipeline
- `DEGENERACY_LIMITED` — result bounded by parameter degeneracy
- Descriptive free-text (e.g. "αL2= 0.040 ± 0.024 (1.7σ)") — allowed but
  discouraged in new entries

Only `COLLAPSED` counts toward `stats.json["n_falsified"]` recount.

## Gap IDs

Gap rows in `docs/public/EFC_Gap_Analysis.html` are identified by
`<tr data-gap-id="...">`. Slug convention:

  `<section-slug>-<short-topic-slug>`

Known sections:
- `kill-criteria-*` — §2 Kill Criteria Readiness
- `theory-*` — §3 Theory Gaps
- `external-landscape-*` — §1 External Landscape

New gap rows added to the HTML **must** carry a stable `data-gap-id`
so `ledger_impact.gaps_closed` can reference them without regex
matching on free text.

## Idempotence

The sync script writes `applied_at` + `applied_by_doi` into the
`ledger_impact` block after successfully applying. On subsequent
runs:

- If `applied_by_doi == current doi` → skip, no mutation
- If `applied_by_doi != current doi` (e.g. DOI changed) → warn, require
  human to manually clear `applied_at` + `applied_by_doi` and re-run
- If `status == "draft"` → skip, warn "finalize before sync"

## Failure modes (hard errors)

The sync script refuses to apply and exits non-zero when:

- A `tests_updated` entry references a `test_id` that doesn't exist
- A `tests_added` entry uses an unknown `category`
- A `gaps_closed` entry references a `data-gap-id` not present in the HTML
- `result` value in `tests_added` is outside the known vocabulary
  (can be overridden with `--allow-new-vocab`)

## Writing a `ledger_impact` block

For humans: copy the schema above into the paper's `index.json`, fill in
what the paper actually changes, leave lists empty if not applicable.
Set `status: "ready"` when done.

For LLM-assisted drafting (`efc_ai_brain.py`): generate with
`status: "draft"` and let a human flip to `ready` after review.
