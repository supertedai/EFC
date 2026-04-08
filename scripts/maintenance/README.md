# EFC Repository Maintenance

This directory contains the automation that keeps the EFC paper archive,
validation ledger, and AI-friendly metadata layer consistent.

## Files

- **`efc_gen_ai_friendly.py`** — Walks every directory under
  `docs/papers/efc/` and ensures each has the uniform AI-friendly metadata
  layer (`index.json`, `metadata.json`, `ai_manifest.json`, `<slug>.jsonld`,
  `README.md`). Hand-curated packages are preserved: existing files are
  never overwritten. `ai_manifest.json` is the one exception — it is
  always regenerated so the file inventory stays accurate. Writes the
  catalogue `docs/papers/efc/ai_friendly_index.json`.

- **`efc_verify.py`** — Non-destructive consistency checker. Runs seven
  invariants (see below) and exits 1 on error, 0 on clean / warnings only.

- **`efc_maintain.py`** — Orchestrator. Runs the generator then the
  verifier. Invoked by the `SessionStart` hook in `.claude/settings.json`
  and by CI (`.github/workflows/efc-verify.yml`).

## Invariants checked by `efc_verify.py`

| Code | What it checks |
|------|---------------|
| C1 | Every paper directory has `index.json`, `metadata.json`, `ai_manifest.json`, `README.md`, and at least one `*.jsonld`. |
| C2 | `data/evidence-register.json` and `data/ledger.json` empirical lists contain only 8-digit Figshare DOIs (no arXiv IDs, no free text). |
| C3 | The public HTML ledger contains no forbidden phrases (`confirms EFC`, `proves EFC`, `validates EFC`, …) outside the §4b external block. |
| C4 | Version consistency within each track: `ledger.json` ↔ `validation-ledger/index.md` (internal v4.x), HTML footer (public v3.x). The two tracks are independent on purpose. |
| C5 | `ai_friendly_index.json` is present and its `n_packages` equals the number of directories on disk. |
| C6 | No arXiv IDs have leaked into the JSON evidence registers. |
| C7 | §4b entries carry the `[external — …]` tag. |

## The epistemic rule the verifier enforces

Three evidence layers are kept strictly separate:

1. **EFC publications with their own Figshare DOI** → `evidence-register.json` / `ledger.json` empirical list.
2. **Third-party arXiv publications** → `§4b` in the public HTML ledger, marked `[external — …]`, status `no EFC working note yet`.
3. **EFC working notes that confront an external result** → their own Figshare DOI, their own report ID (EFC-VAL-2026-0XX), entered in (1), and the corresponding `§4b` status line flipped to `confronted in [DOI]`.

Any violation of this separation is claim inflation and is rejected by the
verifier.

## How it runs

- **On every Claude Code session start**: `.claude/settings.json` fires a
  `SessionStart` hook that runs `efc_maintain.py`. The exit code is
  suppressed so it never blocks the session, but the report is printed.
- **On every pull request and push to main**: the GitHub Action in
  `.github/workflows/efc-verify.yml` runs the generator, then the
  verifier, then fails if the generator produced any uncommitted diff
  (catches stale `ai_manifest.json` files).
- **Manually**: `python3 scripts/maintenance/efc_maintain.py` at any time.

## Adding a new paper

Mirror the hand-curated reference packages
(`docs/papers/efc/WP4_BOSS_transfer_validation/` or
`docs/papers/efc/Multi_epoch_Growth_Rate_Test_of_EFC/`). Required files:

- `README.md`
- `index.json` + `metadata.json` + `schema.json`
- `<slug>.jsonld`
- `citations.bib`
- `data/` with CSV inputs and JSON outputs
- `src/` with the analysis script
- `examples/reproduce_minimal.py`
- the paper PDF

Then run `efc_maintain.py` to regenerate the manifest and catalogue,
update the ledger (`evidence-register.json`, `ledger.json`, HTML §4 + §6),
and commit.
