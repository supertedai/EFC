"""Demo: structural closure of growth-sector couplings.

Runs the three coupling classes (A, B, C) against LCDM and produces
f*sigma8(z) and EG(z) comparison curves.

Usage:  python demo_a_structural_closure_of_growth_sector_co.py
"""
import numpy as np
from a_structural_closure_of_growth_sector_co import (
    solve_growth, fsigma8, EG_statistic, C_EFC, OMEGA_M0, gate_G_integrated, gate_g,
)


def main() -> None:
    sigma8_0 = 0.811
    z_eval = np.array([0.0, 0.15, 0.38, 0.51, 0.61, 0.70, 0.85, 1.0, 1.5, 2.0])
    a_eval = 1.0 / (1.0 + z_eval)

    # --- Solve each class -------------------------------------------------
    configs = {
        'LCDM':    dict(coupling='LCDM', beta=0.0),
        'Class A': dict(coupling='A', k=0.1),
        'Class B': dict(coupling='B', beta=0.5),
        'Class C': dict(coupling='C', beta=0.5),
    }

    results = {}
    for label, kw in configs.items():
        a_arr, D_arr, f_arr = solve_growth(**kw)
        fs8_arr = fsigma8(a_arr, D_arr, f_arr, sigma8_0)
        results[label] = (a_arr, D_arr, f_arr, fs8_arr)

    # --- Print f*sigma8 table ---------------------------------------------
    print(f'{"z":>5s}', end='')
    for label in configs:
        print(f'  {label:>12s}', end='')
    print('  EG(LCDM)')
    print('-' * 72)

    for z_i, a_i in zip(z_eval, a_eval):
        print(f'{z_i:5.2f}', end='')
        for label in configs:
            a_arr, _, f_arr, fs8_arr = results[label]
            idx = np.argmin(np.abs(a_arr - a_i))
            print(f'  {fs8_arr[idx]:12.4f}', end='')
        # EG for LCDM
        a_lcdm, _, f_lcdm, _ = results['LCDM']
        idx0 = np.argmin(np.abs(a_lcdm - a_i))
        eg = EG_statistic(z_i, f_lcdm[idx0])
        print(f'  {eg:10.4f}')

    # --- Gate kernel illustration -----------------------------------------
    print('\n--- Gate & memory kernel values ---')
    for a_val in [0.1, 0.3, 0.5, 0.7, 1.0]:
        g_val = gate_g(a_val)
        G_val = gate_G_integrated(a_val)
        ratio = g_val / G_val if G_val > 1e-12 else float('inf')
        print(f'  a={a_val:.1f}:  g={g_val:.4f}  G={G_val:.4f}  g/G={ratio:.2f}')

    # --- Coupling degeneracy demo: Class B beta scan ----------------------
    print('\n--- Class B: f*sigma8(z=0.5) vs beta ---')
    betas = np.linspace(-1.0, 2.0, 13)
    for b in betas:
        a_arr, D_arr, f_arr = solve_growth(coupling='B', beta=b)
        fs8 = fsigma8(a_arr, D_arr, f_arr, sigma8_0)
        idx = np.argmin(np.abs(a_arr - 1.0 / 1.5))  # z=0.5
        print(f'  beta={b:+5.2f}  f*sigma8(z=0.5) = {fs8[idx]:.4f}')

    # --- Optional plot ----------------------------------------------------
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        for label, (a_arr, _, f_arr, fs8_arr) in results.items():
            z_arr = 1.0 / a_arr - 1.0
            mask = z_arr < 2.5
            axes[0].plot(z_arr[mask], fs8_arr[mask], label=label)

        axes[0].set_xlabel('z')
        axes[0].set_ylabel(r'$f\sigma_8(z)$')
        axes[0].legend()
        axes[0].set_title('Growth observable: f sigma_8')
        axes[0].invert_xaxis()

        # EG for each class
        for label, (a_arr, _, f_arr, _) in results.items():
            z_arr = 1.0 / a_arr - 1.0
            mask = (z_arr > 0.05) & (z_arr < 2.5)
            eg_arr = OMEGA_M0 / f_arr[mask]  # Sigma=1
            axes[1].plot(z_arr[mask], eg_arr, label=label)

        axes[1].set_xlabel('z')
        axes[1].set_ylabel(r'$E_G(z)$')
        axes[1].legend()
        axes[1].set_title(r'$E_G$ statistic ($\Sigma=1$)')
        axes[1].invert_xaxis()

        plt.tight_layout()
        plt.savefig('growth_sector_couplings.png', dpi=150)
        print('\nPlot saved to growth_sector_couplings.png')
    except ImportError:
        print('\nMatplotlib not available — skipping plot.')


if __name__ == '__main__':
    main()
