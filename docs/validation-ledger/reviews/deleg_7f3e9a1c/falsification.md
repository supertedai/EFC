# Blind adversarial review: falsification of the reconciliation claims

**Scope.** Dette er en falsifikasjonsanalyse av manuskriptet slik det foreligger, ikke en validering av EFC. «Finnes i data» betyr her at testen er kjørt med identifiserbare data, låste parametre, spesifisert likelihood og rapportert usikkerhet. En ligning, kode eller intern metadataregistrering teller ikke som empirisk test.

## Kort dom

Manuskriptet er ærlig om at det ikke utfører nye fit, men de sentrale empiriske påstandene er i hovedsak ikke operative ennå. Den enkleste reelle testen er en låst, out-of-sample sammenligning av de alternative funksjonsformene på samme datasett. For `E ∝ √g` finnes det en plausibel falsifikasjonsretning (RAR/SPARC), men ingen komplett, reproducerbar test i manuskriptet. KC1 er logisk falsifiserbar i prinsippet, men ikke kjørbar slik den er formulert. De to aksene er primært en ontologisk klassifikasjon, ikke empiriske funn. De to preregistrerte diskriminatorene er foreslåtte tester; ingen av dem er utført her.

## Påstand-for-påstand

### 1. «Γ-bifurkasjon» / modellfamilien

**Påstand.** Korpset inneholder flere realiserte former for `Γ(ρ)`, og disse utgjør en formbifurkasjon, ikke en demonstrert lineær modningskjede `Γ_A → Γ_B → Γ_C`.

**Enkleste falsifiserende observasjon/test.** Del påstanden i to, ellers blir den immun mot data:

1. For den rene korpus-påstanden: les tilbake de normative, versjonerte PDF-/kildeartefaktene. Påstanden feiler dersom én autoritativ versjon viser at formene ikke faktisk er distinkte realiseringer, eller at A/B/C bare er samme funksjon med en parameteromskriving.
2. For den fysiske bifurkasjonen: spesifiser ett felles datasett og én felles likelihood, og sammenlign
   `Γ_A = ρ/(ρ+ρ_crit)`, `Γ_B = ρ^(3/2)/(ρ+ρ_crit)` og `Γ_C = √(ρ/ρ_crit)/(1+√(ρ/ρ_crit))`
   med samme nuisance-parametre og holdout-data. Bifurkasjonen som fysisk alternativstruktur er falsifisert dersom én form entydig forkastes eller alle tre er observasjonelt ekvivalente over det relevante regimet.

**Status i eksisterende materiale.** Korpusnivået er dokumentert: 31942821 har intern uoverensstemmelse mellom den saturerende formen i beskrivelsen og `ρ^(3/2)` i key result/kode; 31942800 deklarerer square-root-formen. Det er imidlertid ikke en empirisk seleksjon. Ingen felles fit, likelihood-rangering eller holdout-test for Γ-formene finnes i dette manuskriptet. Bifurkasjon er derfor en beskrivelse av dokument- og modellfamilien, ikke et etablert fysisk resultat.

**Falsifiserbarhet slik formulert.** Delvis. Korpusbeskrivelsen er arkiv-/kilde-falsifiserbar. «Bifurkasjon» som fysisk påstand mangler datasett, regime, parametre og beslutningsregel, og er dermed ikke tilstrekkelig operasjonalisert.

### 2. `B → B+` som companion upgrade / eventuell supersession

**Påstand.** B+ er en deklarert companion upgrade av B, men supersession er ikke etablert.

**Enkleste falsifiserende test.** Frys før dataanalysen alle parametre og domenet, og sammenlign B og B+ på samme ubrukte datasett. B+ kan bare kalles en empirisk oppgradering dersom den gir bedre predefinert out-of-sample prediksjon (for eksempel en låst Δχ²/Bayes-faktor med en eksplisitt terskel) uten flere frihetsgrader eller etterfølgende parameterbytte. Påstanden om B+ som oppgradering falsifiseres hvis B predikerer holdout-data bedre, eller hvis forskjellen forsvinner når frihetsgrader og parametre behandles likt. Hvis begge er like gode, er supersession ikke demonstrert.

**Status i eksisterende materiale.** Det finnes en deklarert relasjon i kilde-/metadata-laget: 31942821 omtaler 31942800 som companion/upgrade, og B+ endrer den antatte density-of-states-avhengigheten. Manuskriptet sier selv at ingen seleksjon er utført og at supersession er `not established`. Ingen sammenlignende empirisk fit er rapportert.

**Falsifiserbarhet slik formulert.** Den deklarerte relasjonen er en historisk/provenienspåstand og kan kontrolleres mot versjonerte kilder. «B+ supersedes B» ville vært falsifiserbart med testen over, men er ikke faktisk påstått som etablert i teksten. Uten låst sammenligning er oppgraderingsordet ikke evidens.

### 3. `KC1` og `E ∝ √g`

**Påstand.** Hvis robuste, bias-kontrollerte galaksedata ved `≥5σ` foretrekker `μ(g)=1/(exp(g/a₀)-1)` og signifikant ekskluderer square-root-formen, er teoremet `E ∝ √g` falsifisert.

**Enkleste falsifiserende observasjon/test.** Før fitten må følgende låses: datasett/galakseseleksjon, rotasjonskurve-likelihood, baryonisk modell, nuisance-parametre, `a₀`, begge konkurrerende `μ(g)`-former, behandling av korrelerte feil, systematikk og beslutningsregel. Kjør deretter én blind eller holdout-basert felles fit. En robust, forhåndsdefinert `≥5σ` eksklusjon av `μ_√g` til fordel for `μ_linear`, på tvers av den forhåndsdefinerte galakseprøven, er den enkleste observasjonen som falsifiserer den koblede påstanden. Omvendt: manglende `≥5σ` er ikke støtte for square-root-teoremet; det er bare ikke-falsifikasjon.

**Viktig logisk hull.** KC1 hopper fra en preferanse mellom fenomenologiske `μ`-funksjoner til falsifikasjon av et teorem om eksitasjonsenergien. Den implikasjonen må utledes eksplisitt og vise at alternative forklaringer, mappingen fra E til μ og nuisance-parametre ikke kan absorbere avviket. Ellers falsifiserer testen høyst den bestemte `μ_√g`-implementasjonen, ikke nødvendigvis alle modeller med `E ∝ √g`.

**Status i eksisterende materiale.** Ingen slik test er utført i manuskriptet. For 31941465 er `Δχ²` og signifikans null, og datasettfeltet sier «referenced; no new fit performed». Det er derfor ingen rapportert `≥5σ`-falsifikasjon og heller ingen empirisk støtte for teoremet. Det eksisterer også intern/cross-package konflikt mellom lineær `exp(g/a₀)` og square-root `exp(√(g/a₀))`; det er en proveniens-/modellkonflikt, ikke et resultat fra en kontrollert observasjon.

**Falsifiserbarhet slik formulert.** Prinsipielt ja, praktisk nei. `≥5σ` er ikke nok som spesifikasjon: «robust», «bias-controlled», «preferred» og «diverse systems» er udefinert, og ingen fit/proveniens er levert. KC1 er derfor ikke kjørbar eller reproduserbar i nåværende form.

### 4. De to ortogonale aksene

#### 4a. E-eksponentaksen (`α=1` vs. `α=1/2`)

**Påstand.** Valget av energiskalering, `E ∝ g^α`, er uavhengig av valget av Γ-form.

**Enkleste falsifiserende test.** Skriv en full felles modell med både `α` og Γ-form som eksplisitte parametre/valg, og deriver observablene. Påstanden om ortogonalitet feiler hvis feltligningene tvinger én akse til en bestemt verdi på den andre, eller hvis den samme reparametriseringen gjør at de ikke er identifiserbare separat. Empirisk må en joint fit kunne variere `α` uten å endre Γ-form og omvendt, med ikke-singulær identifikasjon på et relevant datasett.

**Status.** Manuskriptet erklærer uavhengighet, men leverer ingen joint derivation, identifiability-analyse eller test. Det finnes derfor ingen data som etablerer ortogonalitet.

**Falsifiserbarhet.** Som matematisk strukturell påstand: ja, ved å vise en avhengighet i den komplette modellen. Som empirisk påstand: ikke ennå, fordi modellen og estimanden ikke er spesifisert tilstrekkelig.

#### 4b. Γ-formaksen (saturerende A vs. square-root-saturerende C)

**Påstand.** Γ-formen er et uavhengig åpent valg.

**Enkleste falsifiserende test.** Samme som for Γ-bifurkasjonen: en felles, låst, out-of-sample sammenligning av A og C. Aksenes uavhengighet feiler hvis den fullstendige teorien viser at valgt `α` entydig bestemmer A/C, eller hvis A/C ikke kan identifiseres separat fra `α` i observablene.

**Status.** Manuskriptet sier uttrykkelig at Γ-aksen ikke har en egen preregistrert diskriminator. Ingen data er derfor brukt til å velge eller falsifisere A kontra C.

**Falsifiserbarhet.** Ikke tilstrekkelig operasjonalisert som empirisk påstand. Den kan gjøres falsifiserbar først etter at en observabel, et regime og en sammenligningsregel er låst.

### 5. Preregistrert diskriminator 1: låst-`a₀` SPARC/RAR-retrodiksjon

**Påstand/testidé.** Med ett autoritativt, forhåndslåst `a₀` skal EFCs screeningform retrodusere SPARC/RAR; `a₀` skal ikke fit'es etterpå.

**Enkleste falsifiserende observasjon.** Frys `a₀`, baryonisk massemodell, galakseutvalg og alle nuisance-priorer før SPARC-data åpnes for testen. Kjør den låste EFC-kurven mot holdout-galaksene. Testen falsifiseres dersom den pre-spesifiserte residual-/likelihood-terskelen overskrides, eller hvis den lineære modellen med samme låste protokoll entydig slår square-root-modellen. En god fit etter at `a₀` eller andre frihetsgrader er valgt på samme data er ikke en retrodiksjon.

**Status.** Ikke utført. Manuskriptet sier at preregistreringen fortsatt venter på author freeze, og at `a₀` er author-gated. Det finnes ingen rapportert låst fit, residualtabell, Δχ² eller holdout-resultat her.

**Falsifiserbarhet.** Ja i prinsippet, men ikke ennå som en gyldig preregistrert test. Uten ett låst `a₀` og eksplisitt terskel kan resultatet flyttes post hoc og er dermed ikke en ren falsifikasjonstest.

### 6. Preregistrert diskriminator 2: `d_L^GW ≠ d_L^EM`

**Påstand/testidé.** Den relativistiske EFC-koblingen gir
`d_L^GW/d_L^EM = √[F(φ₀)/F(φ_z)]`, `F(φ)=1+αφ`, og dermed generelt ulik GW- og EM-luminositetsavstand.

**Enkleste falsifiserende observasjon.** Før standard-siren-samplet analyseres, frys `α`, `φ₀`, normaliseringen av `φ`, redshift-avhengigheten og en minimumseffekt/retning. Sammenlign samme-source `d_L^GW/d_L^EM` med 1 i en forhåndsdefinert hierarchical likelihood, inkludert kalibrering, inclination, host-identifikasjon og selection effects. En presis, uavhengig multi-messenger-sample som er konsistent med ratio 1 og ekskluderer den låste EFC-avvikskurven, falsifiserer denne konkrete prediksjonen. Et avvik fra 1 uten å passe de låste parameterne bekrefter heller ikke EFC.

**Status.** Ikke utført i manuskriptet. Kilden gir en mekanisme og en lukket form, men manuskriptet sier eksplisitt at `α` og `φ₀` ikke er frosset, og ledger-preregistreringen beskriver prediksjonen som code-supported, ikke som en frozen numeric prediction. Det foreligger ingen analysert standard-siren-sample eller signifikans for dette testforslaget.

**Falsifiserbarhet.** Bare delvis slik formulert. `d_L^GW ≠ d_L^EM` uten effektstørrelse, fortegn, parametre, redshiftform og terskel kan nesten alltid reddes ved å endre `α`/felt-normalisering. Det er derfor en falsifiserbar mekanisme etter parameterfrysing, men ikke en falsifiserbar numerisk prediksjon ennå.

## Samlet evidensstatus

| Påstand | Enkleste falsifikasjon | Finnes testen/data i manuskriptet? | Dom |
|---|---|---:|---|
| Γ-bifurkasjon | Låst felles fit av A/B/C; eller autoritativ kilde viser at formene ikke er distinkte | Nei; bare kilde-/metadataevidens | Strukturelt delvis falsifiserbar, empirisk uoperasjonalisert |
| B→B+ supersession | Samme holdout-data viser B ≥ B+ under lik kompleksitetsstraff | Nei | Ikke demonstrert; testbar når protokollen fryses |
| KC1 / `E ∝ √g` | Robust, forhåndsspesifisert `≥5σ` eksklusjon av square-root-formen i låst SPARC/RAR-fit | Nei; `Δχ²=null`, «no new fit» | Prinsipielt falsifiserbar, aktuelt ikke kjørbar |
| E-eksponentaksens ortogonalitet | Full modell viser at α og Γ ikke kan velges uavhengig | Nei | Påstått, ikke vist |
| Γ-formaksens ortogonalitet | Full modell/joint fit viser kobling eller manglende identifikasjon | Nei | Påstått, ikke vist |
| SPARC/RAR-diskriminator | Låst `a₀`-retrodiksjon feiler predefinert terskel | Nei; `a₀` author-gated | Testidé er gyldig først etter freeze |
| Siren-diskriminator | Låst EFC-ratio forkastes av standard-sirens som ratio=1 | Nei; parametre ikke frosset | Mekanisme testbar, prediksjon ikke frosset |

**Konklusjon.** Den enkleste observasjonen som kan ødelegge den mest konkrete EFC-påstanden er en blind, låst SPARC/RAR-analyse som foretrekker den lineære `g`-eksponenten og ekskluderer `√g` på forhåndsdefinert nivå. Men manuskriptet inneholder ikke denne analysen. Det som faktisk foreligger er deklarasjoner, kilde-/proveniensinformasjon og foreslåtte tester — ikke en utført falsifikasjon eller empirisk modellseleksjon.
