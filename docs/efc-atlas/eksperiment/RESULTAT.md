# Result: the experiment felled the instrument, not the hypothesis

Run 2026-09-18 against `origin/main`. The key (corrected, `67938617`) and the protocol
(`f8bbd7c6`) were written and committed **before** the run.

## The numbers

| | A: today's reader | B: prototype with evidence layer |
|---|---|---|
| Correct | **5** | **7** |
| Wrong | 1 | 1 |
| Abstentions | **2** | 0 |
| False support claims | **0** | **0** |
| Provenance (file:field) | 6 of 8 | **8 of 8** |
| Time | 0.08 s | 0.07 s |

```text
A: {"korrekt": 5, "feil": 1, "avstaaelse": 2, "falske_stoettepastander": 0, "proveniens": 6}
B: {"korrekt": 7, "feil": 1, "avstaaelse": 0, "falske_stoettepastander": 0, "proveniens": 8}
```

Both systems answer alike and correctly on Q1, Q2, Q5, Q6 and Q8. Both fail Q4.

## This does not settle the question — and the reason is mine

The protocol set up three criteria for taking the support edges in. Two of them fell:

**The criterion that was to decide, did not discriminate.** "B shall have fewer false
support claims than A" — both have **0**. System A **did not lie**; it abstained on
Q3 and Q7 instead of answering about links. It was I who gave A permission to abstain,
and thereby I removed precisely the error mode the experiment was built to
find. The instrument cannot settle what it was made for.

**Q4 is invalid for both.** The key was corrected from "1 edge" to "3 edges"
*after* the systems had been built against the old version. Both answer one edge.
That is my sequencing error, not a system error — but the observation stands: **neither
of them finds all three inverted edges.**

**What remains is a coverage gain — and it is narrow.** B answers two
questions A abstains from (Q3 and Q7), both correctly. That is not "better
lookup accuracy"; it is that two questions today have no answer to give.

## What I felled myself along the way, and it must stand

1. **The scorer measured itself.** The first run gave 3 correct for both. The errors
   were the word `merknad` — explanatory prose I had myself put into the key,
   which the scorer compared as if it were the answer. That measures the instrument, not
   the systems. Both scorings stand here; the fix is to **declare** in
   `key.json` which keys are explanation.
2. **The key had four counting errors.** Q3: 16 → 18 relation rows. Q4: 1 → 3
   edges. Q5: 4 rows and "duplicated" → 2 rows, no duplication. Q7:
   `kan_besvares_i_dag` false → true. Found by two tracks independently of each other,
   corrected before the run in a separate commit. The cause is mine: I read an output that
   cut a list with `[:4]` and treated the cut as the number.
3. **A became stronger than specified.** I wrote "if the field does not exist, the answer is
   no". The implementation checked all three falsifier forms and answered Q6
   correctly — including the trap with `efc.rotation_engine`. That is not wrong, but
   it means the A that was measured is not the naive reader I had imagined.

## What it means for ADR-086

- **The uncertainty layer:** weakly supported. It gives an answer A cannot give (Q7 with
  a reason), without filling anything with guesswork. Not more than that.
- **The support edges:** **unresolved, not rejected.** The decisive criterion could
  not fire because A was allowed to abstain. The decision in ADR §3 stands unchanged: no for now.
- **The pipeline change:** not affected. Nothing here argues for it.

## Next iteration — the instrument must be changed here

1. **Remove A's right to abstain on Q3 and Q7.** Force A to answer with a
   rule it actually has (links = support), and measure how many false
   support claims it then produces. Only then can the criterion discriminate.
2. **Correct the key before the systems are built** — or build the systems after
   the key is frozen and verified. The chain was: key → build A/B → verify
   → correct key. It should be: key → verify → freeze → build.
3. **Q4 must require the list, not one example.** Three edges, not one.
4. **Add a question where A answers incorrectly with certainty.** Candidate measured
   today: `efc.rotation_engine` — a lookup that only looks for
   `ville_falsifisere` reports it as uncovered. Q6 catches that only if A is
   specified to be as naive as it would actually have been without the child's
   obliging implementation.

**In short: the experiment did not give the support edges right — and it did not give the atlas
wrong. It showed that I had built an instrument that let both get away.**

---

## Reproducibility note — appended 2026-09-20, after the seal

**This is a CLOSED, DATED measurement.** Its input is not «the atlas» — it is
the atlas as it stood when `key.json` was sealed. Both readers read
`origin/main` at run time, which quietly made every sealed answer depend on a
bank that is still being edited. That is the defect this note records.

* Sealed input: `schema/regime_nodes.jsonld` at commit
  `c70e004d508dbd341271bd3f272e656e8d14db1a` (the commit that added `key.json`,
  both readers and this file), sha256
  `f61049c40463e3eaa22d6d822f165faba59b85d1c28864caba2a6df38f014b2a`.
* The pin lives in `bank.py`, and `test_repro.py` re-derives the table below
  from it.

### What the break was

Measured 2026-09-19 on `origin/main` (`bbc2c3b1`): `pytest
docs/efc-atlas/eksperiment -q` gave **4 failed, 8 passed**. The key was intact
(`key.json` sha256 unchanged, matching `KEY_SHA256`); the bank under the
readers had moved. Two commits landed on 2026-09-18, **68 and 75 minutes after
the seal (21:26)**:

| commit | when | what it did | questions it falsifies |
|---|---|---|---|
| `10087393` (#567) | 2026-09-18 22:34 | the six `OBSERVED_IN` rows with an **engine as subject** became `obs.X --OBSERVED_THROUGH--> efc.motor`; the duplicated `ANALOGOUS_TO` row was removed and the predicate's symmetry declared | Q1, Q4, Q5 |
| `fe865b95` (#568) | 2026-09-18 22:41 | ADR-086 §3.1, adopted by Morten 2026-09-18: the optional `usikkerhet` field came in — `obs.rar` k = 0.415 ± 0.029, `obs.bao` β = 0.16 as a HOLE | Q7 |

The direction matters: **the bank was not broken, it was repaired.** `#567`
closes K6 (`t_efcfe7f0`) and measures exactly the defect Q4 measured here — six
engine-subject edges, one pair stated in both directions. It does not cite this
experiment; the two findings are independent and agree. `#568` is the
uncertainty layer coming in, the question the §"What it means for ADR-086"
section above fed.

A third commit moved the bank on 2026-09-19 without changing any score:
`e8afd591` (#575) put the producers in English. It renamed the phase vocabulary
on the living bank — `observasjon` → `observation`, `teoretisk` →
`theoretical` — while the uncertainty field kept its name `usikkerhet`. The
sealed bank still says `observasjon`, so `leser_b`'s Q4 direction rule ("an
engine stated as observed inside an observation") is live against the seal and
**inert against the living atlas**: there the phase test can never match, and
the reader abstains for a second reason. One more measured argument for reading
a named bank instead of "the atlas".

Per-reference measurement (reader B):

| ref | Q1 `observasjon` | Q4 | Q5 `syklus` | Q7 `antall` |
|---|---|---|---|---|
| `c70e004d`, and its parent | `[obs.fsigma8, obs.s8]` | finds `efc.hubble_engine OBSERVED_IN obs.bao` | true | 0 |
| `10087393` | `[]` | abstains (no inverted edge) | false | 0 |
| `fe865b95` … `origin/main` | `[]` | abstains | false | **1** |

### What reproduces, and what does not

**Reproduces — on the sealed bank, exactly.** Re-derived with `scorer.py`, not
asserted by hand:

```text
A: {"korrekt": 5, "feil": 1, "avstaaelse": 2, "falske_stoettepastander": 0, "proveniens": 6}
B: {"korrekt": 7, "feil": 1, "avstaaelse": 0, "falske_stoettepastander": 0, "proveniens": 8}
```

That is the table at the top of this file, number for number. The argument that
survives is the one about the instrument: the decisive criterion could not fire
because system A was allowed to abstain, and that is a property of the design,
reproducible forever.

**Does NOT reproduce — on the living atlas.** Measured on `origin/main`
2026-09-20: A `{"korrekt": 3, "feil": 3, "avstaaelse": 2, "falske_stoettepastander": 0, "proveniens": 6}`,
B `{"korrekt": 4, "feil": 3, "avstaaelse": 1, "falske_stoettepastander": 0, "proveniens": 8}`.
Everything in this file that describes the *state of the bank* is a statement
about 2026-09-18 and nothing else:

* the row counts in Q3 and the inverted-edge count in Q4 — the six edges are
  gone;
* Q5's «2 rows for the pair» — the pair now stands once, with symmetry declared
  in the predicate;
* Q7's «no node carries an uncertainty field» — one does;
* the coverage gain that survived the run («B answers two questions A abstains
  from, Q3 and Q7, both correctly») no longer holds on the living atlas: the
  bank has the field, B answers 1 where the sealed key says 0, and A still
  abstains on Q7 by construction.

**No new key was written, and that is deliberate.** A re-run against today's
bank is a *different* experiment with a new key: the §"Next iteration" rule
above requires key → verify → freeze → build, and both systems already exist.
Writing a key now would repeat the ordering error this file lists as its second
self-inflicted finding, and would erase the dated measurement.

### How to run it

```sh
/opt/venvs/t_123ed6d9/bin/python -m pytest docs/efc-atlas/eksperiment -q   # 18 passed
make eksperiment PYTHON=/opt/venvs/t_123ed6d9/bin/python
```

`bank.py` reads the seal commit; a shallow clone cannot see it and says so
instead of falling back to another ref. The readers keep `--ref` for honest
runs against the living atlas:

```sh
/opt/venvs/t_123ed6d9/bin/python docs/efc-atlas/eksperiment/leser_b.py --ref origin/main
```

`test_repro.py` asserts both claims: that the sealed table reproduces on the
snapshot, and that the living atlas has drifted in exactly the two ways named
above. If the drift is undone, that test fails and points back to this note —
so this note cannot quietly stop being true.
