# NATS-koblingskart — hvilke bussemner mater hvilke motorer

Trinn 9 (2026-09-16), oppdatert etter trinn 10–12. Kartet er en
**observasjon**, ikke en taksonomi: det beskriver hvilke emner
verdensbussen faktisk bærer, og hvilke EFC-motorer de kan mate.
Inndelingen av verden i domener er en beslutning for eierne — dette
kartet bare SPEILER den beslutningen slik den står på bussen i dag.

## Bussen

Én NATS-server («verdensserveren») bærer fem strømmer etter lag:

| Strøm | Lag | Betydning |
|---|---|---|
| VERDEN_OBS | observasjon | instrumentbårne rådata (GDELT GKG, MAST/CAOM) |
| VERDEN_TILSTAND | tilstand | aggregert nå-tilstand (energi, vær, økonomi, kosmos-kataloger) |
| VERDEN_PROGNOSE | prediksjon / oppgjør | prognoser og oppgjorte prediksjoner (værvarsel, ENTSO-E, EFC-fs8) |
| VERDEN_TOLKET | diskusjon / hendelse | tolkede hendelser (GDELT mentions/export, GCN, ALeRCE) |
| OPUS_SELV | — | egen dommekrafts-ledger (handlingsledger) |

Emnene har formen `<rot>.<domene>.<lag>.<kilde>` der `rot` er `verden`
(samfunnsmessig virkelighet) eller `kosmos` (fysisk virkelighet utenfor
den).

## Koblinger: emne → motor

### Koblet (datakilde eksisterer og er bygget)

| Emne | Motor | Status |
|---|---|---|
| `verden.energi.tilstand.victron` | `VictronChargeEngine` | **Koblet via victron-nats-bro** (utenfor dette repoet, read-only). Live på bussen: `batteri_spenning` (V) og `batteri_ladning` (SOC). `batteri_stroem` (A, VRM-kode `CI`, målt) er **bygget, ikke deployet** — produsentkoden er merget i trinn 10, men deploy til bussen er eiernes steg. Timeoppløsning, anonymisert stedskode. Kne-deteksjonen rapporterer `found=False` (payload: `found`, `t_knee`, `v_knee`, `i_knee` — NaN når ikke funnet — pluss tellerne `n_samples`, `n_cc`, `n_cv`; ingen grunnfelt; forklaringen av grunnen står i broens kjøringsartefakt). |

**Motorens kontrakt vs broens skjema — to forskjellige ting.** Motoren
er injiserbar og krever per kjøring:

1. `v_series` — spenning over tid (V). Bussen bærer den i dag
   (`batteri_spenning`).
2. `i_series` — strøm over tid (A). Bygget i trinn 10
   (`batteri_stroem`); produsentkoden er merget (PR #969, i
   driftsrepoet) og **deploy til bussen er eiernes steg** — inntil da
   er serien fraværende på bussen.
3. Tersklene `v_knee_tol`, `di_threshold`, `cc_flat_threshold` —
   motorens egne, aldri bussens ansvar.

Broens skjema er bussens egne serier; det broen gjør er å oversette dem
til kontrakten. **Auto-deteksjon av CC→CV-kneet krever alle tre
delene av kontrakten** — v-serien finnes, i-serien er bygget men
deploy-avhengig, tersklene er motorens. I tillegg krever kneet en
tidsoppløsning fin nok til å se strømplatået: kneet er målt usynlig i
15-min-midler (trinn 8), så en I-serie på timeoppløsning vil fortsatt
gi `found=False` — bare med en annen grunn.

### Live på bussen (målt)

| Emne | Innhold | Motor |
|---|---|---|
| `kosmos.kosmologi.tilstand.efc-fs8` | Forseglet fσ8-**baseline**: OBSERVERTE målinger (DESI DR1, eBOSS) med L/S-klassifisering — referanseverdier, ikke EFC-utfall | ingen — baselinen er arbiterens grunnlag, ikke motor-output |
| `kosmos.kosmologi.diskusjon.arxiv` | arXiv-papirer | (kildegrunnlag, ikke måling) |

### Kontrakter definert — publikasjon venter på skrivetilgang

Disse emnene har et definert skjema og en implementert produsent-side,
men er **ikke verifisert live på bussen** — publisering tilbake krever
skrivetilgang eierne ennå ikke har gitt.

| Emne | Innhold | Produsent |
|---|---|---|
| `kosmos.kosmologi.prediksjon.efc-fs8` | EFC-**prediksjon** (modellert fσ8) | `growth` produserer prediksjonen (fσ8(z=0.7), parameter-avledet); `SealedFs8Arbiter` (trinn 12) dommer den mot baselinen |
| `kosmos.kosmologi.oppgjoer.efc-fs8` | Arbiterens **måling** — DESI DR2 full-shape fσ8(z~0.7), med feltene `must_arrive.required_fields` og proveniens (`seq`, `Nats_Msg_Id`, `referanse`, `survey`, `tracer`) | `scripts/atlas_arbiter_konnektor.py` (t_8e217b72). **0 meldinger målt 2026-09-18**, og det er den korrekte tilstanden: konnektoren publiserer ingenting før målingen finnes, og skriver grunnen i sin egen logg (`logs/atlas-arbiter-konnektor.jsonl`). En måling utenfor `z_window [0.6, 0.8]` rutes til `kosmos.kosmologi.tilstand.efc-fs8` med `arbiter: "nei"` — den er en baseline, ikke arbiteren |
| `kosmos.kosmologi.oppgjoer.efc-fs8-arbiter` | Arbiterens **utfall** (PASS/FAIL/VENTER med regel og kilde) | arbiteren selv — payload-format definert i trinn 12 |

**To emner, én korrelasjon — og de er ikke samme feed.** Målingen
(`…oppgjoer.efc-fs8`) og dommen (`…oppgjoer.efc-fs8-arbiter`) er to
selvstendige emner: NATS matcher emner ledd for ledd, så
`efc-fs8-arbiter` er sitt eget ledd og en abonnent på det ene får ikke
det andre. Begge bærer lag-ordet `oppgjoer`, som er leddet
VERDEN_PROGNOSE fanger (målt 2026-09-17, `tests/test_arbiter_emne_kontrakt.py`).

### Kandidater (emner som finnes, kobling ikke bygget)

| Emne | Innhold | Motor-kandidat |
|---|---|---|
| `kosmos.hoper.observasjon.mast-caom` | Hoper (MAST/CAOM) | `cluster` |
| `kosmos.galakser.observasjon.mast-caom` | Galakser | `lensing` (svak linsing) |
| `kosmos.stjerner.observasjon.mast-caom` | Stjerner | `rotation` (galakserotasjon er L2-domenet; stjernerotasjon er analogi-kandidat) |
| `verden.energi.prediksjon.entsoe-dayahead` | Kraftpris-prognoser | (energiøkonomi — ingen motor ennå) |

### Koblet via vær-broen (L-008)

| Emne | Motor | Status |
|---|---|---|
| `verden.vaer.tilstand.metar` | `water` (WaterPhaseEngine) | **Koblet via vaer-nats-bro** (utenfor dette repoet, read-only). METAR-kanalen: temperatur + duggpunkt → spredning, RH-proxy (P_sat(Td)/P_sat(T) via motorens dampkurve), regime-klassifisering og 0 °C-passeringer. Første kjøring (2026-09-16): 459 punkter, 149 kondensasjonsnære, én fullstendig metning (spredning 0,0 °C). |
| `verden.vaer.tilstand.ecowitt` | `water` (WaterPhaseEngine) | **Koblet via vaer-nats-bro** — ecowitt-kanalen har bare temperatur (ingen fuktighet); der er 0 °C-passeringene de eneste temperaturbaserte indikatorene/proxyene for mulig frysing eller smelting — selve faseovergangen er ikke observert. |

Merk: kondensasjonsnærhet er en faseovergangs-PROXY, ikke selve overgangen —
analogi, ikke identitet (samme disiplin som resten av kartet).

### Koblet via bro-laget (2026-09-17, kosmos_nats_bro/jord_nats_bro/sol_nats_bro)

| Emne | Motor | Status |
|---|---|---|
| `kosmos.sol.tilstand.swpc-goes-xray` + `kosmos.sol.hendelse.nasa-donki` | `solar_flare` (SolarFlareEngine) | **Koblet via sol-nats-bro** — GOES-flux til klasse, DONKI-utbrudd som utløsningshendelser. Kandidat-status: idealisert holding→release-modell, IKKE flare-prediktor. |
| `kosmos.jord.tilstand.usgs-seismikk` | `jordskjelv` (JordskjelvEngine) | **Koblet via jord-nats-bro** — magnitude → moment (Kanamori-invers), b-verdi fra hendelsessekvensen. Kandidat-status: idealisert elastic-rebound, IKKE skjelv-prediktor. |
| `kosmos.romvaer.tilstand.swpc-kp` | `romvaer` (RomvaerEngine) | **Koblet via kosmos-nats-bro** — Kp lest direkte, G-nivå fra NOAA-skalaen. Korrelasjonsmodell, Newell-caveat. |
| `kosmos.transienter.hendelse.alerce` | `transient` (TransientEngine) | **Koblet via kosmos-nats-bro** — klasse-fordeling, stjernedød-telling. ALeRCEs egen klassifikasjon, ikke motorens prediksjon. |
| `kosmos.planetsystem.prediksjon.jpl-horizons` | `orbital` (OrbitalEngine) | **Koblet via kosmos-nats-bro** — avstand_sol_au som a-proxy (deklarert). Kepler gjengir planetperiodene. |
| `kosmos.maane.prediksjon.jpl-horizons` | `tidevann` (TidevannEngine) | **Koblet via kosmos-nats-bro** — avstand_jord_au → tidevannshøyde (åpent hav ~0.62 m). |
| `verden.miljo.tilstand.ecowitt` | `klima` (KlimaEngine) | **CO2-observasjon via kosmos-nats-bro** — drivhus-proxy, IKKE tvunget gjennom motoren (CO2→emissivitet er en egen, upåstått kjede). |

Bro-runden kjører hver time (cron e8c6fd64b23f) og publiserer på
`opus.dommekraft.tilstand.broer`. Alle broene er eksterne og
read-only (samme design som vær-broen).

### Ikke koblet, og ikke åpenbart motorkandidat (per i dag)

Samfunnsemnene (`verden.*` utenom energi/vær: arbeid, demografi, finans,
geopolitikk, helse, handel, lov, miljø, økonomi, politikk, sikkerhet,
teknologi, transport, utdanning) er GDELT/Eurostat/World-Bank-data. De er
ikke faseoverganger i EFC-forstand — en kobling hit ville være en
kategorifeil. De hører hjemme i andre analyseformer, ikke i regime-atlaset.

## Leserens grenser

Dette repoet **leser aldri bussen selv** — motoren er injiserbar og
site-anonym (trinn 8-designet). Broen som leser bussen er en ekstern
datakilde med read-only-konsument-rolle. Skillet er med vilje: atlaset
skal ikke avhenge av en levende buss; bussen er én av flere kilder som
kan mate det. Det gjelder lesesiden, og bare den: **publisering tilbake
til bussen** finnes nå i to spor — målingen
(`scripts/atlas_arbiter_konnektor.py`, t_8e217b72) og dommen
(`scripts/maintenance/arbiter_vakt_kjoer.py`, L-016). Begge er
best-effort og krever `NATS_PRODUSENT` i miljøet; repoet bærer aldri
legitimasjon, og en kjøring uten den melder «ingen
produsent-legitimasjon» i stedet for å gjøre noe. Åpningen er dermed
eiernes: nøkkelen, ikke koden.
