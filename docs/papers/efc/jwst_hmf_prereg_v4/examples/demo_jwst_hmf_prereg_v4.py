"""demo_jwst_hmf_prereg_v4.py

Demonstration of the EFC HMF prediction chain at z = 7-12.
Produces a comparison of EFC vs LCDM halo mass functions using
three prescriptions (PS, ST, Tinker).
"""
import numpy as np
import sys

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_PLT = True
except ImportError:
    HAS_PLT = False

from jwst_hmf_prereg_v4 import (
    build_D_interpolator, dn_dM,
    B_DEFAULT, ZT_DEFAULT, N_EXP_DEFAULT
)

# ---- configuration ----
redshifts = [7, 8, 9, 10, 11, 12]
log_M = np.linspace(9.5, 13.0, 40)  # log10(M / [Msun/h])
M_arr = 10**log_M
prescriptions = ['PS', 'ST', 'Tinker']

# ---- build growth interpolators ----
print('Building LCDM growth factor...')
D_lcdm = build_D_interpolator(B=0.0)
print('Building EFC growth factor  (B={}, zt={}, n={})...'.format(
    B_DEFAULT, ZT_DEFAULT, N_EXP_DEFAULT))
D_efc = build_D_interpolator()

# ---- compute HMFs and print summary table ----
print('\n{:>4s}  {:>12s}  {:>6s}  {:>12s}  {:>12s}  {:>8s}'.format(
    'z', 'log10 M', 'HMF', 'dn/dM LCDM', 'dn/dM EFC', 'ratio'))
print('-' * 70)

results = {}
for presc in prescriptions:
    results[presc] = {}
    for z in redshifts:
        hmf_lcdm = np.array([dn_dM(M, z, D_lcdm, presc) for M in M_arr])
        hmf_efc  = np.array([dn_dM(M, z, D_efc,  presc) for M in M_arr])
        results[presc][z] = (hmf_lcdm, hmf_efc)
        # print one representative mass bin
        idx = 20  # ~log M = 11.3
        if hmf_lcdm[idx] > 0:
            ratio = hmf_efc[idx] / hmf_lcdm[idx]
        else:
            ratio = np.inf
        if presc == 'ST':  # keep table concise
            print(f'{z:4d}  {log_M[idx]:12.2f}  {presc:>6s}  '
                  f'{hmf_lcdm[idx]:12.4e}  {hmf_efc[idx]:12.4e}  '
                  f'{ratio:8.3f}')

# ---- growth factor comparison ----
print('\nGrowth factor D(z) comparison:')
print('{:>4s}  {:>10s}  {:>10s}  {:>10s}'.format(
    'z', 'D_LCDM', 'D_EFC', 'D_EFC/D_LCDM'))
for z in redshifts:
    a = 1.0 / (1.0 + z)
    dl = float(D_lcdm(a))
    de = float(D_efc(a))
    print(f'{z:4d}  {dl:10.6f}  {de:10.6f}  {de/dl:10.6f}')

# ---- optional plot ----
if HAS_PLT:
    fig, axes = plt.subplots(2, 3, figsize=(15, 9), sharex=True, sharey=True)
    colors = {'LCDM': 'C0', 'EFC': 'C1'}
    for i, z in enumerate(redshifts):
        ax = axes[i // 3][i % 3]
        for presc in prescriptions:
            lcdm, efc = results[presc][z]
            ls = {"PS": ":", "ST": "-", "Tinker": "--"}[presc]
            mask = lcdm > 0
            ax.plot(log_M[mask], np.log10(lcdm[mask]),
                    ls=ls, color='C0', label=f'LCDM {presc}' if i == 0 else '')
            mask2 = efc > 0
            ax.plot(log_M[mask2], np.log10(efc[mask2]),
                    ls=ls, color='C1', label=f'EFC {presc}' if i == 0 else '')
        ax.set_title(f'z = {z}')
        ax.set_xlabel(r'$\log_{10}(M\;[M_\odot/h])$')
        ax.set_ylabel(r'$\log_{10}(dn/dM)$')
        ax.set_ylim(-25, -5)
    axes[0][0].legend(fontsize=7, ncol=2)
    plt.tight_layout()
    plt.savefig('efc_hmf_prediction_z7_12.png', dpi=150)
    print('\nPlot saved to efc_hmf_prediction_z7_12.png')
else:
    print('\nMatplotlib not available — skipping plot.')

print('\nDone.')
