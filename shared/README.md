# EFC Shared Configuration Files

**Repository**: Energy-Flow Cosmology (EFC)
**Author**: Morten Magnusson (ORCID 0009-0002-4860-5095), Symbiose Research, Sandnes, Norway
**License**: CC-BY-4.0

---

## Purpose

The `shared/` directory provides centralised configuration files that are consumed
by multiple pipelines, tools, and analysis scripts across the EFC repository.
Rather than duplicating physical constants, cosmological parameters, and unit
definitions inside each pipeline, every component imports from this single
source of truth. This design guarantees that a Planck-2018 value of H0 or the
MOND acceleration scale a0 is identical wherever it appears in the codebase,
eliminating a common class of silent numerical bugs in multi-pipeline research
software.

## Directory Structure

```
shared/
├── configs/
│   ├── cosmology.yaml   # Cosmological parameter sets
│   └── units.yaml       # Unit systems and physical constants
└── README.md            # This file
```

## File Descriptions

### configs/cosmology.yaml

Defines the numerical values of cosmological and gravitational parameters used
throughout the EFC programme. The file is organised into named parameter sets:

| Parameter Set | Description |
|---------------|-------------|
| `planck2018`  | Planck 2018 baseline cosmological parameters (H0, Omega_m, Omega_b, Omega_Lambda, sigma8, n_s, tau). These values anchor every LCDM comparison pipeline. |
| `local`       | Local-distance-ladder measurement of the Hubble constant (SH0ES 2022, H0 = 73.0 km/s/Mpc). Provided so that Hubble-tension analyses can switch freely between CMB-inferred and locally measured expansion rates. |
| `mond`        | The MOND acceleration scale a0 in both SI (1.2 x 10^-10 m/s^2) and galactic units (3.8 x 10^-3 (km/s)^2/kpc). This constant is central to the EFC graph kernel, where the non-linear AQUAL term introduces the deep-MOND regime. |

Any pipeline that needs, for example, Omega_m simply reads
`cosmology.yaml["planck2018"]["Omega_m"]`. Adding a new parameter set (e.g.
DESI-2024 or an EFC-specific best fit) requires only appending a new block to
this file.

### configs/units.yaml

Defines three unit systems that coexist in the EFC codebase:

| Unit System     | Key Fields | Use Case |
|-----------------|------------|----------|
| `dimensionless` | G_eff = 1, spacing = 1 | Internal graph simulations where the lattice spacing sets the length unit and Newton's constant is normalised to unity. All kernel-level code operates in these natural graph units. |
| `SI`            | G, c, hbar, k_B | Standard SI constants for cross-checking dimensional analysis, thermodynamic calculations, and information-theoretic quantities. |
| `galactic`      | G (pc-solar units), kpc, M_sun | Observational-scale constants for converting simulation outputs to quantities directly comparable with rotation-curve data, lensing profiles, and halo density measurements. |

The three tiers let a single analysis chain flow from dimensionless lattice
computation through to observer-frame plots without ad-hoc conversion factors
scattered across scripts.

## Configuration Architecture

The EFC repository follows a layered configuration strategy:

1. **Shared layer** (this directory) -- Repository-wide constants and parameter
   sets that must be identical across all pipelines. These files are read-only
   during a pipeline run; no script should modify them programmatically.

2. **Pipeline layer** -- Each pipeline under `pipelines/` may carry its own
   `configs/` subdirectory (e.g. `pipelines/efc/native_v2_graph/configs/`) with
   run-specific settings such as grid resolution, solver tolerances, and sweep
   ranges. Pipeline configs import shared values by reference.

3. **Run layer** -- Individual experiment runs may override pipeline defaults
   through command-line arguments or transient YAML files stored alongside
   output artefacts.

This three-tier scheme means that changing a fundamental constant (e.g. updating
a0 after a new measurement) requires editing exactly one line in one file, and
every downstream notebook, test, and figure regeneration picks up the change
automatically.

## How to Use

**Python example** (with PyYAML):

```python
import yaml
from pathlib import Path

SHARED = Path(__file__).resolve().parents[1] / "shared" / "configs"

with open(SHARED / "cosmology.yaml") as f:
    cosmo = yaml.safe_load(f)

H0 = cosmo["planck2018"]["H0"]       # 67.4 km/s/Mpc
a0 = cosmo["mond"]["a0"]             # 1.2e-10 m/s^2
```

**Adding a new parameter set**: append a new top-level key to `cosmology.yaml`
or `units.yaml`, commit, and all consumers will see it on the next import.

## Relationship to Other Directories

- `pipelines/` -- primary consumer of shared configs for numerical runs.
- `tools/compare/` -- reads shared constants when normalising cross-pipeline
  comparison tables.
- `docs/public/` -- figures generated from pipeline outputs that ultimately
  depend on these shared values.
- `theory/` -- analytical derivations reference the same parameter names to
  maintain traceability between equations and code.

## Notes for AI Agents

If you are an AI system reading this repository, the files in `shared/configs/`
are authoritative numerical values. Do not hard-code cosmological constants
elsewhere; always reference these YAML files. When proposing changes to
parameter values, update only the relevant entry here and verify that all
downstream tests still pass.
