"""EFC Water Phase Engine — H2O fasemotor (trinn 1, runde 2).

Beregner fase-grense-kurvene til H2O (damp, smelte, sublimasjon) og
klassifiserer fasen for et gitt (T, P)-punkt, fra materialparametre og
Clausius-Clapeyron-ligningen — ikke fra tabell-oppslag.

Modell-agnostisk i CoolPack-ånden: alle fysiske konstanter er innganger
(REQUIRED_PARAMS), saa alternative beskrivelser av samme regime kan
plugges inn og sammenlignes uten aa bytte motor.

EFC-rolle: H2O er demonstratoraksen for node/regime/fase/emergens/proxy.
Fasene er regimer med egne gyldighetsomraader; grensekurvene er
regimeovergangene; trippelpunktet er punktet der tre regimer moetes.

Gyldighetsomraader (hvert regime svarer NaN utenfor sitt, maalt mot IAPWS):
    saturation_pressure :  t_triple <= T <= t_vap_ref
                           (Watson-korrelasjonen n=0.33 er kalibrert i
                           0-100 C; ved 450 K er avviket -9.7 %, ved 625 K
                           -52.5 % — derfor ingen extrapolering mot T_c)
    melting_temperature :  0 <= P <= p_ice_ih_max (208.566 MPa, IAPWS
                           R14-08; hoyere trykk er andre isfaser)
    sublimation_pressure:  t_sublim_min (50 K) <= T <= t_triple
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
        "p_critical",                # Pa (brukes i klassifiseringen)
        "latent_vaporization_ref",   # J/kg, ved t_vap_ref
        "t_vap_ref",                 # K — ogsaa ovre kalibreringsgrense
        "p_vap_ref",                 # Pa — fysisk referanse ved t_vap_ref
                                     # (kokepunkt per definisjon: 101325 Pa)
        "latent_fusion",             # J/kg
        "latent_sublimation",        # J/kg, ved ~0 C
        "gas_constant",              # J/(kg*K), R_v for H2O
        "density_ice",               # kg/m3
        "density_water",             # kg/m3
        "p_ice_ih_max",              # Pa — ice Ih-grensen (IAPWS R14-08)
        "t_sublim_min",              # K — nedre sublimasjonsgrense
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
        riktig: over kritisk punkt fins ingen latent varme. (Motoren
        bruker uansett bare korrelasjonen innenfor kalibreringsvinduet.)
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

        Gyldighetsomraade: t_triple <= T <= t_vap_ref. Utenfor: NaN
        (korrelasjonen er kalibrert i 0-100 C; extrapolering mot T_c
        ble maalt til -52.5 % avvik ved 625 K i uavhengig review).
        """
        t = np.atleast_1d(np.asarray(t, dtype=float))
        t0 = params["t_triple"]
        tmax = params["t_vap_ref"]
        r = params["gas_constant"]
        p0 = params["p_triple"]
        out = np.full(t.shape, np.nan)
        ok = (t >= t0) & (t <= tmax)
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
        """Smeltetemperatur T_m(P) langs fast-vaeske-grensen (ice Ih).

        Clausius-Clapeyron for fast-vaeske med konstant latent varme og
        volumendring:
            T_m(P) = t_triple * exp( dv_melt * (P - p_triple) / L_f )
        der dv_melt = 1/rho_vann - 1/rho_is < 0 (is flyter).

        Gyldighetsomraade: 0 <= P <= p_ice_ih_max (208.566 MPa, IAPWS
        R14-08). Over det finnes andre isfaser — NaN, ikke extrapolering.
        Negativt trykk avvises ogsaa deterministisk.
        """
        p = np.atleast_1d(np.asarray(p, dtype=float))
        dv = 1.0 / params["density_water"] - 1.0 / params["density_ice"]
        lf = params["latent_fusion"]
        out = np.full(p.shape, np.nan)
        ok = (p >= 0.0) & (p <= params["p_ice_ih_max"])
        out[ok] = params["t_triple"] * np.exp(
            dv * (p[ok] - params["p_triple"]) / lf)
        return out

    def sublimation_pressure(self, params: dict, t: np.ndarray) -> np.ndarray:
        """Sublimasjonstrykk P_sub(T) langs fast-gass-grensen.

        Clausius-Clapeyron med konstant L_s:
            P_sub(T) = p_triple * exp( -(L_s/R) * (1/T - 1/t_triple) )
        Gyldighetsomraade: t_sublim_min (50 K, IAPWS R14-08) <= T <=
        t_triple. Utenfor: NaN (negativ temperatur ga tidligere inf).
        """
        t = np.atleast_1d(np.asarray(t, dtype=float))
        out = np.full(t.shape, np.nan)
        ok = (t >= params["t_sublim_min"]) & (t <= params["t_triple"])
        r = params["gas_constant"]
        ls = params["latent_sublimation"]
        out[ok] = params["p_triple"] * np.exp(
            -(ls / r) * (1.0 / t[ok] - 1.0 / params["t_triple"]))
        return out

    # ------------------------------------------------------------------
    # Klassifisering — «hvilken fase er H2O her?»
    # ------------------------------------------------------------------

    # Relativ toleranse for «punktet ligger paa fasegrensen».
    EPS_REL = 1e-6
    EPS_T = 1e-6  # K

    def classify(self, params: dict, t: float, p: float) -> str:
        """Fase for ett (T, P)-punkt.

        Returverdier: solid, liquid, gas, supercritical, coexistence.
        - Superkritisk krever T > T_c OG P > P_c (konvensjonen); over
          T_c med P <= P_c er det én gasslignende fluidfase.
        - Et punkt paa en fasegrense (innenfor EPS_REL/EPS_T) er
          «coexistence» — to faser sameksisterer der, grensen er ikke
          en vilkaarlig side.
        """
        t = float(t)
        p = float(p)
        tc = params["t_critical"]
        pc = params["p_critical"]
        if t > tc:
            # Superkritisk krever STRENGT T > T_c og P > P_c (review runde 2).
            return "supercritical" if p > pc else "gas"
        if abs(t - tc) <= self.EPS_T:
            # Selve kritiske temperatur: P == P_c er det kritiske punktet
            # (grense), P < P_c er gass, P > P_c utenfor dommekraften.
            if abs(p - pc) <= self.EPS_REL * pc:
                return "coexistence"
            return "gas" if p < pc else "unknown"
        if (abs(t - params["t_vap_ref"]) <= self.EPS_T
                and abs(p - params["p_vap_ref"])
                <= self.EPS_REL * params["p_vap_ref"]):
            # Kokepunktet er en fasegrense — modellens P_sat(373.15)
            # ligger 1.7 % under den fysiske definisjonen, saa
            # referansepunktet maa brukes her. Staar FOER t_vap_ref-
            # grenen slik at toleransen er symmetrisk paa begge sider
            # av kokepunktstemperaturen (review runde 3).
            return "coexistence"
        if t > params["t_vap_ref"]:
            # Over kalibreringsvinduet er P_sat monotont stigende, og den
            # FYSISKE referansen p_vap_ref (kokepunkt per definisjon) er en
            # nedre grense for ekte P_sat(T). p <= p_vap_ref er SIKKERT
            # gass. Hoyere p kan motoren ikke avgjoere ærlig — «unknown»,
            # ikke en gjettet side.
            return "gas" if p <= params["p_vap_ref"] else "unknown"
        if t < params["t_triple"]:
            p_vap = float(self.sublimation_pressure(
                params, np.array([t]))[0])
        else:
            p_vap = float(self.saturation_pressure(
                params, np.array([t]))[0])
        t_melt = float(self.melting_temperature(params, np.array([p]))[0])
        if (abs(p - p_vap) <= self.EPS_REL * max(p_vap, 1.0)
                or abs(t - t_melt) <= self.EPS_T):
            return "coexistence"
        if t < t_melt:
            return "gas" if p < p_vap else "solid"
        return "gas" if p <= p_vap else "liquid"

    # ------------------------------------------------------------------
    # EFCEngine-kontrakten
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """Primaerobservabel: dampkurven. coordinates = 1-D T-array (K).

        Kontrakten: ugyldige eller manglende parametre og feil
        koordinatformer gir NaN-array — aldri unntak.
        """
        coordinates = np.asarray(coordinates, dtype=float)
        try:
            ok = self.validate_params(params_dict)
        except (TypeError, ValueError):
            # Ugyldige parametertyper (None, streng, array) skal feile
            # lukket som NaN, ikke som unntak (review runde 2).
            ok = False
        if coordinates.ndim != 1 or not ok:
            return np.full(coordinates.shape, np.nan)
        return self.saturation_pressure(params_dict, coordinates)

    # ------------------------------------------------------------------
    # Motor↔skjema-broen — motorens selvbeskrivelse som regime-node
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        """Full RegimeNode etter schema/regime_node.schema.json.

        Broen mellom motor og atlas: enhver EFCEngine med denne metoden
        er en gyldig node i EFC-atlaset — koblingsgrafen og regime-
        instansene kan konsumere selvbeskrivelsen maskinelt. Manifestet
        nedenfor er en bakoverkompatibel projeksjon av denne.

        Id og gyldighetsomraade er IKKE lokale valg: de skal stemme med
        h2o-nodenes deklarerte regimer i schema/regime_nodes.jsonld —
        konsistensen testes maskinelt (tests/test_engine_manifest_bridge.py).
        Grensene DERIVERES fra de effektive parametrene, slik at
        selvbeskrivelsen aldri lyver om motorens faktiske regimer —
        ogsa ved alternative parametre (review 2026-09-16).
        """
        t_vap = params["t_vap_ref"]
        p_ice = params["p_ice_ih_max"]
        t_sub = params["t_sublim_min"]
        n = float(params.get("watson_exponent", WATSON_EXPONENT_DEFAULT))
        validity = (
            "damp ["
            + str(params["t_triple"]) + ", " + str(t_vap) + "] K; "
            "smelte [0, " + str(p_ice / 1e6) + "] MPa (ice Ih); "
            "sublimasjon [" + str(t_sub) + " K, t_triple] — "
            "for kanoniske parametre identisk med h2o-nodenes gyldighetsomraader"
        )
        law_form = ("Clausius-Clapeyron med Watson L_v(T) (n=" + str(n)
                    + ") — numerisk integrasjon, ingen tabell-oppslag")
        return {
            "id": "efc.water_phase_engine",
            "perspektiv": "paradigme",
            "regime": {
                "name": "H2O fase-grense-beregning",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "fasegrenser P_sat(T), T_m(P), P_sub(T)",
                "measurer": "numerisk integrasjon av Clausius-Clapeyron",
                "instrument": "WaterPhaseEngine (efc_inference/engine/water.py)",
                "proxy_chain": [
                    "P_sat(T) via Watson L_v(T)",
                    "T_m(P) via dv_melt = 1/rho_vann - 1/rho_is",
                    "P_sub(T) via konstant L_s"
                ],
                "placement": "P-T-rom — motoren regner ett (T,P)-punkt om gangen",
                "compression": "grensekurver + faseklassifisering (solid/liquid/gas/supercritical + coexistence/unknown)"
            },
            "episenter": "P-T-landskapet — motoren leser det samme landskapet som h2o-nodene, og deklarerer de samme grensene",
            "buffer": {
                "role": "gyldighetsomraadene er motorens buffer: utenfor dem svarer den NaN/unknown i stedet for aa ekstrapolere",
                "note": "buffer-logikken i instrumentform: motoren demper sin egen overrekkevidde."
            },
            "ontology": {
                "assumes": [
                    "materialparametrene (latente varme, tettheter, kritiske konstanter) er korrekte",
                    "Clausius-Clapeyron gjelder i de deklarerte regimene"
                ],
                "source": "IAPWS R6-95/R14-08; standard termodynamikk; review-verifisert mot IAPWS (2026-09-16)"
            },
            "observer": {
                "bandwidth": "motoren ser bare T og P — ingen optiske, akustiske eller kjemiske kanaler",
                "awareness": "instrument_window"
            },
            "emergence": {
                "loop": "parametre -> grensekurver -> faseklassifisering -> kalibrering mot trippelpunktet -> parametre",
                "properties": [
                    "faseklassifisering",
                    "deklarert gyldighetsomraade per kurve"
                ]
            },
            "fractal": {
                "pattern": "samme beregningslov i hvert punkt av P-T-landskapet — motoren er en instans av monsteret h2o-nodene beskriver",
                "note": "en motor, ett monster, tre grensekurver som moetes."
            },
            "coupling": {
                "local": "hver kurve beregnes lokalt i sitt regime",
                "global": "motorens gyldighetsomraader ER h2o-nodenes — og broen testes maskinelt mot regime_nodes.jsonld",
                "empathy_note": "motoren vet hvilke atlas-noder den baerer (CARRIES), og testene verifiserer at den ikke deklarerer noe atlaset motsier."
            },
        }

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
