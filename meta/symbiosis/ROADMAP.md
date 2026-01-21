# Symbiosis Runtime — Roadmap

This roadmap outlines the development trajectory of the Symbiosis subsystem within the
Energy-Flow Cosmology (EFC) ecosystem. It establishes clear milestones, dependencies, 
and versioning checkpoints.

---

## 1.0 — Baseline Runtime (DOI-Ready)

**Goal:** Establish a reproducible, fully functional baseline for Symbiosis.

### Requirements
- Unified-API running on Hetzner runtime-master
- Query-API connected to Qdrant + Neo4j
- Graph-RAG-API with validated schema
- Stable .env + config alignment across services
- Neo4j labels validated (Lag 1a lock)
- Qdrant collections validated (Lag 1b lock)
- Conversation logging → Neo4j pipeline working
- `meta/symbiosis` documentation complete (this folder)

### Deliverables
- Figshare DOI dataset: “Symbiosis Runtime v1.0”
- Updated MASTER_GUIDE.md
- Example end-to-end query workflow

---

## 1.1 — Memory Consolidation Layer

### Goals
- Unified schema for Neo4j and Qdrant
- Cross-referencing metadata (concept → chunk → embedding → relationship)
- Automatic ingestion pipeline
- Enhanced JSON-LD alignment

### Deliverables
- `memory_design.md`
- Complete schema.json update

---

## 1.2 — Reflection Layer Integration

### Goals
- Multi-agent reflection (analysis, reasoning, memory)
- Metadata tracking: resonance, context, tags
- Logging enrichment pipeline

### Deliverables
- `reflection_architecture.md`
- Neo4j logging ontology update

---

## 2.0 — Full Symbiotic Runtime

### Goals
- Autonomous knowledge integration
- Self-updating metadata pipeline
- Cross-modal retrieval (text, graph, embeddings)
- Optional GNN embedding layer (PyTorch Geometric)

### Deliverables
- “Symbiosis Runtime v2.0” release
- Published architecture spec paper (EFC meta-series)

---

## Long-Term Vision

Symbiosis will serve as the cognitive and computational backbone for:

- EFC research automation
- large-scale reasoning over graphs, papers and models
- Meta-cognitive reflection loops
- AI-augmented scientific discovery

---

## Versioning

| Version | Status | Notes |
|--------|--------|-------|
| 0.1.0-dev | active | Initial metadata + docs |
| 1.0.0 | planned | First DOI release |
| 2.0.0 | planned | Full reflection + GNN integration |

---
