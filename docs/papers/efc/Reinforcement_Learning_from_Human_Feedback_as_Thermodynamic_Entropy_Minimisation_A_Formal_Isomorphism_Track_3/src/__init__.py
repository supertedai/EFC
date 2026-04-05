"""RLHF Thermodynamic Isomorphism — AI-friendly implementation.

Formal isomorphism: RLHF ≡ statistical-mechanical free energy minimisation.
R → −E, β_KL → T, J = −F (algebraically exact).

DOI: 10.6084/m9.figshare.31940535
"""

from .rlhf_thermodynamics import (
    BoltzmannPolicy,
    FreeEnergyObjective,
    GrokkingPhaseTransition,
    JailbreakKramersEscape,
    AlignmentCapabilityBound,
    RLHFIsomorphism,
)
