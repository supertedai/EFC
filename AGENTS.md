# AI Agents Guide for Energy-Flow Cosmology

**Version**: 2.0 | **Updated**: 2026-01-30

This document provides comprehensive instructions for AI agents working with the EFC repository.

---

## Quick Reference

```yaml
author: Morten Magnusson
orcid: 0009-0002-4860-5095
repository: github.com/supertedai/EFC
license: CC-BY-4.0
core_principle: "Energy flows along entropy gradients"
```

| Resource | Location |
|----------|----------|
| Machine Navigation | [`llms.txt`](./llms.txt) |
| Provenance | [`/auth/`](./auth/) |
| Schema | [`/schema/global_schema.json`](./schema/global_schema.json) |
| Papers | [`/docs/papers/efc/`](./docs/papers/efc/) |
| DOI Map | [`/figshare/doi-map.json`](./figshare/doi-map.json) |

---

## Core Theory Summary

### The Big Picture

EFC is a unified thermodynamic framework where **energy flows along entropy gradients**. This single principle explains:

| Phenomenon | EFC Mechanism |
|------------|---------------|
| Galaxy rotation | Entropy gradient coupling (no dark matter particles) |
| Cosmic acceleration | Thermodynamic expansion (no dark energy substance) |
| Structure formation | Regime-dependent growth via R(k,S) |
| S₈ tension | L1→L2 regime transition |

### Key Equations

**Effective Gravitational Coupling:**
```
μ(a) = G_eff/G = 1 + βS(a)
```

**Regime Response Surface:**
```
μ(k,S) = 1 + R(k,S)
```

**Empirical Constraint (2026):**
```
β ≈ 0.16 (from unified BAO/SN/RSD analysis)
R(k≈0.13, S≈0.30) ≈ +0.30 (from WP3 RSD slice)
```

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
│   └── papers/efc/     # All papers (AI-optimized metadata)
├── schema/             # Ontology, JSON-LD contexts
├── api/                # Semantic REST API
├── jsonld/             # Linked data files
├── figshare/           # DOI mappings
├── integrations/
│   └── mcp/            # MCP Server for AI agents
├── llms.txt            # Machine-readable navigation
└── AGENTS.md           # This file
```

---

## Paper Metadata Structure

Each paper in `/docs/papers/efc/[paper-name]/` contains:

| File | Purpose | Format |
|------|---------|--------|
| `README.md` | Human-readable summary | Markdown |
| `index.json` | Machine-readable index | JSON |
| `schema.json` | Validation schema | JSON Schema |
| `*.jsonld` | Linked data | JSON-LD |
| `citations.bib` | References | BibTeX |
| `*.pdf` | Authoritative document | PDF |

### Example: Reading Paper Metadata

```python
import json

# Load machine-readable index
with open('docs/papers/efc/WP3__First_Empirical_Slice.../index.json') as f:
    paper = json.load(f)

print(paper['doi'])           # "10.6084/m9.figshare.31215259"
print(paper['keywords'])      # ["R(k,S)", "fσ₈", "RSD", ...]
print(paper['results'])       # {"delta_chi2": 1.71, ...}
```

---

## Navigation Rules

### When Asked About EFC

1. **Check `/auth/`** — Understand provenance first
2. **Read `/theory/formal/`** — For mathematical claims
3. **Reference `/docs/papers/`** — For published findings
4. **Use DOIs** — From `/figshare/doi-map.json`

### When Modifying Content

1. **Preserve semantic structure** — Maintain JSON-LD consistency
2. **Update both formats** — Keep .md and .jsonld in sync
3. **Follow schema** — Respect `/schema/global_schema.json`
4. **Log changes** — Update metadata timestamps

### When Creating New Papers

Required files:
```
docs/papers/efc/[Paper-Name]/
├── README.md              # Human summary
├── index.json             # Machine index
├── schema.json            # Validation
├── [Paper-Name].jsonld    # Linked data
├── [Paper-Name].pdf       # Authoritative
└── citations.bib          # References
```

---

## Key Publications Index

### Foundational Theory
| ID | DOI | Title |
|----|-----|-------|
| `efc-v1.2` | 10.6084/m9.figshare.30563738 | EFC Foundational Framework |
| `efc-v2.2` | 10.6084/m9.figshare.30530156 | Cross-Field Integration |
| `auth-layer` | 10.6084/m9.figshare.30656828 | AUTH Layer (Provenance) |

### Empirical Analysis
| ID | DOI | Key Result |
|----|-----|------------|
| `rks-framework` | 10.6084/m9.figshare.31211437 | R(k,S) theoretical framework |
| `wp3-rks-slice` | 10.6084/m9.figshare.31215259 | R≈+0.30 at (k≈0.13, S≈0.30) |
| `unified-bao` | 10.6084/m9.figshare.31215613 | β=0.16, Δχ²=+1.7 |

### Human-AI Collaboration
| ID | DOI | Topic |
|----|-----|-------|
| `symbiosis` | 10.6084/m9.figshare.30773684 | Graph-Vector memory architecture |

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

---

## Error Handling

If inconsistencies found:

1. **Schema authority**: `/schema/global_schema.json`
2. **Scope boundaries**: `/auth/manifest.json`
3. **Canonical DOIs**: `/figshare/doi-map.json`
4. **Report issues**: Repository maintainer

---

## Contact

- **Website**: [magnusson.as/cooperation](https://www.magnusson.as/cooperation)
- **Project**: [energyflow-cosmology.com](https://energyflow-cosmology.com/)
- **ORCID**: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)

---

*This repository supports symbiotic human-AI collaboration as defined in `/methodology/symbiosis-interface/`*
