"""EFC Cross-Domain Bridge Equations — AI-friendly implementation.

Bridge B1: Cosmology -> Neural (degree heterogeneity driven)
Bridge B2: Neural -> RLHF (entropy topology <-> reward curvature)
Unified: dF/dt = -integral |nabla s_dot|^2 dV + B

DOI: 10.6084/m9.figshare.31940547
"""

from .bridge_equations import (
    UnifiedGradientFlow,
    BridgeB1Cosmology2Neural,
    BridgeB1StarStar,
    BridgeB2Neural2RLHF,
    CrossDomainPredictions,
    ObservableDictionary,
)
