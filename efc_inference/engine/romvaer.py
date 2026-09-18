"""EFC Romvær Engine — magnetosfærens Kp-buffer (L-038).

Kp-indeksen (0-9) er magnetosfærens utladningsnivå: solvinden lader
bufferen (sørvendt Bz er ladestrømmen — magnetisk gjenkobling åpner
porten), og bufferen utlades i geomagnetiske stormer over noen døgn.

Dette er en KORRELASJONSMODELL (solvind -> Kp), ikke fysikk fra
bunnen — geomagnetisk stormfysikk er et eget fag. Den virkelige
solvind-Kp-koblingen er betydelig mer kompleks enn den lineære
formen her (se f.eks. Newell-koblingen og andre fluks-koblinger);
den lineære lade-formen er en IDEALISERT forenkling, kalibrert så
Bz=-12/v=600 gir Kp~5. EFC-bidraget er formens kobling: solens
flares (SolarFlareEngine) lader jordas buffer (denne motoren) — to
domener, én kjede (samme kilde, SWPC).

Idealisert lade-/utladningsmodell:
    lading:  Kp_opp ~ koeffisient * (-Bz_sør/10) * (v/100)
    utlading: Kp(t+1) = Kp(t) - utladningsrate per 3t-tikk
Stormnivåene (NOAA-skalaen): Kp 5 = G1, 6 = G2, 7 = G3, 8 = G4,
9 = G5.
"""
from __future__ import annotations

import numpy as np

from .base_engine import EFCEngine


class RomvaerEngine(EFCEngine):
    """Kp-buffermotor for magnetosfæren (korrelasjonsmodell, idealisert)."""

    REQUIRED_PARAMS = [
        "lade_koeffisient",  # Kp per (nT/10 * 100 km/s) — kalibreringsproxy
        "utladningsrate",    # Kp per 3t-tikk — bufferens utladning
        "storm_terskel",     # Kp — G1-stormgrensen (5)
    ]

    @property
    def name(self) -> str:
        return "romvaer"

    # ------------------------------------------------------------------
    # Fysikk
    # ------------------------------------------------------------------

    def forventet_kp(self, params: dict, bz: float,
                     hastighet: float) -> float:
        """Ladestrømmen: sørvendt Bz (negativ) lader; nordvendt
        skjermer. Kp ~ koeffisient * (-Bz/10) * (v/100) for Bz < 0."""
        if bz >= 0:
            ladning = 0.0
        else:
            ladning = (params["lade_koeffisient"]
                       * (-bz / 10.0) * (hastighet / 100.0))
        # Tak ved 9 — skalaens maksimum
        return float(min(9.0, ladning))

    def utlad(self, kp: float, params: dict, tikk: int = 1) -> float:
        """Bufferen utlades: Kp faller med utladningsraten per tikk."""
        return float(max(0.0, kp - params["utladningsrate"] * tikk))

    def storm_niva(self, params: dict, kp: float) -> str:
        """NOAA G-skalaen: Kp 5=G1, 6=G2, 7=G3, 8=G4, 9=G5."""
        if kp < params["storm_terskel"]:
            return "ingen"
        niva = {5: "G1", 6: "G2", 7: "G3", 8: "G4", 9: "G5"}
        return niva.get(int(np.floor(kp)), "G5")

    # ------------------------------------------------------------------
    # EFCEngine-kontrakten
    # ------------------------------------------------------------------

    def compute(self, params_dict: dict,
                coordinates: np.ndarray) -> np.ndarray:
        """Gitt (Bz, hastighet)-par (N x 2), returner forventet Kp."""
        koord = np.asarray(coordinates, dtype=float)
        if koord.ndim == 1:
            koord = koord.reshape(1, -1)
        return np.array([
            self.forventet_kp(params_dict, float(rad[0]), float(rad[1]))
            for rad in koord
        ])

    # ------------------------------------------------------------------
    # Selvbeskrivelse
    # ------------------------------------------------------------------

    def regime_node(self, params: dict) -> dict:
        validity = (
            "Kp-bufferregime: solvinden lader magnetosfæren (sørvendt "
            "Bz = ladestrøm), bufferen utlades i stormer over noen "
            "døgn. KORRELASJONSMODELL (solvind -> Kp) — IKKE fysikk "
            "fra bunnen; den virkelige koblingen er mer kompleks "
            "(Newell-koblingen m.fl.) og den lineære lade-formen er "
            "en IDEALISERT forenkling. NOAA G-skalaen (Kp 5=G1 ... "
            "9=G5). EFC-bidraget er formens kjede: solens flares "
            "lader jordas buffer."
        )
        law_form = ("lading: Kp ~ koeffisient * (-Bz_sør/10) * (v/100) "
                    "for Bz < 0; utlading: Kp(t+1) = Kp(t) - rate per "
                    "3t-tikk; G-nivåer ved Kp 5-9")
        return {
            "id": "efc.romvaer_engine",
            "synlighet": self.SYNLIGHET,
            "perspektiv": "paradigme",
            "stipulasjoner": {"stipulert_av_oss": True,
            "terskler": ["NOAA G-skala: 5=G1 ... 9=G5 — varslingsskala", "Bz=-12/v=600 -> Kp 5.04 — lineaer korrelasjon — Newell-caveat: virkelig kobling mer kompleks"],
            "motor": "romvaer"},
            "epistemikk": {
                "sannhetsstatus": "hypotese",
                "evidensstatus": "proxy",
                "konsensusstatus": "minoritet",
                "sosial_mekanisme": "vår egen ramme — bæres av oss, ikke av feltet; narrativet er vårt eget, og det er en styrke å vite det",
                "konsensus_er_ikke_sannhet": True
            },
            "maale_paradigme": {
                "koordinater": ["magnetfelt", "tid", "hastighet"],
                "enheter": "motorspesifikke (SI)",
                "status": "avledet",
                "alternativer": ["koordinatfrie formuleringer"]
            },
            # Plataseringen eies av ATLASET (scripts/maintenance/efc_bro_konvensjon.py):
            # motoren kan ikke vite hvor i stigen dens node hoerer. Feltet maa
            # likevel staa her fordi RegimeNode krever det — testen binder dem.
            "nivaa": {
                "indeks": 1,
                "forelder": None,
                "tidsskala": "motortid",
                "lengdeskala": "domene"
            },            "regime": {
                "name": "Magnetosfærens Kp-buffer",
                "validity": validity,
                "law_form": law_form,
            },
            "phase": "computation_engine",
            "measure": {
                "target": "forventet Kp, stormnivå, utladningsbane",
                "measurer": "korrelasjonsmodell solvind -> Kp",
                "instrument": "RomvaerEngine (efc_inference/engine/romvaer.py)",
                "proxy_chain": [
                    "Bz, v -> ladestrøm (korrelasjonsproxy)",
                    "Kp -> G-nivå (NOAA-skalaen)",
                ],
                "placement": "magnetosfærens buffer — ett (Bz, v)-punkt om gangen",
                "compression": "solvind-tilstand -> (Kp, G-nivå)",
            },
            "episenter": "stormterskelen Kp=5: punktet der bufferen går fra holding til release — magnetosfærens regimeskifte",
            "buffer": {
                "role": "magnetosfæren er bufferen: den holder ladningen fra solvinden til stormen utløses",
                "note": "ANALOGI til solens magnetiske buffer (SolarFlareEngine) — ikke identitet: jordas buffer utlades gradvis, solens utløses brått.",
            },
            "ontology": {
                "assumes": [
                    "korrelasjonen Bz/v -> Kp er stabil i den idealiserte formen",
                    "G-skalaen (NOAA) er den riktige storm-klassifiseringen",
                ],
                "source": "romvær-korrelasjoner (etablert praksis); NOAA G-skalaen; analogi-merkingen er atlasets egen",
            },
            "observer": {
                "bandwidth": "motoren ser bare (Bz, v) — ingen magnetopause-dynamikk, ingen ringstrøm",
                "awareness": "instrument_window",
                "er_del_av_systemet": True,
            },
            "emergence": {
                "loop": "solvind lader -> terskel -> storm utlader -> rolig — magnetosfærens loop",
                "properties": ["Kp", "G-nivå", "utladningsbane"],
            },
            "fractal": {
                "pattern": "lade/utlad-buffer med terskel: magnetosfære, solens flares, batteriet (analogi)",
                "note": "ett mønster, tre domener.",
            },
            "coupling": {
                "local": "én solvind-tilstand, ett Kp",
                "global": "solens utløsninger lader jordas buffer — COUPLED_TO efc.solar_flare_engine via SWPC-kjeden",
                "empathy_note": "jorda holder solens vrede i sitt magnetiske favn — til den slipper.",
            },
        }
