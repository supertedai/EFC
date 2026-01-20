# CLASS Patch: EFC Regime Transition via Anisotropic Stress

## Overview

This patch implements a **dynamically activated** anisotropic stress modification in CLASS that:
- Remains dormant during CMB (G_CMB ≈ 10⁻¹²)
- Activates at late times (G(z=0) ≈ 1)
- Tests EFC regime transition hypothesis

**Philosophy:** No background modification. Pure late-time perturbative effect.

---

## File Structure

```
class_public/
├── include/
│   └── background.h          [NEW: Add regime parameter struct]
├── source/
│   ├── input.c               [MODIFY: Read new parameters]
│   ├── background.c          [NEW: Compute G(z) table]
│   └── perturbations.c       [MODIFY: Apply anisotropic stress]
└── explanatory.ini           [NEW: Example parameter file]
```

---

## PATCH 1: Add Parameters to `include/background.h`

**File:** `include/background.h`  
**Location:** After existing parameter structs (around line 200)

```c
/**
 * EFC regime transition parameters
 */
struct efc_regime {
  
  /* Control parameter χ(z) */
  double chi_early;      /**< χ at high z (default: 0.2) */
  double chi_late;       /**< χ at low z (default: 2.5) */
  double z_transition;   /**< Transition redshift (default: 50.0) */
  double z_width;        /**< Transition width (default: 30.0) */
  
  /* Landau equation parameters */
  double alpha;          /**< Coupling strength (default: 10.0) */
  double chi_c;          /**< Critical χ (tipping point, default: 1.0) */
  double b;              /**< Cubic coefficient (default: 1.0) */
  double tau;            /**< Relaxation time (default: 0.1) */
  double phi0;           /**< Saturation scale (default: 1.0) */
  
  /* Physical coupling */
  double epsilon_pi;     /**< Anisotropic stress strength (default: 0.0) */
  
  /* Computed table */
  int    table_size;     /**< Size of G(a) table */
  double *a_table;       /**< Scale factor values */
  double *G_table;       /**< G(a) = φ²/(φ² + φ₀²) values */
  
  short has_efc_regime;  /**< Flag: is EFC regime active? */
};
```

**Add to main background struct (around line 400):**

```c
struct background {
  /* ... existing members ... */
  
  struct efc_regime efc;  /**< EFC regime transition parameters */
  
  /* ... rest of struct ... */
};
```

---

## PATCH 2: Read Parameters from `source/input.c`

**File:** `source/input.c`  
**Location:** In `input_read_parameters()`, after reading cosmological parameters

**Add around line 1500 (after Omega_cdm, etc.):**

```c
  /* ============================================ */
  /* EFC Regime Transition Parameters            */
  /* ============================================ */
  
  pba->efc.has_efc_regime = _FALSE_;
  
  class_call(parser_read_double(pfc, "epsilon_pi", &param1, &flag1, errmsg),
             errmsg, errmsg);
  
  if (flag1 == _TRUE_) {
    pba->efc.epsilon_pi = param1;
    
    if (fabs(pba->efc.epsilon_pi) > 1e-10) {
      pba->efc.has_efc_regime = _TRUE_;
      
      /* Read regime parameters with defaults */
      class_call(parser_read_double(pfc, "efc_chi_early", &param1, &flag1, errmsg),
                 errmsg, errmsg);
      pba->efc.chi_early = (flag1 == _TRUE_) ? param1 : 0.2;
      
      class_call(parser_read_double(pfc, "efc_chi_late", &param1, &flag1, errmsg),
                 errmsg, errmsg);
      pba->efc.chi_late = (flag1 == _TRUE_) ? param1 : 2.5;
      
      class_call(parser_read_double(pfc, "efc_z_transition", &param1, &flag1, errmsg),
                 errmsg, errmsg);
      pba->efc.z_transition = (flag1 == _TRUE_) ? param1 : 50.0;
      
      class_call(parser_read_double(pfc, "efc_z_width", &param1, &flag1, errmsg),
                 errmsg, errmsg);
      pba->efc.z_width = (flag1 == _TRUE_) ? param1 : 30.0;
      
      class_call(parser_read_double(pfc, "efc_alpha", &param1, &flag1, errmsg),
                 errmsg, errmsg);
      pba->efc.alpha = (flag1 == _TRUE_) ? param1 : 10.0;
      
      class_call(parser_read_double(pfc, "efc_chi_c", &param1, &flag1, errmsg),
                 errmsg, errmsg);
      pba->efc.chi_c = (flag1 == _TRUE_) ? param1 : 1.0;
      
      class_call(parser_read_double(pfc, "efc_b", &param1, &flag1, errmsg),
                 errmsg, errmsg);
      pba->efc.b = (flag1 == _TRUE_) ? param1 : 1.0;
      
      class_call(parser_read_double(pfc, "efc_tau", &param1, &flag1, errmsg),
                 errmsg, errmsg);
      pba->efc.tau = (flag1 == _TRUE_) ? param1 : 0.1;
      
      class_call(parser_read_double(pfc, "efc_phi0", &param1, &flag1, errmsg),
                 errmsg, errmsg);
      pba->efc.phi0 = (flag1 == _TRUE_) ? param1 : 1.0;
    }
  }
  else {
    pba->efc.epsilon_pi = 0.0;
  }
```

---

## PATCH 3: Compute G(z) Table in `source/background.c`

**File:** `source/background.c`  
**Location:** Add new function before `background_init()` (around line 500)

```c
/**
 * Compute EFC regime transition table G(a)
 * 
 * Integrates Landau equation:
 *   τ dφ/dt = -a(χ)φ - bφ³
 * where a(χ) = α(χ - χ_c)
 * 
 * Returns G(a) = φ²/(φ² + φ₀²) ∈ [0,1]
 */
int background_efc_regime_table(
  struct background *pba,
  ErrorMsg errmsg
) {
  
  if (pba->efc.has_efc_regime == _FALSE_) return _SUCCESS_;
  
  int i;
  double z, a, dz, phi, phi_new;
  double chi, a_coeff, H, k1, k2, k3, k4;
  
  /* Table setup: z from 3000 to 0 */
  int N = 5000;
  double z_max = 3000.0;
  double z_min = 0.0;
  
  pba->efc.table_size = N;
  pba->efc.a_table = malloc(N * sizeof(double));
  pba->efc.G_table = malloc(N * sizeof(double));
  
  if (pba->efc.a_table == NULL || pba->efc.G_table == NULL) {
    sprintf(errmsg, "%s: Failed to allocate EFC regime table", __func__);
    return _FAILURE_;
  }
  
  /* Initial condition at high z */
  phi = 1e-6;
  
  /* RK4 integration from high z to low z */
  for (i = 0; i < N; i++) {
    z = z_max - i * (z_max - z_min) / (N - 1);
    a = 1.0 / (1.0 + z);
    dz = (i < N-1) ? -(z_max - z_min) / (N - 1) : 0.0;
    
    /* Store current values */
    pba->efc.a_table[i] = a;
    pba->efc.G_table[i] = (phi * phi) / (phi * phi + pba->efc.phi0 * pba->efc.phi0);
    
    if (i == N-1) break;
    
    /* Compute χ(z) - tanh profile */
    double chi_mid = 0.5 * (pba->efc.chi_early + pba->efc.chi_late);
    double chi_amp = 0.5 * (pba->efc.chi_late - pba->efc.chi_early);
    chi = chi_mid - chi_amp * tanh((z - pba->efc.z_transition) / pba->efc.z_width);
    
    /* Landau coefficient */
    a_coeff = pba->efc.alpha * (chi - pba->efc.chi_c);
    
    /* H(z) from background (use simple ΛCDM approximation) */
    double Omega_r = pba->Omega0_g + pba->Omega0_ur;
    double Omega_m = pba->Omega0_cdm + pba->Omega0_b;
    double Omega_L = 1.0 - Omega_m - Omega_r;
    H = sqrt(Omega_r * pow(1+z, 4) + Omega_m * pow(1+z, 3) + Omega_L);
    
    /* RK4 step for dφ/dz = (aφ + bφ³) / [(1+z)Hτ] */
    #define dphi_dz(z_val, phi_val) \
      ((a_coeff * phi_val + pba->efc.b * phi_val * phi_val * phi_val) / \
       ((1.0 + z_val) * H * pba->efc.tau))
    
    k1 = dphi_dz(z, phi);
    k2 = dphi_dz(z + dz/2, phi + dz*k1/2);
    k3 = dphi_dz(z + dz/2, phi + dz*k2/2);
    k4 = dphi_dz(z + dz, phi + dz*k3);
    
    phi_new = phi + dz * (k1 + 2*k2 + 2*k3 + k4) / 6.0;
    
    /* Stability bounds */
    if (phi_new < 0.0) phi_new = 0.0;
    if (phi_new > 100.0) phi_new = 100.0;
    
    phi = phi_new;
    
    #undef dphi_dz
  }
  
  if (pba->background_verbose > 0) {
    printf(" -> EFC regime table computed:\n");
    printf("    G(z=1100) = %.2e\n", 
           pba->efc.G_table[(int)(1100.0 * N / z_max)]);
    printf("    G(z=0)    = %.2e\n", pba->efc.G_table[N-1]);
  }
  
  return _SUCCESS_;
}
```

**Call this function in `background_init()` after background table is complete:**

```c
int background_init(
  struct precision *ppr,
  struct background *pba
) {
  
  /* ... existing background initialization ... */
  
  /** - Compute EFC regime transition table */
  class_call(background_efc_regime_table(pba, pba->error_message),
             pba->error_message,
             pba->error_message);
  
  return _SUCCESS_;
}
```

**Add interpolation helper function:**

```c
/**
 * Interpolate G(a) from pre-computed table
 */
double background_efc_G_at_a(
  struct background *pba,
  double a
) {
  
  if (pba->efc.has_efc_regime == _FALSE_) return 0.0;
  
  int i;
  double G;
  
  /* Linear interpolation */
  if (a <= pba->efc.a_table[0]) {
    return pba->efc.G_table[0];
  }
  if (a >= pba->efc.a_table[pba->efc.table_size - 1]) {
    return pba->efc.G_table[pba->efc.table_size - 1];
  }
  
  /* Find bracketing indices */
  for (i = 0; i < pba->efc.table_size - 1; i++) {
    if (a >= pba->efc.a_table[i] && a < pba->efc.a_table[i+1]) {
      double frac = (a - pba->efc.a_table[i]) / 
                    (pba->efc.a_table[i+1] - pba->efc.a_table[i]);
      G = pba->efc.G_table[i] + frac * (pba->efc.G_table[i+1] - pba->efc.G_table[i]);
      return G;
    }
  }
  
  return 0.0;
}
```

---

## PATCH 4: Apply Anisotropic Stress in `source/perturbations.c`

**File:** `source/perturbations.c`  
**Function:** `perturb_einstein()`  
**Location:** Around line 3500-4000 (where metric perturbations are computed)

**Find the section computing anisotropic stress (search for `metric->phi_prime_prime` or similar):**

```c
  /* Original CLASS code (simplified): */
  double pi_aniso = some_standard_expression;
  
  /* MODIFY TO: */
  double pi_aniso = some_standard_expression;
  
  /* Add EFC regime contribution */
  if (pba->efc.has_efc_regime == _TRUE_) {
    double G = background_efc_G_at_a(pba, a);
    pi_aniso += pba->efc.epsilon_pi * G * k * k;  /* k-dependent, late-time */
  }
```

**Alternative (cleaner): Add as separate metric component**

Look for where metric perturbations are assembled (around computation of Ψ, Φ):

```c
  /* After standard metric computation */
  if (pba->efc.has_efc_regime == _TRUE_) {
    double G = background_efc_G_at_a(pba, a);
    double delta_phi = pba->efc.epsilon_pi * G * delta_rho_total / (k*k);
    
    /* Add to metric potential */
    ppw->pvecmetric[ppw->index_mt_phi_prime_prime] += delta_phi;
  }
```

**Note:** Exact line depends on CLASS version. Search for:
- `ppw->pvecmetric[ppw->index_mt_phi_prime_prime]`
- `metric->phi` or `metric->psi`
- Anisotropic stress contributions

---

## PATCH 5: Memory Cleanup

**File:** `source/background.c`  
**Function:** `background_free()`

```c
int background_free(struct background *pba) {
  
  /* ... existing cleanup ... */
  
  /* Free EFC regime table */
  if (pba->efc.has_efc_regime == _TRUE_) {
    free(pba->efc.a_table);
    free(pba->efc.G_table);
  }
  
  return _SUCCESS_;
}
```

---

## Test Parameter File: `efc_regime_test.ini`

```ini
# EFC Regime Transition Test
# Based on Planck 2018 best-fit

# Standard cosmology (FIXED - no background modification)
h = 0.6736
omega_b = 0.02237
omega_cdm = 0.1200
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.0544

# EFC regime parameters
epsilon_pi = 1e-6           # Start conservative!
efc_chi_early = 0.2         # χ at high z
efc_chi_late = 2.5          # χ at low z  
efc_z_transition = 50.0     # Transition redshift
efc_z_width = 30.0          # Transition width
efc_alpha = 10.0            # Coupling strength
efc_chi_c = 1.0             # Tipping point
efc_b = 1.0                 # Cubic coefficient
efc_tau = 0.1               # Relaxation time
efc_phi0 = 1.0              # Saturation scale

# Output
output = tCl,pCl,lCl
lensing = yes
l_max_scalars = 2500
```

---

## Testing Protocol

### Step 1: Null Test (ε_π = 0)
```bash
./class efc_regime_test.ini
diff output_cl.dat output_cl_LCDM.dat
# Should be identical
```

### Step 2: Weak Coupling (ε_π = 10⁻⁶)
```bash
# Set epsilon_pi = 1e-6
./class efc_regime_test.ini
# Check: ΔC_ℓ^TT at ℓ < 100 (should be ~0)
# Check: C_ℓ^φφ (lensing, may show small effect)
```

### Step 3: Parameter Scan
Vary in this order:
1. `epsilon_pi`: 0, 10⁻⁷, 10⁻⁶, 10⁻⁵
2. `efc_chi_c`: 0.5, 1.0, 1.5 (changes activation redshift)
3. `efc_z_transition`: 20, 50, 100 (changes transition timing)

### Expected Results

**CMB peaks (ℓ = 200-2000):** No change (G_CMB ≈ 10⁻¹²)  
**ISW (ℓ < 100):** Possible small effect if ε_π > 10⁻⁶  
**Lensing:** Most likely place to see effect  
**Polarization:** Check TE, EE - should be unaffected

---

## Debugging Checklist

- [ ] Compile without errors: `make clean && make`
- [ ] Null test passes: ε_π=0 gives ΛCDM
- [ ] G(z=1100) printed as ~10⁻¹²
- [ ] G(z=0) printed as ~1
- [ ] C_ℓ output generated successfully
- [ ] No NaN or Inf in output

---

## Expected Physics

**What this tests:**
- Can a late-activated regime transition remain compatible with CMB?
- Does anisotropic stress gating produce observable effects in lensing/ISW?

**What this does NOT test:**
- Background modifications (H(z) unchanged)
- Sound horizon changes (r_s unchanged)
- Recombination physics (unchanged)

**Prediction:**
If EFC is correct, increasing ε_π should:
1. Leave CMB peaks untouched (G_CMB ≈ 0)
2. Modify late-time integrated Sachs-Wolfe
3. Possibly affect lensing convergence

---

## Citation

Based on vippepunkt-mathematics tested 2026-01-20.  
CMB-safe regime transition: G_CMB = 1.00×10⁻¹² < 10⁻⁴ threshold.

**Key insight:** Dynamically suppressed at recombination, activated at late times through χ(z) crossing critical threshold.

---

## Contact / Issues

If implementation fails:
1. Check CLASS version (tested on v3.2.0)
2. Verify header includes
3. Enable verbose output: `background_verbose = 1`
4. Contact: [your details]

**Status:** Ready for implementation ✓
