# Symbiose Operating Model — EFC side

This is the EFC-side mirror of the Symbiose Operating Model. **Canonical SOM lives in supertedai/AGI** at `som/`:

- Schemas: https://github.com/supertedai/AGI/tree/claude/backend-daemon-structure-ilT2W/som/schemas
- Governance (SOM.md, RCE-CONTRACT.md, loops.md, quality-gates.md): https://github.com/supertedai/AGI/tree/claude/backend-daemon-structure-ilT2W/som/governance
- Registries (domains.yaml, ports.yaml, daemons.yaml, layers.yaml): https://github.com/supertedai/AGI/tree/claude/backend-daemon-structure-ilT2W/som/registry
- Templates: https://github.com/supertedai/AGI/tree/claude/backend-daemon-structure-ilT2W/som/templates
- RFCs: https://github.com/supertedai/AGI/tree/claude/backend-daemon-structure-ilT2W/som/RFCs

This repo carries:

- `/layer.yaml` at repo root — the canonical declaration of EFC as a layer in Symbiose topology
- `som/capabilities/*.capability.yaml` — the 5 master EFC orchestrators with full RCE 5-component contract
- `som/INVENTORY-EFC.md` — EFC-side inventory at bootstrap time (2026-05-19)

## Why two-place storage

The SOM is one operating model that applies to all Symbiose repos. Schemas + governance live once, in AGI. Each repo carries only its own `layer.yaml` + per-capability manifests. CI tooling (`sym` CLI from AGI) walks the registry and validates across repos.

When `supertedai/medicine` + `supertedai/economy` + `supertedai/biology` + `supertedai/earth` come online, each gets the same skeleton: `/layer.yaml`, `/som/capabilities/`, `/som/INVENTORY-<repo>.md`. Same gates apply.

## Status

Bootstrapped 2026-05-19 on `claude/backend-daemon-structure-ilT2W` (this branch).

See RFC-0001 in AGI for the full proposal.
