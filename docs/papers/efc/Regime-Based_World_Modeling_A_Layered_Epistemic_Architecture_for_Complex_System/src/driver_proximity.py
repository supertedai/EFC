"""
Driver Proximity Implementation

Driver proximity measures how directly a measurement relates
to the physical driver of interest.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ProximityScore:
    """Result of a proximity calculation."""
    measured_quantity: str
    target_driver: str
    proxy_steps: int
    score: float  # 1.0 = direct, 0.0 = maximally indirect
    transformations: list[str]

    @property
    def is_direct(self) -> bool:
        return self.proxy_steps == 0

    @property
    def is_acceptable(self) -> bool:
        return self.score >= 0.5


class DriverProximity:
    """
    Driver proximity calculator.

    Measures how directly a measurement relates to the physical
    driver being studied. Higher proximity = stronger conclusions.

    Example:
        dp = DriverProximity()
        score = dp.compute(
            measured="spectral_velocity",
            target="gravitational_acceleration",
            transformations=["doppler_shift", "inclination_correction", "v_squared_over_r"]
        )
    """

    # Proximity decay factor per transformation step
    DECAY_PER_STEP = 0.2

    def __init__(self):
        """Initialize the proximity calculator."""
        self.known_chains: dict[tuple[str, str], list[str]] = {
            # (measured, target): transformations
            ("spectral_velocity", "gravitational_acceleration"): [
                "doppler_correction",
                "inclination_correction",
                "centripetal_formula"
            ],
            ("photometric_flux", "stellar_mass"): [
                "distance_correction",
                "extinction_correction",
                "mass_luminosity_relation"
            ],
            ("redshift", "distance"): [
                "cosmological_model"
            ],
        }

    def compute(
        self,
        measured: str,
        target: str,
        transformations: Optional[list[str]] = None
    ) -> ProximityScore:
        """
        Compute proximity between measured quantity and target driver.

        Args:
            measured: The quantity actually measured
            target: The physical driver of interest
            transformations: List of transformations (if not known)

        Returns:
            ProximityScore with proximity assessment
        """
        # Check for known chain
        key = (measured.lower(), target.lower())
        if key in self.known_chains and transformations is None:
            transformations = self.known_chains[key]

        if transformations is None:
            transformations = []

        proxy_steps = len(transformations)

        # Compute score with exponential decay
        score = max(0.0, 1.0 - self.DECAY_PER_STEP * proxy_steps)

        return ProximityScore(
            measured_quantity=measured,
            target_driver=target,
            proxy_steps=proxy_steps,
            score=score,
            transformations=transformations,
        )

    def register_chain(
        self,
        measured: str,
        target: str,
        transformations: list[str]
    ) -> None:
        """
        Register a known transformation chain.

        Args:
            measured: The measured quantity
            target: The target driver
            transformations: List of transformation steps
        """
        key = (measured.lower(), target.lower())
        self.known_chains[key] = transformations


def compute_proximity(
    measured: str,
    target: str,
    transformations: list[str]
) -> ProximityScore:
    """
    Convenience function to compute proximity.

    Args:
        measured: The measured quantity
        target: The target driver
        transformations: List of transformation steps

    Returns:
        ProximityScore
    """
    dp = DriverProximity()
    return dp.compute(measured, target, transformations)


def assess_claim_strength(
    proximity: ProximityScore,
    confidence: float
) -> tuple[str, float]:
    """
    Assess overall claim strength from proximity and confidence.

    Args:
        proximity: Proximity score
        confidence: Base confidence level

    Returns:
        Tuple of (strength_category, combined_score)
    """
    combined = proximity.score * confidence

    if combined >= 0.8:
        category = "strong"
    elif combined >= 0.5:
        category = "moderate"
    elif combined >= 0.25:
        category = "weak"
    else:
        category = "very_weak"

    return category, combined
