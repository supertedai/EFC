#!/usr/bin/env python3
"""
EFC White Paper Series — Quick demonstration.

Shows the key results from all four parts:
  Part 1: Recovery conditions (mu -> 1 in GR limits)
  Part 2: Entropy field and coupling mu(a)
  Part 3: Validation summary counts
  Part 4: Susceptibility function T(S)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from white_paper_overview import (
    theta_z, mu_recovery, entropy_field, mu_coupling,
    VALIDATION_SUMMARY, rho_eff, susceptibility_T
)

print("=== EFC White Paper Series Demo ===\n")

# Part 1: Recovery — mu approaches 1 at high z
print("Part 1: Recovery Conditions")
for z in [0, 0.5, 1.0, 2.0, 5.0]:
    print(f"  z={z:.1f}  mu={mu_recovery(0.01, z):.6f}  (theta={theta_z(z):.4f})")

# Part 2: Entropy field and coupling
print("\nPart 2: Field Equations")
for a in [0.2, 0.4, 0.6, 0.8, 1.0]:
    S = entropy_field(a)
    mu = mu_coupling(a)
    print(f"  a={a:.1f}  S(a)={S:.6f}  mu(a)={mu:.6f}")

# Part 3: Validation counts
print("\nPart 3: Validation Summary")
for k, v in VALIDATION_SUMMARY.items():
    print(f"  {k}: {v}")

# Part 4: Susceptibility
print("\nPart 4: Regime Susceptibility T(S)")
for S in [0.01, 0.04, 0.1, 0.3, 0.5]:
    print(f"  S={S:.2f}  rho_eff={rho_eff(S):.4f}  T(S)={susceptibility_T(S):.4f}")

print("\nDone.")
