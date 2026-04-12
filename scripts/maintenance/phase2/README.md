# EFC Maintenance — Phase 2 Staging Area

**Status: STAGED, NOT ACTIVE.** Nothing in this directory runs
automatically. The scripts here are a future rewrite of the
maintenance pipeline that will make `docs/validation-ledger/ledger.json`
the single source of truth for the validation ledger, with the public
HTML, README badge, and roadmap auto-generated from it.

They are stored here so you can read, inspect, and experiment with
them without risk to the production Phase 1 pipeline.

## Why they're staged rather than installed

Three concrete conflicts with the current repo layout prevent a
drop-in replacement:

### Conflict 1: `index.json` schema mismatch (138 files)

The current `docs/papers/efc/<paper>/index.json` files follow a
**paper-metadata schema** with ~27 fields (`id`, `title`, `doi`,
`figshare_url`, `headline_result`, `probe_results`, `cobaya_runs`,
`regime_architecture`, `falsification_criteria`, `related_papers`,
`resolved_questions`, …).

`phase2/efc_gen_ai_friendly.py::generate_index_json()` writes a
**file-listing schema** (`package`, `version`, `generated`, `files[]`).

If the Phase 2 generator is run against the current repo, it will
**overwrite 138 paper-metadata files** with file listings, destroying
the entire Phase 1 DOI-propagation work.

**Before promoting:** rewrite the generator to preserve the existing
schema, or create a migration step that merges the file-listing view
into a separate file (e.g. `files.json`).

### Conflict 2: `ledger.json` entry count mismatch

The current `docs/validation-ledger/data/ledger.json` has **103 test
entries** (35 physics_test + 17 consistency_check + 13 phenomenological
+ 23 framework_constraint + 15 planned_pipeline) and **23 empirical
DOIs** in `evidence_register.empirical`.

The sample `phase2/ledger.json` has **8 entries**. It is a format
template, not a migration of the real data.

If `phase2/efc_render_ledger.py` is run against the sample, it will
regenerate `docs/public/EFC_Validation_Ledger.html` from the 8-entry
file and **lose 95 test entries** from the public HTML.

**Before promoting:** write `phase2/efc_bootstrap_ledger.py` that
parses the live 2135-line HTML and the `data/*.json` files into a
complete `ledger.json` with all 103 entries. Then run the renderer and
diff against the original HTML to catch regressions.

### Conflict 3: Public HTML content regression

The current `docs/public/EFC_Validation_Ledger.html` is **2135 lines**
of hand-curated content including: stage banner, elevator pitch,
executive summary, §0.0 regime coordinates, §0.1 status key, §0.2
parameter registry, §0.3 regime-observable matrix, §1 main
validation table, §1.1 discrete gravity, §1.2 phenomenological, §2
methodological notes, §3 planned pipeline, §3.1 falsification
conditions, §4 evidence register, §4b external observations, §5
pipeline, §6 recent updates (18 versioned entries), footer.

`phase2/efc_render_ledger.py` produces a **~200-line dark-theme HTML**
with only: stage summary, main table, discrete gravity table,
phenomenological table, falsification table, evidence register,
footer. No elevator pitch, no §0.x architecture, no §2 methodology,
no §3 pipeline details, no §4b externals, no §6 changelog.

If the renderer is run against the live path, **2135 → ~200 lines**
of content is lost.

**Before promoting:** extend the renderer to produce the full current
layout, or accept the content loss and move the missing sections to
separate auto-generated pages.

## Removed epistemic checks in the Phase 2 verifier

The Phase 2 `efc_verify.py` has new C1–C8 semantics that **drop**
three invariants currently enforced by Phase 1:

| Phase 1 check | What it enforced | Phase 2 replacement |
|---|---|---|
| C2 (Phase 1) | No arXiv IDs in `evidence-register.json` / `ledger.json` empirical lists | Dropped — Phase 2 C2 checks DOI↔paper bidirectional |
| C3 (Phase 1) | No forbidden phrases (`confirms EFC`, `proves EFC`, `validates EFC`) outside §4b external block | Dropped — Phase 2 C3 checks paper-DOI appears in ledger |
| C6 (Phase 1) | No arXiv ID leakage | Dropped — Phase 2 C6 checks falsification-condition completeness |
| C7 (Phase 1) | §4b entries carry `[external — …]` tag | Dropped — Phase 2 C7 checks status-tier hierarchy |

These Phase 1 invariants exist to **prevent claim inflation**: they
enforce the three-layer separation between EFC publications,
third-party arXiv preprints, and EFC working notes that confront
external results. Dropping them without a replacement lets
third-party results creep into the EFC empirical register.

**Before promoting:** merge the Phase 1 tree-layer invariants into
the Phase 2 verifier as C9/C10/C11 so the epistemic discipline is
preserved.

## Staged files

| File | Role | Destructive if run? |
|---|---|---|
| `efc_gen_ai_friendly.py` | PDF extraction + manifest generation | **YES** — overwrites 138 `index.json` files |
| `efc_sync_dois.py` | Cross-ref + auto-checkbox logic | Only if `ledger.json` exists at the Phase 2 path |
| `efc_render_ledger.py` | Render HTML from ledger.json | **YES** — overwrites the live `EFC_Validation_Ledger.html` |
| `efc_verify.py` | Phase 2 C1–C8 invariants | No (read-only), but drops Phase 1 epistemic checks |
| `efc_maintain.py` | Orchestrates all four above | **YES** via the destructive children |
| `ledger.json` | Sample ledger with 8 entries | No (read-only, sample data) |
| `README.md` | This file | No |

## Migration checklist (when you're ready)

1. Write `phase2/efc_bootstrap_ledger.py` that consumes:
   - `docs/validation-ledger/data/ledger.json` (103 tests)
   - `docs/validation-ledger/data/evidence-register.json` (23 empirical)
   - `docs/validation-ledger/data/tests.json` (same 103 tests)
   - `docs/public/EFC_Validation_Ledger.html` (for hand-curated prose)

   and produces a complete `docs/validation-ledger/ledger.json` with
   every existing entry and correct status/tier assignments.

2. Extend `phase2/efc_render_ledger.py` to produce the full 2135-line
   layout: stage banner, elevator pitch (link to `EFC_Elevator_Pitch.html`),
   executive summary, §0.x architecture, §1 main + §1.1 + §1.2 tables,
   §2 methodology, §3 pipeline + §3.1 falsification, §4 evidence + §4b
   externals, §5 pipeline, §6 recent updates. Round-trip diff against
   the current HTML until zero semantic drift.

3. Rewrite `phase2/efc_gen_ai_friendly.py` to **preserve** the existing
   paper-metadata `index.json` schema and only regenerate
   `ai_manifest.json` (as Phase 1 does). Add a separate `files.json`
   for the file-listing view if that capability is still wanted.

4. Merge the dropped Phase 1 invariants (no-arXiv-leakage,
   forbidden-phrase guard, §4b external-tag) into the Phase 2
   verifier as C9/C10/C11.

5. Install `pdftotext` (poppler-utils) in both `efc-sync.yml` and
   `efc-verify.yml`, and add a graceful-degradation path for local
   runs where poppler isn't available (the Phase 2 generator already
   returns `""` on ImportError, so local runs produce empty
   `paper_extractions.json` — that's fine as long as downstream
   consumers tolerate empty extractions).

6. Add a feature flag / opt-in: `EFC_PHASE2=1 python3 efc_maintain.py`
   so you can test the new pipeline alongside the old one before
   flipping the default.

7. Run `efc_maintain.py` with the flag, diff every touched file
   against its pre-run state, and only promote Phase 2 to the default
   once the diff is reviewed and approved.

## Running any of these scripts

None of the scripts in this directory are invoked by:

- `.claude/settings.json` SessionStart hook
- `.github/workflows/efc-sync.yml`
- `.github/workflows/efc-verify.yml`
- `scripts/maintenance/efc_maintain.py` (main orchestrator)

They are reachable only if you explicitly invoke them:

```bash
# Read-only test (safe — uses the sample 8-entry ledger.json):
python3 scripts/maintenance/phase2/efc_verify.py \
    --root scripts/maintenance/phase2

# DESTRUCTIVE — would overwrite 138 index.json files:
python3 scripts/maintenance/phase2/efc_gen_ai_friendly.py     # DON'T

# DESTRUCTIVE — would overwrite the live 2135-line HTML:
python3 scripts/maintenance/phase2/efc_render_ledger.py       # DON'T
```

Each staged script carries a `PHASE2_STAGED` marker at the top of its
docstring and a runtime guard that refuses to run when invoked from
the default working directory unless you pass
`--i-know-this-is-staged`. That prevents accidental execution.

## Phase 1 is still the authoritative pipeline

If you just want things to keep working, you don't need to touch
anything here. Phase 1 (the files directly under
`scripts/maintenance/`, without the `phase2/` prefix) is still the
live pipeline driven by the SessionStart hook and the CI workflows.
