# Change charter — EFC atlas settlement status

- **Change ID:** `CHG-EFC-ATLAS-SETTLEMENT-2026-10-08`
- **Kanban:** `t_d7c63861` on `energy-flow-cosmology`
- **Owner:** Morten (requested correction)
- **Implementer:** `default`
- **Status:** Review-driven changes and final local gates pass in fresh Kanban run 799; commit, PR readback, and independent PR review remain pending.

## Request
Correct the EFC atlas lookup so a node with a pending settlement contract is not presented as if an outcome has already been settled.

## Scope
Change the `--emne` lookup result/rendering and add regression coverage. Preserve the existing distinction between a settlement contract, a pending arbiter, and a completed outcome. Do not change EFC predictions, physics, evidentiary status, schemas, generated public pages, or the live event bus. Do not add a top-level EFC regime node: the concept-only namespace entry is intentional.

## Exit criterion
A test fails on the measured baseline and passes after the minimal fix; pending and completed cases render distinctly; relevant repository gates pass; an independent review has a recorded disposition; exact branch/PR state is read back. Merge/landing remains the owner's decision.