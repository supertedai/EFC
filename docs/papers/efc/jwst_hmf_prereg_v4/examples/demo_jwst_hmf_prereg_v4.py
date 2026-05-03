"""demo_jwst_hmf_prereg_v4.py

Demonstration script for the EFC JWST HMF pre-registration prediction chain.
Computes halo mass functions at z=7-12 for LCDM and EFC, and optionally plots them.
"""
import numpy as np
import sys

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
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
