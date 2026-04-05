#!/usr/bin/env python3
"""Demonstration: EFC Screening Model Multi-Scale Validation.

DOI: 10.6084/m9.figshare.31940469
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from efc_screening import (
    EFCScreening, CrossScaleConsistency, KiDS1000Analysis,
    BulletClusterInterpretation, HubbleTension, ClosureConjecture,
)

def demo_rar():
    print("=" * 70)
    print("SPARC RAR FIT: ln(mu) = k * ln(1 + g†/g_bar)")
    print("=" * 70)
    print()
    model = EFCScreening()
    summary = model.fit_summary()
    print(f"  k = {summary['k']['value']} +/- {summary['k']['error']}")
    print(f"  g† = {summary['g_dagger']['value']:.2e} +/- {summary['g_dagger']['error']:.2e} m/s²")
    print(f"  sigma_int = {summary['sigma_int']['dex']:.2f} dex")
    print(f"  N = {summary['n_galaxies']} galaxies, {summary['n_data_points']} points")
    print()
    g_values = [1e-12, 1e-11, 1e-10, 1e-9, 1e-8]
    print(f"{'g_bar (m/s²)':>14s} {'mu':>10s} {'g_obs':>14s} {'ln(mu)':>10s}")
    print("-" * 52)
    for g in g_values:
        print(f"{g:14.2e} {model.mu(g):10.4f} {model.g_obs(g):14.4e} {model.ln_mu(g):10.4f}")
    print()

def demo_cross_scale():
    print("=" * 70)
    print("CROSS-SCALE CONSISTENCY: C = k/a_G")
    print("=" * 70)
    print()
    cs = CrossScaleConsistency()
    print(f"  k (galactic, SPARC):     {cs.k}")
    print(f"  a_G (cosmological, H0):  {cs.a_G}")
    print(f"  C = k/a_G = {cs.C:.2f} +/- {cs.C_error:.2f}")
    print()
    ct = cs.closure_test()
    print(f"  Closure conjecture: C = 2e-1 = {ct['C_conjectured']:.3f}")
    print(f"  Deviation: {ct['deviation_sigma']:.1f} sigma")
    print(f"  Consistent: {ct['consistent']}")
    print()

def demo_kids():
    print("=" * 70)
    print("KiDS-1000 LENSING (Case A)")
    print("=" * 70)
    print()
    kids = KiDS1000Analysis()
    s = kids.summary()
    print(f"  alpha_L2 = {s['alpha_L2']}")
    print(f"  Delta(-2 ln L) = {s['delta_neg2lnL']} vs LCDM")
    print(f"  S8 (EFC Case A) = {s['S8_efc_case_a']}")
    print(f"  S8 (LCDM) = {s['S8_lcdm']}")
    print(f"  Note: {s['note']}")
    print()
    landscape = kids.s8_landscape()
    print("  Stage-III S8 landscape (2025-2026):")
    for key, val in landscape.items():
        s8 = val.get('S8', val.get('sigma8', '?'))
        print(f"    {key}: S8 = {s8}")
    print()

def demo_h0():
    print("=" * 70)
    print("HUBBLE TENSION: a_G = 2 * a_H0")
    print("=" * 70)
    print()
    h = HubbleTension()
    d = h.derivation_chain()
    print(f"  ln(73.0/67.4) = {d['ln_ratio']:.4f}")
    print(f"  a_H0 = {d['a_H0']:.4f}")
    print(f"  a_G = 2 * a_H0 = {d['a_G']:.4f}")
    print(f"  {d['note']}")
    print()

def demo_closure():
    print("=" * 70)
    print("CLOSURE CONJECTURES")
    print("=" * 70)
    print()
    cc = ClosureConjecture()
    r1 = cc.H0_from_g_dagger(2.51e-10)
    print(f"  CC1: g† = c*H0/e")
    print(f"    H0 predicted = {r1['H0_predicted']:.1f} +/- {r1['H0_error']} km/s/Mpc")
    print()
    r2 = cc.C_conjecture()
    print(f"  CC2: C = 2e-1 = {r2['C_conjectured']:.3f}")
    print(f"    C observed = {r2['C_observed']} +/- {r2['C_error']}")
    print()

def demo_bullet():
    print("=" * 70)
    print("BULLET CLUSTER (qualitative)")
    print("=" * 70)
    print()
    bc = BulletClusterInterpretation.effective_potential_description()
    print(f"  Phi_eff = Phi_N + alpha * nabla S")
    print(f"  Shocked gas: {bc['mechanism']['shocked_gas']}")
    print(f"  Galaxies:    {bc['mechanism']['galaxies']}")
    print(f"  Prediction:  {bc['prediction']}")
    print(f"  Offset:      {bc['offset']}")
    print(f"  Status:      {bc['status']}")
    print()

def demo_falsification():
    print("=" * 70)
    print("FALSIFICATION CRITERIA")
    print("=" * 70)
    print()
    criteria = [
        "F1: k outside [0.30, 0.55] from independent SPARC re-analysis",
        "F2: g† inconsistent with c*H0/e at >3 sigma",
        "F3: No lensing Sigma(k,z) in Stage-IV data (Euclid, LSST)",
        "F4: C = k/a_G inconsistent with 2e-1 at >3 sigma",
        "F5: Bullet Cluster offset without entropy-gradient coupling",
    ]
    for c in criteria:
        print(f"  {c}")
    print()

if __name__ == "__main__":
    demo_rar()
    demo_cross_scale()
    demo_kids()
    demo_h0()
    demo_closure()
    demo_bullet()
    demo_falsification()
    print("All demonstrations complete.")
