# Reflection Index

The Reflection Index defines the structural map of all reflection domains inside the meta-architecture.  
It lists what can be reflected upon, how reflection domains are organised, and which surfaces are accessible to reflection.

This index is not the reflective protocol and not self-evaluation.  
It is a **structural registry** of all reflective surfaces, levels, and categories.

---

## 1. Purpose
- map all domains where reflection is valid  
- define reflection levels (local → global)  
- catalogue structural reflection types  
- identify reflection-eligible surfaces  
- provide a unified index for reflection-based operations  

---

## 2. Scope
The Reflection Index covers:

- reflection domains  
- reflection types  
- reflection levels  
- reflection surfaces  
- cross-domain relationships  
- boundaries of reflectability  

Reflection Index does not:
- execute reflection  
- analyse content  
- modify architecture  

---

## 3. Included Files

- `index.jsonld`  
- `reflection-map.md`  
- `reflection-types.md`  
- `reflection-surfaces.md`  
- `reflection-levels.md`  
- `examples.md`  

---

## 4. Mermaid Overview

```mermaid
flowchart TD

A[Reflection Domains] --> B[Reflection Types]
A --> C[Reflection Surfaces]
A --> D[Reflection Levels]

B --> E[Reflection Index]
C --> E
D --> E
