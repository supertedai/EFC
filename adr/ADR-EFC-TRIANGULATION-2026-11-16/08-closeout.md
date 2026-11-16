# Closeout

## Measured outcome (build complete, wiring pending)

1. **Layer built + unit-tested** — ✅ `efc_triangulate.py` + `tests/test_efc_triangulate.py`, 8/8 hermetic tests green (canonical venv, `env -u PYTHONPATH`).
2. **Pilot claim classified** — ✅ P2 fσ8(z=0.7)=0.430 run through the layer with four measured cases:
   - 3 disjoint surveys (BOSS/VIPERS/6dFGS) → `independent` + `replicated` → **auto-accept**.
   - BOSS + eBOSS (both SDSS, shared lineage) → `correlated` → **escalate**.
   - 2 surveys + one self-generated source (own DOI) laundered in → `unknown` → **escalate**.
   - 2 agree + DESI contradicts → `contradicted` → **escalate**.
3. **Second opinion recorded** — ✅ both panels BLOCK (gpt-5.6-luna 0.96, deepseek-v4-pro 0.84); the circularity hole is closed in the revised decision.
4. **Owner confirmed the escalation boundary** — ✅ 2026-11-16: falsify / canonize / publish remain always human-gated.

## Pilot learning
The layer is only as correct as its source metadata: with inconsistent `organization` fields ("BOSS" vs "SDSS"), the correlated-source case slipped through as `independent`; fixing the metadata caught it. This confirms the panel's point — independence must be a machine-checkable provenance property fed by the ledger's actual lineage, not ad-hoc labels.

## Residual gaps (next build)
- Automatic multi-source retrieval of external survey data (the pilot used sources already in the ledger).
- Wire the layer into figshare-presence Pass 3 (auto-land L2/L3, flag L1/L4 in the draft PR body).
- PR #664 merge (owner word).

## Deviation
No RED-before-GREEN was done for this ADR (classifier and tests written together, green at first run). The unit tests cover each panel hole, but the strict TDD order was not followed.
