# 08 — Closeout

**Observed outcome, 2026-11-10.** Everything below is measured; nothing is a forecast.

## State reached

| State | Reached | Evidence |
|---|---|---|
| `proposed` | yes | this ADR package (`00`–`07`) |
| `implemented` | yes | commits `b67759b5`, `d7b9ec51`, `cf758572` on `wt/t_1610348d` |
| `reviewed` | yes, with a standing disagreement | `06-review.md` — round 1 PASS 0.93; round 2 BLOCK on a ground measurably absent from the artifact |
| `published` (branch + PR) | yes | PR **#641**, base `main`, head `wt/t_1610348d`, `MERGEABLE`, state `OPEN` |
| `verified` (readback) | yes | head read back `cf758572d76f2c60b808da675e7f811a969072e6` = local `HEAD`; 7/7 CI checks `SUCCESS` |
| `merged` | **no — and must not be claimed** | landing is Morten's word |

This file is itself a docs-only commit on the same branch, so it re-runs CI and moves the PR
head. The readback above was taken at `cf758572` (7/7 `SUCCESS`); the same seven checks passed
again at `784e2935`, the commit that first carried this closeout. The **definitive** final
head and check readback live on kanban card `t_1610348d`, which is the durable handoff — not
here, where the figure would be one commit stale by construction.

## What changed

| Path | Commit | Change |
|---|---|---|
| `schema/regime_nodes.jsonld` | `b67759b5` | `efc.lag_c0`: +2 DOI entries in `ontology.proveniens.kilder`; +1 `revisjon` entry (2026-11-10). Diff: 13 lines, 12 insertions, 1 deletion (the trailing-comma line) |
| `tests/test_atlas_bro_status.py` | `b67759b5` | new, 7 tests |
| `docs/validation-ledger/data/doi_coverage_{matrix,pending,open_findings}.json` | `b67759b5` | regenerated: `atlas_union_literal_urls` 20→24; four rows `in_atlas_literal_url` false→true with `class`/`disposition` unchanged; backlog `count` still 60 |
| `docs/ontology.jsonld`, `docs/ontology.html` | `b67759b5` | regenerated: `usedAsProperty` for `hentet`/`ref` 193→195, `type` 201→203 |
| `docs/validation-ledger/data/changelog.json`, `docs/public/EFC_Changelog.html` | `d7b9ec51` | projection: one row for `b67759b5`, `categories: {ledger_data: 3}` |
| `docs/adr/2026-11-10-cosmos-cognition-bridge-status/**` | `b67759b5`, `cf758572` | this package |

Not changed: node count (126), relation count (86), every `epistemikk` field, the schema,
`docs/public/EFC_Atlas.html`, `docs/efc-atlas/atlas/data.mjs` (measured: no diff).

## Deviations from `03-decision.md`

1. **`docs/ontology.jsonld` / `.html` had to be regenerated.** Not anticipated: the ontology
   records *usage counts* per term (`usedAsProperty`), and two new provenance entries change
   them. Not a schema change — a generated artifact, same identity rule as `data.mjs`.
2. **Two clauses and one word were changed after review** (findings 3, 6, 7): "at least two";
   the bridge "does not close the cosmology-RLHF loop directly"; "EFC-C had not yet been
   fitted to a neural dataset". Each is now pinned by the test.
3. **The first commit was rewritten before push.** It carried a malformed DOI
   (`10.32091700`) in its message. Rewriting required re-deriving the changelog projection;
   the projection start point was verified to remain an ancestor (`merge-base
   --is-ancestor`) so the window was not silently skipped.
4. **Two tests fail on a dirty worktree by design.** `test_atlas_buss.py::…never_writes_it`
   and `test_atlas_feltvekt.py::…leaves_the_bank_alone` assert that the bank is clean in
   `git status`; they report `M schema/regime_nodes.jsonld` while the change is uncommitted
   and pass after the commit (measured: 3 passed). Recorded as a known property of the
   gates, not as a pass-by-luck.

## Gate results (final)

```
pytest tests/ -q --ignore=tests/test_growth_friction.py  → 1317 passed, 0 failed (109.66s)
efc_bro_synk.py --sjekk        → ingen avvik
efc_schema_check.py            → OK
efc_ontology.py                → OK (355 terms / 511 documents)
validate_repo.py               → 0 errors
validate_ownership.py          → 0 files without an owner
efc_page_consistency.py        → all invariants hold
efc_narrative_consistency.py   → OK, 0 warnings
efc_navbar_sync.py --check     → 13/13 canonical
efc_spraakvakt.py              → no new Norwegian
statement_graph_check.py       → no hard errors
changelog_projeksjon.py        → idempotent; start point verified an ancestor
CI on PR #641                  → 7/7 SUCCESS (changelog-sync, forside, spraakvakt,
                                 page-consistency, verify, review-gate, schema)
```

## Residual unknowns — carried forward, not resolved here

1. **`32091700`'s version label.** DataCite: "EFC-C v2.0". This repo's `index.json` and
   `doi-map.json`: v2.1. Recorded as a discrepancy in the bank. Resolving it needs the
   Figshare record itself, which this card does not touch.
2. **The two proposals sit in the atlas as `changelog`-class DOIs.** The coverage register's
   `class` is derived from the evidence register's `is_empirical`; re-classing them
   `atlas_scope` is a separate classification decision with its own evidence burden.
3. **`31289806` remains `atlas_candidate`**, deliberately: its DOI is not in the bank, so the
   human semantic-mapping decision is still open and still visible in the backlog (60).
4. **`efc.lag_c0`'s engine link** (`efc.klima_engine`, flagged `UNCERTAIN` in
   `efc_bro_konvensjon.MOTOR_DELT`) is untouched and still unverified.
5. **The bridge itself is still not empirically or causally validated.** This change records
   that fact; it does not advance it.

## Rollback

`gh pr close 641 --repo supertedai/EFC`, or revert `cf758572`, `d7b9ec51`, `b67759b5` on the
branch. `origin/main` was never modified. Full procedure: `07-rollback.md`.

## Lessons (candidates, with their conditions)

- **A gate that measures `git status` fails on every legitimate uncommitted change.** Two
  tests here do exactly that. When a suite goes red right after an edit, read *what* the test
  measures before calling it a regression — a cleanliness guard is not a content check. Does
  not apply to tests that read file content.
- **An amended or rewritten commit can strand the changelog projection's start point.** After
  any rewrite, `merge-base --is-ancestor <last_processed_sha> HEAD` is the check that catches
  it; without it the window is skipped in silence.
- **A review's BLOCK is not automatically a defect in the artifact.** When the reviewer's
  ground is something the dossier failed to include, the honest record says so and settles it
  by a rerunnable measurement — it does not re-ask until the verdict turns green, and it does
  not silently drop the BLOCK either.
- **A generated register can turn a text mention into a coverage claim.** `in_atlas_literal_url`
  is a substring match, so citing a queued DOI anywhere in the bank clears it from the
  backlog. Keep queued DOIs out of the bank until the mapping is actually decided.
