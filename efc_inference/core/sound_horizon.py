"""
EFC Sound Horizon — D2b: Self-Consistent Standard Ruler

Computes r_d^EFC = integral of c_s,eff(a) / (a^2 * H_eff(a)) da
from a=0 to a=a_drag, where:

    c_s,eff(a) = c_eff(a) / sqrt(3 * (1 + R_b(a)))
    c_eff(a)   = c / (1 + R(a))
    R(a)       = R_max * (rho_tot(a) / rho_tot(a_d)) * W(a)
    W(a)       = exp(-((ln a - ln a_d)^2) / (2 * sigma_ln_a^2))

EFC physics postulate (D2b-0):
    Grid resistance R(a) is proportional to normalized total energy density,
    localized to the drag epoch by a Gaussian window. This gives c_eff < c
    at high density (early times), reducing the sound horizon relative to
    the standard GR prediction.

    R_max = 0.01 (1%) is a fixed EFC constant, not a fit parameter.
    The sign R > 0 means c_eff < c: the grid is "slower" at high density.

D2a (GR-early) mode:
    Set R_max = 0.0 to recover standard GR sound horizon (consistency check).

Physical constants:
    T_CMB    = 2.7255 K (COBE/FIRAS)
    Omega_r  = derived from T_CMB via Stefan-Boltzmann
    z_drag   = Eisenstein & Hu 1998 fitting formula (function of Om_bh2, Om_mh2)

Safety:
    Three-tier verdict: PASS (|Δ| < 0.5%), WARNING (0.5% ≤ |Δ| < 1.0%), FAIL (|Δ| ≥ 1.0%).
    Safety is checked as EFC vs own GR baseline (same z_drag, same integration),
    NOT vs Planck absolute value (which depends on Boltzmann code calibration).
    At R_max = 0.01 with sigma_ln_a = 0.5, expect Δr_d depends on posterior (Ωm, H0);
    typical Δr_d ~ -0.3% to -0.7% for R_max=0.01. This is within BAO-scale tolerance
    (~1-2% measurement uncertainty) and represents a small but non-zero grid correction.

References:
    - Eisenstein & Hu (1998): https://arxiv.org/abs/astro-ph/9710252
    - Planck 2018: r_d = 147.09 +/- 0.26 Mpc
    - EFC grid resistance: theory/formal/ c_eff = (1+R)^{-1}
"""

import numpy as np
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
#  PHYSICAL CONSTANTS
# ═══════════════════════════════════════════════════════════════

C_KM_S = 299792.458           # speed of light [km/s]
C_CM_S = 2.99792458e10        # speed of light [cm/s]
T_CMB = 2.7255                # CMB temperature today [K] (COBE/FIRAS)
# Photon density parameter: Omega_gamma h^2 = 2.469e-5 (for T_CMB = 2.7255 K)
OMEGA_GAMMA_H2 = 2.469e-5
# Neutrino contribution (3 species, standard): N_eff = 3.046
N_EFF = 3.046
# Total radiation: Omega_r h^2 = Omega_gamma h^2 * (1 + 7/8 * (4/11)^{4/3} * N_eff)
OMEGA_R_H2 = OMEGA_GAMMA_H2 * (1.0 + 7.0/8.0 * (4.0/11.0)**(4.0/3.0) * N_EFF)

# EFC D2b-0 defaults (FIXED constants, NOT fit parameters)
R_MAX_DEFAULT = 0.01          # peak grid resistance (1%)
SIGMA_LN_A_DEFAULT = 0.5      # Gaussian window width in ln(a)
SAFETY_THRESHOLD_PCT = 1.0    # |Delta r_d(EFC-GR)/r_d(GR)| FAIL threshold [%]
SAFETY_WARN_PCT = 0.5         # |Delta r_d(EFC-GR)/r_d(GR)| WARNING threshold [%]

# Standard GR reference
RD_PLANCK = 147.09             # Planck 2018 [Mpc]

# Integration settings
N_INTEGRAL_STEPS = 2000        # trapezoid steps for r_d integral


# ═══════════════════════════════════════════════════════════════
#  DRAG EPOCH (Eisenstein & Hu 1998)
# ═══════════════════════════════════════════════════════════════

def compute_z_drag(Omega_m: float, h: float, Omega_b: float = 0.0493) -> float:
    """Baryon drag redshift from Eisenstein & Hu (1998) eq. 4.

    Args:
        Omega_m:  Total matter density parameter
        h:        Hubble parameter in units of 100 km/s/Mpc (H0/100)
        Omega_b:  Baryon density parameter (default: Planck 2018)

    Returns:
        z_drag:   Drag epoch redshift (~1060)
    """
    Om_h2 = Omega_m * h**2
    Ob_h2 = Omega_b * h**2

    b1 = 0.313 * Om_h2**(-0.419) * (1.0 + 0.607 * Om_h2**0.674)
    b2 = 0.238 * Om_h2**0.223
    z_d = 1291.0 * Om_h2**0.251 / (1.0 + 0.659 * Om_h2**0.828) * (
        1.0 + b1 * Ob_h2**b2
    )
    return z_d


# ═══════════════════════════════════════════════════════════════
#  EFC GRID RESISTANCE R(a)
# ═══════════════════════════════════════════════════════════════

def grid_resistance(
    a: np.ndarray,
    a_drag: float,
    Omega_m: float,
    h: float,
    R_max: float = R_MAX_DEFAULT,
    sigma_ln_a: float = SIGMA_LN_A_DEFAULT,
) -> np.ndarray:
    """EFC grid resistance R(a) — D2b-0 minimal postulate.

    R(a) = R_max * rho_tot(a) * W(a) / max(rho_tot * W)

    where:
        rho_tot(a) = Omega_r * a^{-4} + Omega_m * a^{-3}  (radiation + matter)
        W(a) = exp(-((ln a - ln a_drag)^2) / (2 sigma_ln_a^2))

    The normalization ensures max(R) = R_max exactly. The peak of rho*W
    occurs slightly before a_drag (density amplification), so R(a_drag)
    is somewhat below R_max. This is physically correct: the grid is
    slowest where the combined density-localization product peaks.

    Properties:
        - max(R) = R_max (guaranteed)
        - R -> 0 at late times (W vanishes)
        - R -> 0 at very early times (W vanishes, despite high density)
        - R is continuous and smooth

    Args:
        a:          Scale factor array
        a_drag:     Scale factor at drag epoch
        Omega_m:    Matter density
        h:          H0/100
        R_max:      Maximum grid resistance (default: 0.01)
        sigma_ln_a: Gaussian window width in ln(a) (default: 0.5)

    Returns:
        R(a):       Grid resistance at each scale factor (max = R_max)
    """
    if R_max == 0.0:
        return np.zeros_like(a)

    # Radiation density parameter
    Omega_r = OMEGA_R_H2 / h**2

    # Total energy density (radiation + matter, in units of rho_crit,0)
    rho_a = Omega_r * a**(-4) + Omega_m * a**(-3)

    # Gaussian window in ln(a) centered on drag epoch
    ln_a = np.log(np.maximum(a, 1e-30))
    ln_a_drag = np.log(a_drag)
    W = np.exp(-0.5 * ((ln_a - ln_a_drag) / sigma_ln_a)**2)

    # Product rho * W — unnormalized resistance profile
    product = rho_a * W

    # Normalize so that max(R) = R_max exactly
    # Find peak on a dense grid (product peak shifts from a_drag due to density slope)
    a_dense = np.logspace(np.log10(max(a_drag * np.exp(-3 * sigma_ln_a), 1e-10)),
                          np.log10(a_drag * np.exp(3 * sigma_ln_a)),
                          5000)
    rho_dense = Omega_r * a_dense**(-4) + Omega_m * a_dense**(-3)
    W_dense = np.exp(-0.5 * ((np.log(a_dense) - ln_a_drag) / sigma_ln_a)**2)
    peak_product = np.max(rho_dense * W_dense)

    return R_max * product / peak_product


def c_eff_over_c(
    a: np.ndarray,
    a_drag: float,
    Omega_m: float,
    h: float,
    R_max: float = R_MAX_DEFAULT,
    sigma_ln_a: float = SIGMA_LN_A_DEFAULT,
) -> np.ndarray:
    """Effective signal speed ratio c_eff(a) / c = 1 / (1 + R(a)).

    Returns:
        c_eff/c:  Array of speed ratios (< 1 when R > 0)
    """
    R = grid_resistance(a, a_drag, Omega_m, h, R_max, sigma_ln_a)
    return 1.0 / (1.0 + R)


# ═══════════════════════════════════════════════════════════════
#  BARYON-PHOTON RATIO
# ═══════════════════════════════════════════════════════════════

def baryon_photon_ratio(a: np.ndarray, Omega_b: float, h: float) -> np.ndarray:
    """Baryon-to-photon ratio R_b(a) = 3 rho_b / (4 rho_gamma).

    R_b(a) = (3 Omega_b h^2) / (4 Omega_gamma h^2) * a

    This is the standard formula, not modified by EFC (baryons and photons
    couple through Thomson scattering, which is local physics).
    """
    Ob_h2 = Omega_b * h**2
    return (3.0 * Ob_h2) / (4.0 * OMEGA_GAMMA_H2) * a


# ═══════════════════════════════════════════════════════════════
#  SOUND SPEED
# ═══════════════════════════════════════════════════════════════

def sound_speed_eff(
    a: np.ndarray,
    a_drag: float,
    Omega_m: float,
    Omega_b: float,
    h: float,
    R_max: float = R_MAX_DEFAULT,
    sigma_ln_a: float = SIGMA_LN_A_DEFAULT,
) -> np.ndarray:
    """EFC effective sound speed c_{s,eff}(a).

    c_{s,eff}(a) = c_eff(a) / sqrt(3 * (1 + R_b(a)))

    where c_eff(a) = c / (1 + R(a)) is the EFC grid-state signal speed,
    and R_b(a) is the standard baryon-photon ratio.

    Returns:
        c_s_eff in km/s
    """
    c_ratio = c_eff_over_c(a, a_drag, Omega_m, h, R_max, sigma_ln_a)
    R_b = baryon_photon_ratio(a, Omega_b, h)
    return C_KM_S * c_ratio / np.sqrt(3.0 * (1.0 + R_b))


# ═══════════════════════════════════════════════════════════════
#  HUBBLE PARAMETER IN EARLY UNIVERSE
# ═══════════════════════════════════════════════════════════════

def H_early(a: np.ndarray, Omega_m: float, h: float, H0: float) -> np.ndarray:
    """Hubble parameter including radiation for early universe.

    H(a) = H0 * sqrt(Omega_r * a^{-4} + Omega_m * a^{-3} + Omega_Lambda)

    Note: EFC gate is closed at a << a_t = 0.5, so E^2 is pure LCDM+radiation
    in the early universe. No alpha term needed here.
    """
    Omega_r = OMEGA_R_H2 / h**2
    Omega_Lambda = 1.0 - Omega_m - Omega_r
    E2 = Omega_r * a**(-4) + Omega_m * a**(-3) + Omega_Lambda
    return H0 * np.sqrt(np.maximum(E2, 1e-30))


# ═══════════════════════════════════════════════════════════════
#  COMPUTE r_d — THE EFC SOUND HORIZON
# ═══════════════════════════════════════════════════════════════

def compute_rd_efc(
    Omega_m: float,
    H0: float,
    Omega_b: float = 0.0493,
    R_max: float = R_MAX_DEFAULT,
    sigma_ln_a: float = SIGMA_LN_A_DEFAULT,
    safety_threshold_pct: float = SAFETY_THRESHOLD_PCT,
) -> Dict[str, Any]:
    """Compute EFC-native sound horizon r_d^EFC.

    r_d = integral from 0 to a_drag of c_{s,eff}(a) / (a^2 * H(a)) da

    This is the COMOVING sound horizon: the physical distance sound waves
    travel in the baryon-photon fluid from the Big Bang to the drag epoch,
    measured in today's coordinates.

    Safety is checked as |Delta r_d(EFC-GR)| / r_d(GR) against the
    threshold. This measures the EFC correction size relative to own GR
    baseline (same integration, same z_drag), which is what matters for
    scientific interpretation.

    Args:
        Omega_m:    Total matter density parameter
        H0:         Hubble constant [km/s/Mpc]
        Omega_b:    Baryon density parameter (default: 0.0493)
        R_max:      EFC peak grid resistance (default: 0.01)
        sigma_ln_a: Gaussian window width (default: 0.5)
        safety_threshold_pct: FAIL threshold |Delta r_d| in % (default: 1.0)

    Returns:
        Dict with:
            rd_efc:       r_d^EFC [Mpc]
            rd_gr:        r_d^GR  [Mpc] (R_max=0, for comparison)
            delta_rd_pct: (r_d^EFC - r_d^GR) / r_d^GR * 100 [%]
            delta_rd_vs_planck_pct: (r_d^EFC - 147.09) / 147.09 * 100 [%]
            z_drag:       Drag epoch redshift
            a_drag:       Drag epoch scale factor
            R_at_drag:    Grid resistance at drag
            R_peak:       Peak grid resistance over integration range
            c_eff_at_drag: c_eff/c at drag
            safety_pass:  True if |delta_rd(EFC-GR)| < FAIL threshold
            safety_level: "pass" | "warning" | "fail"
    """
    h = H0 / 100.0

    # Drag epoch
    z_d = compute_z_drag(Omega_m, h, Omega_b)
    a_d = 1.0 / (1.0 + z_d)

    # Integration grid: a from a_min to a_drag
    a_min = 1e-6  # well before any relevant physics
    a_grid = np.linspace(a_min, a_d, N_INTEGRAL_STEPS + 1)

    # ── EFC sound horizon (with grid resistance) ──
    cs_eff = sound_speed_eff(a_grid, a_d, Omega_m, Omega_b, h, R_max, sigma_ln_a)
    H_grid = H_early(a_grid, Omega_m, h, H0)
    integrand_efc = cs_eff / (a_grid**2 * H_grid)
    _trapz = getattr(np, 'trapezoid', None) or np.trapz
    rd_efc = float(_trapz(integrand_efc, a_grid))

    # ── GR sound horizon (R_max=0, pure standard physics) ──
    cs_gr = sound_speed_eff(a_grid, a_d, Omega_m, Omega_b, h, 0.0, sigma_ln_a)
    integrand_gr = cs_gr / (a_grid**2 * H_grid)
    rd_gr = float(_trapz(integrand_gr, a_grid))

    # ── Diagnostics ──
    R_profile = grid_resistance(a_grid, a_d, Omega_m, h, R_max, sigma_ln_a)
    R_at_drag = float(grid_resistance(
        np.array([a_d]), a_d, Omega_m, h, R_max, sigma_ln_a
    )[0])
    R_peak = float(np.max(R_profile))
    c_eff_at_drag = 1.0 / (1.0 + R_at_drag)

    delta_rd_pct = (rd_efc - rd_gr) / rd_gr * 100.0
    delta_rd_vs_planck = (rd_efc - RD_PLANCK) / RD_PLANCK * 100.0

    abs_delta = abs(delta_rd_pct)
    safety_pass = abs_delta < safety_threshold_pct  # < 1.0%
    if abs_delta < SAFETY_WARN_PCT:
        safety_level = "pass"
    elif abs_delta < safety_threshold_pct:
        safety_level = "warning"
    else:
        safety_level = "fail"

    if safety_level == "fail":
        logger.warning(
            f"D2b SAFETY FAIL: |Delta r_d(EFC-GR)| = {abs_delta:.3f}% >= "
            f"{safety_threshold_pct}% threshold! "
            f"R_max={R_max}, rd_efc={rd_efc:.4f}, rd_gr={rd_gr:.4f}"
        )
    elif safety_level == "warning":
        logger.info(
            f"D2b SAFETY WARNING: |Delta r_d(EFC-GR)| = {abs_delta:.3f}% "
            f"(>{SAFETY_WARN_PCT}%, <{safety_threshold_pct}%). "
            f"Small but non-zero grid correction — within BAO tolerance."
        )

    return {
        "rd_efc": rd_efc,
        "rd_gr": rd_gr,
        "delta_rd_pct": delta_rd_pct,
        "delta_rd_vs_planck_pct": delta_rd_vs_planck,
        "z_drag": z_d,
        "a_drag": a_d,
        "R_at_drag": R_at_drag,
        "R_peak": R_peak,
        "c_eff_at_drag": c_eff_at_drag,
        "R_max": R_max,
        "sigma_ln_a": sigma_ln_a,
        "Omega_b": Omega_b,
        "safety_pass": safety_pass,
        "safety_level": safety_level,
        "safety_threshold_pct": safety_threshold_pct,
        "safety_warn_pct": SAFETY_WARN_PCT,
    }


# ═══════════════════════════════════════════════════════════════
#  D2b SENSITIVITY SWEEP
# ═══════════════════════════════════════════════════════════════

def run_d2b_sensitivity(
    Omega_m: float = 0.315,
    H0: float = 67.4,
    Omega_b: float = 0.0493,
    R_max_values: Optional[list] = None,
) -> list:
    """Sweep R_max to map the EFC grid resistance → r_d relationship.

    Useful for understanding how sensitive r_d is to the grid state.

    Args:
        Omega_m, H0, Omega_b: Cosmological parameters
        R_max_values: List of R_max values to sweep (default: log-spaced)

    Returns:
        List of result dicts from compute_rd_efc.
    """
    if R_max_values is None:
        R_max_values = [0.0, 0.001, 0.005, 0.01, 0.02, 0.05, 0.10]

    results = []
    for R_max in R_max_values:
        result = compute_rd_efc(Omega_m, H0, Omega_b, R_max=R_max)
        results.append(result)

    return results


# ═══════════════════════════════════════════════════════════════
#  QUICK TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 65)
    print("  D2b-0: EFC Sound Horizon — Grid State Proxy")
    print("=" * 65)

    # Standard cosmology (Planck 2018)
    Om = 0.315
    H0 = 67.4
    Ob = 0.0493

    # D2a: GR baseline (R_max = 0)
    result_gr = compute_rd_efc(Om, H0, Ob, R_max=0.0)
    print(f"\nD2a (GR-early, R_max=0):")
    print(f"  z_drag   = {result_gr['z_drag']:.2f}")
    print(f"  r_d^GR   = {result_gr['rd_gr']:.4f} Mpc")
    print(f"  vs Planck: {result_gr['delta_rd_vs_planck_pct']:+.4f}%")

    # D2b-0: EFC grid state (R_max = 0.01)
    result_efc = compute_rd_efc(Om, H0, Ob, R_max=0.01)
    print(f"\nD2b-0 (EFC, R_max=0.01, peak-normalized):")
    print(f"  r_d^EFC  = {result_efc['rd_efc']:.4f} Mpc")
    print(f"  r_d^GR   = {result_efc['rd_gr']:.4f} Mpc")
    print(f"  Delta    = {result_efc['delta_rd_pct']:+.4f}%")
    print(f"  vs Planck: {result_efc['delta_rd_vs_planck_pct']:+.4f}%")
    print(f"  R(a_d)   = {result_efc['R_at_drag']:.6f}")
    print(f"  R_peak   = {result_efc['R_peak']:.6f}")
    print(f"  c_eff/c  = {result_efc['c_eff_at_drag']:.6f}")
    print(f"  Safety   = {'PASS' if result_efc['safety_pass'] else 'FAIL'} (<{result_efc['safety_threshold_pct']}%)")

    # Sensitivity sweep
    print(f"\n{'=' * 65}")
    print(f"  Sensitivity sweep: R_max → r_d")
    print(f"{'=' * 65}")
    print(f"  {'R_max':>8s}  {'r_d [Mpc]':>12s}  {'Delta vs GR':>12s}  {'vs Planck':>12s}  {'Safety':>7s}")
    print(f"  {'-'*8}  {'-'*12}  {'-'*12}  {'-'*12}  {'-'*7}")

    for r in run_d2b_sensitivity(Om, H0, Ob):
        print(f"  {r['R_max']:8.4f}  {r['rd_efc']:12.4f}  {r['delta_rd_pct']:+11.4f}%  "
              f"{r['delta_rd_vs_planck_pct']:+11.4f}%  {'PASS' if r['safety_pass'] else 'FAIL'}")
