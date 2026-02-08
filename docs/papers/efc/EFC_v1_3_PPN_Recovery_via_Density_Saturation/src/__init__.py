"""
EFC v1.3 PPN Recovery via Density Saturation

Implementation of dual screening mechanisms that guarantee
GR recovery in the Solar System while allowing EFC modifications
at galactic and cosmological scales.

Key components:
- AccelerationScreening: μ(g_bar) = (1 + g†/g_bar)^k
- DensityScreening: Θ(ρ_eff) = exp[-(ρ_eff/ρ*)^n]
- PPNAnalysis: Derives γ = 1 from EFC field structure
"""

from .efc_ppn_screening import (
    AccelerationScreening,
    DensityScreening,
    PPNAnalysis,
    SolarSystemLocation
)

__all__ = [
    'AccelerationScreening',
    'DensityScreening',
    'PPNAnalysis',
    'SolarSystemLocation'
]
