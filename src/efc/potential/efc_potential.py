"""
efc_potential.py
Energy-flow potential for EFC.
"""

import numpy as np


def compute_energy_flow(rho, S):
    """
    Energistrømpotensial:
    Ef = ρ * (1.0 - S)
    """
    return rho * (1.0 - S)


def energy_density(mass, volume):
    """
    ρ = m / V
    """
    return mass / volume


def energy_flow_rate(Ef, t):
    """
    dEf/dt beregnet numerisk langs t.
    """
    return np.gradient(Ef, t)

