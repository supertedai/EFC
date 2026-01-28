"""
PHYSICAL DERIVATION v2: w AND L₀
=================================

Problem with v1: τ_mix was too short (0.2 Myr), giving w → ∞

Better approach:
- w: Use PHASE SPACE density preservation, not just entropy mixing
- L₀: Use physical correlation length directly

"""

import numpy as np

print("=" * 70)
print("PHYSICAL DERIVATION v2: w AND L₀")
print("=" * 70)
print()

# =============================================================================
# BULLET CLUSTER PARAMETERS
# =============================================================================

T_ICM_keV = 15.5           # keV
n_e_cm3 = 3e-3             # cm⁻³
v_merger_km_s = 4700       # km/s
R_core_kpc = 250           # kpc
t_since_Myr = 150          # Myr since core passage

kpc_to_cm = 3.086e21
Myr_to_s = 3.15e13

# =============================================================================
# DERIVATION OF w: COLLISIONAL vs COLLISIONLESS RESPONSE
# =============================================================================

print("1. DERIVATION OF w")
print("-" * 50)
print()

# Key insight: In EFC, the entropy-gravity coupling comes from ∇S.
# 
# For COLLISIONLESS matter (stars/galaxies):
#   - Particles follow geodesics
#   - Phase space density f is conserved (Liouville)
#   - Entropy S = -∫f ln(f) dΓ is conserved
#   - ∇S follows the matter distribution
#
# For COLLISIONAL matter (gas):
#   - Particles interact via Coulomb collisions
#   - Entropy is PRODUCED in shocks
#   - ∇S is dominated by THERMODYNAMIC gradients, not density
#
# After a merger shock:
#   - Gas ∇S points perpendicular to shock front (thermal gradient)
#   - Stellar ∇S still follows the mass distribution
#
# The parameter w should reflect the EFFICIENCY of entropy gradient
# in tracing mass distribution.

# Model: w = (dS/dρ)_stars / (dS/dρ)_gas
#
# For ideal gas: S ∝ ln(T^(3/2) / ρ)
#   → (∂S/∂ρ)_T = -1/ρ
#   → (∂S/∂T)_ρ = (3/2)/T
#
# Gas: After shock, T and ρ are decorrelated. 
#      The gradient ∇S ~ (3/2)(∇T)/T - (∇ρ)/ρ
#      The (∇T)/T term dominates in post-shock region.
#
# Stars: No temperature, S ∝ -ln(ρ) (configuration space)
#      The gradient ∇S ~ -(∇ρ)/ρ
#
# Ratio: How much does gas ∇S correlate with mass vs stellar ∇S?

# Post-shock ICM: temperature gradient scale ~ shock width
# Bullet Cluster shock Mach number M ≈ 3
# Shock width ~ few × mean free path

M_shock = 3.0  # Mach number
lambda_mfp_kpc = 23  # Mean free path in ICM ~23 kpc (Markevitch+ 2006)
L_shock_kpc = 3 * lambda_mfp_kpc  # Shock transition region

print(f"Shock Mach number: M = {M_shock}")
print(f"Mean free path: λ_mfp = {lambda_mfp_kpc} kpc")
print(f"Shock width: L_shock = {L_shock_kpc} kpc")
print()

# Temperature jump across shock: T_post/T_pre = (5M² - 1)(M² + 3)/(16M²)
T_ratio = (5*M_shock**2 - 1) * (M_shock**2 + 3) / (16 * M_shock**2)
print(f"Temperature jump: T_post/T_pre = {T_ratio:.2f}")

# Density jump: ρ_post/ρ_pre = 4M²/(M² + 3)
rho_ratio = 4 * M_shock**2 / (M_shock**2 + 3)
print(f"Density jump: ρ_post/ρ_pre = {rho_ratio:.2f}")
print()

# For gas, the entropy gradient in shock region:
# |∇S|_gas ~ |(3/2)(ΔT/T)/L_shock - (Δρ/ρ)/L_shock|
# The temperature term dominates for strong shocks

grad_S_gas_thermal = (3/2) * np.log(T_ratio) / L_shock_kpc
grad_S_gas_density = np.log(rho_ratio) / L_shock_kpc
grad_S_gas = np.abs(grad_S_gas_thermal - grad_S_gas_density)

print(f"|∇S|_gas (thermal contribution): {grad_S_gas_thermal:.4f} /kpc")
print(f"|∇S|_gas (density contribution): {grad_S_gas_density:.4f} /kpc")
print(f"|∇S|_gas (total in shock): {grad_S_gas:.4f} /kpc")
print()

# For stars, entropy gradient follows density:
# |∇S|_stars ~ |∇ln(ρ)| ~ 1/R_core (for NFW-like profile)
grad_S_stars = 1 / R_core_kpc
print(f"|∇S|_stars ~ 1/R_core: {grad_S_stars:.4f} /kpc")
print()

# But the key is: which ∇S traces MASS?
# - Gas ∇S in shock region points along shock normal (perpendicular to merger axis)
# - Stellar ∇S points toward mass centers
#
# The GEOMETRIC CORRELATION with mass distribution:
# - Stellar: cos(θ) ≈ 1 (aligned with mass gradient)
# - Gas: cos(θ) ≈ 0 in shock region (perpendicular)
#
# Effective contribution to mass-tracing:
# (contribution) ∝ |∇S| × cos(θ) × Σ

# In shocked region (where gas ∇S is misaligned):
# Volume fraction of cluster in shock-affected region
f_shocked = 0.3  # ~30% of cluster volume is post-shock mixed

# Effective gas contribution to mass-tracing gradient:
# (1 - f_shocked) × (normal contribution) + f_shocked × (reduced contribution)
alignment_factor_gas = (1 - f_shocked) * 1.0 + f_shocked * 0.1  # 0.1 = residual alignment
print(f"Shocked fraction: f_shocked = {f_shocked}")
print(f"Gas alignment factor: {alignment_factor_gas:.2f}")
print()

# w = (stellar entropy-mass coupling) / (gas entropy-mass coupling)
# Including both gradient magnitude and alignment:
coupling_stars = grad_S_stars * 1.0  # Perfect alignment
coupling_gas = grad_S_gas * alignment_factor_gas

w_derived = coupling_stars / coupling_gas
print(f"Stellar coupling: {coupling_stars:.5f}")
print(f"Gas coupling: {coupling_gas:.5f}")
print(f"DERIVED: w = {w_derived:.1f}")
print()

# =============================================================================
# DERIVATION OF L₀: ENTROPY CORRELATION LENGTH
# =============================================================================

print()
print("2. DERIVATION OF L₀")
print("-" * 50)
print()

# L₀ should be the scale over which entropy fluctuations are correlated.
#
# In a cluster, this is set by:
# 1. Turbulent cascade: largest coherent eddies
# 2. Thermal conduction: smoothing scale
# 3. Gravitational: Jeans-like scale for entropy modes
#
# The dominant one for post-merger ICM is TURBULENCE.

# Turbulent injection scale in mergers:
# Energy injected at scale ~ impact parameter ~ R_core
L_inject_kpc = R_core_kpc
print(f"Turbulent injection scale: L_inject = {L_inject_kpc} kpc")

# Turbulent cascade: energy dissipates at viscous scale
# But entropy correlations persist to injection scale
# Correlation length ≈ (0.5 - 1.0) × injection scale
L0_turb = 0.8 * L_inject_kpc
print(f"Turbulent correlation: L₀ ~ 0.8 × L_inject = {L0_turb:.0f} kpc")
print()

# Cross-check with thermal conduction scale:
# Conduction smooths temperature on scale λ_cond ~ √(κ × t)
# κ ~ (k_B T τ_ei) / m_e for electrons
# For ICM: κ ≈ 10^31 cm²/s (Spitzer, but suppressed by factor ~100 in magnetized ICM)

kappa_suppression = 100  # Magnetic suppression factor
kappa_Spitzer = 1e31 / kappa_suppression  # cm²/s
kappa_kpc2_Myr = kappa_Spitzer * (Myr_to_s / kpc_to_cm**2)

L_cond = np.sqrt(kappa_kpc2_Myr * t_since_Myr)
print(f"Conduction κ (suppressed): {kappa_Spitzer:.1e} cm²/s")
print(f"Conduction scale: L_cond = √(κt) = {L_cond:.0f} kpc")
print()

# Best estimate: turbulent scale dominates
L0_derived = L0_turb
print(f"DERIVED: L₀ = {L0_derived:.0f} kpc")
print()

# =============================================================================
# SUMMARY
# =============================================================================

print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()

w_fitted = 20
L0_fitted = 200

print(f"{'Parameter':<12} {'Derived':<12} {'Fitted':<12} {'Ratio':<10} {'Status'}")
print("-" * 60)
print(f"{'w':<12} {w_derived:<12.1f} {w_fitted:<12} {w_derived/w_fitted:<10.2f} {'✓ OK' if 0.5 < w_derived/w_fitted < 2.0 else '⚠'}")
print(f"{'L₀ (kpc)':<12} {L0_derived:<12.0f} {L0_fitted:<12} {L0_derived/L0_fitted:<10.2f} {'✓ OK' if 0.5 < L0_derived/L0_fitted < 2.0 else '⚠'}")
print()

# =============================================================================
# TESTABLE PREDICTIONS
# =============================================================================

print("=" * 70)
print("TESTABLE PREDICTIONS FOR OTHER MERGERS")
print("=" * 70)
print()

print("1. w SCALES WITH SHOCK STRENGTH AND GEOMETRY:")
print(f"   w ∝ 1 / (M² × f_shocked × alignment)")
print(f"   Weaker shocks (lower M) → smaller w")
print(f"   Face-on mergers (higher f_shocked) → larger w")
print()

print("2. L₀ SCALES WITH CORE RADIUS:")
print(f"   L₀ ≈ 0.8 × R_core")
print(f"   Larger clusters → larger L₀")
print()

print("3. SPECIFIC PREDICTIONS:")
print()

# Abell 520: "cosmic train wreck", multiple mergers
print("   Abell 520 (complex merger, R_core ~ 200 kpc):")
print(f"   → L₀ ≈ {0.8 * 200:.0f} kpc")
print(f"   → w uncertain (complex geometry)")
print()

# MACS J0025: "baby bullet", smaller/cooler
print("   MACS J0025 ('baby bullet', R_core ~ 150 kpc, M ~ 2):")
M_macs = 2.0
w_macs = w_derived * (M_shock/M_macs)**2  # Weaker shock → smaller w
print(f"   → L₀ ≈ {0.8 * 150:.0f} kpc")
print(f"   → w ≈ {w_macs:.0f} (weaker shock)")

print()
print("=" * 70)
