"""
H0/S8 Tension Module — STUB

Constrains the H0 and S8 tensions between early- and late-universe
measurements. In EFC, the energy flow field could resolve these
tensions through scale-dependent modifications.

Key observables:
    - H0 from local distance ladder (SH0ES: 73.0 +/- 1.0)
    - H0 from CMB (Planck: 67.4 +/- 0.5)
    - S8 = sigma8 * sqrt(Omega_m/0.3) from lensing
    - S8 from CMB (Planck: 0.834 +/- 0.016)

Data format (planned):
    quantity, probe, value, sigma, reference

STATUS: Interface stub — load_data() raises NotImplementedError.
Morten: implement when ready to add H0/S8 tension analysis.
"""

import numpy as np
import logging
from typing import Optional

from .base_module import BaseModule
from ..engine.hubble import EFCHubble

logger = logging.getLogger(__name__)


class H0S8Module(BaseModule):
    """
    H0/S8 tension constraints module.

    Reserved interface for analyzing the Hubble and S8 tensions
    within the EFC framework.
    """

    def __init__(self, engine: Optional[EFCHubble] = None):
        if engine is None:
            engine = EFCHubble()
        super().__init__(engine)

    @property
    def name(self) -> str:
        return "h0s8"

    def load_data(self, data_path: str = None, **kwargs):
        """
        Load H0/S8 tension data.

        STATUS: Not yet implemented.
        """
        raise NotImplementedError(
            "H0S8Module.load_data() is not yet implemented.\n"
            "Morten: add H0/S8 tension data here.\n"
            "Expected format: quantity, probe, value, sigma, reference\n"
            "Key probes: SH0ES, Planck CMB, KiDS, DES."
        )
