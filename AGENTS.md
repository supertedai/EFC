# AI Agents Guide for Energy-Flow Cosmology

**Version**: 3.6 | **Updated**: 2026-04-12

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
validation_ledger_public: v3.18
validation_ledger_internal: v4.6
ai_packages: 169 (100% coverage)
stage: non_rejectable_model (global verdict OPEN)
maintenance: scripts/maintenance/ (auto-run by SessionStart hook + CI)
pipelines: pipelines/efc/native_v2_graph/ (AQUAL) + pipelines/efc/euclid_dr1/ (Euclid DR1)
```

| Resource | Location |
|----------|----------|
| Machine Navigation | [`llms.txt`](./llms.txt) |
| Provenance | [`/auth/`](./auth/) |
| Schema | [`/schema/global_schema.json`](./schema/global_schema.json) |
| Vocabulary (`efc:`) | [`/docs/ontology.jsonld`](./docs/ontology.jsonld) / [`ontology.html`](./docs/ontology.html) — one namespace, `https://supertedai.github.io/EFC/ontology#`, generated from use by `scripts/maintenance/efc_ontology.py` and checked in CI (C9) |
| Concepts | [`/docs/concepts.jsonld`](./docs/concepts.jsonld) — SKOS registry of the five core concepts (EFC, ∇S, GHF, HME, IMX) against the `efc:` namespace; `schema/concepts.json` and `api/concept-index.json` are generated views (C11, `scripts/maintenance/efc_concepts.py`) |
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

## Automated Maintenance Protocol (for Claude Code)

The SessionStart hook runs `efc_maintain.py` + `efc_drift_detector.py` on every session.
**Claude MUST act on the output before doing anything else.**

### Step 1: Fix drift (if any)

The drift detector reports stale counts, versions, and missing DOIs.
Fix every item it reports — update the number/version in the affected file.

### Step 2: Scan for unprocessed papers

After maintenance, Claude MUST check for papers that have a DOI but are
not yet registered in the public pages. Run this check:

```
For each paper directory in docs/papers/efc/:
  1. Read index.json — does it have a "doi" field?
  2. If yes: is that DOI mentioned in EFC_Validation_Ledger.html?
  3. If no: this paper needs processing.
```

### Step 3: Process each unregistered paper

For each paper with a DOI that is NOT in the Ledger, Claude MUST:

1. **Read the paper** — Read the PDF (or README.md + index.json if PDF not readable).
   Extract: title, key results, what it tests, which kill criteria it relates to,
   whether it is a new test / sealed prediction / methodology / theory paper.

2. **Classify relevance** — Determine which public pages need updating:
   - Does it contain a **new empirical test**? → Ledger entry (with tier T1/T2/T3)
   - Does it relate to **kill criteria KC1-KC5**? → Roadmap update
   - Does it contain a **sealed prediction**? → White Paper + Roadmap
   - Does it change **pipeline status**? → Roadmap pipeline table
   - Is it a **significant result**? → README NEW banner + Elevator Pitch

3. **Decide the Ledger entry** — Determine:
   - Which row it belongs in (new row, or update existing row?)
   - Status: PASS / Planned / Completed / SEALED / Awaiting
   - Tier: T1 (blind/pre-registered), T2 (post-diction), T3 (sealed/awaiting)
   - Which regime columns to check (L0, L1, L2, L3)
   - Whether any kill criteria can be ticked

4. **Update ALL relevant pages** — Every page that should mention this DOI:
   - `EFC_Validation_Ledger.html` — new or updated row with DOI link
   - `EFC_Stage-IV_Data_Roadmap.html` — update pipeline status / kill criteria
   - `EFC_White_Paper_Series.html` — update sealed count / prediction block
   - `EFC_Elevator_Pitch.html` — update summary if significant
   - `EFC_Changelog.html` — add versioned entry (increment v3.XX)
   - `README.md` — add NEW banner if significant; update counts
   - `AGENTS.md` — update counts if changed
   - `docs/validation-ledger/data/evidence-register.json` — add DOI to empirical list
   - `docs/validation-ledger/data/ledger.json` — mirror the evidence register

5. **Propagate DOI** — Run `python3 scripts/maintenance/efc_sync_dois.py --apply`
   to ensure DOI is in all package files.

6. **Validate** — Run `python3 scripts/maintenance/efc_maintain.py` and
   `python3 scripts/maintenance/efc_drift_detector.py`. Both must be clean.

7. **Commit and push** — Single commit with descriptive message listing what
   was updated and why. Push to main.

### What counts as "relevant" for each page

| Page | Include paper if... |
|------|-------------------|
| **Validation Ledger** | It contains ANY empirical test, comparison, or pre-registered prediction |
| **Stage-IV Roadmap** | It relates to KC1-KC5, Euclid/DESI/Rubin, or pipeline readiness |
| **White Paper Series** | It contains a sealed prediction or changes the falsifiability count |
| **Elevator Pitch** | It is a top-3 most significant result (rare — most papers don't go here) |
| **Changelog** | ALL papers with DOI get a Changelog entry — no exceptions |
| **README NEW banner** | Only if it's a major milestone (new pipeline, new kill-test, sealed prediction) |

### Decision rules for Ledger tiers

| Tier | Criteria | Example |
|------|----------|---------|
| T1 | Blind prediction registered BEFORE data | DESI DR2 blind prediction |
| T2 | Post-diction analysis, not pre-registered | KiDS-1000 Case A lensing |
| T3 | Prediction sealed, awaiting future data | Euclid DR1 benchmark |

### Decision rules for kill criteria

- KC1 (P(k) full-shape): only tick if full-shape likelihood run with EFC growth
- KC2 (fσ₈): only tick if growth rate measured and compared to EFC μ prediction
- KC3 (S₈): only tick if weak lensing S₈ compared to EFC Σ prediction
- KC4 (η slip): only tick if gravitational slip η measured or E_G computed
- KC5 (w(z)): only tick if dynamical DE equation of state constrained

### Classification rules: NOT everything goes in the Ledger

Many papers are theory, methodology, meta-architecture, or philosophy.
These do NOT get Ledger entries. Only add to the Ledger if the paper:

- Contains a **quantitative empirical test** against observational data
- Contains a **sealed prediction** with falsification criteria
- Contains a **pipeline result** (e.g. Boltzmann output, MCMC posterior)
- Contains a **cross-validation** (e.g. parameter transfer between surveys)

Papers that are theory derivations, frameworks, or methodology get
a Changelog entry ONLY (no Ledger row). This keeps the Ledger clean.

### Quality gate: GPT council validation

For Ledger entries, before committing Claude SHOULD verify the classification
is correct by checking:
1. Does the paper actually contain the claimed test? (read the PDF/README)
2. Is the tier assignment correct? (T1 requires prior DOI with prediction)
3. Is the status assignment correct? (PASS requires specific numerical agreement)
4. Are the regime columns correct? (only tick regimes actually tested)

The weekly GPT-5 council audit (efc-ai-audit.yml) provides an independent
cross-check. If the council flags an issue, Claude must investigate and fix.

### Automatic Gap Analysis Protocol (every session)

Claude MUST update the Gap Analysis at every session, not just monthly.
The protocol is:

1. **Read the weekly scan report** — `docs/weekly_scan_report.json`
   contains all flagged items from `efc_weekly_scan.py` (papers, pipeline
   runs, commits, validation drift, theory files, KC changes).

2. **Query the symbiosis** — Use `get_research_status` (MCP) to get current:
   - MCMC inference status (α-signal, robustness)
   - Knowledge gaps (open, critical, stalled)
   - Validation tests (passed/failed/planned)
   - GRAV pipeline (kill-test results)
   - Sealed predictions status
   - Learning loop connectivity

3. **Search the web** — Use WebSearch for:
   - New arXiv papers on entropic gravity, modified gravity, EFC competitors
   - Survey timeline updates (Euclid, DESI, Rubin, SO)
   - New data releases relevant to KC1-KC5
   - Deadline changes for pre-registration windows

4. **Update all 7 public pages** — Based on findings:
   - `EFC_Gap_Analysis.html` — update every section (landscape, KC readiness,
     theory gaps, data timeline, priority actions, competitors, symbiosis status)
   - `EFC_Validation_Ledger.html` — new test rows + evidence register entries
   - `EFC_Stage-IV_Data_Roadmap.html` — update pipeline status, dates, §12
   - `EFC_White_Paper_Series.html` — update sealed count if changed
   - `EFC_Elevator_Pitch.html` — update summary if significant
   - `EFC_Changelog.html` — add versioned entry (increment v3.XX)
   - `README.md` — update counts and NEW banners

5. **Process every flagged item** from the scan report:
   - Unprocessed papers → classify and register (Ledger or Changelog)
   - Pipeline runs → document in Changelog if significant
   - Validation drift → fix JSON/HTML sync
   - New theory files → add to Changelog if they represent new work
   - KC changes → update Roadmap pipeline status

6. **Commit, push, let GPT-5 council validate** — The CI workflow
   (`efc-ai-audit.yml`) runs the GPT-5 council on every push to main.
   The council independently cross-checks all public pages for:
   - Consistency (counts, versions, DOIs match across pages)
   - Language discipline (no "confirms EFC")
   - Pre-registration integrity (prior DOI cited)
   - Evidence layer separation (no external papers in evidence register)
   If the council flags issues, Claude must fix them in the same session.

### Quality gate: GPT-5 council audit

The weekly GPT-5 council audit (efc-ai-audit.yml) runs:
- Every push to main (when public pages change)
- Wednesday 06:30 UTC (consistency audit)
- Monday 07:00 UTC (full scan + classification)

The council uses OpenAI GPT-5 to independently verify:
1. All test counts match across HTML, JSON, and AGENTS.md
2. All DOIs in evidence register are real and correctly linked
3. Language rules are followed (no "confirms", "proves", etc.)
4. Pre-registration citations are correct (prior DOI exists)
5. Tier assignments are justified (T1 requires prior prediction DOI)

Claude MUST check the audit results (GitHub Actions artifacts) and fix
any findings before proceeding with other work.

### Public pages that must stay in sync (13 pages)

| Page | What it tracks |
|------|---------------|
| `docs/public/EFC_Validation_Ledger.html` | Every test, every DOI, tier status |
| `docs/public/EFC_Evaluation_Ledger.html` | Pre/post-Stage-IV evaluation rubric for each KC |
| `docs/public/EFC_Likelihood_Ledger.html` | Per-likelihood declared / runnable / executed / frozen status |
| `docs/public/EFC_Model_Comparison.html` | Side-by-side EFC ↔ ΛCDM ↔ MOND comparison |
| `docs/public/EFC_Master_v1.1.html` | Standalone master-spec snapshot (mirrors `efc_formal_spec` DOI 30630500) |
| `docs/public/EFC_Stage-IV_Data_Roadmap.html` | Kill criteria, pipeline status, timeline |
| `docs/public/EFC_White_Paper_Series.html` | Sealed predictions, falsifiability count |
| `docs/public/EFC_Elevator_Pitch.html` | Plain-English summary, pipeline status |
| `docs/public/EFC_Gap_Analysis.html` | Gaps, deadlines, competitors, symbiosis status |
| `docs/public/EFC_External_Research_Ledger.html` | §4b external arXiv work confronted with EFC notes |
| `docs/public/EFC_Predictions.html` | Sealed predictions with cryptographic hashes |
| `docs/public/EFC_Atlas.html` | 43 frameworks × 35 phenomena cross-comparison |
| `docs/public/EFC_Changelog.html` | Every structural/empirical update, versioned |
| `README.md` | Paper count, test count, NEW banners, tree structure |

### Language rules (never violate)

- NEVER write "confirms EFC", "proves EFC", "validates EFC"
- Use: "consistent with", "within prediction band", "passes test"
- External papers: "overlaps with EFC prediction", not "confirms"
- Always cite the prior EFC DOI where a prediction was first stated
- Pre-registration: always cite the PRIOR DOI where prediction was first stated

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
│   ├── papers/efc/     # 169 papers (169 with AI-friendly packages, 100%) + _archived/
│   └── public/         # Validation Ledger (v3.18), White Paper, Roadmap, Elevator Pitch, Changelog
├── src/efc/            # Core Python library
├── pipelines/          # Graph-AQUAL + Euclid DR1 pipelines
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

## AI-Friendly Paper Packages (140)

All 169 active papers have full AI-friendly packages (10/10 standard: `src/`, `data/`, `examples/`, `CITATION.cff`, `LICENSE`, `citations.bib`, `schema.json`); two superseded packages live under `docs/papers/efc/_archived/` for provenance:

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
| **Scale-Localised Modified Gravity** | `scale_localised_gravity.py` | 31985313 |
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
| `lcdm-special-case` | 10.6084/m9.figshare.31943361 | **ΛCDM = L0/L1 limit of EFC, DESI DR2 α=−0.14±0.21, 204 pubs, 102 tests** |

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
| `kids1000` | 10.6084/m9.figshare.31271917 | Regime-activated lensing |

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
