# Verification plan

## Unit tests (hermetic, no network)
- `independence()`: same-model second reading → not independent; different external paper → independent; sealed-before-test → independent; same-source re-read → not independent.
- `confidence()`: 0 independent sources → L1 (single, if any) or L0 (mechanical); 1 → L1; 2 → L2; 3+ → L3; conflicting → L4; falsify/canonize/publish kind → L5.
- `escalate()`: L0/L2/L3 → no escalation; L1 → no escalation unless it contradicts an existing L2/L3; L4 → escalate; L5 → escalate.
- A confidence record without a source list is rejected.
- Pilot: P2 fσ8 = 0.430, three independent survey sources → L3; one source → L1; conflicting → L4.

## Repository gates
- `python3 scripts/maintenance/efc_spraakvakt.py` (0 new findings — all prose English).
- `python3 scripts/maintenance/efc_verify.py` (0 errors).
- `git diff --check`.
- CI green on the branch.

## Second opinion
Independent panel (gpt-5.6-luna standard, claude-opus-5 escalation) reviews the confidence model and independence definition, specifically probing for a circularity hole. Disposition recorded in `06-review.md` and on the PR.
