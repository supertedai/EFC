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
