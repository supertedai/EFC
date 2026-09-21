# Attacker review — runde 2

## Dom

Det sterkeste angrepet er ikke at manuskriptet later som om det har gjort en fit; det sier uttrykkelig at det ikke har gjort det. Problemet er at selve **reconciliation-påstanden ikke er fysisk lukket**: den setter sammen størrelser fra inkompatible eller uavklarte modellag og kaller dem én modellfamilie med to «ortogonale» akser. Kildene viser ikke en felles generativ modell som mapper

```text
Gamma(rho) -> feltligning -> observabler (RAR, vekst, linse, sirener).
```

Uten denne mappingen er «model family», «orthogonal», «derived», «upgrade» og «discriminator» primært metadataetiketter, ikke fysiske resultater.

---

## 1. Samme `Gamma` brukes som ulike objekter uten en kilde-forankret identifikasjon

**Berørte claim_id:** `C03`, `C04`, `C06`, `C07`, `C08`, `C15`

**Manuskript:** Linje 127–131 definerer `Gamma(rho) = dS/d rho` og `sigma_s = Gamma dot-rho`; linje 160–164 kobler samtidig E-eksponenten til grid-action-pakken; linje 209 sier at sirentesten ikke tester Gamma-formen.

**Kildene:**

- `docs/papers/efc/Derivation_of_the_Entropy_Production/index.json:24-27,49-55` bruker `Gamma(rho)` som kilde i `Box phi = Gamma(rho)` og sier at Gamma følger av BE/von Neumann-entropi.
- `docs/papers/efc/EFC_Relativistic_Action_Field_Equations_Perturbation_Theory_and_Extraction/index.json:28-43,147-182,205-217` bruker `Gamma(rho)` i en Lagrange-multiplikatorbegrensning `Box phi = Gamma(rho)`, med en konkret saturerende form og en egen felt-/lambda-dynamikk.
- `docs/papers/efc/Derivation_of_the_Entropy_Production/index.json:108` setter derimot `key_result` til `rho^(3/2)/(rho+rho_crit)`, mens samme fil på `:49-55` og `:68-77` presenterer den saturerende formen som derivert resultat/prediksjon.

**Angrep:** Manuskriptet registrerer formene, men viser ikke at `dS/d rho`, kilden i `Box phi = Gamma(rho)`, og Gamma-funksjonen i den relativistiske handlingen er samme fysiske størrelse. Det mangler minst en eksplisitt dimensjons-/normaliseringsmapping mellom `S`, `phi`, `Gamma`, `Box phi` og `sigma_s`. Dermed følger ikke den sentrale implikasjonen: at en formbifurkasjon i `Gamma` er en bifurkasjon mellom alternative gravitasjonsmodeller og ikke bare mellom forskjellige definisjoner eller roller i ulike pakker.

Dette er sterkere enn den allerede erkjente A/B-uoverensstemmelsen: selv om A/B/C listes korrekt som dokumenterte uttrykk, er det ikke vist at de kan settes inn i samme feltligning eller sammenlignes på samme observabel. `C03` bør derfor ikke stå som mer enn en manuskriptsyntese, og `C06`/`C07` kan ikke løftes til modellstruktur uten denne identifikasjonen.

**Minstekrav:** skriv én felles handling/feltligning, angi enheter og normaliseringer, og vis hvordan hver av A/B/C faktisk gir bakgrunns- og perturbasjonsligninger. Hvis dette ikke kan gjøres, må de beskrives som uttrykk fra separate pakker, ikke som alternative realiseringer av én responsfunksjon.

---

## 2. Kildene motsier påstanden om at `E proportional sqrt(g)` er en etablert mikro-til-makro-avledning

**Berørte claim_id:** `C08`, `C09`, `C13`, `C16`

**Manuskript:** Linje 160 sier at square-root-formen «derives from» gradient-coupled grid action. Linje 186–190 omtaler KC1 som falsifikasjonskriterium, men linje 190 erkjenner at ingen fit/proveniens er levert. Linje 213 presenterer sirenformelen fra en annen relativistisk pakke.

**Kildene:**

- `docs/papers/efc/EFC_Gradient_Coupled_Grid_Action/index.json:28-71` gir en grid-action med dispersjon og `E proportional sqrt(g)` bare når `alpha*g >> kappa_0`; `:57-59` definerer en separat crossover `g_cross = kappa_0/alpha`.
- Samme kilde `:74-88` sier at ingen dataset-fit er utført (`delta_chi2=null`, `significance_sigma=null`) og at SPARC bare er «referenced; no new fit performed».
- `docs/papers/efc/From_Grid_Microphysics_to_the_Radial_Acceleration/index.json:114-121,187-192` sier uttrykkelig at modellen er kinematisk, uten dynamikk, uten QFT, uten kosmologisk avledning, og at `a0` er målt, ikke predikert.
- `docs/papers/efc/Covariant_EFT_for_Entropy_Driven_Gravitational_Modification_Construction_Constraints/index.json:235-241,243-249` sier at den klassiske handlingen gir feil fortegn mot RAR, og at BE-formen er **postulated as effective relation**, ikke derivert fra den klassiske handlingen.

**Angrep:** Manuskriptets formulering i linje 160 er for sterk i forhold til kildene. Grid-pakken viser en lokal dispersjonsgrense under en eksplisitt regimebetingelse; den viser ikke at denne graden av frihet er samme felt eller samme handling som den relativistiske `F(phi)R + K(rho) + lambda(Box phi-Gamma)`-modellen. Den manglende broen er ikke bare «ingen empirisk test». Kildene erklærer et teoretisk mikro-til-makro-gap og en klassisk feilretning. Å kalle E-aksen en «derived» realisering, samtidig som den makroskopiske BE-responsen i kildens EFT er postulatert, blander en avledet lokal skalering med en avledet gravitasjonsrespons.

KC1 har dessuten et implikasjonsgap: `mu_linear` versus `mu_sqrt` er en preferanse mellom fenomenologiske funksjoner. Kilden `31941465/index.json:102-107` sier at en slik preferanse ved `>=5 sigma` falsifiserer teoremet `E proportional sqrt(g)`, men ingen kilde viser hvorfor andre deler av modellen ikke kan gi samme `mu`-form, eller hvorfor mappingen fra mode-energi til gravitasjonsrespons er entydig. En eventuell KC1-falsifikasjon ville derfor høyst falsifisere den spesifikke `mu`-implementasjonen, ikke automatisk alle modeller med `E proportional sqrt(g)`.

**Minstekrav:** enten gi en eksplisitt felles handling og variabelmapping fra grid-modus til relativistisk respons, eller reduser `C08` til «deklarert grid-regimeskalering» og `C09` til et kill-kriterium for den konkrete `mu`-implementasjonen.

---

## 3. `a0` er ikke bare ufrosset; det er en importert kalibrering som endrer hva som kan kalles prediksjon

**Berørte claim_id:** `C13`, `C14`, `C16`

**Kilder:**

- `docs/validation-ledger/preregistrations/axis_e_sparc_rar.md:44-67` lister tre konkurrerende skalaer: `1.2e-10`, `6.5e-10` og `a0,eff=C^2 a0 approximately 5.4 a0`, og sier at testen er `INVALID until fixed`.
- `docs/papers/efc/From_Grid_Microphysics_to_the_Radial_Acceleration/index.json:41-43,129-146` definerer `a0` som en kombinasjon av mikroparametre, men sier samtidig at tallet er «measured SPARC».
- `docs/papers/efc/Covariant_EFT_for_Entropy_Driven_Gravitational_Modification_Construction_Constraints/index.json:57-60,158-166` bruker samme tall som empirisk målt SPARC-skala.
- Manuskriptet linje 211 kaller `1.2 times 10^-10` den normative screening-skalaen.

**Angrep:** Dette er mer enn et uferdig preregistreringsfelt. Kildene gir ingen uavhengig EFC-bestemmelse av `a0`; de absorberer en observert MOND/RAR-skala inn i EFC-parametrene. Når `a0` samtidig kan erstattes av en effektivt reskalert `a0,eff`, er «single scale» og «without new free parameters» ikke demonstrert. En låst `a0` etter author freeze kan gjøre testen reproducerbar, men kan ikke gjøre den til en EFC-retrodiksjon dersom tallet først er importert fra samme fenomenologi som testen skal forklare.

**Minstekrav:** skill eksplisitt mellom empirisk input, EFC-output og eventuell `a0,eff`; vis hvilken verdi som står i eksponenten; og test EFC mot MOND med samme låste normalisering. Før dette er `C14` ikke bare author-gated, men epistemisk feilklassifisert hvis den brukes som belegg for en parameterfri mikroavledning.

---

## 4. «To ortogonale akser» er ikke etablert og skjuler at den viktigste fysiske koblingen mangler

**Berørte claim_id:** `C06`, `C07`, `C16`

**Manuskript:** Linje 155–179 kaller E-eksponenten og Gamma-formen to ortogonale/independent axes og sier at begge har fremtidig diskriminant. Linje 162–174 viser bare A og C på Gamma-aksen, selv om linje 133–141 viser A, B og C. Linje 209 sier at Gamma-formen ikke har en egen preregistrert diskriminant.

**Kildestøtte:** `31941465/index.json:28-71` beskriver E-aksen i en grid-action; `31876324/index.json:28-55,147-182` legger Gamma inn i en annen relativistisk handling; `31878760/index.json:176-192` beskriver en egen mikro-til-makro-bro og oppgir at den mangler full dynamikk.

**Angrep:** «Orthogonal» krever her enten en felles parameter-/modellmatrise eller en vist faktoriseringsstruktur. Ingen kilde viser at alle kombinasjoner av E-eksponent og Gamma-form eksisterer, at valg av den ene ikke endrer feltligningene for den andre, eller at de er separat identifiserbare i noen observabel. Tvert imot kommer de fra forskjellige handlinger, regimer og statusnivåer. Aksen er derfor en organisatorisk indeks over dokumenter, ikke en fysisk koordinat i en etablert modellfamilie. At `Gamma_B` utelates fra selve aksetabellen gjør også representasjonen inkomplett.

Påstanden «each with a discriminant» er i tillegg operasjonelt asymmetrisk: E-aksen har en foreslått RAR-test, mens Gamma-aksen mangler preregistrert test. Dette undergraver `C07` som mer enn en beskrivende taksonomi.

**Minstekrav:** erstatt «orthogonal/independent» med «separate descriptive axes», eller lever en eksplisitt modellmatrise med realiserte kombinasjoner, felles likelihood og identifikasjonsanalyse. Inkluder B.

---

## 5. Sirenformelen er en klasseobservabel, ikke en EFC-spesifikk discriminator

**Berørte claim_id:** `C15`, `C16`

**Manuskript:** Linje 213 kaller `d_L^GW != d_L^EM` den «single paradigm-resistant discriminator», men sier samtidig at `alpha` og `phi_0` ikke er frosset.

**Kilde:** `docs/papers/efc/EFC_Relativistic_Action_Field_Equations_Perturbation_Theory_and_Extraction/index.json:288-301` gir formelen og kravet `|F_dot/F| << H`; `:58-70` sier at ingen data/fit er brukt. Preregistreringen `axis_dl_gw_em.md:19-34,85-91,105-109` klassifiserer uttrykket som code/metadata-supported candidate, ikke frosset numerisk prediksjon.

**Angrep:** `d_L^GW != d_L^EM` er en mulig test av modifisert tensorfriksjon, men ikke en EFC-spesifikk observasjon. Formelen er bare identifiserende etter at `F(phi)`, feltbakgrunn, normalisering, fortegn og redshiftavhengighet er frosset. Uten dette kan samme avvik tilskrives en annen running-Planck-masse-modell eller avstands-/waveform-systematikk. Manuskriptets «paradigm-resistant» er derfor en uncited overclaim, ikke en egenskap som følger av kilden.

**Minstekrav:** sammenlign EFC mot GR og minst én generisk modified-gravity-friksjonsmodell i en felles hierarkisk likelihood, med lensing, inclination, host/redshift og waveform-systematikk inkludert. Et avvik fra én er ikke i seg selv støtte for EFC.

---

## Samlet beslutning

Manuskriptet kan forsvares som en begrenset **dokument- og statusreconciliation**. Det kan ikke forsvares som en fysisk reconciliation av en modellfamilie før det leverer:

1. en felles dimensjonskonsistent mapping fra `Gamma` til feltligninger;
2. en eksplisitt bro mellom grid-actionen og den relativistiske EFT-en;
3. en avgrensning av hva som er EFC-utledet versus hentet fra SPARC/MOND-fenomenologi;
4. en modellmatrise som viser realiserte kombinasjoner av begge akser;
5. frosne parameter- og nuisance-protokoller med ΛCDM/MOND/generisk modified gravity som likeverdige alternativer.

Inntil dette er gjort, er de sterkeste påstandene `C06`, `C07`, `C08`, `C14`, `C16` ikke empirisk falsifiserte, men de er heller ikke kilde-forankret som fysiske konklusjoner. De er deklarerte organisasjons- eller modellhypoteser med åpne koblinger.
