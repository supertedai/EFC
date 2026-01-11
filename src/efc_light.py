"""
EFC Light Speed Model — c(S)

Implements the entropy-dependent effective speed of light used in the
formal specification (Section 4 of efc_formal_spec.pdf):

    c(S) = c0 * (1 + a_edge * x(S)**2)

where:
    S_mid  = (S0 + S1)/2
    DeltaS = S1 - S0
    x(S)   = (S - S_mid) / (DeltaS/2)

Reference:
    M. Magnusson,
    "Energy-Flow Cosmology — Formal Specification"
    theory/formal/efc_formal_spec.pdf
"""

import numpy as np


def c_of_S(S, c0=3.0e8, S0=0.0, S1=1.0, a_edge=0.6):
    """
    Compute the effective speed of light c(S).

    Parameters
    ----------
    S : float or array
        Entropy value(s)
    c0 : float
        Baseline mid-entropy light speed
    S0, S1 : float
        Entropy endpoints
    a_edge : float
        Enhancement factor toward s0 and s1

    Returns
    -------
    c : float or array
        Effective light speed at entropy S
    """

    S = np.asarray(S, dtype=float)
    S_mid = 0.5 * (S0 + S1)
    DeltaS = S1 - S0

    # normalized entropy coordinate
    x = (S - S_mid) / (DeltaS / 2)

    return c0 * (1.0 + a_edge * x**2)
