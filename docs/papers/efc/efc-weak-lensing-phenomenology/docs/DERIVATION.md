# DERIVATION.md — Complete Mathematical Derivation

> Step-by-step derivation of μ(k,z) from EFC field equations with Postulat A.

---

## 1. Starting Point: EFC Field Equations

### 1.1 Action

```
S = ∫d⁴x √(-g) [ R/(16πG) - (κ_S/2)(∇S)² - V(S) - (κ_J/2)J_μJ^μ + γ∇_μS J^μ + λ(∇_μJ^μ - Σ) ]
```

**Fields:**
- `S(x) ∈ [0,1]`: normalized entropy potential
- `J^μ`: energy/entropy flow four-vector
- `Σ ≥ 0`: entropy production rate
- `λ`: Lagrange multiplier

**Constants:**
- `κ_S, κ_J, γ`: dimensionless couplings
- `V(S) = V₀ + ½m_S²(S - S₀)²`: entropic potential

### 1.2 Equations of Motion

From variation of the action:

**Einstein equations:**
```
G_μν = 8πG (T_μν^(m) + T_μν^(S,J))
```

**S equation (from δS):**
```
κ_S □S - V'(S) + γ∇_μJ^μ = 0
```

**J equation (from δJ^μ):**
```
κ_J J_μ = γ∇_μS + ∇_μλ
```

**Constraint (from δλ):**
```
∇_μJ^μ = Σ
```

### 1.3 Combined S Equation

Substituting the constraint:
```
κ_S □S - V'(S) + γΣ = 0
```

---

## 2. The Matter Coupling Problem

### 2.1 Gap Identification

In the above equation, `Σ` is the **only** source for entropy dynamics.

**Problem:** `Σ` is not defined as a function of matter density `ρ_m`.

**Consequence:** Matter perturbations `δ_m` do not source entropy perturbations `δS`.

**Result:** No prediction for modified lensing without additional structure.

### 2.2 Options to Close the System

| Option | Form | Status in EFC |
|--------|------|---------------|
| A | `Σ = Σ(ρ_m, T, ...)` | NOT specified |
| B | `∫ f(S) T √(-g) d⁴x` coupling | NOT in action |
| C | `f(S)R` coupling | NOT in action |

---

## 3. Postulat A: Minimal Closure

### 3.1 The Assumption

We introduce:
```
δΣ(k,z) = ξ ρ_m(z) δ_m(k,z) g(z) h(k)
```

**This is an ASSUMPTION, not a derivation.**

### 3.2 Choice of Functions

**Regime gating:**
```
g(z) = Θ(z_t - z),  z_t = 2
```
- No modification at z > 2
- Preserves CMB and BBN

**Scale filter:**
```
h(k) = 1/(1 + k²/k_*²),  k_* = 0.1 h/Mpc
```
- Concentrates on DES-relevant scales
- Suppresses small-scale modifications

### 3.3 Dimensional Analysis

Since `κ_S, κ_J, γ` are dimensionless and `S ∈ [0,1]`:
- `Σ` has dimension [time⁻¹]
- `ξ` must carry dimension [length³ × time⁻¹ × mass⁻¹]

---

## 4. Linear Perturbation Theory

### 4.1 Background + Perturbation

**Metric (Newtonian gauge):**
```
ds² = -(1 + 2Ψ)dt² + a²(1 - 2Φ)δ_ij dx^i dx^j
```

**Fields:**
```
S = S̄(t) + δS(x,t)
ρ_m = ρ̄_m(t) + δρ_m(x,t)
```

**Matter density contrast:**
```
δ_m ≡ δρ_m / ρ̄_m
```

### 4.2 Linearized S Equation

Perturbing `κ_S □S - V'(S) + γΣ = 0`:

**Background (0th order):**
```
κ_S □S̄ - V'(S̄) + γΣ̄ = 0
```

**Perturbation (1st order):**
```
κ_S □δS - V''(S̄)δS + γδΣ = 0
```

### 4.3 Quasi-Static Approximation

For sub-horizon modes (k >> aH), time derivatives are subdominant:
```
□δS ≈ -∇²δS/a² = k²δS/a²
```

**Result:**
```
(κ_S k²/a² + m_S²) δS = γ δΣ
```

where `V''(S̄) = m_S²`.

### 4.4 Solving for δS

Substituting Postulat A:
```
δS = γξ ρ_m δ_m g(z) h(k) / (κ_S k²/a² + m_S²)
```

---

## 5. Modified Poisson Equation

### 5.1 Energy Density Perturbation

From the stress-energy tensor, the entropy contribution to energy density:
```
ρ_S = ½κ_S(∇S)² + V(S) + ...
```

**Linear perturbation:**
```
δρ_S = κ_S ∇S̄·∇δS + V'(S̄)δS + O(δS²)
```

**Dominant term** (for S̄ slowly varying):
```
δρ_S ≈ V'(S̄) δS = m_S²(S̄ - S₀) δS
```

### 5.2 Total Poisson Equation

Standard form:
```
k²Ψ = 4πGa² (ρ_m δ_m + δρ_S)
```

**Substituting δρ_S:**
```
k²Ψ = 4πGa² ρ_m δ_m [1 + δρ_S/(ρ_m δ_m)]
```

### 5.3 Definition of μ(k,z)

```
k²Ψ = 4πGa² μ(k,z) ρ_m δ_m
```

where:
```
μ(k,z) ≡ 1 + δρ_S/(ρ_m δ_m)
```

---

## 6. Explicit μ(k,z) Formula

### 6.1 Substitution

```
δρ_S/(ρ_m δ_m) = m_S²(S̄ - S₀) × δS / (ρ_m δ_m)
                = m_S²(S̄ - S₀) × γξ g(z) h(k) / (κ_S k²/a² + m_S²)
```

### 6.2 Effective Amplitude

Define:
```
A_μ ≡ m_S²(S̄ - S₀) γξ / (κ_S k_*² + m_S²)
```

### 6.3 Final Result

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   μ(k,z) = 1 + A_μ × Θ(z_t - z) × 1/(1 + k²/k_*²)     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Parameters:**
- `A_μ ∈ [-0.5, +0.5]`: free parameter (constrained by data)
- `z_t = 2`: fixed
- `k_* = 0.1 h/Mpc`: fixed

---

## 7. Gravitational Slip

### 7.1 Definition

```
η ≡ Φ/Ψ
```

### 7.2 Sources of Slip

Anisotropic stress `π` gives:
```
k²(Φ - Ψ) = 12πGa² (ρ + p) σ
```

where `σ` is the shear stress.

### 7.3 EFC Minimal Model

In our linear treatment, the entropy-flow stress-energy has no significant anisotropic stress:
```
π^(S,J) ≈ 0  at linear order
```

**Result:**
```
η ≈ 1
```

---

## 8. Lensing Parameter

### 8.1 Definition

Light deflection depends on:
```
Φ_lens = (Φ + Ψ)/2
```

The lensing parameter is:
```
Σ_lens(k,z) = μ(k,z)/2 × (1 + η)
```

### 8.2 Minimal Model Result

With η = 1:
```
┌─────────────────────────────────────┐
│                                     │
│   Σ_lens(k,z) = μ(k,z)             │
│                                     │
└─────────────────────────────────────┘
```

**Implication:** Same function controls growth and lensing.

---

## 9. Parameter Translation

### 9.1 From A_μ to EFC Constants

If data measures `A_μ = A_μ^obs`:
```
m_S²(S̄ - S₀) γξ = A_μ^obs × (κ_S k_*² + m_S²)
```

### 9.2 Physical Interpretation

**A_μ < 0** (reduced lensing):
- Requires `(S̄ - S₀) γξ < 0`
- Either: S̄ < S₀ (entropy below equilibrium), or γξ < 0

**A_μ > 0** (enhanced lensing):
- Would increase S₈ tension
- Disfavored by current data

### 9.3 Order of Magnitude

For DES Y6 match (S₈ ratio ~ 0.95):
```
A_μ ≈ -0.1 to -0.2
```

---

## 10. Validity Conditions

### 10.1 Linear Regime

This derivation assumes:
- `|δS/S̄| << 1`
- `|δ_m| << 1`

**Breaks down:** k > 0.3 h/Mpc (non-linear scales)

### 10.2 Quasi-Static Approximation

Assumes:
- `k >> aH` (sub-horizon)
- `∂²δS/∂t² << k²δS/a²`

**Breaks down:** k < 0.001 h/Mpc (horizon scales)

### 10.3 Regime Gating

The Heaviside function `Θ(z_t - z)` ensures:
- No modification at z > z_t = 2
- CMB physics unaffected
- Early universe unchanged

---

## Summary

```
INPUT:
  - EFC action with fields S, J^μ, Σ
  - Postulat A: δΣ ∝ ρ_m δ_m

DERIVATION:
  1. Linearize S equation
  2. Apply quasi-static approximation
  3. Solve for δS
  4. Compute δρ_S from potential
  5. Modify Poisson equation
  6. Define μ(k,z)

OUTPUT:
  μ(k,z) = 1 + A_μ × Θ(2-z) × 1/(1 + k²/k_*²)
  Σ_lens(k,z) = μ(k,z)  [minimal model]

FREE PARAMETER:
  A_μ ∈ [-0.5, +0.5] — constrained by DES Y6
```
