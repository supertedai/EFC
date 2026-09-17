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
(`/opt/agent-work/EFC` has since been brought level with `main`):

| Copy | Nodes | Problem |
|---|---|---|
| `/opt/agent-work/EFC` (working tree) | 72 | six PRs behind `origin/main` |
| `/home/morten/EFC-review` (`pr-463`) | 82 | a PR branch, later merged |
| `.worktrees/vedlikehold` | 45 | `perspektiv` missing on all 45 nodes |

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

## What is *not* claimed here

The guard in `supertedai/Hetzner` (`metrikk/atlasoppgjoer.py`, PR #1016)
applies the same rule inside that repository. This document does not
describe that file — it lives in a different repository and is reviewed
there.

## The other copies

Every other copy of the atlas is a **working copy** and must not be read as
the atlas. They exist for editing, not for answering.

## Measured on the authoritative ref

`origin/main` @ `2026-09-17`: **82 nodes.**

| Measure | Value |
|---|---|
| Nodes | 82 |
| Nodes with `_engine` in the id | 19 |
| Distinct values of `stipulasjoner.motor` | 32 |
| `perspektiv` set | 82 of 82 — 48 paradigm / 23 consensus / 11 academia |

**Two different numbers, and both are real.** "Engines" is ambiguous: 19
node ids contain `_engine`, while 32 distinct engine names appear in
`stipulasjoner.motor`. Earlier text said "19 engines" and meant the first
measure while reading as the second. State which one you mean.
