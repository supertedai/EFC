"""EFC Water Phase Engine — H2O fasemotor (trinn 1).

Beregner fase-grense-kurvene til H2O (damp, smelte, sublimasjon) og
klassifiserer fasen for et gitt (T, P)-punkt, fra materialparametre og
Clausius-Clapeyron-ligningen — ikke fra tabell-oppslag.

Modell-agnostisk i CoolPack-ånden: alle fysiske konstanter er innganger
(REQUIRED_PARAMS), saa alternative beskrivelser av samme regime kan
plugges inn og sammenlignes uten aa bytte motor.

EFC-rolle: H2O er demonstratoraksen for node/regime/fase/emergens/proxy.
Fasene er regimer med egne gyldighetsomraader; grensekurvene er
regimeovergangene; trippelpunktet er punktet der tre regimer moetes.
Motoren svarer «utenfor gyldighetsomraade» med NaN, ikke med et tall.

Regimegrenser (hver metode har sitt regime):
    saturation_pressure :  t_triple <= T <= t_critical   (vaeske <-> gass)
    melting_temperature :  alle P (is I)                 (fast <-> vaeske)
    sublimation_pressure:  T <= t_triple                 (fast <-> gass)
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine

# Watson-eksponent for L_v(T) i 0-100 C-vinduet. Maa lt mot tabellverdier:
# n=0.33 gir 2501 kJ/kg ved 0 C, 2443 ved 25 C, 2385 ved 50 C, 2323 ved 75 C
# (kjente verdier: 2501, 2442, 2383, 2321) — n=0.38 overvurderer lavintervallet.
WATSON_EXPONENT_DEFAULT = 0.33


class WaterPhaseEngine(EFCEngine):
    """Fase-grense-motor for H2O (trinn 1: grensekurver + klassifisering)."""

    REQUIRED_PARAMS = [
        "t_triple",                  # K
        "p_triple",                  # Pa
        "t_critical",                # K
        "latent_vaporization_ref",   # J/kg, ved t_vap_ref
        "t_vap_ref",                 # K
        "latent_fusion",             # J/kg
        "latent_sublimation",        # J/kg, ved ~0 C
        "gas_constant",              # J/(kg*K), R_v for H2O
        "density_ice",               # kg/m3
        "density_water",             # kg/m3
    ]

    @property
    def name(self) -> str:
        return "water_phase"

    # ------------------------------------------------------------------
    # Fysikk
    # ------------------------------------------------------------------

    def _watson_lv(self, params: dict, t) -> np.ndarray:
        """Latent fordampningsvarme L_v(T) via Watson-korrelasjonen.

        L_v(T) = L_ref * ((Tc - T) / (Tc - T_ref)) ** n
        For T > Tc blir argumentet negativt og resultatet NaN — det er
        riktig: over kritisk punkt fins ingen latent varme.
        """
        n = float(params.get("watson_exponent", WATSON_EXPONENT_DEFAULT))
        tc = params["t_critical"]
        tref = params["t_vap_ref"]
        lref = params["latent_vaporization_ref"]
        return lref * ((np.asarray(tc) - np.asarray(t)) / (tc - tref)) ** n

    def saturation_pressure(self, params: dict, t: np.ndarray) -> np.ndarray:
        """Damptrykk P_sat(T) langs vaeske-gass-grensen.

        Integrert Clausius-Clapeyron med L_v(T):
            P_sat(T) = p_triple * exp( int_{t_triple}^{T} L_v/(R T^2) dT )

        Gyldighetsomraade: t_triple <= T <= t_critical. Utenfor: NaN.
        """
        t = np.asarray(t, dtype=float)
        t0 = params["t_triple"]
        tc = params["t_critical"]
        r = params["gas_constant"]
        p0 = params["p_triple"]
        out = np.full(t.shape, np.nan)
        ok = (t >= t0) & (t <= tc)
        if not np.any(ok):
            return out
        try:
            trapz = np.trapezoid  # numpy >= 2.0
        except AttributeError:
            trapz = np.trapz
        for i in np.flatnonzero(ok):
            ti = float(t[i])
            if abs(ti - t0) < 1e-12:
                out[i] = p0  # integralet er null — eksakt per kalibrering
                continue
            # Tett grid som ender EKSAKT i ti — et grid som stopper paa
            # siste punkt under ti, underslaar halen og drev kokepunktet
            # fra 99.6 kPa til 97.3 kPa (maalt).
            tt = np.linspace(t0, ti, 400)
            lv = self._watson_lv(params, tt)
            integrand = lv / (r * tt * tt)
            out[i] = p0 * np.exp(trapz(integrand, tt))
        return out

    def melting_temperature(self, params: dict, p: np.ndarray) -> np.ndarray:
        """Smeltetemperatur T_m(P) langs fast-vaeske-grensen (is I).

        Clausius-Clapeyron for fast-vaeske med konstant latent varme og
        volumendring:
            T_m(P) = t_triple * exp( dv_melt * (P - p_triple) / L_f )
        der dv_melt = 1/rho_vann - 1/rho_is < 0 (is flyter).
        """
        p = np.asarray(p, dtype=float)
        dv = 1.0 / params["density_water"] - 1.0 / params["density_ice"]
        lf = params["latent_fusion"]
        return params["t_triple"] * np.exp(dv * (p - params["p_triple"]) / lf)

    def sublimation_pressure(self, params: dict, t: np.ndarray) -> np.ndarray:
        """Sublimasjonstrykk P_sub(T) langs fast-gass-grensen.

        Clausius-Clapeyron med konstant L_s:
            P_sub(T) = p_triple * exp( -(L_s/R) * (1/T - 1/t_triple) )
        Gyldighetsomraade: T <= t_triple. Over: NaN.
        """
        t = np.asarray(t, dtype=float)
        out = np.full(t.shape, np.nan)
        ok = t <= params["t_triple"]
        r = params["gas_constant"]
        ls = params["latent_sublimation"]
        out[ok] = params["p_triple"] * np.exp(
            -(ls / r) * (1.0 / t[ok] - 1.0 / params["t_triple"]))
        return out

    # ------------------------------------------------------------------
    # Klassifisering — «hvilken fase er H2O her?»
    # ------------------------------------------------------------------

    def classify(self, params: dict, t: float, p: float) -> str:
        """Fase for ett (T, P)-punkt: solid / liquid / gas / supercritical."""
        if t > params["t_critical"]:
            return "supercritical"
        if t < params["t_triple"]:
            p_vap = float(self.sublimation_pressure(
                params, np.array([t]))[0])
        else:
            p_vap = float(self.saturation_pressure(
                params, np.array([t]))[0])
        t_melt = float(self.melting_temperature(params, np.array([p]))[0])
        if t < t_melt:
            return "gas" if p < p_vap else "solid"
        return "gas" if p <= p_vap else "liquid"

    # ------------------------------------------------------------------
    # EFCEngine-kontrakten
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """Primaerobservabel: dampkurven. coordinates = T-array (K)."""
        return self.saturation_pressure(params_dict, coordinates)

    # ------------------------------------------------------------------
    # Empati-porten — hva motoren betjener og er kalibrert mot
    # ------------------------------------------------------------------

    def manifest(self, params: dict) -> dict:
        """Motorens globale koblingsflate: hvilke atlasbegreper den betjener,
        og hvilke fysiske referanser den er kalibrert mot. Konsumeres av
        koblingsgrafen/atlaset, slik at lokale beregninger har en erklært
        global rekkevidde (systemisk empati)."""
        return {
            "name": self.name,
            "couplings": [
                {"axis": "node",
                 "relation": "hvert (T,P)-punkt er en node i faseregimet"},
                {"axis": "regime",
                 "relation": "solid/liquid/gas/supercritical er regimer "
                             "med egne gyldighetsomraader"},
                {"axis": "fase",
                 "relation": "tre grensekurver som moetes i trippelpunktet"},
                {"axis": "emergens",
                 "relation": "faseegenskaper (tetthet, optikk) endres ved "
                             "overgangen — emergent per regime, ikke "
                             "lineært avledet"},
                {"axis": "proxy",
                 "relation": "P_sat, T_m og P_sub er observerbare proxyer "
                             "for fasen — fasen selv er en tilstand"},
            ],
            "calibration": {
                "t_triple": float(params["t_triple"]),
                "p_triple": float(params["p_triple"]),
                "t_critical": float(params["t_critical"]),
            },
        }
