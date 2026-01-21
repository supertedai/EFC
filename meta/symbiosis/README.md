# Symbiosis Runtime Layer

The *Symbiosis* subsystem is the cognitive and computational backbone that integrates
Energy-Flow Cosmology (EFC) with real-time retrieval, memory, structure, and automated reasoning.
It acts as the execution layer of the EFC ecosystem.

Symbiosis is responsible for:

- API orchestration (unified-api, query-api, graph-rag-api)
- Long-term structured memory (Neo4j knowledge graph)
- Vector memory and embeddings (Qdrant)
- Automated logging and conversation metadata
- Meta-cognitive reflection loops
- Runtime governance (Hetzner as master node)
- Cross-layer consistency and schema alignment

Symbiosis ensures that all components of EFC operate as one coherent cognitive system.

---

## Goals

- Provide a stable runtime environment for all EFC operations.
- Unify graph memory, vector memory, and RAG-assisted reasoning.
- Maintain strict separation of responsibilities: *runtime-master vs code-master*.
- Enable semantic linking across all EFC papers, models, and APIs.
- Support long-term reproducibility through metadata, logs, and schema validation.
- Offer a single point of interaction for external clients and agents.

---

## Architecture Summary

Symbiosis consists of four main layers:

### **1. Memory Layer**
- **Neo4j** (global knowledge graph)
- **Qdrant** (vector memory and embeddings)
- **Metadata stores** (JSON-LD, codemeta)

### **2. API Layer**
- `unified-api`  
- `query-api`  
- `graph-rag-api`

Each API is isolated but connected through the shared semantic schema.

### **3. Reflection & Logging Layer**
- Neo4j logging pipelines  
- Conversation metadata recording  
- RAG retrieval context tracking  
- Multi-agent introspection (planned)  

### **4. Runtime Layer**
- Hetzner: *runtime-master node*  
- GitHub: *code-master*  
- Qdrant Cloud or self-hosted vector stores  
- Neo4j Aura or self-hosted graph  

---

## File Overview

This directory includes:

- `index.md` – High-level description of Symbiosis.
- `index.jsonld` – JSON-LD metadata index.
- `schema.json` – Auto-generated schema and metadata bindings.
- `symbiosis_metadata.jsonld` – Primary metadata descriptor.
- `README.md` – This overview file.

---

## Status

The Symbiosis system is actively being developed.  
A stabilised *baseline* will be published with a DOI on Figshare.

---

## License

See repository root for global license terms.
