"""EFC-bakgrunnsloeseren — den FOERSTE selvkonsistente FRW-bakgrunnen (L-033).

Kilde — aksjonspapiret
(docs/papers/efc/EFC_Relativistic_Action_Field_Equations_Perturbation_
Theory_and_Extraction), DOI 10.6084/m9.figshare.31876324.

Aksjonen (papirets eq. 1)::

    S = int d^4x sqrt(-g) [ 1/2 M_Pl^2 F(phi) R
                            - 1/2 K(rho) d_mu phi d^mu phi
                            - V(phi)
                            - lambda (box phi - Gamma(rho)) ]

    F(phi) = 1 + alpha phi                                    (eq. 1)
    K(rho) = K0 / (1 - rho/rho_crit)                          (eq. 2)
    Gamma(rho) = gamma0 (rho/rho_crit) / (1 + rho/rho_crit)   (eq. 47)
    Gamma'(rho) = gamma0 / (rho_crit (1 + rho/rho_crit)^2)    (eq. 48)

Bakgrunnsligningene er papirets egne (seksjon 4.1, FRW-metrikk eq. 11)::

    3 M_Pl^2 F(phi) H^2 = rho_m + 1/2 K(rho) phi_dot^2 + V(phi)
                          + 3 M_Pl^2 H F_dot + lambda_dot phi_dot     (12)
    phi_ddot + 3 H phi_dot = Gamma(rho)                                (13)

og responsfeltet lambda fra eq. 10::

    box lambda = V'(phi) - 1/2 M_Pl^2 F'(phi) R
                 - nabla_mu (K(rho) nabla^mu phi)                      (10)

VARFOR (12) OG (13) ER NOK SOM KRAV: (13) er flyt-betingelsen — den
bestemmer phi-dynamikken, og lambda absorberer resten (papirets egen
formulering: lambda er et RESPONSFELT). (12) er den modifiserte
Friedmann-ligningen og brukes her som STARTBETINGELSE for H. Evolusjonen
drives av akselerasjonsligningen — (i,j)-delen av eq. 7 — og residualen
til (12) langs loesningen rapporteres som en maalt indre konsistens.

TRE KONVENSJONER SOM ER GJORT EKSPLISITTE (ingen stille valg):

1. TEGNET PAA IKKE-MINIMALT-LEDDET. Papirets eq. (12) skriver
   ``+ 3 M_Pl^2 H F_dot``. Den direkte variasjonen av eq. (1) i den
   signaturen papiret selv oppgir (eq. 11: ds^2 = -dt^2 + a^2 dx^2) gir
   ``- 3 M_Pl^2 H F_dot`` — det er ogsaa den standarde formen for
   F(phi)R-gravitasjon. Begge kan velges med ``nonminimal_sign``
   (NONMINIMAL_SIGN_PAPER = +1, NONMINIMAL_SIGN_STANDARD = -1), og
   forskjellen maales i ``diagnostics``. LCDM-grensen skiller dem IKKE
   (der er F_dot = 0), saa valget er ikke skjult i falsifikatoren —
   det staar i tallet.

2. V(phi). Papiret spesifiserer ikke potensialet (framework.json lister
   ``V_phi: false`` bare for TENSOR-sektoren, ikke som V = 0). Vi velger
   V = const, fordi LCDM-grensen — kortets falsifikator — krever et
   Lambda-liknende ledd. Da er V/(3 M_Pl^2 H0^2) = Omega_Lambda når
   normaliseringen under brukes. Alternativet V = 0 gir Einstein-de
   Sitter, ikke LCDM; det er dokumentert, ikke skjult.

3. ENHETER. Alt er dimensjonsloest med ``H0 = M_Pl = 1``: tid maales i
   1/H0, tetthet i 3 M_Pl^2 H0^2, ``k0 = K0/M_Pl^2`` (K har masse^2),
   ``lambda_tilde = lambda/M_Pl^2`` og ``V0 = V/(3 M_Pl^2 H0^2)``.
   ``omega_crit = rho_crit/(3 M_Pl^2 H0^2)``. E(z) = H/H0 er
   enhetsoverflaten ut — den er den samme i alle enheter.

AERLIGHET — DETTE ER DEN FOERSTE BAKGRUNNEN, IKKE EN BOLTZMANN-KODE:
    * Ingen CMB, ingen perturbaSJONER, ingen EFCLASS. ``mu(k,z)``-modulen
      tar fortsatt bakgrunnen som INNGANG — men den faar den naa FRA
      denne loesningen (``mu_kz_inputs``) i stedet for fra luften.
    * Loeseren er definert bare for ``rho_m < rho_crit``: K divergerer
      (eq. 2), og loeseren stopper ved krysset og sier det
      (``status = "rho_crit_reached"``). Den fyller ikke inn tall.
    * Super-horisont og full ADM/Hamilton-analyse er aapent i papiret.
      Vi gjor ingen stabilitetspaastand ut over det som maales her.
    * Stråling er utelatt: E^2 inneholder Omega_m og Omega_Lambda, ikke
      Omega_r. Det er greit for z <~ 3, ikke for CMB-epoken.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp

from .base_engine import EFCEngine

# ---------------------------------------------------------------------------
# Konvensjoner (se modul-docstringen, punkt 1)
# ---------------------------------------------------------------------------

#: Papirets eq. (12) som trykket: + 3 M_Pl^2 H F_dot.
NONMINIMAL_SIGN_PAPER = 1.0

#: Direkte variasjon av eq. (1) i papirets egen signatur (og standard
#: scalar-tensor-form): - 3 M_Pl^2 H F_dot.
NONMINIMAL_SIGN_STANDARD = -1.0

#: Standardvalget. Begrunnelsen er MAALT, ikke smakt: se
#: ``BackgroundSolution.diagnostics["constraint_residual_max"]`` og testen
#: ``test_sign_konvensjonen_er_maalt_mot_constraint_residualen``.
NONMINIMAL_SIGN_DEFAULT = NONMINIMAL_SIGN_PAPER

#: Nokkelnavn loeseren krever. V0 kan vaere None (flat lukning).
PAKREVDE = ("alpha", "k0", "omega_crit", "gamma0", "Omega_m")
VALGFRIE_DEFAULTS = {
    "V0": None,
    "phi0": 0.0,
    "phi_dot0": 0.0,
    "lam0": 0.0,
    "lam_dot0": 0.0,
}

#: Hvordan T^(lambda) (eq. 6) fores inn i bakgrunnsligningene.
#:
#: "paper_eq12": papirets trykte form. Eq. (12) har bare ``lambda_dot phi_dot``
#:     — dvs. det andrederiverte leddet ``lambda(nabla nabla phi - g box phi)``
#:     i eq. (6) er droppet (papirets eget notat i seksjon 2.1 sier at
#:     varianter skiller seg med randledd og forskyver bidrag mellom
#:     Einstein- og phi-ligningen "without changing the physical content").
#: "full_eq6": hele eq. (6) med metrisk d'Alembert-operator:
#:     rho_lambda = lambda_dot phi_dot - 3 H lambda phi_dot,
#:     p_lambda   = lambda_dot phi_dot + lambda Gamma  (ved eq. 13).
#:     De to MAALES mot hverandre — constraint-residualen er dommen, ikke
#:     en paastand i en kommentar. Er de ikke ekvivalente, er det et funn.
LAMBDA_STRESS_FORMS = ("paper_eq12", "full_eq6")
LAMBDA_STRESS_DEFAULT = "paper_eq12"

KONSTRAINT_RESIDUAL_DEF = (
    "max |F E^2 - [rho_m + K phi_dot^2/(6(1-x)) + V0 + sigma E alpha phi_dot "
    "+ lambda_dot phi_dot/3]| / E^2 langs loesningen; x = rho_m/omega_crit. "
    "E er integrert via (i,j)-ligningen (eq. 7), ikke satt fra (12) — "
    "residualen er derfor en ekte maaling, ikke en tautologi."
)


# ---------------------------------------------------------------------------
# Aksjonens responsfunksjoner (eq. 2, 47, 48)
# ---------------------------------------------------------------------------

def kinetic_stiffness(k0: float, rho_over_crit: float) -> float:
    """Eq. 2 i enheter av M_Pl^2: K(rho)/M_Pl^2 = k0/(1 - rho/rho_crit).

    Divergerer ved rho -> rho_crit og er ikke definert for rho >= rho_crit
    (+inf), som i referansekoden (efc_relativistic.py:26-29) og i
    mu_kz.k_rho. Stivheten er modellens domene-vegg, ikke en advarsel.
    """
    if rho_over_crit >= 1.0:
        return np.inf
    return k0 / (1.0 - rho_over_crit)


def gamma_of_rho(gamma0: float, rho_over_crit: float) -> float:
    """Eq. 47, dimensjonsloes: Gamma/(H0^2) = gamma0 x/(1+x), x = rho/rho_crit."""
    x = rho_over_crit
    return gamma0 * x / (1.0 + x)


def gamma_prime_of_rho(gamma0: float, rho_over_crit: float) -> float:
    """Eq. 48, i enheter av rho_crit: dGamma/dx = gamma0/(1+x)^2.

    Samme tall som mu_kz.gamma_prime_rho naar den kalles med
    ``rho_crit = 1`` — testen ``test_gamma_og_gamma_prime_eq47_48``
    holder de to modulene sammen, slik at de ikke kan gli fra hverandre.
    """
    x = rho_over_crit
    return gamma0 / (1.0 + x) ** 2


#: Numerisk vegg: K og 1/(1-x)-leddene klippes denne avstanden innenfor
#: rho_crit. Uten den ville integratoren proeve et steg forbi domenet og
#: krasje i det ugylidge omraadet i stedet for aa stoppe ved veggen.
#: Klippingen er en numerisk vakt, ikke fysikk: loeseren RAPPORTERER at den
#: stoppet ved rho_crit (status + z_rho_crit), og punktene etter er NaN.
VEGG_EPS = 1e-9


def _x_num(rho_over_crit: float) -> float:
    """rho/rho_crit klippet til veggen (VEGG_EPS innenfor rho_crit)."""
    return min(rho_over_crit, 1.0 - VEGG_EPS)


def _normaliser(params: dict) -> dict:
    """Fyller inn defaults og sjekker at det som maa finnes, finnes."""
    mangler = [k for k in PAKREVDE if k not in params]
    if mangler:
        raise KeyError(f"mangler bakgrunnsparametre: {mangler}")
    p = {**VALGFRIE_DEFAULTS, **params}
    if p["omega_crit"] <= 0:
        raise ValueError("omega_crit maa vaere > 0 (K divergerer ved rho_crit)")
    if p["Omega_m"] <= 0:
        raise ValueError("Omega_m maa vaere > 0")
    return p


def _V0_fra_lukning(params: dict, nonminimal_sign: float,
                    lambda_stress: str = LAMBDA_STRESS_DEFAULT) -> float:
    """V0 = V/(3 M_Pl^2 H0^2) naar den skal settes av z=0-normaliseringen.

    E(0) = 1 (flat lukning) gir, med eq. (12) evaluert ved z = 0:

        V0 = F(phi0) - Omega_m - K(0) phi_dot0^2/6
             - sigma alpha phi_dot0 - rho_lambda0/3

    Samme konvensjon som EFC-hubble-motoren og LCDM-grensen krever; for en
    statisk phi ved z=0 er V0 = Omega_Lambda.
    """
    p = params
    if p["V0"] is not None:
        return float(p["V0"])
    x0 = p["Omega_m"] / p["omega_crit"]
    F0 = 1.0 + p["alpha"] * p["phi0"]
    kin = p["k0"] * p["phi_dot0"] ** 2 / (6.0 * (1.0 - x0))
    if lambda_stress == "full_eq6":
        rho_lam0 = p["lam_dot0"] * p["phi_dot0"] - 3.0 * p["lam0"] * p["phi_dot0"]
    else:
        rho_lam0 = p["lam_dot0"] * p["phi_dot0"]
    return float(F0 - p["Omega_m"] - kin
                 - nonminimal_sign * p["alpha"] * p["phi_dot0"]
                 - rho_lam0 / 3.0)


# ---------------------------------------------------------------------------
# Loesningen
# ---------------------------------------------------------------------------

@dataclass
class BackgroundSolution:
    """Bakgrunnen paa en z-grid. NaN der loeseren ikke har dekning."""

    z: np.ndarray
    a: np.ndarray
    E: np.ndarray              # H/H0
    rho_m: np.ndarray          # i enheter av 3 M_Pl^2 H0^2
    phi: np.ndarray
    phi_dot: np.ndarray        # d phi/d tau, tau = H0 t
    lam: np.ndarray            # lambda/M_Pl^2
    lam_dot: np.ndarray        # d lam/d tau
    status: str
    z_rho_crit: float | None
    diagnostics: dict
    honesty: dict
    params: dict
    nonminimal_sign: float

    # -- avledede, navngitte maal ------------------------------------------

    @property
    def lcdm_max_rel_error(self) -> float | None:
        """Maks |E_loeser/E_LCDM - 1| — bare definert naar loesningen ER
        LCDM-grensen: alpha = gamma0 = 0 OG phi_dot = lambda_dot = 0 ved
        z = 0 (ellers er den stive kinetiske energien ikke null og
        bakgrunnen er ikke LCDM). Ellers None — ikke 0."""
        return self.diagnostics.get("lcdm_max_rel_error")

    @property
    def h_consistency_max_rel(self) -> float:
        """Maks |E_integert - E_fra_eq12|/E langs loesningen."""
        return self.diagnostics["h_consistency_max_rel"]

    def mu_kz_inputs(self, z: float) -> dict:
        """Bakgrunns-inngangene mu(k,z)-modulen trenger, ved roedforskyvning z.

        Enheter: loeserens egne (H0 = M_Pl = 1) — phi_dot_bar og
        lambda_dot_bar er per tau = H0 t. Enhetsbyttet til mu_kz' naturlige
        enheter er kallerens ansvar og er ikke gjort her.

        Dette er L-033s formaal: inngangene kommer fra loesningen, ikke
        fra luften. De er fortsatt bare definert der loesningen er det.
        """
        def _ved(arr):
            return float(np.interp(z, self.z, arr))

        gyldig = np.isfinite(self.E)
        nokler = ("phi_bar", "phi_dot_bar", "rho_bar", "lambda_dot_bar")
        if not np.any(gyldig) or z > float(np.nanmax(self.z[gyldig])):
            return {k: float("nan") for k in nokler}
        return {
            "phi_bar": _ved(self.phi),
            "phi_dot_bar": _ved(self.phi_dot),
            "rho_bar": _ved(self.rho_m),
            "lambda_dot_bar": _ved(self.lam_dot),
        }


# ---------------------------------------------------------------------------
# Loeseren
# ---------------------------------------------------------------------------

class EFCBackgroundSolver:
    """Integrerer (12)-(13) + materie-bevaring + responsfeltet (10).

    Tilstand: (a, E, rho_m, phi, phi_dot, lambda, lambda_dot) i
    z = roedforskyvning. E er H/H0 og integreres via
    akselerasjonsligningen (eq. 7, (i,j)-delen); eq. (12) settes som
    startbetingelse og maales langs hele loesningen.
    """

    def __init__(self, params: dict,
                 nonminimal_sign: float = NONMINIMAL_SIGN_DEFAULT,
                 lambda_stress: str = LAMBDA_STRESS_DEFAULT):
        self.params = _normaliser(params)
        if nonminimal_sign not in (NONMINIMAL_SIGN_PAPER,
                                   NONMINIMAL_SIGN_STANDARD):
            raise ValueError(
                "nonminimal_sign maa vaere NONMINIMAL_SIGN_PAPER eller "
                "NONMINIMAL_SIGN_STANDARD")
        if lambda_stress not in LAMBDA_STRESS_FORMS:
            raise ValueError(
                f"lambda_stress maa vaere en av {LAMBDA_STRESS_FORMS}")
        self.nonminimal_sign = float(nonminimal_sign)
        self.lambda_stress = str(lambda_stress)
        self._V0 = _V0_fra_lukning(self.params, self.nonminimal_sign,
                                   self.lambda_stress)

    # -- T^(lambda): energitetthet og trykk (eq. 6 vs eq. 12) --------------

    def _lambda_ledd(self, E, lam, u, w, G):
        """(rho_lambda, p_lambda), begge i enheter av 3 M_Pl^2 H0^2.

        ``rho_lambda`` er leddet som gaar inn i eq. (12); ``p_lambda`` er
        det som gaar inn i (i,j)-ligningen (som trykk). Gamma kommer inn
        via flyt-betingelsen (13), phi_ddot + 3 H phi_dot = Gamma.

        Skillet mellom formene er dokumentert ved LAMBDA_STRESS_FORMS;
        hvilken som lukker systemet er et MAALT spoersmaal
        (constraint-residualen), ikke et valg begrunnet i prosa.
        """
        if self.lambda_stress == "full_eq6":
            return (w * u - 3.0 * E * lam * u, w * u + lam * G)
        return (w * u, w * u)

    # -- E fra den modifiserte Friedmann-ligningen (eq. 12) ----------------

    def _E_fra_constraint(self, rho_m, phi, u, w, lam=0.0):
        """Eq. (12) loest for H/H0 — den er kvadratisk naar alpha != 0.

        F E^2 - sigma alpha phi_dot E - X = 0,
        X = rho_m + K phi_dot^2/6 + V0 + rho_lambda/3.
        Den fysiske roten (E > 0) velges. Ingen reell rot -> NaN.
        """
        p, pr = self.params, self.nonminimal_sign
        x = _x_num(rho_m / p["omega_crit"])
        if not np.isfinite(x):
            return np.nan
        F = 1.0 + p["alpha"] * phi
        if F <= 0.0:
            return np.nan
        K = kinetic_stiffness(p["k0"], x)
        G = gamma_of_rho(p["gamma0"], x)
        rho_lam, _ = self._lambda_ledd(1.0, lam, u, w, G)
        X = rho_m + K * u ** 2 / 6.0 + self._V0 + rho_lam / 3.0
        b = pr * p["alpha"] * u
        disk = b ** 2 + 4.0 * F * X
        if disk < 0.0:
            return np.nan
        return (b + np.sqrt(disk)) / (2.0 * F)

    # -- integrasjonen ----------------------------------------------------

    def _dy_dz(self, z, y):
        """Hoyresiden. y = (a, E, rho_m, phi, u, lam, w), ' = d/dtau."""
        p, pr = self.params, self.nonminimal_sign
        # (i,j)-leddet er ikke-minimalt-leddet i eq. (7), som papiret
        # skriver med MINUS — motsatt av plusset i eq. (12). De to er
        # konsistente med hverandre: sigma' = -sigma.
        sign7 = -pr
        a, E, rho_m, phi, u, lam, w = y
        x = _x_num(rho_m / p["omega_crit"])
        F = 1.0 + p["alpha"] * phi
        if F <= 0.0 or E <= 0.0:
            raise RuntimeError("feltene forlot sitt gyldighetsomraade")
        K = kinetic_stiffness(p["k0"], x)
        G = gamma_of_rho(p["gamma0"], x)
        _, p_lam = self._lambda_ledd(E, lam, u, w, G)

        # (i,j): -F(2E' + 3E^2) = K u^2/2 - 3 V0 + 3 p_lambda + sign7 alpha Gamma
        D = (-3.0 * F * E ** 2 - K * u ** 2 / 2.0 + 3.0 * self._V0
             - 3.0 * p_lam - sign7 * p["alpha"] * G) / (2.0 * F)

        # (10): lam'' + 3 E lam' = 3 V' - 3 alpha (E' + 2E^2)
        #                          - K Gamma + K' rho' phi'
        dVdphi = 0.0                      # V = const -> V' = 0
        rho_p = -3.0 * E * rho_m          # d rho_m/d tau
        Kprime_term = (p["k0"] * rho_p * u
                       / (p["omega_crit"] * (1.0 - x) ** 2))
        rhs_lam = (3.0 * dVdphi - 3.0 * p["alpha"] * (D + 2.0 * E ** 2)
                   - K * G + Kprime_term)

        dz = 1.0 / ((1.0 + z) * E)
        return np.array([
            -E * a * dz,                   # da/dtau = E a
            -D * dz,                       # dE/dtau = D  (eq. 7, (i,j))
            3.0 * E * rho_m * dz,          # d rho_m/dtau = -3 E rho_m
            -u * dz,
            -(G - 3.0 * E * u) * dz,
            -w * dz,
            -(rhs_lam - 3.0 * E * w) * dz,
        ])

    def solve(self, z_max: float = 3.0, n_points: int = 201,
              rtol: float = 1e-10, atol: float = 1e-12
              ) -> BackgroundSolution:
        """Loes bakgrunnen fra z=0 til z_max paa et grid av n_points.

        Stopper aerlig ved rho_m = rho_crit (K divergerer): punktene etter
        krysset er NaN og ``status`` sier hvorfor.
        """
        if z_max <= 0:
            raise ValueError("z_max maa vaere > 0")
        p = self.params
        n_points = max(int(n_points), 2)
        z_grid = np.linspace(0.0, float(z_max), n_points)

        honesty = {
            "status": "first_self_consistent_background",
            "boltzmann_cmb": "open — ingen Boltzmann/CMB-implementasjon",
            "V_choice_note": (
                "V(phi) er uspesifisert i aksjonspapiret; V = const er "
                "valgt fordi LCDM-grensen krever et Lambda-liknende ledd. "
                f"V0 = {self._V0:.6g} i enheter av 3 M_Pl^2 H0^2"
                + (" (satt av z=0-normaliseringen)" if p["V0"] is None
                   else " (oppgitt av kaller)")),
            "nonminimal_sign": self.nonminimal_sign,
            "nonminimal_sign_note": (
                "papirets eq. 12 skriver +3 M_Pl^2 H F_dot; direkte "
                "variasjon av eq. 1 i papirets egen signatur (eq. 11) gir "
                "-3 M_Pl^2 H F_dot. Begge kan velges eksplisitt. MAALT: "
                "papirets trykte fortegn gir mindre constraint-residual enn "
                "den direkte variasjonen (se diagnostics) — derfor default."),
            "lambda_stress": self.lambda_stress,
            "lambda_stress_note": (
                "T^(lambda) (eq. 6) kan fores inn som papirets eq. 12 "
                "(bare lambda_dot phi_dot) eller i full eq. 6-form; "
                "papirets eget notat i 2.1 sier at formene skiller seg med "
                "randledd. MAALT: ingen av dem lukker eksakt — begge gir en "
                "strukturell residual (~1e-7 for referanseparametrene, "
                "aarsak i diagnostics); full eq. 6-form gir den minste."),
            "units": ("H0 = M_Pl = 1: tid i 1/H0, tetthet i 3 M_Pl^2 H0^2, "
                      "k0 = K0/M_Pl^2, lambda_tilde = lambda/M_Pl^2, "
                      "V0 = V/(3 M_Pl^2 H0^2)"),
            "not_valid_for": [
                "perturbasjoner og CMB (Boltzmann-krever — egen post)",
                "rho_m >= rho_crit (K divergerer, eq. 2)",
                "z der straling betyr noe (Omega_r er ikke med)",
                "super-horisont/ADM-stabilitet (aapent i papiret)",
            ],
        }

        # -- startbetingelse: eq. (12) settes ved z = 0 -------------------
        x0 = p["Omega_m"] / p["omega_crit"]
        F0 = 1.0 + p["alpha"] * p["phi0"]
        E0 = self._E_fra_constraint(p["Omega_m"], p["phi0"],
                                    p["phi_dot0"], p["lam_dot0"],
                                    p["lam0"])
        if not np.isfinite(E0) or x0 >= 1.0 or F0 <= 0.0:
            return self._tomt_grid(z_grid, honesty, status="invalid_state",
                                   z_rho_crit=None)

        y0 = np.array([1.0, E0, p["Omega_m"], p["phi0"], p["phi_dot0"],
                       p["lam0"], p["lam_dot0"]])

        def _rho_crit_event(z, y):
            return p["omega_crit"] - y[2]

        _rho_crit_event.terminal = True
        _rho_crit_event.direction = -1.0

        try:
            res = solve_ivp(self._dy_dz, (0.0, float(z_max)), y0,
                            method="RK45", rtol=rtol, atol=atol,
                            events=[_rho_crit_event], dense_output=True)
        except (RuntimeError, ValueError, FloatingPointError) as exc:
            return self._tomt_grid(z_grid, honesty,
                                   status=f"integration_failed: {exc}",
                                   z_rho_crit=None)

        z_rho_crit = None
        if res.t_events and len(res.t_events[0]) > 0:
            z_rho_crit = float(res.t_events[0][0])
        status = "rho_crit_reached" if z_rho_crit is not None else "ok"
        if not res.success and status == "ok":
            status = f"integration_failed: {res.message}"

        gyldig = z_grid <= (z_rho_crit if z_rho_crit is not None
                            else float(z_max) + 1e-12)
        ut = self._tomt_grid(z_grid, honesty, status=status,
                             z_rho_crit=z_rho_crit)
        if np.any(gyldig):
            Y = res.sol(z_grid[gyldig])
            ut.a[gyldig] = Y[0]
            ut.E[gyldig] = Y[1]
            ut.rho_m[gyldig] = Y[2]
            ut.phi[gyldig] = Y[3]
            ut.phi_dot[gyldig] = Y[4]
            ut.lam[gyldig] = Y[5]
            ut.lam_dot[gyldig] = Y[6]

        ut.diagnostics = self._diagnostikk(ut)
        return ut

    def _tomt_grid(self, z_grid, honesty, status, z_rho_crit
                   ) -> BackgroundSolution:
        nan = np.full_like(z_grid, np.nan, dtype=float)
        return BackgroundSolution(
            z=z_grid.copy(), a=nan.copy(), E=nan.copy(), rho_m=nan.copy(),
            phi=nan.copy(), phi_dot=nan.copy(), lam=nan.copy(),
            lam_dot=nan.copy(), status=status, z_rho_crit=z_rho_crit,
            diagnostics={}, honesty=honesty, params=dict(self.params),
            nonminimal_sign=self.nonminimal_sign)

    # -- maalingene -------------------------------------------------------

    def _diagnostikk(self, sol: BackgroundSolution) -> dict:
        """Residualer langs loesningen — den maalte dommen over loesningen."""
        p = self.params
        ok = np.isfinite(sol.E)
        d = {
            "constraint_residual_definition": KONSTRAINT_RESIDUAL_DEF,
            "constraint_residual_cause": (
                "MAALT: residualen er strukturell (uendret fra rtol 1e-8 til "
                "1e-11) og skalerer som K'(rho) = k0/(omega_crit(1-x)^2) — "
                "dvs. som papirets egen neglisjering av delta K/delta g^mu_nu "
                "(seksjon 2.1, 'Note on delta K'): den vokser med k0, med "
                "phi_dot^2 og som 1/omega_crit, og er null naar phi_dot = 0. "
                "Se testen test_constraint_residualen_skalerer_som_K_prime."),
            "h_consistency_definition": (
                "max |E_integert - E_fra_eq12| / E: (12) loest for E paa "
                "hver tilstand i loesningen og sammenlignet med den "
                "integrerte E."),
            "rho_crit_reached": sol.status == "rho_crit_reached",
            "z_rho_crit": sol.z_rho_crit,
        }
        if not np.any(ok):
            d.update({"constraint_residual_max": np.nan,
                      "h_consistency_max_rel": np.nan,
                      "lcdm_max_rel_error": None})
            return d

        rho, phi, u, w = (sol.rho_m[ok], sol.phi[ok],
                          sol.phi_dot[ok], sol.lam_dot[ok])
        lam = sol.lam[ok]
        E = sol.E[ok]
        x = rho / p["omega_crit"]
        F = 1.0 + p["alpha"] * phi
        K = np.where(x < 1.0, p["k0"] / (1.0 - x), np.inf)
        G = gamma_of_rho(p["gamma0"], x)
        rho_lam = (w * u - 3.0 * E * lam * u
                   if self.lambda_stress == "full_eq6" else w * u)
        rhs = (rho + K * u ** 2 / 6.0 + self._V0 + rho_lam / 3.0
               + self.nonminimal_sign * E * p["alpha"] * u)
        d["constraint_residual_max"] = float(
            np.max(np.abs(F * E ** 2 - rhs) / E ** 2))
        E_c = np.array([self._E_fra_constraint(r, f, uu, ww, ll)
                        for r, f, uu, ww, ll in zip(rho, phi, u, w, lam)])
        d["h_consistency_max_rel"] = float(
            np.max(np.abs(E - E_c) / E))
        d["rho_crit_rho"] = float(np.nanmax(sol.rho_m))
        d["rho_over_crit_max"] = float(np.nanmax(x))

        # LCDM-grensen maales bare der den faktisk er grensen.
        p_er_grense = (p["alpha"] == 0.0 and p["gamma0"] == 0.0
                       and p["phi_dot0"] == 0.0 and p["lam_dot0"] == 0.0)
        if p_er_grense:
            z = sol.z[ok]
            E_lcdm = np.sqrt(p["Omega_m"] * (1.0 + z) ** 3 + self._V0)
            d["lcdm_max_rel_error"] = float(np.max(np.abs(E / E_lcdm - 1.0)))
        else:
            d["lcdm_max_rel_error"] = None
        return d


# ---------------------------------------------------------------------------
# Motorflaten (samme moenster som mu_kz og hubble)
# ---------------------------------------------------------------------------

class EFCBackgroundEngine(EFCEngine):
    """H(z) fra den selvkonsistente EFC-bakgrunnen (eq. 12-13).

    Enhetene er loeserens (H0 = M_Pl = 1); ``H0`` i params brukes bare
    som enhetsomregning ut til km/s/Mpc.
    """

    REQUIRED_PARAMS = ["H0", "alpha", "k0", "omega_crit", "gamma0", "Omega_m"]

    #: Motoren eier sin egen publiseringsflate (se base_engine). Noden ER i
    #: atlaset (``efc.efc_background_engine``) og genereres til GitHub Pages —
    #: «intern» var sann mens noden ikke fantes, og ble staende etter at den
    #: kom inn. Rettet mot maalt tilstand 2026-09-18 (bro-auditen).
    SYNLIGHET = "offentlig"

    @property
    def name(self) -> str:
        return "efc_background"

    def compute(self, params_dict: dict, coordinates: np.ndarray) -> np.ndarray:
        """H(z) = H0 * E(z) i km/s/Mpc naar H0 er gitt i km/s/Mpc."""
        if not self.validate_params(params_dict):
            return np.full_like(np.asarray(coordinates, dtype=float), np.nan)
        z = np.asarray(coordinates, dtype=float)
        solver = EFCBackgroundSolver(
            params_dict, nonminimal_sign=params_dict.get(
                "nonminimal_sign", NONMINIMAL_SIGN_DEFAULT))
        sol = solver.solve(z_max=float(np.max(z)), n_points=2001)
        ok = np.isfinite(sol.E)
        if not np.any(ok):
            return np.full_like(z, np.nan)
        E = np.interp(z, sol.z[ok], sol.E[ok], left=np.nan, right=np.nan)
        E = np.where(z <= np.nanmax(sol.z[ok]) + 1e-12, E, np.nan)
        return params_dict["H0"] * E

    # ------------------------------------------------------------------
    # regime_node(): motorens selvbeskrivelse i atlaset
    # ------------------------------------------------------------------
    def regime_node(self, params_dict: dict) -> dict:
        p = _normaliser(params_dict)
        sign = float(params_dict.get("nonminimal_sign",
                                     NONMINIMAL_SIGN_DEFAULT))
        V0 = _V0_fra_lukning(p, sign)
        validity = (
            f"Bakgrunnsloeser for FLAT FRW med EFC-aksjonen (eq. 1): "
            f"alpha={p['alpha']}, k0={p['k0']}, "
            f"omega_crit={p['omega_crit']}, gamma0={p['gamma0']}, "
            f"Omega_m={p['Omega_m']}, V0={V0:.4g}, "
            f"nonminimal_sign={sign:+.0f}. Dette er den FOERSTE "
            f"selvkonsistente EFC-bakgrunnen: phi drives av "
            f"flyt-betingelsen (13), H av (12) og lambda er et "
            f"responsfelt (eq. 10). Boltzmann/CMB er AAPEN — "
            f"ingen perturbasjoner, ingen EFCLASS. Gyldig bare for "
            f"rho_m < rho_crit (K divergerer, eq. 2), for z der "
            f"stråling er neglisjerbar, og med V = const valgt fordi "
            f"papiret ikke spesifiserer V(phi). Super-horisont og "
            f"ADM-stabilitet er aapent i papiret."
        )
        law_form = (
            "3 M_Pl^2 F(phi) H^2 = rho_m + K phi_dot^2/2 + V(phi) "
            "+ sigma 3 M_Pl^2 H F_dot + lambda_dot phi_dot (eq. 12); "
            "phi_ddot + 3 H phi_dot = Gamma(rho) (eq. 13); "
            "F = 1 + alpha phi; K = k0/(1 - rho/rho_crit) (eq. 2); "
            "Gamma per eq. 47 — sigma = +1 er papirets trykte form, "
            "-1 er den direkte variasjonen av eq. 1."
        )
        return {
            "id": "efc.efc_background_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {
                "stipulert_av_oss": True,
                "terskler": [
                    "rho >= rho_crit -> K divergerer — modellen er ikke "
                    "definert utenfor (eq. 2), loeseren stopper der",
                    "V = const — vaart valg, ikke papirets (V(phi) er "
                    "uspesifisert i kilden)",
                    f"nonminimal_sign = {sign:+.0f} — valgt eksplisitt, "
                    "forskjellen er maalt",
                ],
                "motor": "efc_background"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                # Evidensstatus eies av ATLASET: bakgrunnsloeseren er en
                # hypotese uten maalt evidens (SYSTEM.md: «no evidence yet»).
                # Motoren sa «proxy» om en avledning som ikke er maalt.
                "evidensstatus": "ingen",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "The self-consistent EFC background exists only in our own paper (DOI 31876324); no external group solves these equations, so nobody would discover a correlated error in them.",
                "konsensus_er_ikke_sannhet": True,
            },
            "maale_paradigme": {
                "koordinater": ["rom", "tid", "masse"],
                "enheter": "dimensjonsloes (H0 = M_Pl = 1); E = H/H0 ut",
                "status": "avledet",
                "alternativer": ["koordinatfrie formuleringer",
                                 "anderledes normalisering av a(t)"],
            },
            # Plataseringen eies av ATLASET (scripts/maintenance/efc_bro_konvensjon.py):
            # motoren er SUBSTRATET under de andre kosmologimotorene, og
            # nivaaet staar i atlaset — ikke i en egen kopi her.
            "nivaa": {
                "indeks": 0,
                "forelder": None,
                "tidsskala": "kosmisk tid",
                "lengdeskala": "Hubbleskala",
            },
            "regime": {
                "name": "Selvkonsistent EFC-bakgrunn (FLAT FRW)",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "H(z) og bakgrunns-feltene phi, phi_dot, "
                          "rho_m, lambda_dot",
                "measurer": "numerisk integrasjon av (12)-(13) + eq. 10",
                "instrument": "EFCBackgroundSolver "
                              "(efc_inference/engine/efc_background.py)",
                "proxy_chain": [
                    "parametre (alpha, k0, omega_crit, gamma0, V0) -> "
                    "ODE-system",
                    "ODE-system -> tilstand (a, E, rho_m, phi, phi_dot, "
                    "lambda, lambda_dot)",
                    "tilstand -> mu_kz_inputs -> mu(k,z) (kandidat-kobling)",
                ],
                "placement": "loesningen finnes paa et z-grid fra 0 til "
                             "z_max, og stopper ved rho_crit",
                "compression": "bakgrunn -> syv tilstandsvariabler + "
                               "maalt constraint-residual",
            },
            "episenter": "flyt-betingelsen (13) er det som gjor dette til "
                         "en EFC-bakgrunn og ikke en vilkaarlig "
                         "scalar-tensor: phi har ingen fri "
                         "startbevegelse uten Gamma, og lambda betaler "
                         "for ledgerskapet",
            "buffer": {
                "role": "lambda er bufferen: responsfeltet som holder "
                        "flyt-regnskapet naar phi ikke kan bevege seg fritt",
                "note": "loeseren deklarerer hva den ikke er (Boltzmann, "
                        "stråling, super-horisont) i stedet for aa la "
                        "E(z) se ut som en full loesning.",
            },
            "ontology": {
                "assumes": [
                    "aksjonen (eq. 1) og bakgrunnsligningene (12)-(13) er "
                    "korrekt utledet i papiret",
                    "V(phi) = const — vaart valg, fordi papiret ikke "
                    "spesifiserer potensialet og LCDM-grensen krever et "
                    "Lambda-liknende ledd",
                    "materie er stov som bevares separat (rho ~ a^-3)",
                ],
                "source": "DOI 10.6084/m9.figshare.31876324 (Magnusson, "
                          "2025/2026)",
            },
            "observer": {
                "bandwidth": "loeseren ser bakgrunnen — ingen "
                             "perturbasjoner, ingen CMB",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "rho_m -> Gamma -> phi-dynamikk -> K phi_dot^2 og "
                        "H F_dot -> H -> rho_m",
                "properties": ["H(z)", "phi(z)", "lambda(z)"],
            },
            "fractal": {
                "pattern": "samme bakgrunnsligning holdes langs hele "
                           "z-aksen — loesningen er en instans av (12)",
                "note": "en lov, alle z.",
            },
            "coupling": {
                "local": "hvert z-punkt er en tilstand paa loesningen",
                "global": "mater mu(k,z)-modulen med bakgrunns-inngangene "
                          "— COUPLED_TO efc.mu_kz_engine (kandidat: "
                          "injeksjonen i growth er ikke implementert)",
                "empathy_note": "bakgrunnen vet hva den ikke er: den er "
                                "ingen Boltzmann-kode.",
            },
        }
