"""
Regime Classifier

Classifies cosmological probes into background vs structure regimes.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Regime(Enum):
    """Gravitational regime classification."""
    BACKGROUND = "background"  # Linear, smooth
    STRUCTURE = "structure"    # Nonlinear, collapsed
    MIXED = "mixed"           # Partially both


@dataclass
class ProbeInfo:
    """Information about a cosmological probe."""
    name: str
    regime: Regime
    effective_G: str
    h0_typical: float
    description: str


# Probe classifications
PROBE_CLASSIFICATIONS = {
    # Background probes
    "CMB": ProbeInfo(
        name="CMB (Planck)",
        regime=Regime.BACKGROUND,
        effective_G="G₀",
        h0_typical=67.4,
        description="Cosmic microwave background - probes recombination era"
    ),
    "BAO": ProbeInfo(
        name="Baryon Acoustic Oscillations",
        regime=Regime.BACKGROUND,
        effective_G="G₀",
        h0_typical=67.0,
        description="Sound horizon scale in galaxy clustering"
    ),

    # Structure probes
    "SN_Ia_Cepheids": ProbeInfo(
        name="SN Ia + Cepheids (SH0ES)",
        regime=Regime.STRUCTURE,
        effective_G="G_eff > G₀",
        h0_typical=73.0,
        description="Type Ia supernovae calibrated with Cepheid variables"
    ),
    "TRGB": ProbeInfo(
        name="Tip of Red Giant Branch",
        regime=Regime.STRUCTURE,
        effective_G="G_eff > G₀",
        h0_typical=69.8,
        description="Standard candles in galaxy halos"
    ),
    "Masers": ProbeInfo(
        name="Megamasers",
        regime=Regime.STRUCTURE,
        effective_G="G_eff > G₀",
        h0_typical=73.0,
        description="Water masers in AGN accretion disks"
    ),
    "Surface_Brightness": ProbeInfo(
        name="Surface Brightness Fluctuations",
        regime=Regime.STRUCTURE,
        effective_G="G_eff > G₀",
        h0_typical=70.0,
        description="Fluctuations in unresolved stellar populations"
    ),

    # Mixed probes
    "Gravitational_Waves": ProbeInfo(
        name="Gravitational Wave Standard Sirens",
        regime=Regime.MIXED,
        effective_G="Depends on source environment",
        h0_typical=70.0,
        description="GW events with electromagnetic counterparts"
    ),
}


def classify_probe(probe_name: str) -> Regime:
    """
    Classify a probe by its gravitational regime.

    Args:
        probe_name: Name of the probe (e.g., "CMB", "SN_Ia_Cepheids")

    Returns:
        Regime classification

    Example:
        >>> classify_probe("CMB")
        Regime.BACKGROUND
        >>> classify_probe("SN_Ia_Cepheids")
        Regime.STRUCTURE
    """
    if probe_name in PROBE_CLASSIFICATIONS:
        return PROBE_CLASSIFICATIONS[probe_name].regime

    # Try case-insensitive match
    for key, info in PROBE_CLASSIFICATIONS.items():
        if key.lower() == probe_name.lower():
            return info.regime

    raise ValueError(f"Unknown probe: {probe_name}")


def get_probe_info(probe_name: str) -> ProbeInfo:
    """Get full information about a probe."""
    if probe_name in PROBE_CLASSIFICATIONS:
        return PROBE_CLASSIFICATIONS[probe_name]
    raise ValueError(f"Unknown probe: {probe_name}")


def list_probes_by_regime(regime: Regime) -> list[ProbeInfo]:
    """List all probes in a given regime."""
    return [
        info for info in PROBE_CLASSIFICATIONS.values()
        if info.regime == regime
    ]


class RegimeClassifier:
    """
    Classifier for cosmological probes.

    Example:
        classifier = RegimeClassifier()

        # Classify a single probe
        regime = classifier.classify("CMB")

        # Get expected H₀ by regime
        h0_bg = classifier.expected_h0(Regime.BACKGROUND)
        h0_st = classifier.expected_h0(Regime.STRUCTURE)
    """

    def __init__(self):
        self.probes = PROBE_CLASSIFICATIONS.copy()

    def classify(self, probe_name: str) -> Regime:
        """Classify a probe."""
        return classify_probe(probe_name)

    def get_info(self, probe_name: str) -> ProbeInfo:
        """Get probe information."""
        return get_probe_info(probe_name)

    def by_regime(self, regime: Regime) -> list[ProbeInfo]:
        """Get all probes in a regime."""
        return list_probes_by_regime(regime)

    def expected_h0(self, regime: Regime) -> float:
        """Get expected H₀ for a regime (average of probes)."""
        probes = self.by_regime(regime)
        if not probes:
            return 0.0
        return sum(p.h0_typical for p in probes) / len(probes)

    def summary(self) -> str:
        """Get summary of all classifications."""
        lines = ["Probe Classification by Gravitational Regime", "=" * 50]

        for regime in Regime:
            probes = self.by_regime(regime)
            if probes:
                lines.append(f"\n{regime.value.upper()} REGIME:")
                for p in probes:
                    lines.append(f"  {p.name}: H₀ ~ {p.h0_typical} km/s/Mpc")

        return "\n".join(lines)
