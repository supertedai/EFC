#!/usr/bin/env python3
"""
RBWM Physics Example

Demonstrates using the (R, L) coordinate system for physics claims.
"""

import sys
from pathlib import Path

# Add package root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.world_model import WorldModel
from src.claim import Claim
from src.r_axis import RRegime
from src.l_axis import LLayer
from src.driver_proximity import compute_proximity


def main():
    """Run physics example."""
    print("=" * 60)
    print("RBWM Physics Example: Galaxy Dynamics")
    print("=" * 60)
    print()

    # Create world model
    model = WorldModel(name="Galaxy Dynamics Model")

    # Add claims with (R, L) coordinates
    claims = [
        Claim(
            statement="Galaxy rotation curves show flat profiles at large radii",
            r_regime=RRegime.R2,
            l_layer=LLayer.L2,
            driver="gravitational_acceleration",
            validity_domain="r > 5 kpc",
            confidence=0.95,
        ),
        Claim(
            statement="Baryonic mass follows exponential disk profile",
            r_regime=RRegime.R1,
            l_layer=LLayer.L2,
            driver="mass_distribution",
            validity_domain="disk galaxies",
            confidence=0.90,
        ),
        Claim(
            statement="Dark matter halo is required to explain dynamics",
            r_regime=RRegime.R2,
            l_layer=LLayer.L3,
            driver="gravitational_acceleration",
            validity_domain="ΛCDM framework",
            confidence=0.60,
        ),
    ]

    for claim in claims:
        model.add_claim(claim)
        print(f"Added: {claim.statement[:50]}...")
        print(f"  Coordinate: {claim.coordinate_str}")
        print()

    # Validate model
    print("Model Validation:")
    print("-" * 40)
    result = model.validate()
    print(f"Valid: {result.is_valid}")
    if result.warnings:
        print("Warnings:")
        for w in result.warnings:
            print(f"  - {w}")
    print()

    # Test regime transfer
    print("Regime Transfer Test:")
    print("-" * 40)
    transfer = model.validate_transfer(
        claims[2],  # Dark matter claim
        target_r=RRegime.R1,
        target_l=LLayer.L2,
    )
    print(f"Transfer from {claims[2].coordinate_str} to (R1, L2):")
    print(f"  Status: {transfer.status.value}")
    print(f"  Reason: {transfer.reason}")
    print()

    # Compute driver proximity
    print("Driver Proximity Analysis:")
    print("-" * 40)
    proximity = compute_proximity(
        measured="spectral_velocity",
        target="gravitational_acceleration",
        transformations=[
            "doppler_correction",
            "inclination_correction",
            "centripetal_formula"
        ]
    )
    print(f"Measured: {proximity.measured_quantity}")
    print(f"Target: {proximity.target_driver}")
    print(f"Proxy steps: {proximity.proxy_steps}")
    print(f"Score: {proximity.score:.2f}")
    print(f"Acceptable: {proximity.is_acceptable}")
    print()

    # Model summary
    print("Model Summary:")
    print("-" * 40)
    print(model.summary())


if __name__ == "__main__":
    main()
