# Options

## Option A — Internal multi-role agreement (rejected)
Several roles of the same model cross-check each other; agreement raises confidence.
- **Pro:** cheap, fast, no external dependencies.
- **Con:** circular. Same-model agreement is reading consistency, not validation. It manufactures false safety. **Rejected.**

## Option B — External-source triangulation + deterministic cross-check + confidence levels (chosen)
Retrieve *independent external* sources for a claim, compare deterministically (number vs number, field vs field), and set confidence from the count of *independent* agreeing sources. Internal self-agreement never raises confidence. Escalate only low-confidence / conflicting / high-stakes claims.
- **Pro:** real independence where it matters; gets the owner out of the routine loop; deterministic where possible; honest about the LLM ceiling.
- **Con:** requires defining "independent" precisely and building the retrieval + comparison machinery.

## Option C — Full autonomy (rejected)
No human gates anywhere, including falsification verdicts, canonization and publish.
- **Pro:** maximum removal of the owner.
- **Con:** irreversible error cost; a self-checking system's independence ceiling is structural, so "safe enough to never need a human" is not reachable for Type B. **Rejected** — high-stakes edges stay gated.

## Option D — Do nothing (rejected)
Keep every step human-gated.
- **Con:** does not meet the stated goal; the owner must remain in the loop for routine claims. **Rejected.**
