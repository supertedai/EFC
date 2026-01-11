"""
SPARC175 HYBRID ANALYSIS - Day 4
Visualization: 3 core figures + failure taxonomy
"""

import numpy as np
import json
import matplotlib.pyplot as plt
from collections import Counter

print("="*80)
print("SPARC175 HYBRID ANALYSIS - DAY 4: VISUALIZATION")
print("="*80)

# Load classified results
with open('/home/claude/sparc175_classified.json') as f:
    data = json.load(f)

results = data['results']

print(f"\nLoaded classified results for {len(results)} galaxies")

# ============================================================================
# FIGURE 1: Regime Distribution
# ============================================================================

print("\n[FIGURE 1] Regime distribution...")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Subplot 1: Regime counts
regime_counts = Counter(r['regime'] for r in results.values())
regimes = ['FLOW', 'TRANSITION', 'LATENT']
counts = [regime_counts[r] for r in regimes]
colors = ['#2ecc71', '#f39c12', '#e74c3c']

axes[0].bar(regimes, counts, color=colors, alpha=0.7, edgecolor='black')
axes[0].set_ylabel('Number of galaxies')
axes[0].set_title('Regime Distribution (N=175)')
axes[0].grid(axis='y', alpha=0.3)

# Add percentages
for i, (regime, count) in enumerate(zip(regimes, counts)):
    pct = 100 * count / len(results)
    axes[0].text(i, count + 2, f'{pct:.1f}%', ha='center', fontweight='bold')

# Subplot 2: EFC success rate by regime
success_rates = []
for regime in regimes:
    regime_results = [r for r in results.values() if r['regime'] == regime]
    efc_wins = sum(1 for r in regime_results if r['comparison']['winner'] == 'EFC')
    success_rates.append(100 * efc_wins / len(regime_results) if regime_results else 0)

axes[1].bar(regimes, success_rates, color=colors, alpha=0.7, edgecolor='black')
axes[1].set_ylabel('EFC win rate (%)')
axes[1].set_title('EFC Success Rate by Regime')
axes[1].set_ylim(0, 110)
axes[1].grid(axis='y', alpha=0.3)
axes[1].axhline(50, color='gray', linestyle='--', alpha=0.5)

# Add values
for i, rate in enumerate(success_rates):
    axes[1].text(i, rate + 3, f'{rate:.1f}%', ha='center', fontweight='bold')

# Subplot 3: Chi-squared by regime
chi2_by_regime = {regime: [] for regime in regimes}
for r in results.values():
    if r['efc']['success'] and r['regime'] in regimes:
        chi2_by_regime[r['regime']].append(r['efc']['chi2_red'])

bp = axes[2].boxplot([chi2_by_regime[r] for r in regimes], 
                      labels=regimes,
                      patch_artist=True,
                      showfliers=False)

for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

axes[2].set_ylabel('χ²/dof (EFC-fit)')
axes[2].set_title('Fit Quality by Regime')
axes[2].set_yscale('log')
axes[2].grid(axis='y', alpha=0.3)
axes[2].axhline(10, color='red', linestyle='--', alpha=0.5, label='χ²/dof=10')

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/sparc175_regime_distribution.png', dpi=150, bbox_inches='tight')
print("✓ Saved: sparc175_regime_distribution.png")
plt.close()

# ============================================================================
# FIGURE 2: ΔAIC vs Latent Proxy L
# ============================================================================

print("\n[FIGURE 2] ΔAIC vs Latent proxy...")

fig, ax = plt.subplots(figsize=(10, 8))

# Collect data
plot_data = {regime: {'delta_aic': [], 'L': []} for regime in regimes}

for r in results.values():
    if r['efc']['success'] and r['regime'] in regimes:
        if np.isfinite(r['comparison']['delta_aic']):
            plot_data[r['regime']]['delta_aic'].append(r['comparison']['delta_aic'])
            plot_data[r['regime']]['L'].append(r['latent']['L'])

# Plot each regime
for regime, color in zip(regimes, colors):
    if plot_data[regime]['L']:
        ax.scatter(plot_data[regime]['L'], 
                  plot_data[regime]['delta_aic'],
                  c=color, 
                  label=regime,
                  alpha=0.6,
                  s=50,
                  edgecolors='black',
                  linewidth=0.5)

# Decision boundaries
ax.axhline(-10, color='green', linestyle='--', alpha=0.5, label='ΔAIC = -10 (EFC favored)')
ax.axhline(+10, color='red', linestyle='--', alpha=0.5, label='ΔAIC = +10 (ΛCDM favored)')
ax.axhline(0, color='gray', linestyle='-', alpha=0.3)

# Regime boundaries (approximate from data)
flow_L_max = np.percentile([r['latent']['L'] for r in results.values() if r['regime'] == 'FLOW'], 75)
latent_L_min = np.percentile([r['latent']['L'] for r in results.values() if r['regime'] == 'LATENT'], 25)

ax.axvline(flow_L_max, color='green', linestyle=':', alpha=0.3, label=f'L ~ {flow_L_max:.2f}')
ax.axvline(latent_L_min, color='red', linestyle=':', alpha=0.3, label=f'L ~ {latent_L_min:.2f}')

ax.set_xlabel('Latent Proxy L', fontsize=12)
ax.set_ylabel('ΔAIC (EFC - ΛCDM)', fontsize=12)
ax.set_title('Model Preference vs Structural Complexity\n(N=175 SPARC galaxies)', fontsize=14, fontweight='bold')
ax.legend(loc='best', framealpha=0.9)
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/sparc175_aic_vs_latent.png', dpi=150, bbox_inches='tight')
print("✓ Saved: sparc175_aic_vs_latent.png")
plt.close()

# ============================================================================
# FIGURE 3: Success Rate by L Bins
# ============================================================================

print("\n[FIGURE 3] Success rate by L bins...")

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Create L bins
L_values = [r['latent']['L'] for r in results.values() if r['efc']['success']]
L_bins = [0, 0.25, 0.35, 0.45, 1.0]
L_labels = ['L<0.25\n(Low)', '0.25-0.35\n(Mid-Low)', '0.35-0.45\n(Mid-High)', 'L>0.45\n(High)']

bin_data = {label: {'total': 0, 'efc_wins': 0, 'L_mean': 0, 'L_vals': []} 
            for label in L_labels}

for r in results.values():
    if not r['efc']['success']:
        continue
    
    L = r['latent']['L']
    
    # Find bin
    for i in range(len(L_bins)-1):
        if L_bins[i] <= L < L_bins[i+1]:
            label = L_labels[i]
            bin_data[label]['total'] += 1
            bin_data[label]['L_vals'].append(L)
            if r['comparison']['winner'] == 'EFC':
                bin_data[label]['efc_wins'] += 1
            break

# Compute success rates
success_rates_binned = []
bin_sizes = []
for label in L_labels:
    if bin_data[label]['total'] > 0:
        rate = 100 * bin_data[label]['efc_wins'] / bin_data[label]['total']
        success_rates_binned.append(rate)
        bin_sizes.append(bin_data[label]['total'])
    else:
        success_rates_binned.append(0)
        bin_sizes.append(0)

# Subplot 1: Success rate
colors_gradient = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(L_labels)))

axes[0].bar(L_labels, success_rates_binned, color=colors_gradient, alpha=0.7, edgecolor='black')
axes[0].set_ylabel('EFC Win Rate (%)', fontsize=12)
axes[0].set_xlabel('Latent Proxy Bins', fontsize=12)
axes[0].set_title('EFC Success Rate vs Structural Complexity', fontsize=13, fontweight='bold')
axes[0].set_ylim(0, 110)
axes[0].grid(axis='y', alpha=0.3)
axes[0].axhline(50, color='gray', linestyle='--', alpha=0.5)

# Add annotations
for i, (rate, size) in enumerate(zip(success_rates_binned, bin_sizes)):
    axes[0].text(i, rate + 3, f'{rate:.1f}%\n(n={size})', ha='center', fontsize=9)

# Subplot 2: Sample distribution
axes[1].bar(L_labels, bin_sizes, color=colors_gradient, alpha=0.7, edgecolor='black')
axes[1].set_ylabel('Number of Galaxies', fontsize=12)
axes[1].set_xlabel('Latent Proxy Bins', fontsize=12)
axes[1].set_title('Sample Distribution', fontsize=13, fontweight='bold')
axes[1].grid(axis='y', alpha=0.3)

for i, size in enumerate(bin_sizes):
    axes[1].text(i, size + 1, str(size), ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/sparc175_success_by_bins.png', dpi=150, bbox_inches='tight')
print("✓ Saved: sparc175_success_by_bins.png")
plt.close()

# ============================================================================
# BONUS: Failure Taxonomy Examples
# ============================================================================

print("\n[BONUS] Creating failure taxonomy examples...")

# Find worst failures in each category
latent_failures = [(name, r) for name, r in results.items() 
                   if r['regime'] == 'LATENT' and r['efc']['success']]
latent_failures.sort(key=lambda x: x[1]['efc']['chi2_red'], reverse=True)

if len(latent_failures) >= 3:
    print(f"\nTop 3 LATENT failures (by χ²/dof):")
    for name, r in latent_failures[:3]:
        print(f"  {name:15s}: χ²/dof = {r['efc']['chi2_red']:.1f}, L = {r['latent']['L']:.3f}")

print("\n" + "="*80)
print("DAY 4 COMPLETE: Visualization")
print("="*80)
print("\nGenerated figures:")
print("  1. sparc175_regime_distribution.png")
print("  2. sparc175_aic_vs_latent.png") 
print("  3. sparc175_success_by_bins.png")
print("\nNext: Day 5 - Documentation")

