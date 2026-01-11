"""
efc_core.py
Kjernekonstruksjon for Energy-Flow Cosmology (EFC).

Inneholder:
- EFCParameters (dataklasse)
- EFCModel (basismodell for Ef, ∇S, rotasjonshastighet)
- load_parameters() for å lese parameters.json
"""

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import json


# -------------------------
# Dataklasse for parametere
# -------------------------
@dataclass
class EFCParameters:
    entropy_scale: float      # S0
    length_scale: float       # Ls
    flow_constant: float
    velocity_scale: float
    seed: int = 42
    grid_resolution: int = 32
    time_steps: int = 10


# -------------------------
# EFC modell
# -------------------------
class EFCModel:
    def __init__(self, params: EFCParameters):
        self.params = params
        np.random.seed(params.seed)

    # -------------------------
    # Full state (S, ∇S, Ef)
    # -------------------------
    def compute_state(self, x):
        """
        Returnerer en state-pakke:
        {
            "Ef": Ef(r),
            "gradS": ∇S(r)
        }
        """
        Ef = self._compute_Ef(x)
        gradS = self._compute_entropy_gradient(x)
        return {
            "Ef": Ef,
            "gradS": gradS,
        }

    # -------------------------
    # Energi-flyt (EFC-D)
    # -------------------------
    def _compute_Ef(self, x):
        """
        Ef(r) = ρ * (1 - S)
        """
        from ..potential.efc_potential import compute_energy_flow

        # Standard uniform baseline (kan senere byttes til profiler)
        rho = 1e-24 * np.ones(x.shape[0])
        S = 0.5 * np.ones(x.shape[0])

        return compute_energy_flow(rho, S)

    # -------------------------
    # Entropi-gradient (EFC-S)
    # -------------------------
    def _compute_entropy_gradient(self, x):
        """
        Henter ∇S fra EFC-S modul.
        """
        from ..entropy.efc_entropy import entropy_gradient
        return entropy_gradient(x, self.params)

    # -------------------------
    # Rotasjonshastighet (EFC-D)
    # -------------------------
    def rotation_velocity(self, r):
        """
        EFC rotasjonsprofil:
        v(r) = sqrt(|Ef(r)| * r)

        r: 1D array (kpc)
        """
        # Lag posisjoner i 3D-plane: (r, 0, 0)
        x = np.stack([r, np.zeros_like(r), np.zeros_like(r)], axis=1)

        # Beregn Ef(r)
        Ef = self._compute_Ef(x)  # Ef er 1D array

        # Rotasjonshastighet
        return np.sqrt(np.abs(Ef) * r)


# -------------------------
# Parameter loader
# -------------------------
def load_parameters(path: Path) -> EFCParameters:
    """
    Leser parameters.json og returnerer EFCParameters.
    Forventer struktur:
    {
        "efc_parameters": {
            "entropy_scale": ...,
            "length_scale": ...,
            ...
        }
    }
    """
    with open(path, "r") as f:
        cfg = json.load(f)

    return EFCParameters(**cfg["efc_parameters"])
