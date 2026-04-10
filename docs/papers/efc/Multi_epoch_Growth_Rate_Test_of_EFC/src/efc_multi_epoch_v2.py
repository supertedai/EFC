"""
EFC Multi-epoch Growth Rate Test (v2)
Report: EFC-VAL-2026-003   DOI: 10.6084/m9.figshare.31955871

Solves the linear growth ODE with a regime-dependent gravitational coupling
mu(a) = 1 - B * T(a),  T(a) = 1 / (1 + (a_t/a)^n)
and fits f sigma8(z) over 14 measurements (z = 0.067 - 1.491).
"""
from __future__ import annotations
import csv, json, os
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import differential_evolution, minimize

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_CSV = os.path.join(HERE, "..", "data", "fsigma8_compilation.csv")


def load_data(path: str = DATA_CSV):
    z, f, s = [], [], []
    with open(path) as fh:
        for row in csv.DictReader(fh):
            z.append(float(row["z"]))
            f.append(float(row["fsigma8"]))
            s.append(float(row["sigma"]))
    return np.array(z), np.array(f), np.array(s)


def mu_of_a(a, B, z_t, n=2):
    a_t = 1.0 / (1.0 + z_t)
    return 1.0 - B / (1.0 + (a_t / a) ** n)


def E2(a, Om):
    return Om * a ** -3 + (1.0 - Om)


def growth_rhs(a, y, Om, B, z_t, n):
    D, Dp = y
    Ode = (1.0 - Om) / E2(a, Om)
    Om_a = Om * a ** -3 / E2(a, Om)
    mu = mu_of_a(a, B, z_t, n)
    Dpp = -(3.0 / (2.0 * a)) * (1.0 + Ode) * Dp + (3.0 / (2.0 * a * a)) * Om_a * mu * D
    return [Dp, Dpp]


def integrate_growth(zs, Om, sig8_0, B=0.0, z_t=1.0, n=2):
    a_i = 1e-3
    a_arr = np.sort(np.unique(np.concatenate(([a_i, 1.0], 1.0 / (1.0 + zs)))))
    sol = solve_ivp(
        growth_rhs, (a_i, 1.0), [a_i, 1.0],
        t_eval=a_arr, args=(Om, B, z_t, n),
        rtol=1e-9, atol=1e-12, method="DOP853",
    )
    a_out = sol.t
    D = sol.y[0]
    Dp = sol.y[1]
    f = (a_out / D) * Dp
    D0 = np.interp(1.0, a_out, D)
    a_targets = 1.0 / (1.0 + zs)
    D_z = np.interp(a_targets, a_out, D)
    f_z = np.interp(a_targets, a_out, f)
    return f_z * sig8_0 * D_z / D0


def chi2_LCDM(theta, z, fobs, sig):
    Om, s8 = theta
    if not (0.05 < Om < 0.6 and 0.4 < s8 < 1.2):
        return 1e9
    model = integrate_growth(z, Om, s8, B=0.0, z_t=1.0)
    return float(np.sum(((model - fobs) / sig) ** 2))


def chi2_EFC(theta, z, fobs, sig, Om_fixed):
    s8, B, z_t = theta
    if not (0.4 < s8 < 1.2 and 0.0 <= B < 0.5 and 0.05 < z_t <= 3.0):
        return 1e9
    model = integrate_growth(z, Om_fixed, s8, B=B, z_t=z_t)
    return float(np.sum(((model - fobs) / sig) ** 2))


def fit_LCDM(z, f, s):
    res = differential_evolution(chi2_LCDM, [(0.1, 0.5), (0.5, 1.0)], args=(z, f, s), seed=0, tol=1e-10)
    pol = minimize(chi2_LCDM, res.x, args=(z, f, s), method="L-BFGS-B")
    return {"Omega_m": float(pol.x[0]), "sigma8_0": float(pol.x[1]), "chi2": float(pol.fun), "dof": len(z) - 2}


def fit_EFC(z, f, s, Om_fixed):
    res = differential_evolution(chi2_EFC, [(0.5, 1.0), (0.0, 0.49), (0.05, 3.0)],
                                 args=(z, f, s, Om_fixed), seed=0, tol=1e-10)
    pol = minimize(chi2_EFC, res.x, args=(z, f, s, Om_fixed), method="L-BFGS-B")
    s8, B, z_t = pol.x
    return {"sigma8_0": float(s8), "B": float(B), "z_t": float(z_t),
            "mu0": float(1.0 - B), "chi2": float(pol.fun), "dof": len(z) - 3}


def main():
    z, f, s = load_data()
    lcdm = fit_LCDM(z, f, s)
    efc = fit_EFC(z, f, s, Om_fixed=lcdm["Omega_m"])
    out = {
        "n_data": len(z),
        "LCDM": lcdm,
        "EFC": efc,
        "delta_chi2": efc["chi2"] - lcdm["chi2"],
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
