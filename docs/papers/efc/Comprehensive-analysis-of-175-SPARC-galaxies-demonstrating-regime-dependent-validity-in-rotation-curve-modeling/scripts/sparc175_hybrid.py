"""
SPARC175 HYBRID ANALYSIS
Combining Svar 2's thoroughness with Svar 1's simplicity

Day 1: QC + Data Preparation
"""

import numpy as np
import json
from collections import defaultdict
from pathlib import Path

print("="*80)
print("SPARC175 HYBRID ANALYSIS - DAY 1: DATA QC")
print("="*80)

# ============================================================================
# PHASE 0: DATA QC (from Svar 2)
# ============================================================================

print("\n[PHASE 0] Data Quality Control")
print("-"*80)

def load_sparc_with_qc(filepath='/home/claude/sparc-data/sparc_rotation_curves.dat'):
    """
    Load SPARC data with explicit QC checks
    
    Returns:
    - galaxies: dict of galaxy data
    - qc_log: quality control information per galaxy
    """
    
    raw_data = defaultdict(lambda: {
        'r': [], 'v_obs': [], 'v_err': [], 
        'v_gas': [], 'v_disk': [], 'v_bulge': []
    })
    
    qc_log = {}
    
    # Load raw data
    with open(filepath) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 9:
                continue
            
            name = parts[0]
            try:
                raw_data[name]['r'].append(float(parts[2]))
                raw_data[name]['v_obs'].append(float(parts[3]))
                raw_data[name]['v_err'].append(float(parts[4]))
                raw_data[name]['v_gas'].append(float(parts[5]))
                raw_data[name]['v_disk'].append(float(parts[6]))
                raw_data[name]['v_bulge'].append(float(parts[7]))
            except (ValueError, IndexError):
                continue
    
    # QC each galaxy
    galaxies = {}
    
    for name, data in raw_data.items():
        # Convert to numpy
        for key in data:
            data[key] = np.array(data[key])
        
        r = data['r']
        v_obs = data['v_obs']
        v_err = data['v_err']
        
        # QC checks
        qc = {
            'n_points': len(r),
            'r_min': r.min() if len(r) > 0 else np.nan,
            'r_max': r.max() if len(r) > 0 else np.nan,
            'v_obs_min': v_obs.min() if len(v_obs) > 0 else np.nan,
            'v_obs_max': v_obs.max() if len(v_obs) > 0 else np.nan,
            'median_v_err': np.median(v_err) if len(v_err) > 0 else np.nan,
            'max_v_err': v_err.max() if len(v_err) > 0 else np.nan,
            'issues': []
        }
        
        # Flag issues
        if qc['n_points'] < 5:
            qc['issues'].append('too_few_points')
        
        if np.any(np.isnan(v_obs)) or np.any(np.isinf(v_obs)):
            qc['issues'].append('invalid_v_obs')
        
        if np.any(v_err <= 0):
            qc['issues'].append('invalid_errors')
        
        if np.any(v_obs < 0):
            qc['issues'].append('negative_velocity')
        
        # Relative error check
        rel_err = v_err / np.maximum(v_obs, 1e-10)
        if np.median(rel_err) > 0.5:
            qc['issues'].append('high_relative_error')
        
        # Accept if no critical issues
        critical_issues = {'invalid_v_obs', 'invalid_errors', 'negative_velocity'}
        if not any(issue in critical_issues for issue in qc['issues']):
            galaxies[name] = data
        
        qc['accepted'] = name in galaxies
        qc_log[name] = qc
    
    return galaxies, qc_log

print("Loading data with QC...")
galaxies, qc_log = load_sparc_with_qc()

# QC Summary
n_total = len(qc_log)
n_accepted = sum(1 for qc in qc_log.values() if qc['accepted'])
n_rejected = n_total - n_accepted

print(f"\n✓ QC Complete:")
print(f"  Total galaxies: {n_total}")
print(f"  Accepted: {n_accepted}")
print(f"  Rejected: {n_rejected}")

# Issue breakdown
all_issues = []
for qc in qc_log.values():
    all_issues.extend(qc['issues'])

if all_issues:
    from collections import Counter
    issue_counts = Counter(all_issues)
    print(f"\n  Issue breakdown:")
    for issue, count in issue_counts.most_common():
        print(f"    {issue}: {count}")

# Save QC log
qc_output = {
    'summary': {
        'n_total': n_total,
        'n_accepted': n_accepted,
        'n_rejected': n_rejected
    },
    'per_galaxy': qc_log
}

with open('/home/claude/sparc175_qc.json', 'w') as f:
    json.dump(qc_output, f, indent=2, default=lambda x: float(x) if isinstance(x, np.floating) else x)

print(f"\n✓ QC log saved: sparc175_qc.json")

# ============================================================================
# DATA PREPARATION
# ============================================================================

print("\n[DATA PREP] Computing statistics...")

stats = {
    'n_galaxies': len(galaxies),
    'n_points_total': sum(len(g['r']) for g in galaxies.values()),
    'n_points_mean': np.mean([len(g['r']) for g in galaxies.values()]),
    'n_points_std': np.std([len(g['r']) for g in galaxies.values()]),
    'n_points_min': min(len(g['r']) for g in galaxies.values()),
    'n_points_max': max(len(g['r']) for g in galaxies.values())
}

print(f"\n✓ Dataset statistics:")
print(f"  Galaxies: {stats['n_galaxies']}")
print(f"  Total points: {stats['n_points_total']}")
print(f"  Points/galaxy: {stats['n_points_mean']:.1f} ± {stats['n_points_std']:.1f}")
print(f"  Range: [{stats['n_points_min']}, {stats['n_points_max']}]")

# Save clean data
print(f"\n[SAVE] Writing clean dataset...")

# Convert to JSON-serializable format
clean_data = {}
for name, data in galaxies.items():
    clean_data[name] = {
        k: v.tolist() for k, v in data.items()
    }

with open('/home/claude/sparc175_clean.json', 'w') as f:
    json.dump(clean_data, f, indent=2)

print(f"✓ Clean data saved: sparc175_clean.json ({len(clean_data)} galaxies)")

print("\n" + "="*80)
print("DAY 1 COMPLETE: QC + Data Preparation")
print("="*80)
print(f"\nNext: Day 2 - Fit all {len(galaxies)} galaxies with residual diagnostics")

