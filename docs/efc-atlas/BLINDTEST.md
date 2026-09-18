# Blindtest: does a research decision get better WITH the atlas?

Status: protocol, not run. The scenarios shall be drawn from the 21
registered open questions in the bank (`schema/regime_nodes.jsonld`,
the field `open_questions`) and from engine/bus questions. Written 2026-09-18 after an independent
assessment (different model, direct API, `model_verified: true`) pointed to
«nothing is demonstrated» as the decisive one of six measured gaps.

## The requirement being tested

> Given a defined research task: does the atlas give a more correct, better
> justified, more actionable or faster decision than a reasonable
> alternative way of working?

The atlas does not need to predict a cosmological transition in order to be a
research instrument. It qualifies if it reliably improves
decisions such as: which connector is built now, which node/engine is
relevant, whether a claim is supported or planned, and whether a conclusion goes
beyond the evidence.

## Design

- **12 scenarios**, drawn from the 21 registered open questions and from
  engine/bus questions in the bank. Matched in pairs by difficulty.
- **Two conditions, crossover:**
  - **A (atlas):** the bank, `atlas_lesing.py`, `atlas_navigasjon.py`, the
    generated views and the declared engine/bus links.
  - **B (baseline):** the repo and ordinary file search/reading. The baseline shall NOT
    be artificially weakened — README, source catalogue and search are available.
- **Isolated contexts** between trials: one scenario per session, no
  reuse of conversation.
- **Random order**, and half of the scenarios switch condition,
  so the difference cannot be attributed to the choice of scenario.

## What the assistant shall deliver per scenario

1. relevant node(s)
2. epistemic status (observed / built / planned / assumed / unknown)
3. best next research action
4. expected observation or result
5. falsifier
6. which sources carry the answer (node id, file, topic)
7. what is still unknown

## Scale (0-2 per dimension, set BEFORE the results are read)

- **correctness** — did the answer hit the key?
- **actionability** — can the researcher actually take the next step?
- **evidence discipline** — are the claims carried by cited sources, without
  implausible extrapolation?
- **gap awareness** — did the answer distinguish between unknown / planned / observed /
  established?
- **falsifiability** — does the answer name a meaningful contradiction?

Sum 0-10. Time and the number of unsupported claims are reported SEPARATELY, not
hidden in the sum.

## Procedure

1. Different answers in advance: a key with acceptable alternatives,
   written before anyone sees generated answers.
2. The answers are labelled A/B only, and assessed in random order.
3. Every cited source is verified afterwards.
4. The condition is revealed AFTER the assessment.
5. A human assessor is not fully independent. Mitigation: a fixed
   rubric with examples of full, partial and zero credit, written down
   in advance.

## What supports the requirement

- at least 20 % higher mean sum than the baseline
- no increase in unsupported claims
- somewhat shorter time to decision
- better distinction between planned and observed
- at least one clear case where the atlas finds a correct next step that
  the baseline misses

The threshold is set before the results are seen.

## What FALSIFIES the requirement

- atlas and baseline score equally and spend equally long time
- the atlas is slower without becoming more correct
- the atlas gives more glib, unsupported answers
- the errors cluster around core words such as «energy flow»
- the assistant retrieves more node names, but does not choose better actions
- planned nodes are taken to be evidence

A small trial cannot prove that the atlas never helps. It can show that
the claimed utility is not observable on representative tasks — and that
is enough to move the requirement from «assumed» to «not demonstrated».

## What is NOT tested here

- whether the atlas improves anything over TIME (requires repeated use)
- whether the nodes are scientifically correctly chosen (requires peer review)
- whether the bus snapshot is representative of the living bus


## How to run it

1. Fetch 12 scenarios: `python scripts/atlas_arbeidskoe.py --sakse` and
   `--ghost` name where something is missing; `open_questions` name what
   is waiting. Choose 12, match them in pairs by difficulty.
2. Write the key (acceptable answers) for ALL 12 before anyone sees a generated answer.
3. Run each scenario in an isolated session: 6 with `scripts/atlas_inngang.py` +
   `scripts/atlas_lesing.py` available, 6 with only the repo and file search.
4. Switch condition for half, so the difference cannot be attributed to
   the choice of scenario.
5. Assess A/B blindly according to the scale above, verify every cited source, and
   reveal the condition at the end.

## What has already been measured, and shall not be measured again

- The atlas reaches 118/118 topics, 39/39 domains and 32/32 engine files.
- 27 of 31 EFC claims can be refuted; 85 nodes measure or are established.
- 21 open questions are registered and quoted verbatim from the bank.
- The five core concepts are namespace values without a node — that is measured, not
  assumed, and is part of what the test shall uncover the consequences of.
