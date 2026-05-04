"""demo_jwst_hmf_prereg_v4.py

<<<<<<< HEAD
Demonstration of the EFC HMF prediction chain at z = 7-12.
Produces a comparison of EFC vs LCDM halo mass functions using
three prescriptions (PS, ST, Tinker).
=======
Demonstration script for the EFC JWST HMF pre-registration prediction chain.
Computes halo mass functions at z=7-12 for LCDM and EFC, and optionally plots them.
>>>>>>> origin/main
"""
import numpy as np
import sys

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
<<<<<<< HEAD
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
=======
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

from jwst_hmf_prereg_v4 import (
    compute_growth, calibrate_Pk_norm, dndlnM, compute_hmf_table,
    gate_function, mu_eff, B_DEFAULT, ZT_DEFAULT, N_DEFAULT
)
from scipy.interpolate import interp1d


def main():
    print('EFC JWST HMF Pre-Registration — Demonstration')
    print('=' * 55)
    print(f'Gate parameters: B={B_DEFAULT}, zt={ZT_DEFAULT}, n={N_DEFAULT}')
    print()

    redshifts = np.array([7, 8, 9, 10, 11, 12], dtype=float)
    logM_arr = np.linspace(9.5, 13.0, 30)

    # --- LCDM (B=0) ---
    print('Computing LCDM growth (B=0)...')
    a_lcdm, D_lcdm = compute_growth(B=0.0)
    D_lcdm_interp = interp1d(a_lcdm, D_lcdm, kind='cubic', fill_value='extrapolate')

    # --- EFC ---
    print(f'Computing EFC growth (B={B_DEFAULT})...')
    a_efc, D_efc = compute_growth(B=B_DEFAULT)
    D_efc_interp = interp1d(a_efc, D_efc, kind='cubic', fill_value='extrapolate')

    Pk_norm = calibrate_Pk_norm()
    print(f'Power spectrum normalisation: {Pk_norm:.6e}')
    print()

    # Print growth factor comparison
    print(f'{"z":>4s}  {"D_LCDM":>12s}  {"D_EFC":>12s}  {"ratio":>8s}  {"mu(a)":>8s}')
    print('-' * 52)
    for z in redshifts:
        a = 1.0 / (1.0 + z)
        dl = D_lcdm_interp(a)
        de = D_efc_interp(a)
        mu = mu_eff(a)
        print(f'{z:4.0f}  {dl:12.6e}  {de:12.6e}  {de/dl:8.5f}  {mu:8.5f}')
    print()

    # Compute HMF tables for all three prescriptions
    prescriptions = ['PS', 'ST', 'Tinker']
    for pres in prescriptions:
        print(f'\n--- HMF prescription: {pres} ---')
        # LCDM
        hmf_lcdm = np.zeros((len(redshifts), len(logM_arr)))
        hmf_efc = np.zeros((len(redshifts), len(logM_arr)))
        for i, z in enumerate(redshifts):
            a = 1.0 / (1.0 + z)
            Dl = D_lcdm_interp(a)
            De = D_efc_interp(a)
            for j, lgM in enumerate(logM_arr):
                M = 10.0**lgM
                hmf_lcdm[i, j] = dndlnM(M, z, Dl, Pk_norm, pres)
                hmf_efc[i, j] = dndlnM(M, z, De, Pk_norm, pres)

        # Print selected mass bins
        for i, z in enumerate(redshifts):
            idx_11 = np.argmin(np.abs(logM_arr - 11.0))
            ratio = hmf_efc[i, idx_11] / hmf_lcdm[i, idx_11] if hmf_lcdm[i, idx_11] > 0 else np.nan
            print(f'  z={z:2.0f}  log10(M)=11.0  LCDM={hmf_lcdm[i, idx_11]:.4e}  '
                  f'EFC={hmf_efc[i, idx_11]:.4e}  EFC/LCDM={ratio:.4f}')

    # --- Optional plot ---
    if HAS_MPL:
        print('\nGenerating plot...')
        fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharex=True, sharey=True)
        colors_z = plt.cm.viridis(np.linspace(0.1, 0.9, len(redshifts)))

        for i, z in enumerate(redshifts):
            ax = axes.flat[i]
            a = 1.0 / (1.0 + z)
            Dl = D_lcdm_interp(a)
            De = D_efc_interp(a)
            hmf_l = np.array([dndlnM(10**lgM, z, Dl, Pk_norm, 'ST') for lgM in logM_arr])
            hmf_e = np.array([dndlnM(10**lgM, z, De, Pk_norm, 'ST') for lgM in logM_arr])
            ax.semilogy(logM_arr, hmf_l, 'b-', lw=2, label='LCDM')
            ax.semilogy(logM_arr, hmf_e, 'r--', lw=2, label='EFC')
            ax.set_title(f'z = {z:.0f}')
            ax.set_xlabel(r'$\log_{10}(M\;[h^{-1}M_\odot])$')
            ax.set_ylabel(r'$dn/d\ln M\;[h^3\,{\rm Mpc}^{-3}]$')
            ax.set_ylim(1e-12, 1e-1)
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)

        fig.suptitle('EFC vs LCDM Halo Mass Function (Sheth-Tormen)', fontsize=14)
        plt.tight_layout()
        plt.savefig('hmf_efc_vs_lcdm.png', dpi=150)
        print('Plot saved to hmf_efc_vs_lcdm.png')
    else:
        print('matplotlib not available — skipping plot.')

    print('\nDone.')


if __name__ == '__main__':
    main()
>>>>>>> origin/main
