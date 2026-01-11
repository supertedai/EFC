import numpy as np
from ..core.efc_core import EFCParameters


def entropy_field(x, params: EFCParameters) -> np.ndarray:
    """
    EFC-S: S(r) = S0 * (1 - exp(-r/Ls))
    """
    r = np.linalg.norm(x, axis=-1)
    S0 = params.entropy_scale
    Ls = params.length_scale

    return S0 * (1.0 - np.exp(-r / Ls))


def entropy_gradient(x, params: EFCParameters) -> np.ndarray:
    """
    ∇S(r) = (S0/Ls) * exp(-r/Ls) * r̂
    """
    r = np.linalg.norm(x, axis=-1)
    S0 = params.entropy_scale
    Ls = params.length_scale

    dSdr = (S0 / Ls) * np.exp(-r / Ls)

    # enhetvektor i radial retning
    direction = np.zeros_like(x)
    mask = r > 0
    direction[mask] = x[mask] / r[mask][:, None]

    return dSdr[:, None] * direction
