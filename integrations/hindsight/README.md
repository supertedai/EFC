# Hindsight bank `efc`: configuration

Desired configuration for the Hindsight memory bank `efc`. The Hindsight
server itself is not in this repository. This folder holds the target state
and a script that applies it. The live EFC API reported OpenAPI server
version **1.2.0** and the available Python package was
`hindsight-client 0.10.3` when measured on 2026-11-13. Hindsight **1.2.1**
renames Knowledge Pages to Pages; the script supports both method families.

| File | Purpose |
|------|---------|
| `efc_bank.config.json` | Per-bank overrides, directives and page tree: the target state |
| `apply_efc_bank.py` | Diffs the live bank against the target and applies it with `--apply` (dry run by default) |

## Principle

Inside `efc`, the stored evidence-backed record is the working truth, so the
bank reads with **low skepticism (2)**, **high literalism (4)** and
**low empathy (2)**. Rigour is applied when something is stored, not every
time it is read:

- `retain_mission` decides what counts as an established fact and what is only
  an attributed claim.
- `_mission_additions` describes idempotent additions to an existing
  bank-authored retain/reflect mission; it does not replace that text.
- `entity_labels` sets a controlled vocabulary.
- Directives hold the hard rules.

## What each setting fixes

| Observed problem | Setting |
|---|---|
| Entities that are whole claims | `retain_mission` (entities are short proper names), plus `entity_labels` of type `multi-text` for framework, dataset, observable and doi, and closed enums for evidence layer, RCMP chronology, EBE physical regime, KC1–KC5 and Ledger status |
| Graph nodes without visible relations | Label entities link memories automatically (same `key:value` produces a graph link), and `tag: true` makes every label filterable in recall and reflect |
| Schema not enforced on writes | Enum label groups silently drop values outside the vocabulary, so the evidence-layer list from `docs/validation-ledger/review-protocol.md` is enforced at extraction |
| Knowledge tree returned no roots | `pages`: four folders and seven pages, rebuilt from observations after each consolidation |
| Duplicate raw facts alongside observations | `recall_prefer_observations: true` (also applies to MCP callers that never pass the flag) |
| Memory depth | `recall_budget_function: adaptive`, where search breadth scales with `max_tokens`, and `high` = 0.3 × `max_tokens` (30–2000) |
| Chat outranking canonical sources | `reflect_mission` prefers `source=figshare` / `source=ledger` metadata (reflect has seen document metadata since 0.10.2) |

## Safety

The script never removes entity-label groups, directives or pages:

- `entity_labels` are merged additively. Existing label groups (e.g. `lesson`,
  set by `hermes-opus/metrikk/lesson-label.py`) are kept. A spec group whose
  key already exists is left as the bank has it.
- Bank-authored `retain_mission`, `observations_mission` and `reflect_mission`
  overrides are preserved. Only the exact additions declared in
  `_mission_additions` are appended, once, to the relevant existing text.
  `--replace-missions` remains the explicit opt-in to replace mission text
  with the spec's full value.
- The full config is backed up to `~/.hermes/bankconfig-backup/` before any
  write, and read back after it.
- Directives and pages are only created, never changed or deleted.

### Client/server schema drift

The installed `hindsight-client` can lag the server: a key can be a valid
override (and be served back by `GET /v1/default/banks/<bank>/config`) while
`update_bank_config` has no keyword for it. The script sends the keys the
client exposes through the client and PATCHes the rest to
`/v1/default/banks/<bank>/config` with `{"updates": {...}}`, then reads the
whole config back. A rejected key fails the run before directives and pages
are touched.

Hindsight 1.2.1 renamed Knowledge Pages to Pages. The script resolves and
preflights these aliases **before any write**:

| Operation | Pages API (1.2.1) | Legacy name (1.x) |
|---|---|---|
| Read tree | `get_page_tree` | `get_knowledge_base_tree` |
| Create folder | `create_page_folder` | `create_knowledge_folder` |
| Create page | `create_page` | `create_knowledge_page` |

The call adapter handles keyword-only and positional bank-id signatures. If
neither alias for a required operation exists, it stops before config,
directive or page writes. Legacy names are documented as kept through 1.x;
the script does not depend on them surviving into 2.x.

For REST config updates, any HTTP 2xx is accepted as transport success
(including 204, which has no response body), but the script then GETs the
config and verifies every requested field. Non-2xx or a mismatched readback
stops before directives/pages are changed. A successful PATCH alone is not
reported as a successful config update.

Review label meanings, not only names. In the EFC bank, `evidence_layer` is
provenance while `epistemic_layer` is document level; `rcmp_regime` is the
cosmological/entropy chronology while `physical_regime` is scale/structure.
Those are separate axes. The repository target uses L0–L3 for `rcmp_regime`,
while the measured live bank definition for `physical_regime` uses
`S_flow`/`S_trans`/`S_latent`; preserve the live definition when the key
already exists.

## Running it on the Hetzner host

The Hindsight API is private (`10.9.0.2:8006` over WireGuard to byopus12), so
run the script from the Hetzner host or from the Opus session there. The
defaults read the URL and `MCP_HINDSIGHT_<BANK>_API_KEY` from
`~/.hermes/.env`:

```bash
python3 integrations/hindsight/apply_efc_bank.py --bank efc
```

## Order of operations

1. If testing a full config write, use an isolated test bank and first measure
   the storage/copy and LLM costs for the intended test. The clone endpoint is:
   `POST /v1/default/banks/efc/clone?target_bank_id=efc-test&include_bank_config=false`
2. Do a dry run on `efc-test`, then apply with `--apply`.
3. Check the prompt: `POST /v1/default/banks/efc-test/prompts/preview` for
   `retain`, `consolidation` and `reflect`.
4. Labels apply to new retains. Do not reprocess documents as an ordinary
   backfill: the API deletes the document's existing memory units before
   re-extracting them. A history migration needs its own snapshot, mapping,
   test plan, rollback and owner approval.
5. Apply to `efc` only after the exact change has passed review, a full config
   backup is created, and the owner has approved the production write.

When retaining, send `metadata: {"source": "figshare" | "ledger" | "chat" | ...}`
so the reflect precedence has something to act on.

## Server-level settings (on the Hindsight host, not per bank)

These are environment variables. They cannot be set through the bank config API.

| Variable | Recommended | Why |
|---|---|---|
| `HINDSIGHT_API_DEFAULT_TIMEZONE` | `Europe/Oslo` | Retain timestamps without an offset are read correctly (1.2.0) |
| `HINDSIGHT_API_RECALL_DECISION_MODEL_PRUNE` | `true` | Drops memories that don't help the query, when a decision model is configured (1.2.0) |
| `HINDSIGHT_API_RECALL_DECISION_MODEL_DEDUP` | `true` | Drops repeated memories (1.2.0) |
| `HINDSIGHT_API_RERANKER_TYPESAFE_PRUNE_CANDIDATES` | `true` | Only if the TypeSafe Jev reranker is used (0.10.1) |
| reranker | default `hindsight-ai/hs-rerank-1` | New multilingual default since 1.2.0, good for Norwegian and English content |

## Not set here on purpose

- `default_observation_scopes`: grouping observations by `framework:*` is
  possible (1.1.0), but memories without a framework label need testing on
  `efc-test` first.
- `entities_allow_free_form: false`: this would drop people and other named
  entities that the labels do not cover.
- The `morten` bank: it is left at its current settings.
