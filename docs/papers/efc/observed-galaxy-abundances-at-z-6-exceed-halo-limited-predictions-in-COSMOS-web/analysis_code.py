#!/usr/bin/env python3
"""
Reproducible Analysis Code
Observed Galaxy Abundances at z > 6 Exceed Halo-Limited Predictions in COSMOS-Web
Magnusson (2026) - DOI: 10.6084/m9.figshare.31059964
"""

import pandas as pd
import numpy as np
from scipy import stats

# Survey parameters
AREA = 0.54  # deg²

# ΛCDM predictions (Behroozi+19 upper envelope)
LCDM_PREDICTIONS = {
    (5, 6): 200,
    (6, 7): 80,
    (7, 8): 25,
    (8, 9): 8,
    (9, 10): 2,
}

# Halo limits (ε=1, Sheth-Tormen + Planck 2018)
HALO_LIMITS = {
    (5, 6): 1500,
    (6, 7): 800,
    (7, 8): 400,
    (8, 9): 200,
    (9, 10): 100,
}

def analyze_cosmos2025(filepath):
    """Main analysis pipeline."""
    
    # Load data
    df = pd.read_csv(filepath)
    df = df.replace(-99, np.nan)
    
    # Filter valid
    df = df[(df['z_phot'] > 5) & (df['mass_med'] >= 9.0)].copy()
    
    print(f"Loaded {len(df)} massive galaxies (log M > 9)")
    
    # Calculate sSFR
    df['log_ssfr'] = df['sfr_med'] - df['mass_med']
    
    # Number density comparison
    print("\n" + "="*60)
    print("ΛCDM COMPARISON")
    print("="*60)
    
    for (z_min, z_max), lcdm in LCDM_PREDICTIONS.items():
        mask = (df['z_phot'] >= z_min) & (df['z_phot'] < z_max)
        n_obs = mask.sum()
        n_density = n_obs / AREA
        halo_lim = HALO_LIMITS[(z_min, z_max)]
        
        print(f"\nz = {z_min}-{z_max}:")
        print(f"  N_obs = {n_obs}")
        print(f"  n_obs = {n_density:.0f} deg⁻²")
        print(f"  Ratio vs ΛCDM: {n_density/lcdm:.1f}×")
        print(f"  Ratio vs halo limit: {n_density/halo_lim:.1f}×")
    
    # sSFR correlation
    print("\n" + "="*60)
    print("sSFR ANALYSIS")
    print("="*60)
    
    valid = df[df['log_ssfr'].notna()]
    rho, p = stats.spearmanr(valid['z_phot'], valid['log_ssfr'])
    print(f"\nSpearman ρ = {rho:.3f}")
    print(f"p-value = {p:.2e}")
    
    return df

if __name__ == '__main__':
    df = analyze_cosmos2025('supplementary_data.csv')
