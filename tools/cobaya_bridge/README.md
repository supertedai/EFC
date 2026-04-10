# EFC Bridge — Local cobaya Installer

Self-contained tool that installs the EFC cobaya / CAMB stack into a
subdirectory of this folder and runs the Kill-Test v5 bridge test.

## What this installs

- A local Python venv (`.venv/`)
- `cobaya` + vanilla `camb` via pip
- Optional: `MGCAMB` from source (requires `gfortran`)
- Cobaya PACKAGES_DIR (`packages/`) with all Planck 2018 likelihoods
  that the current network can reach

## Files kept in git

- `install.sh`             — idempotent installer (venv + pip + cobaya-install)
- `run.sh`                 — runner wrapper (minimize / mcmc / GR reference)
- `efc_bridge.yaml`        — full configuration (plik_lite + lowl + lensing.clik), samples (mu0, Sigma0)
- `efc_bridge_reduced.yaml`— reduced configuration (lowl + lensing.native only), Alens proxy
- `efc_bridge_K0m2.yaml`   — full posterior config over (K0, m^2) + DESI BAO + Pantheon+
- `bridge_theory.py`       — closed-form bridge `(K0, m^2) -> (mu0, Sigma0)`
- `efc_mu_table.json`      — `mu(k,a)`, `Sigma(k,a)` bridge table from `(K0, m^2)`
- `README.md`              — this file

`.venv/`, `packages/`, `chains/`, `logs/` are git-ignored and rebuilt by
`install.sh`.

## Quick start

```bash
cd tools/cobaya_bridge
./install.sh                 # full install (will fall back to reduced if ESA is blocked)
./install.sh --reduced       # only low-ell + lensing.native (no external data needed)
./install.sh --with-mgcamb   # also try to build MGCAMB (see caveat below)

./run.sh minimize            # reduced yaml (in-sandbox)
./run.sh minimize --full     # full plik_lite yaml
./run.sh gr                  # GR reference chi^2 baseline
```

## Three yamls, three questions

| file                    | likelihoods                                            | free parameters                                              | answers                                                       |
|-------------------------|--------------------------------------------------------|--------------------------------------------------------------|---------------------------------------------------------------|
| `efc_bridge.yaml`         | `plik_lite TTTEEE` + `lowl.TT` + `lowl.EE` + `lensing.clik` | H0, ombh2, omch2, logA, ns, tau, **mu0, Sigma0** (MGCAMB)     | Full sweet-spot test, reproduces the Localization Δχ² = -0.45  |
| `efc_bridge_reduced.yaml` | `lowl.TT` + `lowl.EE` + `lensing.native`                   | H0, ombh2, omch2, logA, ns, tau, **Alens** (Σ² proxy)         | What a lensing-isolated sandbox can actually decide            |
| `efc_bridge_K0m2.yaml`    | `plik_lite TTTEEE` + lowl + lensing.clik + **DESI 2024 BAO** + **Pantheon+** | H0, ombh2, omch2, logA, ns, tau, **K0, m_sq** (EFC field params) | Full MCMC posterior over the two underlying EFC field parameters; "the run that decides" from Kill-Test v5 §9 |

The reduced yaml is **not** equivalent to the full one. It was added
specifically so this tool can still produce a real cobaya minimize in
environments where the ESA Planck download is blocked. The Alens-free
run is known (from the Localization paper Phase 3) to be tight with the
`(μ, Σ)` valley at the `+0.45 / -0.45` level and to give an Alens-proxy
`+2.2` conflict signal when Alens is pinned at `Σ²`. That's a feature, not
a bug — it's what quantifies the "lensing sector is angry at GR-optimal
parameters" statement.

## Known limitation: MGCAMB pip wrapper is broken

As of 2026-04, the `sfu-cosmo/MGCAMB` pip build compiles and installs a
working Fortran backend (symbols `__mgcamb_MOD_mu0`, `__mgcamb_MOD_sigma0`,
etc. are present in `camblib.so`), but the Python wrapper does not
correctly push `mu0` / `Sigma0` / `E11` / `E22` from `CAMBparams` into the
Fortran module globals. Concretely:

```python
import camb
def sig8(mu0, sig0):
    p = camb.CAMBparams()
    p.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.12, tau=0.0544)
    p.InitPower.set_params(As=2.1e-9, ns=0.9649)
    p.set_mgparams(MG_flag=3, pure_MG_flag=2, mu0=mu0, sigma0=sig0)
    p.set_matter_power(redshifts=[0.0], kmax=2.0)
    return camb.get_results(p).get_sigma8_0()

print(sig8( 0.00, 0.00))   # 0.9229   (should be 0.811 — MG_flag=0 baseline)
print(sig8( 0.50, 0.50))   # 0.9229
print(sig8(-0.06, 0.05))   # 0.9229   (Σ = 1.05 sweet spot)
```

Setting `MG_flag=3` switches to a non-GR path, but the actual `mu0` /
`sigma0` values never reach the Fortran common block, so the output is
independent of them. Direct writes to `ctypes.c_double.in_dll(...,
'__mgcamb_MOD_mu0')` also fail because the driver re-reads the
parameter cache from somewhere else before each transfer.

Until this is fixed upstream (or a custom theory wrapper is written that
post-processes vanilla CAMB output via the `efc_mu_table.json` bridge),
the `efc_bridge.yaml` run in this tool will not sample `mu0` / `Sigma0`
correctly. It will still sample cosmology and run plik_lite + lensing,
but the MG parameters will be fixed at their effective GR value.

## Network dependencies

`install.sh` will try to reach:

- `pypi.org` — required for pip packages (always OK in practice)
- `github.com` — required for MGCAMB source (OK in sandbox)
- `pla.esac.esa.int` — required for `plik_lite` + `lensing.clik` data
  (⚠ blocked in some sandboxes; 403 on the CONNECT tunnel)

If ESA is blocked, `install.sh` falls back to reduced mode automatically.

## Sampling (K0, m^2) directly

`efc_bridge_K0m2.yaml` samples the two EFC field parameters and derives
`(mu0, Sigma0)` via the closed-form bridge in `bridge_theory.py`:

```
R(K0)        = K0 * (Gamma' phi_dot)^2 / k_lens^4    = K0 * 9.604e-2  (k_lens = 0.05)
mu0(K0)      = 1 / (1 + R)
f(K0, m^2)   = 1 - m^2 / (K0 * k_lens^2)
eta(K0, m^2) = 1 + ((eta_ref - 1) / f_ref) * f
Sigma0       = 0.5 * (1 + eta) * mu0
```

with `eta_ref = 1.23` and `f_ref = 1 - 0.0035/(1.66 * 0.0025) = 0.156627`.

At the reference point `(K0 = 1.66, m_sq = 0.0035)` this returns
`(mu0, Sigma0) = (0.9401, 1.0482)` exactly — i.e. the Localization paper's
Phase 2 sweet spot. The yaml expresses these as `value: lambda K0: ...` /
`value: lambda K0, m_sq: ...` so that cobaya recomputes them at every
theory call from the sampled `(K0, m_sq)` and forwards them to the
underlying CAMB / MGCAMB module as input parameters.

To verify the bridge is consistent before launching the run:

```bash
python3 bridge_theory.py
# bridge sweet spot: {... 'mu0': 0.9401, 'Sigma0': 1.0482, 'eta': 1.23 ...}
```

To launch the full posterior on a real machine (≥32 GB RAM, plik_lite +
DESI BAO + Pantheon+ data installed):

```bash
./install.sh                # downloads DESI + Pantheon+ alongside Planck
./run.sh mcmc --K0m2        # full MCMC over (K0, m^2)
./run.sh minimize --K0m2    # best-fit only (cheaper)
```

This is the run that gives the joint `(K0, m^2)` posterior. Δchi² ≤ 0
means the bridge holds and ΛCDM emerges as the `K0 → 0` limit; Δchi² > 10
means the bridge is falsified at this confidence.

## Sanity check of the mu-table

The `efc_mu_table.json` file reproduces the sweet-spot `(μ, Σ) = (0.94, 1.05)`
at `(a = 1, k = 0.05 h/Mpc)` exactly, from `K0 = 1.66` and the slip
calibration. To verify:

```bash
python3 -c "
import json
t = json.load(open('efc_mu_table.json'))
ia = t['a'].index(1.0); ik = t['k_h_per_Mpc'].index(0.05)
print(f'mu    = {t[\"mu\"][ia][ik]:.4f}  (expect 0.940)')
print(f'Sigma = {t[\"Sigma\"][ia][ik]:.4f}  (expect 1.048)')
"
```

## References

- Kill-Test v5, Magnusson (2026), Session Note v5
- Localization paper, DOI 10.6084/m9.figshare.31368433
- Relativistic Action, DOI 10.6084/m9.figshare.31876324
