# Cognitive Layer

Curated theoretical-reference layer for the **five leading scientific
frameworks of consciousness and cognition** that the EFC / CEM bridge work
draws on. Each subdirectory holds:

| File | Purpose |
|---|---|
| `README.md` | Long-form reference: core claims, formalism, predictions, critiques, EFC bridge |
| `index.json` | Machine-readable metadata (schema.org / EFC index format) |
| `references.bib` | BibTeX of canonical + critical references |
| `papers/` | Downloaded open-access full-texts (where licence permits) |

Layer routes to Neo4j `knowledge_domain='cognitive'` and Qdrant
`cognitive` collection per `LAYER_PATH_MAP` in `tools/orchestrator_v2.py`
(AGI repo).

## Frameworks

| Folder | Framework | Originator | First | Key idea |
|---|---|---|---|---|
| [`FEP/`](FEP/) | **Free Energy Principle** | Karl Friston | 2006 | Self-organising systems minimise an upper bound on sensory surprise |
| [`GWT/`](GWT/) | **Global Workspace Theory / GNW** | Bernard Baars; Dehaene & Changeux | 1988 / 2001 | Consciousness = brain-wide broadcast of selected content |
| [`IIT/`](IIT/) | **Integrated Information Theory** | Giulio Tononi | 2004 | Consciousness *is* irreducible cause-effect power (Φ) |
| [`PP/`](PP/) | **Predictive Processing** | Rao & Ballard; Clark; Hohwy; Seth | 1999 | The brain is a hierarchical prediction machine |
| [`AST/`](AST/) | **Attention Schema Theory** | Michael Graziano | 2011 | Awareness = the brain's internal model of its own attention |

## How the five relate

```
                            ┌──────────────────┐
                            │  Free-Energy     │ ←─ generalised
                            │  Principle (FEP) │     mathematical foundation
                            └────────┬─────────┘
                                     │ instantiated as
                                     ▼
                            ┌──────────────────┐
                            │  Predictive      │ ←─ neural process theory
                            │  Processing (PP) │     (precision-weighted error)
                            └────────┬─────────┘
                                     │
            ┌────────────────────────┼────────────────────────┐
            ▼                        ▼                        ▼
   ┌─────────────────┐     ┌────────────────────┐    ┌──────────────────┐
   │ Global Workspace│     │ Attention Schema   │    │   Integrated     │
   │   (GWT / GNW)   │     │      (AST)         │    │  Information     │
   │                 │     │                    │    │     (IIT)        │
   │ ignition /      │     │ self-model of      │    │ intrinsic Φ;     │
   │ broadcast       │     │ attention →        │    │ structure ≠      │
   │ → access conf.  │     │ subjective report  │    │ broadcast        │
   └─────────────────┘     └────────────────────┘    └──────────────────┘
        ⇡                          ⇡                         ⇡
        └── coexistence — Safron 2020 IWMT; Graziano 2020 "standard model" ──┘
```

- **FEP / PP**: provide the optimisation principle and its neural implementation.
- **GWT**: explains *access* and *report*; tested by P3b, ignition,
  attentional-blink, masking, no-report paradigms.
- **IIT**: explains *structure* and *quality* of experience via Φ; tested by
  PCI, posterior hot-zone, anaesthesia, cerebellar agnosia.
- **AST**: explains *introspective report content* — why we say experience
  feels ineffable — and unifies neatly with GWT / HOT / illusionism.
- **EFC / CEM** *(this repo)*: provides a **thermodynamic ontology** — the
  reflection coefficient `R = κ ⟨τ_ref⟩_E / τ_leak` and its critical
  threshold `R_c ≈ 1/e ≈ 0.37` — that places all four on a common
  energy/information substrate. See:
  - `docs/papers/efc/CEM-Consciousness-Ego-Mirror/`
  - `docs/papers/efc/Closing_the_EFC_Consciousness_Bridge/`
  - `docs/papers/efc/Connecting_Cosmology_Neural_Entropy_and_RLHF_Bridge/`
  - `docs/papers/efc/EFC-C_Consciousness_Field_Resonance/`
  - `docs/papers/efc/EFC-Is-Consciousness-Linked-to-Entropy/`

The CEM paper (A14, 2026-05-09) remains in `docs/papers/efc/CEM-…` for
provenance, and is cross-referenced here.

## The COGITATE adversarial collaboration (2023-2025)

The Templeton-funded *COGITATE* programme (lead PIs Lucia Melloni,
Liad Mudrik, Christof Koch, Stanislas Dehaene) is the largest
pre-registered adversarial test of consciousness theories yet attempted —
specifically pitting **GWT** vs. **IIT** on three crucial predictions
(NCC location, sustained vs. transient activity, inter-areal connectivity
pattern). First definitive results: Cogitate Consortium (2025), *Nature*.
**Headline:** *both* theories had some predictions falsified; neither was
killed. See entries in `GWT/references.bib` and `IIT/references.bib`.

## Personal cognitive notes (NOT for publication)

`/Users/morpheus/Documents/symbiose/cognitive/`

Those notes are author-private working drafts; the public-facing,
canonical material lives here.

## Reading order for newcomers

1. `FEP/README.md` — the meta-framework (skim § 1–3, § 8)
2. `PP/README.md` — the neural-circuit implementation (§ 1, § 5)
3. `GWT/README.md` — what gets *broadcast* (§ 2 empirical signatures)
4. `IIT/README.md` — what is intrinsically *integrated* (§ 1 axioms, § 6 critiques)
5. `AST/README.md` — why we *say* it feels like something (§ 1, § 4)
6. `docs/papers/efc/Closing_the_EFC_Consciousness_Bridge/` — how they line up under EFC

---

*Curated 2026-05-13 (Stage IV groundwork for orchestrator_v2 cognitive
layer). Add new papers under `<theory>/papers/` and update each
`<theory>/index.json#related_packages`.*
