# Operating Model — supertedai/EFC

**This repository follows the Symbiose Operating Model (SOM).**

> ANY work in this repo — by Claude, by Morten, by any other agent —
> follows the model defined in `som/governance/SOM.md` (canonical in
> `supertedai/AGI`). Use the SOM as the working template for every task.
> Same logic everywhere.

The SOM is **not** specific to backend daemon structure. It is the
universal operating grammar for the whole Symbiose ecosystem (AGI + EFC
+ medicine + economy + biology + earth).

---

## Canonical SOM home

**All shared schemas, governance docs, registries, templates, RFCs live in `supertedai/AGI` at `som/`.** This repo only carries its own `layer.yaml` and `som/capabilities/` (the 5 master EFC orchestrator manifests).

Read these in `supertedai/AGI` before starting non-trivial work here:

1. **[`som/governance/SOM.md`](https://github.com/supertedai/AGI/blob/main/som/governance/SOM.md)** — the doctrine
2. **[`som/governance/RCE-CONTRACT.md`](https://github.com/supertedai/AGI/blob/main/som/governance/RCE-CONTRACT.md)** — cornerstone 5-component contract
3. **[`som/governance/loops.md`](https://github.com/supertedai/AGI/blob/main/som/governance/loops.md)** — develop / maintain / update
4. **[`som/governance/quality-gates.md`](https://github.com/supertedai/AGI/blob/main/som/governance/quality-gates.md)** — CI gates
5. **[`som/registry/domains.yaml`](https://github.com/supertedai/AGI/blob/main/som/registry/domains.yaml)** — 7 first-class domains

## EFC-specific entrypoints (this repo)

- **[`layer.yaml`](./layer.yaml)** — EFC's declaration in Symbiose topology
- **[`som/INVENTORY-EFC.md`](./som/INVENTORY-EFC.md)** — EFC-side inventory at 2026-05-19
- **[`som/capabilities/`](./som/capabilities/)** — 5 capability manifests for master EFC orchestrators (efc.maintain, efc.full-sync, efc.qdrant-ingest, efc.system-health, efc.mcp)

## EFC-specific non-negotiables (in addition to global SOM)

From `AGENTS.md` v3.6 (locked maintenance discipline):

- **Three evidence layers strictly separated**: EFC own DOI / arXiv §4b / EFC working notes. CI rejects mixing.
- **Language discipline**: never "confirms EFC". Use "consistent with", "overlaps with", "within prediction band".
- **Pre-registration**: predictions cite prior EFC DOI in same sentence. No post-diction.
- **Sealed predictions**: `.seal-manifest.json` SHA-256 hashes never mutated without explicit re-seal.
- **Council audit**: GPT-5 weekly audit must pass before public-page changes land on main (`efc-ai-audit.yml`).
- **SessionStart hook**: every Claude session in this repo runs `scripts/maintenance/efc_maintain.py` + `efc_drift_detector.py` before any other work.

## Decision tree (EFC-flavored)

```
I need to ...
├─ add a new EFC paper
│   → SessionStart hook runs maintenance + drift
│     classify against Ledger tier rules (T1/T2/T3)
│     update 13 public pages per AGENTS.md §Step 4
│     scripts/maintenance/efc_process_paper.py per-paper flow
│
├─ modify a sealed prediction
│   → RFC FIRST (would invalidate .seal-manifest.json)
│     efc-sealed-prediction-guard.yml blocks the PR otherwise
│
├─ add new pipeline
│   → use som/templates/capability/pipeline/ from AGI
│     declare under som/capabilities/ in this repo
│     update layer.yaml provides:
│
├─ fix drift detected by SessionStart hook
│   → AGENTS.md §Step 1 — fix every reported item before other work
│
└─ anything that mutates Symbiose Qdrant/Neo4j directly from here
    → NO. EFC pushes via SYMBIOSE_WEBHOOK_URL only.  _(retired 2026-08-23: the Symbiose webhook was removed from efc-sync.yml and efc-main-sync.yml (Hetzner ADR-024 §8.3 pt. 4))_
      Mutation happens in supertedai/AGI's shared.ingestion.repo-sync daemon.
```

## For AI agents

Before starting work in this repo:

1. **Run SessionStart maintenance** (`efc_maintain.py` + `efc_drift_detector.py`) — fix what it reports before anything else.
2. **Confirm three evidence layers separated** — never blend own DOI / arXiv 4b / working notes.
3. **No "confirms EFC"** — language discipline is hard rule.
4. **Cite prior DOI for any new prediction** — in the same sentence as the prediction.
5. **Sealed predictions are immutable** — re-seal only via RFC.
6. **External arbitration is council audit** — GPT-5 audit must agree before public pages change.

## What this is NOT

- Not a duplicate of AGI's SOM. Schemas/governance/templates live ONCE, in AGI.
- Not an exemption from EFC's existing maintenance discipline (AGENTS.md v3.6 still applies).
- Not a backend-only model. Same template applies to papers, ledger entries, pipelines, atlas.

---

**Locked**: 2026-05-19, RFC-0001 (in supertedai/AGI).
**Branch**: `claude/backend-daemon-structure-ilT2W`.
**Canonical companion**: [`OPERATING_MODEL.md` in supertedai/AGI](https://github.com/supertedai/AGI/blob/main/OPERATING_MODEL.md).
