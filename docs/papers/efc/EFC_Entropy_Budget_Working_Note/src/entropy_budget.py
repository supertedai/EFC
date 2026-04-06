"""
EFC Entropy Budget — Source Module
DOI: 10.6084/m9.figshare.31942734

Implements the cosmic entropy budget analysis as constraint on the EFC S-field.
Key result: SMBH-dominated entropy (~10^104 k_B) is structurally consistent
with S=S_max (grid collapse boundary) in the GRC triad.

References:
  Magnusson 2026, "The Cosmic Entropy Budget as Constraint on the EFC S-Field"
  Egan & Lineweaver 2010, ApJ 710, 1825
  Bekenstein 1973, Phys. Rev. D 7, 2333
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ── Physical constants ──────────────────────────────────────────────
G = 6.674e-11        # m^3 kg^-1 s^-2
C = 2.998e8          # m/s
HBAR = 1.055e-34     # J·s
K_B = 1.381e-23      # J/K
M_SUN = 1.989e30     # kg
L_P = 1.616e-35      # Planck length, m


# =====================================================================
#  1. Cosmic Entropy Inventory  (Table 1 of the paper)
# =====================================================================
@dataclass
class EntropyComponent:
    """Single component of the cosmic entropy budget."""
    name: str
    log10_entropy_kB: float        # log10(S / k_B)
    description: str
    s_field_regime: str            # EFC S-field interpretation

    @property
    def entropy_kB(self) -> float:
        """Entropy in units of k_B."""
        return 10 ** self.log10_entropy_kB

    @property
    def entropy_SI(self) -> float:
        """Entropy in J/K."""
        return self.entropy_kB * K_B


class CosmicEntropyInventory:
    """
    Table 1: Cosmic entropy budget (Egan & Lineweaver 2010).

    SMBH entropy dominates at ~10^104 k_B, comprising >99.99% of the total.
    In EFC, this maps to S = S_max (grid collapse boundary).

    >>> inv = CosmicEntropyInventory()
    >>> inv.dominant_component().name
    'Supermassive black holes'
    >>> inv.smbh_fraction() > 0.99
    True
    """

    def __init__(self):
        self.components: List[EntropyComponent] = [
            EntropyComponent(
                name="Supermassive black holes",
                log10_entropy_kB=104.0,
                description="~10^10 SMBHs, M ~ 10^6-10^10 M_sun",
                s_field_regime="S = S_max (grid collapse)",
            ),
            EntropyComponent(
                name="Stellar-mass black holes",
                log10_entropy_kB=98.0,
                description="~10^8-10^9 stellar BHs, M ~ 5-50 M_sun",
                s_field_regime="S = S_max (grid collapse)",
            ),
            EntropyComponent(
                name="CMB photons",
                log10_entropy_kB=89.0,
                description="T = 2.725 K, ~411 photons/cm^3",
                s_field_regime="S → S_max (thermal equilibrium limit)",
            ),
            EntropyComponent(
                name="Relic neutrinos",
                log10_entropy_kB=88.0,
                description="T_nu ≈ 1.95 K, 3 flavours",
                s_field_regime="S → S_max (thermal limit)",
            ),
            EntropyComponent(
                name="Baryonic matter",
                log10_entropy_kB=81.0,
                description="Stars, gas, dust",
                s_field_regime="S ≪ S_max (structured)",
            ),
        ]

    def total_entropy_kB(self) -> float:
        """Total entropy in k_B (dominated by SMBHs)."""
        return sum(c.entropy_kB for c in self.components)

    def dominant_component(self) -> EntropyComponent:
        """Return the component with the largest entropy."""
        return max(self.components, key=lambda c: c.log10_entropy_kB)

    def smbh_fraction(self) -> float:
        """Fraction of total entropy in SMBHs."""
        total = self.total_entropy_kB()
        smbh = next(c for c in self.components if "Supermassive" in c.name)
        return smbh.entropy_kB / total

    def fraction(self, name: str) -> float:
        """Fraction of total entropy for a named component."""
        total = self.total_entropy_kB()
        comp = next(c for c in self.components if name.lower() in c.name.lower())
        return comp.entropy_kB / total

    def summary(self) -> Dict[str, float]:
        """Return dict of component name → log10(S/k_B)."""
        return {c.name: c.log10_entropy_kB for c in self.components}


# =====================================================================
#  2. Bekenstein-Hawking Entropy
# =====================================================================
class BekensteinHawkingEntropy:
    """
    Bekenstein-Hawking entropy: S_BH = 4π G M² k_B / (ℏ c)

    This is the maximum entropy for a region of given mass — the holographic
    bound. In EFC, BH horizons represent S = S_max (grid collapse).

    >>> bh = BekensteinHawkingEntropy()
    >>> s = bh.entropy_kB(1e6 * M_SUN)
    >>> 1e76 < s < 1e78
    True
    """

    @staticmethod
    def entropy_kB(mass_kg: float) -> float:
        """
        Bekenstein-Hawking entropy in units of k_B.
        S_BH = 4π G M² k_B / (ℏ c)
        """
        return 4.0 * math.pi * G * mass_kg**2 / (HBAR * C)

    @staticmethod
    def entropy_SI(mass_kg: float) -> float:
        """Bekenstein-Hawking entropy in J/K."""
        return BekensteinHawkingEntropy.entropy_kB(mass_kg) * K_B

    @staticmethod
    def horizon_area(mass_kg: float) -> float:
        """Schwarzschild horizon area A = 16πG²M²/c⁴ in m²."""
        return 16.0 * math.pi * G**2 * mass_kg**2 / C**4

    @staticmethod
    def entropy_from_area(area_m2: float) -> float:
        """S = A k_B / (4 l_P²) in units of k_B."""
        return area_m2 / (4.0 * L_P**2)

    @staticmethod
    def mass_from_entropy_kB(s_kB: float) -> float:
        """Invert Bekenstein-Hawking: M = sqrt(S ℏ c / (4π G))."""
        return math.sqrt(s_kB * HBAR * C / (4.0 * math.pi * G))

    @staticmethod
    def typical_smbh_entropy() -> Dict[str, float]:
        """
        Entropy for representative SMBH masses (Table context).
        Returns {label: log10(S/k_B)}.
        """
        masses = {
            "Sgr A* (4×10^6 M_sun)": 4e6 * M_SUN,
            "M87* (6.5×10^9 M_sun)": 6.5e9 * M_SUN,
            "TON 618 (6.6×10^10 M_sun)": 6.6e10 * M_SUN,
        }
        return {
            label: math.log10(BekensteinHawkingEntropy.entropy_kB(m))
            for label, m in masses.items()
        }


# =====================================================================
#  3. GRC Triad Mapping  (Table 2)
# =====================================================================
@dataclass
class GRCConfiguration:
    """A row of Table 2: phenomenon → GRC triad configuration."""
    phenomenon: str
    grid_state: str       # G
    energy_state: str     # E (called R for "Reality" flow in some notation)
    clarity_S: str        # S-field value / regime
    description: str


class GRCTriadMapping:
    """
    Table 2: How different cosmic phenomena map onto the GRC triad
    Reality = Grid ⊗ Energy · Clarity(S).

    >>> grc = GRCTriadMapping()
    >>> grc.get("black_holes").clarity_S
    'S = S_max'
    >>> len(grc.configurations)
    4
    """

    def __init__(self):
        self.configurations: Dict[str, GRCConfiguration] = {
            "particles": GRCConfiguration(
                phenomenon="Elementary particles",
                grid_state="Discrete nodes",
                energy_state="Quantised modes",
                clarity_S="S → 0 (low entropy, high clarity)",
                description="Minimal entropy; grid fully resolved",
            ),
            "fields": GRCConfiguration(
                phenomenon="Classical fields",
                grid_state="Continuum limit",
                energy_state="Smooth flow",
                clarity_S="S ≈ 0.5 S_max (intermediate)",
                description="Intermediate entropy; effective field theory regime",
            ),
            "cmb": GRCConfiguration(
                phenomenon="CMB radiation",
                grid_state="Thermalised grid",
                energy_state="Planck spectrum",
                clarity_S="S → S_max (thermal equilibrium)",
                description="Maximal thermal entropy; information fully delocalised",
            ),
            "black_holes": GRCConfiguration(
                phenomenon="Black holes",
                grid_state="Collapsed grid",
                energy_state="Trapped flow",
                clarity_S="S = S_max",
                description="Grid collapse boundary; Bekenstein-Hawking entropy saturates bound",
            ),
        }

    def get(self, key: str) -> GRCConfiguration:
        """Look up a GRC configuration by key."""
        return self.configurations[key]

    def all_configurations(self) -> List[GRCConfiguration]:
        """Return all GRC configurations."""
        return list(self.configurations.values())

    def s_field_hierarchy(self) -> List[Tuple[str, str]]:
        """Return configurations ordered by S-field value (low → high)."""
        order = ["particles", "fields", "cmb", "black_holes"]
        return [(k, self.configurations[k].clarity_S) for k in order]


# =====================================================================
#  4. S-Field Normalization  (Eq. 2 of the paper)
# =====================================================================
class SFieldNormalization:
    """
    S-field mapping: S_EFC / S_max = S_BH / S_BH,max(M)

    Maps the Bekenstein-Hawking entropy of a black hole to the normalised
    EFC S-field. For a BH at its maximum mass (Hubble-scale), ratio → 1.

    >>> sf = SFieldNormalization()
    >>> r = sf.ratio(mass_kg=1e6 * M_SUN, m_max_kg=1e10 * M_SUN)
    >>> 0 < r < 1
    True
    """

    @staticmethod
    def ratio(mass_kg: float, m_max_kg: float) -> float:
        """
        S_EFC/S_max = (M/M_max)² since S_BH ∝ M².
        """
        return (mass_kg / m_max_kg) ** 2

    @staticmethod
    def s_efc(mass_kg: float, m_max_kg: float, s_max: float = 1.0) -> float:
        """Compute S_EFC given a mass and reference maximum."""
        return s_max * SFieldNormalization.ratio(mass_kg, m_max_kg)

    @staticmethod
    def mass_for_ratio(target_ratio: float, m_max_kg: float) -> float:
        """What mass gives a desired S_EFC/S_max ratio?"""
        return m_max_kg * math.sqrt(target_ratio)

    @staticmethod
    def grid_collapse_condition(mass_kg: float, m_max_kg: float) -> bool:
        """
        Grid collapse occurs when S_EFC/S_max → 1,
        i.e., M → M_max for the system.
        """
        return SFieldNormalization.ratio(mass_kg, m_max_kg) > 0.99


# =====================================================================
#  5. Thermostat Conjecture  (Section 3 of the paper)
# =====================================================================
class ThermostatConjecture:
    """
    SMBH Thermostat Conjecture: AGN activity decline drives S(z) sigmoid at z~1.

    Accretion luminosity: L_acc = η Ṁ c²
    Entropy production:   Ṡ_acc ≈ L_acc / T_acc

    AGN luminosity density peaks at z ≈ 2 and declines by ~10× to z = 0,
    driving the S-field transition in the same epoch as the DESI BAO fit.

    >>> tc = ThermostatConjecture()
    >>> l = tc.accretion_luminosity(mdot_kg_per_s=1.0 * M_SUN / (3.156e7))
    >>> l > 1e44
    True
    """

    # Typical radiative efficiency for thin disk accretion
    ETA_THIN_DISK = 0.1

    @staticmethod
    def accretion_luminosity(mdot_kg_per_s: float, eta: float = 0.1) -> float:
        """L_acc = η Ṁ c² in Watts."""
        return eta * mdot_kg_per_s * C**2

    @staticmethod
    def entropy_production_rate(luminosity_W: float, T_acc_K: float) -> float:
        """Ṡ_acc ≈ L_acc / T_acc in k_B/s."""
        return luminosity_W / (T_acc_K * K_B)

    @staticmethod
    def agn_luminosity_density(z: float) -> float:
        """
        Phenomenological AGN bolometric luminosity density (W/Mpc³).
        Simple model: peaks at z ≈ 2, declines exponentially to z = 0.
        ρ_L(z) = ρ_L,peak × exp(−((z − 2)/1.2)²)

        Normalised to ρ_L,peak ≈ 2 × 10^40 W/Mpc³.
        """
        rho_peak = 2.0e40  # W/Mpc³
        return rho_peak * math.exp(-((z - 2.0) / 1.2) ** 2)

    @staticmethod
    def s_field_sigmoid(z: float, z_mid: float = 1.0, delta_z: float = 0.5) -> float:
        """
        S(z)/S_max sigmoid transition driven by AGN decline.
        S(z) = 1 / (1 + exp(−(z − z_mid)/δz))

        At z >> z_mid: S → 1 (high entropy production era)
        At z << z_mid: S → 0 (entropy production quenched)
        """
        x = (z - z_mid) / delta_z
        # Clamp to avoid overflow
        x = max(-500.0, min(500.0, x))
        return 1.0 / (1.0 + math.exp(-x))

    @staticmethod
    def transition_redshift() -> Dict[str, float]:
        """Key redshifts for the thermostat transition."""
        return {
            "z_mid": 1.0,
            "z_AGN_peak": 2.0,
            "z_quench": 0.5,
            "delta_z": 0.5,
        }


# =====================================================================
#  6. Predictions & Open Gaps
# =====================================================================
@dataclass
class Prediction:
    """A testable prediction from the entropy budget analysis."""
    id: str
    description: str
    observable: str
    status: str = "untested"


@dataclass
class OpenGap:
    """An identified open gap requiring future work."""
    id: str
    description: str
    level: str  # L1/L2/L3


class Predictions:
    """
    Predictions P1–P4 and open gaps G1–G4 from the entropy budget paper.

    >>> p = Predictions()
    >>> len(p.predictions)
    4
    >>> p.get_prediction("P1").observable
    'SMBH mass function vs local gravitational coupling'
    """

    def __init__(self):
        self.predictions: List[Prediction] = [
            Prediction(
                id="P1",
                description="SMBH density correlates with local μ",
                observable="SMBH mass function vs local gravitational coupling",
            ),
            Prediction(
                id="P2",
                description="S(z) tracks AGN luminosity density",
                observable="BAO S(z) sigmoid vs AGN bolometric luminosity density",
            ),
            Prediction(
                id="P3",
                description="Void galaxies show enhanced μ",
                observable="Galaxy rotation curves in voids vs clusters",
            ),
            Prediction(
                id="P4",
                description="S_max scales with BH entropy for typical SMBH mass",
                observable="S_max normalization from BH population statistics",
            ),
        ]

        self.open_gaps: List[OpenGap] = [
            OpenGap(
                id="G1",
                description="Quantitative S(z)–AGN derivation from first principles",
                level="L2",
            ),
            OpenGap(
                id="G2",
                description="S-field normalization: relate S_max to physical units",
                level="L2",
            ),
            OpenGap(
                id="G3",
                description="Interior black hole description within EFC (L3 problem)",
                level="L3",
            ),
            OpenGap(
                id="G4",
                description="Hawking radiation as S-field decay channel",
                level="L3",
            ),
        ]

    def get_prediction(self, pid: str) -> Prediction:
        """Look up prediction by ID."""
        return next(p for p in self.predictions if p.id == pid)

    def get_gap(self, gid: str) -> OpenGap:
        """Look up gap by ID."""
        return next(g for g in self.open_gaps if g.id == gid)

    def summary(self) -> Dict[str, str]:
        """Return dict of prediction/gap ID → description."""
        result = {p.id: p.description for p in self.predictions}
        result.update({g.id: g.description for g in self.open_gaps})
        return result
