# t_0d7802b1 — a corrupt `settlement_result` gets its own marker

## The finding (confirmed as BLOCK by the panel 2026-11-18)

`scripts/atlas_lesing.py::_oppgjoer_status` failed closed to `None` for a
**present-but-invalid** `settlement_result` (explicit null, non-dict, missing or
mismatched `node` / `correlation` / `outcome`). `None` is the same token the
reader returns for "this node carries no settlement information at all", so
corruption collapsed into absence: a broken verdict reported as silence.

## The change

- `_oppgjoer_status` returns `"invalid"` for every present-but-invalid verdict.
  `"invalid"` is an **integrity marker**, deliberately kept out of the
  settlement vocabulary proper (`none/pending/settled/record_only`, PR #634):
  a caller that counts settled claims must not have to guess whether a token is
  a signed verdict.
- Unchanged: absent `settlement_result` -> `None`; the writer's unfilled
  container `{}` still falls through to the static contract; `pending` /
  `settled` semantics are untouched.
- An invalid verdict suppresses the static contract: corruption must not be
  downgraded to "still awaiting" one step later.
- `_har_oppgjoer` counts a *written* `settlement_result` slot as presence for
  every value except `{}`, so an explicit null reads as presence + `invalid`
  instead of "no settlement info".
- The CLI prints `SETTLEMENT RESULT INVALID (integrity anomaly — not a verdict)`.
- `schema/regime_node.schema.json`: the `settlement_result` description now
  names the marker (description only; no structural change).

## Measurements (all on this worktree unless stated)

| Measurement | Result |
|---|---|
| `pytest tests/test_atlas_oppslag.py -q` | 81 passed, 1 skipped |
| focused (`-k "settlement or oppgjoer or Ugyldig or invalid"`) | 39 passed |
| full suite, branch | **47 failed, 1457 passed, 1 skipped** |
| full suite, clean base `origin/main` bbe78fc0 (`/tmp/base_0d78`) | **47 failed, 1437 passed, 1 skipped** |
| failure-set diff (`comm -13` / `comm -23`) | **empty both ways** — 0 regressions, 0 fixed |
| `make full-check PYTHON=/opt/venvs/t_123ed6d9/bin/python` | exit 0 (repo-contract 0 errors, links 0 hard) |
| `efc_schema_check.py` | OK — 4 pairs valid and closed |
| `efc_identity.py` | OK |

The 47 pre-existing full-suite failures are identical before and after; the
identifiers are in `full-suite-47-ids.txt`. Interpreted as pre-existing, by
comparison — not by assertion.

## Mutation proof (the pin bites)

Reverting only the new marker (`return "invalid"` -> `return None`, six sites)
makes the suite fail:

    28 failed, 9 passed, 45 deselected        (log: mutasjon-reversert-markor.txt)

Restored byte-identical: `sha256sum -c atlas_lesing.sha256` -> OK.

## CI scope, read not assumed

`.github/workflows/efc-schema.yml` lists `scripts/atlas_lesing.py`,
`tests/test_atlas_oppslag.py` and `schema/regime_node.schema.json` in its
`paths:` filter **and** runs `pytest tests/test_atlas_oppslag.py` in its test
step. Green CI on this PR is therefore a real signal for the changed file —
unlike `efc-verify.yml`, which triggers on `tests/**` but runs no pytest step.

Hosted read-back (PR #697, run 45517307433, job 138879953518) — the job log,
not the badge: the pytest step names `tests/test_atlas_oppslag.py` and reports
`306 passed, 2 skipped in 13.72s`. `spraakvakt` and `verify` also green.
