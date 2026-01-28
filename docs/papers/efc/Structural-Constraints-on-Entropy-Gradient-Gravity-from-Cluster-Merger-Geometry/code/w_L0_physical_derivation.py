"""
PHYSICAL DERIVATION OF w AND L₀
================================

Goal: Derive the EFC parameters w (component weighting) and L₀ (non-local scale)
from first principles, WITHOUT using lensing data to fit them.

Key insight: 
- w relates to entropy PRESERVATION (collisionless) vs DISSIPATION (collisional)
- L₀ relates to entropy CORRELATION LENGTH in the system

"""

import numpy as np

# =============================================================================
# PHYSICAL CONSTANTS
# =============================================================================

k_B = 1.381e-23      # Boltzmann constant [J/K]
m_p = 1.673e-27      # Proton mass [kg]
m_e = 9.109e-31      # Electron mass [kg]
c = 2.998e8          # Speed of light [m/s]
G = 6.674e-11        # Gravitational constant [m³/kg/s²]
kpc_to_m = 3.086e19  # kpc to meters

# =============================================================================
# BULLET CLUSTER PARAMETERS (from observations)
# =============================================================================

# ICM plasma properties (from Markevitch 2006, Clowe 2006)
T_ICM = 15.5         # keV - ICM temperature
T_ICM_K = T_ICM * 1.16e7  # Convert to Kelvin (~1.8e8 K)
n_e = 3e-3           # cm⁻³ - electron density (typical ICM)
n_e_SI = n_e * 1e6   # m⁻³

# Merger properties
v_merger = 4700      # km/s - relative velocity (from shock Mach number)
v_merger_SI = v_merger * 1e3  # m/s

# Cluster properties
M_cluster = 1.5e15   # M_sun - total mass (main cluster)
R_virial = 2000      # kpc - virial radius
R_core = 250         # kpc - core radius (from X-ray)

print("=" * 70)
print("PHYSICAL DERIVATION OF EFC PARAMETERS w AND L₀")
print("=" * 70)
print()

# =============================================================================
# DERIVATION 1: w FROM ENTROPY DISSIPATION TIMESCALES
# =============================================================================

print("1. DERIVATION OF w (component weighting)")
print("-" * 50)
print()

# Key idea: w = τ_dissipation(gas) / τ_dissipation(stars)
# 
# For collisional gas: entropy dissipates on Coulomb collision timescale
# For collisionless stars: entropy preserved (τ → ∞ effectively)
#
# But we need a finite ratio. Use:
# w = τ_crossing / τ_collision
# where τ_crossing is the cluster crossing time

# Coulomb collision time for ICM plasma
# τ_ee ≈ 3.5e5 * T^(3/2) / (n_e * ln(Λ)) years
# where T in keV, n_e in cm⁻³, ln(Λ) ≈ 40 for ICM

ln_Lambda = 40  # Coulomb logarithm for ICM
tau_coulomb_yr = 3.5e5 * (T_ICM ** 1.5) / (n_e * ln_Lambda)
tau_coulomb_Myr = tau_coulomb_yr / 1e6

print(f"ICM temperature: T = {T_ICM} keV")
print(f"Electron density: n_e = {n_e} cm⁻³")
print(f"Coulomb logarithm: ln(Λ) = {ln_Lambda}")
print(f"Coulomb collision time: τ_Coulomb = {tau_coulomb_Myr:.1f} Myr")
print()

# Cluster crossing time
tau_crossing_Myr = (R_virial * kpc_to_m / 1e3) / (v_merger_SI) / (3.15e13)  # in Myr
print(f"Merger velocity: v = {v_merger} km/s")
print(f"Virial radius: R = {R_virial} kpc")
print(f"Crossing time: τ_cross = {tau_crossing_Myr:.1f} Myr")
print()

# However, the relevant comparison for ENTROPY is:
# - Gas: thermalizes on τ_Coulomb (loses memory of pre-merger state)
# - Stars: never thermalize (preserve pre-merger phase space)
#
# During merger, gas has time to "forget" its entropy structure if:
# τ_merger ~ τ_Coulomb
#
# The ratio w should reflect how much MORE the stellar component
# preserves its entropy gradient structure compared to gas.

# Simple model: w = (effective entropy preservation factor)
# 
# For gas during merger: entropy is PRODUCED (shock heating) and MIXED
# Net effect: original gradient structure is smoothed/destroyed
# Preservation factor ≈ exp(-t_merger / τ_thermal_mixing)
#
# For stars: entropy structure preserved
# Preservation factor ≈ 1

# Thermal mixing timescale (conduction + turbulent mixing)
# In post-shock ICM, turbulent mixing dominates
# τ_mix ≈ L_eddy / v_turb ≈ 100 kpc / 500 km/s ≈ 200 Myr

L_eddy_kpc = 100  # typical turbulent eddy scale
v_turb_km_s = 500  # post-shock turbulence
tau_mix_Myr = (L_eddy_kpc * kpc_to_m / 1e3) / (v_turb_km_s * 1e3) / 3.15e13

print(f"Turbulent eddy scale: L_eddy = {L_eddy_kpc} kpc")
print(f"Turbulent velocity: v_turb = {v_turb_km_s} km/s")
print(f"Mixing timescale: τ_mix = {tau_mix_Myr:.1f} Myr")
print()

# Time since collision (Bullet Cluster)
t_since_collision_Myr = 150  # ~150 Myr since core passage

# Gas entropy preservation factor
f_gas = np.exp(-t_since_collision_Myr / tau_mix_Myr)
print(f"Time since collision: t = {t_since_collision_Myr} Myr")
print(f"Gas entropy preservation: f_gas = exp(-t/τ_mix) = {f_gas:.3f}")
print()

# Stellar entropy preservation factor
f_stars = 1.0  # Perfect preservation (collisionless)

# w = ratio of preservation factors
# But this gives w → ∞, which isn't useful.
#
# Better model: w reflects the RELATIVE WEIGHT in producing G_eff
# If gas contributes proportional to f_gas and stars to f_stars:
# 
# Effective: G_eff ∝ f_gas * Σ_gas + f_stars * Σ_stellar
#          = f_gas * (Σ_gas + (f_stars/f_gas) * Σ_stellar)
#          = f_gas * (Σ_gas + w * Σ_stellar)
#
# So: w = f_stars / f_gas = 1 / f_gas

w_derived = f_stars / f_gas
print(f"DERIVED: w = f_stars / f_gas = {w_derived:.1f}")
print()

# Compare to fitted value
w_fitted = 20
print(f"FITTED VALUE: w = {w_fitted}")
print(f"RATIO (derived/fitted): {w_derived / w_fitted:.2f}")
print()

# =============================================================================
# DERIVATION 2: L₀ FROM ENTROPY CORRELATION LENGTH
# =============================================================================

print()
print("2. DERIVATION OF L₀ (non-local scale)")
print("-" * 50)
print()

# Key idea: L₀ is the scale over which entropy gradients are correlated
# This should relate to a physical length scale in the cluster.
#
# Candidates:
# 1. Turbulent injection scale (largest eddies)
# 2. Sound horizon (acoustic correlation)
# 3. Cooling radius
# 4. Core radius

# Option A: Turbulent injection scale
# In cluster mergers, turbulence is injected at scale ~ R_core to R_virial/2
L0_turb = R_core  # ~250 kpc - matches turbulent cascade injection
print(f"Option A - Turbulent injection scale: L₀ = {L0_turb} kpc")

# Option B: Sound crossing scale during merger
# How far does a sound wave travel in the dynamical time?
c_s = np.sqrt(5/3 * k_B * T_ICM_K / m_p)  # isothermal sound speed
c_s_km_s = c_s / 1e3
tau_dyn_Myr = tau_crossing_Myr
L0_sound = c_s_km_s * tau_dyn_Myr * 3.15e13 / kpc_to_m * 1e3  # in kpc
print(f"Sound speed: c_s = {c_s_km_s:.0f} km/s")
print(f"Option B - Sound horizon: L₀ = c_s × τ_dyn = {L0_sound:.0f} kpc")

# Option C: Entropy gradient correlation length from ICM properties
# From simulations: entropy fluctuations decorrelate on scale ~ R_core
L0_entropy = R_core  # ~250 kpc
print(f"Option C - Entropy correlation (empirical): L₀ ~ R_core = {L0_entropy} kpc")

# Option D: Jeans-like scale for entropy perturbations
# λ_J ∝ c_s / sqrt(G * ρ)
rho_ICM = n_e_SI * m_p * 1.17  # mean molecular weight ~1.17 for ionized H+He
lambda_J = c_s / np.sqrt(G * rho_ICM)
lambda_J_kpc = lambda_J / kpc_to_m
print(f"Option D - Entropy Jeans scale: λ_J = {lambda_J_kpc:.0f} kpc")

print()

# Best estimate: geometric mean of physically motivated scales
L0_derived = np.sqrt(L0_turb * L0_sound)
print(f"DERIVED (geometric mean): L₀ = √(L_turb × L_sound) = {L0_derived:.0f} kpc")
print()

# Compare to fitted value
L0_fitted = 200
print(f"FITTED VALUE: L₀ = {L0_fitted} kpc")
print(f"RATIO (derived/fitted): {L0_derived / L0_fitted:.2f}")

# =============================================================================
# SUMMARY
# =============================================================================

print()
print("=" * 70)
print("SUMMARY: PHYSICALLY DERIVED vs FITTED PARAMETERS")
print("=" * 70)
print()
print(f"{'Parameter':<15} {'Derived':<15} {'Fitted':<15} {'Ratio':<10}")
print("-" * 55)
print(f"{'w':<15} {w_derived:<15.1f} {w_fitted:<15} {w_derived/w_fitted:<10.2f}")
print(f"{'L₀ (kpc)':<15} {L0_derived:<15.0f} {L0_fitted:<15} {L0_derived/L0_fitted:<10.2f}")
print()

# Agreement assessment
if 0.5 < w_derived/w_fitted < 2.0 and 0.5 < L0_derived/L0_fitted < 2.0:
    print("✓ BOTH parameters within factor 2 of fitted values!")
    print("  This suggests the physical derivation is on the right track.")
else:
    print("⚠ Parameters differ by more than factor 2")
    print("  Physical model may need refinement.")

print()
print("=" * 70)
print("TESTABLE PREDICTIONS")
print("=" * 70)
print()
print("If this derivation is correct, then for OTHER cluster mergers:")
print()
print("1. w should scale as: w ∝ exp(t_since_collision / τ_mix)")
print(f"   Prediction: Older mergers have LARGER w")
print()
print("2. L₀ should scale as: L₀ ∝ √(R_core × c_s × τ_dyn)")
print(f"   Prediction: Hotter clusters have LARGER L₀")
print()
print("3. For a 'fresh' merger (t → 0): w → 1 (gas and stars equal)")
print(f"   For Bullet Cluster (t = {t_since_collision_Myr} Myr): w ≈ {w_derived:.0f}")
print()
print("These are TESTABLE on Abell 520 (older merger) and MACS J0025.")
