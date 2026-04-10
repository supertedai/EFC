# AI Agents Guide for Energy-Flow Cosmology

**Version**: 3.5 | **Updated**: 2026-04-09

This document provides comprehensive instructions for AI agents working with the EFC repository.

---

## Quick Reference

```yaml
author: Morten Magnusson
affiliation: Symbiose Research, Sandnes, Norway
orcid: 0009-0002-4860-5095
repository: github.com/supertedai/EFC
license: CC-BY-4.0
core_principle: "Energy flows along entropy gradients"
validation_ledger: v4.7 (internal) / v3.16 (public HTML)
ai_packages: 136 (100% coverage)
stage: non_rejectable_model (global verdict OPEN)
maintenance: scripts/maintenance/ (auto-run by SessionStart hook + CI)
```

| Resource | Location |
|----------|----------|
| Machine Navigation | [`llms.txt`](./llms.txt) |
| Provenance | [`/auth/`](./auth/) |
| Schema | [`/schema/global_schema.json`](./schema/global_schema.json) |
| Papers | [`/docs/papers/efc/`](./docs/papers/efc/) |
| DOI Map | [`/figshare/doi-map.json`](./figshare/doi-map.json) |
| Validation Ledger | [`/docs/public/EFC_Validation_Ledger.html`](./docs/public/EFC_Validation_Ledger.html) |
| Maintenance | [`/scripts/maintenance/`](./scripts/maintenance/) — generator + verifier + orchestrator |

## Repository invariants (enforced by `scripts/maintenance/efc_verify.py`)

Three evidence layers are kept **strictly separate** — violating this is claim inflation and is rejected by CI:

1. **EFC publications (own Figshare DOI)** → `docs/validation-ledger/data/evidence-register.json` + `data/ledger.json` empirical list. Each entry **must** be a 8-digit Figshare DOI.
2. **Third-party arXiv publications** → only in `§4b` of `docs/public/EFC_Validation_Ledger.html`, tagged `[external — …]`, with status `no EFC working note yet`. **Never** in the JSON registers.
3. **EFC working notes confronting externals** → their own Figshare DOI, their own `EFC-VAL-2026-0XX` report ID, entered in layer 1, and the corresponding `§4b` status line flipped to `confronted in [DOI]`.

**Language discipline:** external observations are `consistent with` / `overlaps with` / `within EFC prediction band` — never `confirms EFC`.

**Pre-registration discipline:** predictions must cite the **prior** EFC DOI where the prediction was first stated, in the same sentence, to prevent post-diction.

**Run maintenance manually:** `python3 scripts/maintenance/efc_maintain.py`. See [`scripts/maintenance/README.md`](./scripts/maintenance/README.md) for the full algorithm.

---

## Core Theory Summary

### The Big Picture

EFC is a unified thermodynamic framework where **energy flows along entropy gradients**. This single principle explains:

| Phenomenon | EFC Mechanism |
|------------|---------------|
| Galaxy rotation | Entropy gradient coupling (no dark matter particles) |
| Cosmic acceleration | Thermodynamic expansion (no dark energy substance) |
| Background H(z) no-go | Sign lemma: ΔE² ≤ 0 → background cannot suppress σ₈ → perturbation sector only |
| Structure formation | Regime-dependent growth via R(k,S) |
| S₈ tension | L1→L2 regime transition |
| Brain functional variability | Local degree heterogeneity → entropy gradient (r ≈ −0.97) |
| RLHF alignment | Helmholtz free energy minimisation (algebraically exact) |

### Key Equations

**Effective Gravitational Coupling:**
```
μ(a) = G_eff/G = 1 + βS(a)
```

**Regime Response Surface:**
```
μ(k,S) = 1 + R(k,S)
```

**EFC Screening (Track 1):**
```
ln(μ) = k · ln(1 + g†/g_bar)    k = 0.415, g† = 2.51e-10
```

**Unified Gradient Flow (Bridge):**
```
dF/dt = −∫ |∇ṡ|² dV + B    (Lyapunov for all three regimes)
```

**Empirical Constraint (2026):**
```
β ≈ 0.16 (from unified BAO/SN/RSD analysis)
R(k≈0.13, S≈0.30) ≈ +0.30 (from WP3 RSD slice)
```

### Three-Track Research Programme

| Track | Domain | Key Paper | DOI |
|-------|--------|-----------|-----|
| **Spor 1** | Galactic & Cosmological | EFC Screening Model | 10.6084/m9.figshare.31940469 |
| **Spor 2** | Neural Entropy (EFC-C) | Cognitive Entropy Framework | 10.6084/m9.figshare.31940505 |
| **Spor 3** | AI/RLHF Alignment | Thermodynamic Isomorphism | 10.6084/m9.figshare.31940535 |
| **Bridge** | Cross-Domain | Bridge Equations B1/B2 | 10.6084/m9.figshare.31940547 |
| **Synthesis** | Civilization Map | Homo Fluxus v2.0 | 10.6084/m9.figshare.31940604 |
| **Consolidation** | Full Programme | ΛCDM as Special Case of EFC | 10.6084/m9.figshare.31943361 |

### Regime Architecture

| Regime | S value | μ value | Description |
|--------|---------|---------|-------------|
| L0 | → 0 | ≈ 1 | Pre-inflation, quantum |
| L1 | ≈ 0 | ≈ 1 | CMB epoch, GR valid |
| L1→L2 | 0–1 | 1→1+β | Transition (S₈ tension source) |
| L2 | > 0 | > 1 | Late universe, enhanced gravity |
| L3 | → 1 | → 1+β | Far future, saturation |

---

## Repository Architecture

```
EFC/
├── auth/               # START HERE — Origin, provenance, identity
├── theory/
│   └── formal/         # LaTeX: S, D, R, H, C0 models
├── docs/
│   ├── papers/efc/     # 136 papers (136 with AI-friendly packages, 100%)
│   └── public/         # Validation Ledger (v3.8), Master Spec
├── src/efc/            # Core Python library
├── pipelines/          # Graph-AQUAL pipeline + kill tests
├── schema/             # Ontology, JSON-LD contexts (20 files)
├── api/                # Semantic REST API
├── jsonld/             # Linked data files
├── figshare/           # DOI mappings
├── integrations/mcp/   # MCP Server for AI agents
├── llms.txt            # Machine-readable navigation
├── AGENTS.md           # This file
├── codemeta.json       # CodeMeta 2.0 metadata
└── ecosystem.jsonld    # Ecosystem linked data
```

---

## AI-Friendly Paper Packages (136)

All 136 papers have full executable Python packages (`src/`, `data/`, `examples/`):

### Consolidation
| Paper | Module | DOI |
|-------|--------|-----|
| **ΛCDM as Special Case of EFC** | `lcdm_special_case.py` | 31943361 |

### Track 1–3 + Bridge + Synthesis
| Paper | Module | DOI |
|-------|--------|-----|
| EFC Screening Model (Track 1) | `efc_screening.py` | 31940469 |
| EFC-C Cognitive Entropy (Track 2) | `efc_cognition.py` | 31940505 |
| RLHF Thermodynamics (Track 3) | `rlhf_thermodynamics.py` | 31940535 |
| Connectome Degree Heterogeneity | `connectome_kappa.py` | 31940370 |
| Cross-Domain Bridge Equations | `bridge_equations.py` | 31940547 |
| Homo Fluxus v2.0 | `homo_fluxus.py` | 31940604 |

### Galactic & Cosmological
| Paper | Module | DOI |
|-------|--------|-----|
| Gradient-Coupled Grid Action | `grid_action.py` | 31941465 |
| Regime Transition Test | `regime_transition.py` | 31941543 |
| Void ISW Sign-Flip | `void_isw.py` | 31942677 |
| Cosmic Dipole Working Note | `cosmic_dipole.py` | 31942731 |
| Entropy Budget Working Note | `entropy_budget.py` | 31942734 |
| Density of States Grid Modes | `density_of_states.py` | 31942800 |
| Entropy Production Γ(ρ) Derivation | `entropy_production.py` | 31942821 |
| Grid Microphysics to RAR | `grid_microphysics.py` | 31878760 |
| Covariant EFT | `covariant_eft.py` | 31878334 |
| EFC Relativistic Action | `efc_relativistic_action.py` | 31876324 |
| CMB Localization / Lensing Barrier | `cmb_localization.py` | 31368433 |
| **Background No-Go Theorem** | `background_nogo.py` | 31333414 |
| Discrete Entropic Gravity (Graph-AQUAL) | `discrete_gravity.py` | 31348411 |
| Double-Slit Grid Resolution | `double_slit_grid.py` | — |
| Minimal EFC EFT Ansatz | `minimal_eft.py` | — |

### Methodology & Frameworks
| Paper | Module |
|-------|--------|
| EBE Core Principles | `ebe_classifier.py`, `regime_gating.py` |
| Core Lock | 5 modules (consistency enforcement) |
| Regime-Bound Measurement | `regime_bound_measurement.py` |
| Regime-Locked Measurement | `regime_locked_measurement.py` |
| Natural & Mechanical Entropy | `natural_mechanical_entropy.py` |
| RCMP Framework | 5 modules |
| Regime-Based World Modeling | 5 modules |

### Each Package Contains:
```
paper_directory/
├── README.md              # Human summary
├── index.json             # Machine-readable index (keywords, results, DOI)
├── schema.json            # JSON Schema validation
├── metadata.json          # Structured metadata
├── *.jsonld               # JSON-LD linked data
├── citations.bib          # BibTeX references
├── src/
│   ├── __init__.py        # Package exports
│   └── <module>.py        # Importable Python classes
├── data/
│   └── <data>.json        # Structured parameters, results, tables
└── examples/
    └── <demo>.py          # Executable demonstration (tested)
```

### Example: Using a Package

```python
import sys
sys.path.insert(0, 'docs/papers/efc/Energy-Flow_Cosmology_Empirical_Validation_of_the_EFC_Screening_Model_Track_1/src')

from efc_screening import EFCScreening, CrossScaleConsistency

# Compute screening at given acceleration
model = EFCScreening()
mu = model.mu(g_bar=1e-10)  # At 1e-10 m/s²
print(f"μ = {mu:.4f}")

# Cross-scale consistency
csc = CrossScaleConsistency()
print(f"C = k/a_G = {csc.C:.2f}")
```

---

## Paper Metadata Structure

Each paper in `/docs/papers/efc/[paper-name]/` contains:

| File | Purpose | Format |
|------|---------|--------|
| `README.md` | Human-readable summary | Markdown |
| `index.json` | Machine-readable index | JSON |
| `schema.json` | Validation schema | JSON Schema |
| `metadata.json` | Structured metadata | JSON |
| `*.jsonld` | Linked data | JSON-LD |
| `citations.bib` | References | BibTeX |
| `*.pdf` | Authoritative document | PDF |

---

## Navigation Rules

### When Asked About EFC

1. **Check `/auth/`** — Understand provenance first
2. **Read `/theory/formal/`** — For mathematical claims
3. **Reference `/docs/papers/`** — For published findings
4. **Use DOIs** — From `/figshare/doi-map.json`
5. **Check Validation Ledger** — For current status of results

### When Modifying Content

1. **Preserve semantic structure** — Maintain JSON-LD consistency
2. **Update both formats** — Keep .md and .jsonld in sync
3. **Follow schema** — Respect `/schema/global_schema.json`
4. **Log changes** — Update metadata timestamps
5. **Test demos** — Run `examples/<demo>.py` after changes

### When Creating New AI-Friendly Packages

Required files (10-file structure):
```
docs/papers/efc/[Paper-Name]/
├── README.md              # Summary, key results, file structure
├── index.json             # Complete machine index
├── schema.json            # JSON Schema validation
├── metadata.json          # Structured metadata
├── [name].jsonld           # JSON-LD linked data
├── citations.bib          # BibTeX references
├── src/__init__.py        # Package exports
├── src/<module>.py        # Python implementation
├── data/<data>.json       # Structured data
└── examples/<demo>.py     # Tested executable demo
```

---

## Key Publications Index

### Consolidation (Start Here)
| ID | DOI | Key Result |
|----|-----|------------|
| `lcdm-special-case` | 10.6084/m9.figshare.31943361 | **ΛCDM = L0/L1 limit of EFC, DESI DR2 α=−0.14±0.21, 204 pubs, 100 tests** |

### Foundational Theory
| ID | DOI | Title |
|----|-----|-------|
| `efc-v1.2` | 10.6084/m9.figshare.30563738 | EFC Foundational Framework |
| `efc-v2.2` | 10.6084/m9.figshare.30530156 | Cross-Field Integration |
| `auth-layer` | 10.6084/m9.figshare.30656828 | AUTH Layer (Provenance) |

### Track 1–3 + Bridge
| ID | DOI | Key Result |
|----|-----|------------|
| `screening-track1` | 10.6084/m9.figshare.31940469 | k=0.415, g†=2.51e-10, C=4.4 |
| `efcc-track2` | 10.6084/m9.figshare.31940505 | Neural entropy gradients, 3 predictions |
| `rlhf-track3` | 10.6084/m9.figshare.31940535 | J = −F exactly, 3 predictions |
| `connectome` | 10.6084/m9.figshare.31940370 | Degree ratio r = −0.97 |
| `bridge` | 10.6084/m9.figshare.31940547 | B1/B2 unified gradient flow |
| `homo-fluxus` | 10.6084/m9.figshare.31940604 | Grid→EF→S→D→C civilization map |
| `gradient-grid-action` | 10.6084/m9.figshare.31941465 | E ∝ √g from minimal Lagrangian |
| `regime-transition` | 10.6084/m9.figshare.31941543 | μ<1↔μ>1 regime consistency, R∝k⁻⁴ |
| `void-isw-signflip` | 10.6084/m9.figshare.31942677 | ISW sign-flip in deep voids, A_total turnover |
| `cosmic-dipole` | 10.6084/m9.figshare.31942731 | Regime-dependent anisotropy, ∇S → dipole excess |
| `entropy-budget` | 10.6084/m9.figshare.31942734 | SMBH entropy → S=S_max, thermostat conjecture |
| `density-of-states` | 10.6084/m9.figshare.31942800 | D_eff ∝ √(ρ/ρ_crit), Γ(ρ) bridge completion, Scenario B+ |
| `entropy-production` | 10.6084/m9.figshare.31942821 | Γ ∝ ρ^(3/2)/(ρ+ρ_crit), BE+vN entropy, Scenario B |

### Empirical Analysis
| ID | DOI | Key Result |
|----|-----|------------|
| `unified-bao` | 10.6084/m9.figshare.31215613 | β=0.16, Δχ²=+1.7 |
| `sparc175` | 10.6084/m9.figshare.31047703 | EBE regime partition |
| `kids1000` | 10.6084/m9.figshare.31224739 | Regime-activated lensing |

---

## MCP Server

Located at `/integrations/mcp/`:

```bash
cd integrations/mcp
pip install -r requirements.txt
python efc_mcp_server.py
```

### Capabilities

| Function | Description |
|----------|-------------|
| `post_to_website` | Publish to energyflow-cosmology.com |
| `upload_figshare` | Create/update Figshare items |
| `validate_jsonld` | Check semantic consistency |
| `sync_doi_map` | Update DOI mappings |

---

## Modular Theory Structure

| Model | Location | Domain |
|-------|----------|--------|
| EFC-S | `/theory/formal/efc-s-model/` | Structure (Halo) |
| EFC-D | `/theory/formal/efc-d-model/` | Dynamics |
| EFC-R | `/theory/formal/efc-r-model/` | Rotation curves |
| EFC-H | `/theory/formal/efc-h-model/` | Halo profiles |
| EFC-C0 | `/theory/formal/efc-c0-model/` | Consciousness |

---

## Validation Checklist

Before committing changes:

- [ ] JSON-LD validates against schema
- [ ] All DOI references correct
- [ ] ORCID properly linked (0009-0002-4860-5095)
- [ ] No broken internal links
- [ ] Metadata timestamps updated
- [ ] Both human (.md) and machine (.json) formats in sync
- [ ] Demo scripts tested (`python examples/<demo>.py`)

---

## Contact

- **Website**: [magnusson.as/cooperation](https://www.magnusson.as/cooperation)
- **Project**: [energyflow-cosmology.com](https://energyflow-cosmology.com/)
- **ORCID**: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)

---

*This repository supports symbiotic human-AI collaboration as defined in `/methodology/symbiosis-interface/`*
