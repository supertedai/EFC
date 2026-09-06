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

- **`efc_sync_dois.py`** — DOI sync engine. Walks every paper
  directory, discovers the paper's canonical Figshare DOI from any of
  `index.json` / `metadata.json` / `CITATION.cff` / `<slug>.jsonld` /
  `README.md` header, reconciles conflicts, and in `--apply` mode
  propagates the canonical DOI into every in-package metadata file that
  is missing it. Also syncs the top-level `efc_index.json` entries and
  the ledger evidence registers. Non-destructive and idempotent.
  See the [DOI sync](#doi-sync) section below.

- **`efc_verify.py`** — Non-destructive consistency checker. Runs eight
  invariants (see below) and exits 1 on error, 0 on clean / warnings only.

- **`efc_maintain.py`** — Orchestrator. Runs the full pipeline:
  `efc_gen_ai_friendly` → `efc_sync_dois --apply` → `efc_gen_ai_friendly`
  (re-run to reflect byte-size drift) → `efc_verify`. Invoked by the
  `SessionStart` hook in `.claude/settings.json` and by CI
  (`.github/workflows/efc-verify.yml` and `efc-sync.yml`).

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
| C9 | `efc:` namespace (`efc_ontology.py`): every JSON-LD document binds `efc` to `https://supertedai.github.io/EFC/ontology#` (measured 2026-09-05: nine different bindings, none a vocabulary), every `efc:` term in use — prefixed, `@vocab`-bound or context-aliased — is declared in `docs/ontology.jsonld`, and `docs/ontology.{jsonld,html}` are byte-fresh (`efc_maintain.py` runs `--apply`; `--rewrite` was the one-time migration). Declared limits: strings that start with `efc:` but are not a local name (`efc:term/x`, IRIs with spaces) are LISTED, not declared or failed — the registry's job; and a term "used as value" is a string literal in the sources, not an IRI, until the registry attaches it. Identity, not meaning. |
| C8 | Per-paper DOI consistency. Every source that declares a DOI inside a paper directory (`index.json`, `metadata.json`, `CITATION.cff`, `*.jsonld`) must declare the **same** canonical Figshare DOI. Hard error on conflict. |

## The epistemic rule the verifier enforces

Three evidence layers are kept strictly separate:

1. **EFC publications with their own Figshare DOI** → `evidence-register.json` / `ledger.json` empirical list.
2. **Third-party arXiv publications** → `§4b` in the public HTML ledger, marked `[external — …]`, status `no EFC working note yet`.
3. **EFC working notes that confront an external result** → their own Figshare DOI, their own report ID (EFC-VAL-2026-0XX), entered in (1), and the corresponding `§4b` status line flipped to `confronted in [DOI]`.

Any violation of this separation is claim inflation and is rejected by the
verifier.

## DOI sync

`efc_sync_dois.py` is the new keep-it-fresh layer for Figshare DOIs.
When you register a new DOI (i.e. upload the paper to Figshare and want
its deposit DOI tracked in the repo), the only manual step required is:

1. Put the DOI in **one** of these three places for the relevant paper:
   - `docs/papers/efc/<paper>/index.json` → add `"doi": "10.6084/m9.figshare.NNNNNNNN"`
   - `docs/papers/efc/<paper>/metadata.json` → add `paper.doi`
   - `docs/papers/efc/<paper>/CITATION.cff` → add a top-level `doi:` field

2. Commit and push. The `.github/workflows/efc-sync.yml` action takes
   it from there and auto-commits:
   - Writes the same DOI to the other two metadata files above
   - Writes the DOI to the paper's `<slug>.jsonld` (`identifier`,
     `sameAs`, `doi`)
   - Regenerates `ai_manifest.json`
   - Adds a `doi` field to the matching entry in
     `docs/papers/efc/efc_index.json`
   - Mirrors the DOI into `docs/validation-ledger/data/evidence-register.json`
     and `docs/validation-ledger/data/ledger.json` if the paper has a
     matching test entry in `tests.json`
   - Refreshes the catalogue `ai_friendly_index.json`

3. **Manual drift** (things the script intentionally does *not*
   auto-fix, because the insertion point is editorial):
   - Paper `README.md` DOI badge in the header block
   - Top-level `README.md` NEW entry / validation-reports table row
   - Public HTML (`EFC_Validation_Ledger.html`,
     `EFC_Changelog.html`, `EFC_White_Paper_Series.html`)

   The sync script **reports** these as "manual drift" so you know
   what's left. It never silently rewrites Markdown prose or HTML body
   content.

4. **Conflicts**: if two in-package files declare different DOIs (e.g.
   you edited `index.json` to DOI-A but `CITATION.cff` still has
   DOI-B), the sync refuses to propagate and exits with error C8. You
   must reconcile manually — the script will not guess which one you
   meant.

## How it runs

- **On every Claude Code session start**: `.claude/settings.json` fires
  a `SessionStart` hook that runs `efc_maintain.py`. The exit code is
  suppressed so it never blocks the session, but the report is printed.
- **On every push to a development branch**: the
  `.github/workflows/efc-sync.yml` action runs the full maintenance
  pipeline and **auto-commits drift corrections back to the branch** so
  you never have to run the scripts manually after editing a DOI. Skips
  `main` (which is protected and only changes via merged PRs).
- **On every pull request and push to `main`**: the strict read-only
  `.github/workflows/efc-verify.yml` action runs the generator and
  verifier and fails if there's any uncommitted drift. This keeps
  reviewed branches honest.
- **Nightly at 05:30 UTC** (`efc-sync.yml` schedule): catches drift
  that slipped in via direct web edits or rebases.
- **Manually**: `python3 scripts/maintenance/efc_maintain.py` at any
  time.

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

Once you have a Figshare DOI, add it to `index.json` `doi` field and
push. The `efc-sync` action will propagate it through the rest of the
stack automatically. Then manually add:

- A NEW entry in the top-level `README.md`
- An entry in `docs/public/EFC_Validation_Ledger.html` Section 6
- An entry in `docs/public/EFC_Changelog.html`
- If empirical: a `physics_test` entry in `docs/validation-ledger/data/tests.json`
  (with `paper_directory` set to the directory name so the sync script
  can mirror it into `evidence-register.json` / `ledger.json`
  automatically)
