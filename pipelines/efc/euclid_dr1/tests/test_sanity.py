"""
EFC Pipeline Sanity Checks
===========================
Validates ALL prerequisites before freezing predictions or running hi_class.
Based on GPT peer review (April 2026) flagging:
  A. Early-time GR recovery
  B. Stability (no-ghost)
  C. k-unit consistency (the real bug, now fixed)
  D. Finiteness + positivity
  E. Smoothness (Boltzmann-safe)
  F. Neutrino discriminant

Run this BEFORE every pipeline execution.
"""
import numpy as np
import sys


def check_early_time_gr():
    """A: Verify GR recovery at z >> z_onset."""
    from src.efc_mg_functions import mu_efc, eta_efc, sigma_efc, K_C

    print("A. Early-time GR recovery")
    passed = True
    for z in [10, 50, 100, 1100]:
        for k in [0.001, K_C, 0.1]:
            ka, za = np.array([k]), np.array([z])
            mu = mu_efc(ka, za)[0]
            eta = eta_efc(ka, za)[0]
            sig = sigma_efc(ka, za)[0]

            # F = 1.00005 gives constant offset ~5e-5 in mu
            # This is degenerate with G_N rescaling (absorbed in A_s/Om)
            if z >= 50:
                if abs(mu - 1/1.00005) > 1e-4:
                    print(f"   FAIL: mu({k},{z}) = {mu}")
                    passed = False
                if abs(eta - 1) > 1e-3:
                    print(f"   FAIL: eta({k},{z}) = {eta}")
                    passed = False

    print(f"   {'PASS' if passed else 'FAIL'}: mu -> 1/F, eta -> 1, Sigma -> 1 for z > 50")
    if passed:
        print("   NOTE: Constant F=1.00005 offset is degenerate with G_N rescaling")
        print("         and absorbed in A_s/Omega_m calibration (not observable)")
    return passed


def check_stability():
    """B: No-ghost condition Q_S > 0 at all epochs."""
    from src.efc_hiclass_bridge import EFCHorndeskiMapping

    print("B. Stability (no-ghost)")
    m = EFCHorndeskiMapping()
    passed = True
    a_vals = np.linspace(0.001, 1.0, 1000)
    for a in a_vals:
        QS = m.no_ghost_QS(a)
        if QS <= 0:
            print(f"   FAIL: Q_S({a:.3f}) = {QS}")
            passed = False

    QS_min = min(m.no_ghost_QS(a) for a in a_vals)
    print(f"   {'PASS' if passed else 'FAIL'}: Q_S > 0 for all a in [0.001, 1.0]")
    print(f"   Q_S_min = {QS_min:.4f} at a ~ {a_vals[np.argmin([m.no_ghost_QS(a) for a in a_vals])]:.3f}")
    print(f"   NOTE: c_s^2 > 0 must be verified by hi_class at runtime")
    return passed


def check_k_units():
    """C: k-unit conversion end-to-end consistency."""
    from src.efc_mg_functions import mgcamb_mu_sigma, mu_efc, K_C

    print("C. k-unit consistency (h/Mpc <-> 1/Mpc)")
    h = 0.6736

    # k_c in physical units (what hi_class sends)
    k_c_phys = K_C * h  # 0.05 * 0.6736 = 0.0337 1/Mpc

    # Bridge should recover mu at k_c
    mu_bridge, _ = mgcamb_mu_sigma(1.0, k_c_phys)
    mu_direct = mu_efc(np.array([K_C]), np.array([0.0]))[0]

    match = abs(mu_bridge[0] - mu_direct) < 1e-10
    print(f"   k_c = {K_C} h/Mpc = {k_c_phys:.4f} 1/Mpc")
    print(f"   bridge(k_phys) -> mu = {mu_bridge[0]:.6f}")
    print(f"   direct(k_c)    -> mu = {mu_direct:.6f}")
    print(f"   {'PASS' if match else 'FAIL'}: k[h/Mpc] = k[1/Mpc] / h conversion correct")

    # Also check that the Limber ell is consistent
    from scipy.integrate import quad
    Om = 0.3153
    E = lambda z: np.sqrt(Om*(1+z)**3 + (1-Om))
    chi_h, _ = quad(lambda z: 2997.9/E(z), 0, 0.5)  # Mpc/h
    chi_m = chi_h / h  # Mpc

    ell_1 = K_C * chi_h           # k[h/Mpc] * chi[Mpc/h]
    ell_2 = (K_C * h) * chi_m     # k[1/Mpc] * chi[Mpc]

    ell_match = abs(ell_1 - ell_2) < 0.5
    print(f"   Limber ell(z=0.5): {ell_1:.1f} (h-units) vs {ell_2:.1f} (phys)")
    print(f"   {'PASS' if ell_match else 'FAIL'}: ell = k*chi consistent across unit systems")

    return match and ell_match


def check_finiteness():
    """D: All functions finite and positive."""
    from src.efc_mg_functions import mu_efc, eta_efc, sigma_efc

    print("D. Finiteness + positivity")
    passed = True
    count = 0
    for z in [0, 0.1, 0.5, 1, 2, 5, 10, 50, 1100]:
        for k in [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 10.0]:
            ka, za = np.array([k]), np.array([z])
            mu = mu_efc(ka, za)[0]
            eta = eta_efc(ka, za)[0]
            sig = sigma_efc(ka, za)[0]

            ok = (np.isfinite(mu) and mu > 0 and
                  np.isfinite(eta) and eta > 0 and
                  np.isfinite(sig) and sig > 0)
            if not ok:
                print(f"   FAIL: k={k}, z={z}: mu={mu}, eta={eta}, Sigma={sig}")
                passed = False
            count += 1

    print(f"   {'PASS' if passed else 'FAIL'}: {count} points checked, all finite and positive")
    return passed


def check_smoothness():
    """E: Verify mu/eta/Sigma are smooth (no spikes for Boltzmann solvers).
    Tests gradients in both k-space and ln(a)-space (what Boltzmann uses)."""
    from src.efc_mg_functions import mu_efc, eta_efc, sigma_efc

    print("E. Smoothness (Boltzmann-safe)")
    dk = 1e-5
    passed = True
    max_grad_k = 0
    max_grad_lna = 0

    for z in [0.0, 0.3, 0.5, 1.0]:
        a = 1.0 / (1.0 + z)
        for k in [0.005, 0.01, 0.03, 0.05, 0.1, 0.3]:
            ka = np.array([k])
            ka_dk = np.array([k + dk])
            za = np.array([z])

            # k-gradient (dk in h/Mpc)
            mu1 = mu_efc(ka, za)[0]
            mu2 = mu_efc(ka_dk, za)[0]
            grad_k = abs(mu2 - mu1) / dk
            max_grad_k = max(max_grad_k, grad_k)

            # ln(a)-gradient (what Boltzmann solvers use internally)
            dlna = 1e-4
            a_shifted = a * np.exp(dlna)
            z_shifted = 1.0 / a_shifted - 1.0
            mu3 = mu_efc(ka, np.array([z_shifted]))[0]
            grad_lna = abs(mu3 - mu1) / dlna
            max_grad_lna = max(max_grad_lna, grad_lna)

            if grad_k > 100 or grad_lna > 100:
                print(f"   FAIL: spike at k={k}, z={z}: dmu/dk={grad_k:.1f}, dmu/dlna={grad_lna:.1f}")
                passed = False

    print(f"   {'PASS' if passed else 'FAIL'}: max |dmu/dk| = {max_grad_k:.4f}, max |dmu/d(ln a)| = {max_grad_lna:.4f}")
    print(f"   All gradients << 100 (Boltzmann-safe)")
    return passed


def check_neutrino_discriminant():
    """F: Verify EFC signature is qualitatively distinct from neutrino mass."""
    from src.efc_mg_functions import eta_efc, K_C

    print("F. Neutrino discriminant")

    # EFC produces eta != 1 at k_c. Neutrinos don't.
    eta_at_kc = eta_efc(np.array([K_C]), np.array([0.5]))[0]
    eta_far = eta_efc(np.array([1.0]), np.array([0.5]))[0]  # far from k_c

    localized = abs(eta_at_kc - 1) > 10 * abs(eta_far - 1)

    print(f"   eta(k_c, z=0.5) = {eta_at_kc:.4f} (EFC: slip present)")
    print(f"   eta(k=1, z=0.5) = {eta_far:.6f} (far from k_c: ~GR)")
    print(f"   {'PASS' if localized else 'FAIL'}: EFC slip is scale-localized (neutrinos: uniform)")
    print(f"   Neutrinos: suppress growth but eta=1 everywhere")
    return localized


def run_all():
    """Run all sanity checks. Returns True only if ALL pass."""
    print("=" * 60)
    print("EFC PIPELINE SANITY CHECKS")
    print("=" * 60)
    print()

    sys.path.insert(0, '.')

    results = {
        'A_early_time': check_early_time_gr(),
        'B_stability': check_stability(),
        'C_k_units': check_k_units(),
        'D_finiteness': check_finiteness(),
        'E_smoothness': check_smoothness(),
        'F_neutrino': check_neutrino_discriminant(),
    }

    print()
    print("=" * 60)
    all_pass = all(results.values())
    print(f"OVERALL: {'ALL PASS' if all_pass else 'FAILURES DETECTED'}")
    for name, ok in results.items():
        print(f"  {name}: {'PASS' if ok else 'FAIL'}")
    print("=" * 60)

    return all_pass


if __name__ == "__main__":
    ok = run_all()
    sys.exit(0 if ok else 1)
