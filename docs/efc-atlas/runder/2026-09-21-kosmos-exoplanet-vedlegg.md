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

## C. Panel runde 1 — `gpt-5.6-luna`

Proveniens fra svaret: `{"ok": true, "provider": "openai", "model": "gpt-5.6-luna",
"model_requested": "gpt-5.6-luna", "model_verified": true, "bruk": "panel",
"route": "openai", "http_status": 200}` — modell-id-en er API-ets eget ekko,
ikke vår anmodning.

> 1. **C1 — observed: defensible.** The returned columns and connector
>    description directly support that the subject carries observation metadata,
>    not planetary physical parameters. The negative formulation is justified by
>    the measured schema, within the inspected data.
> 2. **C2 — observed: too strong.** The facts support that the CAOM rows do not
>    contain those physical parameters and that relevant products exist in
>    candidate/planetary data products. They do not establish that the parameters
>    are at a wholly different institution; the stated pipeline-to-archive chain
>    includes overlapping institutions and services.
> 3. **C3 — observed: defensible.** The source code explicitly documents regex
>    matching, ordered domain evaluation, and precedence. That directly supports
>    the claim that the boundary is connector-created rather than a natural
>    source partition.
> 4. **C4 — interpreted: the grade is appropriate, but the claim is
>    over-claimed.** The evidence supports the interpretation that routing is
>    strongly influenced by archive labels, telescope coverage, release timing,
>    and connector precedence. It does not yet show that the resulting domain
>    share *measures* observation practice, nor exclude all correlation with
>    planetary physics.
> 5. **C5 — observed: too strong.** The measurements show no such field or
>    connection in the examined materials, and the fabricated-field test supports
>    caution about API/schema claims. They cannot establish the universal
>    negative that no external source connects the observations to entropy
>    production or gradients. The proposed node being a hypothesis is defensible.
>
> **C4 assessment:** Over-claimed. The facts support "the current connector share
> is an observation/archive-routing signal rather than a direct measurement of
> planetary physics." They do not support the stronger causal or exclusive
> wording that it therefore measures observation practice rather than planetary
> physics.
>
> **Evidence that would change my mind about C4:** a longitudinal,
> denominator-aware analysis showing domain share versus telescope allocation,
> survey footprint, cadence, and public-release timing; a join to authoritative
> candidate/planetary tables showing whether the share tracks physical
> distributions after controlling for sky coverage, survey, instrument, and
> release date; CAOM rows carrying stable candidate/planet identifiers and
> measured physical parameters, or a documented connector rule that uses such
> parameters; a routing audit or counterfactual replay showing how often changing
> the regex or precedence order changes domain membership; evidence that the
> domain share predicts physical quantities independently of observation
> selection effects.
>
> **Confidence: 0.91**
> **VERDICT: BLOCK**

Eskalert etter stigen: `BLOCK` er grunn alene (uavhengig av konfidens).

---

## D. Panel runde 2 — `claude-opus-5`

Proveniens: `{"ok": true, "provider": "anthropic", "model": "claude-opus-5",
"model_requested": "claude-opus-5", "model_verified": true, "bruk": "panel",
"route": "anthropic", "http_status": 200}`. Begge panelister står i protokollen;
en eskalering erstatter ikke en runde.

> **C1 — "observed": defensible.** The column list from a live CAOM response is
> direct, white-box evidence, and the absence of radius/period/mass/depth is a
> schema fact, not a sampling fact, so n=16 from one cone is sufficient. One
> caveat on the bookkeeping, not the grade: the "2 sources" are the API response
> and the connector's own code, which are *complementary* (what the archive emits
> + what the connector forwards), not two independent confirmations of the same
> proposition. Report it as 1 external + 1 internal.
>
> **C2 — "observed": too strong as bundled.** The "different chain" half is
> observed. The "different institution" half is undercut by your own Fact 3,
> which says the TESS *candidate catalogue* is published on MAST, and by Fact 4's
> note that all the counts share the same institutions. Split it: chain =
> observed, institution = interpreted.
>
> **C3 — "observed": defensible.** Precedence order and regex matching are read
> directly from source, and the code's own statement that "the order IS the
> decision" is about as direct as evidence gets. The "not a natural line in the
> source" clause is carried by Fact 1's multi-survey heterogeneity at one sky
> position plus the code's admission that the classification fields are the
> source's judgements — thin but adequate.
>
> **C4 — "interpreted": correct grade, incomplete statement.** … Supported in
> direction, **under-specified in attribution**. C1–C3 license "the share is not
> planetary physics." They do not license "the share measures observation
> practice" *alone*, because C3 establishes a second driver: with
> first-match-wins precedence, any earlier domain whose regex also matches an
> exoplanet-ish `target_classification` silently absorbs those rows. The 63/zero-
> node result is therefore a joint function of telescope pointing, release
> timing, **and the connector's domain ordering**. As written, C4 attributes a
> connector artifact to the sky. Rewrite: "measures observation practice as
> filtered through the connector's regex and precedence order." Also note that no
> share-over-time series was measured at all, so C4's temporal content ("when it
> became public") is inference from the polling design, not from data.
>
> Separately: **F1 is not a risky falsifier.** Restricting a query to exoplanet
> classes selects rows, it cannot add columns to a fixed schema — F1 is close to
> a priori false and buys no information. F2 is genuinely risky and was not run.
> Half the falsifier set is decorative; say so.
>
> **What would change my mind:** the reorder test (highest value, cheapest):
> permute the connector's domain list, replay the same 63 messages, and record
> the resulting shares. If the share moves materially, the connector's precedence
> is a first-order driver and C4-as-written is wrong; if it is stable, C4's
> attribution holds. Shadow-route audit: log every row whose
> `target_classification` matched an exoplanet-ish pattern but was claimed by an
> earlier domain. F2, actually executed. A CAOM extension or joined view that
> attaches planetary parameters at the observation row level. A named institution
> check resolving Fact 3 vs Fact 4.
>
> **Confidence: 0.78.** High on C1/C3; the residual is concentrated in C2's
> institution clause, the unmeasured share-over-time behind C4, and the un-run
> reorder test.
>
> The report errs conservative where it counts: it refuses the entropy node,
> keeps independence counts low and honest, and does not upgrade an inference to
> a measurement. The defects — one bundled over-grade (C2), one universal
> negative graded as observed (C5), one missing causal term in C4, and one
> decorative falsifier (F1) — are all repairable in place and none invert a
> conclusion.
>
> **VERDICT: PASS**

---

## E. Arbitrering — punkt for punkt

| # | panelets punkt | dom | tag | hvorfor |
|---|---|---|---|---|
| 1 | C2 for sterkt: del kjede fra institusjon | **akseptert** | L0 | A1 sier kandidatkatalogen ligger på MAST; B2 henter til arkivets egen tabell. Motsetningen er reell og uavklart → `ukjent` |
| 2 | C5 er et universelt negativ | **akseptert** | L0 | et søk kan ikke lukke en ubegrenset korpus. Delt i C5a (`observert`) og C5b (`ukjent`) |
| 3 | C4 mangler rutingleddet | **akseptert, og målt** | L0 | panelet sa «en tidligere domene kan absorbere radene». Målt: `exoplanet` står først; retningen er motsatt, og effekten er total (12 → 0) |
| 4 | F1 er dekorativ | **akseptert** | L1 | en avgrensning velger rader, den legger ikke til kolonner. Flyttet ut av falsifikatorsettet |
| 5 | C1: «2 kilder» er komplementære | **akseptert** | L1 | svaret og koden svarer på to ulike spørsmål. Rettet til «1 ekstern + 1 intern» |
| 6 | C4s tidsinnhold er ikke målt | **akseptert** | L0 | ingen serie er kjørt. Står nå som «ikke målt», ikke som «målt» |
| 7 | C3 holdes | **akseptert** | L0 | både kode og måling bærer den |
| 8 | C1 holdes | **akseptert** | L0 | skjemaet er et faktum, ikke et utvalg |

**Meta-punktet panelet reiste og som jeg tok inn:** «the report errs conservative
where it counts» er ikke en attestasjon på at konklusjonen er *sann* — den er en
vurdering av *retningen* på feilene. Det står slik i artefaktet, ikke som støtte.

**Samlet:** konklusjonen endres ikke — gapet er fortsatt et målt hull uten node,
og den foreslåtte noden står som `hypotese`. To statuser er **svekket** (C2
delt, C5 avgrenset), én påstand er **skjerpet** (C4 med rutingleddet, nå målt),
og én falsifikator er **fjernet**. Ingen av dem velter en konklusjon; alle er
rettet i filen.

## F. Hva som gjenstår å bestemme av et menneske

1. Om `atlas_dekning.json`s begrunnelse skal stå som den er — den tilskriver
   kilden («kildens egen taksonomi skiller dem») en grense konnektorens kode
   gjør selv (`:471-479`). Status og begrunnelse er «MENNESKETS stillingtagen og
   utledes aldri»; jeg har målt, ikke flyttet.
2. Om C2b skal løses nå (hvem serverer kandidattabellen) eller parkeres.
3. Om konnektorens md5-festede rekkefølge skal inn i `stipulasjoner.terskler`
   som en navngitt terskel med verdi — eller fortsette å bo bare i koden.
