# 02 — Options, alternatives and rejections

The card requires: record the proposals and their provenance/status for later retrieval,
minimally, without inventing a node, edge, status, metric or causal relation. Every
option below is judged against that, against the schema, and against what the primary
sources actually state.

## A — Add a new node for "the bridge" (rejected)

Rejected on four independent grounds:

1. `tests/test_atlas_proveniens.py` pins **126 nodes**; a new node changes a pinned
   invariant for a claim that is not itself a regime the bank models.
2. The card forbids inventing a node.
3. The bank's node vocabulary is a *regime/engine* per domain (`efc.lag_c0`, `h2o.*`,
   `kosmos.*`, `homo.*`). "A proposed mapping between two regimes" is not one of those;
   it would be a category invention.
4. A node would need its own `epistemikk`, `measure`, `observer` chain — inventing a
   measurement chain for something with **no instrument** would manufacture exactly the
   structure whose absence is the finding.

## B — Add a typed edge between the cognition node and a cosmology node (rejected)

Candidate predicates, each measured against the schema's closed enum of 9:

- `COUPLED_TO` — asserts the coupling. That is **the** unvalidated claim. Rejected: an edge
  is not a place to assert what the evidence has not shown.
- `EMERGES_FROM` — stronger still (causal/derivational). Rejected on the same ground.
- `ANALOGOUS_TO` — the only defensible candidate, but it is *also* wrong in the other
  direction: the sources claim more than analogy (a formal mapping with equations,
  predictions and a constant), so `ANALOGOUS_TO` would understate them. And the one source
  that does frame it as analogy (`31289806`: "This is not identity — it is the same class of
  thermodynamic arc") is the same source this card treats as *limiting* evidence.
- `OBSERVED_THROUGH` / `OBSERVED_IN` — would claim an observable that does not exist for
  the cross-scale link.

Additional measured ground: **0** of the 86 relations currently touch `efc.lag_c0` or
`efc.lag_d`. The first such edge would therefore be the bank's only assertion of a
cosmos↔cognition relation — a large authored claim carried by a one-word predicate, with
no note field able to encode "proposed and unvalidated" in the schema's vocabulary.
Rejected. The relation count stays at 86 and a regression test pins it.

## C — Rewrite `epistemikk` to describe the proposals (rejected)

`epistemikk` already carries the decisive sentence
(`sosial_mekanisme`: "the cosmology-to-cognition bridge is not established"). It is a
*status* field, not a record; expanding it with narrative would (a) blur the status field's
meaning, (b) risk weakening the pin the new regression test places on
`hypotese`/`proxy`, and (c) is the field most likely to be read as a promotion. Rejected.

## D — Enrich `ontology.proveniens.kilder` + `revisjon` (chosen)

- `ontology.proveniens.kilder` is `ATLAS_EIDE`, schema-declared as `{type, ref, hentet}`
  with `doi` in the enum — the bank's own machine-readable slot for "what this node rests
  on". Adding the two proposal DOIs is a provenance claim of exactly the declared kind.
- `revisjon` is schema-declared "log of changed thresholds/assumptions (date + what)" and
  is not engine-owned, so it survives a bridge sync. A dated entry can carry the limits
  (ansatz, unconstrained γ, equilibrium-level, "does not yet constitute a direct test") and
  the counter-evidence without asserting any new status.
- Neither field changes a count, a status, or a relation. This is the minimal
  representation the atlas actually supports.

## E — Do nothing in the bank; report only in the PR (rejected)

The card's stated purpose is retrieval *by future work in the atlas*. A PR comment or a
chat summary is not the atlas and is not what a later reader queries. Rejected.

## F — Also map `31289806` (and re-classify the proposals as `atlas_scope`) (rejected)

`31289806` is `atlas_scope` / `atlas_candidate` in the repo's coverage register: a DOI
explicitly queued for a **semantic node mapping decision**. Writing its DOI into the bank
would flip it to `atlas_covered` on a literal mention (`in_atlas_literal_url` is a
substring match), silently draining a review backlog item without anyone deciding the
mapping — the repo's own "silent" failure mode. Likewise, editing `figshare/doi-map.json`
to re-class the two proposals as `atlas_scope` would be a classification change with its
own evidence burden, not part of this mandate.

Rejected as **scope**: the paper is cited in `revisjon` by repository path and date
instead, and the DOI tension is left visible in `doi_coverage_matrix.json` where a human
can act on it.

## Trade-offs accepted

- The atlas will contain two DOIs that the coverage register classes `changelog`. That
  disagreement is deliberate, mandated, and visible in the register diff.
- Six differing facts about the bridge live in a *string* (`revisjon`) rather than in
  structured fields, because the schema has no structured bridge-status slot and inventing
  one is out of scope. A future schema extension can promote it; this change does not
  invent the slot.
- `data.mjs` will not display the new entry (measured: the generator does not surface
  `revisjon` or `kilder`). Retrieval is from the bank — the declared truth in this repo
  ("`regime_nodes.jsonld` is the truth; the atlas is its mirror").
