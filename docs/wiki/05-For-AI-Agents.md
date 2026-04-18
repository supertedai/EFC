# 05 · For AI agents

> Machine-readable entry points and the protocol every AI agent must follow when working in this repository.

[🏠 Home](./Home.md) · [← Reproduce](./04-Reproduce.md) · [→ Glossary](./06-Glossary.md)

---

## Start here (in this order)

1. [`llms.txt`](../../llms.txt) — machine-readable index (identity, axiom, key equations, empirical constraints, three-track programme).
2. [`AGENTS.md`](../../AGENTS.md) — full operating protocol for AI agents. **Not optional.**
3. [`/schema/global_schema.json`](../../schema/global_schema.json) — canonical schema for all JSON objects in the repo.
4. [`/figshare/doi-map.json`](../../figshare/doi-map.json) — DOI registry.

---

## AI-friendly paper packages

Every paper ships with a structured package under [`/docs/papers/efc/<slug>/`](../papers/efc/):

| File | Purpose |
|---|---|
| `index.json` | Structured metadata (title, DOI, keywords, core_equations, kill_criteria, sealed_predictions, tier, paper_type) |
| `README.md` | Human + agent-readable summary |
| `*.pdf` | The paper itself |
| `ai_friendly.py` (when applicable) | Executable Python for the paper's results |
| `code/`, `data/` | Reproducible artefacts |

Catalogue: [`docs/papers/efc/ai_friendly_index.json`](../papers/efc/ai_friendly_index.json) — 150 packages, 138 with executable Python (100% metadata coverage).

---

## Session maintenance protocol (MUST)

On every session start, the `SessionStart` hook runs [`scripts/maintenance/efc_maintain.py`](../../scripts/maintenance/efc_maintain.py). Claude Code (and any conforming agent) **must act on its output before anything else**:

### Step 1 — Fix drift

If `efc_drift_detector.py` reports stale counts/versions/missing DOIs, fix every item before proceeding.

### Step 2 — Scan for unprocessed papers

For each `docs/papers/efc/<slug>/index.json`:

1. Does it have a `doi` field?
2. If yes, is that DOI present in `EFC_Validation_Ledger.html`?
3. If no → the paper needs processing.

### Step 3 — Process each unregistered paper

Run [`scripts/maintenance/efc_process_paper.py`](../../scripts/maintenance/efc_process_paper.py) or, if manual: read the PDF, extract title / key results / kill-criteria links / sealed predictions, then add to the Ledger under the correct section with the correct evidence layer.

Full step-by-step protocol: [`AGENTS.md`](../../AGENTS.md).

---

## Evidence-layer discipline (non-negotiable)

Three evidence layers are kept **strictly separate** — violations are rejected by CI via `efc_verify.py`:

| Layer | What | Where |
|---|---|---|
| 1 | EFC publications (own 8-digit Figshare DOI) | `evidence-register.json` + `ledger.json` empirical list |
| 2 | Third-party arXiv | Only in `§4b` of `EFC_Validation_Ledger.html`, tagged `[external — …]` |
| 3 | EFC working notes confronting externals | Own DOI + own `EFC-VAL-2026-0XX` report ID; flip `§4b` status |

**Language rule:** external observations are `consistent with` / `overlaps with` / `within EFC prediction band` — never `confirms EFC`.

**Pre-registration rule:** every prediction must cite the **prior** EFC DOI where it was first stated, in the same sentence.

---

## JSON-LD and structured interop

- [`/ecosystem.jsonld`](../../ecosystem.jsonld) — top-level knowledge graph
- [`/jsonld/`](../../jsonld/) — per-entity JSON-LD documents
- [`/meta-graph/`](../../meta-graph/) — cross-references
- [`/codemeta.json`](../../codemeta.json) — software metadata (CodeMeta v3.0)
- [`/CITATION.cff`](../../CITATION.cff) — citation metadata

---

## Maintenance scripts (agent-callable)

All under [`scripts/maintenance/`](../../scripts/maintenance/):

| Script | Use |
|---|---|
| `efc_maintain.py` | Full chain (runs the below in order) |
| `efc_verify.py` | Evidence-layer + drift check |
| `efc_drift_detector.py --fix` | Fix count/version drift |
| `efc_sync_dois.py --apply` | Sync DOIs across ledger and indices |
| `efc_gen_ai_friendly.py` | Regenerate AI-friendly packages |
| `efc_ledger_autofill.py` | Autofill empirical/sealed DOIs into Ledger |
| `efc_process_paper.py` | Process one unregistered paper |
| `efc_unprocessed.py` | List unregistered papers |
| `efc_build_wiki.py` | Regenerate [Papers by topic](./03-Papers-by-Topic.md) |

---

## Next

- **Need the vocabulary?** → [06 · Glossary](./06-Glossary.md)
- **Back to the top** → [🏠 Home](./Home.md)
