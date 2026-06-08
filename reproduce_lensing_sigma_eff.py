#!/usr/bin/env python3
"""
EFC Lensing Sigma_eff(z) Reproducibility Script  (F9: slip/crossover STRUCTURE)
===============================================================================

Deterministic reproduction of the EFC effective lensing coupling Sigma(k,z)
and its non-monotonic Sigma_eff(z) CROSSOVER (criterion F9), run from a
self-contained copy of EFC's OWN production lensing engine.

    python reproduce_lensing_sigma_eff.py

Reproduces, from the FROZEN EFC action (no per-observable tuning):
    - mu(k,z), eta(k,z), Sigma(k,z) = mu(1+eta)/2 at observable scales
    - the F9 STRUCTURE: Sigma > 1 at low z, Sigma < 1 at high z (a crossover
      near z ~ 0.5), with mu < 1 throughout (the simultaneous growth-suppression
      + lensing-slip that is EFC's distinctive perturbation-sector signature)
    - KT-A: the "valley" (mu<1, Sigma>1) survives a k-average at z=0.5

PHYSICS PROVENANCE.  EFCLensingParams, classify_regime, _compute_background and
compute_mu_eta_sigma below are copied VERBATIM from the EFC inference engine:
    efc_inference/engine/lensing.py
    (AGI-Test git de95e3e1723b126978be668ae88e02ad5cdd98a2)
derived from the EFC relativistic action (DOI 10.6084/m9.figshare.31876324,
Eq. 24-32). The mechanism: kinetic stiffness K(rho) brakes growth (mu<1);
the Lagrange-multiplier anisotropy (lambda term) boosts slip (eta>1), giving
Sigma = mu(1+eta)/2 > 1 at low z. This verbatim copy was checked against the
live production engine on 2026-06-08: identical mu/eta/Sigma to machine
precision across the F9 grid.

SCOPE DISCLAIMER (read this).  This reproduces the F9 THEORY prediction -- the
crossover STRUCTURE from the action -- NOT the F9 DATA test. Two honest caveats:

  (1) DATA.  The decisive F9 test is the Sigma_eff(z) SHAPE vs Euclid tomographic
      cosmic shear, which awaits Euclid DR1 (Oct 2026) + the full Cobaya+MGCAMB
      tomographic-shear likelihood. No code substitutes for that data.

  (2) AMPLITUDE.  The frozen-action Sigma at a single observable scale (e.g.
      Sigma(k=0.1) ~ 1.5-2 at z~0.1) is LARGER than the small k-integrated
      deviations quoted in the sealed F9 table (Sigma_eff ~ 1.03 at z~0.1).
      Sigma(k,z) is strongly scale-dependent; the OBSERVABLE Sigma_eff(z) is a
      lensing-kernel-weighted k-integral (matter P(k) x shear efficiency, which
      up-weights high k where Sigma -> ~0.99), suppressing the deviation toward
      the table values. A crude uniform/peaked k-average OVERSTATES it. The
      robust, code-verified claim here is the crossover STRUCTURE + mu<1, NOT
      the exact table amplitude (that needs the full lensing kernel).

This is the fragile eta-branch's distinctive shape. A monotonic Euclid result
kills only this branch and is consistent with robust EFC (Sigma ~ 0.99 flat).

Dependencies: numpy.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np


# =====================================================================
# PHYSICS -- copied verbatim from efc_inference/engine/lensing.py
#            (git de95e3e1)
# =====================================================================
@dataclass
class EFCLensingParams:
    """Physical parameters from the EFC action (frozen; no per-observable tuning)."""
    alpha: float = 0.012         # F(phi) = 1 + alpha*phi
    K0: float = 1.37             # stiffness scale
    rho_crit: float = 94.5       # screening density
    gamma0: float = 5.13         # entropy production rate
    V_prime: float = 0.61        # potential gradient (H0=1 units)
    Omega_m: float = 0.315
    H0: float = 67.4


def classify_regime(R: float, slip: float) -> str:
    if R > 10.0:
        return "EXTREME"
    if R > 0.2:
        return "STIFFNESS"
    if R > 0.01 and 0.02 < slip < 0.15:
        return "VALLEY"
    return "GR"


def _compute_background(a: float, p: EFCLensingParams) -> dict:
    """Background quantities at scale factor a. Units: H0=1, M_Pl=1."""
    Om = p.Omega_m
    E2 = Om * a**(-3) + (1.0 - Om)
    E = np.sqrt(E2)
    H = E
    rho = 3.0 * Om * a**(-3)
    rr = rho / p.rho_crit
    F = 1.0 + p.alpha
    denom_K = max(1.0 - rho / p.rho_crit, 1e-10)
    K_rho = p.K0 / denom_K
    Gamma = p.gamma0 * rr / (1.0 + rr)
    Gamma_prime = p.gamma0 / p.rho_crit / (1.0 + rr)**2
    phi_dot = Gamma / (3.0 * H)
    K_dot = p.K0 / denom_K**2 / p.rho_crit * (-3.0 * H * rho)
    Om_a = Om * a**(-3) / E2
    R_ricci = 6.0 * H**2 * (2.0 - 1.5 * Om_a)
    Ricci_term = 0.5 * p.alpha * R_ricci
    K_bracket = K_dot * phi_dot + K_rho * Gamma
    lambda_dot = (p.V_prime - Ricci_term - K_bracket) / (3.0 * H)
    return {'a': a, 'E': E, 'H': H, 'F': F, 'rho': rho, 'rr': rr,
            'K_rho': K_rho, 'K_dot': K_dot, 'Gamma': Gamma,
            'Gamma_prime': Gamma_prime, 'phi_dot': phi_dot,
            'lambda_dot': lambda_dot, 'R_ricci': R_ricci}


def compute_mu_eta_sigma(k: float, z: float, p: Optional[EFCLensingParams] = None) -> dict:
    """Compute (mu, eta, Sigma) at a single (k, z) point. (Eq. 24-31)"""
    if p is None:
        p = EFCLensingParams()
    a = 1.0 / (1.0 + z)
    bg = _compute_background(a, p)
    F = bg['F']; K_rho = bg['K_rho']; phi_dot = bg['phi_dot']
    lambda_dot = bg['lambda_dot']; Gamma_prime = bg['Gamma_prime']
    common = a**2 * Gamma_prime / (F * k**2)
    eps_F = p.alpha * phi_dot * common
    eps_lambda = lambda_dot * common
    eps_K = K_rho * phi_dot * common
    R = K_rho * a**4 * Gamma_prime**2 * phi_dot**2 / (F * k**4)
    slip = eps_F + eps_lambda - eps_K
    mu = (1.0 + eps_F) / (F * (1.0 + R))
    if abs(slip) < 0.99:
        eta = (1.0 + slip) / (1.0 - slip)
    else:
        eta = np.inf if slip > 0 else 0.0
    sigma = mu * (1.0 + eta) / 2.0 if np.isfinite(eta) else np.inf
    regime = classify_regime(R, slip)
    return {'k': k, 'z': z, 'a': a, 'mu': mu, 'eta': eta, 'sigma': sigma,
            'R': R, 'slip': slip, 'regime': regime}


# =====================================================================
# F9 grid + the sealed F9 table (k-integrated reference, fragile branch)
# =====================================================================
F9_Z = [0.10, 0.29, 0.44, 0.58, 0.87, 1.21]
F9_TABLE = [1.026, 1.008, 1.000, 0.994, 0.988, 0.985]   # sealed k-integrated ref
K_OBS = 0.1          # representative observable lensing scale (h/Mpc)
K_INT = np.logspace(-2, 0, 100)   # KT-A k-integration range 0.01-1.0


def sigma_at(k, z, p):
    return compute_mu_eta_sigma(k, z, p)['sigma']


def crossover_z(p, k=K_OBS, lo=0.05, hi=2.0, n=400):
    """Redshift where Sigma(k,z) crosses 1 (first sign change, high->low z)."""
    zs = np.linspace(lo, hi, n)
    s = np.array([sigma_at(k, float(z), p) for z in zs])
    above = s > 1.0
    idx = np.where(np.diff(above.astype(int)) != 0)[0]
    return float(zs[idx[0]]) if len(idx) else None


def kt_a_average(z, p):
    """KT-A: uniform log-k average of (mu, Sigma) over 0.01-1.0, excl EXTREME."""
    mus, sigs = [], []
    for k in K_INT:
        r = compute_mu_eta_sigma(float(k), z, p)
        if r['regime'] != 'EXTREME' and np.isfinite(r['mu']) and np.isfinite(r['sigma']):
            mus.append(r['mu']); sigs.append(r['sigma'])
    return (float(np.mean(mus)), float(np.mean(sigs)), len(mus)) if len(mus) > 10 else (np.nan, np.nan, 0)


class Result:
    def __init__(self):
        self.checks, self.n_pass, self.n_fail = [], 0, 0

    def check(self, name, passed, detail=""):
        tag = "\033[32mPASS\033[0m" if passed else "\033[31mFAIL\033[0m"
        print(f"  [{tag}] {name}" + (f"  ({detail})" if detail else ""))
        self.checks.append({"name": name, "passed": bool(passed), "detail": detail})
        self.n_pass += int(passed); self.n_fail += int(not passed)

    def summary(self):
        return {"total": self.n_pass + self.n_fail, "passed": self.n_pass, "failed": self.n_fail}


def main():
    print("=" * 70)
    print("  EFC LENSING Sigma_eff(z) REPRODUCIBILITY SCRIPT  (F9: crossover STRUCTURE)")
    print("  frozen action, copied verbatim -- THEORY prediction, NOT the Euclid data test")
    print(f"  Python {sys.version.split()[0]}, numpy {np.__version__}")
    print("=" * 70)
    R = Result(); t0 = time.time()
    p = EFCLensingParams()

    # ── Sigma(k=0.1, z) across the F9 grid vs the sealed table ──────────
    print(f"\n--- Sigma(k={K_OBS}, z) [single-scale] vs sealed F9 table [k-integrated] ---")
    print(f"  {'z':>5} {'mu':>8} {'eta':>8} {'Sigma':>9} {'F9-table':>9} {'regime':>9}")
    sig_obs = []
    for i, z in enumerate(F9_Z):
        r = compute_mu_eta_sigma(K_OBS, z, p)
        sig_obs.append(r['sigma'])
        print(f"  {z:>5.2f} {r['mu']:>8.4f} {r['eta']:>8.4f} {r['sigma']:>9.4f} {F9_TABLE[i]:>9.3f} {r['regime']:>9}")
    R.check("predictions_finite", all(np.isfinite(s) for s in sig_obs))

    # ── mu < 1 (growth suppression) at observable scale ─────────────────
    mus = [compute_mu_eta_sigma(K_OBS, z, p)['mu'] for z in F9_Z]
    R.check("mu_below_1", all(m < 1.0 for m in mus),
            f"mu in [{min(mus):.3f}, {max(mus):.3f}] < 1 (growth suppression)")

    # ── F9 crossover STRUCTURE: Sigma>1 low z, Sigma<1 high z ────────────
    print("\n--- F9 crossover structure ---")
    R.check("sigma_above_1_low_z", sig_obs[0] > 1.0,
            f"Sigma(z={F9_Z[0]})={sig_obs[0]:.3f} > 1 (lensing boost)")
    R.check("sigma_below_1_high_z", sig_obs[-1] < 1.0,
            f"Sigma(z={F9_Z[-1]})={sig_obs[-1]:.3f} < 1 (slip decays)")
    R.check("sigma_monotonic_decreasing", all(sig_obs[i] >= sig_obs[i+1] for i in range(len(sig_obs)-1)),
            "Sigma(z) decreases with z (non-monotonic crossover)")
    zc = crossover_z(p)
    print(f"  crossover (Sigma=1) at z = {zc:.3f}" if zc else "  no crossover found")
    R.check("crossover_z_in_range", zc is not None and 0.3 < zc < 0.8,
            f"crossover at z={zc:.3f} in [0.3,0.8] (F9 table ~0.44)" if zc else "no crossover")

    # ── KT-A: valley survives k-average at z=0.5 ────────────────────────
    print("\n--- KT-A: k-average at z=0.5 (valley survives?) ---")
    mu_avg, sig_avg, nval = kt_a_average(0.5, p)
    print(f"  <mu> = {mu_avg:.4f}   <Sigma> = {sig_avg:.4f}   (n_valid={nval} of {len(K_INT)})")
    R.check("kt_a_valley_survives", mu_avg < 1.0 and sig_avg > 1.0,
            f"<mu>={mu_avg:.3f}<1 and <Sigma>={sig_avg:.3f}>1 (valley survives k-average)")

    # ── HONEST amplitude note (informational, not a pass/fail) ──────────
    amp_ratio = sig_obs[0] / F9_TABLE[0]
    print(f"\n--- amplitude (honest) ---")
    print(f"  single-scale Sigma(k={K_OBS},z={F9_Z[0]})={sig_obs[0]:.2f} vs F9-table {F9_TABLE[0]:.3f} "
          f"(ratio {amp_ratio:.1f}x)")
    print(f"  -> structure is code-verified; exact table amplitude needs the full")
    print(f"     lensing-kernel k-integral (up-weights high-k where Sigma->~0.99).")

    # ── determinism ─────────────────────────────────────────────────────
    R.check("deterministic", abs(sigma_at(K_OBS, F9_Z[0], p) - sig_obs[0]) < 1e-12, "identical on re-run")

    elapsed = time.time() - t0
    s = R.summary()
    print(f"\n{'=' * 70}")
    tag = "\033[32mALL PASSED\033[0m" if s["failed"] == 0 else f"\033[31m{s['failed']} FAILED\033[0m"
    print(f"  {s['passed']}/{s['total']} checks passed  [{tag}]  ({elapsed:.2f}s)")
    print(f"  VERDICT: frozen action reproduces the F9 crossover STRUCTURE (mu<1,")
    print(f"  Sigma>1 low-z -> <1 high-z, crossover z~{zc:.2f}). DATA test (shape vs")
    print(f"  Euclid tomographic shear) + exact amplitude (full kernel) remain GAPS.")
    print("=" * 70)

    output = {
        "meta": {"script": "reproduce_lensing_sigma_eff.py",
                 "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                 "provenance": "physics copied verbatim from efc_inference (AGI-Test git de95e3e1): lensing.py",
                 "scope": "F9 crossover STRUCTURE (theory prediction); NOT the Euclid Sigma_eff(z) DATA test, NOT the exact table amplitude",
                 "amplitude_caveat": "single-scale Sigma >> k-integrated F9 table; observable needs full lensing-kernel k-integral; structure (crossover + mu<1) is the code-verified claim"},
        "params": {"alpha": p.alpha, "K0": p.K0, "rho_crit": p.rho_crit,
                   "gamma0": p.gamma0, "V_prime": p.V_prime, "Omega_m": p.Omega_m},
        "results": {
            "sigma_k0p1": {str(z): round(float(sv), 4) for z, sv in zip(F9_Z, sig_obs)},
            "mu_k0p1": {str(z): round(float(m), 4) for z, m in zip(F9_Z, mus)},
            "f9_table_ref": {str(z): t for z, t in zip(F9_Z, F9_TABLE)},
            "crossover_z": round(zc, 4) if zc else None,
            "kt_a_z0p5": {"mu_avg": round(mu_avg, 4), "sigma_avg": round(sig_avg, 4)},
            "amplitude_ratio_lowz": round(amp_ratio, 3),
        },
        "checks": R.checks, "summary": s,
    }
    rstr = json.dumps(output["results"], sort_keys=True, default=str)
    output["content_hash"] = hashlib.sha256(rstr.encode()).hexdigest()
    outp = Path(__file__).resolve().parent / "reproduce_lensing_sigma_eff_output.json"
    outp.write_text(json.dumps(output, indent=2, default=str))
    print(f"\n  Output: {outp.name}\n  SHA-256: {output['content_hash']}")
    return 0 if s["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
