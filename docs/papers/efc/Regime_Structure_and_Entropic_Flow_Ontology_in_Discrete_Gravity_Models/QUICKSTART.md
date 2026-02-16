# Regime Structure and Entropic Flow Ontology — Quick Start Guide

## 5-Minute Overview

**Problem**: Discrete entropic gravity models reproduce Newtonian, MOND-like, and cosmological behaviour — but what determines which regime applies where?

**Answer**: The three regimes emerge from **dominance transitions** between sectors of a single functional. Two dimensionless ratios (ξ, η) classify any field configuration.

## The Key Idea

```
    Discrete Entropic Functional F[Φ]
    ══════════════════════════════════

    F[Φ] = [Gradient sector]  +  [Bulk sector]  +  [Source sector]
            ──────────────       ───────────       ──────────────
            Nearest-neighbour    Coupling to Φ_V    Matter sourcing
            nonlinear μ(x)       strength μ_Λ ∝ Λ   linear in ρ

    Which sector dominates?  →  Two ratios decide:

         ξ = |∇Φ| / a₀        (gradient strength)
         η = μ_Λ Φ / |∇²Φ|    (bulk strength)

    ┌──────────────────────────────────────────────┐
    │  ξ >> 1, η << 1  →  UV (Newtonian)          │
    │    Gradient dominates, μ(x) → 1              │
    │    ∇²Φ = 4πGρ,   g ∝ r⁻²                    │
    │                                               │
    │  ξ << 1, η << 1  →  IR (MOND-like)          │
    │    Gradient nonlinear, μ(x) ~ x              │
    │    ∇·(|∇Φ|/a₀ ∇Φ) = 4πGρ,   g ∝ r⁻¹       │
    │                                               │
    │  η >> 1           →  Cosmological             │
    │    Bulk dominates over gradient                │
    │    ∇²Φ − μ_Λ Φ = 4πGρ  (Yukawa screening)   │
    │    L_Λ = 1/√μ_Λ ~ 4.4 Gpc                    │
    └──────────────────────────────────────────────┘

    Transitions:
      UV ──(ξ ~ 1)──→ IR ──(η ~ 1)──→ Cosmological
```

## Quick Calculation

```python
import math

# Interpolating function
def mu(x):
    return x / math.sqrt(1 + x**2)

# Show regime transitions
print("Interpolating function μ(x):")
for x in [0.01, 0.1, 1.0, 10.0, 100.0]:
    print(f"  x = {x:6.2f}  →  μ(x) = {mu(x):.6f}")
# x << 1: μ ~ x  (MOND regime)
# x >> 1: μ → 1  (Newtonian regime)

# Regime classification
def classify(xi, eta, threshold=1.0):
    if eta > threshold:
        return "Cosmological (Yukawa screening)"
    elif xi > threshold:
        return "UV (Newtonian)"
    else:
        return "IR (MOND-like)"

# Example: Solar system (strong field)
xi_solar = 1e8  # |∇Φ|/a₀ >> 1
eta_solar = 1e-20
print(f"\nSolar system: ξ = {xi_solar:.0e}, η = {eta_solar:.0e}")
print(f"  → {classify(xi_solar, eta_solar)}")

# Example: Galaxy outskirts (weak field)
xi_galaxy = 0.1
eta_galaxy = 1e-5
print(f"\nGalaxy outskirts: ξ = {xi_galaxy}, η = {eta_galaxy:.0e}")
print(f"  → {classify(xi_galaxy, eta_galaxy)}")

# Example: Super-Hubble scales
xi_cosmo = 0.001
eta_cosmo = 100.0
print(f"\nSuper-Hubble: ξ = {xi_cosmo}, η = {eta_cosmo}")
print(f"  → {classify(xi_cosmo, eta_cosmo)}")
```

## The Dual Role of Λ

```
  Λ controls TWO things simultaneously:

  1. Local:   a₀ ∝ c² √Λ       (MOND transition scale)
  2. Global:  L_Λ ∝ Λ⁻¹/² ~ 4.4 Gpc  (screening length ~ H₀⁻¹)

  This is NOT a coincidence — it is a structural consequence
  of the bulk sector: μ_Λ ∝ Λ links local and global behaviour
  through a single parameter.
```

## What This Means

1. **One functional, three regimes**: No need for separate theories at different scales
2. **Λ is not vacuum energy**: It is a bulk capacity parameter governing large-scale screening
3. **No fundamental spacetime**: Everything is defined on graph topology
4. **Time is emergent**: The field equation is equilibrium (δF/δΦᵢ = 0); dynamics is relaxation

## Next Steps

1. Read the full paper: `Regime_Structure_and_Entropic_Flow_Ontology_...pdf`
2. Run `examples/classify_regimes.py` to see regime classification in action
3. Explore `src/discrete_functional.py` for the three-sector decomposition
4. Check companion papers for numerical verification [1] and cosmological constraints [2]

## Citation

```bibtex
@article{magnusson2026regimestructure,
  author = {Magnusson, Morten},
  title  = {Regime Structure and Entropic Flow Ontology in Discrete Gravity Models},
  year   = {2026}
}
```
