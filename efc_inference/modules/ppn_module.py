"""
PPN (Parametrized Post-Newtonian) Module — STUB

Solar System constraints on EFC modifications to gravity.

Key observables:
    - gamma_PPN (Cassini: 1 + (2.1 +/- 2.3) x 10^-5)
    - beta_PPN (Lunar Laser Ranging)
    - Mercury perihelion precession

In EFC: alpha(planetary) should be near zero, recovering GR.
This provides a strong prior constraint on the theory.

Data format (planned):
    test, parameter, value, sigma, reference

STATUS: Interface stub — load_data() raises NotImplementedError.
Morten: implement when ready to add Solar System constraints.
"""

import numpy as np
import logging
from typing import Optional

from .base_module import BaseModule
from ..engine.base_engine import EFCEngine

logger = logging.getLogger(__name__)


class _PPNEngine(EFCEngine):
    """Placeholder engine for PPN predictions."""

    REQUIRED_PARAMS = ["alpha_planetary"]

    @property
    def name(self) -> str:
        return "ppn"

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        raise NotImplementedError(
            "PPN engine not yet implemented. "
            "Morten: add EFC planetary-scale predictions here."
        )


class PPNModule(BaseModule):
    """
    Solar System PPN constraints module.

    Reserved interface for Cassini, LLR, and Mercury perihelion tests.
    """

    def __init__(self, engine: Optional[EFCEngine] = None):
        if engine is None:
            engine = _PPNEngine()
        super().__init__(engine)

    @property
    def name(self) -> str:
        return "ppn"

    def load_data(self, data_path: str = None, **kwargs):
        """
        Load PPN constraint data.

        STATUS: Not yet implemented.
        """
        raise NotImplementedError(
            "PPNModule.load_data() is not yet implemented.\n"
            "Morten: add Solar System PPN data loading here.\n"
            "Expected format: test, parameter, value, sigma, reference"
        )
