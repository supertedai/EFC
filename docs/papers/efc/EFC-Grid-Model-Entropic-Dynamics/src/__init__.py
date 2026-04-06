"""
EFC Grid Model for Entropic Dynamics

Implements entropic dynamics from the interaction of the Grid field,
entropy field S, and energy-flow field Ef.

Reference:
    Magnusson, M. EFC -- Grid Model for Entropic Dynamics.
"""

from .entropic_dynamics import (
    GridField,
    EntropicFlow,
    EntropicDynamicsModel,
)

__version__ = "1.0.0"
__all__ = [
    "GridField",
    "EntropicFlow",
    "EntropicDynamicsModel",
]
