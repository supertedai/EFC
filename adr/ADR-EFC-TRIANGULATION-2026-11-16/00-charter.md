# ADR-EFC-TRIANGULATION-2026-11-16 — Charter

**Status:** Proposed, pre-implementation. **Owner:** researcher. **Task:** `t_a7ad092c` (component 2 scope extension).

## Request
Remove the owner from the approval loop for routine claims by building a triangulation / cross-check layer. Accept only what is *externally and independently* confirmed; never what is merely internally self-agreeing. The owner should review only genuine exceptions (low confidence, conflict, or high-stakes), not every step.

## Scope
A new verification layer under `scripts/maintenance/` that (1) retrieves independent external sources for a claim, (2) compares them deterministically (field vs field, number vs number), and (3) assigns a confidence level from the count of *independent* agreeing sources. Plus the escalation rules that decide auto-accept vs human review. No changes to publish/mint/merge gates. Read-only with respect to existing claims until a claim reaches its confidence threshold.

## Exit criteria
- Confidence model and independence definition written and reviewed.
- The layer classifies claims into the levels below with measured, reproducible behavior.
- A claim is auto-accepted only when its evidence is external and independent; internal self-agreement never raises confidence.
- Escalation fires on low-confidence / conflicting / high-stakes claims, demonstrably (tests).
- Second opinion (independent panel) recorded with disposition.
