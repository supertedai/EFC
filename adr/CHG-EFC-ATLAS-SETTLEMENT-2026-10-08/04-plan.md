# Implementation plan

1. **Done:** The pending-status regression failed on the baseline because `oppgjoer_status` was absent; completed and pending cases are covered.
2. **Done:** The first classifier distinguished pending/settled/record-only; independent review then exposed untested static non-terminal and correlation paths, which are covered by new red-before-fix tests.
3. **Done:** The classifier now requires node/correlation identity and producer-shaped evidence for result blocks, preserves the legacy `har_oppgjoer` meaning, and fails closed on non-terminal or mis-correlated static records.
4. **Done:** The review-refined tree passes 56 focused atlas tests and all 1293 EFC tests; schema, repository-verification, reference-relative language, and exact CLI readbacks are recorded in `05-verification.md`.
5. **Done:** The `atlas_oppgjoer.py` no-write CLI output is exercised as a producer fixture; pending, correlated-complete, mis-correlated, and no-contract CLI cases are asserted.
6. **In progress:** PR #634 is open and its current exact head/checks are read back in `05-verification.md`; after this ADR readback update is pushed, verify the new head/checks and request independent PR review. Do not merge or land.