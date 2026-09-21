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
| C10 | JSON Schema gate (`efc_schema_check.py`, own workflow `efc-schema.yml` because it needs `jsonschema`): registered (schema, instance) pairs — likelihood-ledger, framework atlas — are valid against their metaschema, the instance validates, and every object subschema at any depth is CLOSED (`additionalProperties: false`; `{}`/`true` and typed maps count as open; formats such as `date-time` are enforced), so an invented key fails instead of passing silently (measured 2026-09-05: 0 of 16 workflows ran a validator, 0 of ~400 schemas closed). Declared limits: the paper `index.json` → `./schema.json` pairs are NOT gated. Counting rule, so the number can be re-run: every `index.json` in `git ls-files -z` whose `$schema` is a relative path to an existing file, validated against that file with `jsonschema` 4.25.1, where "validates" means the schema itself is valid AND the instance has no errors. Listing files with `git ls-files -z` rather than a glob is part of the rule: a macOS working tree silently drops one half of a case-colliding pair. On `20f81f71` that is **161 pairs, 48 of which validate** and 113 whose instance fails (0 invalid schemas), and **79 distinct schemas once `$id` and `title` are ignored** — 74 of the 161 are unique and 77 share two older templates. The raw text count is 160 and says nothing, because C12 gave every schema its own `$id`. An earlier row said 162/48/115: true when C10 landed, false 47 minutes later when C12 landed, and left standing — that is the failure the counting rule exists to prevent; evaluation-ledger and model-comparison have no instance and are checked as schemas only. `efc_atlas_export.py` validates its snapshot against the same schema before writing. |
| C11 | Concept registry (`efc_concepts.py`): a judgement the model may not make — `efc:registryStatus` other than `candidate`, any `efc:entityType` finer than `concept`, `empiricalStatus`, `mappingStrength`, `falsifier`, `alternativeExplanation` — is accepted ONLY with an `efc:attested` entry naming one of the ORCIDs in the `authors:` block of `CITATION.cff` (all of them, so widening the author list widens who may attest, and a `references:` block cannot hijack the authority), a real calendar date in `YYYY-MM-DD` that is also a real day, a basis, and the same value. One attestation carries one field. `efc:reviewAt` is optional and, once set, enforced: an expired attestation is a problem, which makes this the first gate whose verdict can change with the clock and no commit. `candidate` is free, `canonical` is signed: registry membership is exactly what a model can grant itself, so it is the thing that needs a human. A retired entry names a `dcterms:isReplacedBy` that resolves in the registry. Note that the bookkeeping properties this adds (`efc:entityType`, `efc:registryStatus`, `efc:attested…`) are declared in the vocabulary like any other `efc:` term in use — C9 asserts identity, not meaning, so it carries plumbing too. Every entry carries an `efc:entityType` from a closed list, and the five kinds that are not concepts at all (publication, dataset, artifact, person, organization) are refused with that message and nothing else — no attestation makes a publication a concept. `definition_status` is computed into the generated view, never stored. `docs/concepts.jsonld` is the ONE source for the five core concepts (SKOS: prefLabel/altLabel/notation, broader, inScheme, definition, scopeNote; `dcterms:source` for provenance), against the `efc:` namespace so C9 declares each concept as a `skos:Concept`. `schema/concepts.json` (schema.org DefinedTermSet) and `api/concept-index.json` (ItemList) are generated views and must be byte-fresh (`efc_maintain.py` runs `--apply`); `api/v1/concepts.json` and `api/v1/terms.json` were dead copies and must stay absent. Every `skos:definition` is a verbatim sentence from a document in the tree, named by `efc:definitionQuotedFrom` as a GitHub line anchor (`…/README.md#L15`), so the identifier is the clickable evidence; the gate requires the fragment, resolves the file inside the tree and checks the quote is a non-empty verbatim substring of exactly those lines, plus the optional `efc:quoteSha256`; where the tree has no defining sentence the concept carries sources and a scopeNote saying so — the registry authors nothing (ADR-024). |
| C12 | Schema identity and JSON-LD form (`efc_identity.py`): every JSON Schema file — declared dialect, or properties+type/required, or `$defs`, or *named* `*schema*.json` with properties/required/definitions — carries the 2020-12 dialect and `$id` = `https://supertedai.github.io/EFC/<served path>` (docs/ is the Pages root, measured: `…/EFC/index.jsonld` 200, `…/EFC/docs/index.jsonld` 404 — the same form the vocabulary and the concept registry use; percent-encoded); every JSON-LD document without `@graph` has a top-level `@id` (DOI URL for papers with a DOI, else the served identifier; pre-existing foreign `@id`s kept; `@graph` documents exempt because a top-level `@id` would make a named graph); every `"$schema"` pointer in an instance (an editor convention, not a validator binding — C10 is) resolves to a *schema* in the tree; codemeta is 3.0. Reported, not enforced: CITATION.cff `type` vs codemeta `@type` — a human word. Declared on every check: identifiers outside `docs/` are identifiers, not URLs (count printed); `_archived/` is not maintained; the EFC-R-SPARC case-colliding pair is skipped (t_e505c64c); files named `schema.json` that carry no schema keys are listed. Robots write `@id`/`$id` themselves (`efc_auto_metadata`, `efc_gen_ai_friendly`, `efc_ai_brain`), and the per-package `schema.json` template describes the `index.json` the robots write (114 of 162 legacy pairs failed their own template, measured pre-C12 at `6a170fb5^`; hand-written schemas untouched). |
| C8 | Per-paper DOI consistency. Every source that declares a DOI inside a paper directory (`index.json`, `metadata.json`, `CITATION.cff`, `*.jsonld`) must declare the **same** canonical Figshare DOI. Hard error on conflict. |
| C14 | `docs/public/external_research_watch.json` carries no forbidden phrases in the **EFC-authored** free-text fields (`efc_relevance`, `ledger_action`). Sibling of C3 for the watchlist. Claim-like-but-arguable phrasing (`supports EFC`, …) warns rather than fails — see below. |

### C14: why the §4b carve-out does not transfer to JSON

C3's carve-out is **positional** — §4b is where third-party results are
quoted, so the forbidden phrases are tolerated inside that block and rejected
in §1–§4.

The watchlist has no sections, and every item in it is external by
construction, so a positional carve-out would exempt the whole file. C14's
equivalent split is **by field**, i.e. by who is speaking:

| Field | Voice | Scanned |
|---|---|---|
| `title`, `url`, `source_type` | the external work's own words | no |
| `efc_relevance`, `ledger_action` | EFC's editorial voice | **yes** |

No §4b-equivalent exemption exists *inside* the scanned fields, and none is
wanted: there is no legitimate reason for EFC's own annotation of an external
result to assert that the result confirms EFC.

`supports EFC` / `demonstrates EFC` / `verifies EFC` are listed separately in
`SOFT_CLAIM_PHRASES` and reported as **warnings only**. They breach the same
discipline, but the verbs have legitimate non-claim uses ("the DESI DR2
release supports EFC WP4's reanalysis" = supplies data for). Promoting them
to hard errors is a human judgement call about false positives.

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

## When the checks run (measured 2026-09-06, t_0d65ccdf)

`efc-verify.yml` (C1–C9, C11–C14) runs on `pull_request`, on `push` to
`main` (same path list — `tests/test_workflows_parse.py` keeps the two lists
identical), on a daily schedule, and on `workflow_dispatch`. Since
2026-04-28 it had run on `pull_request` only, to avoid racing the auto-sync:
four merges to `main` and four `efc-sync` commits on 2026-09-06 were never
verified after landing. The race is now expected and visible: a bare PDF
upload turns the push run red on "Fail on uncommitted changes" while the
sync repairs the tree, and the dispatched run on the sync commit goes green
— read the newest run on `main`. `efc-schema.yml` (C10) runs on both events
and on dispatch.

`efc-main-sync.yml` watches every path `efc-verify.yml` watches, minus the
paths that cannot leave a generated artifact stale (`tests/**` and the
verify workflow's own file); a test locks that. Until 2026-09-06 it watched
8 paths against verify's 12, and 167 of 485 JSON-LD documents lived outside
the 8: a new `efc:` term in `docs/papers/efc/` was declared and committed by
the robot, while the same term in `meta/` left CI red until someone ran
`--apply` by hand. It runs the same gate **after** its maintenance pass and
**before** its auto-commit: a red gate skips the commit and makes the run
red, with the drift visible in its log. Because a commit pushed with
`GITHUB_TOKEN` triggers no workflow, it dispatches `efc-verify.yml` and
`efc-schema.yml` itself, in the same step, right after the push.

GitHub Pages stays on the legacy builder (`main:/docs`). The "errored"
builds of 2026-09-06 and 2026-08-25 were measured to be supersessions —
each merge is followed within two minutes by the robot's own commit, whose
build cancels the one in progress — not failures; the site was never stale.
A real legacy failure (2026-08-24, a submodule path) does carry a log.

## The changelog projection (`efc-changelog-sync.yml`, `changelog_projeksjon.py`)

`docs/validation-ledger/data/changelog.json` is a projection of the git
history from `metadata.last_processed_sha` to `HEAD`: every non-merge commit
that touches more than the four changelog-infrastructure files becomes one
entry (`sha`, `summary` = the verbatim commit subject, file categories), and
`docs/public/EFC_Changelog.html` gets the matching `<li>`. The gate re-runs the
projection in CI and goes red if the committed files diverge, so the projection
is regenerated in the same PR as the change:

```
python3 scripts/maintenance/changelog_projeksjon.py   # regenerate
python3 scripts/maintenance/efc_navbar_sync.py        # navbar last, so the canonical block wins
```

**One writer per generated file.** Both files are owned by the projection and
by nothing else. `efc_auto_changelog.py` — step 8 of `efc_maintain.py` — used
to be a second writer, driven by the working tree instead of the history.
Measured 2026-09-18 (t_9cdf466e): it wrote the JSON with `json.dump`'s default
`ensure_ascii=True`, so one maintenance run turned every em dash into `\u2014`
and merged its own summary into the projection's newest entry; committing the
tree exactly as `efc_maintain.py` left it made the projection rewrite the
escapes back, and the gate was red on a tree that was in fixpoint — no commit
could turn it green. Both writers also prepended `<li>` rows to the same list,
so two such commits merged into a conflict that was committed unresolved
(`docs/public/EFC_Changelog.html`, introduced by 207274ad). Step 8 now detects
and reports only; it writes neither file. `_nav_helper.ensure_nav()` is a thin
call onto `efc_navbar_sync.render_nav()` — one canonical navbar form — and is
asked for the page it is writing, because without the page name it is a no-op.
`tests/test_maintenance_chain_fixpoint.py` locks all of it: it builds a
throwaway git repo carrying real copies of the two files, runs step 8 → the
projection → the navbar twice, and requires the second pass to leave the tree
unchanged.

**The start point must exist.** `last_processed_sha` is stamped from the commit
the projection ran on, and a squash-merge leaves that commit on no branch, so a
recorded start can be unreachable even though it was real when written.
Measured 2026-09-17: `72d91914…` was squashed to `1b51a04e` and *every* run —
on `main` and on every PR — died with `fatal: Invalid revision range`; no
change could turn the gate green. An unreachable start is now repaired
deterministically (`origin/main`, else `HEAD~1`), printed and persisted.
`tests/test_changelog_projeksjon.py` locks the repair and is run by the gate.

**Choosing the boundary is part of the change.** The boundary must be an
ancestor of the PR's merge ref and newer than everything already projected —
otherwise CI projects commits your branch does not carry (a `main` that moved
after you branched), rewrites `metadata.generated_at`, and goes red. Practical
rule: merge `main` into the branch, then let the last projection run record a
commit that contains it.

**Known conflict with the language rule.** Summaries are verbatim commit
subjects, and the language step of the same workflow rejects the first 30
entries that hit the Norwegian stopword list. A landed Norwegian commit
subject inside the projection window therefore makes the two steps mutually
unsatisfiable — measured 2026-09-17 on
`7c7e30b7 feat(atlas): sorte hull (fra Grid-Higgs) og periodesystemet …`
(`fra`, `og`). The repair is an English *source* for the summary (the
activity-log/`change_id` route in PR #430), never an edited or translated
entry: the changelog is a projection, not a second truth source.

## The repo-wide language gate (`efc_spraakvakt.py`, card t_537ab101)

The language rule (Morten 2026-09-17) had one enforcement point in CI until
this card: the newest 30 entries of
`docs/validation-ledger/data/changelog.json`, checked by an inline step inside
`efc-changelog-sync.yml`. Nothing read `docs/validation-ledger/**`,
`docs/public/**`, `public/**`, `scripts/**` or `tests/**`; a Norwegian commit
subject was caught only once it had been projected into the changelog, and only
while it sat inside that 30-entry window.

`efc_spraakvakt.py` adds the missing enforcement, in three modes:

| Mode | What it reads | Measured against | Window |
|------|---------------|------------------|--------|
| `--skann` (default) | file content in the guarded paths | the committed record | none |
| `--skann --referanse REV` | file content in the guarded paths | revision `REV` (the base of the change) | none |
| `--commits RANGE` | commit subjects in the range | nothing | the range |
| `--changelog` | changelog entries, newest first | nothing | declared, default 30 |

House interfaces: `--json`, a `make check` line, and the workflow
`.github/workflows/efc-spraak.yml`. Exit codes: 0 clean, 1 findings, 2 could
not measure (a measurement that could not be made is a finding, not an empty
answer).

**Who runs the default mode.** `make check` runs the scan against the committed
record — the ratchet. CI cannot: it is change-relative by design (`--referanse`),
so nothing in CI ever compares the tree to the record. Measured 2026-09-19
(card t_aad5f41e): the record was written once, no line ran it, and the tree
grew 1 212 hits past it while every PR stayed green. A ratchet with no runner
is a number nobody reads, which is why the line was added and the residual
written in per file (measured, not regenerated blindly): see `spraak-baseline.json`.

The vocabulary is `scripts/maintenance/spraak-ord.json` — the same alternation
the changelog step inlines. `tests/test_spraakvakt.py` fails when the two drift
apart, so the two rules cannot disagree about what is Norwegian.

**The failure rule belongs to the change, not to the branch it sits on.**
In CI the scan runs with `--referanse origin/<base>` (a push: the previous tip),
so it answers «did THIS change add Norwegian» and never «is the base branch
clean». Measured on the gate's own first CI run (PR #530, 2026-09-18): without a
reference it went red for two files the PR had never touched, because `main` had
grown under it — the same wedged-gate condition this card was written about for
the changelog. Debt that already sits on the base branch is *reported* on every
run (`undeclared_growth`), never failed, and never silenced. A reference that
cannot be read is exit 2 (could not measure) — never a fallback that blames the
change for its base branch.

**The residual is recorded, never silenced.** `spraak-baseline.json` holds the
measured count per file (110 files, 5033 hits, measured on `74565031`; the first
record was written 2026-09-18 with 131 files and 6254 hits, and no number rose
when it was written in per file after the translations landed). The gate fails
when a file exceeds its recorded count, and reports slack when a file drops
below it, so the translation work has a finish line instead of a number nobody
checks. Regenerate after a translation lands:

```
python3 scripts/maintenance/efc_spraakvakt.py --oppdater-baseline
```

Growth is never a baseline update: a new Norwegian string fails the PR that
adds it, which is the point of the ratchet. A recorded entry may carry `owner`
(who owns the residual) and `reason` (why it is left standing) — the generator
preserves both, so a declared residual does not become an anonymous number
again. One file is recorded that way today: `tests/test_atlas_dekning_aerlighet.py`,
whose pattern pins `schema/atlas_dekning.json`, outside the guard (U2).
`--grenser` prints the declared limits with the measured count of what sits
outside the guard.

**Declared limits.** R1 reads a hyphen-adjacent match as an identifier, so a
hyphen-joined compound is invisible — that is the rule that removes the
measured `badge-med` false positive. R2 treats the declared uppercase labels
MED/MEDIUM as English severity labels. The vocabulary is narrow on purpose:
function words that collide with English are absent, and prose built only from
them is invisible. Only the guarded paths are scanned. A file that does not
decode as UTF-8 is skipped and counted, and fails only when its extension is a
text format. The commit mode sees only the range it is handed.

**Relationship to the changelog step.** The window in the changelog step is
unchanged, and so is the collision recorded in card t_f610686f: a landed
Norwegian subject inside the projection window makes that step unsatisfiable,
because an entry is a verbatim projection and rewriting it would make the
changelog a second source of truth. The repair stays an English source. The
commit mode is what catches the violation before it reaches the window.

**Not wired into `vedlikeholdsrunde.py`.** A violation always has a PR owner —
CI goes red on the PR that adds it — so there is nothing for the weekly round
to schedule; the round exists for drift nobody owns. Recorded here so the
absence is a decision rather than an oversight.

## Proposing a concept (`efc_candidates.py`)

Not a gate. `python3 scripts/maintenance/efc_candidates.py [TERM …]` reads the
tree for a term and reports what can be measured: whether it is already a
vocabulary term (C9) or a registered concept (C11), which spellings were
searched and which matched, the DOIs of papers whose own files NAME it, and
candidate definition sentences with GitHub line anchors, ranked by whether the
sentence defines rather than merely uses. It then stops. The four judgements —
which sentence is the definition or whether that is a gap, what kind of thing
it is, candidate or canonical, and where it sits — are printed as open
decisions. What C11 does and does not refuse is stated below; do not read
the top of the ranking as an answer.

Two measured reasons for its shape: a null on one spelling is a search and not
an absence, so a NOT-IN-TREE result carries the forms tried; and proximity is
not a source, so a paper counts only when one of its own files carries the
term, which is the mistake two drafts of `efc:HME` made. A file is attributed
to the longest matching paper directory, so a container is not credited with
its child's term.

The forms tried are four layers, each declared: literal case and punctuation,
morphology (plural, acronym), Unicode (Greek letter ↔ Latin name, subscript
digit ↔ plain digit, so `Λ` and `σ₈` are searched as `Lambda` and `sigma8`
too), and a curated English/alias table (Norwegian ↔ English, notation
aliases). Measured 2026-09-06: `oscillering` alone reads NOT IN TREE while
`oscillat*` is in 60 tracked files; the English table closes that gap, so
`oscillering` now resolves to `oscillation`/`oscillating`/`oscillatory`. The
table is curated and finite, not a general dictionary — a term absent from it
is searched without translation, and the NOT-IN-TREE result says so.

Two limits remain. The ranking is a heuristic and prints its score. And the
gate does not stop a `candidate` entry whose definition came from the top of
this list: choosing which sentence defines a term is judgement, and only a
reader stands between the ranking and the registry.
