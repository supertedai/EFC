# Vedlegg til runden 2026-09-21 — `kosmos.exoplanet`

Dette er **revisjonsmaterialet til kortet** `t_a0e3260f`, ikke atlasinnhold:
en uavhengig lesning (readback), panelets svar (andre mening), og min
arbitrering av begge. Hovedartefaktet er `2026-09-21-kosmos-exoplanet.md`.

Ingenting her er skrevet inn i `schema/regime_nodes.jsonld` eller i
`atlas_dekning.json`.

---

## A. Readback — uavhengig kjørt lesning

**Hvem:** en isolert kontekst som bare fikk inngangen (artefaktets sti, de
deterministiske kommandoene, API-beina). Den fikk ikke min konklusjon.
**Epistemisk vekt:** uavhengig *kontekst*, ikke uavhengig *modell*.
**Varighet:** 60,5 s. **Fullførte verktøykall:** 9 (1 lesing, 3 terminal, 5 kode).

### A.1 Dens egen tabell

| påstand | dom | observert |
|---|---|---|
| 39 domener i skjemaet | reproduced | 39 |
| `kosmos.exoplanet` = `ikke_dekket` | reproduced | ikke_dekket |
| 63 meldinger | reproduced | 63 |
| 0 noder, ett emne `observasjon.mast-caom` | reproduced | 0 noder; ett emne |
| emnet: ingen node, 6 banktreff | reproduced | ingen node; 6 treff |
| volumet: 63 for domenet | reproduced | 63 |
| kilden MAST/CAOM: 1 069 meldinger | reproduced | 1069 |
| kilden dekker 6 domener | reproduced | 6 |
| 2 lesere, 0 eiere | reproduced | interstellart + stjerner; eiere [] |
| andelen 63/1 069 ≈ 5,9 % | reproduced | 63/1069 = 5,893 % |
| konnektorens md5 | reproduced | 7c2278d5bbc79d7ba8e46687f78c197c |
| A1: 2 241 kandidater | reproduced | 2241 |
| A1: ApJS 254, s. 39, 2021 | reproduced | ApJS 254/39/2021 |
| A2: ARA&A 53, 409-447, 2015 | reproduced | ARA&A 53/409-447/2015 |
| B1: «more than 6,000» | reproduced | samme |
| B2: 6 366 · 4 708 · 1 200 · 97 · 289 · 2 787 · 1 936 · 8 148 · 4 833 | reproduced | alle ni |
| B3: `Mast.Caom.Cone` er CAOMs spørrelagetjeneste | **not_reproducible** | «the broader statement … was not established by this response alone» |
| N1 oppdiktet tjeneste | reproduced | ERROR: Unable to Locate Adaptor |
| N2 oppdiktet parameter | **differs** | meldte ERROR, ikke COMPLETE |
| N3 oppdiktet kolonne | **differs** | meldte ERROR, ikke COMPLETE |
| N4 oppdiktet emne | reproduced | no node, 0 treff, ingen motor, ingen bussrute |
| N5 oppdiktet påstand | **not_reproducible** | ingen deterministisk kommando oppgitt |
| positivkontrollen | **not_reproducible** | samme grunn |
| tallet 5 bein / 3 OK / 2 feiler åpent | **differs** | «N2 and N3 both returned explicit service errors» |

### A.2 Dens innvendinger, ordrett (kortet)

- «The artifact claims N2 and N3 silently returned COMPLETE, but the exact
  rerun returned the same explicit adaptor error as N1 for both.»
- «The artifact treats A1's 2241 TESS candidates, B1's more-than-6000 confirmed
  exoplanets, and B2's 6366 confirmed exoplanets as three views of one line,
  but these are different populations and measures.»
- «The artifact's section 5 says N2/N3 are silent-ignore cases, while the
  current exact calls show explicit rejection, so the report is stale relative
  to the live endpoint.»

### A.3 Min arbitrering av readbacken

| # | innvending | dom | grunnlag |
|---|---|---|---|
| 1 | N2/N3 ga ERROR, ikke COMPLETE | **avvist (målt)** | readbackens egen logg viser `for svc in Cone Entropi`; dens egen tidligere kjøring ga `status COMPLETE rows 16`. Kallene ble kjørt på nytt to ganger i to former: begge `COMPLETE`, 16 rader, `entropi`-nøkkel finnes ikke i raden |
| 2 | A1/B1/B2 er ulike populasjoner | **akseptert (delvis)** | riktig at de ikke måler én størrelse. Formuleringen i §4 sa «tre visninger av én linje» og lovet mer enn det; den er skrevet om til «tre ledd av én linje», med populasjonene navngitt |
| 3 | B3 ikke reproduserbar | **akseptert** | dokumentasjonen navngir tjenesten; at CAOM *er* spørrelaget ble ikke vist av den kilden alene. §3-feltet er nedtonet |
| 4 | N5/positivkontrollen ikke reproduserbare | **akseptert, med forbehold** | de er ikke deterministiske — det var kjent og står i §7. Den eksakte spørrestrengen er nå lagt inn så uenighet kan gjelde treffene, ikke spørsmålet |

**Meta-funnet, og det er det varige:** readbacken rapporterte et «avvik» som
var dens egen konstruksjon — tjenestenavnet fra en løkkeiterasjon lakk inn i
de to andre kallene. Den skrev ikke ut forespørselen den sendte, så dens
avvik kunne bare skilles fra virkeligheten ved å kjøre etter den. Kravet
heretter: **readbacken skal ekko den eksakte forespørselen ved siden av
svaret.** Uten det er en avviksrapport verdiløs — den kan være målerens feil.

---

## B. Andre mening — spørsmålet, ordrett

Nøytralisert: fakta og påstander, ingen av mine konklusjoner, ingen ledende
ord. Fila ble skrevet til scratch og er gjengitt her i sin helhet, fordi et
panelsvar uten spørsmålet ikke kan leses.

```markdown
# Panel question — assessment of an evidence grading

You are assessing a measurement report. You have not seen the author's reasoning; the
claims and the measured facts are below. Judge the grading, do not rewrite the report.

## Setting

A repository keeps a "coverage map" for a message bus. One domain, `kosmos.exoplanet`,
is declared `ikke_dekket` ("not covered"): 63 bus messages, zero graph nodes, one bus
subject `observasjon.mast-caom`. The messages come from a connector that polls the
public MAST/CAOM archive API (STScI) for newly released observations and routes each
row into one domain by matching a regular expression against the row's
`target_classification` field. Domain order is precedence order: first match wins.

## Measured facts

1. A CAOM cone query around a known exoplanet host (TRAPPIST-1) returned 16 rows.
   Columns present: obs_collection, instrument_name, dataproduct_type (all 16 = "image"),
   calib_level, s_ra/s_dec, t_min/t_max, t_exptime, obs_id, target_name,
   target_classification, proposal_pi. No column carries a planet's radius, period, mass,
   transit depth, or temperature. Rows from several surveys (TESS, K2, PS1, GALEX, SDSS)
   appeared for the same sky position.
2. The connector's source code states the row is an "observation" ("the archive wrote
   down what happened; nobody judged it"), that the classification fields it carries are
   the source's own judgements, and that the connector's domain list is in precedence
   order and that "the order IS the decision".
3. A peer-reviewed catalogue paper (ApJS 254, 39, 2021) states the TESS data products,
   including the candidate catalogue, light curves and pixel files, are publicly available
   on MAST. A peer-reviewed review (ARA&A 53, 409, 2015) covers orbits, eccentricities and
   host-star spin-axis orientation.
4. Institutional pages (NASA Exoplanet Archive counts; a nasa.gov page) report 6366 and
   "more than 6000" respectively; the peer-reviewed catalogue reports 2241 candidates.
   All three derive from the same mission pipelines and the same institutions
   (pipeline -> MAST -> IPAC archive -> NASA narrative).
5. A negative control on a fabricated target (a claimed per-observation "entropy gradient"
   field in CAOM) found zero supporting sources. A fabricated service name is explicitly
   rejected by the API; a fabricated parameter or column is silently ignored and the API
   still answers "COMPLETE" with ordinary rows and no such key.

## Claims to assess

- C1 (graded "observed"): the bus subject carries observation metadata (pointing, time
  window, instrument, calibration level), not a measured quantity of a planet.
- C2 (graded "observed"): the planet's physical parameters live in a different chain
  (candidate/planetary tables) and at a different institution than the archive metadata.
- C3 (graded "observed"): the domain boundary is produced by the connector's own regular
  expression and its precedence order applied to the source's label field, not by a
  natural line in the source.
- C4 (graded "interpreted"): the domain's share therefore measures observation practice
  (who pointed where, and when it became public) rather than planetary physics.
- C5 (graded "observed"): no external source connects these observations to an entropy
  production or entropy gradient. The proposed node for the domain is graded "hypothesis".
- Independence count reported: 2 independent sources for C1, 1 for each of C2, C3, C4, C5.

Stated falsifiers for C4: (F1) a CAOM query restricted to exoplanet classes returns rows
already carrying the planet's physical parameters; (F2) the share over time tracks a
physical distribution rather than telescope allocation and the release window.

## What I want

1. For each of C1-C5: is the assigned grade defensible, too strong, or too weak? Say
   which and why in one or two lines each.
2. Is C4 supported by the facts, over-claimed, or under-claimed?
3. What evidence would change your mind about C4? Be concrete.
4. An explicit confidence in your assessment, 0.00-1.00 (an unmeasurable confidence is
   not an answer).
5. End with a line: `VERDICT: PASS` or `VERDICT: BLOCK`.
```

---

### B.1 Kanalens bokføring — hvilken kjøring vedlegget gjengir

Spørsmålet over (blokken mellom ```` ```markdown ```` og ```` ``` ````, 4 168
byte over 67 linjer) ble skrevet til scratch og sendt som fil. Kallene gikk
gjennom `claude_opus_api.py` **med `--kort t_a0e3260f`** — det flagget er det
som får kanalens eget spor til å lande i `/opt/opus-ledger/andremening.jsonl`:

```
python3 claude_opus_api.py --prompt-file panelsporsmal-t_a0e3260f.md \
    --kort t_a0e3260f --max-tokens 10000
python3 claude_opus_api.py --eskaler --dom block \
    --prompt-file panelsporsmal-t_a0e3260f.md --kort t_a0e3260f --max-tokens 10000
```

Ledgeren bærer nå én **skriptskrevet** linje per kall (feltene er kanalens,
ikke mine):

```
{"ts": 1789972052.4276996, "kort": "t_a0e3260f", "modell": "gpt-5.6-luna", "modell_verifisert": true, "bruk": "panel", "rute": "openai", "svar_lengde": 3199}
{"ts": 1789972125.9047637, "kort": "t_a0e3260f", "modell": "claude-opus-5", "modell_verifisert": true, "bruk": "panel", "rute": "anthropic", "svar_lengde": 5409}
```

**Dette er kjøring 2** (heretter «kjøring 1» og «kjøring 2» om de to
panelkjøringene — hver kjøring rommer begge panelistene). Kjøring 1 ble gjort
uten `--kort`, altså uten spor: den fantes bare som prosa i dette vedlegget, og
prosa er en selvrapport. Kjøring 1s to svar står i git-historikken (`48faaf7f`);
D.1 stiller de to kjøringene mot hverandre punkt for punkt. Selve spørsmålet er
uendret — samme fil, samme byte, samme sha256.

---

## C. Panel — `gpt-5.6-luna` (panelkjøring 2, den ledgerførte)

Proveniens fra svaret: `{"ok": true, "provider": "openai", "model":
"gpt-5.6-luna", "model_requested": "gpt-5.6-luna", "model_verified": true,
"bruk": "panel", "route": "openai", "http_status": 200, "id":
"chatcmpl-EQRmbtGI9akR8QrEK1LLNSMetzIyX"}` — modell-id-en er API-ets eget
ekko, ikke vår anmodning. Bruk: 1 003 inn / 1 620 ut (hvorav 1 024
resonneringstokens).

> 1. **C1 — observed: defensible.** The returned columns and connector description directly establish that the payload contains observational metadata, with no planetary physical parameters.
>
> 2. **C2 — observed: too strong.** The facts support that the CAOM rows lack those parameters and that candidate/planetary data are a separate data product or chain. They do not establish that the physical-parameter data come from a different institution; the cited material instead shows substantial institutional and pipeline continuity.
>
> 3. **C3 — observed: defensible, with a minor qualification.** The source code directly establishes regex matching and precedence-order routing. “Not a natural line in the source” is an interpretation of that mechanism, but is a reasonable one given the arbitrary connector-controlled boundary.
>
> 4. **C4 — interpreted: too strong.** The facts support that the measured share is a share of routed archive observations and is affected by targeting, release timing, and connector classification. They do not show that it measures those factors *rather than* planetary physics, especially without a share analysis or controls for selection effects.
>
> 5. **C5 — observed: too strong.** The negative control supports that the proposed field is unsupported and that fabricated API details are unreliable, but it does not demonstrate an exhaustive absence of external connections to entropy-related quantities. “No connection was found in the searched sources” would be defensible; the unqualified negative is not.
>
> **C4 overall:** It is **over-claimed**, not wholly unsupported. Its descriptive premise is sound, but the causal/semantic conclusion that the share measures observation practice rather than planetary physics requires evidence beyond the row schema and routing logic. F1 would be a strong challenge, while F2 is directionally appropriate but needs a specified statistical test and controls.
>
> Evidence that would change my mind would include:
>
> - A documented join from the CAOM observations to candidate/planet tables containing radius, period, mass, temperature, or transit depth, with those parameters actually present in or deterministically recoverable from the bus payload.
> - A time-series analysis of domain share controlling for telescope, instrument, sky coverage, observing cadence, survey, and release latency, showing a robust relationship to a physical-parameter distribution rather than to allocation or publication effects.
> - Conversely, a matched analysis showing that the share is fully explained by targeting and release processes, with no residual relationship to planetary properties, would substantially strengthen C4.
> - Evidence that connector classification is based on a physically defined exoplanet taxonomy rather than a source label and regex would also weaken the stated interpretation.
>
> The independence count is questionable where sources share the same mission pipelines and institutional chain. Those sources may corroborate one another, but they should not automatically be counted as independent evidence; C5 in particular has no demonstrated independent external support in the supplied facts.
>
> **Confidence: 0.91**
>
> VERDICT: BLOCK

---

## D. Panel — `claude-opus-5` (eskalert i panelkjøring 2, den ledgerførte)

Proveniens: `{"ok": true, "provider": "anthropic", "model": "claude-opus-5",
"model_requested": "claude-opus-5", "model_verified": true, "bruk": "panel",
"route": "anthropic", "http_status": 200, "id":
"msg_011CfG7MaPdUTHLDZ5oVwDQF"}`. Bruk: 1 505 inn / 4 445 ut (hvorav 2 610
tenketokens). Eskalert etter stigen: `BLOCK` er grunn alene (uavhengig av
konfidens). Begge panelister står i protokollen; en eskalering erstatter ikke
en kjøring.

> ## 1. Grade-by-grade
>
> **C1 — "observed": defensible.**
> The column inventory of a real CAOM response is a direct measurement, and the absence of radius/period/mass/depth/temperature is a property of the schema, not of the sample. Minor weakness: it rests on one cone query (n=16, one target) used as a proxy for the 63 actual messages; the CAOM schema is fixed, so the extrapolation is cheap, but a census of the 63 payloads would make it airtight.
>
> **C2 — "observed": too strong, and partly contradicted by your own fact.**
> Fact 3 says the TESS *candidate catalogue* is publicly available **on MAST** — i.e. same institution (STScI). Only the parameters table (NASA Exoplanet Archive / IPAC) supports the "different institution" clause. "Different table/product chain" is observed; "different institution" is an inference that the evidence half-refutes. Split it, or downgrade the institutional clause to "interpreted". Fact 4's own note — all three numbers share pipelines and institutions — cuts the same way.
>
> **C3 — "observed": defensible, arguably the strongest claim in the set.**
> Reading the connector's source is the best available evidence for what the connector does, and the code says it outright ("the order IS the decision"; the classification fields are the *source's* judgements). Fact 1 (five surveys at one sky position) independently corroborates that the boundary can't be a natural line in the sky. Independence of 1 is conservative here; 2 would be defensible.
>
> **C4 — "interpreted": correct grade.**
> It is a conclusion assembled from C1 + C3, not a measurement; no time series of the 63 messages was examined and the "when it became public" half is entirely unmeasured. "Observed" would have been wrong; "hypothesis" would have been too weak given C1/C3 are solid.
>
> **C5 — "observed": defensible only under the scoped reading.**
> "Our search returned zero supporting sources" is a measured fact; "no external source connects these" as a universal is unmeasurable. Re-word to the search-scoped form. The negative control is the good part: the API silently ignoring a fabricated column while still returning "COMPLETE" means a naive confirmation query would have produced a false positive, and the report caught that. Grading the proposed node "hypothesis" is right (I'd accept "unsupported").
>
> **Independence counts:** honest overall. C1's "2" is slightly generous — the API response and the connector's self-description are different artifacts but the code comment is an assertion by the system under audit, not a second measurement of the payload. C2's "1" is correctly conservative given the shared pipeline→MAST→IPAC→NASA provenance.
>
> ## 2. Is C4 supported?
>
> Supported at the grade assigned, with one over-reach and one under-evidenced half. Over-reach: "rather than planetary physics" read exclusively — target selection is itself partly physics-driven (who gets pointed at is not random with respect to what's there), so the honest form is "dominated by observation practice." Under-evidenced: the "when it became public" clause has no measurement behind it at all; nothing in facts 1–5 touches release timing. The core — that a share computed over rows containing only pointing/time/instrument, partitioned by a locally-authored regex in a precedence list, cannot be a physical quantity — is well carried by C1 and C3.
>
> ## 3. What would change my mind about C4
>
> - **Run F1 concretely:** a CAOM query filtered to exoplanet-ish `target_classification` values, checked for any column carrying `pl_rade`/`pl_orbper`/depth/mass. If such columns appear, C1 collapses and C4 with it. (Prediction: they won't — CAOM has no such fields — so this is a cheap, near-certain-to-fail test; that is what makes it a good falsifier to have *stated*.)
> - **Run F2 with a real series:** bin the 63 messages by `t_min` and by public-release date against TESS sector boundaries and proposal-cycle allocation. Correlation with sector/release cadence confirms C4; a share tracking, say, a planet-radius or period distribution independent of allocation refutes it.
> - **Census the 63 messages' `target_classification` values.** If the regex is in fact matching a field that the source populates from a physical determination (not a survey-desk label), C3 weakens and C4 becomes over-claimed.
> - **A counter-example to the precedence claim:** evidence that reordering the domain list leaves the assignment of these 63 rows unchanged would show the boundary is not regex-order-produced after all.
> - **For C2 specifically:** confirm whether the connector could reach the candidate catalogue *on MAST* — if yes, the "different institution" framing must go.
>
> ## 4. Confidence
>
> **0.78.** High on C1/C3/C4 (the schema and code facts are dispositive); the residual uncertainty is concentrated in C2's institutional clause and in whether the 16-row proxy faithfully represents all 63 messages.
>
> ## 5. Disposition
>
> The one real defect (C2's institution clause, contradicted by fact 3) is localised, does not propagate into C4, and is fixable by splitting the claim. The headline inference is correctly hedged and carries two concrete, runnable falsifiers, and the negative control is properly constructed.
>
> Required amendment before publication: split C2 into "different table/product chain" (observed) and "different institution" (interpreted, partly contradicted); re-word C5 to the search-scoped form.
>
> VERDICT: PASS

---

## D.1 Stabilitet — kjøring 1 mot kjøring 2, punkt for punkt

Begge kjøringer svarte på den samme filen, med de samme fakta og de samme
påstandene. Det som er likt, er reprodusert. Det som ikke er likt, skal ikke
leses som om det var det.

| punkt | kjøring 1 | kjøring 2 | stabilt |
|---|---|---|---|
| `gpt-5.6-luna` dom / konfidens | BLOCK / 0,91 | BLOCK / 0,91 | **ja** |
| `claude-opus-5` dom / konfidens | PASS / 0,78 | PASS / 0,78 | **ja** |
| C1 | defensible (begge) | defensible (begge) | ja |
| C2 for sterkt — del kjede fra institusjon | begge ba om delingen | begge ba om delingen | ja |
| C3 holdes | begge | begge (Luna med ett forbehold: «ikke en naturlig grense» er tolkning) | ja |
| C5 er et universelt negativ | Luna: for sterkt. Opus: for sterkt | Luna: for sterkt. Opus: holdbar *bare* i den avgrensede formen | ja, i retning |
| C1s uavhengighetstall | Opus: 1 ekstern + 1 intern | Opus: samme — kodekommentaren er «an assertion by the system under audit» | ja |
| C4 mangler rutingleddet | Opus: en *tidligere* domene kan stjele radene | **ikke sagt**, i noen av svarene | **nei** |
| F1 dekorativ | Opus: «half the falsifier set is decorative» | Opus: billig test som nesten sikkert ikke kan fyre, «that is what makes it a good falsifier to have stated». Luna: «would be a strong challenge» | **nei — snudd** |
| C4: «rather than planetary physics» lest eksklusivt | ikke sagt | Opus: for sterkt — målutvelgelse er selv delvis fysikkdrevet | kun kjøring 2 |

**Hva dette sier, og ikke sier.** Dommen og konfidensen ligger fast mellom to
kjøringer; det gjør også de fleste punktene i arbitreringen (F). To punkter er
ikke stabile, og begge er håndtert i hovedartefaktet:

1. **C4s rutingledd.** Kjøring 1s `claude-opus-5` påstod at en *tidligere*
   domene kan absorbere exoplanet-radene. Kjøring 2 sier det ikke. Påstanden
   ble målt i §4, og målingen ga det motsatte utfallet — `exoplanet` står
   først, og domenet ville hatt 0 rader hvis det stod sist. Leddets plass i
   §4 hviler derfor på **målingen**, ikke på sitatet; panelet pekte på at
   rekkefølgen kunne være en drivkraft, og det holder i begge kjøringer.
2. **F1.** Kjøring 1 ba om at den ble tatt ut; kjøring 2 behandler den som en
   billig test som er verdt å ha stilt. Begge er enige om *hvorfor den nesten
   ikke kan fyre* (en avgrensning legger ikke til kolonner i et fast skjema).
   F1 er ført tilbake til falsifikatorsettet som *stilt, skjemastengt* (§4):
   merkelappen snudde, utfallet gjorde det ikke.

Det er verdt å si rett ut hva dette betyr for prosedyren: **en andremening er
en måling av et svar, ikke av en sannhet.** To kjøringer av de samme modellene
på de samme fakta er to lesninger, ikke to vitner. At *dommen* er stabil sier
at spørsmålet ikke er støyfølsomt. At to *begrunnelser* ikke er det, sier at
en begrunnelse ikke kan siteres som en fasit. Kravet heretter: gjengi kjøringen
med ledgerlinja si, og hold «panelet sa» atskilt fra «jeg målte».

---
## E. Arbitrering — punkt for punkt

| # | panelets punkt | dom | tag | kjøring 2 bærer? | hvorfor |
|---|---|---|---|---|---|
| 1 | C2 for sterkt: del kjede fra institusjon | **akseptert** | L0 | ja, begge | A1 sier kandidatkatalogen ligger på MAST; B2 henter til arkivets egen tabell. Motsetningen er reell og uavklart → `ukjent` |
| 2 | C5 er et universelt negativ | **akseptert** | L0 | ja (Luna: for sterkt; Opus: holdbar bare avgrenset) | et søk kan ikke lukke en ubegrenset korpus. Delt i C5a (`observert`) og C5b (`ukjent`) |
| 3 | C4 mangler rutingleddet | **akseptert, og målt** | L0 | **nei** — påstanden er kjøring 1s | panelet sa «en tidligere domene kan absorbere radene». Målt: `exoplanet` står først; retningen er motsatt, og effekten er total (12 → 0). Leddets plass i §4 hviler på målingen, ikke på sitatet |
| 4 | F1 er dekorativ | **snudd i kjøring 2** | L1 | nei — kjøring 2 sier det motsatte | begge kjøringer er enige om at F1 nesten ikke kan fyre (en avgrensning legger ikke til kolonner). F1 er **ført tilbake** til settet, merket *stilt, skjemastengt* (§4) |
| 5 | C1: «2 kilder» er komplementære | **akseptert** | L1 | ja, begge | svaret og koden svarer på to ulike spørsmål. Rettet til «1 ekstern + 1 intern» |
| 6 | C4s tidsinnhold er ikke målt | **akseptert** | L0 | ja, begge (Opus: «nothing in facts 1–5 touches release timing») | ingen serie er kjørt. Står nå som «ikke målt», ikke som «målt» |
| 7 | C3 holdes | **akseptert** | L0 | ja, begge | både kode og måling bærer den |
| 8 | C1 holdes | **akseptert** | L0 | ja, begge | skjemaet er et faktum, ikke et utvalg |
| 9 | «rather than planetary physics» lest eksklusivt er for sterkt | **akseptert** | L1 | kun kjøring 2 | målutvelgelse er selv delvis fysikkdrevet. §4 sier nå «dominert av», ikke «uttømmende» |

**Meta-punktet panelet reiste og som jeg tok inn:** «the report errs conservative
where it counts» er ikke en attestasjon på at konklusjonen er *sann* — den er en
vurdering av *retningen* på feilene. Det står slik i artefaktet, ikke som støtte.

**Samlet:** konklusjonen endres ikke — gapet er fortsatt et målt hull uten node,
og den foreslåtte noden står som `hypotese`. To statuser er **svekket** (C2
delt, C5 avgrenset), én påstand er **skjerpet** (C4 med rutingleddet, nå målt),
og én falsifikator er **tatt inn igjen med sperren navngitt** (F1: kjøring 2
snudde merkelappen, ikke utfallet). Ingen av dem velter en konklusjon; alle er
rettet i filen.

**Ett forbehold til protokollen:** ni punkter, og to av dem bæres av bare én av
to kjøringer. Det er ikke et argument mot panelet — det er argumentet *for*
ledgerlinja: hadde kjøring 1 vært det eneste sporet, ville F1-avgjørelsen stått
som «innvendt av panelet» uten at noen kunne se at den ikke reproduserte.

## F. Hva som gjenstår å bestemme av et menneske

1. Om `atlas_dekning.json`s begrunnelse skal stå som den er — den tilskriver
   kilden («kildens egen taksonomi skiller dem») en grense konnektorens kode
   gjør selv (`:471-479`). Status og begrunnelse er «MENNESKETS stillingtagen og
   utledes aldri»; jeg har målt, ikke flyttet.
2. Om C2b skal løses nå (hvem serverer kandidattabellen) eller parkeres.
3. Om konnektorens md5-festede rekkefølge skal inn i `stipulasjoner.terskler`
   som en navngitt terskel med verdi — eller fortsette å bo bare i koden.
