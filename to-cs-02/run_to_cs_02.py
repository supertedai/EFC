#!/usr/bin/env python3
"""
TO-CS-02: Full Execution Pipeline
==================================
Tests the EFC-C product hypothesis: C = Omega x Kappa
on the Chennu et al. 2016 propofol sedation dataset (20 subjects).

Usage:
    python run_to_cs_02.py --data-dir /path/to/Sedation-RestingState/

Locked parameters (pre-registered before seeing TE data):
    - Subject classification: >= 24/40 correct = responsive
    - Omega: SE (Welch, normalised), PE (order=3)
    - Kappa: TE (pyinform, k=3, 6 bins)
    - Bands: full (0.5-45 Hz), delta-free (4-40 Hz)
    - Bootstrap: N=10000, seed=42, percentile CI, Bonferroni alpha=0.0125
    - All predictions and decision tree locked before kappa computation

Author: Claude (Symbiose) for Morten Magnusson (EFC)
Date: 2026-02-07
"""

import argparse
import json
import os
import sys
import time
import numpy as np

from analysis.load_eeg import (
    load_roi_mapping, find_subject_files, load_subject_all_conditions
)
from analysis.compute_omega import compute_omega_all_conditions
from analysis.compute_kappa import compute_kappa_all_conditions
from analysis.statistics import (
    cohens_d, run_all_comparisons, score_decision_tree
)


# Locked subject classification (Appendix B.6 item 1)
RESPONSIVE_SUBJECTS = {1, 3, 7, 9, 11, 12, 13, 14, 15, 16, 18, 19, 20}
DROWSY_SUBJECTS = {2, 4, 5, 6, 8, 10, 17}

# Map from file subject numbers to study subject numbers
# File numbers: 02,03,05,06,07,08,09,10,13,14,18,20,22,23,24,25,26,27,28,29
FILE_TO_STUDY = {
    2: 1, 3: 2, 5: 3, 6: 4, 7: 5, 8: 6, 9: 7, 10: 8,
    13: 9, 14: 10, 18: 11, 20: 12, 22: 13, 23: 14,
    24: 15, 25: 16, 26: 17, 27: 18, 28: 19, 29: 20
}


def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def run_phase1_load(data_dir, roi_mapping):
    """Phase 1: Load & verify all subjects."""
    print_header("PHASE 1: LOAD & VERIFY")

    subject_files = find_subject_files(data_dir)
    print(f"Found {len(subject_files)} subjects in {data_dir}")

    for sub_num in sorted(subject_files.keys()):
        n_files = len(subject_files[sub_num])
        study_num = FILE_TO_STUDY.get(sub_num, '?')
        group = 'RESPONSIVE' if study_num in RESPONSIVE_SUBJECTS else 'DROWSY'
        print(f"  Sub-{sub_num:02d} (Study #{study_num}): {n_files} conditions — {group}")

    if len(subject_files) < 20:
        print(f"\n  WARNING: Expected 20 subjects, found {len(subject_files)}")

    return subject_files


def run_phase2_omega(subject_files, roi_mapping, epoch_length=10.0):
    """Phase 2: Compute Omega for all subjects."""
    print_header("PHASE 2: COMPUTE OMEGA (SE + PE)")

    all_omega = {}
    for sub_num in sorted(subject_files.keys()):
        study_num = FILE_TO_STUDY.get(sub_num, sub_num)
        print(f"  Processing Sub-{sub_num:02d} (Study #{study_num})...")
        t0 = time.time()

        subject_data = load_subject_all_conditions(
            subject_files[sub_num], roi_mapping, epoch_length
        )

        omega_full = compute_omega_all_conditions(subject_data, band='full')
        omega_df = compute_omega_all_conditions(subject_data, band='deltafree')

        all_omega[study_num] = {
            'full': omega_full,
            'deltafree': omega_df,
            'subject_data': subject_data,  # Keep for kappa computation
        }

        dt = time.time() - t0
        se_mod_full = omega_full.get('moderate', {}).get('SE_global', float('nan'))
        se_mod_df = omega_df.get('moderate', {}).get('SE_global', float('nan'))
        print(f"    SE(full)={se_mod_full:.4f}, SE(4-40)={se_mod_df:.4f} [{dt:.1f}s]")

    return all_omega


def run_phase3_kappa(all_omega):
    """Phase 3: Compute Kappa (TE) for all subjects."""
    print_header("PHASE 3: COMPUTE KAPPA (TRANSFER ENTROPY)")

    all_kappa = {}
    for study_num in sorted(all_omega.keys()):
        print(f"  Processing Study #{study_num}...")
        t0 = time.time()

        subject_data = all_omega[study_num]['subject_data']
        kappa = compute_kappa_all_conditions(subject_data, band='full')
        all_kappa[study_num] = kappa

        kappa_mod = kappa.get('moderate', {}).get('kappa_global', float('nan'))
        dt = time.time() - t0
        print(f"    kappa_global(moderate)={kappa_mod:.5f} [{dt:.1f}s]")

    return all_kappa


def run_phase4_dissociation(all_omega, all_kappa):
    """Phase 4: Dissociation check — corr(Omega, Kappa)."""
    print_header("PHASE 4: DISSOCIATION CHECK")

    omega_values = []
    kappa_values = []

    for study_num in sorted(all_omega.keys()):
        for cond in ['baseline', 'mild', 'moderate', 'recovery']:
            if cond in all_omega[study_num]['full'] and cond in all_kappa[study_num]:
                omega_values.append(all_omega[study_num]['full'][cond]['SE_global'])
                kappa_values.append(all_kappa[study_num][cond]['kappa_global'])

    omega_arr = np.array(omega_values)
    kappa_arr = np.array(kappa_values)
    correlation = np.corrcoef(omega_arr, kappa_arr)[0, 1]

    print(f"  corr(Omega, Kappa) = {correlation:.4f} (N={len(omega_arr)} points)")
    if correlation > 0.8:
        print("  STOP RULE TRIGGERED: corr > 0.8 — dataset unsuitable!")
    elif correlation > 0.6:
        print("  WARNING: Moderate correlation — proceed with caution")
    else:
        print("  PASS: Sufficient dissociation (corr < 0.6)")

    return correlation


def run_phase5_comparisons(all_omega, all_kappa):
    """Phase 5: Four-way comparison at moderate sedation."""
    print_header("PHASE 5: FOUR-WAY COMPARISON (responsive vs drowsy at moderate)")

    # Collect subject-level values at moderate sedation
    resp_omega_full = []
    resp_omega_df = []
    resp_kappa = []
    drowsy_omega_full = []
    drowsy_omega_df = []
    drowsy_kappa = []

    for study_num in sorted(all_omega.keys()):
        if 'moderate' not in all_omega[study_num]['full']:
            print(f"  WARNING: No moderate condition for Study #{study_num}")
            continue

        se_full = all_omega[study_num]['full']['moderate']['SE_global']
        se_df = all_omega[study_num]['deltafree']['moderate']['SE_global']
        kappa_g = all_kappa[study_num]['moderate']['kappa_global']

        if study_num in RESPONSIVE_SUBJECTS:
            resp_omega_full.append(se_full)
            resp_omega_df.append(se_df)
            resp_kappa.append(kappa_g)
        elif study_num in DROWSY_SUBJECTS:
            drowsy_omega_full.append(se_full)
            drowsy_omega_df.append(se_df)
            drowsy_kappa.append(kappa_g)

    resp_omega_full = np.array(resp_omega_full)
    resp_omega_df = np.array(resp_omega_df)
    resp_kappa = np.array(resp_kappa)
    drowsy_omega_full = np.array(drowsy_omega_full)
    drowsy_omega_df = np.array(drowsy_omega_df)
    drowsy_kappa = np.array(drowsy_kappa)

    print(f"  Responsive: N={len(resp_omega_full)}")
    print(f"  Drowsy: N={len(drowsy_omega_full)}")

    # Individual effect sizes
    d_omega_full = cohens_d(resp_omega_full, drowsy_omega_full)
    d_omega_df = cohens_d(resp_omega_df, drowsy_omega_df)
    d_kappa = cohens_d(resp_kappa, drowsy_kappa)

    C_resp_df = resp_omega_df * resp_kappa
    C_drowsy_df = drowsy_omega_df * drowsy_kappa
    C_resp_full = resp_omega_full * resp_kappa
    C_drowsy_full = drowsy_omega_full * drowsy_kappa

    d_C_df = cohens_d(C_resp_df, C_drowsy_df)
    d_C_full = cohens_d(C_resp_full, C_drowsy_full)

    # Regional measures
    print("\n  --- Individual Effect Sizes ---")
    print(f"  Omega_SE (full, 0.5-45 Hz):    d = {d_omega_full:.3f}")
    print(f"  Omega_SE (delta-free, 4-40 Hz): d = {d_omega_df:.3f}")
    print(f"  Kappa (global):                 d = {d_kappa:.3f}")
    print(f"  C = Omega(full) x Kappa:        d = {d_C_full:.3f}")
    print(f"  C = Omega(4-40) x Kappa:        d = {d_C_df:.3f}")

    # Hub-level kappa (P_L)
    resp_kappa_pl = []
    drowsy_kappa_pl = []
    for study_num in sorted(all_kappa.keys()):
        if 'moderate' not in all_kappa[study_num]:
            continue
        kappa_hub_pl = all_kappa[study_num]['moderate']['kappa_hub'].get('P_L', float('nan'))
        if study_num in RESPONSIVE_SUBJECTS:
            resp_kappa_pl.append(kappa_hub_pl)
        elif study_num in DROWSY_SUBJECTS:
            drowsy_kappa_pl.append(kappa_hub_pl)

    if resp_kappa_pl and drowsy_kappa_pl:
        d_kappa_pl = cohens_d(np.array(resp_kappa_pl), np.array(drowsy_kappa_pl))
        print(f"  Kappa_hub(P_L):                 d = {d_kappa_pl:.3f}")

    # Run locked comparisons
    print("\n  --- Bootstrap Comparisons (N=10000, seed=42) ---")
    comparisons = run_all_comparisons(
        resp_omega_full, drowsy_omega_full,
        resp_omega_df, drowsy_omega_df,
        resp_kappa, drowsy_kappa
    )

    for comp_id in ['a', 'b', 'c', 'd']:
        comp = comparisons[comp_id]
        status = "PASS" if comp['beats'] else "FAIL"
        print(f"\n  ({comp_id}) {comp['description']}")
        print(f"      d(A) = {comp['d_A']:.3f}, d(B) = {comp['d_B']:.3f}")
        print(f"      Delta_d = {comp['delta_d']:.3f} [{comp['delta_d_ci_lower']:.3f}, {comp['delta_d_ci_upper']:.3f}]")
        print(f"      p = {comp['p_value']:.4f} (threshold: {0.0125})")
        print(f"      Result: {status}")

    return comparisons


def run_phase6_scoring(correlation, comparisons):
    """Phase 6: Apply decision tree and score."""
    print_header("PHASE 6: DECISION TREE SCORING")

    score = score_decision_tree(correlation, comparisons)

    print(f"  GRADE: {score['grade']}")
    print(f"  {score['explanation']}")
    print()

    # Prediction checks
    print("  --- Prediction Checks ---")
    if 'a' in comparisons:
        print(f"  kappa-1 (Parietal hub): See kappa_hub(P_L) above")
        print(f"  kappa-3 (Occipital null): Check C_occipital < C_PL")
        print(f"  C-1 (Product beats delta-free Omega): {'PASS' if comparisons['a']['beats'] else 'FAIL'}")
        if 'c' in comparisons:
            print(f"  C-2 (Product beats full-band Omega): {'PASS' if comparisons['c']['beats'] else 'FAIL'}")

    return score


def save_results(output_dir, all_omega, all_kappa, correlation, comparisons, score):
    """Save all results to JSON."""
    os.makedirs(output_dir, exist_ok=True)

    # Prepare serializable results
    results = {
        'metadata': {
            'date': '2026-02-07',
            'protocol': 'TO-CS-02',
            'version': '2.0',
            'n_subjects': len(all_omega),
            'n_responsive': len(RESPONSIVE_SUBJECTS),
            'n_drowsy': len(DROWSY_SUBJECTS),
        },
        'dissociation': {
            'correlation_omega_kappa': float(correlation),
            'stop_rule_triggered': correlation > 0.8,
        },
        'omega_summary': {},
        'kappa_summary': {},
        'comparisons': {},
        'score': {
            'grade': score['grade'],
            'explanation': score['explanation'],
        },
    }

    # Omega summary per subject
    for study_num in sorted(all_omega.keys()):
        results['omega_summary'][str(study_num)] = {}
        for cond in ['baseline', 'mild', 'moderate', 'recovery']:
            if cond in all_omega[study_num]['full']:
                results['omega_summary'][str(study_num)][cond] = {
                    'SE_full': float(all_omega[study_num]['full'][cond]['SE_global']),
                    'SE_deltafree': float(all_omega[study_num]['deltafree'][cond]['SE_global']),
                    'PE': float(all_omega[study_num]['full'][cond]['PE_global']),
                }

    # Kappa summary per subject
    for study_num in sorted(all_kappa.keys()):
        results['kappa_summary'][str(study_num)] = {}
        for cond in ['baseline', 'mild', 'moderate', 'recovery']:
            if cond in all_kappa[study_num]:
                k = all_kappa[study_num][cond]
                results['kappa_summary'][str(study_num)][cond] = {
                    'kappa_global': float(k['kappa_global']),
                    'kappa_hub_P_L': float(k['kappa_hub'].get('P_L', float('nan'))),
                    'kappa_hub_C_R': float(k['kappa_hub'].get('C_R', float('nan'))),
                    'A_FP': float(k['A_FP']),
                    'A_CP': float(k['A_CP']),
                }

    # Comparisons
    for comp_id in ['a', 'b', 'c', 'd']:
        if comp_id in comparisons:
            c = comparisons[comp_id]
            results['comparisons'][comp_id] = {
                'description': c['description'],
                'd_A': float(c['d_A']),
                'd_B': float(c['d_B']),
                'delta_d': float(c['delta_d']),
                'ci_lower': float(c['delta_d_ci_lower']),
                'ci_upper': float(c['delta_d_ci_upper']),
                'p_value': float(c['p_value']),
                'beats': bool(c['beats']),
            }

    output_path = os.path.join(output_dir, 'to_cs_02_results.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to: {output_path}")

    return results


def main():
    parser = argparse.ArgumentParser(description='TO-CS-02: EFC-C Product Hypothesis Test')
    parser.add_argument('--data-dir', required=True,
                        help='Path to Sedation-RestingState directory with .set/.fdt files')
    parser.add_argument('--output-dir', default='results',
                        help='Output directory for results (default: results/)')
    parser.add_argument('--epoch-length', type=float, default=10.0,
                        help='Epoch length in seconds (default: 10.0)')
    parser.add_argument('--skip-kappa', action='store_true',
                        help='Skip kappa computation (omega only)')
    args = parser.parse_args()

    print_header("TO-CS-02: EFC-C PRODUCT HYPOTHESIS TEST")
    print("  Testing: C = Omega x Kappa on Chennu et al. 2016 propofol sedation data")
    print("  All parameters pre-registered (Appendix B)")
    print(f"  Data directory: {args.data_dir}")

    # Load config
    roi_mapping = load_roi_mapping()

    # Phase 1: Load & verify
    subject_files = run_phase1_load(args.data_dir, roi_mapping)

    # Phase 2: Compute Omega
    all_omega = run_phase2_omega(subject_files, roi_mapping, args.epoch_length)

    if args.skip_kappa:
        print_header("SKIPPING KAPPA (--skip-kappa flag)")
        print("  Run without --skip-kappa to compute transfer entropy and complete the test.")
        return

    # Phase 3: Compute Kappa
    all_kappa = run_phase3_kappa(all_omega)

    # Phase 4: Dissociation check
    correlation = run_phase4_dissociation(all_omega, all_kappa)

    # Phase 5: Comparisons
    comparisons = run_phase5_comparisons(all_omega, all_kappa)

    # Phase 6: Scoring
    score = run_phase6_scoring(correlation, comparisons)

    # Save results
    output_dir = os.path.join(os.path.dirname(__file__), args.output_dir)
    save_results(output_dir, all_omega, all_kappa, correlation, comparisons, score)

    print_header("DONE")


if __name__ == '__main__':
    main()
