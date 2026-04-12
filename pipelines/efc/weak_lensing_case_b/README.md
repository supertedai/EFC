# EFC Weak Lensing — Case B Pipeline

Growth-modified power spectrum + scale-dependent lensing constraint.

## Case A vs Case B

| | Case A (nested_sampling) | Case B (this pipeline) |
|---|---|---|
| **P(k) modification** | None — Alens scales amplitude | μ(k,z) in growth ODE modifies D(k,z) |
| **Lensing modification** | Alens = Σ₀² (constant) | Σ(k,z) full scale-dependent |
| **What it tests** | Does EFC improve CMB lensing amplitude? | Does EFC produce consistent growth + lensing? |
| **Degeneracy** | Can absorb noise in Alens | Growth and lensing must agree simultaneously |
| **Constraint power** | Low (1 number) | High (k,z structure) |

## How it works

```
(K0, m_sq)
    ↓ bridge_theory.py
R(k,a) = K0 × Θ(ρ) × (Γ'φ̇)² × a⁴ / k⁴
    ↓
μ(k,z) = 1/(1+R)           ←── injected into growth ODE
η(k,z) = 1 + (η_ref-1)/f_ref × f(K0,m²,k)
Σ(k,z) = μ(1+η)/2         ←── modifies lensing kernel
    ↓
P_eff(k,z) = P_ΛCDM × [D_EFC/D_GR]² × Σ²
    ↓
C_ℓ^{γγ}(i,j) via Limber integral
    ↓
ln(B) = ln(Z_EFC) - ln(Z_ΛCDM)
```

## Key physics

At the calibration anchor (K0=1.66, m²=0.0035, k=0.05 h/Mpc, z=0):
- μ = 0.94 (6% weaker gravity → suppressed growth)
- Σ = 1.05 (5% enhanced lensing)
- These compete: growth suppression vs lensing enhancement

At DES Y3 scales (k ~ 0.1-1 h/Mpc):
- R(k) ∝ k⁻⁴ → modification vanishes at small scales (GR recovered)
- Σ(k,z) carries scale structure that a constant Alens cannot

This is why Case B constrains more than Case A.

## Files

```
config/
  efc_wl_polychord.yaml      # EFC nested sampling (8 params)
  lcdm_wl_polychord.yaml     # ΛCDM reference (6 params)
src/
  efc_lensing_theory.py      # Bridge + growth ODE + modified P(k,z)
  cosmic_shear_likelihood.py  # DES Y3-like C_ℓ likelihood
  launch_wl_nested.py        # Pipeline launcher
tests/
  test_case_b_theory.py      # Physics + config sanity tests
```

## Quick start

```bash
cd pipelines/efc/weak_lensing_case_b

# Run tests first
python tests/test_case_b_theory.py

# Cobaya + PolyChord
mpirun -n 32 python src/launch_wl_nested.py

# Or dynesty standalone
python src/launch_wl_nested.py --dynesty --ncpu 16
```

## Expected outcomes

Given Δχ² ≈ -0.30 from CMB (Case A):

| Scenario | ln(B) | Meaning |
|----------|-------|---------|
| Lensing confirms CMB signal | > 0 | EFC modification real |
| Lensing contradicts CMB | << 0 | CMB signal was noise |
| Inconclusive | ~ 0 | Need more data (Euclid DR1) |

The most informative outcome is **disagreement** between Case A and Case B:
- If Case A gives ln(B) ~ 0 but Case B gives ln(B) < -2: the model
  absorbs noise through Alens but cannot explain actual lensing structure
- This is the falsification pathway SPARC cannot provide

## Integration with Symbiose

```python
mattermost_post(
    channel="mcmc-emcee",
    text=f"### Case B Weak Lensing Complete\n"
         f"ln(Z_EFC) = {logZ_efc:.2f}\n"
         f"ln(B) = {ln_B:.2f} → {verdict}\n"
         f"Case A vs Case B: {'consistent' if consistent else 'TENSION'}"
)
```
