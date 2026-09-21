# Runde 2026-09-21 — `kosmos.exoplanet` (pilot for forskerløkka)

**Kort:** `t_a0e3260f` (brett `energy-flow-cosmology`). Én runde, kjørt i hånda.
Ingenting bygget: ingen konnektor, ingen scheduler, ingen vakt, ingen bankskriving.
**Målt mot:** `/opt/agent-work/EFC` @ `origin/main` = `22438ec9`.

Dette er **ett evidensartefakt**. Det inneholder gapet, spørsmålet, metoden,
treffene per kildeklasse, uavhengighetstellingen, falsifikatoren, statusene,
negativkontrollen med råutskrift, og hva som er reproduserbart.

---

## 1. Gapet er valgt fordi det er målt, og atlaset er spurt først

Valgt gap: **`kosmos.exoplanet`**. Inngangen er `schema/atlas_dekning.json`
(målt 2026-09-19, 39 domener): `ikke_dekket`, 63 meldinger, 0 noder, ett emne
(`observasjon.mast-caom`).

Atlaset ble spurt **før** noe annet ble lest:

```
$ python3 scripts/atlas_inngang.py kosmos.exoplanet /opt/agent-work/EFC
ENTRY: kosmos.exoplanet
REF: origin/main @ 22438ec9
NODE: no node — KNOWN GAP
  domain: kosmos.exoplanet
  status: ikke_dekket
  reason: Maalt 2026-09-19: 63 meldinger over ett emne (observasjon.mast-caom),
          og ingen node navngir domenet — MAST/CAOM-andelen er ikke beskrevet. …
TOPIC: 0 hits in the bank — THE ATLAS DOES NOT KNOW
ENGINE: no engine file
BUS: no bus route
```

Og på emnet:

```
$ python3 scripts/atlas_inngang.py observasjon.mast-caom /opt/agent-work/EFC
NODE: no node — THE ATLAS DOES NOT KNOW (no measurement)
TOPIC: 6 hits in the bank
```

**Hvilket av de tre svarene fikk jeg?** Begge de to ikke-tomme, og de er ikke
det samme svaret:

| spørsmål | svar | hva det betyr |
|---|---|---|
| domenet `kosmos.exoplanet` | **KJENT HULL** | navngitt hull med målt størrelse (63 meldinger) |
| emnet `observasjon.mast-caom` | **ATLASET VET IKKE** (0 noder, ingen måling) | emnet finnes i banken (6 treff) men er ikke målt inn i atlaset |

Volumet er målt om igjen med det andre verktøyet, og stemmer:

```
$ python3 scripts/atlas_volum.py --hull --repo /opt/agent-work/EFC
git:origin/main @ 22438ec9
        63  ikke_dekket  kosmos.exoplanet  0 node(s), 1 subject(s)
                         observasjon.mast-caom  63
```

Kildenivået, samme ref (dette er den *andre* aksen i samme fil — den som
domeneaksen ikke kan se):

```
$ python3 scripts/atlas_kilder.py --json --ref origin/main
{"navn": "MAST/CAOM", "ledd": ["mast-caom"], "meldinger": 1069,
 "domener": ["kosmos.exoplanet","kosmos.galakser","kosmos.hoper",
             "kosmos.planetsystem","kosmos.stjerner","kosmos.uklassifisert"],
 "lesere": ["kosmos.interstellart","kosmos.stjerner"], "eiere": [], "status": ["lest"]}
```

**63 av 1069 meldinger** er exoplanet-andelen av MAST/CAOM-strømmen (5,9 %).
Ingen node eier kilden (`eiere: []`).

---

## 2. Spørsmålet, i husets skjema

Skjemaet er gjenbrukt, ikke funnet opp: `schema/regime_node.schema.json`
(`$defs.RegimeNode`). Kortets liste mappes mot feltene som faktisk finnes —
og der kortet navngir noe skjemaet ikke har, står det her i stedet for å bli
diktet inn i skjemaet:

| kortets ord | husets felt |
|---|---|
| mål | `measure.target` |
| observasjon | `measure.measurer` + `measure.placement` (hva leses faktisk ut) |
| måler/instrument | `measure.instrument` |
| proxy + full proxykjede | `measure.proxy_chain` (ordnet array) |
| regime | `regime.{name,validity,law_form}` + `maale_paradigme` |
| regime, de sju aksene | **ikke egne felt** — mappet til `regime.validity`, `nivaa.{tidsskala,lengdeskala}`, `measure.*`, `epistemikk` (se tabellen under) |
| vektor/endringsretning | **ikke eget felt** — måles som drift i `observasjon` over tid |
| entropitype | **ikke eget felt** — nærmeste er `buffer.role` og `maale_paradigme.sektor` |
| svakeste ledd | `ontology.proveniens.begrensning` |
| neste mest informative test | `open_questions[].q` |
| — | `stipulasjoner.stipulert_av_oss` (grensen vi selv setter) |
| — | `ville_falsifisere` / `falsifiserbarhet` |
| — | `rcmp.{instrument,observabel,teori,overlap}` |

### Spørsmålet

> **Er exoplanet-andelen av `observasjon.mast-caom` et mål på planetfysikk
> eller på observasjonspraksis — og hva må en `kosmos.exoplanet`-node i så
> fall erklære at den måler?**

### Feltvis

**`measure.target`** — «observatørens deklarerte målklasse for et pekt
teleskop», ikke planeten. Skillet er målt: en `observasjon` i husets egen
§11.13-tabell er «ingen — rådata fra kilden».

**`measure.measurer`** — arkivet (STScI/MAST). Ingen vurderte raden:
`mast-konnektor.py`:17-18 sier det selv — «Arkivet skrev ned hva som skjedde.»

**`measure.instrument`** — misjonenes fotometre og spektrografer, ett sett per
misjon i ÉN CAOM-modell (`obs_collection` i raden: TESS, K2, HLSP, PS1, GALEX,
SDSS i det målte utvalget).

**`measure.proxy_chain`** — ordnet, tre substitusjoner innebygd:

1. operatørens forslag og måltekst → arkivets `target_classification` (fri
   tekst fra fremmed kilde, ulik skrivemåte per misjon: `EXT-STAR`, `Star`,
   `TIER1=STAR` — konnektoren:485-487)
2. `target_classification` → domene, ved **vår** regex + presedensrekkefølge
   (`mast-konnektor.py`:488-511)
3. CAOM-rad → busstemne, filtrert på `t_obs_release` i et to-døgnsvindu
   (konnektoren:40-46)

**`measure.placement`** — katalogens rad, ikke observatøren. Observatøren
(operatøren, forslags-PI-en) er ikke plassert i kjeden; bare navnet hans
(`proposal_pi`) følger med som hode.

**`measure.compression`** — ja, men arkivets: en peking med utstrekning og
tidsvindu komprimeres til én rad med instrument, kalibreringsnivå, MJD-vindu
og fotavtrykk. Målt: 16 rader over et kjent exoplanetfelt, **alle**
`dataproduct_type = image`, `calib_level` 2 eller 3.

**`regime`** — de sju aksene, som kortet ba om:

| akse | målt svar |
|---|---|
| fysisk | stråling ved himmelen, detektert og arkivert. Ingen gravitasjons-, fluid- eller feltregime. Ingen EFC-regimebinding. |
| skala | fotavtrykk (grader), apertur og bølgelengde (nm–µm). **Ingen fysisk skala på målet** — planeten har ingen skala i strømmen. |
| tid | to tider, og det er de to: `t_min`/`t_max` = observasjonsvindu (MJD), `t_obs_release` = offentliggjøring. Konnektoren **filtrerer på release**. Busstidsstempelet er altså *publiseringstid*, ikke observasjonstid. |
| måling | `calib_level`, `dataproduct_type`, `instrument_name`. Instrumentets lag, ikke himmelens. |
| proxy | tre substitusjoner (se kjeden). Det er her regimet skifter, og skiftene er ikke merket i raden. |
| modell | ingen fysisk modell i strømmen. Transitmodell, limb-darkening og stjerneradius ligger nedstrøms, utenfor domenet. |
| epistemisk | institusjonell/konsensus. Raden er «ingen — rådata fra kilden»; klassifikasjonene den bærer er kildens vurderinger (konnektoren:20-24). |

**`maale_paradigme.s_regime`** = `S>0`, **`sektor`** = `S` — men det står med
forbehold: dette er **arvet fra atlasets plassering av kosmos-domenene, ikke
målt i strømmen**. Ingenting i en CAOM-rad måler S. Å skrive S>0 her uten det
forbeholdet er nøyaktig den arven som ga 52 gruppeløse noder.

**`vektor` / endringsretning** — den eneste målte retningen er i
*publiseringsvolum* over tid (rader per utgivelsesvindu). Det er en retning i
praksis, ikke i fysikk. Ingen fysisk vektor finnes i strømmen.

**`entropitype`** — **ingen, og det er svaret, ikke et hull i svaret.** Strømmen
bærer ingen entropistørrelse. Å fylle feltet ville være å finne den opp på
strømmen. `buffer.role` er den ærlige naboformuleringen: bufferet er *arkivet
selv* — det holder raden mellom utgivelser.

**`svakeste ledd`** — `target_classification`. Fri tekst fra en fremmed kilde,
normalisert ulikt per misjon, og grensen `exoplanet` ↔ `planetsystem` er **vår**
regex og **vår** presedensrekkefølge. Konnektoren dokumenterer at den HAR
brent seg, og hvordan: `IO\b` traff «RAD-IO » i `RADIO GALAXY;JET`, og fordi
`planetsystem` står før `galakser`, ble en radiogalakse rutet til Jupiters måne
(`mast-konnektor.py`:501-506). Nest svakest: presedensrekkefølgen, som
konnektoren selv kaller beslutningen (`:471-472` — «første treff vinner — og
rekkefølgen ER beslutningen»).

**`neste mest informative test`** — mål andelen i to 90-dagers vinduer og kryss
den mot NEA-metodikktabellen per måned. Faller de sammen, faller `tolket`-en i
C4; spriker de, står den. Én runde, ingen ny konnektor: samme API, to vinduer.

---

## 3. Søket — to kildeklasser utenfor bussen

Hentet **2026-09-21**. «Utenfor bussen» = ikke GDELT, ikke arXiv-feeden i
huset, ikke konnektoren.

### Klasse (a) — indeksert faglitteratur (peer-reviewed)

| # | verk | URL | hentet | hva den bærer |
|---|---|---|---|---|
| A1 | Guerrero, Seager, Huang m.fl., *The TESS Objects of Interest Catalog from the TESS Prime Mission*, ApJS **254**, 39 (2021) | `https://arxiv.org/abs/2103.12538v1` | 2026-09-21 | 2 241 kandidater; «The TESS data products for the Prime Mission (Sectors 1-26), including the TOI Catalog, light curves, full-frame images, and target pixel files, are publicly available on the Mikulski Archive for Space Telescopes» |
| A2 | Winn & Fabrycky, *The Occurrence and Architecture of Exoplanetary Systems*, ARA&A **53**, 409–447 (2015) | `https://arxiv.org/abs/1410.4199` | 2026-09-21 | gjennomgang av baner, eksentrisitet, innbyrdes inklinasjoner og vertsstjernens rotasjonsakse — altså det fysiske laget som *ikke* ligger i CAOM |

Bibliografien er verifisert mot Crossref, ikke husket:

```
10.3847/1538-4365/abefe1              | ApJS  | vol 254 | page 39    | 2021
10.1146/annurev-astro-082214-122246   | ARA&A | vol 53  | page 409-447 | 2015
```

### Klasse (b) — primærkilde (.gov / NASA eller tilsvarende)

| # | kilde | URL | hentet | hva den bærer |
|---|---|---|---|---|
| B1 | NASA Science, Exoplanets — **nasa.gov** | `https://science.nasa.gov/exoplanets/` | 2026-09-21 | «We've confirmed more than 6,000 exoplanets» — og lenker selv til arkivet som «continuously updated resource» |
| B2 | NASA Exoplanet Archive, *Exoplanet and Candidate Statistics* (NASA- finansiert, IPAC/Caltech) | `https://exoplanetarchive.ipac.caltech.edu/docs/counts_detail.html` | 2026-09-21 | All Exoplanets 6 366 · Transit 4 708 · Radial Velocity 1 200 · Imaging 97 · Microlensing 289 · Kepler 2 787 · TESS 1 936 · TESS-kandidater 8 148 (inkl. falske positiver), 4 833 uavklarte. Kilden til tallene er oppgitt: Planetary Systems-tabellen og ExoFOP |
| B3 | MAST API-dokumentasjon (STScI, for NASA) | `https://mast.stsci.edu/api/v0/index.html` | 2026-09-21 | **navngir tjenesten** `Mast.Caom.Cone` og viser at en spørring mot CAOM er formen `{'service':'Mast.Caom.Cone','params':{'ra':…}}` |
| B4 | MAST, *Search Interfaces* | `https://archive.stsci.edu/search-interfaces` | 2026-09-21 | «exo.MAST — Search by exoplanet to find data, parameters, visualizations, and MAST holdings from Kepler, K2, Hubble, TESS and JWST» |

### Husets egen primærkilde — deklarert, ikke regnet som uavhengig

| # | kilde | identitet | hva den bærer |
|---|---|---|---|
| H1 | `hermes-drift/nats/mast-konnektor.py` (ADR-043 §11.44) | md5 `7c2278d5bbc79d7ba8e46687f78c197c`, sist endret `5863cf96` 2026-09-20 | **definisjonen av strømmen**: `observasjon`, ikke `tilstand`; domenet dannes av regex + presedens over `target_classification`; vinduet er to døgn |

H1 er den kilden som faktisk avgjør hva emnet er. Den er i huset, og teller
derfor **ikke** som uavhengig støtte.

### Egen måling av strømmen (metode, ikke kildeklasse)

Én lesning av det dokumenterte endepunktet som H1 og B3 navngir — ikke en
konnektor, én avgrenset spørring:

```
$ curl -sSG --data-urlencode 'request={"service":"Mast.Caom.Cone",
    "params":{"ra":345.5042,"dec":-5.0413,"radius":0.005},
    "format":"json","pagesize":50,"removenullcolumns":true}' \
    https://mast.stsci.edu/api/v0/invoke
rows: 16   status: COMPLETE
kolonner: calib_level, dataURL, dataproduct_type, em_max, em_min, filters,
          instrument_name, intentType, obs_collection, obs_id, obs_title, obsid,
          project, proposal_id, proposal_pi, proposal_type, provenance_name,
          s_dec, s_ra, s_region, sequence_number, t_exptime, t_max, t_min,
          t_obs_release, target_classification, target_name, wave_max, wave_min,
          wave_region, wavelength_region
obs_collection:    PS1 5 · TESS 3 · HLSP 3 · K2 2 · GALEX 2 · SDSS 1
instrument_name:   Photometer 6 · GPC1 5 · Kepler 2 · GALEX 2 · SDSS Camera 1
dataproduct_type:  image 16        calib_level: 3 (14) · 2 (2)
kolonner med en målt fysisk størrelse (rad/period/mass/depth/temp/entropi): INGEN
```

Feltet er TRAPPIST-1 (2MASS J23062928-0502285). Poenget står i siste linje:
**null** kolonner bærer en målt størrelse. Og feltet er ikke et exoplanetfelt —
det er et himmelfelt: en kjent exoplanetverts posisjon gir også PS1, SDSS og
GALEX-rader. «Exoplanet-andelen» er altså ikke en fysisk kategori i strømmen;
den er vårt regex-treff på kildens klassefelt.

---

## 4. Gradering — uavhengighet, svakeste ledd, falsifikator

**Konsensus er en observatørvariabel, ikke sannhet.** Her er den målt og
navngitt: B1 (nasa.gov «more than 6,000»), B2 (NEA 6 366) og A1 (TESS-katalog)
er **tre ledd av én linje** — TESS/Kepler-pipelinen → MAST (L1-produkter) →
NEA (avledede parametre) → nasa.gov (fortellingen) — og de måler i tillegg
**ulike populasjoner**: 2 241 kandidater (A1), «mer enn 6 000» bekreftede
(B1), 6 366 i arkivets tabell (B2). De kan derfor verken støtte eller
motbevise hverandre. Det de deler er data, kode og institusjon — det er arv,
ikke uavhengighet. At tallene «stemmer», er ingen støtte: de er ikke tre
målinger av samme størrelse.

**Uavhengighetstelling (delt data / kode / forfatterskap):**

| påstand | uavhengige kilder | hvorfor |
|---|---|---|
| C1 strømmen bærer observasjonsmetadata, ikke en målt størrelse | **1 ekstern + 1 intern** | den egne API-lesningen er den eksterne; H1s kode er husets eget design. To *komplementære* veier — hva arkivet sender ut, og hva konnektoren sender videre — ikke to bekreftelser av samme påstand |
| C2a den fysiske størrelsen ligger i en annen kjede | **1** | B2 + A1 er samme linje |
| C2b … og hos en annen institusjon | **0** | ingen av kildene avgjør om kandidattabellen serveres fra MAST, fra IPAC eller fra begge. A1 sier kandidatkatalogen ligger *på MAST*; B2 sier tallene kommer fra Planetary Systems-tabellen. Uavklart, se §10 |
| C3 domenet er dannet av vårt regex og vår rekkefølge | **1** | bare H1 sier det; ingen ekstern part beskriver vår ruting. Målingen i §4 støtter den |
| C4 andelen er ikke planetfysikk | **1** | ingen ekstern kilde sier dette om vår strøm; det er vår tolkning av C1–C3, nå med egen måling av rutingleddet |
| C5 ingen ekstern kilde kobler observasjonene til entropi | **0 universelt / 1 avgrenset** | det *universelle* negativet kan ikke etableres (§10); det *avgrensede* — «ingen støtte i det søkte settet, med virkende positiv kontroll» — er målt |

**Svakeste ledd, skrevet ut:** `target_classification` (kildens fri tekst,
ulikt skrevet per misjon) og vår presedensrekkefølge over den. Alt annet i
kjeden er målt og navngitt; dette leddet er en merkelapp satt av en annen, og
grensen vi trekker på den er vår egen.

**Falsifikator for C4** (den ene tolkningen i denne runden):

- **F2 (den bærende):** hvis exoplanet-andelen over tid følger en *fysisk*
  fordeling (oppdagelsesrate, radiusfordeling, vertsstjernens magnitude,
  galaktisk bredde) heller enn teleskopallokeringen, utgivelsesvinduet og vår
  egen ruting, faller C4. Test: to 90-dagers vinduer mot B2s metodikktabell.
- **F3 (kjørt her, se under):** hvis andelen er invariant under en permutasjon
  av domenerekkefølgen, er presedensen ikke en drivkraft. Målt: den er ikke
  invariant — den er total.
- **F1 (lagt til side):** «en CAOM-spørring avgrenset til rene exoplanetklasser
  returnerer rader som bærer planetens parametre» er nesten a priori usann — en
  avgrensning velger rader, den kan ikke legge til kolonner i et fast skjema.
  Den står her som stråmann, ikke som falsifikator. (Innvendt av panelet, og
  innvendigen er riktig.)

Ingen av F2 er kjørt her. C4 står som `tolket`, ikke som `observert`.

### Den kontrafaktiske målingen: rekkefølgen ER domenet

Panelet (begge runder) pekte på at C1–C3 ikke alene bærer «måler praksis»,
fordi konnektorens egen presedensrekkefølge er en *egen* årsak. Den ble målt,
med konnektorens egen kode (importert, ikke gjenfortalt), mot hans eget vindu
og hans eget kolonnesett — 2 døgn, MJD 61302,251–61304,251, 366 rader:

```
status: COMPLETE  |  366 rader i vinduet
fordeling: uklassifisert 221 (60,4 %) · hoper 60 · stjerner 34 ·
           interstellart 27 · galakser 12 · exoplanet 12
rader som matcher >1 domene: 99 av 366
   ('hoper','stjerner') 60 · ('interstellart','stjerner') 27 · ('exoplanet','stjerner') 12
KONTRAFAKTISK, exoplanet sist i stedet for først:
   exoplanet først: 12   |   exoplanet sist: 0   |   flyttet: 12
eksempler på target_classification for exoplanet-radene:
   'Star; Exoplanet Systems'                                     (JWST)
   'EXT-STAR;EMISSION LINE STAR;EXTRA-SOLAR PLANETARY SYSTEM;M V-IV'  (HST)
   'STAR;HERBIG AE/BE;PROTOPLANETARY DISK'                        (HST)
```

Reproduserbar uten å legge til noe i repoet — kjør dette fra scratch:

```python
import importlib.machinery, importlib.util, json, time, urllib.parse, urllib.request
sp = importlib.util.spec_from_loader("mk", importlib.machinery.SourceFileLoader(
    "mk", "/opt/hermes-drift/nats/mast-konnektor.py"))
mk = importlib.util.module_from_spec(sp); sp.loader.exec_module(mk)
now = time.time(); mj = lambda t: t / 86400.0 + 40587.0
fra, til = mj(now) - mk.VINDU_DOEGN, mj(now)
req = {"service": mk.TJENESTE, "format": "json", "params": {
    "columns": ",".join(mk.KOLONNER),
    "filters": [{"paramName": "obs_collection", "values": list(mk.KOLLEKSJONER)},
                {"paramName": "t_obs_release", "values": [{"min": fra, "max": til}]}]}}
r = urllib.request.Request(mk.BASE + "?request=" + urllib.parse.quote(json.dumps(req)))
r.add_header("User-Agent", mk.AGENT)
rader = json.load(urllib.request.urlopen(r, timeout=120))["data"]
print(len(rader), sum(1 for x in rader if mk.domene(x.get("target_classification")) == "exoplanet"))
print(sum(1 for x in rader if len([d for d, mo in mk._DOMENER
      if mo.search(mk.hodetrygg(x.get("target_classification")).upper())]) > 1))
```

**Hva målingen viser, og den retter panelet i én retning mens den bekrefter
det i en annen:**

- Panelet sa: en tidligere domene kan stjele exoplanet-rader. **Det kan den
  ikke** — `exoplanet` står *først* i `DOMENER`; ingenting står foran. Retningen
  på årsaken er den motsatte.
- Panelet sa: presedensen er en drivkraft av første orden. **Det er den, og
  målingen er total:** alle 12 exoplanet-rader matcher også `stjerner`, og med
  `exoplanet` sist ville **0** blitt igjen. Domenet er ikke *funnet* i kilden —
  det er *skåret ut* av stjernedomenet av vår egen rekkefølge.
- Typen er dermed målt i klartekst: `Star; Exoplanet Systems` er en
  **stjerneobservasjon** som matchet fordi målet *har* planeter — nøyaktig det
  konnektoren selv skriver (`:477-479`), og her bekreftet på 12 av 12 rader.
- Og 60,4 % av vinduet bærer ingen klasse i det hele tatt. Andelene regnes altså
  over et korpus der flertallet ikke er klassifisert — det er enda et målt ledd
  mellom «himmelen» og «andelen».

Det er dette som gjør C4 `tolket` og ikke `observert`: retningen er målt, men
*vekten* mellom praksis, allokering og vår egen ruting er ikke bestemt.

---

## 5. Negativkontrollen — det som gjør runden testet

Samme prosedyre, mot mål som **ikke finnes**. Prosedyren skal svare `ukjent` /
«ingen uavhengige kilder», og **ikke finne på noe**. Fem bein, én positiv
kontroll for å vise at kanalen virker.

### N1 — oppdiktet tjeneste (API)

```
$ ... service = "Mast.Caom.Entropi"
{"status":"ERROR","msg":"Unable to Locate Adaptor for service: Mast.Caom.Entropi"}
```

**Riktig:** eksplisitt avvisning. Ingen verdi diktet opp.

### N2 — oppdiktet parameter (API)

```
$ ... params = {..., "entropi_gradient_S": 0.42}
{"status":"COMPLETE","msg":"","data":[{... ordinære rader ...}]}
```

**FEIL MODUS, og det er funnet:** API-et **ignorerer** den oppdiktede
parameteren i stillhet og svarer `COMPLETE`. En prosedyre som spør «bekrefter
API-et at entropifeltet finnes?» ville svart **ja** — på et felt som ikke
finnes. Samme resultat for en oppdiktet kolonne (N3):

```
$ ... params = {..., "columns":"obsid,target_name,entropi_gradient_S"}
{"status":"COMPLETE", ...}   # kolonnen er ikke med i svaret, ingen advarsel
```

Kravet prosedyren må bære, lært her: **et 200-svar med `COMPLETE` er ikke
bevis for at et felt finnes.** Feltet må *vises fram* i radens nøkler, ellers
er svaret `ukjent`.

### N4 — oppdiktet emne i atlaset

```
$ python3 scripts/atlas_inngang.py observasjon.mast-caom-planetentropi /opt/agent-work/EFC
NODE: no node — THE ATLAS DOES NOT KNOW (no measurement)
TOPIC: 0 hits in the bank — THE ATLAS DOES NOT KNOW
ENGINE: no engine file
BUS: no bus route
```

**Riktig:** tre ikke-svar, ingen oppdiktet node.

### N5 — oppdiktet påstand, litteratursøket

Søkt (eksakt spørrestreng, gjengitt så den er etterprøvbar som *streng* — ikke
som treffliste, se §7):

```
MAST CAOM entropy gradient flag exoplanet observations EFC entropy production per observation
```

Treff: MAST-portalen, en YouTube-webinar om amatørobservasjoner, to
entropi-forklaringsartikler (Quanta; økologisk entropiproduksjon) og et
bildefilter. **Null** kilder som sier at CAOM bærer et entropifelt per
exoplanetobservasjon.

**Riktig svar fra prosedyren:** `ukjent` — ingen uavhengige kilder. Nær-treffene
er ikke støtte, og en prosedyre som telte dem, ville funnet på noe.

### Positiv kontroll — er kanalen i det hele tatt åpen?

Samme kanal, et mål som finnes: *TRAPPIST-1 seven planets confirmed mass radius
transit observations archive* → Wikipedia, ESOs systemside, ESO/A&A-manuset,
en atmosfære-review og en TTV-analyse. Altså: **nullen i N5 er en null, ikke en
død kanal.**

### Fasit på negativkontrollen

| bein | skal | gjorde | dom |
|---|---|---|---|
| N1 oppdiktet tjeneste | avvise | avviste eksplisitt | OK |
| N2 oppdiktet parameter | ikke finne på | ignorerte i stillhet, svarte OK | **FEILER ÅPENT** |
| N3 oppdiktet kolonne | ikke finne på | ignorerte i stillhet, svarte OK | **FEILER ÅPENT** |
| N4 oppdiktet emne | `ukjent` | `THE ATLAS DOES NOT KNOW` | OK |
| N5 oppdiktet påstand | `ukjent` | `ukjent`, med virkende positiv kontroll | OK |

To av fem bein feiler åpent. Det er ikke en detalj: det er derfor runden er
«testet» og ikke «demonstrert». Prosedyren har nå ett skjerpet krav (N2/N3)
som den ikke hadde da den startet.

---

## 6. Status per påstand

| # | påstand | status | grunnlag |
|---|---|---|---|
| C1 | `observasjon.mast-caom` bærer observasjonsmetadata (mål, instrument, kalibreringsnivå, tidsvindu, fotavtrykk), ikke en målt størrelse ved himmelen | **observert** | H1 + egen API-lesning (§3) |
| C2a | de fysiske størrelsene ligger i en annen kjede (TOI/Planetary Systems) | **observert** | B2 + A1 (API-nøklene i §3) |
| C2b | … og hos en annen institusjon | **ukjent** | ingen av kildene skiller MAST fra IPAC for kandidattabellen; A1 sier den ligger på MAST, B2 henter til arkivets egen tabell. Panelet fant motsetningen; jeg har ikke løst den |
| C3 | `kosmos.exoplanet` er dannet av vårt regex + vår presedensrekkefølge over kildens `target_classification` | **observert** | `mast-konnektor.py`:471-511 (md5 + commit) og målingen i §4 |
| C4 | andelen er ikke planetfysikk; den er et signal fra observatørens merkelapp, utgivelsesvinduet **og vår egen regex + rekkefølge** (målt total: 12 → 0) | **tolket** | C1–C3 + målingen i §4; *vekten* mellom leddene er ikke bestemt |
| C5a | ingen ekstern kilde i det søkte settet kobler observasjonene til entropi/EFC | **observert** | N5, med virkende positiv kontroll |
| C5b | det finnes ingen slik kobling | **ukjent** | et universelt negativ kan ikke etableres av et søk |
| H | hva noden bør måle | **hypotese** | under |
| — | negativkontrollens oppdiktede mål | **ukjent** | riktig svar (§5) |

### Hypotese: hva noden må bære (input til spesifikasjonen, ikke en endring)

Hvis atlaset skal dekke domenet, må noden erklære at den måler en
**merkelapp**, ikke en himmel. Konkret:

- `measure.target` = observatørens deklarerte målklasse — ikke planeten
- `measure.proxy_chain` = operatørens tekst → arkivets `target_classification`
  → **vår** regex og presedens → busstemne
- `stipulasjoner.stipulert_av_oss` = **true**, med regexen **og rekkefølgen**
  som navngitte terskler — målingen i §4 viser at rekkefølgen ikke er en
  detalj: med `exoplanet` sist ville domenet hatt 0 rader, ikke 63.
- `falsifiserbarhet.status` = `stub` eller `ikke_falsifiserbar_grunn` — dette er
  en instrument-/praksisnode. Den KAN ikke felles av en observasjon; den ER
  observasjonen. Å gi den et `ville_falsifisere` ville være å dikte en
  falsifikator på en merkelapp.
- `maale_paradigme.s_regime` = `S>0` **med forbeholdet skrevet inn**: arvet
  plassering, ikke målt.
- `buffer.role` = arkivet selv: det holder raden mellom utgivelser.
- `open_questions` = F1 og F2 fra §4.

Dette er en **hypotese** — noden er ikke laget, og statusvalget i
`atlas_dekning.json` er «MENNESKETS stillingtagen og utledes aldri». Jeg har
ikke rørt den.

---

## 7. Readback — hva en annen kan gjenta, og hva som ikke er reproduserbart

**Reproduserbart (deterministisk gitt ref):**

```
# 1 gapet og atlasets tre svar
python3 scripts/atlas_inngang.py kosmos.exoplanet /opt/agent-work/EFC
python3 scripts/atlas_inngang.py observasjon.mast-caom /opt/agent-work/EFC
# 2 volumet
python3 scripts/atlas_volum.py --hull --repo /opt/agent-work/EFC
# 3 kildenivået
python3 scripts/atlas_kilder.py --json --ref origin/main
# 4 strømdefinisjonen (annen repo, leses — endres ikke)
md5sum /opt/hermes-drift/nats/mast-konnektor.py   # 7c2278d5bbc79d7ba8e46687f78c197c
# 5 konnektorens domeneruting
sed -n '471,511p' /opt/hermes-drift/nats/mast-konnektor.py
# 6 negativkontrollen i atlaset
python3 scripts/atlas_inngang.py observasjon.mast-caom-planetentropi /opt/agent-work/EFC
```

Alle seks er deterministiske gitt `origin/main = 22438ec9` og
konnektor-md5-en. Stiene er absolutte fordi `atlas_inngang.py` leser **git-ref**,
ikke arbeidsstreet.

**IKKE reproduserbart, sagt ærlig:**

- **Søkemotoren.** Trefflisten i §3 kommer fra en søketjeneste over et levende
  indeks. Den kan ikke gjentas bit for bit, og rekkefølgen er ikke en måling.
  Det som ER reproduserbart er *kildelisten* (DOI-ene og URL-ene er
  verifiserbare), *hentedatoen*, og *graderingen* — ikke treffrekkefølgen.
- **MAST-API-et.** Lesningen i §3/N1–N3 er mot en levende tjeneste. Samme
  spørring kan gi andre rader senere (arket vokser). Det som er reproduserbart
  er *formen*: hvilke kolonner som finnes, og at ingen av dem er en målt
  størrelse.
- **DOIsjekken er reproduserbar:** `api.crossref.org/works/<doi>` gir samme
  svar hver gang.

**Selve spørringen** (les den som inngangen, ikke som resultatet): mål → hva
leses faktisk ut → instrument → proxykjede → de sju regimeaksene → vektor →
entropitype → svakeste ledd → neste test. Kjørt mot ett gap, med to
kildeklasser utenfor bussen, og med negativkontrollen som port.

**Egen lesning av §7 er utført av en annen kontekst** (isolert subagent, kun
inngangen over) og ligger ved som `…-vedlegg.md`. Dens epistemiske vekt:
uavhengig *kontekst*, ikke uavhengig *modell*.

---

## 8. Grenser — hva runden ikke gjorde

- **Ingen bankskriving.** Destillatbroen er stengt til ADR-014 er armet
  (ADR-043 beslutning 5). Null skriving til `efc`, `ego` eller `morten`.
- **Ingen ny konnektor, ingen ny scheduler, ingen ny vakt.** Én lesning av et
  dokumentert offentlig endepunkt er en måling, ikke et bygg.
- **Ingen endring i `atlas_dekning.json`.** Status og begrunnelse er menneskets
  stillingtagen; jeg har målt den, ikke flyttet den.
- **Ingen endring i `mast-konnektor.py`.** Den ligger i et annet repo og er
  lest, ikke rørt.
- **Ingen kanonendring, ingen DOI, ingen merge.** Landing er menneskeord.

## 9. Sidefunn fra samme ref — målt, men utenfor denne rundens dom

Disse ble målt av kjøringen og legges her fordi de ellers forsvinner. De er
**ikke** vurdert, og de er **ikke** en del av evidensdommen over C1–C5.

1. **«32 av 40 kilder med 0 lesere og 0 eiere» er nå 32 av 38.** Samme 32,
   færre kilder i målingen. Kortet siterer 40 fra 2026-09-19; `atlas_kilder.py`
   gir 38 ved `22438ec9`.
2. **MAST/CAOM har fått lesere, men ingen eier.** `lesere:
   ["kosmos.interstellart","kosmos.stjerner"]`, `eiere: []`. Kildeaksens egen
   dokumentasjon sa «174 meldinger, 0 lesere, 0 eiere» (målt 2026-09-18); nå er
   tallet 1 069 meldinger og to lesere. Kildeaksen har flyttet seg uten at noen
   node eier kilden.
3. **Dekningens begrunnelse og konnektorens kode sier ikke det samme.**
   `atlas_dekning.json` skriver: «kildens egen taksonomi skiller dem (exoplanet
   før planetsystem). Vi leser den, vi lager den ikke.» Konnektoren sier: «Domenene,
   i PRESEDENSREKKEFØLGE. Første treff vinner — og rekkefølgen ER beslutningen.»
   *Merkelappene* er kildens; *grupperingen og rekkefølgen* er vår. Begge
   setningene kan være sanne, men bare den ene står i dekningsfilen, og den
   som står der, tilskriver kilden en grense vi selv trekker.
4. **`planetsystem` bærer 2 471 meldinger, `exoplanet` 63** — 39× forskjell,
   med samme kilde og samme klassefelt. Om det er kildens taksonomi eller vår
   rekkefølge som gjør det, er ikke avgjort her.

---

## 10. Readback — utført av en annen kontekst, med rettinger

Readbacken ble kjørt av en isolert kontekst som **bare** fikk inngangen
(artefaktets sti + de deterministiske kommandoene + API-beina), ikke min
konklusjon. Dens fulle svar ligger ved i `2026-09-21-kosmos-exoplanet-vedlegg.md`.

**Dens epistemiske vekt, sagt med en gang:** uavhengig *kontekst*, ikke
uavhengig *modell*. Det er en annen lesning, ikke en annen part.

**Reprodusert av readbacken:** alle tall i §1 (39 domener; `ikke_dekket`; 63
meldinger; 0 noder; emnet `observasjon.mast-caom`; 6 banktreff; kilden 1 069
meldinger over 6 domener med 2 lesere og 0 eiere; andelen 63/1 069 = 5,9 %),
konnektorens md5, begge DOI-ene mot Crossref (ApJS 254/39/2021; ARA&A
53/409-447/2015), nasa.gov-tallene og alle NEA-tallene, N1 (eksplisitt
avvisning) og N4 (atlaset vet ikke). Den bekreftet også at den eksakte
API-spørringen gir 16 rader med `image` som eneste `dataproduct_type`.

**Der readbacken tok feil — og hvordan jeg vet det:** den meldte at N2 og N3
(oppdiktet parameter og oppdiktet kolonne) ble **eksplisitt avvist**, likt N1.
Det er ikke hva endepunktet gjør. Målt på nytt, to ganger, i to former:

```
# form 1: urlencode i kroppen          # form 2: curl -sSG --data-urlencode
$ python3 n23.py                        $ curl -sSG --data-urlencode "request=…"
N1b ekstra parameter -> COMPLETE, 16 rader, entropi-nøkkel i raden: False
N1c ekstra kolonne   -> COMPLETE, 16 rader, entropi-nøkkel i raden: False
N1a oppdiktet tjeneste -> ERROR «Unable to Locate Adaptor for service: Mast.Caom.Entropi»
```

Readbackens egen logg viser en `for svc in Cone Entropi`-løkke rundt nettopp
disse kallene, og dens egen tidligere kjøring ga `status COMPLETE rows 16`.
Feilen ligger altså i readbackens egen konstruksjon — tjenestenavnet fra en
løkkeiterasjon havnet på de to andre kallene — ikke i endepunktet.
**Meta-funnet, og det er det varige:** en readback som ikke skriver ut den
eksakte forespørselen den sendte, kan ikke skjelnes fra sin egen
konstruksjonsfeil. Kravet heretter: readbacken skal ekko forespørselen ved
siden av svaret. Uten det er en «avvik»-rapport ubrukelig — den kan være
målerens feil.

**To rettinger fra readbacken er tatt inn i teksten (begge er reelle):**

1. **B3 var for sterkt.** Dokumentasjonen navngir tjenesten `Mast.Caom.Cone`;
   at CAOM *er* spørrelaget ble ikke vist av den kilden alene. Feltet i §3 er
   skrevet om til det kilden faktisk bærer. Det bredere kravet bæres av min
   egen lesning, og står nå der.
2. **«Tre visninger av én linje» var upresist.** A1, B1 og B2 måler *ulike
   populasjoner* (2 241 kandidater, «mer enn 6 000», 6 366) og kan derfor
   verken støtte eller motbevise hverandre. Det de deler er arv — data, kode,
   institusjon. Setningen i §4 sier nå det i stedet.

**Ubestridt, men ikke reproduserbart — og det står ved:** N5 og
positivkontrollen hviler på et søk i et levende indeks. Readbacken kunne ikke
gjenta dem, og det er riktig innvendt: det ER ikke reproduserbart. Det som nå
er lagt inn, er den eksakte spørrestrengen, slik at uenighet kan gjelde
*treffene* og ikke hva som ble spurt.

### Andre mening — to panelister, og hva som ble tatt inn

Panelet fikk et nøytralisert spørsmål: fakta og påstander, ingen av mine
konklusjoner, ingen ledende ord. Begge svarte med verifisert modell-id.

| runde | modell (`model_verified`) | dom | konfidens |
|---|---|---|---|
| 1 | `gpt-5.6-luna` (true) | **BLOCK** | 0,91 |
| 2 (eskalert etter stigen: BLOCK er grunn alene) | `claude-opus-5` (true) | **PASS** | 0,78 |

Hele svarene ligger i vedlegget. Det jeg tok inn:

1. **C2 deles** i kjede (`observert`) og institusjon (`ukjent`). Panelet fant en
   reell motsetning mellom A1 og B2 som jeg hadde skrevet bort: A1 sier
   kandidatkatalogen ligger *på MAST*, mens B2 henter til arkivets egen tabell.
   Uavklart er det ærlige svaret.
2. **C5 nedgraderes** til et *avgrenset* fravær. Et universelt negativ kan ikke
   etableres av et søk; det er nå to påstander med hver sin status.
3. **C4 får rutingleddet inn i selve påstanden** — ikke som fotnote, men som
   tredje årsaksledd.
4. **F1 er en stråmann** og er flyttet ut av falsifikatorsettet. Riktig innvendt:
   en avgrensning velger rader, den kan ikke legge til kolonner.
5. **Uavhengighetstallet for C1** er rettet til «1 ekstern + 1 intern». API-svaret
   og konnektorens kode er komplementære, ikke to bekreftelser.

Det jeg **avviste, fordi det ble målt**: panelet antok at en *tidligere* domene
kan stjele exoplanet-rader, og at C4 dermed tilskriver himmelen et
konnektorartefakt. `exoplanet` står først i `DOMENER` — ingenting står foran —
og målingen i §4 gir 12 → 0 i den *motsatte* retningen. Presedensen er en
drivkraft av første orden, akkurat som panelet sa; men den skjærer domenet *ut
av* stjernedomenet, den skjuler det ikke bak et tidligere domene.

Panelets høyest rangerte test («permuter domenelisten og se om andelen flytter
seg») er dermed **kjørt**, med konnektorens egen kode: den flytter seg totalt.

---

## 11. Maskinlesbar kjerne

```json
{"runde": "2026-09-21", "kort": "t_a0e3260f", "ref": "origin/main@22438ec9",
 "gap": {"domene": "kosmos.exoplanet", "status": "ikke_dekket", "meldinger": 63,
         "noder": 0, "emner": ["observasjon.mast-caom"],
         "atlas_svar": {"domene": "KJENT HULL", "emne": "ATLASET VET IKKE"}},
 "kilde": {"navn": "MAST/CAOM", "meldinger": 1069, "domener": 6,
           "lesere": 2, "eiere": 0, "andel_exoplanet": 0.059},
 "kildeklasser": {"a_faglitteratur": 2, "b_primarkilde": 4, "huset_primar": 1},
 "uavhengige": {"C1": "1 ekstern + 1 intern", "C2a": 1, "C2b": 0,
                "C3": 1, "C4": 1, "C5a": 1, "C5b": 0},
 "status": {"C1": "observert", "C2a": "observert", "C2b": "ukjent",
            "C3": "observert", "C4": "tolket", "C5a": "observert",
            "C5b": "ukjent", "node_forslag": "hypotese",
            "negativkontroll_mal": "ukjent"},
 "kontrafaktisk": {"vindu_mjd": [61302.251, 61304.251], "rader": 366,
                   "fordeling": {"uklassifisert": 221, "hoper": 60, "stjerner": 34,
                                 "interstellart": 27, "galakser": 12, "exoplanet": 12},
                   "flerdomene_rader": 99, "exoplanet_forst": 12, "exoplanet_sist": 0,
                   "funnet": "domenet er skaaret ut av stjernedomenet av vaar egen rekkefoelge"},
 "panel": [{"modell": "gpt-5.6-luna", "model_verified": true, "dom": "BLOCK", "konfidens": 0.91},
           {"modell": "claude-opus-5", "model_verified": true, "dom": "PASS", "konfidens": 0.78,
            "eskalert": "BLOCK er grunn alene (stigen)"}],
 "negativkontroll": {"bein": 5, "ok": 3, "feiler_aapent": 2,
                     "laert": "200 COMPLETE er ikke bevis for at et felt finnes"},
 "readback": {"av": "isolert kontekst (annen, ikke uavhengig modell)",
              "reproduserte": "alle tall i §1, md5, begge DOI mot Crossref, NEA, N1, N4",
              "readbackens_feil": "meldte N2/N3 som eksplisitt avvist; målt på nytt i to former: begge COMPLETE, nøkkelen ikke i raden",
              "aarsak": "readbackens egen for svc-løkke lakk tjenestenavnet; dens egen logg viser løkka",
              "meta_funn": "readback skal ekko den eksakte forespørselen — ellers kan den ikke skjelnes fra sin egen konstruksjonsfeil",
              "rettinger_tatt_inn": ["B3 nedtonet til det kilden bærer",
                                     "«tre visninger av én linje» -> tre ledd, ulike populasjoner"],
              "ikke_reproduserbart_ved_design": ["N5", "positivkontrollen"]},
 "rolle_funn": {"epistemisk": "konsensus er observatørvariabel, ikke sannhet",
                "svakeste_ledd": "target_classification + vår presedensrekkefølge",
                "entropitype": "ingen — og det er svaret"},
 "grenser": ["ingen bankskriving", "ingen ny konnektor", "ingen scheduler",
             "ingen vakt", "ingen endring i atlas_dekning.json",
             "ingen endring i mast-konnektor.py"],
 "falsifikator": {"F1": "CAOM-rad bærer planetens fysiske parametre",
                  "F2": "andelen følger en fysisk fordeling, ikke allokeringen"},
 "gjort_av": "researcher", "lest_tilbake_av": "vedlegg"}
```
