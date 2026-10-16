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
| `epistemikk.*`, `perspektiv` | truth, evidence and consensus status are epistemic claims about the node. `sosial_mekanisme` must additionally be INDIVIDUALIZED — see below |
| `ontology.source` | the source the placement rests on |
| `maale_paradigme.alternativer` | which frames were PASSED OVER |
| `buss_domene`, `ville_falsifisere`, `stipulasjoner.ikke_falsifiserbar_grunn`, `falsifiserbarhet.*`, `analogi.*`, `prediction.*` | curated: what the node does not say, what would take it down, why it cannot be struck down, which analogy it stands in, and a sealed prediction |

**Two exceptions from equality**, both in `DELMENGDE`: `ontology.assumes` and
`maale_paradigme.alternativer` are lists where the atlas must be able to carry more than
the engine (a curated assumption the engine does not know is allowed; one the engine
ASSERTS and the atlas has not taken a position on is not allowed). Then the test fails
until someone has curated it into the atlas.

## Both sides saying the same thing is not enough — the text must be individualized

The convention binds engine to atlas, but says nothing about the TEXT being
good. Measured 2026-09-18 (t_b5d8643c): all 20 engine nodes carried one and
the same template in `epistemikk.sosial_mekanisme` — 17 the long one, 3 the
short — with no guard reacting, because `tests/test_epistemikk_v3.py`
compared only nodes with `perspektiv == "konsensus"` while the engine nodes
are `minoritet`. Rule 46 calls template text here false traceability: the
text must state which social forces carry the CLAIM (who says it, who would
gain, who would lose).

The class was bigger than the engines: 47 nodes shared three texts (30 long,
7 short ASCII, 10 h2o/optics). All 47 are now individualized — 126 nodes,
126 distinct texts — and the guard covers the WHOLE population where the
field is set, with a separate test requiring the field to be non-empty
everywhere. A node without an individualized mechanism fails
`test_epistemikk_v3.py`, not only a consensus node.

New nodes (and new engines) hit this guard on purpose: writing a template to
get moving is exactly what the test forbids. The texts are English (Morten's
language rule of 2026-09-17), and so are the additions in this document.

## No third owner

A field the engine emits that neither table names is a HOLE — not a free
zone. Both the test and `--sjekk` stop until someone has taken a position.

The schema also holds fields that NO bridge owns. They stand in
`UTENFOR_BROEN` with **the reason written down**: an omission must be named
AND justified, not only named, because without a reason the next reader
cannot decide whether the name still holds.

| Outside the bridge | Why (measured 2026-09-19) |
|---|---|
| `open_questions` | the node's OWN text in the bank: written by the migration from `stipulasjoner.buss_status` and by curation — never by the engine (0 hits in `efc_inference/`) and never by the generator (the schema says it itself: «the ONLY source of questions in the atlas»). 21 nodes carry it, 0 of the 20 registered bridges |
| `lagdeling.*` | belongs to the layered biology nodes (33 nodes in the bank, 0 of the 20 bridges); the engine has no layering to emit |
| `revisjon` | the house's own bookkeeping, never an engine node; 0 nodes carry it today, but the schema can express it |
| `observer.maalepavirkning` | a curated meta-question about the observer, not derivable from the engine's parameters; 0 nodes carry it today |

`/settlement/*` is on the other hand NOT outside the bridge: `efc.growth_engine` carries it,
and it is atlas-owned (the table above). An earlier edition of this document
named it as a node type outside the bridge — that contradicted `ATLAS_EIDE`,
and five such entries stood in `UTENFOR_BROEN` at the same time as they had an
owner. They are removed, and
`test_every_declared_omission_carries_its_reason` keeps them out:
an omission that contradicts the ownership is not an omission, it is a claim
that the field stands without a rule — and that claim was false.

## Why not just regenerate everything from the engine

Because the atlas would then lose what the engine does not know: that the background
solver is a hypothesis without measured evidence (`efc.efc_background_engine` said «proxy» about a
derivation that is not measured), that `efc.lensing_engine` stands on plateau 0, that
the rotation engine runs the LCDM limit of the EFC frame. And conversely: `regime.validity`
cannot be curated without becoming wrong the day the parameters change.

## The tools

| Tool | Does |
|---|---|
| `efc_bro_synk.py --sjekk` | measures the whole class, split by owner; exit 1 on deviation. It also writes the coverage line: how many engines with `regime_node()` exist, how many are measured, and the names of the declared non-bridges. Exit 1 too when an engine stands in none of the tables |
| `efc_bro_synk.py --skriv` | writes the engine-owned fields back (idempotent, format guard) |
| `efc_bro_synk.py --json` | machine-readable report (for the maintenance round): `dekning` + `avvik` |
| `tests/test_bro_konvensjon.py` | binds the whole class: coverage, field-by-field equality, no holes, schema coverage, and that the omissions are justified without contradicting the ownership |
| `tests/test_epistemikk_v3.py` | binds the TEXT: `sosial_mekanisme` is present on every node and individualized (no text shared by two nodes) |

Canonical parameters are read from the test module that owns them — one source for the test
and the sync. Engines where the parameters are constructed (victron: series ->
`params_for`; the background: `EFC = {**LCDM, ...}`) declare them in a
`bro_kanoniske()` in their own test module, so that neither the sync nor the test
guesses which module-level dict is «the canonical one».

## The declared non-bridge class — the twelve biology engines

The `BROER` register covers 20 bridges. Twelve engines define `regime_node()`
without standing there; they stand in `IKKE_BRO_MOTORER` because they have their
own atlas contracts and are not EFC bridges (#527): `ActionPotentialEngine`
(action potential), `CardiacCycleEngine` (heart cycle), `CellCycleEngine` (cell
cycle), `EvolusjonEngine` (evolution), `FeberRegimeEngine` (fever regime),
`FluxusEngine`, `GenreguleringEngine` (gene regulation), `HomeostaseBufferEngine`
(homeostasis buffer), `ImmunologiEngine` (immunology), `MetabolismEngine`,
`OkologiEngine` (ecology) and `SovnVaakenEngine` (sleep/wake).

Until 2026-09-19 (t_1f95225a) this was in practice a **silent** omission:
`--sjekk` compared the 20 and wrote «no deviation between engine and atlas». It
did not see that the class it did not measure was also the class it did not
name — the bridge was green by absence. `--sjekk` now writes the coverage line
and names the twelve, and the number stands in the docstring of
`efc_bro_synk.py`, bound mechanically by `tests/test_bro_konvensjon.py` (the
docstring and the number cannot drift apart). An engine that none of the three
tables names is a HOLE: `--sjekk` fails and names it.

Why they are not registered — measured, not a matter of taste:

* The sync has no canonical parameter SOURCE for them: the parameters are read
  FROM the test module a bridge points at, and no bridge points at their engine
  file (11 of 12 therefore stand in `MOTOR_UTEN_PARAMKILDE`). The values do
  exist, though — all 12 are run by `tests/test_biologi{_motorer,_engines}.py`
  and `test_biology_engines.py`, four engines each — so registering them is not
  about inventing data, but about naming one source per engine (the house's own
  form: `bro_kanoniske()` in the test module) and taking the ownership question
  first.
* Measured 2026-09-19: 8 of the 12 answer `regime_node({})` with their node
  (Evolusjon, Feber, Fluxus, Genregulering, Homeostase, Immunologi, Okologi,
  SovnVaaken); 4 raise KeyError without their parameters (ActionPotential,
  CardiacCycle, CellCycle, Metabolism). The omission is about the missing
  source, not about the engines being unable to run.
* And `--skriv` would write the engine's terse strings over the atlas's curated
  text. Measured on `homo.hjerte_syklus`: `/regime/validity` is a paragraph in
  the bank and `t in [0, 0.8] s; NaN outside` in the engine. That is a content
  regression dressed as a sync, and that decision belongs to the owner.

Each of the twelve points at exactly one node in the bank (the engine file's
stem name is the node's `stipulasjoner.motor`), and that node carries the reason
— it is the test `test_every_declared_non_bridge_has_a_declared_reason` that
holds: an omission must be named, not silent, and a list that only grows is the
silent tolerance the convention exists to stop.

That omission had a measurable CONTENT consequence, not only a bookkeeping one:
measured with the gate's own word list and its word-boundary rule (R1), the
twelve carried 25 Norwegian values in engine-owned fields on main — the 8 that
answer `{}`, plus the four that require parameters, measured with the parameters
taken from their OWN test module (not guessed). It is the same class the bridge
did not see: the class the bridge did not measure was also the class that
carried the untranslated text. On the language branch (PR #575) the number is 0,
measured with the same rule — so that hole is closed there, and closing it is
not this card's job. The point here is that the hole is now COUNTED: the next
time someone weighs registering the twelve, both the number and the reason stand
there.

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

## Closed by this round

* **The TEMPLATE in `epistemikk.sosial_mekanisme`** (found above, measured
  2026-09-18 in t_b5d8643c): 20 engine nodes carried one template, 17 the
  long one and 3 the short. Now individualized — and the class turned out to
  be 47 nodes across THREE templates (30/7/10), not only the engines. The
  guard is widened from the consensus nodes to the whole population
  (t_eccc25ef). The texts are English, per Morten's language rule of
  2026-09-17.
* **The FORMAT GUARD in `efc_bro_synk.py` was red on main** (measured
  2026-09-18): `FORMAT` stood at `indent=1` while the file has stood in
  `indent=2` since #545 (d826235b, a 14197/13691-line rewrite of the whole
  file). `--sjekk` then refused with '599848 bytes mot 543142', so
  `make check`'s bridge line failed and `--skriv` could not write at all.
  The form is now measured against the file and bound in
  `test_atlaset_staar_i_synkens_format` — a constant that is not bound to
  the artifact it guards drifts alone. (Found and fixed independently on
  the open PR #549 as well; the two fixes are the same one-line change.)
