# EFC Euclid DR1 Pipeline

Pre-registration package for October 2026.

**Status:** Core modules verified, ready for hi_class integration
**Deadline:** Euclid DR1 public release -- 21 October 2026
**Author:** Morten Magnusson (ORCID: 0009-0002-4860-5095)

---

## What this package contains

### 1. `src/efc_mg_functions.py` -- Verified mu/eta/Sigma functions

Canonical implementation from Scale-Localised Modified Gravity
(DOI: 10.6084/m9.figshare.31985313).

Verified outputs at k_c = 0.05 h/Mpc, z = 0:

| Function | Value  | Paper |
|----------|--------|-------|
| mu(k_c)  | 0.9400 | 0.940 |
| eta(k_c) | 1.2000 | 1.200 |
| Sigma(k_c) | 1.0340 | 1.034 |
| E_G bump (z=0.35) | 5.5% | 5-7% |

Includes `mgcamb_mu_sigma(a, k)` interface for MGCAMB integration.

### 2. `src/efc_hiclass_bridge.py` -- hi_class Horndeski mapping

Maps EFC entropy field to Horndeski alpha-basis:

- alpha_B(a) = B0 * dS/d(ln a) -- braiding
- alpha_M(a) = M0 * S(a) -- Planck-mass running
- alpha_T = 0 -- GW170817 constraint

Generates:

- `efc_hiclass.ini` -- ready-to-run hi_class configuration
- `efc_hiclass_alphas.dat` -- tabulated alpha-functions (200 points)
- `efc_cobaya.yaml` -- complete cobaya config with PolyChord sampler

### 3. `src/euclid_mock_likelihood.py` -- Euclid DR1 mock (simplified)

Gaussian mock with DR1 survey specs (2100 deg^2, 10 WL + 4 GC bins).
**Note:** This uses a simplified Cl model. Replace with hi_class output.

---

## Critical path to October 2026

### Step 1: Install hi_class

```bash
git clone https://github.com/miguelzuma/hi_class_public.git
cd hi_class_public
make class
pip install .
```

### Step 2: Run EFC through hi_class

```bash
cd pipelines/efc/euclid_dr1
PYTHONPATH=. python src/efc_hiclass_bridge.py --write-ini
# Then run hi_class with the generated .ini
```

This produces CORRECT Cl with full Boltzmann integration.

### Step 3: Validate against existing results

Compare hi_class output against:

- Kill-Test v6 fsigma8 values (must match 2.20 sigma signal)
- KiDS-1000 Case A lensing response
- Planck CMB survival (mu-Sigma valley)

### Step 4: Build real Euclid likelihood

Replace mock with proper Limber-integrated Cl from hi_class:

- Use `classy_hiclass` theory module in cobaya
- Euclid forecast covariance from EC20

### Step 5: Run PolyChord for full posterior

```bash
cobaya-run config/efc_cobaya.yaml
```

Output: Full posterior on (B0, M0, h, Omega_b, Omega_c, n_s, A_s, tau) + ln Z.

### Step 6: Freeze predictions

Generate sealed predictions with SHA-256 hash:

- E_G(k,z) bump at k_c for Euclid redshift bins
- S8 shift from EFC Sigma modification
- eta(z) profile in gravitational slip window [0.5, 2.0]

### Step 7: Wait for Euclid DR1 (October 2026)

Swap mock data vector with real Euclid Cl. Run cobaya. Compare.

---

## Why hi_class, not MGCAMB

| | hi_class | MGCAMB |
|---|---|---|
| Language | Python (CLASS-based) | Fortran (CAMB-based) |
| alpha-functions | Native input | Requires custom patch |
| Stability | Built-in ghost/gradient checks | Manual |
| Cobaya | Direct via classy_hiclass | Needs wrapper |
| EFC mapping | Already done (efc_eft_ansatz.py) | Would need new code |

hi_class is the path of least resistance. MGCAMB can be added later as cross-check.

---

## Kill criteria mapped to this pipeline

| KC | Observable | EFC prediction | Pipeline module |
|----|-----------|---------------|-----------------|
| KC1 | P(k) full-shape | mu < 1 at k_c | hi_class -> P(k) |
| KC2 | fsigma8(z) | 2.20 sigma suppression | Kill-Test v6 (done) |
| KC3 | S8 (WL) | Sigma > 1 shifts S8 | hi_class -> Cl^{WL} |
| KC4 | eta = Psi/Phi | eta > 1 (slip) | hi_class -> E_G |
| KC5 | w(z) | Dynamical DE | hi_class -> BAO |

---

## Running sanity checks

```bash
cd pipelines/efc/euclid_dr1
PYTHONPATH=. python tests/test_sanity.py
```

Must show ALL PASS (A through F) before any pipeline execution.

---

## Files

```
euclid_dr1/
├── README.md
├── RUN_CHECKLIST.sh
├── config/
│   ├── efc_cobaya.yaml
│   └── efc_hiclass.ini
├── data/
│   └── efc_hiclass_alphas.dat
├── docs/
│   └── RCMP_COMPLIANCE_MATRIX.md
├── src/
│   ├── __init__.py
│   ├── efc_mg_functions.py
│   ├── efc_hiclass_bridge.py
│   └── euclid_mock_likelihood.py
└── tests/
    └── test_sanity.py
```
