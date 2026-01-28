"""Fine-tune v1.1 to find passing combinations - focus on peak_ratio."""

import numpy as np
from efc_lensing_v1_1_nonlocal import (
    run_v11_nonlocal_test, generate_bullet_cluster_data, BETA
)

data = generate_bullet_cluster_data()

# Finer grid around best result
alpha_values = np.array([0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 2.5])
L0_values = np.array([200, 300, 500, 700, 1000])
w_values = np.array([5.0, 7.0, 10.0, 15.0, 20.0])

print("Fine-tuning v1.1 to find peak_ratio 0.9-1.2")
print(f"β = {BETA} (FIXED)")
print()

results = []
for alpha in alpha_values:
    for L0 in L0_values:
        for w in w_values:
            result = run_v11_nonlocal_test(data, alpha, L0, w)
            results.append(result)

# Find results close to passing
good_results = [r for r in results 
                if r.pass_peak_count 
                and r.pass_gas_offset 
                and r.pass_galaxy_proximity]

print(f"Results passing peak_count + gas_offset + galaxy_proximity: {len(good_results)}")
print()

if good_results:
    # Sort by how close peak_ratio is to 1.0
    good_results.sort(key=lambda r: abs(r.peak_ratio - 1.05))
    
    print("Top 10 closest to passing (by peak_ratio):")
    print("-" * 70)
    for r in good_results[:10]:
        status = "✓ PASS" if r.overall_pass else f"✗ ratio={r.peak_ratio:.3f}"
        print(f"α={r.alpha:.1f}, L₀={r.L0_kpc:.0f}, w={r.w:.0f} | "
              f"gal={[f'{d:.1f}' for d in r.galaxy_offsets_kpc]} | "
              f"gas={[f'{d:.1f}' for d in r.gas_offsets_kpc]} | "
              f"ratio={r.peak_ratio:.3f} | χ²={r.chi2:.2f} | {status}")

passing = [r for r in results if r.overall_pass]
print()
print(f"TOTAL PASSING: {len(passing)}")
