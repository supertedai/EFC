"""demo_a_falsified_bar_instability_criterion_re.py

Demonstration of the EFC-modified Toomre-Q parameter (Pi_EFC)
from Magnusson (2026).

Creates synthetic galaxy rotation curves analogous to paper's templates
(NGC 6503, NGC 3198, NGC 2841 -like) and reproduces key diagnostics.
"""
import numpy as np
import sys

try:
    from a_falsified_bar_instability_criterion_re import (
        Pi_EFC, Pi_min_disk_window, Pi_proxy_scalar, fit_Rd,
        ZETA_DEFAULT, ZETA_MAX, DISK_WINDOW_INNER, DISK_WINDOW_OUTER
    )
except ImportError:
    sys.exit('Could not import source module. Ensure '
             'a_falsified_bar_instability_criterion_re.py is on PYTHONPATH.')

# ---- Three template galaxies (tanh models) ----
templates = {
    'NGC6503-like':  {'Vflat': 116.0, 'Rd': 2.2, 'Sigma0': 150.0, 'alpha': 0.55},
    'NGC3198-like':  {'Vflat': 150.0, 'Rd': 3.5, 'Sigma0': 80.0,  'alpha': 0.60},
    'NGC2841-like':  {'Vflat': 290.0, 'Rd': 4.5, 'Sigma0': 350.0, 'alpha': 0.35},
}

print('='*72)
print('EFC-BIC Reference Implementation Demo')
print('Magnusson (2026) – DOI: 10.6084/m9.figshare.32101111')
print('='*72)

results = {}
for name, p in templates.items():
    r = np.linspace(0.3, 5.0 * p['Rd'], 100)
    v = p['Vflat'] * np.tanh(r / p['Rd'])
    Sigma = p['Sigma0'] * np.exp(-r / p['Rd'])
    pi_profile = Pi_EFC(r, v, Sigma, p['Rd'], p['alpha'],
                        zeta=ZETA_DEFAULT, proxy_mode='shear')
    pmin = Pi_min_disk_window(r, pi_profile, p['Rd'])
    pproxy = Pi_proxy_scalar(p['Vflat'], p['Rd'], p['Sigma0'],
                             p['alpha'], zeta=ZETA_DEFAULT)
    results[name] = {'Pi_min': pmin, 'Pi_proxy': pproxy, 'profile': pi_profile, 'r': r}
    print(f'\n{name}:')
    print(f'  Vflat={p["Vflat"]} km/s  Rd={p["Rd"]} kpc  '
          f'Sigma0={p["Sigma0"]} Msun/pc^2  alpha={p["alpha"]}')
    print(f'  Pi_min (disk window [{DISK_WINDOW_INNER}-{DISK_WINDOW_OUTER}] Rd) = {pmin:.3f}')
    print(f'  Pi_proxy (scalar at 2.2 Rd) = {pproxy:.3f}')

# ---- Zeta scan showing kappa_eff^2 >= 0 constraint ----
print(f'\n--- Zeta scan for NGC6503-like (zeta_max = {ZETA_MAX}) ---')
for zeta in [0.0, 0.5, 1.0, ZETA_MAX]:
    p = templates['NGC6503-like']
    r = np.linspace(0.3, 5.0*p['Rd'], 100)
    v = p['Vflat'] * np.tanh(r / p['Rd'])
    Sigma = p['Sigma0'] * np.exp(-r / p['Rd'])
    pi = Pi_EFC(r, v, Sigma, p['Rd'], p['alpha'], zeta=zeta)
    pm = Pi_min_disk_window(r, pi, p['Rd'])
    print(f'  zeta={zeta:.2f}  ->  Pi_min={pm:.3f}')

# ---- Paper key statistics ----
print('\n--- Paper reported statistics ---')
print('  AUC (v0.1, bar prediction): 0.22  -> FALSIFIED')
print('  AUC (v0.2, resonance-aware): 0.31 -> FALSIFIED')
print('  Spearman rho(Pi_min, log Sigma_disk) = -0.71  (SPARC N=112)')
print('  Spearman rho(Pi_min, fgas)            = +0.65  (SPARC N=112)')
print('  xGASS replication rho(Pi_proxy, log Sigma*) = -0.49  (N=98)')
print('  xGASS replication rho(Pi_proxy, fgas)       = +0.67  (N=98)')

# ---- Optional plot ----
try:
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, (name, res) in zip(axes, results.items()):
        ax.plot(res['r'], res['profile'], 'b-', lw=2)
        Rd = templates[name]['Rd']
        ax.axvspan(DISK_WINDOW_INNER*Rd, DISK_WINDOW_OUTER*Rd,
                   alpha=0.15, color='green', label='disk window')
        ax.axhline(1.0, ls='--', color='red', alpha=0.5, label=r'$\Pi=1$')
        ax.set_title(name)
        ax.set_xlabel('R [kpc]')
        ax.set_ylabel(r'$\Pi_{\rm EFC}$')
        ax.set_ylim(0, min(25, np.nanmax(res['profile'])*1.2))
        ax.legend(fontsize=8)
    plt.suptitle(r'EFC-modified Toomre $\Pi_{\rm EFC}(R)$ profiles', fontsize=13)
    plt.tight_layout()
    plt.savefig('demo_Pi_EFC_profiles.png', dpi=150)
    print('\nPlot saved: demo_Pi_EFC_profiles.png')
    plt.show()
except ImportError:
    print('\nmatplotlib not available; skipping plot.')

print('\nDemo complete.')
