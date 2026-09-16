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
| `kosmos.kosmologi.utfall.efc-fs8-arbiter` | Arbiterens **utfall** (PASS/FAIL/VENTER med regel og kilde) | arbiteren selv — payload-format definert i trinn 12 |

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
kan mate det. Det gjelder begge veier: **publisering tilbake til
bussen** (f.eks. arbiterens utfall) er ikke bygget inn — det er en
dør eierne kan åpne, ikke en dør repoet lukker.
