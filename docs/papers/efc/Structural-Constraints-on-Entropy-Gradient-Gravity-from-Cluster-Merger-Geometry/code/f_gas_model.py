"""
f_gas(M,t) MODEL - Entropy Gradient Survival Fraction
======================================================

Minimal physical model with 1 global parameter (η)

f_gas(M,t) = g_shock(M) × g_mix(t)
           = (1/r(M)) × exp(-t × σ_v / (η × L₀))

w(M,t) = 1 / f_gas(M,t) = r(M) × exp(t × σ_v / (η × L₀))

"""

import numpy as np

# =============================================================================
# RANKINE-HUGONIOT COMPRESSION RATIO
# =============================================================================

def compression_ratio(M, gamma=5/3):
    """
    Rankine-Hugoniot compression ratio for shock with Mach number M.
    
    r(M) = (γ+1)M² / ((γ-1)M² + 2)
    
    For γ=5/3:
      M=1: r=1 (no shock)
      M=2: r=2.29
      M=3: r=3.0
      M→∞: r=4 (strong shock limit)
    """
    return (gamma + 1) * M**2 / ((gamma - 1) * M**2 + 2)


def g_shock(M):
    """Shock term: coherent gradient signal reduced by compression."""
    return 1.0 / compression_ratio(M)


def g_mix(t_Myr, sigma_v_km_s, L0_kpc, eta):
    """
    Mixing term: exponential decay of gradient coherence.
    
    g_mix = exp(-t × σ_v / (η × L₀))
    
    τ_mix = η × L₀ / σ_v
    """
    # Convert units: t in Myr, σ_v in km/s, L₀ in kpc
    # τ_mix = η × L₀ / σ_v [in Myr]
    # L₀ [kpc] / σ_v [km/s] = L₀ × 3.086e16 [km] / σ_v [km/s] / 3.15e13 [s/Myr]
    # = L₀ × 3.086e16 / σ_v / 3.15e13 Myr
    # = L₀ × 0.98 / σ_v Myr
    # ≈ L₀ / σ_v Myr (for σ_v in km/s, L₀ in kpc)
    
    tau_mix = eta * L0_kpc / sigma_v_km_s  # in Myr (approximate)
    return np.exp(-t_Myr / tau_mix)


def f_gas(M, t_Myr, sigma_v_km_s, L0_kpc, eta):
    """Full entropy gradient survival fraction."""
    return g_shock(M) * g_mix(t_Myr, sigma_v_km_s, L0_kpc, eta)


def w_from_physics(M, t_Myr, sigma_v_km_s, L0_kpc, eta):
    """Component weighting w = 1 / f_gas."""
    return 1.0 / f_gas(M, t_Myr, sigma_v_km_s, L0_kpc, eta)


# =============================================================================
# BULLET CLUSTER PARAMETERS
# =============================================================================

print("=" * 70)
print("f_gas(M,t) MODEL: CALIBRATION ON BULLET CLUSTER")
print("=" * 70)
print()

# Measured/estimated parameters for Bullet Cluster
M_bullet = 3.0          # Mach number (from Markevitch+ 2006)
t_bullet = 150          # Myr since core passage (estimated)
sigma_v_bullet = 500    # km/s turbulent velocity (typical post-merger)
L0_bullet = 200         # kpc (from our hypothesis L₀ ≈ 0.8 × R_core)

print("BULLET CLUSTER INPUTS (measured/estimated):")
print(f"  Mach number: M = {M_bullet}")
print(f"  Time since collision: t = {t_bullet} Myr")
print(f"  Turbulent velocity: σ_v = {sigma_v_bullet} km/s")
print(f"  Non-local scale: L₀ = {L0_bullet} kpc")
print()

# Compression ratio
r_bullet = compression_ratio(M_bullet)
print(f"  Compression ratio: r(M) = {r_bullet:.2f}")
print(f"  Shock term: g_shock = 1/r = {g_shock(M_bullet):.3f}")
print()

# Target w from fitting
w_target = 20

# Solve for η
# w = r(M) × exp(t × σ_v / (η × L₀))
# ln(w) = ln(r) + t × σ_v / (η × L₀)
# η = t × σ_v / (L₀ × (ln(w) - ln(r)))

ln_w = np.log(w_target)
ln_r = np.log(r_bullet)
eta_calibrated = t_bullet * sigma_v_bullet / (L0_bullet * (ln_w - ln_r))

print(f"CALIBRATION:")
print(f"  Target w = {w_target}")
print(f"  ln(w) = {ln_w:.3f}")
print(f"  ln(r) = {ln_r:.3f}")
print(f"  Solving: η = t × σ_v / (L₀ × (ln(w) - ln(r)))")
print(f"  η = {t_bullet} × {sigma_v_bullet} / ({L0_bullet} × ({ln_w:.3f} - {ln_r:.3f}))")
print(f"  CALIBRATED: η = {eta_calibrated:.2f}")
print()

# Verify
w_check = w_from_physics(M_bullet, t_bullet, sigma_v_bullet, L0_bullet, eta_calibrated)
print(f"  Verification: w(M={M_bullet}, t={t_bullet}, η={eta_calibrated:.2f}) = {w_check:.1f}")
print()

# Physical interpretation of η
tau_mix = eta_calibrated * L0_bullet / sigma_v_bullet
print(f"  Mixing timescale: τ_mix = η × L₀ / σ_v = {tau_mix:.0f} Myr")
print()

# =============================================================================
# PREDICTIONS FOR OTHER MERGERS
# =============================================================================

print("=" * 70)
print("PREDICTIONS FOR OTHER MERGERS (η = {:.2f} fixed)".format(eta_calibrated))
print("=" * 70)
print()

# Use SAME η for all clusters

# Abell 520 - "Cosmic Train Wreck"
# Multiple merger, complex geometry
# Rough estimates from literature
M_a520 = 2.5            # Weaker shock (estimated)
t_a520 = 300            # Myr - older merger
sigma_v_a520 = 600      # km/s - more turbulence (complex merger)
R_core_a520 = 200       # kpc
L0_a520 = 0.8 * R_core_a520

w_a520 = w_from_physics(M_a520, t_a520, sigma_v_a520, L0_a520, eta_calibrated)
r_a520 = compression_ratio(M_a520)

print("ABELL 520 ('Cosmic Train Wreck'):")
print(f"  Inputs: M={M_a520}, t={t_a520} Myr, σ_v={sigma_v_a520} km/s")
print(f"  L₀ = 0.8 × R_core = 0.8 × {R_core_a520} = {L0_a520:.0f} kpc")
print(f"  r(M) = {r_a520:.2f}")
print(f"  PREDICTED: w = {w_a520:.0f}")
print()

# MACS J0025 - "Baby Bullet"
# Smaller, cooler, weaker shock
M_macs = 2.0            # Weaker shock
t_macs = 100            # Myr - younger merger
sigma_v_macs = 400      # km/s - less turbulence
R_core_macs = 150       # kpc - smaller cluster
L0_macs = 0.8 * R_core_macs

w_macs = w_from_physics(M_macs, t_macs, sigma_v_macs, L0_macs, eta_calibrated)
r_macs = compression_ratio(M_macs)

print("MACS J0025 ('Baby Bullet'):")
print(f"  Inputs: M={M_macs}, t={t_macs} Myr, σ_v={sigma_v_macs} km/s")
print(f"  L₀ = 0.8 × R_core = 0.8 × {R_core_macs} = {L0_macs:.0f} kpc")
print(f"  r(M) = {r_macs:.2f}")
print(f"  PREDICTED: w = {w_macs:.0f}")
print()

# Fresh merger (hypothetical)
M_fresh = 3.0
t_fresh = 10            # Myr - very recent
sigma_v_fresh = 500
L0_fresh = 200

w_fresh = w_from_physics(M_fresh, t_fresh, sigma_v_fresh, L0_fresh, eta_calibrated)

print("FRESH MERGER (hypothetical, t=10 Myr):")
print(f"  Inputs: M={M_fresh}, t={t_fresh} Myr")
print(f"  PREDICTED: w = {w_fresh:.1f}")
print(f"  (Approaches w→r(M)={compression_ratio(M_fresh):.1f} as t→0)")
print()

# =============================================================================
# SUMMARY TABLE
# =============================================================================

print("=" * 70)
print("SUMMARY: PREDICTIONS WITH η = {:.2f}".format(eta_calibrated))
print("=" * 70)
print()
print(f"{'Cluster':<20} {'M':<6} {'t(Myr)':<8} {'L₀(kpc)':<10} {'w_pred':<10} {'Status'}")
print("-" * 70)
print(f"{'Bullet (calibration)':<20} {M_bullet:<6} {t_bullet:<8} {L0_bullet:<10} {w_target:<10} {'← fitted'}")
print(f"{'Abell 520':<20} {M_a520:<6} {t_a520:<8} {L0_a520:<10.0f} {w_a520:<10.0f} {'prediction'}")
print(f"{'MACS J0025':<20} {M_macs:<6} {t_macs:<8} {L0_macs:<10.0f} {w_macs:<10.0f} {'prediction'}")
print(f"{'Fresh (t=10 Myr)':<20} {M_fresh:<6} {t_fresh:<8} {L0_fresh:<10} {w_fresh:<10.1f} {'limit check'}")
print()

print("=" * 70)
print("MODEL EQUATIONS")
print("=" * 70)
print()
print("r(M) = (γ+1)M² / ((γ-1)M² + 2)     [γ = 5/3]")
print()
print("f_gas(M,t) = (1/r(M)) × exp(-t × σ_v / (η × L₀))")
print()
print("w(M,t) = r(M) × exp(t × σ_v / (η × L₀))")
print()
print(f"Global parameter: η = {eta_calibrated:.2f}")
print()
print("Inputs per cluster: M (Mach), t (Myr), σ_v (km/s), L₀ (kpc)")
