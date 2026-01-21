# Symbiosis Runtime Architecture

The Symbiosis subsystem forms the core runtime environment of the EFC ecosystem.  
It connects the conceptual layer (theory), the memory layer (Neo4j + Qdrant), and the 
interaction layer (APIs and agents).

---

## Architectural Overview

Symbiosis is composed of four major layers:

1. **Memory Layer**  
2. **API Layer**  
3. **Reflection & Logging Layer**  
4. **Runtime Layer**

---

## 1. Memory Layer

### 1.1 Neo4j — Structured Knowledge Graph  
- Stores concepts, documents, sections, chunks  
- Captures semantic and causal relationships  
- Supports reasoning across the EFC ontology  
- Stores long-term logging and conversation metadata

### 1.2 Qdrant — Vector Memory  
- Embedding storage for text, chunks, sections  
- Metadata linking to Neo4j nodes  
- RAG search (semantic retrieval)  
- Collection alignment with schema.json

---

## 2. API Layer

### unified-api
- Single entry point for external clients  
- Routes requests to Query-API or Graph-RAG-API  
- Handles health checks, authentication, cross-service logic

### query-api
- Direct Qdrant and Neo4j interactions  
- Embedding generation (OpenAI or local models)  
- Semantic search, chunk retrieval, metadata enrichment

### graph-rag-api
- Graph-based reasoning  
- Hybrid search (vector + graph)  
- Multi-hop traversal over Neo4j  
- Context assembly for LLMs

---

## 3. Reflection & Logging Layer

### Logging Pipeline
- Any LLM (AnythingLLM, ChatGPT, local models) → proxy → Neo4j  
- Each message enriched with metadata:
  - tags
  - resonance score
  - context
  - API used
  - latency
  - agent name

### Reflection Layer (planned)
- Multi-agent analysis  
- Consistency checks across memory  
- Self-updating insights  
- Symbiosis meta-evaluation

---

## 4. Runtime Layer

### Hetzner (runtime-master)
- Hosts all active services  
- Runs docker-compose stack  
- Single source of truth for execution

### GitHub (code-master)
- Holds definitions, metadata, scripts  
- Serves as version-controlled blueprint  
- Updated through structured workflow

---

## Integration Diagram (text-based)

Clients → unified-api → query-api → Qdrant
→ graph-rag-api → Neo4j
→ Logging Proxy → Neo4j (logs)


---

## Principles

- **Hetzner = runtime-master**  
- **GitHub = code-master**  
- **Memory is shared, schema-validated, and consistent**  
- **All services speak through the same semantic layer (JSON-LD + schema)**  

---

