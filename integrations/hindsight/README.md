# Hindsight bank `efc`: configuration

Desired configuration for the Hindsight memory bank `efc`, written against
Hindsight **1.2.1** (2026-11-10). The Hindsight server itself is not in this
repository. This folder holds the target state and a script that applies it.

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
- `entity_labels` sets a controlled vocabulary.
- Directives hold the hard rules.

## What each setting fixes

| Observed problem | Setting |
|---|---|
| Entities that are whole claims | `retain_mission` (entities are short proper names), plus `entity_labels` of type `multi-text` for framework, dataset, observable and doi, and closed enums for evidence layer, RCMP regime, EBE regime, KC1–KC5 and Ledger status |
| Graph nodes without visible relations | Label entities link memories automatically (same `key:value` produces a graph link), and `tag: true` makes every label filterable in recall and reflect |
| Schema not enforced on writes | Enum label groups silently drop values outside the vocabulary, so the evidence-layer list from `docs/validation-ledger/review-protocol.md` is enforced at extraction |
| Knowledge tree returned no roots | `pages`: four folders and seven pages, rebuilt from observations after each consolidation |
| Duplicate raw facts alongside observations | `recall_prefer_observations: true` (also applies to MCP callers that never pass the flag) |
| Memory depth | `recall_budget_function: adaptive`, where search breadth scales with `max_tokens`, and `high` = 0.3 × `max_tokens` (30–2000) |
| Chat outranking canonical sources | `reflect_mission` prefers `source=figshare` / `source=ledger` metadata (reflect has seen document metadata since 0.10.2) |

## Safety

The script never removes anything:

- `entity_labels` are merged additively. Existing label groups (e.g. `lesson`,
  set by `hermes-opus/metrikk/lesson-label.py`) are kept. A spec group whose
  key already exists is left as the bank has it.
- `retain_mission`, `observations_mission` and `reflect_mission` that the bank
  already overrides are kept and printed, unless you pass `--replace-missions`.
- The full config is backed up to `~/.hermes/bankconfig-backup/` before any
  write, and read back after it.
- Directives and pages are only created, never changed or deleted.

Read the dry run's list of existing label keys. If the bank already has
something like `regime` or `epistemic_layer`, remove the overlapping group
from `efc_bank.config.json` before applying, so the bank does not end up with
two vocabularies for the same dimension.

## Running it on the Hetzner host

The Hindsight API is private (`10.9.0.2:8006` over WireGuard to byopus12), so
run the script from the Hetzner host or from the Opus session there. The
defaults read the URL and `MCP_HINDSIGHT_<BANK>_API_KEY` from
`~/.hermes/.env`:

```bash
python3 integrations/hindsight/apply_efc_bank.py --bank efc
```

## Order of operations

1. Clone the bank for testing (no LLM cost; leave webhooks behind):
   `POST /v1/default/banks/efc/clone?target_bank_id=efc-test&include_bank_config=false`
2. Do a dry run on `efc-test`, then apply with `--apply`.
3. Check the prompt: `POST /v1/default/banks/efc-test/prompts/preview` for
   `retain`, `consolidation` and `reflect`.
4. Reprocess `efc-test`'s documents so existing memories get the new labels.
   Labels only apply to new retains. Compare entities and recall with `efc`.
5. Apply to `efc`.

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
