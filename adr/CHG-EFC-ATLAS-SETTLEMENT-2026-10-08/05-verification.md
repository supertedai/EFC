# Verification contract and measured results

## RED before implementation

- Baseline atlas module: `/opt/venvs/t_123ed6d9/bin/python -m pytest tests/test_atlas_oppslag.py -q` → **41 passed**.
- The pending-status regression failed on the old lookup at `assert growth["oppgjoer_status"] == "pending"` with `KeyError: 'oppgjoer_status'` (pytest output retained in the session record).
- A focused incomplete-result probe also exited 1 before the evidence gate; the old helper promoted any non-empty `settlement_result.outcome`. The exact pytest detail from that invocation was not retained.
- During the classifier refinement, tests captured three additional failures: a result with the wrong node was classified `settled` rather than `record_only`; a mismatched result could override an explicit pending contract; and an incomplete result could hide that pending contract as `record_only`.
- After the independent review, five static non-terminal outcome cases and the real `kosmos.asteroider` correlation mismatch returned `settled`; the producer integration probe also measured `har_oppgjoer=True` for a result-only node where the legacy field should remain false. All were red before the final refinement.
- A further precedence probe found that a matching `settlement_result` explicitly waiting for its arbiter could be masked by a completed-looking static record; the regression failed as `settled != pending` before reordering the wait check.

## Green after implementation

- Test-fixture correction: the first non-finite-gap fixture retained a pending contract while expecting `record_only`; the classifier correctly returned `pending`. Removed that contract from the isolated malformed-result case; the focused and full runs below then passed.
- Focused lookup suite: `/opt/venvs/t_123ed6d9/bin/python -m pytest tests/test_atlas_oppslag.py -q` → **56 passed**.
- Full EFC suite with no exclusions: `/opt/venvs/t_123ed6d9/bin/python -m pytest tests/ -q` → **1293 passed**, 1 `SyntaxWarning` in unchanged `tests/test_maintenance_chain_fixpoint.py` (`invalid escape sequence '\\d'`). The growth-friction module is included in the full run; it also passed separately (**3 passed**).
- Schema gate: `/opt/venvs/t_123ed6d9/bin/python scripts/maintenance/efc_schema_check.py` → **OK**, 4 schema/instance pairs valid and closed, 2 instanceless schemas valid, 4 schema-only valid and closed.
- Repository verification: `/opt/venvs/t_123ed6d9/bin/python scripts/maintenance/efc_verify.py` → **171 paper dirs, 0 errors, 0 warnings**.
- Reference-relative language gate: `/opt/venvs/t_123ed6d9/bin/python scripts/maintenance/efc_spraakvakt.py --referanse origin/main` → **0 new findings**.
- `git diff --check` → clean.

## Exact lookup readback

On baseline `HEAD @ 52ba3222`, `efc.growth_engine` printed `has prediction · is settled`. On the task branch the readbacks now show:

- `efc.growth_engine`: `has settlement contract · settlement pending`.
- `verden.vaer`: `has settlement contract · settled outcome` (matching prediction/settlement correlation).
- `kosmos.asteroider`: `has settlement contract · settlement record (completion unverified)` because its correlation differs from the prediction.
- `efc.mu_kz_engine`: `no settlement contract`.

The corresponding `--emne ... --alle --ref HEAD` commands exited 0. A result-only block emitted by `scripts/atlas_oppgjoer.py` is exercised with the no-write `--kandidat` path; it is classified as a settled result while `har_oppgjoer` remains false, preserving the legacy contract-presence meaning.

```text
/opt/venvs/t_123ed6d9/bin/python scripts/atlas_lesing.py . --emne efc.growth_engine --alle --ref HEAD
/opt/venvs/t_123ed6d9/bin/python scripts/atlas_lesing.py . --emne verden.vaer --alle --ref HEAD
/opt/venvs/t_123ed6d9/bin/python scripts/atlas_lesing.py . --emne kosmos.asteroider --alle --ref HEAD
/opt/venvs/t_123ed6d9/bin/python scripts/atlas_lesing.py . --emne efc.mu_kz_engine --alle --ref HEAD
```

The latest broker prediction record read is sequence 31058, timestamp 2026-09-07T15:00:05Z; it names DESI DR2 full-shape as the awaited arbiter. The exact EFC-fσ8 settlement-subject query returned no message. This is a dated bus snapshot, not a claim about whether DESI DR2 data exist elsewhere. This change does not write to or alter the bus.

## Remote readback

PR [#634](https://github.com/supertedai/EFC/pull/634) is **OPEN**, base `main`, head `85ec85aaa1c8cf5051708d82573d92dc9df9eecc`; `git ls-remote` matched that exact branch head. GitHub reported `mergeStateStatus=CLEAN`; required check runs `schema`, `verify`, and `spraakvakt` all concluded `SUCCESS` on that head. Independent PR review and the owner’s landing decision remain pending; nothing was merged.