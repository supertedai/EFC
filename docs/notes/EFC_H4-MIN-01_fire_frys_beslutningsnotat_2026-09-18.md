# H4-MIN-01 — de fire frysene lagt fram for menneskeord

**Status**: beslutningsnotat. Skrivebordsarbeid. Ingen data åpnet, ingen prediksjon
endret, ingen fil i figshare rørt, ingen atlasendring pushet.
**Kort**: t_c37e1efc (avledet fra t_23d05721). **Dato**: 2026-09-18.
**Kildeversjon**: `/opt/agent-work/EFC` på `origin/main` `823b52e0`, lest og remålt
2026-09-18 i arbeidsgrenen `wt/t_c37e1efc`.
**Human gate**: `prereg_H4_PROP_01_v2_FINAL.json` (B1) står uendret. Dette notatet
kjører ikke oppgjøret, og det er ikke en claim-oppgradering.

Alle tall under er målt i denne kjøringen, av skriptene i §10, mot `823b52e0`.
Ingen av dem er målinger av universet. Der H4s tall ikke lot seg reprodusere, står
det eksplisitt (§1).

---

## 0. Kortets grunnlag — og én henvisning som ikke finnes

Kortet ber om EFC-H4 §6, §8 og §12. Rapporten
(`attachments/t_23d05721/EFC-H4-doi-mesh-og-minste-falsifikasjonstest.md`) har
`## 0`–`## 11` pluss Sources, Repositorium, Kjøringsartefakter og Begrensninger.
**§6 og §8 finnes og er lest**; **§12 finnes ikke**, og rapporten viser selv til en
«§13» som heller ikke finnes (linje 9: «Se §9 og §13»). Materialet bak de fire
beslutningene står i §8s siste tabell og i §6, og er lest derfra — ikke fra en §12.

Henvisningen er ikke bare en skrivefeil: den gjør at et kort kan se ut som det
hviler på et avsnitt ingen kan slå opp. Ingenting i dette notatet hviler på §12.

---

## 1. Hva som har flyttet seg siden H4 — målt, ikke antatt

H4 målte på `606b3127`. Siden da har atlaset fått tre leveranser (#491–#493).
Remålingen gir derfor andre tall på atlas-siden, og identiske tall på korpus-siden:

| Mål | H4 (`606b3127`) | Nå (`823b52e0`) |
|---|---|---|
| noder i `schema/regime_nodes.jsonld` | 82 | **89** |
| noder med `prediction` | 1 | **4** |
| noder med `settlement` | 0 | **3** |
| korpus-DOI-er (165) atlaset viser til | 9 | **10** |
| `sealed_prediction`-pakker synlige i atlaset | 1 av 14 | 1 av 14 (uendret) |
| pakker med `index.json` | 170 | 170 |
| forseglede prediksjoner | 356 | 356 |
| kill-kriterier | 774 | 774 |
| unike DOI-er | 165 | 165 |
| tester i `docs/validation-ledger/data/tests.json` | 142 | 142 |

De fire prediction-nodene er `efc.growth_engine`, `verden.vaer`, `opus.dommekraft`
og `kosmos.asteroider`; de tre settlement-nodene er de tre siste. H4s setning
«bussen gjør opp og kartet ikke ser det» er altså **delvis rettet** — men bare for
domener utenfor EFC-korpuset. For EFCs egen forseglede prediksjon står den uendret:
`efc.growth_engine` har `prediction`, **ingen `settlement`, og ingen kobling til
husets eget korrigendum VAL-006**.

**Og ett H4-tall lot seg ikke reprodusere.** H4 skriver «bare 34 av 356 forseglede
prediksjoner nevner blinding/frys/forsegling». Jeg målte tre definisjoner og fikk
tre andre tall:

| Definisjon | Målt nå |
|---|---|
| ordet «holdout» i prediksjonsteksten | 1 av 356 |
| bredt termsett (blind / frys / frossen / freeze / frozen / forseglet / sealed) i prediksjonsteksten | 18 av 356 |
| samme termsett, men en prediksjon teller også hvis termen står i pakkens kill-kriterier | 46 av 356 |

H4 oppgir ikke regex-en sin, så 34 kan ikke etterprøves. **Notatet bruker derfor
ikke 34 som faktum.** Den bærende observasjonen står uansett: andelen forseglede
prediksjoner som nevner frys, blindhet eller holdout er lav, og ordet «holdout» er
nesten fraværende — 0 treff i 142 registrerte tester, og 1 treff i 356 prediksjoner.

---

## 2. De fire beslutningene — oversikt

| ID | Beslutning | Kilde (sti i repoet) | Målt tilstand | Status |
|---|---|---|---|---|
| **D1** | Arbiterens eksakte artefakt + versjon + hash, **eller** en eksplisitt utsettelse til 2027–2028 | `schema/regime_nodes.jsonld` (`efc.growth_engine`); `tests/fixtures/nats-prediksjon-efc-fs8.json`; `docs/papers/efc/Sealed_Blind_Predictions_for_Growth_Rate_Observables_EFC_vs_LCDM/index.json`; `docs/public/EFC_Changelog.html` | kontrakten navngir «DESI DR2 full-shape»; formen finnes ikke for galakser/RSD per 2026-09-18 | **foreslått — avventer menneskeord** |
| **D2** | `data/models.json` med frys-tidspunkt og hash for lrcdm/efc og minst én horndeski-/f(R)-rival | `docs/model-comparison/index.md` §1 og §3; `docs/model-comparison/README.md`; `docs/model-comparison/schema.json`; `scripts/maintenance/efc_schema_check.py` | filen finnes ikke; skjemaet har status `frozen` men ingen felt for frys eller hash; tre filer i samme mappe er uenige om hvor registeret bor | **foreslått — avventer menneskeord** |
| **D3** | Holdout-regel: utgivelses-holdout eller frosset K-fold | `docs/validation-ledger/data/tests.json`; `docs/papers/efc/Energy_Flow_Cosmology__Regime_Transition_Fit_to_DESI_DR2_BAO_With_Cross_Validation/index.json` (KC2) | 0 treff på «holdout» i 142 tester; KC2 krever K-fold med faste partisjoner; kontrakten lover utgivelses-holdout | **foreslått — avventer menneskeord** |
| **D4** | Hvilken α-frys (−0.689 eller −0.702) som er grenen av record | `tests/fixtures/nats-prediksjon-efc-fs8.json` (`frys`); `schema/regime_nodes.jsonld` (`prediction.freeze`); `docs/papers/efc/Non-MCMC_Constraints_on_the_EFC_α-Parameter/index.json` | bussen og atlaset rangerer −0.689 som primær; korpuset fører begge uten rang | **foreslått — avventer menneskeord** |

Status-ordene er kortets to: *foreslått* betyr at det ligger et konkret forslag i
dette notatet, *avventer menneskeord* at forslaget ikke er gyldig før eieren sier
ja. Ingen av de fire er gjennomført.

---

## 3. D1 — arbiteren: hvilket artefakt, hvilken versjon, hvilken hash

### Målt tilstand, fem steder i samme hus

1. **Kontrakten.** `schema/regime_nodes.jsonld`, node `efc.growth_engine`:
   `prediction.arbiter_waiting_for` = «DESI DR2 full-shape», `prediction.criterion`
   = «DESI DR2 full-shape fsigma8(z~0.7) must fall within ~1sigma of 0.430»,
   `ville_falsifisere` likelydende. `prediction.arbiter` = **«nei»** — ingen har
   felt dom.
2. **Busspeilingen.** `tests/fixtures/nats-prediksjon-efc-fs8.json`, `hoder.
   arbiter_venter_paa` = samme streng. Fixturen er felt-for-felt-speilingen av
   meldingen på bussen (emne `kosmos.kosmologi.prediksjon.efc-fs8`).
3. **Pakken.** `docs/papers/efc/Sealed_Blind_Predictions_for_Growth_Rate_
   Observables_EFC_vs_LCDM/index.json`: P1 `falsifiable_by` = «DESI DR2 full-shape
   RSD measurement of fσ8 at z≈0.7», P2 = «DESI DR2 BAO full-shape constraints on
   DH/rd at z≈0.7», P3 = «DESI DR2/DR3 BAO and full-shape constraints at z≈1.0»,
   KC1 og KC3 likedan. Pakkens eget abstract sier «prior to the unblinding of DESI
   DR2 full-shape RSD results» og «forthcoming DESI DR2 data»: **arbiteren var en
   framtidig måling allerede i kilden.**
4. **Husets changelog.** `docs/public/EFC_Changelog.html`: «Falsifiable by DESI
   DR2/DR3 full-shape RSD + BAO (2027–2028).» Huset har altså selv skrevet datoen
   — den står bare ikke i kontrakten.
5. **Litteraturen** (denne kjøringen, 2026-09-18, fire arXiv-spørringer ordrett
   lagret i `arxiv_desi_dr2_check.json`):

   | Spørring | Treff |
   |---|---|
   | `all:"DESI DR2" AND all:"full-shape"` | 23 |
   | `all:"DESI DR2" AND all:"RSD"` | 8 |
   | `ti:"DESI DR2" AND all:"galaxy clustering"` | 2 |
   | `all:"DESI DR2" AND all:"fsigma8"` | **0** |

   DR2 full-shape finnes for **Lyα-foresten**: «Validation of the DESI DR2 Lyα
   forest full-shape analysis» (arXiv:2607.27411, 2026-07-29) og «DESI DR2 Results
   IV» (2026-07-29). Galakse-/RSD-full-shape i DR2 finnes ikke i treffene; det
   seneste som kombinerer full-shape med DR2 er DR1-full-shape + DR2 BAO
   (arXiv:2602.18761, 2026-02-21; arXiv:2606.23936, 2026-06-22).

### Forslag — del frysen i to bein, fordi beina har ulik tilgjengelighet

Kontrakten behandler «DESI DR2 full-shape» som én ting. Målt er den to ting, og
bare det ene finnes i navngitt form i dag.

**Avstandsbeinet (P2, P3, KC3) — frys nå.** Artefaktet ligger allerede i repoet:

- `efc_inference/data/bao/desi_dr2/bao_desi_dr2.json`
- 13 punkter i 7 rødforskyvningsbins, blokk-diagonal kovarians, `DV/DM/DH over r_s`
- `source`: «DESI DR2 (arXiv:2503.14738)», `reference`: «DESI Collaboration 2025,
  Phys. Rev. D 112, 083515», `cobaya_repo` og `date_retrieved` oppgitt i filen
- **sha256 = `c38531eecfeee0ca3f479342aea18b3f624f4a184b19747ff40c1a91a45ec5a6`**

  *Sidefunn, målt:* samme fil ligger i to spor med **identisk hash** —
  `pipelines/efc/grav_bridge/data/bao_desi_dr2.json` (2870 bytes, samme sha256).
  To stier til samme måling er to sannhetskilder. De er enige i dag; det bør bli én.

**Vekstbeinet (P1, KC1) — velg, og bare ett av valgene er ærlig:**

- **(a1) Utsettelse.** Skriv «2027–2028» inn i kontrakten med husets egen
  changelog-formulering, og la `arbiter_waiting_for` stå navngitt men **datert**.
  Konsekvens: H4-MIN-01 er kjørbar som forhåndsregistrering, ikke som test, fram
  til vinduet. **Foreslått.**
- **(a2) Omnavning.** Pek på den nærmeste formen som faktisk finnes — DR2 Lyα
  full-shape (arXiv:2607.27411) — og si eksplisitt at den ikke måler fσ8 i
  galakser ved z≈0.7. Kontrakten er da **endret**, ikke presisert.
  **Ikke foreslått av meg**, men det er det ærlige alternativet hvis eieren vil ha
  en arbiter som kan kalles i dag.

Valget endrer ikke tallene, frysene eller kill-kriteriene. Det endrer hva
«kjørbar» betyr — og det er nettopp det B1-gaten skal avgjøre, ikke en worker.

---

## 4. D2 — nuisance-registeret: hvilken fil, hvilke felt, og én motsetning i repoet

### Målt tilstand

- **`data/models.json` finnes ikke**, og `data/comparisons.json` finnes ikke
  (`find` over sporet tre uten arbeidstrær: 0 treff for begge).
- Kravene står **tre steder, og de er ikke enige om hvor registeret bor**:

  | Kilde | Sier |
  |---|---|
  | `docs/model-comparison/index.md` §1 | samme datasett, samme likelihood, samme nuisance og priorer; bare modellen varierer |
  | `docs/model-comparison/index.md` §3 | «Stored in `data/models.json`» — seks rader: `lcdm` (6 frie), `efc_v3` (TBD), `horndeski_min` (8), `f_of_r_hu_sawicki` (7), `dgp_normal` (6), `wcdm` (7); de fire siste merket *placeholder* |
  | `docs/model-comparison/README.md` | lover **begge** filer: `data/comparisons.json` og `data/models.json` |
  | `docs/model-comparison/schema.json` | krever `[version, generated_at, models, comparisons]` i **samme** dokument — altså registeret som `models[]` inne i comparison-ledgeren, ikke som egen fil |
  | `docs/model-comparison/index.md` (Status) | DRAFT 2026-04-23, «awaiting maintainer review» |

- **Skjemaet kan ikke uttrykke en frys.** `$defs.model_entry` har
  `status: enum [placeholder, registered, frozen]` — men **ingen felt for
  frys-tidspunkt eller hash**. Å sette `frozen` i dag er en status uten innhold.
- **C10-gaten sier selv hva som skjer den dagen en instans dukker opp**
  (`scripts/maintenance/efc_schema_check.py`, linje 171): «…exists now — register
  (…) in PAIRS and close the schema». Skjemaet er i dag **åpent**
  (`additionalProperties` mangler på objekt-nivåene), og paret står derfor som
  instansløst: «docs/model-comparison/schema.json (instance promised:
  data/comparisons.json — absent)».

### Forslag

1. **Bestem registerets fil** — `data/models.json` (index.md + README) eller
   `models[]` i `data/comparisons.json` (schema.json). Motsetningen må avgjøres
   **før** noe skrives; å skrive begge er å lage den drift-klassen ADR-002 finnes
   for å hindre.
2. **Utvid `$defs.model_entry`** med et frys-felt —
   `{timestamp_utc, sha256, source (DOI eller commit), files[]}` — og **lukk
   skjemaet** (`additionalProperties: false` på hvert objektnivå), slik at paret kan
   registreres i `PAIRS`.
3. **Frys minst tre modeller**: `lcdm`, `efc_v3` og **én rival**. Kandidatene står
   i registeret: `horndeski_min` (αB, αM frie, 8 parametre) og
   `f_of_r_hu_sawicki` (f(R) Hu-Sawicki, 7). *Hvilken* av dem som er rivalen er en
   del av frysen og velges ikke her. Open question 2 i `index.md` — «MGCAMB
   defaults eller repo-pinned configs?» — må besvares i samme slengen, ellers er
   `code_path` ikke et felt.
4. **Skriv inn likelihood, nuisance og kovarians for H4-MIN-01**, med VAL-006s eget
   krav ordrett: «DESI DR2 + real fσ8 with full covariance»
   (`docs/papers/efc/EFC-VAL-2026-006/index.json`, P1).

Ingen fil er opprettet. Forslaget over er innhold, ikke en skisse som ligger i
treet og venter på å bli trodd.

---

## 5. D3 — holdout-regelen

### Målt tilstand

- `docs/validation-ledger/data/tests.json` v3.0 fører **142 tester** i fem
  kategorier (physics_test 48, consistency_check 22, phenomenological 17,
  framework_constraint 29, planned_pipeline 26). Termtellinger: «holdout» **0**,
  «sealed» 31, «blind» 16, «frozen» 20 — H4s tall står ved lag.
- På prediksjonsflaten er «holdout» nesten fraværende: 1 av 356 (§1).
- **Korpusets eneste holdout-krav** står i `31230703`
  (`docs/papers/efc/Energy_Flow_Cosmology__Regime_Transition_Fit_to_DESI_DR2_BAO_With_Cross_Validation/index.json`),
  KC2: «Covariance-aware conditional hold-out or K-fold cross-validation on DESI
  DR2 (or successor datasets) shows average Δχ^2_h|t ≥ −4 for EFC relative to ΛCDM
  across multiple random partitions». Pakken rapporterer selv Δχ²_h|t = −18.65
  (in-sample på DR2) og sier «Awaiting multiple random partitions and K-fold
  cross-validation on successor datasets for full closure».
- **Kontraktens eget svar på «hvordan dømmes jeg»** er utgivelses-holdout:
  `falsifiable_by` navngir DESI DR2.

### Presiseringen kortet ikke gjør — og som jeg tror er den viktigste i notatet

**De to er ikke alternativer.** (a) utgivelses-holdout er hvordan *arbiteren* feller
dommen; (b) frosset K-fold er hvordan *modellene måles mot hverandre* på samme data
uten å velge partisjoner etter utfallet. H4 stilte dem som et enten/eller fordi
begge kalles «holdout»; lest mot kilden svarer de på hvert sitt spørsmål.
H4-MIN-01 trenger begge.

### Forslag

- **Velg (b) som mekanisme for modell-sammenligningen**, med disse feltene frosset
  **før** dataåpning: datasettartefakt + versjon + sha256 (§3 gir et konkret
  forslag), `n_folds`, partisjonsregel og **dens** hash, og regelen at alle tre
  modellene **må** bruke identiske partisjoner.
- **Terskelen gjenbrukes ordrett fra KC2** (Δχ²_h|t ≥ −4). Det er det eneste
  holdout-kravet korpuset selv har skrevet, og å finne opp et nytt ville vært å
  innføre en konvensjon i det samme notatet som sier at konvensjonen mangler.
- **Behold (a) uendret som arbiterens domsform.** Den er det prediksjonen selv
  lover å bli felt av, og den kan ikke byttes uten å endre prediksjonen.

H4 anbefalte (b). Her legges (b) fram med presiseringen over; valget er eierens.

---

## 6. D4 — hvilken α-frys er grenen av record

### Målt tilstand

| Sted | α = −0.689 | α = −0.702 | Rang |
|---|---|---|---|
| busspeilingen `tests/fixtures/nats-prediksjon-efc-fs8.json` (`frys`) | 2026-02-18T05:07:13, hash-prefiks `7a850cfa58477701` | 2026-02-21T16:08:57.818002, `dbccda150abca0e7` | **primary / secondary** |
| atlasnoden `prediction.freeze` | samme | samme | **primary / secondary** |
| `docs/papers/efc/Non-MCMC_Constraints_on_the_EFC_α-Parameter/index.json` (DOI 10.6084/m9.figshare.32101213) | `freeze_20260218_050713` | `freeze_20260221_160857` | **ingen rang** |
| `docs/papers/efc/white-paper-part-3-of-4-…-data-validation-ledger-and-/index.json` | P1, 2026-02-18, hash `7a850cfa…` | P2, 2026-02-21, hash `dbccda…` | **ingen rang** |

Tre α-verdier er altså i spill: **−0.689** (primærfrys), **−0.702**
(sekundærfrys) og **−1.00 ± 0.46** (2.2σ, den tilpassede grenen i samme pakkes
`key_results` — forbudt som pass-kriterium, H4 §8 B3, men lovlig som diagnostikk).

**Én datoobservasjon.** Atlasnoden har `issued_at` og `valid_for` = 2026-04-14
(pakkens DOI-dato), mens frysene er 2026-02-18/21. Rekkefølgen er riktig for en
forhåndsregistrering — frys før deponering — men en leser som tar `issued_at` for
preregistreringsdatoen leser den to måneder for sent. Kontrakten bør si hvilken av
datoene som *er* preregistreringsdatoen.

### Forslag

**α = −0.689 (2026-02-18, hash `7a850cfa58477701`) skrives inn i prereg-filen som
grenen av record, og −0.702 merkes eksplisitt som sensitivitetssjekk.**

Grunnen er ikke smak: −0.689 er den eneste av de to som er rangert som *primær* noe
sted i huset (bussmeldingen og atlasnoden), og den er den tidligste. Men
rangeringen står **bare i bussoverflaten, ikke i korpuset** — derfor er dette en
beslutning eieren må bekrefte, ikke et oppslag. Uten den skrevet ned med hash er
testen ikke-falsifiserende (H4 §9, R2: den fittede grenen kan ellers reprodusere
frysen ved å velge α etter utfallet).

---

## 7. VAL-006-flagget inn i atlasnoden `efc.growth_engine` — forslag med diff

### Hva som skal sies

Korrigendet står i `docs/papers/efc/EFC-VAL-2026-006/index.json` (DOI
10.6084/m9.figshare.32114530, 2026-04-28), i pakkens `description` og i
`sealed_predictions` **P1**:

> «Growth-sector sealed predictions (fσ8/BAO) from VAL-005 are flagged as
> conditional on retired stub/DR1 inputs and require re-testing under DESI DR2 +
> real fσ8 with full covariance.»

og i beskrivelsen:

> «Re-runs show the earlier DESI DR1 non-MCMC Δχ² signal dissolves under DESI DR2
> + real fσ8, and the EFC VariantH entropy-gradient growth model yields a genuine
> null under a symmetric prior and patched pipeline.»

Atlaset sier ingenting om dette. Kartet og korpuset sier derfor ikke det samme om
samme gren — og det er den koblingen dette forslaget lukker.

### Hvor flagget skal stå — og hvorfor ikke de tre nærmeste alternativene

- **Ikke i `prediction`.** Skjemaet beskriver kontrakten som «SPEILET fra bussen
  (NATS VERDEN_PROGNOSE), **ikke oppfunnet her**», og fixturen er felt-for-felt.
  Et felt som bare finnes i repoet ville gjort speilingen til en påstand den ikke
  kan innfri.
- **Ikke i `settlement`.** Oppgjøret finnes ikke: `prediction.arbiter` = «nei», og
  ingen måling har felt dom. Å skrive korrigendet som settlement ville sagt at
  dommen er falt.
- **Ikke i `falsifiserbarhet`.** Det feltet sier hvorfor en node *ikke kan* felles,
  ikke at en kilde har svekket den.
- **`revisjon` er nærmest** (array av strenger: «Logg over endrede
  terskler/antakelser (dato + hva)») — men det er **våre egne** endringer, uten DOI
  og uten sitat. Et korrigendum er en kilde **utenfor** noden.

Derfor to forslag, ett anbefalt.

### Forslag A (anbefalt) — nytt valgfritt nodefelt `korrigendum`

Array av `{doi, dato, sitat, virkning, kildefil}`, pluss skjemafeltet som gjør det
lovlig: skjemaet er lukket (`additionalProperties: false` i
`schema/regime_node.schema.json`), så et felt uten skjemaoppføring ville blitt
avvist av C10-porten.

```diff
diff --git a/schema/regime_node.schema.json b/schema/regime_node.schema.json
index 0140498d..4176da2f 100644
--- a/schema/regime_node.schema.json
+++ b/schema/regime_node.schema.json
@@ -351,6 +351,43 @@
           },
           "description": "Logg over endrede terskler/antakelser (dato + hva)."
         },
+        "korrigendum": {
+          "type": "array",
+          "description": "Eksterne korrigenda som svekker nodens tall uten aa endre dem. Skilt fra `revisjon`: revisjon er VAARE egne endringer av terskler og antakelser, et korrigendum er en kilde UTENFOR noden som sier at noden ikke lenger er uforbeholden — med egen DOI og eget sitat.",
+          "items": {
+            "type": "object",
+            "required": [
+              "doi",
+              "dato",
+              "sitat",
+              "virkning",
+              "kildefil"
+            ],
+            "additionalProperties": false,
+            "properties": {
+              "doi": {
+                "type": "string",
+                "description": "DOI-en til korrigendet."
+              },
+              "dato": {
+                "type": "string",
+                "description": "Utgivelsesdato for korrigendet."
+              },
+              "sitat": {
+                "type": "string",
+                "description": "Det som svekker noden, ordrett."
+              },
+              "virkning": {
+                "type": "string",
+                "description": "Hva det betyr for nodens status — ikke hva det betyr for tallene."
+              },
+              "kildefil": {
+                "type": "string",
+                "description": "Stien i dette repoet der sitatet staar."
+              }
+            }
+          }
+        },
         "epistemikk": {
           "type": "object",
           "required": [
diff --git a/schema/regime_nodes.jsonld b/schema/regime_nodes.jsonld
index 80def5b5..a091a6f9 100644
--- a/schema/regime_nodes.jsonld
+++ b/schema/regime_nodes.jsonld
@@ -3781,7 +3781,16 @@
     "ebe_s_regime": "high_s"
    },
    "synlighet": "offentlig",
-   "ville_falsifisere": "DESI DR2 full-shape fσ8(z~0.7) utenfor ~1σ av 0.430 — den forseglede prediksjonen."
+   "ville_falsifisere": "DESI DR2 full-shape fσ8(z~0.7) utenfor ~1σ av 0.430 — den forseglede prediksjonen.",
+   "korrigendum": [
+    {
+     "doi": "10.6084/m9.figshare.32114530",
+     "dato": "2026-04-28",
+     "sitat": "Re-runs show the earlier DESI DR1 non-MCMC Δχ² signal dissolves under DESI DR2 + real fσ8, and the EFC VariantH entropy-gradient growth model yields a genuine null under a symmetric prior and patched pipeline.",
+     "virkning": "Vekstgrenen denne noden forseglet er BETINGET, ikke uforbeholden: husets eget korrigendum flagger de forseglede veksttallene som hvilende paa tilbaketrukne stub/DR1-innsatser og sier at signalet loeses opp under DESI DR2 + reell fsigma8. Det endrer ikke tallene og ikke frysene; det sier hva de er verdt i dag.",
+     "kildefil": "docs/papers/efc/EFC-VAL-2026-006/index.json (sealed_predictions P1)"
+    }
+   ]
   },
   {
    "id": "efc.lensing_engine",
```

(Fil: `docs/notes/proposals/H4-MIN-01-korrigendum-A-schema-og-node.patch`,
3125 bytes, sha256 `05243a98ceed10316b5f92a3e0e5f6cdf9c0747f5fce6d94efa6ec6033253a8d`.)

### Forslag B (minimalt) — gjenbruk `revisjon`, ingen skjemaendring

```diff
diff --git a/schema/regime_nodes.jsonld b/schema/regime_nodes.jsonld
index 80def5b5..37b023c2 100644
--- a/schema/regime_nodes.jsonld
+++ b/schema/regime_nodes.jsonld
@@ -3781,7 +3781,10 @@
     "ebe_s_regime": "high_s"
    },
    "synlighet": "offentlig",
-   "ville_falsifisere": "DESI DR2 full-shape fσ8(z~0.7) utenfor ~1σ av 0.430 — den forseglede prediksjonen."
+   "ville_falsifisere": "DESI DR2 full-shape fσ8(z~0.7) utenfor ~1σ av 0.430 — den forseglede prediksjonen.",
+   "revisjon": [
+    "2026-04-28 — VAL-006-korrigendum (DOI 10.6084/m9.figshare.32114530): de forseglede veksttallene fra VAL-005 er flagget som betingede av tilbaketrukne stub/DR1-innsatser, og vekstsignalet loeses opp under DESI DR2 + reell fsigma8; noden er derfor betinget, ikke uforbeholden. Kilde: docs/papers/efc/EFC-VAL-2026-006/index.json P1."
+   ]
   },
   {
    "id": "efc.lensing_engine",
```

(Fil: `docs/notes/proposals/H4-MIN-01-korrigendum-B-revisjon.patch`, 892 bytes,
sha256 `63fb9793f8ea36bfcd194ab966149fea67997ed1e82c5cccb94bea7512c408e8`.)

### Nabofunn: den offentlige statement-grafen sier det — svakere, og uten side

Det finnes en **tredje** flate mellom korpuset og atlaset, og den er verdt å lese
før man bestemmer hvor flagget hører:

- `public/graph/statements.yaml` fører `efc.h1.003`: «Variant H
  (entropigradient-vekstmekanismen) viser ingen datapreferanse: ΔAIC = +4.05,
  S₀ = 0.21 ± 0.14 ved 1,5σ — signalet kan ligge under nåværende sensitivitet»
  (`kind: negative_result`, `epistemic_level: partial_support`).
- Den støttes av `ev.efc.desidr2.001`, som lokaliserer til
  `evidence/01_hypothesis.md` §«H1 DESI DR2 update», `source_class:
  internal_analysis`, med en egen begrensning: «EFCs EGEN analyse av DESI DR2-data;
  den eksterne DESI-referansen (paper/DOI/tabell) skal etterfylles».
- **Ingen** evidensnode i `public/graph/evidence.yaml` viser til DOI
  10.6084/m9.figshare.32114530 eller til VAL-006 (0 treff).
- Og `efc.h1.003` har `appears_on: []` — den står på **ingen side**. Målt: 4 av
  grafens 10 statements har tom `appears_on` (checkeren melder dem som INFO, ikke
  som feil).

Presist sagt: påstanden finnes på tre steder, i tre styrker. Korpuset sier at
signalet **løses opp**; den offentlige grafen sier at mekanismen **ikke har noen
datapreferanse** og at signalet «kan ligge under nåværende sensitivitet»; atlaset
sier ingenting. Det er ikke en motsetning i fysikken — det er tre tekster om samme
gren som ikke siterer hverandre.

Følgen for forslaget under er bare at `kildefil` peker på korrigendet (den
sterkeste kilden), ikke på `efc.h1.003`. En utvidelse der flagget også bærer
`statement_id: efc.h1.003` er mulig og ville knyttet kartet til grafen — den er
**ikke** foreslått her, fordi den krever at noen først bestemmer om grafens svakere
formulering eller korrigendets sterkere er den gjeldende. Orphan-funnet (4 av 10)
hører til vedlikeholdsrunden, ikke til denne frysen.

### Verifisert i denne kjøringen — ikke påstander

`verifiser_forslag.py` anvender patchen på `823b52e0`, måler, og setter treet
tilbake:

| Sjekk | Forslag A | Forslag B |
|---|---|---|
| `git apply --check` mot `823b52e0` | OK | OK |
| metaschema (Draft202012) gyldig | OK | OK |
| `schema/regime_nodes.jsonld` (89 noder) validerer mot skjemaet | OK | OK |
| C10-closure: `additionalProperties: false` på alle objektnivåer | OK | OK |
| `test_regime_node_schema.py`, `test_prediksjon_og_oppgjoer.py`, `test_efc_atlas_generator.py`, `test_atlas_dekning.py`, `test_falsifiserbarhet.py` | **76 passed** | **76 passed** |
| `prediksjonsblokken urørt` (18 nøkler; `sealed_doi`, `sealing_sha256`, `arbiter_waiting_for` uendret) | OK | OK |
| `scripts/maintenance/efc_schema_check.py` på grenen | OK — 4 par gyldige og lukkede | OK — 4 par gyldige og lukkede |

**Ingen av dem er anvendt i grenen**, og ingen av dem er pushet. De er filer.

### Hva flagget gjør — og ikke gjør

Det flytter ikke et tall, endrer ikke en frys, og feller ingen dom. Det gjør at
kartet sier det korpuset alt sier i VAL-006 P1: **vekstgrenen er betinget, ikke
uforbeholden.** Uten det står atlaset igjen med en kontrakt som venter på et
datasett husets egen revisjon allerede har beskrevet som avgjørende for grenen —
og med 13 av 14 forhåndsregistrerte pakker fortsatt usynlige i kartet (§1).

---

## 8. Hva dette notatet ikke gjør

1. **Kjører ikke oppgjøret.** Ingen dataåpning. B1 i
   `prereg_H4_PROP_01_v2_FINAL.json` står uendret.
2. **Endrer ingen prediksjon** — ikke tallene i `32013156`, ikke frysene, ikke
   kill-kriteriene, ikke `prereg`-filen.
3. **Rører ingen fil i figshare.** Ingen DOI er opprettet, endret eller lest på nytt.
4. **Pusher ingen atlasendring.** Begge forslagene ligger som patcher med målte
   tall; de er ikke anvendt.
5. **Oppgraderer ingen claim**, og påberoper ingen ekstern validering.
6. **Fatter ingen av de fire beslutningene** — de er lagt fram, ikke tatt.

---

## 9. Kilder — stier lest i denne kjøringen (alle mot `823b52e0`)

| Sti | Hva den sier her |
|---|---|
| `schema/regime_nodes.jsonld` | 89 noder; `efc.growth_engine` med `prediction` (sealed_doi `32013156`, sha `fbb53d61…`, `freeze` med to α, `arbiter` = «nei», `arbiter_waiting_for` = «DESI DR2 full-shape»); 4 prediction-noder, 3 settlement-noder |
| `schema/regime_node.schema.json` | node-skjemaet; `prediction` beskrevet som speiling av bussen; `revisjon` = array av strenger; lukket på objektnivå |
| `tests/fixtures/nats-prediksjon-efc-fs8.json` | den målte bussmeldingen felt for felt (`frys`, `arbiter_venter_paa`, `forseglet_doi`, `forsegling_sha256`) |
| `docs/papers/efc/Sealed_Blind_Predictions_for_Growth_Rate_Observables_EFC_vs_LCDM/index.json` | P1–P3 og KC1–KC4; DOI `32013156`, datert 2026-04-14 |
| `docs/papers/efc/Non-MCMC_Constraints_on_the_EFC_α-Parameter/index.json` | begge α-frysene uten rang; `key_results` α = −1.00 ± 0.46 |
| `docs/papers/efc/white-paper-part-3-of-4-energy-flow-cosmology-part-3-data-validation-ledger-and-/index.json` | begge α-frysene som P1 og P2 |
| `docs/papers/efc/EFC-VAL-2026-006/index.json` | korrigendet: P1, P2, KC1–KC4, `description` |
| `docs/papers/efc/Energy_Flow_Cosmology__Regime_Transition_Fit_to_DESI_DR2_BAO_With_Cross_Validation/index.json` | KC2 — korpusets eneste holdout-krav |
| `docs/validation-ledger/data/tests.json` | 142 tester, fem kategorier; «holdout» 0, «sealed» 31, «blind» 16, «frozen» 20 |
| `docs/model-comparison/index.md`, `README.md`, `schema.json` | protokollen, fil-løftene og skjemaet som ikke kan uttrykke en frys |
| `scripts/maintenance/efc_schema_check.py` | C10-porten; linje 171 sier hva som kreves den dagen instansen finnes |
| `docs/public/EFC_Changelog.html` | «Falsifiable by DESI DR2/DR3 full-shape RSD + BAO (2027–2028)» |
| `efc_inference/data/bao/desi_dr2/bao_desi_dr2.json` (+ tvilling i `pipelines/efc/grav_bridge/data/`) | DESI DR2 BAO, 13 punkter, sha256 `c38531ee…` |
| `tests/test_prediksjon_og_oppgjoer.py` | «Problemet er ikke at oppgjøret mangler — det er at bussen gjør opp og kartet ikke ser det» |
| `public/graph/statements.yaml` | 10 statements, 4 med tom `appears_on`; `efc.h1.003` = Variant H uten datapreferanse |
| `public/graph/evidence.yaml` | `ev.efc.desidr2.001` støtter `efc.h1.003`; **ingen** node viser til VAL-006 eller DOI `32114530` |

---

## 10. Kjøringsartefakter

Alle er lesende. Ingen åpner data, ingen skriver til repoet utenom de to patchene
(§7) og denne notatfilen.

| Artefakt | Gjør |
|---|---|
| `h4_min01_remaal.py` | remåler §1: atlasnoder, prediction/settlement/DOI-dekning, korpus-totaler, ledger-tellinger, prediksjonsflatens termer |
| `verifiser_forslag.py` | anvender hver patch, validerer skjema + instans + C10-closure, kjører de fem testfilene, sjekker at prediksjonsblokken er urørt, og setter treet tilbake |
| `arxiv_desi_dr2_check.json` | de fire arXiv-spørringene ordrett med treff og datoer (§3) — **kortvedlegg, ikke repofil**; spørringene står ordrett i §3 og kan kjøres på nytt |
| `H4-MIN-01-korrigendum-A-schema-og-node.patch` | forslag A (§7) |
| `H4-MIN-01-korrigendum-B-revisjon.patch` | forslag B (§7) |

---

## 11. Begrensninger

- **Testene ble kjørt i et eget venv.** Runtime-en for denne kjøringen mangler
  numpy, pytest og emcee og har ingen `.venv`. `pytest 9.1.1` ble installert i et
  venv med `--system-site-packages` (repoet pinner `pytest>=8,<9` — versjonen er
  altså utenfor pinnen, og det er en svakhet ved beviset, ikke ved forslaget).
  **`make check` og `efc_bro_synk.py --sjekk` kunne ikke kjøres** (numpy mangler);
  `efc_schema_check.py` og `validate_repo.py` kjørte OK. CI kjører resten.
- **Litteratursjekken er fire arXiv-spørringer**, ikke en fullstendig gjennomgang.
  Den støtter «finnes ikke i navngitt form per 2026-09-18»; den beviser ikke fravær.
- **H4s 34/356 er ikke reprodusert** (§1) og brukes ikke som faktum.
- **Hva bussen faktisk gjør opp, er ikke lest** — bare fixturen og atlasnoden,
  samme begrensning som H4 §10.
- **Atlasets tilstand er en dato, ikke en egenskap.** Tallene i §1 er målt på
  `823b52e0`; `origin/main` flyttet seg én gang mens dette notatet ble skrevet
  (`5e02b4e6` → `823b52e0`, PR #494, som ikke rører `schema/`).
