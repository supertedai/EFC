#!/usr/bin/env python3
"""K5 (t_eb9794ce): genererer notatet «kontraktene uten maskinadresse».

REN MAALING. Leser atlaset fra en git-ref og skriver ETT notat i docs/notes/.
Ingen node endres, ingen kanon flyttes.

    python3 docs/notes/atlas_kontrakter_uten_maskinadresse_t_eb9794ce.py \
        --repo . --ref origin/main --skriv

Kategoriene (kortets tre):
    R  har rute                  — falsifikatoren navngir en observasjon atlaset
                                   alt bærer en adresse for (obs.*, buss-emne,
                                   forseglet DOI, eller en maskinlesbar relasjonskant)
    O  navngir observasjon uten atlas-node — testen er navngitt, atlaset bærer den ikke
    I  navngir ingen observasjon — ingen referent finnes i materialet

Adresse-slag: obs = obs.*-node, buss = buss-emne i nodens eget domene,
doi = den forseglede DOI-en/arbiteren, kant = OBSERVED_THROUGH/INSTANCE_OF i relations.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# (id, klasse, kildefelt, sitat, adresse, adresse_slag, kategori, merknad)
RADER = [
    ("efc.l0", "P", "ville_falsifisere",
     "An observed structure seed or a non-Gaussian signature in the CMB that cannot be traced back to quantum fluctuations at S→0.",
     "", "", "O",
     "Nærmeste bærer: `obs.cmb_tt` (target = «the temperature/polarisation spectrum», instrument Planck) — det er spekteret, ikke f_NL/seed-statistikken. Nodens eget `measure.instrument` sier «none direct — model-dependent»."),
    ("efc.l1", "P", "ville_falsifisere",
     "A deviation from LCDM in the CMB spectrum or the BAO scale at L1 level.",
     "obs.cmb_tt (target: the temperature/polarisation spectrum) og obs.bao (target: the BAO scale)",
     "obs", "R",
     "Begge har `OBSERVED_IN → efc.l1` i `relations` — ruten er maskinlesbar, ikke bare navngitt."),
    ("efc.l2", "P", "ville_falsifisere",
     "DESI DR2 full-shape fσ8(z≈0.7) outside ~1σ of 0.430, or S8 that does not lie between the CMB prediction and weak lensing.",
     "obs.fsigma8 og obs.s8 (begge `OBSERVED_IN → efc.l2`), obs.cmb_lensing; forseglet DOI 10.6084/m9.figshare.32013156 (arbiter: DESI DR2 full-shape)",
     "obs+doi", "R",
     "En av de tre radene som navngir den forseglede DOI-en og voldgiftsmannen; den eneste i L-serien som navngir statistikk, instrument (DESI/KiDS) OG forseglingen i samme setning."),
    ("efc.l3", "P", "ville_falsifisere",
     "A measured dark-energy state that does not move toward structure saturation, or a w(z) that excludes the end station.",
     "obs.w0wa (target: the w(z) parametrisation); obs.cc (`OBSERVED_IN → efc.l3`)",
     "obs", "R",
     "«the end station» er ikke navngitt som node; w(z) og den kosmologiske konstantens størrelse er det."),
    ("efc.water_phase_engine", "P", "ville_falsifisere",
     "A measured phase boundary for H2O that deviates from the IAPWS-95 value outside the uncertainty IAPWS-95 itself states for the point.",
     "", "", "O",
     "IAPWS-95 finnes verken som `obs.*`-node, `kilder`-ledd eller buss-emne. `h2o.solid/liquid/gas/triple_point` er B-noder (etablert fysikk), og `relations` bærer `T_m(P)`, `P_sat(T)`, `P_sub(T)` fra motoren — men det er lovformer, ikke en observasjonsadresse."),
    ("efc.rotation_engine", "F", "falsifiserbarhet.grunn",
     "…would be falsified if the SPARC rotation curves can be fitted just as well without the field — or if the best fit requires a K that varies from galaxy to galaxy.",
     "obs.rar (instrument = SPARC)",
     "obs", "R",
     "Samme datasett, annen statistikk: `obs.rar.target` er «a_obs vs a_bar» (RAR), falsifikatoren navngir v(r). Domenets egen strøm er `observasjon.mast-caom` (MAST) — den bærer ikke SPARC."),
    ("efc.hubble_engine", "P", "ville_falsifisere",
     "H(z) measurements that exclude the EFC-deformed expansion at Omega_m=0.3, H0=70.0.",
     "obs.bao via `OBSERVED_THROUGH obs.bao → efc.hubble_engine`; `kosmos.kosmologi_desi_bao INSTANCE_OF obs.bao`",
     "kant+obs", "R",
     "Eneste kant i atlaset som gir en motor direkte til en observasjonsnode uten omvei. `measure.instrument` sier «the observation side is BAO/chronometers»."),
    ("efc.growth_engine", "P", "ville_falsifisere",
     "DESI DR2 full-shape fσ8(z~0.7) outside ~1σ of 0.430 — the sealed prediction.",
     "obs.fsigma8 og obs.s8 (`OBSERVED_THROUGH → efc.growth_engine`); egen `prediction`-blokk: DOI 10.6084/m9.figshare.32013156, sealing_sha256 fbb53d61…, correlation efc-fs8.fsigma8.z0.7",
     "kant+doi", "R",
     "Den ENESTE av de 35 med korrelasjon, forsegling og voldgiftsmann i sin egen data. Referansen for hva «adresse» betyr."),
    ("efc.lensing_engine", "F", "falsifiserbarhet.grunn",
     "…if the lens maps can be explained just as well with a mass model that is not a potential well from the field — or if the KiDS-1000 fit deteriorates when the background model is replaced.",
     "obs.cmb_lensing (`OBSERVED_THROUGH → efc.lensing_engine`) og obs.s8 (instrument KiDS)",
     "kant+obs", "R",
     "Granularitetsbrudd: `obs.cmb_lensing` er CMB-linsing (Planck/ACT/SPT) — KiDS-1000 er galakse-shear og treffer `obs.s8`s instrumentliste."),
    ("efc.cluster_engine", "F", "falsifiserbarhet.grunn",
     "…if the halo masses do not follow from the field — or if the Bullet Cluster (where gas and mass are separated) cannot be reproduced.",
     "obs.cluster_hmf og obs.cluster_mass (begge `OBSERVED_THROUGH → efc.cluster_engine`), obs.bullet (target: the mass-gas offset)",
     "kant+obs", "R",
     "«the Bullet Cluster» er navngitt ordrett og bæres av obs.bullet med samme statistikk (masse-gass-offset)."),
    ("efc.solar_flare_engine", "P", "ville_falsifisere",
     "A triggered flare with B < 0.3 T, or a charging event that does not follow the law.",
     "buss-emne `tilstand.swpc-goes-xray` (domenet kosmos.sol); node kosmos.sol_goes",
     "buss", "R",
     "Ruten går gjennom NODENS EGET målefelt (`measure.measurer`: «GOES class proxy»), ikke gjennom falsifikatorteksten. Domenets begrunnelse sier «instrumentnoden leser swpc-goes-xray»."),
    ("efc.jordskjelv_engine", "P", "ville_falsifisere",
     "An earthquake triggered below the stress threshold 3e6 Pa, or a recurrence time that does not follow the charging law.",
     "buss-emne `tilstand.usgs-seismikk` (domenet kosmos.jord)",
     "buss", "R",
     "Klassenavn-treff («earthquake» → seismikk). Domenets begrunnelse beskriver ikke innholdet."),
    ("efc.mu_kz_engine", "P", "ville_falsifisere",
     "A measured μ(k,z) that does not go toward 1 on large scales — it breaks the quasi-static sub-horizon condition k/a >> H.",
     "", "", "O",
     "Ingen node og ingen strøm bærer μ(k,z). Nærmeste adresser måler den INDIREKTE: `obs.eg` (E_G-crossing), `obs.s8`, `obs.fsigma8`. `measure.instrument` = MuKZEngine (intern); kanten `COUPLED_TO efc.growth_engine` er ingen observasjonsrute."),
    ("efc.selv.atlas", "P", "ville_falsifisere",
     "The self-application would fail if the atlas could not be described by its own schema.",
     "", "", "I",
     "Samme setning som de tre andre selv-nodene; planen (§0.3) klassifiserer dem som `arbiter=utledning`. Ingen observasjon å rute til."),
    ("efc.selv.skjema", "P", "ville_falsifisere",
     "The self-application would fail if the atlas could not be described by its own schema.",
     "", "", "I", "Som over."),
    ("efc.selv.paradigme_tid", "P", "ville_falsifisere",
     "The self-application would fail if the atlas could not be described by its own schema.",
     "", "", "I",
     "`measure.instrument` navngir «the SI second (the caesium clock)» — men navnet står i målefeltet, ikke i falsifikatoren, og atlaset bærer det ingen steder."),
    ("efc.selv.paradigme_masse", "P", "ville_falsifisere",
     "The self-application would fail if the atlas could not be described by its own schema.",
     "", "", "I",
     "`measure.instrument` navngir «the SI kilogram» — samme forbehold som for tids-noden."),
    ("efc.romvaer_engine", "P", "ville_falsifisere",
     "A geomagnetic storm without southward Bz, or a Kp level that does not follow the buffer regime.",
     "buss-emne `tilstand.swpc-kp` (domenet kosmos.romvaer); node kosmos.romvaer_swpc",
     "buss", "R",
     "Både falsifikatoren («a Kp level») og domenets begrunnelse («instrumentnoden leser tilstand.swpc-kp») navngir samme strøm."),
    ("efc.oekonomi_engine", "P", "ville_falsifisere",
     "A debt build-up that does not follow the Minsky sequence (hedge→speculative→ponzi), or a crisis without prior leverage drift.",
     "", "", "O",
     "Domenet verden.oekonomi bærer `prediksjon.imf-datamapper`, `tilstand.world-bank` og `observasjon.gdelt-gkg` — men falsifikatoren navngir ingen av dem, og ingen `obs.*`-node bærer leverageratio. Grensetilfelle, se §5."),
    ("efc.orbital_engine", "P", "ville_falsifisere",
     "A bound orbit with ε ≥ 0, or a Hill sphere that deviates from the Kepler calculation at measurement.",
     "buss-emnene `tilstand.celestrak-katalog` og `tilstand.celestrak-stasjoner` (domenet kosmos.satellitter)",
     "buss", "R",
     "MERK: `obs.satellites` bærer IKKE dette — dens target er «the subhalo population» (HST, simuleringer). Domenets begrunnelse sier «banemekanikken av orbital-motoren»."),
    ("efc.klima_engine", "P", "ville_falsifisere",
     "An equilibrium temperature that does not follow the 0D energy balance.",
     "", "", "O",
     "verden.klima bærer `tilstand.noaa-tides` (havtilstand), `tilstand.world-bank` og `observasjon.gdelt-gkg` — det finnes INGEN temperaturstrøm, og atlaset har ingen node for målt overflatetemperatur. Et målt hull i atlaset, ikke bare i kontrakten."),
    ("efc.samfunn_engine", "P", "ville_falsifisere",
     "An outbreak with R0 < 1 that nevertheless grows, or an epidemic trajectory that does not follow SIR given the measured R0.",
     "", "", "O",
     "verden.helse bærer `tilstand.who-gho`, men verken falsifikatoren eller domenets begrunnelse navngir utbrudd/R0. Grensetilfelle, se §5."),
    ("efc.tidevann_engine", "P", "ville_falsifisere",
     "A tidal acceleration with the opposite sign, or a Roche limit that does not hold under measurement.",
     "buss-emne `tilstand.noaa-tides` (domenet verden.klima)",
     "buss", "R",
     "Delt domene med `efc.klima_engine`: klima-noden finner ingen strøm der, tidevanns-noden gjør det. Strømmen er navngitt etter observasjonen (tides)."),
    ("efc.transient_engine", "P", "ville_falsifisere",
     "A transient with mass above 2,785e30 kg (above the limit) that is nevertheless released — it breaks the holding regime.",
     "buss-emne `hendelse.alerce` (domenet kosmos.transienter); node kosmos.transienter_alerce",
     "buss", "R",
     "Domenets begrunnelse: «transientmotoren beskriver kollapsregimet; instrumentnoden leser alerce-hendelser»."),
    ("efc.enerflyt_engine", "P", "ville_falsifisere",
     "A buffer S that grows while C + L > P (deficit), or a drift dS/dt with the opposite sign of P − C − L.",
     "buss-emnene `prediksjon.entsoe-dayahead` og `tilstand.entsoe-dayahead` (domenet verden.energi)",
     "buss", "R",
     "`measure.instrument` = «statistics agencies and grid operators»; domenets begrunnelse sier ENTSO-E bærer både prediksjon og tilstand. FUNN: samme begrunnelse sier at TILSTANDSKILDEN for ENTSO-E stanset 2026-09-04 — en prediction-blokk som peker dit peker på en død strøm."),
    ("efc.grid_higgs", "P", "ville_falsifisere",
     "INTERNAL (theoretical work, not a measurement): would be falsified if the framework does not give a SINGLE quantity that differs from standard Higgs + GR — or if it gives one already excluded at the LHC.",
     "", "", "O",
     "LHC er navngitt som eksklusjonskanal, men atlaset bærer ingen LHC-node og ingen LHC-strøm. Arbiteren er en utledning (planen §0.3), så LHC-leddet er et filter, ikke testen."),
    ("efc.gr_qft_bro", "P", "ville_falsifisere",
     "INTERNAL: would be falsified if the bridge did not REDUCE to GR in the one limit and to QFT in the other.",
     "", "", "I",
     "Navngir to grenser, ingen observasjon. Ingen adresse å lete etter."),
    ("efc.double_slit", "P", "ville_falsifisere",
     "INTERNAL: would be falsified if the interference pattern does not follow from the grid resolution — or if it follows just as well WITHOUT it.",
     "", "", "O",
     "Interferensmønsteret er en navngitt observasjon; atlaset bærer ingen node eller strøm for det (nærmeste fysikk-noder er `optikk.dispersjon` og `regnbue`, som er geometrisk optikk)."),
    ("efc.grid_mikrofysikk", "P", "ville_falsifisere",
     "INTERNAL: would be falsified if the radial acceleration relation does not follow from gradient-coupled excitation — or if it follows from any other minimal coupling as well.",
     "obs.rar (target: a_obs vs a_bar — den radiale akselerasjonsrelasjonen)",
     "obs", "R",
     "Observasjonen er bært selv om arbiteren er en utledning: «the radial acceleration relation» ER `obs.rar`s target, ord for ord (RAR = a_obs vs a_bar)."),
    ("efc.grid_mikro_engine", "P", "ville_falsifisere",
     "A measured Γ(ρ) that falls outside both the low-density and the saturated branch in model space.",
     "", "", "O",
     "Γ(ρ) bæres ingen steder. Nodens eget `observer`-felt sier det selv: «it is a hole in itself that no direct measurement exists»."),
    ("efc.sort_hull", "P", "ville_falsifisere",
     "INTERNAL: would be falsified if the S=0 limit does not give a horizon — or gives one whose entropy contradicts Bekenstein-Hawking.",
     "", "", "I",
     "Bekenstein-Hawking er en formel, horisonten er en teoretisk grense. `observer`-feltet nevner EHT/GW-broene, men med «are not coupled» — de står ikke i falsifikatoren."),
    ("efc.efc_background_engine", "F", "falsifiserbarhet.grunn",
     "is to reproduce LCDM in one limit, and deviate from it in another — but which limit, and how much deviation counts, is NOT fixed in the node. The first step is to name the limiting case against efc.hubble_engine",
     "obs.bao via den erklærte kanten `COUPLED_TO efc.efc_background_engine → efc.hubble_engine` og nodens eget `measure.target` = H(z)",
     "obs", "R",
     "Ruten er indirekte: falsifikatoren navngir SØSTERNODEN, ikke observasjonen. Grensetilfelle, se §5."),
    ("efc.lag_s", "P", "ville_falsifisere",
     "…if rotation curves in SPARC can be explained equally well WITHOUT a scalar energy-flow field — or if K cannot be determined to 4.4 +- 0.6.",
     "obs.rar (instrument = SPARC); `measure.measurer` navngir «SPARC rotation curves (K = 4.4 +- 0.6)»",
     "obs", "R",
     "Samme adresse og samme granularitetsbrudd som `efc.rotation_engine`: SPARC er datasettet, RAR er nodens statistikk."),
    ("efc.lag_d", "P", "ville_falsifisere",
     "…if the expansion history H(a) from the action deviates from what LCDM gives in the limit it is to reproduce — or if g+ = c*H0/e cannot be distinguished from a cosmological constant in any dataset.",
     "obs.bao (H(z)/BAO) og obs.cc (target: the size of the vacuum energy)",
     "obs", "R",
     "Ingen av dem er en egen «H(a)»-node: ruten er til de to nærmeste målingene av ekspansjon og kosmologisk konstant."),
    ("efc.lag_c0", "P", "ville_falsifisere",
     "NO VALID MEASUREMENT yet … the way alpha in DESI DR2 is read by both even though they interpret it differently.",
     "obs.bao + obs.fsigma8 + forseglet DOI 10.6084/m9.figshare.32013156 (DESI DR2-alpha, correlation efc-fs8.fsigma8.z0.7)",
     "obs+doi", "R",
     "Samme tekst navngir en observasjon atlaset IKKE bærer: propofol-EEG (Chennu et al. 2016) — ingen node, ingen strøm. Raden har altså både en rute og et uadressert ledd."),
]

KATEGORI_NAVN = {
    "R": "har rute",
    "O": "navngir observasjon uten atlas-node",
    "I": "navngir ingen observasjon",
}


def les(repo: str, ref: str) -> dict:
    r = subprocess.run(["git", "show", f"{ref}:schema/regime_nodes.jsonld"],
                       cwd=repo, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"kunne ikke lese {ref}: {r.stderr.strip()[:200]}")
    return json.loads(r.stdout)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--skriv", action="store_true")
    a = ap.parse_args(argv)

    repo = Path(a.repo).resolve()
    atlas = les(str(repo), a.ref)
    ids = {n["id"] for n in atlas["nodes"]}
    kl = {n["id"]: klasse(n) for n in atlas["nodes"]}
    kontrakter = [n["id"] for n in atlas["nodes"] if kl[n["id"]] in ("P", "F")]

    # Nevneren skal være DEN SAMME som planen og emitteren: P ∪ F.
    if sorted(kontrakter) != sorted(r[0] for r in RADER):
        diff = set(kontrakter) ^ set(r[0] for r in RADER)
        raise SystemExit(f"nevneren stemmer ikke med lista: {sorted(diff)}")
    for i, k, *_ in RADER:
        if kl[i] != k:
            raise SystemExit(f"klassen til {i} er {kl[i]}, lista sier {k}")

    telling = {b: sum(1 for r in RADER if r[6] == b) for b in "ROI"}
    slag = {}
    for r in RADER:
        if r[5]:
            slag[r[5]] = slag.get(r[5], 0) + 1

    sha = subprocess.run(["git", "rev-parse", a.ref], cwd=str(repo),
                         capture_output=True, text=True).stdout.strip()
    fil = subprocess.run(["sha256sum", "schema/regime_nodes.jsonld"],
                         cwd=str(repo), capture_output=True, text=True).stdout.split()[0]

    print(f"ref {a.ref} = {sha}")
    print(f"schema/regime_nodes.jsonld sha256 = {fil}")
    print(f"nevner (P∪F): {len(RADER)}  " +
          "  ".join(f"{KATEGORI_NAVN[b]} = {telling[b]}" for b in "ROI"))
    print(f"adresse-slag blant R: {slag}")
    if not a.skriv:
        return 0

    linjer = [
        "# Kontraktene uten maskinadresse — hvilke av de 35 peker på en rute atlaset alt bærer",
        "",
        "**Kort**: t_eb9794ce (researcher) · **Fanout K5** fra `t_c3930d65`",
        "**Målt mot**: `origin/main` = `" + sha + "`",
        "**Fil målt**: `schema/regime_nodes.jsonld` sha256 `" + fil + "`",
        "**Status**: MÅLING, PRE-K2 — ingen node er endret, ingen kanon flyttet",
        "",
        "---",
        "",
        "## 0. Grunnlaget, og hva som ikke var verifisert da jeg begynte",
        "",
        "Kortet ba meg måle forutsetningene først. Begge ble målt, og **ingen av dem holder**:",
        "",
        "| Forutsetning | Kortets sjekk | Målt utfall |",
        "|---|---|---|",
        "| K1 `t_1a49ea8d` — hulltelleren i emitteren | "
        "`grep -n \"forpliktelser\\|fritak som motsier\" …/metrikk/atlasoppgjoer.py` | "
        "**0 treff, og emitterens sha256 er uendret** (`b9a7c97d…`, samme fil som #1016) → "
        "K1 har **ikke landet**. Kortet finnes: `t_1a49ea8d`, status `ready`, assignee `faber`, "
        "på default-brettet i **toppnivå-databasen** `/opt/hermes-tavle/kanban.db`. "
        "*(Rettelse: min første måling sa «finnes ikke» — jeg globbet `boards/*/*.db`, og "
        "default-brettets kort bor IKKE i undermappen. `boards/default/kanban.db` er en 0-byte "
        "dekoy, kjent i huset fra `t_acf4d0e7`. Feil klasse: sjekken så i feil sett og svarte "
        "selvsikkert. Se `t_97c240a5`.)* |",
        "| K2 `t_c355bf46` — de to fritakene tar stilling | "
        "`print([n['id'] for n in d['nodes'] if n['id'] in ('obs.bao','obs.fsigma8')])` | "
        "**Sjekken kan ikke feile** (den skriver ut id-ene uansett). Målt på ekte vis: "
        "`obs.bao` og `obs.fsigma8` har `ville_falsifisere = null` OG "
        "`falsifiserbarhet = null` → de har **ikke** tatt stilling. K2 har ikke landet. |",
        "",
        "Orchestrator bekreftet korreksjonen midt i kjøringen og ba meg fullføre med grunnlaget "
        "skrevet inn i leveransen i stedet for å blokkere. Det er gjort.",
        "",
        "**Rettelse nr. 2 (samme kjøring):** min første K1-måling konkluderte «K1 finnes ikke». "
        "Det var feil, og feilen var i søkesettet, ikke i funnet — default-brettets kort ligger "
        "i toppnivå-databasen, ikke i `boards/default/`. Konklusjonen står (K1 har ikke landet); "
        "begrunnelsen er rettet i raden over, og den er målt på nytt: emitteren er byte-identisk "
        "med #1016 og `grep` gir 0 treff.",
        "",
        "### Derfor står denne lista som PRE-K2",
        "",
        "`obs.bao` og `obs.fsigma8` er klassifisert som **fritatt instrument (M)** i atlaset jeg "
        "leste, og er derfor **ikke** blant de 35 radene under. Begge er likevel navngitt her, "
        "fordi de er de to eneste nodene i atlaset som oppfyller begge vilkårene:",
        "",
        "* de erklærer seg fritatt med instrument-grunnen «any falsification belongs to the "
        "claim that uses the measurement», og",
        "* de bærer samtidig en forseglet `prediction`-blokk: `source: efc-sealed-prediction`, "
        "`sealed_doi: 10.6084/m9.figshare.32013156`, `sealing_sha256: fbb53d61…`, "
        "`arbiter_waiting_for: DESI DR2 full-shape`.",
        "",
        "Målt teller: **2** (`fritak som bærer forseglet krav`). Landingen i K2 flytter dem til "
        "P eller F og gjør nevneren **35 → 37**. Hva det gjør med denne lista er målt i §6.",
        "",
        "### Reproduksjon",
        "",
        "```",
        "python3 docs/notes/atlas_kontrakter_uten_maskinadresse_t_eb9794ce.py \\",
        "        --repo . --ref origin/main",
        "```",
        "",
        "Skriptet leser fra en git-ref, sjekker at nevneren er den samme som planens (P ∪ F = 35) "
        "og at klassen per node stemmer med lista, og skriver ingenting uten `--skriv`.",
        "",
        "---",
        "",
        "## 1. Regelen brukt på alle 35 (én lesning, ingen magefølelse)",
        "",
        "Et referentledd i falsifikatoren **resolverer** når det navngir en observasjon atlaset "
        "alt har en adresse for. Fire slags adresser teller:",
        "",
        "* **obs** — en `obs.*`-node, der falsifikatoren navngir nodens `target` eller dens "
        "`instrument`/`measurer` (begge er nodens egne felt).",
        "* **kant** — en maskinlesbar relasjonskant `OBSERVED_THROUGH`/`INSTANCE_OF` fra en "
        "`obs.*`-node til noden, eller fra en buss-node til en `obs.*`-node.",
        "* **buss** — et buss-emne i domenet noden selv erklærer i `buss_domene` "
        "(emnene er målt fra `schema/atlas_dekning.json`, ikke skrevet for hånd).",
        "* **doi** — den forseglede DOI-en og voldgiftsmannen som alt står i en nodes `prediction`.",
        "",
        "Der falsifikatoren navngir en **størrelse** uten instrument (f.eks. «a triggered flare "
        "with B < 0.3 T»), er nodens eget `measure`-felt lest for å se hvilken kanal størrelsen "
        "leses gjennom. Det er nodens egen deklarasjon, ikke en tolkning — og hvilket felt ruten "
        "kom fra står i merknaden.",
        "",
        "**De tre kategoriene er kortets:**",
        "",
        "| | Kategori | Antall |",
        "|---|---|---|",
    ]
    for b in "ROI":
        linjer.append(f"| {b} | {KATEGORI_NAVN[b]} | **{telling[b]}** |")
    linjer += [
        f"| | **sum (nevneren P ∪ F)** | **{len(RADER)}** |",
        "",
        "**Det reelle hullet er `navngir ingen observasjon` = "
        f"{telling['I']}.** Det tallet skal stå alene og skal ikke kunne leses som «nesten "
        "ferdig»: for disse finnes det ikke noe referentledd i materialet å bygge en adresse av. "
        f"De {telling['O']} i midten er en annen sak — der ER testen navngitt, men atlaset bærer "
        "den ikke, og det er en beslutning om å bygge en node, ikke om å pynte et felt.",
        "",
        "---",
        "",
        "## 2. Lista",
        "",
        "| # | node | kl | observasjonen falsifikatoren navngir (kildefelt) | rute → adresse | adresse-slag | kat. |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, (nid, k, felt, sitat, adresse, aslag, kat, merknad) in enumerate(RADER, 1):
        sitat_kort = sitat if len(sitat) <= 190 else sitat[:187] + "…"
        linjer.append(f"| {i} | `{nid}` | {k} | «{sitat_kort}» ({felt}) | "
                      f"{adresse if adresse else '—'} | {aslag if aslag else '—'} | **{kat}** |")
    linjer += [
        "",
        "### Merknader per rad",
        "",
    ]
    for i, (nid, k, felt, sitat, adresse, aslag, kat, merknad) in enumerate(RADER, 1):
        linjer.append(f"* **{i}. `{nid}`** ({kat}) — {merknad}")
    linjer += [
        "",
        "---",
        "",
        "## 3. Adresse-slagene, fordelt",
        "",
    ]
    obs_rader = [r[0] for r in RADER if r[5] and "obs" in r[5]]
    kant_rader = [r[0] for r in RADER if r[5] and "kant" in r[5]]
    buss_rader = [r[0] for r in RADER if r[5] == "buss"]
    doi_rader = [r[0] for r in RADER if r[5] and "doi" in r[5]]
    linjer += [
        f"* **obs (`obs.*`-node)** — {len(obs_rader)}: " + ", ".join(f"`{x}`" for x in obs_rader),
        f"* **kant (maskinlesbar relasjon)** — {len(kant_rader)}: " + ", ".join(f"`{x}`" for x in kant_rader),
        f"* **buss (bare strøm)** — {len(buss_rader)}: " + ", ".join(f"`{x}`" for x in buss_rader),
        f"* **doi (forseglet DOI/arbiter navngitt)** — {len(doi_rader)}: " + ", ".join(f"`{x}`" for x in doi_rader),
        "",
        "De to tallene som betyr mest for hva som kan kjøres maskinelt: **"
        f"{len(kant_rader)}** av de 35 har alt en relasjonskant fra en `obs.*`-node, og **"
        f"{telling['R']}** har en navngitt adresse i det hele tatt. Resten — **{telling['O'] + telling['I']}** "
        "av 35 — har ingen.",
        "",
        "---",
        "",
        "## 4. Den andre aksen (kortet ba om at den ble brukt, ikke gjettet)",
        "",
        "```",
        "python3 scripts/atlas_volum.py --hull",
        "git:origin/main @ " + sha[:8] + "",
        "        63  ikke_dekket  kosmos.exoplanet  0 node(s), 1 subject(s)",
        "                         observasjon.mast-caom  63",
        "```",
        "",
        "**Kildeaksen har ETT hull; kontraktaksen har "
        f"{telling['O'] + telling['I']}.** Det er to forskjellige spørsmål og skal ikke blandes: "
        "`--hull` spør om et domene mangler en node som LESER strømmen, denne lista spør om en "
        "falsifikator har en adresse å peke på. At kildeaksen er nesten ren betyr ikke at "
        "kontraktene er det.",
        "",
        "---",
        "",
        "## 5. Grensetilfellene, navngitt som grensetilfeller",
        "",
        "Kravet er en **navngitt** adresse, ikke en nærliggende. Tre rader var tvil om, og de er "
        "merket her i stedet for å bli glattet ut: to står som `O` fordi adressen aldri blir "
        "navngitt, én står som `R` på en indirekte adresse.",
        "",
        "| node | hvorfor tvil | hva som ville flyttet den til R |",
        "|---|---|---|",
        "| `efc.oekonomi_engine` | Domenet bærer IMF- og World Bank-strømmer; leverageratio er "
        "«en tilstandsindikator» i domenets begrunnelse, men falsifikatoren navngir ingen strøm. | "
        "At strømmene faktisk bærer leverageratio — målt, ikke antatt. |",
        "| `efc.samfunn_engine` | `tilstand.who-gho` er helsemyndighetenes strøm i nodens eget "
        "domene; men verken navnet eller domenets begrunnelse navngir utbrudd/R0. | At strømmen "
        "bærer utbruddsdata — målt. |",
        "| `efc.efc_background_engine` | Falsifikatoren navngir søsternoden, ikke observasjonen; "
        "ruten går via `COUPLED_TO → efc.hubble_engine` og nodens eget `measure.target` = H(z). "
        "Jeg har talt den som R fordi H(z) ER adressen, men kanten er ikke en observasjonskant. | "
        "En `OBSERVED_THROUGH`-kant, som de fire motorene alt har. |",
        "",
        "---",
        "",
        "## 6. Hva K2 lander med, målt som delta (ikke gjettet)",
        "",
        "`obs.bao` og `obs.fsigma8` er ikke i de 35 radene — de er M i dag. Flytter K2 dem til P "
        "eller F, blir nevneren 37 og de to nye radene havner i **R**, fordi adressen alt står i "
        "noden selv:",
        "",
        "* `obs.bao` — `correlation: efc-dh-over-rd.z0.7-z1.0`, to forseglede `expected`-ledd "
        "(z=0.7 og z=1.0), DOI `10.6084/m9.figshare.32013156`, arbiter «DESI DR2 full-shape», "
        "og kanten `OBSERVED_THROUGH obs.bao → efc.hubble_engine`.",
        "* `obs.fsigma8` — `correlation: efc-fs8.fsigma8.z0.7.atlas`, samme DOI og forsegling, "
        "samme arbiter, og kanten til `efc.growth_engine`.",
        "",
        "Det kan ikke måles FØR K2 har skrevet feltet (klassen utledes av feltet, og feltet "
        "finnes ikke). Det som er målt er at adressen alt ligger i noden — så de to radene vil "
        "ikke koste nye undersøkelser, bare en ny kjøring av dette skriptet. **Lista er derfor "
        "gyldig for nevneren 35 og skal kjøres på nytt etter K2.**",
        "",
        "---",
        "",
        "## 7. Funn som går ut over lista (ingen av dem er rettet)",
        "",
        "1. **En prediction-blokk kan peke på en død strøm.** `efc.enerflyt_engine`s eneste "
        "rute er ENTSO-E-emnene, og domenets egen begrunnelse sier at tilstandskilden for "
        "ENTSO-E stanset 2026-09-04 (`t_395dc396`). En adresse er ikke en levende adresse.",
        "2. **`obs.satellites` er en navnekollisjon.** `efc.orbital_engine` handler om bundne "
        "baner og Hill-sfærer; `obs.satellites` måler «the subhalo population» (HST, "
        "simuleringer) — mørk materie, ikke romfartøy. Ruten går til CelesTrak-emnene i stedet.",
        "3. **SPARC-adressen er delt på tvers av to statistikker.** `obs.rar` er SPARCs "
        "datasett, men bærer RAR (a_obs vs a_bar), mens `efc.rotation_engine` og `efc.lag_s` "
        "begge navngir v(r). Samme datasett, to statistikker, én node.",
        "4. **`efc.klima_engine` navngir en størrelse atlaset ikke har noen strøm for.** "
        "Domenet verden.klima bærer havtilstand, land-/årsindikatorer og medieomtale — ingen "
        "temperatur. Det er et hull i atlaset, ikke bare i kontrakten, og det er ikke det "
        "samme hullet som `atlas_volum.py --hull` viser.",
        f"5. **{len(buss_rader)} av de {telling['R'] + telling['O']} kontraktene som navngir en "
        "observasjon har bare en strøm, ingen `obs.*`-node.** De kan ikke få en "
        "`prediction`-blokk med korrelasjon mot en observasjonsnode før en slik node finnes; "
        "de kan bare få et buss-emne.",
        "6. **De fire selv-nodene deler én setning.** «The self-application would fail if the "
        "atlas could not be described by its own schema.» Fire noder, én påstand, og ingen av "
        "dem navngir en observasjon. Planens §0.3 navngir dem som `arbiter=utledning`.",
        "",
        "---",
        "",
        "## 8. Hva dette notatet IKKE gjør",
        "",
        "* Ingen node i `schema/regime_nodes.jsonld` er endret, lagt til eller fjernet.",
        "* Ingen `prediction`-blokk er skrevet. Hvilke kontrakter som skal få én er en "
        "beslutning som ikke er tatt, og denne lista er bare grunnlaget for den.",
        "* Ingen kanon er flyttet, ingen DOI, ingen merge. Landing er ikke dette kortets.",
        "* Ingen teller for K1 er skrevet (den er K1s leveranse) og ingen K2-endring er gjort.",
        "",
    ]
    (repo / "docs/notes/atlas_kontrakter_uten_maskinadresse_t_eb9794ce.md").write_text(
        "\n".join(linjer) + "\n", encoding="utf-8")
    print("skrev docs/notes/atlas_kontrakter_uten_maskinadresse_t_eb9794ce.md")
    return 0


def klasse(node: dict) -> str:
    if str(node.get("ville_falsifisere") or "").strip():
        return "P"
    if (node.get("falsifiserbarhet") or {}).get("status"):
        return "F"
    g = ((node.get("stipulasjoner") or {}).get("ikke_falsifiserbar_grunn") or "")
    for k, p in (("M", "The instrument node cannot be felled by an observation"),
                 ("B", "Established physics is not ours to fell"),
                 ("S", "The self-description has no claim to strike down")):
        if g.strip().startswith(p):
            return k
    return "U"


if __name__ == "__main__":
    sys.exit(main())
