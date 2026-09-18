# Reading the atlas — which copy is authoritative

**The rule is implemented in `scripts/atlas_lesing.py`. Read it there.**

This document explains why. It deliberately does *not* restate the rule as
prose: a rule written twice can drift, and a document cannot be tested for
meaning. Three tests that only required the words "origin/main" and
"working copy" to be present passed a mutant that said the exact opposite —
they saw the form, not the meaning. The same failure as a test checking
`startswith("git:")` and letting any value through.

So the rule is code, and the test proves it by **changing the world, not the
text**: it mutates the working-tree file and requires the read to be
byte-for-byte identical. A naive implementation changes here. That is the
only test that separates "read from the ref" from "read from the working
tree", whatever the documentation says.

## Why this had to be written down at all

The atlas exists in several working copies, and they do not show the same
map. Measured 2026-09-17:

**Historical measurement, 2026-09-17** — kept because it is what
motivated the rule, not because it describes these copies today
(the primary working clone has since been brought level with `main`):

| Copy | Nodes | Problem |
|---|---|---|
| the primary working clone | 72 | six PRs behind `origin/main` |
| a separate review clone (`pr-463`) | 82 | a PR branch, later merged |
| a maintenance worktree | 45 | `perspektiv` missing on all 45 nodes |

A copy that answers reads as a live atlas. The figure "82 atlas nodes"
reported in the *Atlas, NATS and motorer* thread came from a PR branch, not
from `main` — and a guard built on the working tree reported 72 while `main`
had 82. Same failure mode as 2026-09-16 (atlas sync against components that
did not run) and 2026-09-14 (memory available but not steering).

## Freshness

`origin/main` is a **remote-tracking ref** and can be stale. `les_atlas()`
does not fetch on its own — it reports the full commit SHA it read, so a
stale ref is visible in the result rather than in the reader's assumption.
Pass `hent=True` when the reader wants the freshest available.

## Reading the gaps — with a size

The rule for *how large* a gap is lives in `scripts/atlas_volum.py`. Same
discipline as above: the number is not restated here, because a number
written twice is a number that drifts.

    python3 scripts/atlas_volum.py --hull     # not-covered, largest first
    python3 scripts/atlas_volum.py --alle     # every domain, largest first

Sorting alphabetically answers a question nobody asked. **Historical
measurement, 2026-09-17** — kept because it is what motivated the rule,
not as a current figure: `verden.vaer` carried 190 229 messages and
`verden.utdanning` 2 598, and the reading was identical for both — 73×
apart. The largest prediction-and-settlement loop on the bus sat behind
the same words as the smallest. Today's figure comes from `--hull`.

The size is **measured**, not estimated. `--maal` reads the per-subject
message counts from the bus through the house tool for the bus (its path
is given by `VERDEN_MCP`; the module never carries a host path) and writes
them to `schema/nats_domener.snapshot.json`, whose `_proveniens.maalt` is
the only freshness claim made anywhere. `schema/atlas_dekning.json` carries
the sum per domain, and a test derives that sum again rather than trusting
it. A volume table in the code would rot at the first change in bus
traffic — and a test forbids one.

## Putting something in — the atlas's retain

Reading has an entrance (`finn`), and adding has a door: `--innta` takes a
fragment from a session, places it with `plasser()`, and appends it to a queue
with its provenance and its threshold verdict. Nothing becomes a node by
itself — automation that maps everything would fill the atlas with noise.

    python3 scripts/atlas_lesing.py . --innta "vulkansk aske i stratosfaeren" --kilde samtale
    python3 scripts/atlas_lesing.py . --bekreft "vulkansk aske i stratosfaeren"

The second command is the closed loop: it answers whether the atlas *now*
carries the fragment — naming the node, the fields it matched in, the
generator's code, the placement and the visibility — and whether the node is
new since the intake rather than something that lay there already. The queue
is host-local (`data/inntak` is ignored by git), and that is why the
confirmation reads the **atlas**, not the queue: the queue is working memory,
the atlas is the truth.

Both rules are code — `bekreft`, `NODE_TERSKEL` and `NODE_ANDEL` in
`scripts/atlas_lesing.py`. This section only says why the door exists.

## What is *not* claimed here

An operations guard in a separate systems repository applies the same
rule there. This document does not describe that file — it lives in
different repository and is reviewed there.

## The other copies

Every other copy of the atlas is a **working copy** and must not be read as
the atlas. They exist for editing, not for answering.

## Measured on the authoritative ref

`origin/main` @ `2026-09-17`: **82 nodes.**

| Measure | Value |
|---|---|
| Nodes | 82 |
| Nodes with `_engine` in the id | 19 |
| Distinct `stipulasjoner.motor` values, empty excluded | 32 |
| Distinct `stipulasjoner.motor` values, raw | 33 |
| Nodes with `motor` empty | 50 |
| `perspektiv` set | 82 of 82 — 48 paradigm / 23 consensus / 11 academia |

**Two different numbers, and both are real.** "Engines" is ambiguous: 19
node ids contain `_engine`, while 33 raw values appear in
`stipulasjoner.motor` (32 non-empty — 50 nodes carry an empty string).
Earlier text said "19 engines" and meant the first measure while reading as
the second. State which one you mean, and whether empty values are counted.
