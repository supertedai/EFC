# NATS-koblingskart — hvilke bussemner mater hvilke motorer

Trinn 9 (2026-09-16). Kartet er en **observasjon**, ikke en taksonomi:
det beskriver hvilke emner verdensbussen faktisk bærer, og hvilke
EFC-motorer de kan mate. Inndelingen av verden i domener er en beslutning
for eierne — dette kartet bare SPEILER den beslutningen slik den står på
bussen i dag.

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
| `verden.energi.tilstand.victron` | `VictronChargeEngine` | **Koblet via victron-nats-bro** (utenfor dette repoet, read-only). Bussen bærer V(t), SOC(t) og effekter — timeoppløsning, anonymisert stedskode. Kne-deteksjonen rapporterer `found=False` med grunn: bussen har ingen ladestrøm I(t), og timeoppløsning er grovt nok til at CC→CV-kneet ikke er lesbart (målt i trinn 8: usynlig i 15-min-midler). Krav for auto: serie `batteri_stroem` (A) på emnet. |

### Eksisterende på bussen (bygget av andre, ikke av motoren)

| Emne | Innhold | Motor |
|---|---|---|
| `kosmos.kosmologi.tilstand.efc-fs8` | Forseglet fσ8-baseline (DESI DR1, eBOSS) med L/S-klassifisering og arbiter-kriterium mot DESI DR2 full-shape | `growth` (fσ8) — arbiteren er den faktiske EFC-testen |
| `kosmos.kosmologi.prediksjon.efc-fs8` | Én EFC-prediksjon | `growth` |
| `kosmos.kosmologi.diskusjon.arxiv` | arXiv-papirer | (kildegrunnlag, ikke måling) |

### Kandidater (emner som finnes, kobling ikke bygget)

| Emne | Innhold | Motor-kandidat |
|---|---|---|
| `kosmos.hoper.observasjon.mast-caom` | Hoper (MAST/CAOM) | `cluster` |
| `kosmos.galakser.observasjon.mast-caom` | Galakser | `lensing` (svak linsing) |
| `kosmos.stjerner.observasjon.mast-caom` | Stjerner | `rotation` (galakserotasjon er L2-domenet; stjernerotasjon er analogi-kandidat) |
| `verden.vaer.tilstand.ecowitt` / `metar` | Vær-tilstand | `water` (faseoverganger i atmosfærisk vann — analogi, ikke identitet) |
| `verden.energi.prediksjon.entsoe-dayahead` | Kraftpris-prognoser | (energiøkonomi — ingen motor ennå) |

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
kan mate det.
