# The bridge convention — who owns which field between engine and atlas

**The rule is code: `scripts/maintenance/efc_bro_konvensjon.py`. Read it there.**
This document explains *why* — and why precisely those boundaries. A
rule that stands in two places can drift apart; a table can be tested.

## The problem, measured

Every engine has a `regime_node(params)` — the self-description — and the atlas has
an instance of the same node in `schema/regime_nodes.jsonld`. Two descriptions of
one thing, maintained by hand on both sides. Measured 2026-09-17
(t_2dcd2d82) and again 2026-09-18:

    20 engines, 20 atlas nodes — 20 with deviations, in BOTH directions
    111 field deviations in the class (test_bro_konvensjon, unfixed tree)

So «the engine wins» is not an answer: for `regime.validity`, `law_form`,
`stipulasjoner.terskler` and `maale_paradigme.koordinater` the engine is the source;
for `nivaa`, `epistemikk`, `ontology` and `perspektiv` the atlas is the source, and
it is the engine that must be corrected.

## The convention

**The engine owns** fields that are derived from the engine's parameters or from the way
the engine computes. They are WRITTEN from the engine to the atlas
(`efc_bro_synk.py --skriv`):

| Field | Why the engine |
|---|---|
| `regime.validity`, `regime.law_form`, `regime.name` | built from the effective parameters — a hard-coded text lies when the engine is called with others |
| `stipulasjoner.terskler`, `stipulasjoner.motor` | the threshold stands in the code; the name is the code's own |
| `maale_paradigme.koordinater`, `enheter`, `status` | which axes the engine classifies along |
| `measure.*`, `phase`, `episenter`, `buffer.*`, `emergence.*`, `fractal.*`, `coupling.*`, `observer.*`, `synlighet` | the engine's own description of how it measures and what it is not |

**The atlas owns** fields that are curated claims ABOUT the node: where it belongs in
the plateau, how the consensus is carried, which analogies it is tied to, what
it does not say, and which source the placement rests on. The engine cannot
derive them from its parameters. If it still emits them, it must say the
SAME as the atlas — and when the two diverge, the engine is corrected:

| Field | Why the atlas |
|---|---|
| `id` | the identity is registered; an engine that emits an unregistered id is not connected to anything |
| `nivaa.*` | the plateau graph is the atlas's structure (the rule 49 invariants read it), and an engine that knows only its own parameters cannot place itself on the ladder |
| `epistemikk.*`, `perspektiv` | truth, evidence and consensus status are epistemic claims about the node |
| `ontology.source` | the source the placement rests on |
| `maale_paradigme.alternativer` | which frames were PASSED OVER |
| `buss_domene`, `ville_falsifisere`, `falsifiserbarhet.*`, `analogi.*`, `prediction.*` | curated: what the node does not say, what would take it down, which analogy it stands in, and a sealed prediction |

**Two exceptions from equality**, both in `DELMENGDE`: `ontology.assumes` and
`maale_paradigme.alternativer` are lists where the atlas must be able to carry more than
the engine (a curated assumption the engine does not know is allowed; one the engine
ASSERTS and the atlas has not taken a position on is not allowed). Then the test fails
until someone has curated it into the atlas.

## No third owner

A field the engine emits that neither table names is a HOLE — not a
free zone. Both the test and `--sjekk` stop until someone has taken a position.
The schema also holds node types that are not engine nodes (`/settlement/*`,
`/revisjon`, `/observer/maalepavirkning`); they are named in `UTENFOR_BROEN`
because an omission must be declared, not silent.

## Why not just regenerate everything from the engine

Because the atlas would then lose what the engine does not know: that the background
solver is a hypothesis without measured evidence (`efc.efc_background_engine` said «proxy» about a
derivation that is not measured), that `efc.lensing_engine` stands on plateau 0, that
the rotation engine runs the LCDM limit of the EFC frame. And conversely: `regime.validity`
cannot be curated without becoming wrong the day the parameters change.

## The tools

| Tool | Does |
|---|---|
| `efc_bro_synk.py --sjekk` | measures the whole class, split by owner; exit 1 on deviation |
| `efc_bro_synk.py --skriv` | writes the engine-owned fields back (idempotent, format guard) |
| `efc_bro_synk.py --json` | machine-readable report (for the maintenance round) |
| `tests/test_bro_konvensjon.py` | binds the whole class: coverage, field-by-field equality, no holes, schema coverage |

Canonical parameters are read from the test module that owns them — one source for the test
and the sync. Engines where the parameters are constructed (victron: series ->
`params_for`; the background: `EFC = {**LCDM, ...}`) declare them in a
`bro_kanoniske()` in their own test module, so that neither the sync nor the test
guesses which module-level dict is «the canonical one».

## The old reconnaissance did not become a separate script

`bro_drift_audit.py` (t_2dcd2d82) found engines by scanning the test modules and
guessed parameters from module-level dicts. What it could do — list-shaped
parameters (`KANONISKE`) and `params_for(...)` — now lies in the ONE
resolver (`efc_bro_konvensjon.kanoniske_parametre`), used by both the sync
and the test, and all 20 engines are measured. Coverage is tested instead: a new engine
without a bridge, or a bridge without an atlas node, fails `test_bro_konvensjon.py`. A
separate audit script alongside it would be a second tool measuring the
same reality — the class of drift this card exists to stop.

## Known findings not closed here

* `epistemikk.sosial_mekanisme` is a TEMPLATE on all 20 engine nodes in the atlas
  (17 with long text, 3 with short). Rule 46 requires individualised text;
  the convention binds engine to atlas, but does not say the text is good.
* `efc.efc_background_engine`'s curated short text was replaced by the engine's
  fuller self-description when the node was regenerated (it had never been
  derived). The provenance is kept in `ontology.source`.
