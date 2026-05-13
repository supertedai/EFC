# Meta Layer

Curated theoretical-reference layer for the **three cross-layer
meta-principles** that bind the EFC framework together. These principles
apply *across* cosmos, cognitive, and medicine layers — they are not
domain-specific theories but shared scaffolding.

Layer routes to Neo4j `knowledge_domain='meta'` and Qdrant `efc`
collection (meta shares the cosmos collection per `LAYER_PATH_MAP['meta']`
in `tools/orchestrator_v2.py`).

Each subdirectory holds:

| File | Purpose |
|---|---|
| `README.md` | Long-form reference: principle, predictions, criticisms, EFC bridge |
| `index.json` | Machine-readable metadata (schema.org / EFC index format) |
| `references.bib` | BibTeX of canonical + critical references |
| `papers/` (Autopoiesis only) | Downloaded open-access full-texts |

## Meta-principles

| Folder | Principle | One-line claim | Source EFC paper |
|---|---|---|---|
| [`HomoFluxus/`](HomoFluxus/) | **Homo Fluxus** | Human (and any life) = far-from-equilibrium energy-flow process; identity is a temporal invariant of a dissipative structure | v1: DOI [32099389](https://doi.org/10.6084/m9.figshare.32099389); v2: DOI [31940604](https://doi.org/10.6084/m9.figshare.31940604) |
| [`Proxy/`](Proxy/) | **Proxy / Regime-Bound Measurement** | Every observable substituted for a target quantity is regime-bound; measurement is cartography, not verdict | DOI [31564123](https://doi.org/10.6084/m9.figshare.31564123) |
| [`Autopoiesis/`](Autopoiesis/) | **Autopoiesis** | Life is a network of processes that continually produces its own components and boundary — operationally closed, thermodynamically open (Maturana & Varela 1972, 1980) | (External, brought in as meta-reference) |

## How the three relate

```
                ┌──────────────────────────┐
                │     HOMO FLUXUS          │
                │   (thermodynamic side)   │
                │                          │
                │ R = κ ⟨τ_ref⟩_E / τ_leak │   ← far-from-equilibrium
                │ R > R_c ≈ 1/e  ≈ 0.37    │     flow
                └─────────────┬────────────┘
                              │
        complementary description of the same phenomenon
                              │
                ┌─────────────▼────────────┐
                │     AUTOPOIESIS          │
                │  (organisational side)   │
                │                          │
                │ self-producing network;  │   ← operational closure
                │ Varela's six criteria;   │
                │ enactive cognition       │
                └─────────────┬────────────┘
                              │
                  what makes the observables valid?
                              │
                ┌─────────────▼────────────┐
                │        PROXY             │
                │ (measurement / validity) │
                │                          │
                │ regime · proxy · placement│   ← cartographic
                │ · episenter · compression│     measurement
                └──────────────────────────┘
```

- **HomoFluxus** answers *"what kind of object is a living/cognitive thing
  in EFC?"* — a flow pattern.
- **Autopoiesis** answers *"what gives that flow pattern its own
  identity?"* — operational closure.
- **Proxy** answers *"how do we observe such systems without breaking the
  closure or stepping outside the regime?"* — regime-bound measurement.

Each is necessary; none is sufficient alone.

## Cross-layer reach

| Where they show up | HomoFluxus | Proxy | Autopoiesis |
|---|:---:|:---:|:---:|
| Cosmos (`efc/`) | ✓ (R-threshold, κ scaling) | ✓ (WP3/R(k,S), proxy substitution) | – |
| Cognitive (`cognitive/`) | ✓ (FEP/IIT/PP/GWT/AST integration) | ✓ (PCI/Φ-proxy, COGITATE) | ✓ (FEP Markov blanket; enactive PP) |
| Medicine | ✓ (allostatic load, R-disease) | ✓ (surrogate endpoints, biomarkers) | ✓ (definition of life/disease boundary) |
| AI alignment | ✓ (RLHF-as-entropy-minimisation) | ✓ (benchmark validity) | ✓ (artificial-life autopoiesis) |
| Society | ✓ (Homo Fluxus v2.0 civilisation map) | – | ✓ (Luhmann social autopoiesis) |

## Related layers

- `docs/papers/cognitive/` — five consciousness theories with EFC bridges
- `docs/papers/efc/` — cosmology + EFC-internal source papers
- AGI repo: `meta/meta-architecture/`, `meta/meta-process/` — also
  meta-layer per A14 (tag in place). This directory is for *new
  greenfield papers + publications*, not the AGI orchestrator's
  meta-process docs.

## Personal meta notes (NOT for publication)

`/Users/morpheus/Documents/symbiose/meta/`

Author-private working drafts; the public-facing canonical material
lives here.

## Reading order for newcomers

1. `HomoFluxus/README.md` — thermodynamic substrate (§ 1, § 3)
2. `Autopoiesis/README.md` — organisational closure (§ 1, § 6)
3. `Proxy/README.md` — measurement validity (§ 1, § 4)
4. `docs/papers/efc/Closing_the_EFC_Consciousness_Bridge/` — how the three lock together

---

*Curated 2026-05-13 (Stage IV groundwork for orchestrator_v2 meta
layer). Add new papers under `<principle>/papers/` and update each
`<principle>/index.json#cross_layer_bridges`.*
