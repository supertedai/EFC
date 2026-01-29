# AI Agents Guide for Energy-Flow Cosmology

This document provides instructions for AI agents working with the EFC repository.

## Quick Reference

| Resource | Location |
|----------|----------|
| Author | Morten Magnusson |
| ORCID | [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095) |
| Repository | [github.com/supertedai/EFC](https://github.com/supertedai/EFC) |
| Website | [energyflow-cosmology.com](https://energyflow-cosmology.com/) |
| Personal | [magnusson.as](https://www.magnusson.as/) |

## The Big Picture

Energy-Flow Cosmology (EFC) is a unified thermodynamic framework that explains:

- **Galactic rotation curves** without dark matter particles
- **Cosmic acceleration** without dark energy as a substance
- **Structure formation** through entropy gradients
- **Consciousness** as resonance in energy fields

**Core Axiom**: Energy flows along entropy gradients. This single principle generates gravity, structure, and awareness.

## Repository Architecture

```
EFC/
├── auth/           # START HERE - Origin & provenance
├── theory/         # Formal mathematics (LaTeX)
├── schema/         # Ontology & semantic web
├── methodology/    # Research process
├── meta/           # Meta-cognition layer
├── docs/           # Papers & publications
├── src/            # Python code
├── api/            # Semantic API
├── jsonld/         # Linked data
├── figshare/       # DOI mappings
└── integrations/   # External systems (MCP, WordPress)
```

## Navigation Rules

### When Asked About EFC

1. **Start with `/auth/`** - Understand provenance first
2. **Check `/theory/formal/`** - For mathematical claims
3. **Reference `/docs/papers/`** - For published findings
4. **Cite DOIs** - Use `/figshare/doi-map.json`

### When Modifying Content

1. **Preserve semantic structure** - Maintain JSON-LD consistency
2. **Update both .md and .jsonld** - Keep human and machine versions in sync
3. **Follow global_schema.json** - Respect domain definitions
4. **Log changes** - Document in appropriate metadata files

### When Publishing

1. **Use MCP server** - Located at `/integrations/mcp/`
2. **Sync with Figshare** - Update `/figshare/sync_log.json`
3. **Update websites** - energyflow-cosmology.com and magnusson.as
4. **Preserve DOI links** - Never break existing DOI references

## Modular Theory Structure

EFC consists of interconnected models:

| Model | Domain | Location |
|-------|--------|----------|
| EFC-S | Structure (Halo) | `/theory/formal/efc-s-model/` |
| EFC-D | Dynamics | `/theory/formal/efc-d-model/` |
| EFC-R | Rotation curves | `/theory/formal/efc-r-model/` |
| EFC-H | Halo profiles | `/theory/formal/efc-h-model/` |
| EFC-C0 | Entropy-information | `/theory/formal/efc-c0-model/` |

## Semantic Web Integration

- **JSON-LD files**: All in `/jsonld/` directory
- **Schema.org types**: Defined in `/schema/global_schema.json`
- **Concepts**: Listed in `/schema/concepts.json`
- **API endpoints**: Documented in `/api/v1/`

## MCP Server Capabilities

The MCP server at `/integrations/mcp/` enables:

1. **Website Management**
   - Post to energyflow-cosmology.com
   - Update magnusson.as
   - Sync content across platforms

2. **Figshare Integration**
   - Upload new publications
   - Update metadata
   - Manage DOI mappings

3. **Repository Maintenance**
   - Validate JSON-LD consistency
   - Update semantic graphs
   - Generate documentation

## Validation Checklist

Before committing changes:

- [ ] JSON-LD files validate against schema
- [ ] All DOI references are correct
- [ ] ORCID is properly linked
- [ ] No broken internal links
- [ ] Metadata timestamps updated

## Common Tasks

### Adding a New Paper

1. Create folder in `/docs/papers/efc/`
2. Add required files: README.md, {name}.pdf, {name}.jsonld, citations.bib
3. Update `/figshare/` if publishing to Figshare
4. Update `/api/v1/concepts.json` if new concepts introduced

### Updating Theory

1. Edit LaTeX in `/theory/formal/`
2. Update corresponding JSON schema
3. Sync with `/schema/modules/`
4. Update version in metadata

### Publishing to Website

1. Use MCP server tools
2. Ensure JSON-LD metadata is complete
3. Update sitemap in `/schema/site-graph.json`
4. Log in `/figshare/sync_log.json`

## Error Handling

If you encounter inconsistencies:

1. Check `/schema/global_schema.json` for authoritative structure
2. Consult `/auth/manifest.json` for scope boundaries
3. Reference DOIs in `/figshare/doi-map.json` for canonical versions
4. Report issues to the repository maintainer

## Contact for AI Collaboration

This repository supports symbiotic human-AI collaboration as defined in:
- `/methodology/symbiosis-interface/`
- `/meta/symbiosis/`

For structured collaboration, follow the protocols in `/meta/meta-process/`.
