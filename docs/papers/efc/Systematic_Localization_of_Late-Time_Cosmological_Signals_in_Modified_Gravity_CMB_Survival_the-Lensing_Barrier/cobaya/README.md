# EFC Bridge — cobaya run

Full Planck 2018 **plik_lite TTTEEE + lowl TT/EE + lensing.clik** with free
cosmology and two free modified-gravity parameters `(mu0, Sigma0)`. This is
the configuration referenced in Kill-Test v5 (Session Note v5), Section 9,
and in the Localization paper (DOI: 10.6084/m9.figshare.31368433), Phase 2
`minimize_free_cosmo`.

## Files

| File | Description |
|------|-------------|
| `efc_bridge.yaml` | cobaya configuration — MGCAMB theory + Planck likelihoods + MG params |
| `efc_mu_table.json` | Reference `mu(k, a)` and `Sigma(k, a)` derived from `(K0, m^2)` |
| `run_efc_bridge.sh` | Wrapper script for install / minimize / mcmc / gr reference |

## Why plik_lite and not lensing.native alone

The Alens-proxy run with `planck_2018_lensing.native` + fixed cosmology
gives Δchi² ≈ **+2.2** in the isolated lensing sector, because the native
lensing likelihood has no access to the TT/TE/EE correlations that partially
compensate the lensing-amplitude boost. That is a **conflict signal**, not a
refutation: it means the EFC lensing signal shares modes with `As`, `ns`
(and the TT+TE+EE sector) and must be evaluated in the combined space.

The combined space is exactly what `plik_lite TTTEEE` + `lowl` + `lensing.clik`
with free cosmology provides. In that run, MGCAMB + cobaya previously
reported Δchi² = **-0.45** at `(mu0, Sigma0) = (0.94, 1.05)`. This
configuration reproduces that run.

## Physical bridge

The two free MG parameters map back to EFC field parameters through the
density-screened stiffness response:

```
R(k, a) = K0 * Theta(rho_m(a)) * (Gamma' * phi_dot)^2 * a^4 / k^4
mu(k, a) = 1 / (1 + R(k, a))
eta(k, a) = 1 + ((eta_ref - 1) / R_ref) * R(k, a)
Sigma(k, a) = 0.5 * (1 + eta(k, a)) * mu(k, a)
```

With

* `K0 = 1.66` (from Kill-Test v5 bridge calibration)
* `m^2 ≈ 0.0035` (slip mass, `m/H0 ≈ 0.06`)
* `(Gamma' * phi_dot)^2 = (0.049 * 0.01)^2`
* `Theta(rho) = exp(-(rho/rho_*)^2)`, `rho_* = 1e-22 kg/m^3`

at `(a = 1, k = 0.05 h/Mpc)` one gets `R = 0.0638` and
`(mu, eta, Sigma) = (0.940, 1.23, 1.048)`. See `efc_mu_table.json`.

## Running

Install the likelihoods (only once) into a packages directory:

```bash
export COBAYA_PACKAGES=/path/to/cobaya_packages
./run_efc_bridge.sh install
```

Reproduce the sweet-spot Δchi² ≈ -0.45:

```bash
./run_efc_bridge.sh minimize
```

Full MCMC posterior (requires more RAM, hours of wall time):

```bash
./run_efc_bridge.sh mcmc
```

GR reference best-fit (`mu0 = Sigma0 = 1`) for the Δchi² comparison:

```bash
./run_efc_bridge.sh gr
```

Then:

```
Δchi²(EFC, GR) = chi2_min(EFC) - chi2_min(GR)
```

## Requirements

* cobaya ≥ 3.5
* MGCAMB v1.5.2 (fork of CAMB, installed in place of vanilla `camb`)
* Planck 2018 high-ell plik_lite TTTEEE data (`cobaya-install` can fetch)
* Planck 2018 lowl TT + EE data
* Planck 2018 lensing clik data
* ~16 GB RAM for `--minimize`, ~32 GB recommended for full MCMC

## Decision rule

```
Δchi² ≤  0   ->  EFC bridge holds, ΛCDM becomes the mu0=Sigma0=1 limit
Δchi² > +10  ->  the bridge does not hold, EFC is falsified at this level
```

This is the single run that decides the L2 question in the Kill-Test v5
scorecard (Section 8). Galactic (L3) and recombination (L0) are already
settled in the Localization paper and the SPARC fit; this is the
perturbation sector.
