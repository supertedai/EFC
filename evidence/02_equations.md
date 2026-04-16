# EFC Core Equations -> Code Mapping

Each equation in the theory maps to a specific function in the codebase.
This document provides the explicit binding.

## Background sector

### Gate function (sigmoid transition)

    g(a) = 1 / (1 + (a_t / a)^n)

| Property | Value |
|----------|-------|
| Code | `src/efc/perturbation/gate.py:gate_function()` |
| Parameters | z_t = 1.01, n = 2 or 6 |
| Reference | Technical Note I, DOI:10.6084/m9.figshare.31333414 |

### Background modification

    E^2_EFC(z) = E^2_LCDM(z) + A [g(z) - g(0)]

| Property | Value |
|----------|-------|
| Code | `src/efc/perturbation/background.py:E2_efc()` |
| Sign lemma | DE^2 <= 0 for z > 0 (Lemma 1) |
| Verification | `background.py:verify_sign_lemma()` |
| Reference | Technical Note I, Eq. 5 |

### LCDM baseline

    E^2(z) = Omega_r (1+z)^4 + Omega_m (1+z)^3 + Omega_Lambda

| Property | Value |
|----------|-------|
| Code | `src/efc/perturbation/background.py:E2_lcdm()` |
| Defaults | Omega_m = 0.3134, Omega_r = 9.15e-5 (Planck 2018) |

## Perturbation sector

### Phenomenological gate model (Technical Notes)

    mu(a) = 1 - B g(a)

| Property | Value |
|----------|-------|
| Code | `src/efc/perturbation/mu.py:mu_of_a()` |
| Calibration | B = (1 - mu_0) / g(1; n) via `gate.py:calibrate_B()` |
| WP1a | B = 0.187, mu_0 = 0.85 |
| Reference | Technical Note II, Eq. 2, DOI:10.6084/m9.figshare.31333600 |

### Action-derived (mu, Sigma, eta) system (Perturbation Sector paper)

Derived from the EFC relativistic action with Lagrange-multiplier flow constraint:

    R(k,z) = K(rho) a^4 (Gamma')^2 phi_dot^2 / (M_Pl^2 F k^4)  [stiffness response]
    mu(k,z) = (1 + eps_F) / [F (1 + R)]                           [Eq. 8]
    eta(k,z) = (1 + eps_F + eps_lambda + eps_lambda_resp) /
               (1 - eps_F - eps_lambda - eps_lambda_resp)          [Eq. 9]
    Sigma(k,z) = mu (1 + eta) / 2                                  [Eq. 10]

The Horndeski no-go (Result 1): standard QS Horndeski with alpha_T = 0
cannot produce mu < 1 AND Sigma > 1.  The EFC flow constraint breaks this.

| Property | Value |
|----------|-------|
| Code | `pipelines/efc/euclid_dr1/src/efc_mg_functions.py` |
| Stiffness | `stiffness_response()`, `mu_efc()`, `eta_efc()`, `sigma_efc()` |
| Parameters | R_0 = 0.510, K_C = 0.05 h/Mpc, F = 1.00005, EPS_TOT = 0.40 |
| Reference | DOI:10.6084/m9.figshare.32037990, Eq. 7-10 |

### Lensing crossover prediction

    Sigma_eff(z) = [integral W(k) Sigma^2(k,z) dk / integral W(k) dk]^{1/2}

Crosses unity at z ~ 0.44: enhanced lensing (+2.6%) at z < 0.4,
suppressed lensing (-1.5%) at z > 0.5.

| Property | Value |
|----------|-------|
| Reference | DOI:10.6084/m9.figshare.32037990, Result 3, Fig. 1 |
| Testable by | Euclid DR1 / Rubin LSST tomographic lensing |

### Growth equation

    df/d(ln a) = -f^2 - (1/2 - 3/2 Omega_m_tilde) f + 3/2 mu(a) Omega_m_tilde

where f = d ln D / d ln a and Omega_m_tilde(a) = Omega_m a^{-3} / E^2(a).

| Property | Value |
|----------|-------|
| Code | `src/efc/perturbation/growth.py:growth_ode()` |
| Solver | RK4, z_init=50, n_points=2000 |
| Output | z, a, f, ln_D arrays |
| Reference | Technical Notes I & II |

### fsigma_8

    fsigma_8(z) = f(z) * sigma_8(z) = f(z) * sigma_8,0 * D(z)/D(0)

| Property | Value |
|----------|-------|
| Code | `src/efc/perturbation/growth.py:compute_fsigma8()` |
| LCDM baseline | sigma_8,0 = 0.811 |
| WP1a EFC | sigma_8 = 0.773 (73% S8 gap closure) |

### Chi-squared

    chi^2 = sum_i [(obs_i - model_i)^2 / sigma_i^2]

| Property | Value |
|----------|-------|
| Code | `src/efc/perturbation/robustness.py:chi2_fsigma8()` |
| Data | 7-point fsigma_8 compilation (6dFGS to FastSound) |

## Galactic sector (rotation curves)

### Entropy field

    S(r) = S_0 (1 - exp(-r / L_s))

| Property | Value |
|----------|-------|
| Code | `src/efc/entropy/efc_entropy.py:entropy_field()` |
| Parameters | S_0 (entropy scale), L_s (length scale, kpc) |

### Energy flow

    E_f(r) = rho(r) (1 - S(r))

| Property | Value |
|----------|-------|
| Code | `src/efc/potential/efc_potential.py:compute_energy_flow()` |
| Rotation | v(r) = sqrt(|E_f(r)| * r) |
