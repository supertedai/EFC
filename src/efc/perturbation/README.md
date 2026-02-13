# EFC Perturbation Package

Python implementation of the perturbation-level physics from the EFC gate-function framework.

## Modules

| Module | Description | Reference |
|--------|-------------|-----------|
| `gate.py` | Sigmoid gate g(a) and calibration B = (1−μ₀)/g(1;n) | Technical Notes I & II |
| `background.py` | Background ΔE² sign structure and E²_EFC(z) | Technical Note I (DOI: 10.6084/m9.figshare.31333414) |
| `mu.py` | Perturbation μ(a) = 1 − B g(a) and suppression integral | Technical Note II (DOI: 10.6084/m9.figshare.31333600) |
| `growth.py` | Linear growth ODE solver with modified μ(a) | Technical Notes I & II |
| `robustness.py` | LOO analysis, fσ₈ data, N2a priors | Robustness paper (DOI: 10.6084/m9.figshare.31332730) |

## Quick Start

```python
from efc.perturbation import gate_function, mu_of_a, calibrate_B
from efc.perturbation import solve_growth, compute_fsigma8
from efc.perturbation.mu import WP1A_REFERENCE, verify_universal_factor_2
from efc.perturbation.robustness import get_fsigma8_arrays, summarise_loo

# Gate function
import numpy as np
a = np.linspace(0.1, 1.0, 100)
g = gate_function(a, z_t=1.01, n=2)

# Calibrate B for desired μ₀
B = calibrate_B(mu_0=0.85, n=2)  # → 0.187

# Compute μ(a) profile
mu = mu_of_a(a, B=B, n=2)

# Verify universal factor-2
result = verify_universal_factor_2(mu_0=0.85)
print(f"Ratio n=2/n=6: {result['ratio']:.2f}")  # → 2.00

# Solve growth equation with WP1a reference model
sol = solve_growth(B=0.187, n=2)

# Compute fσ₈ at data redshifts
data = get_fsigma8_arrays()
pred = compute_fsigma8(data["z"], B=0.187, n=2)

# LOO robustness summary
loo = summarise_loo()
print(f"LOO pass rate: {loo['passed']}/{loo['total']}")
```

## Reference Models

### WP1a (Technical Note II, Eq. 6)
- A = 0, B = 0.187, n = 2, z_t = 1.01
- μ₀ = 0.85, σ₈ = 0.773, S₈ = 0.790
- S₈ gap closure: 73%

## Dependencies

- numpy

## Version

1.0
