# Verification plan

## Unit tests (no live bank/API)
- New-only client selects Pages methods and returns results.
- Legacy-only client selects Knowledge Pages methods and returns results.
- Neither family present raises before any write.
- HTTP 200 and 204 count as transport success; caller GETs and confirms exact config fields.
- HTTP 4xx/5xx stops before directives/pages.
- Successful PATCH with mismatched GET stops before directives/pages.
- Mission additions preserve all original text and produce no further change on a second run.

## Repository gates
- Focused tests RED before implementation, GREEN afterward.
- Check canonical EFC pytest environment; full relevant `tests/` suite if available.
- `python -m py_compile integrations/hindsight/apply_efc_bank.py`.
- `python -m json.tool integrations/hindsight/efc_bank.config.json`.
- Run `scripts/maintenance/efc_schema_check.py`, `scripts/maintenance/efc_verify.py`, `scripts/maintenance/efc_spraakvakt.py --referanse origin/main`, `git diff --check`.
- Independent review records findings/disposition; remote readback confirms branch, PR, exact head, checks, review/merge state.

## Bank write acceptance (gated, not yet run)
- Full config backup path/hash recorded before mutation.
- GET readback equals original mission plus exact extension; all original content remains.
- Second dry-run reports zero config changes.
- No directive/page/history changes.
