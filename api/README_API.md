---
title: 📡 **Energy-Flow Cosmology — API v1**
type: foundational
date: '2026-01-04'
layer: API
tags:
- api
- auth
- cognition
- cosmology
- efc
- energy
- flow
- framework
source_path: api/README_API.md
---

# 📡 **Energy-Flow Cosmology — API v1**

The **EFC API v1** is the machine-readable interface for accessing all conceptual, methodological, and semantic components of Energy-Flow Cosmology (EFC).
It is designed for:

* automated processing
* semantic search
* ontology-driven exploration
* LLM integration
* metadata synchronization with Figshare

All files in this directory are **auto-generated** and **kept in sync with Figshare DOIs** through GitHub Actions.

---

# 📁 Directory Overview

```
api/v1/
├── concept/                        # Individual concept entries
│   ├── applied-energy-flow...json
│   ├── cem-cosmos...json
│   ├── energy-flow-cosmology-v21...json
│   └── ...
│
├── methodology.json                # Methodological definitions
├── meta.json                       # Metadata, DOIs, provenance
├── index.json                      # API index (auto-generated)
├── concept-index.json              # Concept index (auto-generated)
├── api_index.json                  # Internal index (legacy support)
└── README_API.md                   # Documentation for API v1
```

---

# 🧠 Purpose of API v1

The EFC API provides a **structured, machine-readable representation** of the full Energy-Flow Cosmology knowledge system.

It covers:

* **Concept definitions** (theoretical + semantic)
* **Cross-field relationships**
* **Methodology and reasoning structure**
* **Model parameter definitions**
* **Metadata (DOI, provenance, authorship)**
* **Release indexing and content mapping**

This allows external tools, dashboards, or AI agents to query EFC without parsing PDFs or TeX files.

---

# 🔄 Auto-Sync With Figshare

The API is automatically synchronized with Figshare:

* new DOIs
* updated metadata
* concept updates
* structure changes
* formal specifications

Triggered by GitHub Actions:

```
fetch_figshare_full.py
update_efc_api.py
export_api.yml
```

This ensures that the API always reflects the *most recent published scientific state* of the EFC system.

---

# 🧩 Core JSON Files

### **Concepts** (moved 2026-09-06)

The concept layer has one source: `docs/concepts.jsonld` — a SKOS registry
of the five core concepts (EFC, ∇S, GHF, HME, IMX) against the `efc:`
vocabulary. `schema/concepts.json` (schema.org DefinedTermSet) and
`api/concept-index.json` (ItemList) are generated views
(`scripts/maintenance/efc_concepts.py`, checked in CI as C11).
`api/v1/concepts.json` and `api/v1/terms.json` were dead copies and are gone.

### **`concept-index.json`**

Lightweight index of all concept keys.
Useful for search and downstream agents.

### **`methodology.json`**

Describes the reasoning structure and scientific method behind EFC.

### **`meta.json`**

Links concepts to DOIs, Figshare entries, and published versions.

### **`index.json` / `api_index.json`**

Global API map for backward compatibility.

---

# 🧬 Concept Entries (`/concept/`)

The `/concept/` folder contains individual concept files.
Each file corresponds to a **single DOI or formal scientific release**.

Examples:

* `energy-flow-cosmology-v21-unified-thermodynamic-framework.json`
* `cem-cosmos-a-field-theoretic-model-of-consciousness.json`
* `applied-energy-flow-cosmology-cross-field-integration.json`

Each entry includes:

* concept summary
* definitions
* cross-links
* semantic relations
* DOI metadata
* publication history
* parameters and variable definitions (if relevant)

---

# 🧠 Semantic Purpose

The API v1 layer is the **glue** between:

* the formal mathematical theory
* the semantic knowledge graph
* computational models
* external platforms (websites, dashboards, agents, LLMs)

It enables:

* deterministic indexing
* reproducible scientific referencing
* schema mapping
* domain-level reasoning for AI systems
* meta-reflective structures (cognition, symbiosis, reflection)

---

# 🚀 Usage

Query the API using any JSON-aware tool:

```bash
jq '."@graph"[] | select(."@type"=="skos:Concept") | ."skos:prefLabel"."@value"' docs/concepts.jsonld
```

or in Python:

```python
import json

with open("docs/concepts.jsonld") as f:
    concepts = json.load(f)
print(concepts.keys())
```

---

# 🧱 Stability Guarantee

API v1 is designed to be:

* backwards-compatible
* deterministic
* automatically regenerated
* traceable to all scientific releases
* linked to DOIs

All updates are tracked through GitHub Actions and Figshare metadata.

---

# 📄 Summary

The EFC API v1 is the **canonical machine interface** to Energy-Flow Cosmology:

* semantic
* structured
* reproducible
* publication-aware
* agent-friendly

It bridges the theory, metadata, computational models, and external ecosystem.

---
