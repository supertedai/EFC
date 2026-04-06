#!/usr/bin/env python3
"""
Demo: L0-L3 Regime Architecture Validator
Demonstrates regime validation, leakage detection, and regime/transition queries.
"""

import os
import sys

# Add the package root to sys.path so we can import from src/
_pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _pkg_root)

from src import Regime, InferenceType, RegimeValidator

# Paths to data files (relative to package root)
_defs = os.path.join(_pkg_root, "data", "regime_definitions.json")
_trans = os.path.join(_pkg_root, "data", "regime_transitions.json")

validator = RegimeValidator(
    regime_definitions_path=_defs,
    transition_definitions_path=_trans,
)


# ---------- Demo 1: Inference validity per regime ----------
print("=== Demo 1: Inference validity across regimes ===")

valid, msg = validator.validate_inference(Regime.L0, InferenceType.CONFIGURATION_ANALYSIS)
print(f"  Configuration analysis in L0 -> valid={valid}  ({msg})")
assert valid is True, "Configuration analysis should be valid in every regime"

valid, msg = validator.validate_inference(Regime.L0, InferenceType.CAUSAL_HISTORY)
print(f"  Causal history in L0          -> valid={valid} ({msg})")
assert valid is False, "L0 has no causal history"

valid, msg = validator.validate_inference(Regime.L1, InferenceType.LINEAR_PREDICTION)
print(f"  Linear prediction in L1       -> valid={valid}  ({msg})")
assert valid is True, "L1 stable dynamics support linear prediction"

valid, msg = validator.validate_inference(Regime.L2, InferenceType.LINEAR_PREDICTION)
print(f"  Linear prediction in L2       -> valid={valid} ({msg})")
assert valid is False, "L2 non-linear dynamics invalidate linear prediction"

print()


# ---------- Demo 2: Regime leakage detection ----------
print("=== Demo 2: Regime leakage detection ===")

is_leakage, msg = validator.detect_regime_leakage(
    Regime.L1, Regime.L3, InferenceType.LINEAR_PREDICTION
)
print(f"  L1 linear prediction applied to L3 -> leakage={is_leakage}")
print(f"    {msg}")
assert is_leakage is True, "Applying L1 linear prediction in L3 is regime leakage"

is_leakage, msg = validator.detect_regime_leakage(
    Regime.L1, Regime.L2, InferenceType.NONLINEAR_PREDICTION
)
print(f"  L1 nonlinear prediction applied to L2 -> leakage={is_leakage}")
print(f"    {msg}")
assert is_leakage is False, "Nonlinear prediction is valid in both L1 and L2"

print()


# ---------- Demo 3: Regime information lookup ----------
print("=== Demo 3: Regime information lookup ===")

for regime in Regime:
    info = validator.get_regime_info(regime)
    print(f"  {regime.name}: {info['name']}")
    print(f"    Energy flow: {info['dynamics']['energy_flow']}")
    print(f"    Entropy production: {info['dynamics']['entropy_production']}")

assert validator.get_regime_info(Regime.L2)["dynamics"]["energy_flow"] == "variable_high"
assert validator.get_regime_info(Regime.L0)["dynamics"]["entropy_production"] == "none"

print()


# ---------- Demo 4: Transition information ----------
print("=== Demo 4: Transition information ===")

transition_pairs = [
    (Regime.L0, Regime.L1, "Activation"),
    (Regime.L1, Regime.L2, "Complexification"),
    (Regime.L2, Regime.L3, "Deactivation"),
    (Regime.L3, Regime.L0, "Cyclical Reset"),
]
for src, tgt, expected_name in transition_pairs:
    info = validator.get_transition_info(src, tgt)
    assert info is not None, f"Transition {src.name}->{tgt.name} should exist"
    assert info["name"] == expected_name, (
        f"Expected transition name '{expected_name}', got '{info['name']}'"
    )
    print(f"  {src.name} -> {tgt.name}: {info['name']} ({info['type']})")

print()


# ---------- Demo 5: L2-to-L3 boundary (highest leakage risk) ----------
print("=== Demo 5: L2-to-L3 boundary (highest leakage risk) ===")

# These inference types are valid in L2 but invalid in L3, so applying
# them across the boundary constitutes regime leakage.
leakage_cases = [
    InferenceType.ACTIVE_DYNAMICS,
    InferenceType.NONLINEAR_PREDICTION,
    InferenceType.CAUSAL_HISTORY,
]
for inf in leakage_cases:
    is_leakage, msg = validator.detect_regime_leakage(Regime.L2, Regime.L3, inf)
    print(f"  {inf.value:30s} -> LEAKAGE={is_leakage}")
    assert is_leakage is True, f"{inf.value} should be flagged as leakage across L2->L3"

# Linear prediction is invalid in both L2 and L3 (L2 requires non-linear
# models), so it does NOT constitute leakage -- it was already wrong.
is_leakage, _ = validator.detect_regime_leakage(
    Regime.L2, Regime.L3, InferenceType.LINEAR_PREDICTION
)
print(f"  {'linear_prediction':30s} -> LEAKAGE={is_leakage} (invalid in both)")
assert is_leakage is False, "Linear prediction is invalid in both L2 and L3, so no leakage"

print()


# ---------- Demo 6: Structural analysis is safe everywhere ----------
print("=== Demo 6: Structural analysis is universally valid ===")

for regime in Regime:
    valid, msg = validator.validate_inference(regime, InferenceType.STRUCTURAL_ANALYSIS)
    print(f"  Structural analysis in {regime.name}: valid={valid}")
    assert valid is True, f"Structural analysis should be valid in {regime.name}"

print()
print("All demos passed.")
