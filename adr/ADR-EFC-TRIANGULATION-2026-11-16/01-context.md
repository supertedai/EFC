# Context

The EFC corpus has grown to 166 DOIs, ~170 paper directories, 14 public HTML pages, a validation ledger, and multiple generators. The owner's stated fear is that the repo and the agent have become so large that drift accumulates invisibly in every link, and that he cannot sit and approve every step.

There are two distinct trust questions that must not be conflated:

- **Type A — mechanical consistency.** Counts, versions, file references, DOI resolution, byte-identical projections, no-orphan. Deterministic. The system can verify itself 100 %. The owner is already (or can immediately be) out of this loop.
- **Type B — scientific truth.** Is a claim right? Are the connections real? This is where triangulation, cross-check and multihop live. It cannot be self-verified: an LLM checking another LLM running the same underlying model is *reading consistency*, not independent validation.

The trap this ADR must avoid: building "triangulation" as several roles of the *same* model agreeing with each other. That feels like safety but is circular — it is the precise failure mode already recorded in the house memory ("all agents are gpt-5.6-luna, so cross-role 'agreement' means reading consistency, never independent validation").

The only honest source of independence for Type B is *external*: different data, different external teams/papers, or time separation (sealed-before-test). Internal self-agreement must never raise confidence.
