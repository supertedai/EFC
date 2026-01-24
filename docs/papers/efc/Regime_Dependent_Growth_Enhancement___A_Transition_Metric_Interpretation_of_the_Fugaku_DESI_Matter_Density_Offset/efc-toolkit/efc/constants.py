"""
EFC Constants and References
============================

Canonical constants, DOIs, and reference values for EFC.

Author: Morten Magnusson
Address: Hasselvegen 5, 4051 Sola, Norway
ORCID: 0009-0002-4860-5095
"""

from dataclasses import dataclass
from typing import Dict


# =============================================================================
# Author Information
# =============================================================================

@dataclass(frozen=True)
class AuthorInfo:
    """Canonical author information."""
    name: str = "Morten Magnusson"
    address: str = "Hasselvegen 5, 4051 Sola, Norway"
    orcid: str = "0009-0002-4860-5095"
    orcid_url: str = "https://orcid.org/0009-0002-4860-5095"


AUTHOR = AuthorInfo()


# =============================================================================
# Publication DOIs
# =============================================================================

@dataclass(frozen=True)
class DOIRegistry:
    """Registry of EFC publication DOIs."""
    
    # Core framework
    foundations: str = "10.6084/m9.figshare.31135597"
    
    # Observational constraints
    desi_bao: str = "10.6084/m9.figshare.31127380"
    cmb_constraints: str = "10.6084/m9.figshare.31095466"
    cmb_thermodynamic: str = "10.6084/m9.figshare.31064929"
    
    # Regime architecture
    regime_transition: str = "10.6084/m9.figshare.31096951"
    l0_l3_architecture: str = "10.6084/m9.figshare.31112536"
    regime_breakdown: str = "10.6084/m9.figshare.31061665"
    
    # Galaxy scale
    sparc_175: str = "10.6084/m9.figshare.31045126"
    sparc_ebe: str = "10.6084/m9.figshare.31047703"
    regime_validity: str = "10.6084/m9.figshare.31007248"
    
    # High-z observations
    cosmos_web: str = "10.6084/m9.figshare.31059964"
    structure_formation: str = "10.6084/m9.figshare.31061872"
    
    # AI methodology
    validity_aware_ai: str = "10.6084/m9.figshare.31122970"
    
    # Tensions
    h0_s8_tensions: str = "10.6084/m9.figshare.31026151"
    
    # Cross-domain
    free_energy_principle: str = "10.6084/m9.figshare.31042678"
    
    def url(self, doi: str) -> str:
        """Get full URL for a DOI."""
        return f"https://doi.org/{doi}"
    
    def all(self) -> Dict[str, str]:
        """Return all DOIs as dictionary."""
        return {
            "foundations": self.foundations,
            "desi_bao": self.desi_bao,
            "cmb_constraints": self.cmb_constraints,
            "cmb_thermodynamic": self.cmb_thermodynamic,
            "regime_transition": self.regime_transition,
            "l0_l3_architecture": self.l0_l3_architecture,
            "regime_breakdown": self.regime_breakdown,
            "sparc_175": self.sparc_175,
            "sparc_ebe": self.sparc_ebe,
            "regime_validity": self.regime_validity,
            "cosmos_web": self.cosmos_web,
            "structure_formation": self.structure_formation,
            "validity_aware_ai": self.validity_aware_ai,
            "h0_s8_tensions": self.h0_s8_tensions,
            "free_energy_principle": self.free_energy_principle,
        }


DOIS = DOIRegistry()


# =============================================================================
# Physical Constants
# =============================================================================

@dataclass(frozen=True)
class EFCConstants:
    """Physical constants and reference values for EFC calculations."""
    
    # Gravitational constant (SI)
    G_N: float = 6.67430e-11  # m³ kg⁻¹ s⁻²
    
    # Speed of light (SI)
    c: float = 299792458.0  # m/s
    
    # Planck constraints (2018)
    H0_planck: float = 67.4  # km/s/Mpc
    H0_planck_err: float = 0.5
    omega_m_planck: float = 0.315
    omega_m_planck_err: float = 0.007
    
    # CMB
    z_cmb: float = 1089.0
    T_cmb: float = 2.7255  # K
    
    # Fugaku/DESI reference values
    delta_F_fugaku: float = 0.1  # Transition estimator
    delta_F_uncertainty: float = 0.03
    omega_m_offset: float = 0.10  # ~10% offset relative to Planck
    
    # Regime boundaries (Mpc)
    scale_L0_min: float = 100.0
    scale_L1_min: float = 1.0
    scale_L2_min: float = 0.001
    
    # Entropy thresholds (normalized S)
    S_low_max: float = 0.1
    S_mid_max: float = 0.9
    
    # Unit conversions
    Mpc_to_m: float = 3.0857e22
    kpc_to_Mpc: float = 0.001
    
    # Reference μ values by regime
    mu_L0: float = 1.00
    mu_L1: float = 1.05
    mu_L2: float = 1.15
    mu_L3: float = 1.00


EFC_CONSTANTS = EFCConstants()


# =============================================================================
# External References
# =============================================================================

EXTERNAL_REFS = {
    "DESI_2024": {
        "title": "DESI 2024 VI: Cosmological Constraints from BAO",
        "arxiv": "2404.03002",
        "year": 2024,
    },
    "Planck_2018": {
        "title": "Planck 2018 results. VI. Cosmological parameters",
        "journal": "A&A 641, A6",
        "year": 2020,
    },
    "Uchuu_2021": {
        "title": "The Uchuu simulations: Data Release 1",
        "journal": "MNRAS 506, 4210",
        "year": 2021,
        "note": "Fugaku N-body baseline",
    },
    "SPARC": {
        "title": "Spitzer Photometry and Accurate Rotation Curves",
        "url": "http://astroweb.cwru.edu/SPARC/",
    },
}
