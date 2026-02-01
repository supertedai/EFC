#!/usr/bin/env python3
"""
EBE Basic Classification Example

Demonstrates basic usage of the EBE classification system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ebe_classifier import EBEClassifier
from s_axis import SRegime
from l_axis import LLayer


def main():
    """Run basic classification examples."""
    print("=" * 60)
    print("EBE Basic Classification Example")
    print("=" * 60)
    print()

    # Create classifier
    classifier = EBEClassifier()

    # Example 1: Galaxy rotation velocity measurement
    print("Example 1: Galaxy Rotation Velocity")
    print("-" * 40)

    result1 = classifier.classify(
        observable="galaxy_rotation_velocity",
        s_parameter=0.85,  # High-S (galactic scale)
        proxy_depth=2,     # Derived from spectroscopy
    )
    print(result1.summary())
    print()

    # Example 2: Particle mass measurement
    print("Example 2: Particle Mass")
    print("-" * 40)

    result2 = classifier.classify(
        observable="electron_mass",
        s_parameter=0.1,   # Low-S (particle physics)
        proxy_depth=1,     # Calibrated measurement
    )
    print(result2.summary())
    print()

    # Example 3: Using system type
    print("Example 3: Stellar Temperature")
    print("-" * 40)

    result3 = classifier.classify_measurement(
        observable="stellar_temperature",
        measurement_type="spectroscopic",
        regime="stellar",
    )
    print(result3.summary())
    print()

    # Example 4: Validate claim transfer
    print("Example 4: Claim Transfer Validation")
    print("-" * 40)

    valid, reason = classifier.validate_claim_transfer(
        claim="Mass estimates are accurate",
        source=result1,
        target_s=SRegime.LOW_S,
        target_l=LLayer.L0,
    )
    print(f"Transfer valid: {valid}")
    print(f"Reason: {reason}")


if __name__ == "__main__":
    main()
