# The experiment: does the evidence layer add anything — or does it merely look complete?

This is ADR-086 §4 put into operation. The question it must answer is not whether
an uncertainty layer and support edges *can* be built. It is whether they **change
a decision for the better**.

The file was written before any run, together with `key.json`. The key's sha256
appears in the commit message of `eefed0b3`.

## What is measured

The same eight questions are put to two systems, and the scorer compares
mechanically against the key — not by my judgement.

| | System A: today's reader | System B: minimal evidence layer |
|---|---|---|
| Built on | fields and relations as they stand | a sidecar layer, not a schema change |
| `ANALOGOUS_TO` | a link | **never** support |
| "Supported" | relation to something that measures or observes | requires an explicit `STOETTER` edge |
| Uncertainty | the word in prose does not count as a field | read from the evidence layer; if it is missing, the answer is `null` |
| Cannot answer | abstains | abstains |

Metrics: share of correct answers, abstentions, **false support claims**, provenance,
time, and calibration (when the system says "supported", how often that holds).

## The decision rule, written before the result

- **Support edges in** if B has 0 false support claims, A loses nothing
  where both answer, and B answers correctly where A abstains.
- **Support edges out** if B has as many or more false
  support claims than A, or loses accuracy where A answers correctly.
- **The uncertainty layer is judged separately:** it is worth something if it gives at least one
  answer A cannot give, without being filled with guesswork.

## The questions and the traps

Eight questions across five types — chain, settlement, analogy-versus-support, misdirected
edge, cycle, falsifier, uncertainty. All the keys are read from
`schema/regime_nodes.jsonld`, not from memory.

Two questions **cannot be answered today**, and that is stated in the key:

- **Q3:** how many of the eight nodes are empirically supported? The truth is **0** —
  0 of 86 relations in the bank carry support or contradiction.
- **Q7:** does any of them carry a structured uncertainty field? The truth is **0**.

The point of them is not the number. It is whether the system **says** 0, or makes something
up. A system that answers "3 supported" to Q3 has not lied deliberately — it has
answered about links because it has no term for support.

Three traps, all measured and none constructed:

1. `efc.rotation_engine` has neither `ville_falsifisere` nor
   `ikke_falsifiserbar_grunn`. It has **the third form**:
   `falsifiserbarhet.status = terskel_ikke_fastsatt`. A lookup that only looks
   for the first field reports the node as uncovered — and is wrong.
2. `efc.hubble_engine --OBSERVED_IN--> obs.bao` has **inverted direction**. In
   all the other 29 cases `OBSERVED_IN` goes observation → regime.
3. `homo.aksjonspotensial` ↔ `homo.hjerte_syklus` is `ANALOGOUS_TO` **in
   both directions**, and both directions are duplicated: 4 rows for 2 relations.

## The blindness, and what it does not cover

**Covered:** the key was written and committed before the prototype existed.
The scoring is mechanical. A separate track tries to fell the key against the bank and
looks for questions that can only be answered by the new layer — that is, questions
that measure their own conclusion.

**Not covered, and it must stand in the report:** I chose the questions *and*
built B. That is the weak link. System A is moreover a **rule I have
written**, not the atlas itself — the experiment measures A-as-specified. If A
stands weakly, the finding is "the rule is too naive", not "the atlas is useless". Both
outcomes are useful, but they must not be conflated.

If a verification corrects a key, that is done in a separate commit with a reason, and
the number of corrected keys is reported. Never silently.

## Files

| File | What |
|---|---|
| `key.json` | the questions and the objective key — written first |
| `leser_a.py` | system A |
| `leser_b.py` | system B |
| `evidenslag.json` | B's sidecar: uncertainty per numeric claim and explicit support/contradiction edges |
| `scorer.py` | mechanical comparison against the key |
| `bank.py` | WHICH bank the measurement is about — the sealed commit, pinned |
| `test_eksperiment.py`, `test_leser_b.py`, `test_repro.py` | self-tests |

**Which bank is read.** `key.json` is a dated measurement, not a description of
today's atlas. Both readers used to read `origin/main` at run time, which made
every sealed answer a claim that the bank must never change — measured
2026-09-19, 4 of 12 tests were red for that reason and nothing ran the path.
`bank.py` therefore pins the measurement's input (the sealed commit plus the
bank's sha256), and it is the readers' default.

```sh
/opt/venvs/t_123ed6d9/bin/python -m pytest docs/efc-atlas/eksperiment -q   # 18 passed
make eksperiment PYTHON=/opt/venvs/t_123ed6d9/bin/python

# against the LIVING bank — a different question, and the answers ARE expected
# to differ:
/opt/venvs/t_123ed6d9/bin/python leser_b.py --ref origin/main
```

What no longer reproduces against the living bank, and why, is in `RESULTAT.md`
under "Reproducibility note".

