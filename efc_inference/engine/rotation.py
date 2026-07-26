"""
EFC Rotation Velocity Engine

Wraps src/efc/core/efc_core.py to compute galaxy rotation curves.
This is the ONLY non-stub engine — it uses existing EFC physics code.

Physics:
    v(r) = sqrt(|Ef(r)| * r)
    where Ef is the EFC energy flow field.
"""

import numpy as np
import sys
from pathlib import Path

from .base_engine import EFCEngine

# Add src/ to path so we can import efc_core
_src_path = str(Path(__file__).resolve().parents[2] / "src")
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)


class EFCRotation(EFCEngine):
    """
    Compute EFC rotation velocity profile v(r).

    Uses EFCParameters and EFCModel from src/efc/core/efc_core.py.

    Required parameters:
        - entropy_scale (S0): entropy normalization
        - length_scale (Ls): characteristic length scale
        - flow_constant: energy flow coupling
        - velocity_scale: velocity normalization
    """

    REQUIRED_PARAMS = ["entropy_scale", "length_scale",
                       "flow_constant", "velocity_scale"]

    @property
    def name(self) -> str:
        return "rotation"

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """
        Compute rotation velocity at radii r.

        Parameters:
            params_dict:  Must contain entropy_scale, length_scale,
                         flow_constant, velocity_scale
            coordinates:  (N,) array of radii in kpc

        Returns:
            (N,) array of rotation velocities in km/s
        """
        if not self.validate_params(params_dict):
            return np.full_like(coordinates, np.nan)

        try:
            from efc.core.efc_core import EFCParameters, EFCModel

            efc_params = EFCParameters(
                entropy_scale=params_dict["entropy_scale"],
                length_scale=params_dict["length_scale"],
                flow_constant=params_dict["flow_constant"],
                velocity_scale=params_dict["velocity_scale"],
            )

            model = EFCModel(efc_params)
            v_rot = model.rotation_velocity(coordinates)

            return v_rot

        except ImportError:
            # Fallback: simple parametric rotation curve
            # v(r) = velocity_scale * sqrt(r / (r + length_scale))
            Ls = params_dict["length_scale"]
            Vs = params_dict["velocity_scale"]
            return Vs * np.sqrt(coordinates / (coordinates + Ls))

        except Exception:
            return np.full_like(coordinates, np.nan)
