# EFC Papers — Energy-Flow Cosmology

This directory contains all papers, editions, formal specifications, and
supporting documents for the Energy-Flow Cosmology (EFC) framework.  
Each subdirectory includes a complete package with:
- PDF (authoritative)
- Markdown (searchable)
- JSON-LD metadata
- Local schema
- Machine index
- Citation file

The papers are grouped into conceptual, structural, observational, and
versioned categories.  
They form the documented progression of EFC from the first specification
to the unified v2.x architecture.

---

## Core Specifications
- **efc_master/** — Master Specification (canonical reference)  
- **efc_master_v1/** — Archived v1 master  
- **efc_formal_spec/** — Formal mathematical and structural definition  

---

## Versioned Editions
- **EFC-v1.2-Foundational-Framework/**  
- **EFC-v2.1-Complete-Edition/**  
- **EFC-v2.1-Modular-Synthesis/**  
- **EFC-v2.2-Cross-Field-Integration-Summary/**  

---

## Conceptual & Theoretical Papers
These papers develop specific aspects of the EFC model:

- **EFC-Grid-Higgs-Paradigm-Shift/**  
- **EFC-Grid-Model-Entropic-Dynamics/**  
- **EFC-The-Energy-Flow-Interface/**  
- **EFC-Thermodynamic-Bridge-GR-QFT/**  

---

## Foundations of Energy Flow & Entropy
- **EFC-Introduction-to-Energy-Flow-in-Space-Time/**  
- **EFC-Introduction-to-Entropy-in-Cosmic-Evolution/**  
- **EFC-Hypothesis-Interrelation-Energy-Entropy/**  
- **EFC-Hypothesis-Universe-as-Energy-Driven-System/**  
- **EFC-Integrated-Hypothesis-Time-Entropy/**  

---

## Light Speed & Propagation Papers
- **EFC-Light-Speed-as-a-Regulator-of-Energy-Flow-in-the-Universe/**  
- **EFC-Subhypothesis-Light-Speed-Limit/**  
- **EFC-Why-is-Light-Speed-a-Cosmic-Limit/**  

---

## Observational Evidence
- **EFC-Observational-Evidence-for-Energy-Flow/**  
- **EFC-Observational-Evidence-Entropy-Cosmic-Evolution/**  
- **EFC_vs_LCDM_Kill_Test_v6_final/** — Complete kill-test across six probes (DOI 10.6084/m9.figshare.31964847)  
- **Kill-Test v6 Universality_SPARC175/** — Extension of the kill-test to all 175 SPARC galaxies (EFC win rate 60.2 %, 2026-04-11; DOI [10.6084/m9.figshare.31986762](https://doi.org/10.6084/m9.figshare.31986762))  
- **Comprehensive-analysis-of-175-SPARC-galaxies-.../** — Regime-dependent validity analysis (DOI 10.6084/m9.figshare.31045126)  

---

## Structural & Dynamic Questions
- **EFC-What-Happens-at-the-Universes-Extremes/**  
- **EFC-What-is-the-Connection-Between-Energy-Flow-and-the-Now/**  
- **EFC-Unresolved-Questions-and-Challenges-Entropy/**  

---

## Methodology & Workflow
- **EFC-Technical-Documentation-Energy-Flow-in-Space-Time/**  

---

---

## AI-Friendly Package (2026-04-07)

Every subdirectory now ships with a uniform **AI-friendly metadata layer** so
that LLMs and automated agents can ingest, cite, and reproduce the work
without scraping the PDFs:

- `index.json` — minimal stable identity (id, title, author, ORCID, license, track, regimes, file list)
- `metadata.json` — schema-aligned superset (paper, domain, files, primary PDF)
- `ai_manifest.json` — machine-truth view, regenerated on each pass
- `*.jsonld` — schema.org `ScholarlyArticle` JSON-LD record
- `README.md` — human-readable summary with file inventory

A directory-level catalogue lives in `ai_friendly_index.json` (138 packages,
auto-generated). Hand-curated reference packages with full reproducer code:

- `WP4_BOSS_transfer_validation/` — DESI DR2 → BOSS DR12 cross-survey transfer (Δχ² = −7.77)
- `Multi_epoch_Growth_Rate_Test_of_EFC/` — 14-point fσ8 multi-epoch test (EFC-VAL-2026-003)
- `EFC_vs_LCDM_Kill_Test_v6_final/` — Six-probe kill-test with full cobaya pipeline
- `Kill-Test v6 Universality_SPARC175/` — Kill-test extended to all 175 SPARC galaxies (2026-04-11, DOI [10.6084/m9.figshare.31986762](https://doi.org/10.6084/m9.figshare.31986762))

These follow the same conventions as the auto-generated packages but add
`src/`, `data/`, `examples/`, `schema.json`, and `citations.bib`.

---

## Purpose of This Directory
This collection provides:
- a stable scientific record  
- version-controlled theory development  
- references for external researchers  
- machine-readable metadata for LLMs and automated systems  
- complete provenance for the evolution of the EFC framework  

All subdirectories follow the same internal structure for consistency,
clarity, and automated semantic indexing.

