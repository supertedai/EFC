# Five reds on main — what each one was, and where the answer lives

**Card**: t_249c4799
**Date**: 2026-09-22
**Measured against**: `fe865b95` (the red revision the card measured on 2026-09-18)
and `5fe3a46d` (= `origin/main` when this note was written)
**Status**: measurement note. The five reds were repaired upstream between
2026-09-19 and 2026-09-21; this note re-measures each one against its own
cause. No code is changed here.

---

## 1. What was asked, and what the measurement says

The card reported five reds on `origin/main` and asked, for each one, whether
the *test's* fact is stale (the K6 case) or the *code* is wrong — with the
rule that a red which guards a fact a landing removed is a red to be
**corrected, never silenced**.

All five were reproduced at `fe865b95` on 2026-09-22 (5 failed, 45 passed,
the same five names as the card), and all five are green on main today.

| # | Test | Measured failure at `fe865b95` | Verdict | Repaired by |
|---|------|-------------------------------|---------|-------------|
| 1 | `test_atlas_avgjorelse.py::test_hver_node_har_tatt_stilling_til_falsifiserbarhet` | `assert len(noder) == 113` → `126 == 113` (the coverage assertion above it **passed**) | stale size pin in the test; the atlas was right | #580 (`b04b3e41`) |
| 2 | `test_atlas_avgjorelse.py::test_grunnen_er_skrevet_for_denne_noden` | `assert not delt` → three texts shared by 27 + 49 + 13 nodes | the demand was stronger than the data can honestly carry (see §3.2) | #580 (`b04b3e41`) |
| 3 | `test_cosmology_engine_bridges.py::test_relasjoner_eksakte` | `efc.hubble_engine: found [('COUPLED_TO','efc.l1'), ('COUPLED_TO','efc.l2')], expected [..., ('OBSERVED_IN','obs.bao')]` | stale fact in the test — the K6 direction (#567) was the correct one | #580 (`b04b3e41`) |
| 4 | `test_epistemikk_v2.py::test_falsifiseringsbetingelsen_er_dekket_ikke_bare_mulig` | `assert (126 - 0) == 113` — coverage complete, the pin stale | stale size pin in the test | #580 (`b04b3e41`) |
| 5 | `test_spraakvakt.py::test_this_change_does_not_grow_the_guard_against_its_parent` | `rc == 1`, `new = [{'file': 'scripts/atlas_lesing.py', 'count': 525, 'expected': 419, 'excess': 106}, {'file': 'tests/test_usikkerhetslag.py', 'count': 124, 'expected': None}]` | **the test was right** — the tree had grown, in guarded paths | translated: #571 (`ec2d9ba9`), #575 (`e8afd591`), record rewritten per file in #600 (`1ceee11a`) |

Three of the five were stale facts in the tests (1, 3, 4); one demanded more
than the tree can carry and was replaced by a measurably weaker-but-checkable
demand (2, argued in §3.2); one was a true finding about the tree and was
repaired in the tree (5).

## 2. The measurement, verbatim

At `fe865b95` (worktree at `/opt/tmp/t_249c4799-old`):

```
$ python -m pytest tests/test_atlas_avgjorelse.py tests/test_cosmology_engine_bridges.py \
      tests/test_epistemikk_v2.py tests/test_spraakvakt.py -q -p no:randomly
5 failed, 45 passed in 24.62s
```

At `5fe3a46d` (= `origin/main`, branch `wt/t_249c4799`):

```
$ python -m pytest tests/test_atlas_avgjorelse.py tests/test_cosmology_engine_bridges.py \
      tests/test_epistemikk_v2.py tests/test_spraakvakt.py -q -p no:randomly
52 passed in 26.52s

$ python -m pytest tests/ -q
1266 passed, 1 warning in 175.87s

$ python -m pytest -q          # root collection: tests/ + efc_inference/tests/ + src
1391 passed, 1 warning in 160.85s
```

The atlas today, measured (not read off the tests): **126 nodes, 31
falsifiable, 4 with a falsifiability status, 91 with a written reason**, and
the reasons use exactly three texts — 63 instrument nodes, 27
established-physics nodes, 1 self-description. The engine↔observation edges
are the six `obs.X --OBSERVED_THROUGH--> efc.Y` pairs, and there is no
`OBSERVED_IN` edge with an engine as subject.

## 3. Each red against its own cause

### 3.1 Two stale size pins (1 and 4)

The atlas grew from 113 to 126 nodes (K4's 13 new nodes, `t_af77c6da`). Both
guards still pinned the old population, so "every node has taken a position"
was measured against a population that no longer existed. Note what the
failures *were not*: in (1) the coverage assertion (`uten == []`) passed
before the size assertion fired, and in (4) the count of nodes without a
position was 0 — the thirteen new nodes had answered. The red measured the
pin, not an omission.

Verdict: the test's fact was old. #580 moved the pins to the measured numbers
(126 / 31 / 4 / 91) and kept them pinned — a node that loses its falsifier or
moves between classes is still a decision someone has to make.

### 3.2 The demand that the data broke the right way (2)

`test_grunnen_er_skrevet_for_denne_noden` demanded that each node's reason be
its own text; the tree answered with three texts spread over 27 + 49 + 13
nodes. #580 measured the premise and replaced the demand: a reason must be a
**declared class** — the class vocabulary is closed, the class sizes are
pinned (`[27, 63]`), every text is at least 40 characters, placeholders are
rejected, and no two texts may be the same statement in two spellings.

This is the one place where the *claim* changed rather than the number, so it
is the one place worth disagreeing with. The argument for the replacement is
sound as far as it goes: 91 reasons drawn from two ideas would be 91
paraphrases of two ideas, and a paraphrase count is not a measure of honesty.
The residual to watch is the other half of the same coin: 63 nodes sharing
one sentence is one sentence answering for 63 nodes on a public claim surface.
The guard against that today is the pinned count, not the sentence's
specificity — a node joining the instrument class is a decision, but the
sentence itself may still be answering more than its node measured. That is a
residual, declared here, not a defect repaired by this note.

### 3.3 The K6 case (3)

Exactly as the card attributed it: the test pinned the inverted edge
(`efc.hubble_engine --OBSERVED_IN--> obs.bao`) that K6 (#567, `t_efcfe7f0`)
removed, and the K6 rename left the expectation list behind. Verdict: the
test's fact was old; the code was right. #580 corrected the expectation and
added compensating coverage — `test_the_edge_to_the_engine_lives_on_the_observation`
holds all six pairs **where they now live**, so removing them from the
engines' expectation lists cannot silently drop the relation.

### 3.4 The one red that was a finding about the tree (5)

The language gate is measured against the change's parent revision, and it
said: relative to `HEAD^`, `scripts/atlas_lesing.py` carried 106 hits above
its record and `tests/test_usikkerhetslag.py` carried 124 hits the record had
never seen. That is not an old fact in a test; that is the gate doing its job
on a tree that had grown Norwegian in guarded paths while the gate was
unlanded.

Repair was in the tree, not in the gate: 18 files translated in #571
(`ec2d9ba9`, including `tests/test_usikkerhetslag.py`), the producers in #575
(`e8afd591`, `scripts/atlas_lesing.py` among them), and the record written per
file in #600 (`1ceee11a`). Measured now: `tests/test_usikkerhetslag.py` — 0
hits; `scripts/atlas_lesing.py` — 21 hits against a record of 21, i.e. a
declared residual, not a bumped ceiling (the record for that file *fell* from
419 to 21). Relative to `HEAD^` the gate is green: `new == []`,
`undeclared_growth == []`.

## 4. What this card did not fix: nothing runs the whole suite

The card's second observation still stands on `5fe3a46d`:

* the workflows name **18 of the 121** files in `tests/`, and **none** of the
  12 in `efc_inference/tests/`;
* `make check` and `make full-check` run `scripts/maintenance/*` and do not
  run pytest at all;
* the job that would close the class exists and is **open, not landed**:
  PR #563 (`wt/t_89eea983`, `cb0f8c69`, `.github/workflows/efc-testsuite.yml`)
  is `OPEN` / `MERGEABLE` on GitHub and is not an ancestor of `main`.

The measurement that matters for landing it: the command the C14 job runs —
`python3 -m pytest -q` from the repository root — is **green on today's main**
(1391 passed). The gate that this card was written because nobody had can land
without a red.

## 5. Limits of this note

* The card's attribution of *when* each red entered (`0789af71` having only
  `test_relasjoner_eksakte` red) was **not** re-measured here; the attribution
  that was re-measured is the repair, per test.
* The reproduction used Python 3.11 with `requirements.txt` plus `pytest`,
  `jsonschema`, `rfc3339-validator`, `PyYAML` and `emcee`. A bare pytest venv
  is not enough: collection stops on `tests/test_growth_friction.py`
  (`ModuleNotFoundError: matplotlib`), which will look like a suite-wide red
  and is an install artefact.
* `tests/test_isolering.py` and `tests/test_risiko_register.py` write canaries
  into pytest's `tmp_path`; they are green here with `TMPDIR` outside `/tmp`.
