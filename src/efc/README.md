# efc — Python Implementation of Energy-Flow Cosmology

**Package:** `efc` | **Python:** 3.9+ | **Dependencies:** numpy, scipy, matplotlib

The `efc` package implements the core equations, entropy fields, perturbation theory, and validation tools for Energy-Flow Cosmology.

## Module Map

### `core/` — Core Framework
- **`efc_core.py`** — `EFCParameters` dataclass, `EFCModel` base model (energy-flow field Ef, entropy gradient nabla-S, rotation velocity), `load_parameters()` for reading parameters.json.

### `entropy/` — Entropy Field
- **`efc_entropy.py`** — `entropy_field()`, `entropy_gradient()` — computes the scalar entropy field S(a) and its spatial gradient.

### `potential/` — Energy-Flow Potential
- **`efc_potential.py`** — `compute_energy_flow()`, `energy_density()`, `energy_flow_rate()` — energy-flow potential and density computations.

### `perturbation/` — Perturbation-Sector Physics
The perturbation module implements the modified growth equation and Hubble friction channel:
- **`mu.py`** — Effective gravitational coupling mu(a) = 1 - B*g(a) with mu < 1 (suppresses growth). Functions: `mu_of_a()`, `mu_of_z()`, `sigma8_suppression_integral()`.
- **`growth.py`** — Modified linear growth ODE solver: f' + f^2 + (1/2 - 3/2 Omega_m)f = 3/2 mu(a) Omega_m. Functions: `solve_growth()`, `compute_fsigma8()`.
- **`gate.py`** — Sigmoid gate g(a) = 1/(1 + (a_t/a)^n). Functions: `gate_function()`, `calibrate_B()`.
- **`background.py`** — Background-level Friedmann modification, sign structure Delta-E^2 <= 0 (Lemma 1). Functions: `E2_efc()`, `hubble_efc()`, `verify_sign_lemma()`.
- **`robustness.py`** — Leave-one-out analysis for MVP-G1 Hubble-Friction channel. Functions: `chi2_fsigma8()`, `loo_pass_criterion()`, `summarise_loo()`.

### `validation/` — Observational Validation
- **`efc_validation.py`** — `rotation_curve_efc()`, `validate_rotation_curve()`, `compare_with_sparc()` — SPARC rotation curve comparison.
- **`sparc_io.py`** — `load_rotation_curve()` — robust SPARC data reader.

### `solver/` — Grid-AQUAL Solver
- **`grid_aqual_killtests.py`** — Discrete AQUAL solver with three kill-tests: Newton recovery (deep UV), prefactor C ~ 2.3 convergence, mass-scaling of transition radius.

### `meta/` — Meta-Level Tools
- **`cofield_simulator.py`** — Placeholder for co-field simulation tools.

## Quick Start

```python
from efc.core import EFCModel, load_parameters
from efc.perturbation.growth import solve_growth, compute_fsigma8
from efc.perturbation.mu import mu_of_a

# Load default parameters
params = load_parameters()

# Compute mu(a) at scale factor a=1
mu_today = mu_of_a(1.0)

# Solve growth equation
a_arr, f_arr, D_arr = solve_growth()
```

## Key References

| Module | DOI |
|---|---|
| perturbation/mu, growth | [10.6084/m9.figshare.31333600](https://doi.org/10.6084/m9.figshare.31333600) |
| perturbation/background | [10.6084/m9.figshare.31333414](https://doi.org/10.6084/m9.figshare.31333414) |
| perturbation/robustness | [10.6084/m9.figshare.31332730](https://doi.org/10.6084/m9.figshare.31332730) |
| solver/grid_aqual | Grid-AQUAL v0.1 (internal) |

_Maintained as part of the EFC repository._
