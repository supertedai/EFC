#!/usr/bin/env python3
"""
Reproduce the EFC Euclid DR1 benchmark prediction.

Requires: hi_class with efc_logistic patch applied.
Apply patch: cd hi_class_public && git apply /path/to/hi_class_efc_logistic.patch
"""

try:
    from classy import Class
except ImportError:
    print("hi_class not installed. Install with:")
    print("  cd hi_class_public && git apply hi_class_efc_logistic.patch")
    print("  make clean && make -j4 class && make libclass.a")
    print("  cd python && python3 setup.py build_ext --inplace")
    raise

import numpy as np

COSMO_BASE = {
    'output': 'tCl,pCl,lCl,mPk', 'lensing': 'yes', 'l_max_scalars': 5000,
    'h': 0.6736, 'omega_b': 0.02237, 'omega_cdm': 0.1200,
    'n_s': 0.9649, 'ln10^{10}A_s': 3.044, 'tau_reio': 0.0544,
    'z_pk': '0.0,0.5', 'P_k_max_h/Mpc': 10.0,
}

# LCDM
lcdm = Class()
lcdm.set(COSMO_BASE)
lcdm.compute()

# EFC benchmark
efc = Class()
efc.set({**COSMO_BASE,
    'Omega_Lambda': 0, 'Omega_fld': 0, 'Omega_smg': -1,
    'gravity_model': 'efc_logistic',
    'expansion_model': 'lcdm',
    'expansion_smg': '0.6862',
    'parameters_smg': '0.02, 0.06, 0.3, 0.3, 1.0, 0.0',
    'cs2_safe_smg': 1e-6,
})
efc.compute()

h = lcdm.h()
s8_l, s8_e = lcdm.sigma8(), efc.sigma8()
cl_l, cl_e = lcdm.lensed_cl(5000), efc.lensed_cl(5000)

print(f"sigma8: LCDM={s8_l:.5f}, EFC={s8_e:.5f} ({(s8_e/s8_l-1)*100:+.3f}%)")
print(f"Cl^pp(ell=66): {(cl_e['pp'][64]/cl_l['pp'][64]-1)*100:+.3f}%")
print(f"Cl^TT(ell=30): {(cl_e['tt'][28]/cl_l['tt'][28]-1)*100:+.3f}%")

pk_l = lcdm.pk(0.05 * h, 0.5) * h**3
pk_e = efc.pk(0.05 * h, 0.5) * h**3
print(f"P(k=0.05,z=0.5): {(pk_e/pk_l-1)*100:+.3f}%")

lcdm.struct_cleanup(); lcdm.empty()
efc.struct_cleanup(); efc.empty()
