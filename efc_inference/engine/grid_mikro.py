"""GridMikroEngine — the grid microphysics behind μ(g) (L-031).

Builds on Morten's published DOIs — the formulas are TAKEN from
the papers, not invented:

- DOI 10.6084/m9.figshare.31942821 (Derivation of Γ(ρ)):
  Γ(ρ) = Γ0 · ρ/(ρ + ρcrit) — linear at low density, saturating at
  high, with ρcrit from the grid-mode scale a0. Γ(ρ) (dynamic) is separated
  from μBE(g) (static) — no double counting.
- DOI 10.6084/m9.figshare.31942800 (Density of States Deff(ρ)):
  Deff(ρ) ∝ √(ρ/ρcrit) with ρcrit = a0/(GN·lg) — boundary-mode
  activation on a finite lattice well. This upgrades the bridge to
  Scenario B+: Γ(ρ) = Γ0·y/(1+y) with y = √(ρ/ρcrit).

Two scenarios are implemented and declared explicitly:
  scenario A  (31942821): Γ = Γ0·ρ/(ρ+ρcrit)
  scenario B+ (31942800): Γ = Γ0·y/(1+y), y = √(ρ/ρcrit)

Regimes (both scenarios):
  low density : Γ ~ linear in ρ (or ~√ρ in B+)
  saturated   : Γ → Γ0 when ρ >> ρcrit

Honesty: this is the microphysical hypothesis of EFC (Scenario B+ is the
paper's own upgrade), NOT consensus physics. L-031 stands open
until the predictions from the papers' sealed tables are tested.
"""
from __future__ import annotations

import math

import numpy as np

from efc_inference.engine.base_engine import EFCEngine


class GridMikroEngine(EFCEngine):
    """The entropy production Γ(ρ) and Deff(ρ) from the grid modes."""

    REQUIRED_PARAMS = ["rho", "rho_crit", "Gamma0"]

    DOI = {
        "gamma_derivation": "10.6084/m9.figshare.31942821",
        "density_of_states": "10.6084/m9.figshare.31942800",
    }

    @property
    def name(self) -> str:
        return "grid_mikro"

    def compute(self, params_dict: dict,
                coordinates: np.ndarray) -> np.ndarray:
        """Given density values, return Γ(ρ) per point (scenario B+)."""
        if not self.validate_params(params_dict):
            return np.full((len(np.atleast_1d(coordinates)),), np.nan)
        coords = np.asarray(coordinates, dtype=float)
        out = []
        for rho in coords:
            p = {**params_dict, "rho": float(rho)}
            out.append(self.gamma(p, scenario="B_plus"))
        return np.array(out)

    def deff(self, params: dict) -> float:
        """Deff(ρ) ∝ √(ρ/ρcrit) — boundary-mode activation (31942800)."""
        rho = float(params["rho"])
        rho_crit = float(params["rho_crit"])
        if rho < 0 or rho_crit <= 0:
            return float("nan")
        return float(math.sqrt(rho / rho_crit))

    def gamma(self, params: dict, scenario: str = "B_plus") -> float:
        """Γ(ρ) in scenario A or B+.

        A:  Γ0·ρ/(ρ+ρcrit)                    (31942821)
        B+: Γ0·y/(1+y), y = √(ρ/ρcrit)        (31942800)
        """
        rho = float(params["rho"])
        rho_crit = float(params["rho_crit"])
        G0 = float(params["Gamma0"])
        if rho < 0 or rho_crit <= 0:
            return float("nan")
        if scenario == "A":
            return float(G0 * rho / (rho + rho_crit))
        if scenario == "B_plus":
            y = math.sqrt(rho / rho_crit)
            return float(G0 * y / (1.0 + y))
        raise ValueError(f"unknown scenario: {scenario}")

    def regime(self, params: dict) -> str:
        rho = float(params["rho"])
        rho_crit = float(params["rho_crit"])
        if not (math.isfinite(rho) and math.isfinite(rho_crit)) \
                or rho < 0 or rho_crit <= 0:
            return "ugyldig"
        if rho < rho_crit:
            return "lav_tetthet"
        return "mettet"

    def regime_node(self, params: dict) -> dict:
        return {
            "id": "efc.grid_mikro_engine",
            "synlighet": self.SYNLIGHET,
            "regime": {
                "name": self.regime(params),
                "validity": "lav_tetthet: Gamma ~ linear (A) or ~ "
                            "sqrt-rho (B+); saturated: Gamma -> Gamma0 for "
                            "rho >> rho_crit. Does NOT predict observed "
                            "rotation curves alone — this is the bridge, "
                            "not the finished response.",
            },
            "phase": self.regime(params),
            "measure": {
                "target": "Gamma(rho) and Deff(rho)",
                "measurer": "the theoretical derivation (von Neumann "
                            "entropy over the BE occupancy statistics of "
                            "the grid modes)",
                "instrument": "no direct one — microphysical derivation, "
                              "model-dependent",
                "proxy_chain": ["density -> grid-mode occupancy -> "
                                "entropy production — a pure theory chain"],
                "placement": "theory space",
                "compression": "the grid microphysics is compressed to "
                               "y = sqrt(rho/rho_crit)",
            },
            "episenter": ("the grid frame: rho_crit = a0/(GN lg) is a "
                          "reading of the density at the scale of the "
                          "grid mode — not a direct observable"),
            "buffer": {
                "role": "the grid modes are the buffer — the entropy of "
                        "occupied modes charges with the density and saturates",
                "note": "the same saturating buffer form as the battery "
                        "and the homeostat — here at lattice scale",
            },
            "ontology": {
                "assumes": [
                    "grid-modene følger Bose-Einstein-okkuperings-"
                    "statistikk (31942821)",
                    "Deff(ρ) comes from boundary-mode activation on a "
                    "finite lattice well (31942800)",
                    "Scenario B+ is the microphysical HYPOTHESIS of EFC — "
                    "not consensus physics; L-031 stands open until the "
                    "sealed predictions of the papers are tested",
                    "Gamma(rho) is DYNAMIC and is separated from muBE(g), "
                    "which is static — double counting is explicitly "
                    "resolved",
                ],
                "source": ("DOI 10.6084/m9.figshare.31942821 and "
                           "10.6084/m9.figshare.31942800 (Magnusson, "
                           "2026)"),
            },
            "observer": {
                "bandwidth": "no instrument window — pure derivation; "
                             "it is a hole in itself that no direct "
                             "measurement exists",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "density -> mode occupancy -> entropy "
                        "production -> effective gravitational response — "
                        "the loop is the paper's bridge",
                "properties": ["linearity at low density",
                               "saturation at high density"],
            },
            "fractal": {
                "pattern": "lattice mode -> grid well -> galaxy "
                           "response: the same saturating form at every scale",
                "note": "y = sqrt(rho/rho_crit) is the microphysical "
                        "version of the buffer saturation",
            },
            "coupling": {
                "local": "each lattice cell contributes locally",
                "global": "Deff(ρ) aggregates the modes into the "
                          "gravitationally active density of states",
                "empathy_note": "the most invisible layer carries the bridge "
                                "between GR and QFT — and it is derived, "
                                "not measured",
            },
            "perspektiv": "paradigme",
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "ingen",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "our own frame — carried by us, "
                                    "not by the field",
                "konsensus_er_ikke_sannhet": True,
            },
            "maale_paradigme": {
                "koordinater": ["masse", "rom", "energi"],
                "enheter": "rho_crit = a0/(GN lg)",
                "status": "avledet",
                "alternativer": ["konsensus-QFT uten grid-struktur"],
            },
            "stipulasjoner": {
                "stipulert_av_oss": True,
                "terskler": ["rho_crit = a0/(GN lg) — the boundary between "
                             "low and saturated is OUR scale definition"],
                "motor": "grid_mikro",
            },
            "analogi": {
                "avbildning": ("grid-moders metning -> batteriets "
                               "ladekurve / hjemostasens setpunkt"),
                "bryter_der": ("the lattice modes are a theoretical "
                               "construct — the battery is measured; "
                               "the form is the same, the substrate's "
                               "status is not"),
            },
            # The placement is owned by the ATLAS (scripts/maintenance/efc_bro_konvensjon.py):
            # the engine cannot know where in the staircase its node belongs. The field must
            # nevertheless stand here because RegimeNode requires it — the test binds them.
            "nivaa": {
                "indeks": 3,
                "forelder": "efc.grid_mikrofysikk",
                "tidsskala": "gitter-skala",
                "lengdeskala": "lg (grid-lengden)",
            },
        }
