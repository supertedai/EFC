#!/usr/bin/env python3
"""
EFC Phase 2.4 — Joint Likelihood with CMB Distance Prior
=========================================================
Upgrades from Phase 2.2:
  1. CMB compressed likelihood (R, l_A, omega_b) with full 3x3 covariance
  2. H0 is FREE (not fixed) — required for honest CMB test
  3. 3D grid scan over (A, Omega_m, H0) + 1D profile likelihoods
  4. LCDM limit verification (A→0)
  5. BAO uses both D_M/r_d and D_H/r_d (anisotropic)
Planck 2018 compressed distance prior: TT,TE,EE+lowE
  R      = 1.74963
  l_A    = 301.80845
  omega_b = 0.02237
  z_*    = 1089.92
Author: Morten Magnusson
Date: 2026-02-12
Ref: EFC Appendix X — CMB Distance Prior Test (Phase 2.4)
"""
import numpy as np
from scipy.integrate import quad
from scipy.integrate import solve_ivp
from scipy.optimize import minimize
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
import time
# ============================================================
# 1. CONSTANTS AND MODEL
# ============================================================
Omega_r = 9.15e-5
n_gate = 6
c_km_s = 299792.458  # km/s

def g_gate(a, a_t, n=n_gate):
    return 1.0 / (1.0 + (a_t / a)**n)

def dg_dlna(a, a_t, n=n_gate):
    gg = g_gate(a, a_t, n)
    return n * gg * (1.0 - gg)

class EFCModel:
    """EFC cosmological model with proper normalisation."""

    def __init__(self, A, z_L1L2, Omega_m, H0, sigma8_0):
        self.A = A
        self.z_L1L2 = z_L1L2
        self.a_t = 1.0 / (1.0 + z_L1L2)
        self.Omega_m = Omega_m
        self.H0 = H0
        self.h = H0 / 100.0
        self.sigma8_0 = sigma8_0

        # Normalisation: E(a=1) = 1  →  Ω_Λ = 1 - Ω_m - Ω_r - A·g(1)
        self.Omega_L = 1.0 - Omega_m - Omega_r - A * g_gate(1.0, self.a_t)

    def E2(self, a):
        """E²(a) = H²(a)/H₀²"""
        return (Omega_r * a**(-4) + self.Omega_m * a**(-3)
                + self.Omega_L + self.A * g_gate(a, self.a_t))

    def E(self, a):
        e2 = self.E2(a)
        if e2 <= 0:
            return 1e10
        return np.sqrt(e2)

    def E_of_z(self, z):
        return self.E(1.0 / (1.0 + z))

    def H(self, z):
        """H(z) in km/s/Mpc"""
        return self.H0 * self.E_of_z(z)

    def EpE(self, a):
        """E'/E = (1/2E²) dE²/dlna"""
        e2 = self.E2(a)
        if e2 <= 0:
            return 0.0
        de2 = (-4*Omega_r*a**(-4) - 3*self.Omega_m*a**(-3)
               + self.A * dg_dlna(a, self.a_t))
        return 0.5 * de2 / e2

    def Om_tilde(self, a):
        """Effective Ω̃_m(a) = Ω_m a⁻³ / E²(a)"""
        e2 = self.E2(a)
        if e2 <= 0:
            return 0.0
        return self.Omega_m * a**(-3) / e2

    # --- Distances ---

    def D_C(self, z):
        """Comoving distance D_C(z) in Mpc (flat)."""
        def integrand(zp):
            return 1.0 / self.E_of_z(zp)
        result, _ = quad(integrand, 0, z, limit=200)
        return (c_km_s / self.H0) * result

    def D_M(self, z):
        """Transverse comoving distance (= D_C for flat)."""
        return self.D_C(z)

    def D_H(self, z):
        """Hubble distance D_H(z) = c/H(z) in Mpc."""
        return c_km_s / self.H(z)

    def d_L(self, z):
        """Luminosity distance in Mpc."""
        return (1.0 + z) * self.D_M(z)

    def mu(self, z):
        """Distance modulus."""
        dl = self.d_L(z)
        if dl <= 0:
            return 99.0
        return 5.0 * np.log10(dl) + 25.0

    # --- CMB distance observables ---

    def R_shift(self, z_star):
        """Shift parameter R = sqrt(Omega_m * H0^2) * D_M(z*) / c"""
        return np.sqrt(self.Omega_m) * self.H0 * self.D_M(z_star) / c_km_s

    def ell_A(self, z_star, r_s):
        """Acoustic angular scale l_A = pi * D_M(z*) / r_s(z*)"""
        return np.pi * self.D_M(z_star) / r_s

    # --- Growth ---

    def solve_growth(self, z_init=50, n_points=1500):
        """Solve f-ODE. Returns (a_arr, D_norm, f_arr)."""
        a_init = 1.0 / (1.0 + z_init)
        lna_eval = np.linspace(np.log(a_init), 0.0, n_points)

        def ode(lna, state):
            lnD, f = state
            a = np.exp(lna)
            ee = self.EpE(a)
            om = self.Om_tilde(a)
            return [f, -(2.0 + ee)*f - f**2 + 1.5*om]

        sol = solve_ivp(ode, [np.log(a_init), 0.0], [np.log(a_init), 1.0],
                        t_eval=lna_eval, method='RK45', rtol=1e-9, atol=1e-11,
                        max_step=0.02)

        if sol.status != 0:
            return None, None, None

        a_arr = np.exp(sol.t)
        D_arr = np.exp(sol.y[0])
        D_norm = D_arr / D_arr[-1]
        f_arr = sol.y[1]
        return a_arr, D_norm, f_arr

    def fsigma8(self, z_arr):
        """Compute fσ8 at given redshifts."""
        a_sol, D_sol, f_sol = self.solve_growth()
        if a_sol is None:
            return np.full_like(z_arr, 99.0, dtype=float)

        z_sol = 1.0/a_sol - 1.0
        idx = np.argsort(z_sol)
        z_s, D_s, f_s = z_sol[idx], D_sol[idx], f_sol[idx]

        D_interp = np.interp(z_arr, z_s, D_s)
        f_interp = np.interp(z_arr, z_s, f_s)

        return f_interp * self.sigma8_0 * D_interp

# ============================================================
# 2. DATA
# ============================================================

# --- Sound horizon (Planck 2018, fixed — Level 1 treatment) ---
r_d = 147.09   # Mpc (BAO, at z_drag)
# r_s at z_* calibrated so LCDM(Om=0.3153,H0=67.36) reproduces l_A=301.808
r_s_star = 144.35  # Mpc (CMB, at z_* — calibrated to Planck compressed prior)

# Planck 2018 best-fit reference (for LCDM baseline)
Om_planck = 0.3153
H0_planck = 67.36

# --- Planck 2018 CMB compressed distance prior (TT,TE,EE+lowE) ---
z_star = 1089.92
cmb_obs = np.array([1.74963, 301.80845, 0.02237])  # (R, l_A, omega_b)
cmb_cov = np.array([
    [2.124e-7,  1.798e-6,  -3.058e-8],
    [1.798e-6,  2.033e-4,  -1.443e-6],
    [-3.058e-8, -1.443e-6,  2.930e-8],
])
cmb_cov_inv = np.linalg.inv(cmb_cov)

# --- BAO: DESI DR2-like (D_M/r_d and D_H/r_d) ---
bao_data = [
    (0.30, 'DM',  8.44, 0.18),
    (0.30, 'DH', 26.15, 0.50),
    (0.51, 'DM', 13.55, 0.20),
    (0.51, 'DH', 23.20, 0.42),
    (0.71, 'DM', 17.86, 0.28),
    (0.71, 'DH', 20.50, 0.42),
    (0.93, 'DM', 22.00, 0.38),
    (0.93, 'DH', 17.70, 0.38),
]

# --- Cosmic Chronometers ---
cc_data = np.array([
    [0.070, 69.0,  19.6], [0.090, 69.0,  12.0], [0.120, 68.6,  26.2],
    [0.170, 83.0,   8.0], [0.179, 75.0,   4.0], [0.199, 75.0,   5.0],
    [0.200, 72.9,  29.6], [0.270, 77.0,  14.0], [0.280, 88.8,  36.6],
    [0.352, 83.0,  14.0], [0.400, 95.0,  17.0], [0.440, 82.6,   7.8],
    [0.480, 97.0,  62.0], [0.593, 104.0,  13.0], [0.680, 92.0,   8.0],
    [0.781, 105.0,  12.0], [0.875, 125.0,  17.0], [0.880, 90.0,  40.0],
    [0.900, 117.0,  23.0], [1.037, 154.0,  20.0], [1.300, 168.0,  17.0],
    [1.363, 160.0,  33.6], [1.430, 177.0,  18.0], [1.530, 140.0,  14.0],
    [1.750, 202.0,  40.0], [1.965, 186.5,  50.4],
])

# --- RSD: BOSS DR12 consensus ---
rsd_z = np.array([0.38, 0.51, 0.61])
rsd_fs8 = np.array([0.497, 0.458, 0.436])
rsd_err = np.array([0.045, 0.038, 0.034])
rsd_corr = np.array([
    [1.000, 0.369, 0.120],
    [0.369, 1.000, 0.457],
    [0.120, 0.457, 1.000],
])
rsd_cov = np.outer(rsd_err, rsd_err) * rsd_corr
rsd_cov_inv = np.linalg.inv(rsd_cov)

# ============================================================
# 3. LIKELIHOODS
# ============================================================

def logL_BAO(model):
    """BAO log-likelihood (D_M/r_d and D_H/r_d, diagonal)."""
    chi2 = 0.0
    for (z, obs_type, val, err) in bao_data:
        if obs_type == 'DM':
            pred = model.D_M(z) / r_d
        elif obs_type == 'DH':
            pred = model.D_H(z) / r_d
        else:
            continue
        chi2 += ((val - pred) / err)**2
    return -0.5 * chi2

def logL_CC(model):
    """Cosmic chronometers log-likelihood (diagonal)."""
    chi2 = 0.0
    for i in range(len(cc_data)):
        z, H_obs, H_err = cc_data[i]
        chi2 += ((H_obs - model.H(z)) / H_err)**2
    return -0.5 * chi2

def logL_RSD(model):
    """RSD log-likelihood with covariance (BOSS DR12)."""
    fs8_pred = model.fsigma8(rsd_z)
    delta = rsd_fs8 - fs8_pred
    return -0.5 * delta @ rsd_cov_inv @ delta

def logL_CMB(model, omega_b=0.02237):
    """
    CMB compressed distance prior (Planck 2018).

    Uses full 3x3 covariance over (R, l_A, omega_b).
    omega_b is treated as a nuisance parameter with the
    observed Planck value (Level 1: r_s fixed).
    """
    R_pred = model.R_shift(z_star)
    lA_pred = model.ell_A(z_star, r_s_star)

    pred = np.array([R_pred, lA_pred, omega_b])
    delta = pred - cmb_obs
    chi2 = delta @ cmb_cov_inv @ delta
    return -0.5 * chi2

def logL_lowz(model):
    """BAO + CC + RSD (no CMB)."""
    return logL_BAO(model) + logL_CC(model) + logL_RSD(model)

def logL_total(model, omega_b=0.02237):
    """Full joint: BAO + CC + RSD + CMB distance prior."""
    return logL_lowz(model) + logL_CMB(model, omega_b)

# ============================================================
# 4. PRIORS (symmetric — A can be negative)
# ============================================================

def log_prior(A, z_L1L2, Omega_m, H0, sigma8_0):
    """Flat priors with physical bounds."""
    if not (-0.5 <= A <= 0.5):
        return -np.inf
    if not (0.3 <= z_L1L2 <= 2.5):
        return -np.inf
    if not (0.20 <= Omega_m <= 0.45):
        return -np.inf
    if not (55.0 <= H0 <= 80.0):
        return -np.inf
    if not (0.6 <= sigma8_0 <= 1.0):
        return -np.inf
    return 0.0

# ============================================================
# 5. PROFILE LIKELIHOOD SCANNER
# ============================================================

def profile_scan_A(A_vals, fixed_z_L1L2, fixed_sigma8_0,
                   likelihood_fn, label="", Om_range=(0.25, 0.40),
                   H0_range=(60.0, 76.0), n_Om=20, n_H0=15):
    """
    Profile likelihood over A, maximising over (Omega_m, H0) at each A.
    Returns logL_profile array.
    """
    Om_grid = np.linspace(*Om_range, n_Om)
    H0_grid = np.linspace(*H0_range, n_H0)
    logL_profile = np.full_like(A_vals, -np.inf)

    for i, A in enumerate(A_vals):
        best = -np.inf
        for Om in Om_grid:
            for H0 in H0_grid:
                lp = log_prior(A, fixed_z_L1L2, Om, H0, fixed_sigma8_0)
                if np.isinf(lp):
                    continue
                try:
                    model = EFCModel(A=A, z_L1L2=fixed_z_L1L2,
                                     Omega_m=Om, H0=H0,
                                     sigma8_0=fixed_sigma8_0)
                    if model.Omega_L < 0:
                        continue
                    ll = likelihood_fn(model)
                    if ll > best:
                        best = ll
                except:
                    continue
        logL_profile[i] = best
        if (i+1) % 10 == 0:
            print(f"    {label} A-scan: {i+1}/{len(A_vals)}")

    return logL_profile

def find_best_3D(A_range, Om_range, H0_range, fixed_z_L1L2, fixed_sigma8_0,
                 likelihood_fn, nA=40, nOm=30, nH0=20):
    """
    Brute 3D grid to find global best-fit (A, Om, H0).
    """
    best_ll = -np.inf
    best_params = {}

    for A in np.linspace(*A_range, nA):
        for Om in np.linspace(*Om_range, nOm):
            for H0 in np.linspace(*H0_range, nH0):
                lp = log_prior(A, fixed_z_L1L2, Om, H0, fixed_sigma8_0)
                if np.isinf(lp):
                    continue
                try:
                    model = EFCModel(A=A, z_L1L2=fixed_z_L1L2,
                                     Omega_m=Om, H0=H0,
                                     sigma8_0=fixed_sigma8_0)
                    if model.Omega_L < 0:
                        continue
                    ll = likelihood_fn(model)
                    if ll > best_ll:
                        best_ll = ll
                        best_params = {'A': A, 'Omega_m': Om, 'H0': H0}
                except:
                    continue

    return best_ll, best_params

# ============================================================
# 6. MAIN ANALYSIS
# ============================================================

def main():
    t0 = time.time()
    print("=" * 65)
    print("EFC PHASE 2.4 — JOINT LIKELIHOOD + CMB DISTANCE PRIOR")
    print("=" * 65)

    z_L1L2_fix = 1.01
    sigma8_fix = 0.811

    # --- ΛCDM verification ---
    print("\n--- ΛCDM Limit Verification ---")
    lcdm = EFCModel(A=0.0, z_L1L2=z_L1L2_fix, Omega_m=Om_planck,
                    H0=H0_planck, sigma8_0=sigma8_fix)
    print(f"  E(a=1) = {lcdm.E(1.0):.8f}  (should be 1.0)")
    print(f"  Omega_L = {lcdm.Omega_L:.6f}")
    print(f"  R(z*) = {lcdm.R_shift(z_star):.5f}  (Planck: 1.74963)")
    print(f"  l_A(z*) = {lcdm.ell_A(z_star, r_s_star):.3f}  (Planck: 301.808)")

    # --- Reference log-likelihoods ---
    print(f"\n--- Reference Log-Likelihoods (Planck: Om={Om_planck}, H0={H0_planck}) ---")
    refs = [
        ("LCDM(Planck)", EFCModel(A=0.0, z_L1L2=z_L1L2_fix, Omega_m=Om_planck,
                           H0=H0_planck, sigma8_0=sigma8_fix)),
        ("EFC(A=+0.05)", EFCModel(A=0.05, z_L1L2=z_L1L2_fix, Omega_m=Om_planck,
                                   H0=H0_planck, sigma8_0=sigma8_fix)),
        ("EFC(A=-0.10)", EFCModel(A=-0.10, z_L1L2=z_L1L2_fix, Omega_m=Om_planck,
                                   H0=H0_planck, sigma8_0=sigma8_fix)),
        ("EFC(A=-0.25)", EFCModel(A=-0.25, z_L1L2=z_L1L2_fix, Omega_m=Om_planck,
                                   H0=H0_planck, sigma8_0=sigma8_fix)),
    ]
    print(f"  {'Model':18s} {'BAO':>8s} {'CC':>8s} {'RSD':>8s} "
          f"{'CMB':>8s} {'Total':>8s}")
    for name, m in refs:
        lb = logL_BAO(m); lc = logL_CC(m); lr = logL_RSD(m)
        lcmb = logL_CMB(m); lt = lb + lc + lr + lcmb
        print(f"  {name:18s} {-2*lb:8.1f} {-2*lc:8.1f} {-2*lr:8.1f} "
              f"{-2*lcmb:8.1f} {-2*lt:8.1f}")

    # --- 1D Profile Likelihood: A (profiling over Om, H0) ---
    print("\n--- 1D Profile Likelihood on A (profiling Om, H0) ---")
    A_vals = np.linspace(-0.4, 0.3, 50)

    print("  Scanning: low-z only (BAO+CC+RSD)...")
    pL_lowz = profile_scan_A(A_vals, z_L1L2_fix, sigma8_fix,
                              logL_lowz, label="lowz")

    print("  Scanning: CMB only...")
    pL_cmb = profile_scan_A(A_vals, z_L1L2_fix, sigma8_fix,
                             logL_CMB, label="CMB")

    print("  Scanning: joint (BAO+CC+RSD+CMB)...")
    pL_joint = profile_scan_A(A_vals, z_L1L2_fix, sigma8_fix,
                               logL_total, label="joint")

    # Δχ² relative to best
    dchi2_lowz = -2*(pL_lowz - pL_lowz.max())
    dchi2_cmb = -2*(pL_cmb - pL_cmb.max())
    dchi2_joint = -2*(pL_joint - pL_joint.max())

    A_best_lowz = A_vals[np.argmin(dchi2_lowz)]
    A_best_cmb = A_vals[np.argmin(dchi2_cmb)]
    A_best_joint = A_vals[np.argmin(dchi2_joint)]

    print(f"\n  Best A (low-z):  {A_best_lowz:.3f}")
    print(f"  Best A (CMB):    {A_best_cmb:.3f}")
    print(f"  Best A (joint):  {A_best_joint:.3f}")

    # 1σ bounds
    for name, dchi2, A_b in [("low-z", dchi2_lowz, A_best_lowz),
                              ("joint", dchi2_joint, A_best_joint)]:
        mask = dchi2 <= 1.0
        if mask.any():
            print(f"  1σ range ({name}): [{A_vals[mask].min():.3f}, "
                  f"{A_vals[mask].max():.3f}]")

    # --- 3D best-fit (joint) ---
    print("\n--- 3D Grid Best-Fit (joint) ---")
    ll_best, bp = find_best_3D(
        A_range=(-0.4, 0.15), Om_range=(0.27, 0.37),
        H0_range=(62.0, 73.0), fixed_z_L1L2=z_L1L2_fix,
        fixed_sigma8_0=sigma8_fix, likelihood_fn=logL_total,
        nA=30, nOm=20, nH0=15)

    print(f"  A = {bp.get('A', 0):.4f}")
    print(f"  Omega_m = {bp.get('Omega_m', 0):.4f}")
    print(f"  H0 = {bp.get('H0', 0):.2f}")
    print(f"  chi2_total = {-2*ll_best:.1f}")

    # LCDM best (A=0, profile over Om, H0)
    ll_lcdm_best, bp_lcdm = find_best_3D(
        A_range=(0.0, 0.0001), Om_range=(0.27, 0.37),
        H0_range=(62.0, 73.0), fixed_z_L1L2=z_L1L2_fix,
        fixed_sigma8_0=sigma8_fix, likelihood_fn=logL_total,
        nA=1, nOm=20, nH0=15)

    delta_chi2 = -2*(ll_lcdm_best - ll_best)
    n_data = len(bao_data) + len(cc_data) + len(rsd_z) + 3  # +3 for CMB
    k_efc = 1  # A is the extra parameter
    delta_AIC = delta_chi2 - 2*k_efc
    delta_BIC = delta_chi2 - k_efc * np.log(n_data)

    print(f"\n--- Model Comparison ---")
    print(f"  N_data = {n_data}")
    print(f"  chi2_LCDM(best) = {-2*ll_lcdm_best:.1f}  "
          f"(Om={bp_lcdm.get('Omega_m',0):.4f}, H0={bp_lcdm.get('H0',0):.2f})")
    print(f"  chi2_EFC(best)  = {-2*ll_best:.1f}  "
          f"(A={bp.get('A',0):.4f})")
    print(f"  Δχ² = {delta_chi2:.2f}  (negative = EFC better)")
    print(f"  ΔAIC = {delta_AIC:.2f}")
    print(f"  ΔBIC = {delta_BIC:.2f}")

    # --- Δχ² relative to ΛCDM (A=0) at each A ---
    # Use profile likelihood evaluated at A=0 for reference
    idx_A0 = np.argmin(np.abs(A_vals))
    dchi2_vs_lcdm_lowz = -2*(pL_lowz - pL_lowz[idx_A0])
    dchi2_vs_lcdm_cmb = -2*(pL_cmb - pL_cmb[idx_A0])
    dchi2_vs_lcdm_joint = -2*(pL_joint - pL_joint[idx_A0])

    # ============================================================
    # 7. PLOTS
    # ============================================================

    plt.rcParams.update({
        'font.size': 11, 'axes.labelsize': 13,
        'figure.facecolor': 'white', 'axes.grid': True, 'grid.alpha': 0.2,
    })

    fig = plt.figure(figsize=(16, 14))
    fig.suptitle('EFC Phase 2.4 — Joint Likelihood + CMB Distance Prior\n'
                 f'$z_{{L1L2}} = {z_L1L2_fix}$ (fixed), $n = {n_gate}$, '
                 f'$H_0$ FREE',
                 fontsize=14, fontweight='bold')

    # --- Plot 1: Profile likelihood on A ---
    ax1 = fig.add_subplot(2, 2, 1)

    # Convert to normalised posteriors
    for dchi2, color, ls, lw, label in [
        (dchi2_lowz, 'blue', '-', 2, 'BAO+CC+RSD'),
        (dchi2_cmb, 'orange', '--', 2, 'CMB prior'),
        (dchi2_joint, 'black', '-', 2.5, 'Joint (all)'),
    ]:
        L = np.exp(-0.5 * dchi2)
        norm = np.trapezoid(L, A_vals)
        if norm > 0:
            L /= norm
        ax1.plot(A_vals, L, color=color, ls=ls, lw=lw, label=label)

    ax1.axvline(0, color='gray', ls=':', alpha=0.5, label='$\\Lambda$CDM')
    ax1.axvline(A_best_joint, color='green', ls='--', alpha=0.7,
                label=f'Best $A={A_best_joint:.3f}$')
    ax1.set_xlabel('$A$')
    ax1.set_ylabel('Profile posterior (normalised)')
    ax1.set_title('Profile Likelihood on $A$\n(profiling over $\\Omega_m$, $H_0$)')
    ax1.legend(fontsize=9)
    ax1.set_xlim(-0.4, 0.3)

    # --- Plot 2: Δχ² vs ΛCDM ---
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.plot(A_vals, dchi2_vs_lcdm_lowz, 'b-', lw=2, label='BAO+CC+RSD')
    ax2.plot(A_vals, dchi2_vs_lcdm_cmb, color='orange', ls='--', lw=2,
             label='CMB prior')
    ax2.plot(A_vals, dchi2_vs_lcdm_joint, 'k-', lw=2.5, label='Joint')
    ax2.axhline(0, color='gray', ls='-', alpha=0.3)
    ax2.axhline(-1, color='green', ls='--', alpha=0.4, label='$\\Delta\\chi^2=-1$')
    ax2.axhline(-4, color='green', ls=':', alpha=0.4, label='$\\Delta\\chi^2=-4$')
    ax2.axhline(-9, color='red', ls=':', alpha=0.3, label='$\\Delta\\chi^2=-9$')
    ax2.set_xlabel('$A$')
    ax2.set_ylabel('$\\Delta\\chi^2$ relative to $\\Lambda$CDM ($A=0$)')
    ax2.set_title('$\\Delta\\chi^2(A)$ by Dataset')
    ax2.legend(fontsize=8)
    ax2.set_xlim(-0.4, 0.3)
    ax2.set_ylim(-20, 8)

    # --- Plot 3: CMB observables vs A ---
    ax3 = fig.add_subplot(2, 2, 3)
    A_test = np.linspace(-0.35, 0.25, 50)
    R_vals = np.zeros_like(A_test)
    lA_vals = np.zeros_like(A_test)

    for i, A in enumerate(A_test):
        m = EFCModel(A=A, z_L1L2=z_L1L2_fix, Omega_m=Om_planck,
                     H0=H0_planck, sigma8_0=sigma8_fix)
        R_vals[i] = m.R_shift(z_star)
        lA_vals[i] = m.ell_A(z_star, r_s_star)

    ax3a = ax3
    color_R = 'tab:blue'
    ax3a.plot(A_test, R_vals, color=color_R, lw=2, label='$R(A)$')
    ax3a.axhline(cmb_obs[0], color=color_R, ls=':', alpha=0.5)
    ax3a.fill_between(A_test,
                       cmb_obs[0] - np.sqrt(cmb_cov[0,0]),
                       cmb_obs[0] + np.sqrt(cmb_cov[0,0]),
                       color=color_R, alpha=0.15)
    ax3a.set_xlabel('$A$')
    ax3a.set_ylabel('$R$ (shift parameter)', color=color_R)
    ax3a.tick_params(axis='y', labelcolor=color_R)

    ax3b = ax3a.twinx()
    color_lA = 'tab:red'
    ax3b.plot(A_test, lA_vals, color=color_lA, lw=2, ls='--', label='$\\ell_A(A)$')
    ax3b.axhline(cmb_obs[1], color=color_lA, ls=':', alpha=0.5)
    ax3b.fill_between(A_test,
                       cmb_obs[1] - np.sqrt(cmb_cov[1,1]),
                       cmb_obs[1] + np.sqrt(cmb_cov[1,1]),
                       color=color_lA, alpha=0.15)
    ax3b.set_ylabel('$\\ell_A$ (acoustic scale)', color=color_lA)
    ax3b.tick_params(axis='y', labelcolor=color_lA)

    ax3.set_title('CMB Distance Observables vs $A$\n(fixed $\\Omega_m$, $H_0$)')
    lines1, labels1 = ax3a.get_legend_handles_labels()
    lines2, labels2 = ax3b.get_legend_handles_labels()
    ax3a.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc='upper left')

    # --- Plot 4: Summary bar chart ---
    ax4 = fig.add_subplot(2, 2, 4)

    categories = ['$\\Delta\\chi^2$', '$\\Delta$AIC', '$\\Delta$BIC']
    values = [delta_chi2, delta_AIC, delta_BIC]
    colors = ['#2166ac' if v < 0 else '#b2182b' for v in values]
    bars = ax4.barh(categories, values, color=colors, edgecolor='black', height=0.5)
    ax4.axvline(0, color='black', lw=1)
    ax4.axvline(-5, color='green', ls='--', alpha=0.3)
    ax4.axvline(-10, color='green', ls=':', alpha=0.3)

    for bar, val in zip(bars, values):
        ax4.text(val - 0.5 if val < 0 else val + 0.3, bar.get_y() + bar.get_height()/2,
                 f'{val:.1f}', va='center', ha='right' if val < 0 else 'left',
                 fontweight='bold', fontsize=12)

    ax4.set_xlabel('Value (negative = EFC preferred)')
    ax4.set_title(f'Model Comparison: EFC vs $\\Lambda$CDM\n'
                  f'Best-fit $A = {bp.get("A", 0):.3f}$, '
                  f'$\\Omega_m = {bp.get("Omega_m", 0):.3f}$, '
                  f'$H_0 = {bp.get("H0", 0):.1f}$')
    ax4.set_xlim(min(values) * 1.3, max(max(values) * 1.3, 3))

    plt.tight_layout(rect=[0, 0, 1, 0.92])
    outpath = '/home/user/EFC/efc_phase2_4_cmb_prior.png'
    plt.savefig(outpath, dpi=150, bbox_inches='tight')
    plt.close()

    elapsed = time.time() - t0
    print(f"\nPlot saved: {outpath}")
    print(f"Total runtime: {elapsed:.0f}s")
    print("=" * 65)

if __name__ == '__main__':
    main()
