"""
Sensitivity analysis: How does w depend on input parameters?
"""

import numpy as np

def compression_ratio(M, gamma=5/3):
    return (gamma + 1) * M**2 / ((gamma - 1) * M**2 + 2)

def w_from_physics(M, t_Myr, sigma_v, L0, eta):
    r = compression_ratio(M)
    return r * np.exp(t_Myr * sigma_v / (eta * L0))

eta = 197.67

print("SENSITIVITY ANALYSIS")
print("=" * 60)
print()

# Base case: Bullet
print("Base (Bullet): M=3, t=150, σ_v=500, L₀=200")
print(f"  w = {w_from_physics(3, 150, 500, 200, eta):.1f}")
print()

# Vary t for Abell 520
print("Abell 520 - sensitivity to t:")
for t in [100, 150, 200, 250, 300]:
    w = w_from_physics(2.5, t, 600, 160, eta)
    print(f"  t = {t} Myr → w = {w:.0f}")

print()

# What t gives w ~ 20-50 for A520?
print("Abell 520 - what t gives reasonable w?")
for w_target in [20, 30, 50, 100]:
    # w = r * exp(t*σ/(η*L))
    # ln(w/r) = t*σ/(η*L)
    # t = η*L*ln(w/r) / σ
    r = compression_ratio(2.5)
    t_needed = eta * 160 * np.log(w_target/r) / 600
    print(f"  w = {w_target} requires t = {t_needed:.0f} Myr")

print()
print("=" * 60)
print("ISSUE: The exponential in g_mix makes w VERY sensitive to t/τ_mix")
print()
print(f"τ_mix (Bullet) = η × L₀ / σ_v = {eta * 200 / 500:.0f} Myr")
print(f"τ_mix (A520) = η × L₀ / σ_v = {eta * 160 / 600:.0f} Myr")
print()
print("If A520 is really t=300 Myr old, and τ_mix=53 Myr,")
print("then t/τ_mix = 5.7, giving exp(5.7) = 300×")
print()
print("This suggests either:")
print("  1. A520 age estimate is wrong (should be ~150 Myr)")
print("  2. Model needs adjustment (weaker t-dependence)")
print("  3. Or A520 really DOES have extreme gas/stellar separation")
