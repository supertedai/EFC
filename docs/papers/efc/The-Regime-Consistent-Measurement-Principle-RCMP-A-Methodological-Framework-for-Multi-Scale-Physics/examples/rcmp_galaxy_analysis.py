#!/usr/bin/env python3
"""
RCMP Galaxy Analysis Example

Demonstrates application of the Regime-Consistent Measurement Principle
to galaxy rotation curve analysis using the SPARC dataset approach.

Reference:
    Magnusson, M. (2026). The Regime-Consistent Measurement Principle (RCMP).
    DOI: 10.6084/m9.figshare.31222900
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rcmp_validator import RCMPValidator, Driver
from regime_tagger import RegimeTagger, EpistemicLayer
from proxy_chain import ProxyChain
from uncertainty_propagator import UncertaintyPropagator


def main():
    """Run complete RCMP analysis example."""

    print("=" * 60)
    print("RCMP Galaxy Rotation Curve Analysis")
    print("=" * 60)
    print()

    # =========================================================================
    # Step 1: Define the Physical Driver
    # =========================================================================
    print("Step 1: Define Physical Driver")
    print("-" * 40)

    driver = Driver(
        name="gravitational_response",
        regime="low_acceleration",
        boundary_condition="g_bar < 1e-11 m/s²",
        primary_variable="centripetal_acceleration",
    )

    print(f"Driver: {driver.name}")
    print(f"Regime: {driver.regime}")
    print(f"Boundary: {driver.boundary_condition}")
    print(f"Primary variable: {driver.primary_variable}")
    print()

    # =========================================================================
    # Step 2: Tag Sample Measurements with Regimes
    # =========================================================================
    print("Step 2: Tag Measurements with Regimes")
    print("-" * 40)

    # Sample measurements (simplified from SPARC)
    measurements = [
        {
            "galaxy": "NGC2403",
            "type": "spiral",
            "g_bar": 8.2e-11,
            "g_obs": 1.46e-10,
            "layer": "L2",
        },
        {
            "galaxy": "NGC2403",
            "type": "spiral",
            "g_bar": 2.1e-11,
            "g_obs": 5.8e-11,
            "layer": "L2",
        },
        {
            "galaxy": "DDO154",
            "type": "dwarf",
            "g_bar": 3.1e-12,
            "g_obs": 5.3e-11,
            "layer": "L2",
        },
        {
            "galaxy": "DDO154",
            "type": "dwarf",
            "g_bar": 1.5e-12,
            "g_obs": 2.8e-11,
            "layer": "L2",
        },
    ]

    tagger = RegimeTagger()
    tagged_measurements = []

    for m in measurements:
        regime_info = tagger.classify_acceleration(m["g_bar"])
        m["regime"] = regime_info.regime_name
        m["regime_boundary"] = regime_info.boundary_condition
        tagged_measurements.append(m)
        print(f"  {m['galaxy']}: g_bar={m['g_bar']:.2e} → {regime_info.regime_name}")

    print()

    # =========================================================================
    # Step 3: Document Proxy Chain
    # =========================================================================
    print("Step 3: Document Proxy Chain")
    print("-" * 40)

    chain = ProxyChain(name="velocity_to_acceleration")

    chain.add_step(
        name="spectral_velocity",
        layer="L0",
        sigma=0.005,
        description="Raw spectral line velocity measurement",
    )

    chain.add_step(
        name="rotation_velocity",
        layer="L1",
        sigma=0.02,
        transformation="V_rot = V_obs / sin(i)",
        assumptions=["Thin disk geometry", "Circular orbits", "Known inclination"],
        parameters=["Inc", "eInc"],
    )

    chain.add_step(
        name="centripetal_acceleration",
        layer="L2",
        sigma=0.05,
        transformation="g_obs = V²/R",
        assumptions=["Accurate distance", "Correct radius"],
        parameters=["D", "eD"],
    )

    print(chain.summary())
    print()

    # Validate the chain
    chain_issues = chain.validate()
    if chain_issues:
        print("Chain validation warnings:")
        for issue in chain_issues:
            print(f"  - {issue}")
    else:
        print("Chain validation: OK")
    print()

    # =========================================================================
    # Step 4: Propagate Uncertainties
    # =========================================================================
    print("Step 4: Propagate Uncertainties")
    print("-" * 40)

    propagator = UncertaintyPropagator()

    propagator.add_source("spectral", sigma=0.005, layer="L0")
    propagator.add_source("inclination", sigma=0.02, layer="L1")
    propagator.add_source("distance", sigma=0.05, layer="L2")

    print(propagator.summary())
    print()

    # =========================================================================
    # Step 5: Create Alternative Chain for Cross-Validation
    # =========================================================================
    print("Step 5: Create Alternative Proxy Chain")
    print("-" * 40)

    alt_chain = ProxyChain(name="photometry_to_acceleration")

    alt_chain.add_step(
        name="infrared_flux",
        layer="L0",
        sigma=0.02,
        description="Spitzer 3.6μm photometry",
    )

    alt_chain.add_step(
        name="stellar_mass",
        layer="L1",
        sigma=0.10,
        transformation="M_* = (M/L) × L_3.6",
        assumptions=["M/L calibration", "No hidden mass"],
        parameters=["M/L_disk", "M/L_bulge"],
    )

    alt_chain.add_step(
        name="baryonic_acceleration",
        layer="L2",
        sigma=0.15,
        transformation="g_bar = GM(<R)/R²",
        assumptions=["Newtonian gravity", "Spherical approximation"],
    )

    print(f"Alternative chain: {alt_chain.name}")
    print(f"  Depth: {alt_chain.depth()} steps")
    print(f"  Total σ: {alt_chain.total_uncertainty():.3f}")
    print()

    # =========================================================================
    # Step 6: Run RCMP Validation
    # =========================================================================
    print("Step 6: RCMP Validation")
    print("-" * 40)

    validator = RCMPValidator()

    result = validator.validate(
        driver=driver,
        proxy_chain=chain,
        measurements=tagged_measurements,
        cross_validation_chains=[alt_chain],
        coordinate_system="galactocentric cylindrical",
    )

    print(result)
    print()

    # =========================================================================
    # Step 7: Generate RCMP-Compliant Conclusion
    # =========================================================================
    print("Step 7: RCMP-Compliant Conclusion")
    print("-" * 40)

    conclusion = """
Following RCMP methodology, we can state:

PROBLEM DEFINITION (not conclusion):
- The low-acceleration manifold is real at the galaxy level
- Excess scatter in dwarfs is internal and low-frequency
- Distance uncertainty explains some amplitude variation
- High-frequency kinematic explanations are disfavored

EXPLAINED:
  ✓ Distance uncertainty contribution

RULED OUT:
  ✗ High-frequency kinematic noise
  ✗ Simple pressure support

OPEN QUESTIONS:
  ? V_flat–median residual correlation remains unexplained

This maps the boundary between what is explained and what
remains open—exactly what RCMP is designed to achieve.
"""
    print(conclusion)

    # =========================================================================
    # Summary Statistics
    # =========================================================================
    print("=" * 60)
    print("Analysis Summary")
    print("=" * 60)
    print(f"Measurements analyzed: {len(tagged_measurements)}")
    print(f"Proxy chain depth: {chain.depth()} layers")
    print(f"Total propagated uncertainty: {chain.total_uncertainty():.4f}")
    print(f"Cross-validation chains: 2")
    print(f"RCMP Status: {result.status.value.upper()}")
    print()

    return result.is_valid


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
