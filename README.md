# Energy-Flow Cosmology (EFC)

> **Core Principle**: Energy flows along entropy gradients — this generates spacetime, structure, and awareness.

[![DOI](https://img.shields.io/badge/DOI-10.6084%2Fm9.figshare.30656828-blue)](https://doi.org/10.6084/m9.figshare.30656828)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0002--4860--5095-green)](https://orcid.org/0009-0002-4860-5095)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

---

## Quick Reference (AI + Human)

| Key | Value |
|-----|-------|
| **Author** | Morten Magnusson |
| **ORCID** | [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095) |
| **Primary DOI** | [10.6084/m9.figshare.30656828](https://doi.org/10.6084/m9.figshare.30656828) |
| **Repository** | [github.com/supertedai/EFC](https://github.com/supertedai/EFC) |
| **Theory Site** | [energyflow-cosmology.com](https://energyflow-cosmology.com/) |
| **AI Navigation** | [`llms.txt`](./llms.txt) / [`AGENTS.md`](./AGENTS.md) |

---

## What EFC Explains

| Phenomenon | Standard Model | EFC Interpretation |
|------------|----------------|-------------------|
| Galaxy rotation curves | Dark matter particles | Entropy gradient coupling |
| Cosmic acceleration | Dark energy (Λ) | Thermodynamic expansion |
| Structure formation | ΛCDM + inflation | Regime-dependent growth |
| S₈ tension | Systematic error? | L1→L2 regime transition |

---

## Core Equations

### Effective Gravitational Coupling
```
μ(a) = G_eff/G = 1 + βS(a)
```
- **β** = coupling constant (~0.16 from unified analysis)
- **S(a)** = entropy field (0 at CMB → 1 at late times)

### Regime Response Surface
```
μ(k,S) = 1 + R(k,S)
```
- **k** = wavenumber (scale)
- **S** = structural maturity
- **R(k,S)** = single global response surface for all probes

### EFC Field Equation
```
G_μν = 8πG(T_μν + T^(Ef)_μν) + Λ_eff g_μν
```

---

## Regime Architecture (L0–L3)

| Regime | Epoch | S value | Physics |
|--------|-------|---------|---------|
| **L0** | Pre-inflation | S → 0 | Quantum-dominated |
| **L1** | CMB (z~1100) | S ≈ 0 | Linear, GR valid (μ≈1) |
| **L1→L2** | Transition | 0 < S < 1 | Regime change |
| **L2** | Late universe | S > 0 | Enhanced gravity (μ>1) |
| **L3** | Far future | S → 1 | Structure saturation |

---

## Latest Empirical Results

### Unified BAO/SN/RSD Analysis
| Model | χ² (total) | Verdict |
|-------|------------|---------|
| ΛCDM | 49.4 | Baseline |
| EFC (β=0.16) | 51.1 | Compatible (Δχ²=+1.7) |

**Key finding**: Same S(a) describes geometry AND growth without internal tension.

### WP3: R(k,S) Empirical Slice
```
R(k ≈ 0.13 h/Mpc, S ≈ 0.30) ≈ +0.30
```
First coordinate on the regime response surface (ΛCDM preferred by AIC, but non-zero response allowed).

---

## Key Publications

### Foundational
| Paper | DOI | Status |
|-------|-----|--------|
| EFC v1.2: Foundational Framework | [10.6084/m9.figshare.30563738](https://doi.org/10.6084/m9.figshare.30563738) | Published |
| EFC v2.2: Cross-Field Integration | [10.6084/m9.figshare.30530156](https://doi.org/10.6084/m9.figshare.30530156) | Published |
| AUTH Layer (Provenance) | [10.6084/m9.figshare.30656828](https://doi.org/10.6084/m9.figshare.30656828) | Published |

### Empirical Analysis
| Paper | DOI | Key Result |
|-------|-----|------------|
| R(k,S) Response Surface | [10.6084/m9.figshare.31211437](https://doi.org/10.6084/m9.figshare.31211437) | Theoretical framework |
| WP3: First Empirical Slice | [10.6084/m9.figshare.31215259](https://doi.org/10.6084/m9.figshare.31215259) | R≈+0.30 at (k,S) |
| Unified BAO/SN/RSD | [10.6084/m9.figshare.31215613](https://doi.org/10.6084/m9.figshare.31215613) | β=0.16, Δχ²=+1.7 |

### Human-AI Collaboration
| Paper | DOI |
|-------|-----|
| Symbiosis Architecture | [10.6084/m9.figshare.30773684](https://doi.org/10.6084/m9.figshare.30773684) |

---

## Repository Structure

```
EFC/
├── auth/               # Origin & provenance (START HERE)
├── theory/             # Formal mathematics
│   └── formal/         # S, D, R, H, C0 models (LaTeX)
├── docs/
│   └── papers/efc/     # All papers with AI-optimized metadata
├── schema/             # Ontology & JSON-LD contexts
├── api/                # Semantic REST API
├── jsonld/             # Linked data files
├── figshare/           # DOI mappings
├── integrations/
│   └── mcp/            # AI Agent MCP Server
├── llms.txt            # AI navigation (machine-readable)
└── AGENTS.md           # AI integration guide
```

---

## For AI Agents

### Entry Points
1. **[`llms.txt`](./llms.txt)** — Machine-readable navigation
2. **[`AGENTS.md`](./AGENTS.md)** — Detailed integration guide
3. **[`/auth/`](./auth/)** — Provenance and identity
4. **[`/schema/global_schema.json`](./schema/global_schema.json)** — Domain definitions

### MCP Server
```bash
cd integrations/mcp && pip install -r requirements.txt && python efc_mcp_server.py
```

### Paper Metadata Structure
Each paper in `/docs/papers/efc/` contains:
- `README.md` — Human-readable summary
- `index.json` — Machine-readable index
- `schema.json` — Validation schema
- `*.jsonld` — Linked data
- `citations.bib` — BibTeX

---

## Modular Theory

| Model | Domain | Key Equation |
|-------|--------|--------------|
| **EFC-S** | Structure | Halo thermodynamic boundaries |
| **EFC-D** | Dynamics | Energy flow field equations |
| **EFC-R** | Rotation | μ(r) rotation curve modification |
| **EFC-H** | Halos | Entropy halo profiles |
| **EFC-C0** | Cognition | Consciousness-entropy coupling |

---

## Ecosystem

| Surface | Purpose | URL |
|---------|---------|-----|
| GitHub | Technical implementation | [github.com/supertedai/EFC](https://github.com/supertedai/EFC) |
| Figshare | Peer-reviewed DOIs | [figshare.com/authors/Morten_Magnusson](https://figshare.com/authors/Morten_Magnusson/18515981) |
| Theory Site | Public documentation | [energyflow-cosmology.com](https://energyflow-cosmology.com/) |
| Personal | Hypothesis platform | [magnusson.as](https://www.magnusson.as/) |
| ORCID | Academic identity | [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095) |

---

## Citation

```bibtex
@misc{magnusson2025efc,
  author       = {Magnusson, Morten},
  title        = {Energy-Flow Cosmology (EFC)},
  year         = {2025},
  doi          = {10.6084/m9.figshare.30656828},
  url          = {https://github.com/supertedai/EFC},
  note         = {ORCID: 0009-0002-4860-5095}
}
```

---

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — Morten Magnusson

---

*"Energy flows along entropy gradients — this is the fundamental dynamic of the Universe."*
