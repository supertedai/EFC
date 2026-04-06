"""EFC - Effective Phenomenological Law for Gravitational Response.

Classes implementing the effective gravitational coupling mu(a) = 1 + beta*S(a),
the entropy field S(a), and regime transition logic.

Author: Morten Magnusson (ORCID 0009-0002-4860-5095)
License: CC-BY-4.0
"""

from .gravitational_response import (
    EntropyField,
    EffectiveGravitationalCoupling,
    RegimeClassifier,
)
