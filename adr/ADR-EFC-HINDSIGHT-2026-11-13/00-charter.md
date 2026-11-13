# ADR-EFC-HINDSIGHT-2026-11-13 — Charter

**Status:** Proposed, pre-implementation. **Owner:** faber. **Task:** `t_c9dbf0a2`.

## Request
Close the remaining findings from the review of EFC Hindsight PR #653: support current and renamed SDK page methods; accept successful REST PATCH statuses only with GET/readback; preserve bank missions while adding the missing retain/reflect requirements; examine new label semantics; measure historical whole-claim entities and identify a safe correction route.

## Scope
Repository changes in `integrations/hindsight/` on an isolated branch/PR, plus read-only investigation of the live EFC Hindsight bank. No changes to other banks, model-timer state, unrelated repos/worktrees, or production historical memories. Any live bank write is gated on merged Git source, backup, independent review, and owner approval.

## Exit criteria
Tests demonstrate both SDK naming families, 2xx+readback acceptance, non-2xx refusal, and fail-closed ordering. Documentation matches measured client/server versions and current Pages API. Existing mission text and label definitions remain preserved. Bank write, if later approved, is backed up and read back exactly. Historic entity migration remains explicitly unresolved unless a reversible, measured, tested approach is proven.
