"""
Abstract base class for EFC physics engines.

An engine takes EFC parameters and computes a physical observable
(rotation velocity, H(z), D(z), kappa, n(M,z), ...).

Engine files contain ONLY physics — never data loading or likelihood computation.
"""

from abc import ABC, abstractmethod
import numpy as np


class EFCEngine(ABC):
    """
    Base class for all EFC computation engines.

    Subclasses must implement:
        - compute(params_dict, coordinates) -> predictions
        - validate_params(params_dict) -> bool

    Convention:
        - params_dict: {name: value} for ALL EFC parameters
        - coordinates: domain-specific independent variable(s)
        - Returns: np.ndarray of predicted observable values
    """

    # Subclasses should list the parameter names they require
    REQUIRED_PARAMS: list[str] = []

    @property
    @abstractmethod
    def name(self) -> str:
        """Short identifier for this engine (e.g. 'rotation', 'hubble')."""
        ...

    @abstractmethod
    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """
        Compute the observable from EFC parameters.

        Parameters:
            params_dict:  {name: value} dict of EFC parameters
            coordinates:  Independent variable(s) — shape depends on engine

        Returns:
            np.ndarray of predicted values, same length as coordinates
        """
        ...

    def validate_params(self, params_dict: dict) -> bool:
        """Check that all required parameters are present and finite."""
        for name in self.REQUIRED_PARAMS:
            if name not in params_dict:
                return False
            if not np.isfinite(params_dict[name]):
                return False
        return True
