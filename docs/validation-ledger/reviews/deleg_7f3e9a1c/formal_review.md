# Formal review — matematikk og logikk

**Rolle:** blind reviewer, formalist  
**Kilde:** `docs/papers/efc/EFC_Model_Family_Reconciliation/EFC_Model_Family_Reconciliation.tex`  
**Dekning:** hele manuskriptet, med hovedvekt på linje 127–179 og 206–214.

## Kort konklusjon

Manuskriptets viktigste formelle problem er at `\Gamma_A`, `\Gamma_B` og `\Gamma_C` presenteres som alternative realiseringer av samme `\Gamma(\rho)` uten en eksplisitt felles dimensjonskonvensjon. Med vanlig dimensjonell tolkning er `\Gamma_A` og `\Gamma_C` dimensjonsløse, mens `\Gamma_B` har dimensjon `\sqrt{[\rho]}` (eller `\sqrt{[\rho_c]}` som valgt referanseskala). Dermed kan de ikke sammenlignes eller settes inn i samme definisjon av `\sigma_s` uten en ekstra normaliseringsfaktor eller separate definisjoner av `S`.

Påstanden om «to ortogonale akser» er nyttig som taksonomi, men «ortogonal» er ikke matematisk definert. I tillegg utelater tabellen `\Gamma_B` fra `\Gamma`-aksen, og manuskriptet hevder både at hver akse har en fremtidig diskriminant og at `\Gamma`-formen foreløpig ikke har en egen preregistrert diskriminant. B→B+-språket er rimelig forsiktig i konklusjonen, men «companion upgrade» gir ikke i seg selv en implikasjon om supersession, ekvivalens eller fysisk forbedring.

## Funn

### FORM-001 — Dimensjonsinkonsistens mellom `\Gamma_A`, `\Gamma_B` og `\Gamma_C`

- **claim_id:** `FORM-001`
- **alvorlighet:** Høy
- **angriper/støtter:** Angriper påstanden i linje 133–141 om at de tre uttrykkene er alternative former av samme `\Gamma(\rho)`.
- **Eksakt tekst/ligning:**
  - Linje 127–131: `\Gamma(\rho) \equiv \mathrm{d}S/\mathrm{d}\rho` og `\sigma_s=\Gamma(\rho)\dot\rho`.
  - Linje 135–140:
    ```tex
    \Gamma_A(\rho) = \frac{\rho}{\rho + \rho_{\mathrm{crit}}},
    \qquad
    \Gamma_B(\rho) = \frac{\rho^{3/2}}{\rho + \rho_{\mathrm{crit}}},
    \qquad
    \Gamma_C(\rho) = \frac{\sqrt{\rho/\rho_{\mathrm{crit}}}}{1 + \sqrt{\rho/\rho_{\mathrm{crit}}}}.
    ```
- **Matematisk detalj:** For `\rho` og `\rho_{\rm crit}` med samme dimensjon `[\rho]` får man
  ` [\Gamma_A]=1`, ` [\Gamma_C]=1`, men
  ` [\Gamma_B]=[\rho]^{3/2}/[\rho]=[\rho]^{1/2}`.
  Å skrive dette som `\sqrt{[\rho_c]}` er bare valg av referanseskala; dimensjonen er fortsatt ikke én. `\Gamma_B` kan derfor ikke uten videre være samme type funksjon som `\Gamma_A` og `\Gamma_C`, og en lineær kombinasjon, rangering eller felles tabell av formene er dimensjonelt underbestemt.
- **Foreslått rettelse:** Velg og skriv eksplisitt én av disse konvensjonene:
  1. Definer en dimensjonsløs tetthet `x=\rho/\rho_c` og bruk dimensjonsløse former, for eksempel `\widetilde\Gamma_B=x^{3/2}/(1+x)`; eller
  2. Behold `\Gamma_B`, men innfør en fast skala `\rho_*^{-1/2}` (eller tilsvarende) slik at `\Gamma_B^{\rm norm}=\rho_*^{-1/2}\rho^{3/2}/(\rho+\rho_c)`; eller
  3. Erklær at A/C og B ikke er samme dimensjonale observabel, og gi separate definisjoner av `S` og `\Gamma`.
  Oppgi også enhetskonvensjonen i avsnittet før ligningene. Ikke kall formene alternative realiseringer av én funksjon før dette er gjort.

### FORM-002 — `\sigma_s=\Gamma\dot\rho` er bare konsistent under en uuttalt felles definisjon av `S`

- **claim_id:** `FORM-002`
- **alvorlighet:** Høy
- **angriper/støtter:** Angriper den ubetingede formuleringen «(chain rule)» i linje 127–131; støtter at formelen er korrekt for hver enkelt modell etter en eksplisitt definisjon.
- **Eksakt tekst:** Linje 131: `with the associated entropy production rate $\sigma_s = \Gamma(\rho)\,\dot{\rho}$ (chain rule).`
- **Matematisk detalj:** Selve kjerneregelen gir `\dot S=(\mathrm dS/\mathrm d\rho)\dot\rho`, altså dimensjon `[S]/T`. For `\Gamma_A` og `\Gamma_C` dimensjonsløse følger dette at `[S]=[\rho]`. For `\Gamma_B` følger det i stedet at `[S]=[\rho]^{3/2}` hvis ligningen skal ha samme status. Da kan alle tre ikke samtidig være derivater av den samme entropifunksjonen `S(\rho)` med én felles dimensjon. Hvis `\sigma_s` skal være en entropiproduksjon per volum/tid, må dessuten dimensjonen til `S` og eventuell volumkonvensjon angis; kjerneregelen alene etablerer ikke dette.
- **Foreslått rettelse:** Skriv enten `\sigma_s=\dot S` og definer separate, dimensjonalt konsistente `S_A,S_B,S_C`, eller normaliser `\Gamma_B` slik at alle `\Gamma` har samme dimensjon. Oppgi hva `S` betyr (entropi, entropitetthet eller dimensjonsløs entropivariabel) og enheten til `\sigma_s`. Påstanden «chain rule» bør begrenses til modeller der `S(\rho)` faktisk er definert og differensierbar.

### FORM-003 — «To ortogonale akser» er ikke matematisk definert, og `\Gamma_B` mangler i aksetabellen

- **claim_id:** `FORM-003`
- **alvorlighet:** Middels–høy
- **angriper/støtter:** Angriper linje 155–179, særlig «These two axes are independent» og tabellens påstand om at den oppsummerer modellfamilien.
- **Eksakt tekst:**
  - Linje 158: «two orthogonal model-family axes» og «two independent choices».
  - Linje 162: `\Gamma`-aksen beskrives med A-formen og C-formen.
  - Linje 171–174: tabellen lister bare saturating `\rho/(\rho+\rho_{\rm crit})` og square-root-formen.
  - Linje 177: «The two orthogonal model-family axes.»
- **Matematisk detalj:** «Uavhengig» kan bety en kartesisk produktstruktur, men «ortogonal» krever normalt et definert parameterrom og en metrikk/indreprodukt. Ingen slik struktur, kombinatorisk modellmatrise eller felles generativ modell er gitt. Det er derfor ikke vist at alle fire kombinasjoner (`\alpha\in\{1,1/2\}` med hver tillatt `\Gamma`-form) eksisterer, eller at valg av `\alpha` ikke påvirker tetthetsresponsen gjennom delte dynamiske antakelser. Dessuten finnes tre realiserte former i linje 133–141, men `\Gamma_B` er utelatt fra den påståtte `\Gamma`-aksen. Dette gjør aksen ufullstendig og kan skjule at B/B+ ikke bare er A/C med en annen koordinat.
- **Foreslått rettelse:** Bytt «orthogonal» til «separate/descriptive axes» med mindre et parameterrom og en uavhengighetsdefinisjon gis. Lag en eksplisitt modellmatrise med alle former, inkludert B, og marker hvilke kombinasjoner som faktisk er realisert versus bare logisk mulige. Vis enten en felles likelihood/generativ modell som faktoriserer valgene, eller formuler påstanden svakere: «manuskriptet organiserer corpuset langs to foreløpig separerte kategorier; fysisk uavhengighet er ikke demonstrert.»

### FORM-004 — Intern motsigelse om diskriminant for `\Gamma`-aksen

- **claim_id:** `FORM-004`
- **alvorlighet:** Middels
- **angriper/støtter:** Angriper linje 158 og 160–164; støtter den mer forsiktige formuleringen i linje 209.
- **Eksakt tekst:**
  - Linje 158: «each with a discriminant that a future test must select between».
  - Linje 209: «The `\Gamma`-shape axis has no preregistered discriminator of its own as yet».
- **Matematisk/logisk detalj:** En akse kan konseptuelt ha mulige diskriminerende observabler uten at en test er preregistrert, men manuskriptet skiller ikke mellom disse to betydningene. Slik teksten står, leses «each with a discriminant» som en faktisk definert fremtidig test, mens linje 209 nekter at `\Gamma`-aksen har en egen preregistrert diskriminant. Dette svekker påstanden om at aksene allerede er parallelle og operasjonelt symmetriske.
- **Foreslått rettelse:** Skriv «each is intended to admit a future discriminator» og presiser at bare `E`-aksen har en foreslått/preregisteringsnær test. Alternativt definer en konkret test for `\Gamma_A/\Gamma_B/\Gamma_C`, med observable, parameterfrysning og beslutningsregel.

### FORM-005 — Gjenbruk av `\alpha` skaper en skjult identifikasjonsantakelse

- **claim_id:** `FORM-005`
- **alvorlighet:** Middels
- **angriper/støtter:** Angriper den formelle separasjonen mellom aksene og siren-testen; ikke nødvendigvis en feil dersom symbolgjenbruket er tilsiktet og definert.
- **Eksakt tekst:**
  - Linje 160: `E \propto g^{\alpha}`, med `\alpha=1` eller `\alpha=1/2`.
  - Linje 213: `F(\phi)=1+\alpha\phi`.
- **Matematisk detalj:** Samme symbol `\alpha` brukes først som BE-/screeningseksponent og senere som koblingskoeffisient i en relativistisk kinetisk funksjon. Manuskriptet sier at disse aksene ikke skal blandes, men notasjonen inviterer nettopp til identifikasjon. Hvis de er samme parameter, er aksene ikke åpenbart uavhengige; hvis de er ulike, er uttrykket tvetydig og sirenprediksjonen mangler dimensjonsinformasjon (`[\alpha\phi]=1`).
- **Foreslått rettelse:** Bruk distinkte symboler, for eksempel `\alpha_E` for eksponenten og `\beta_F` for `F(\phi)=1+\beta_F\phi`, og oppgi `\phi`/koblingskoeffisientens dimensjon. Hvis identifikasjon er tilsiktet, skriv den som en eksplisitt modellantakelse og analyser konsekvensen for aksenes uavhengighet.

### FORM-006 — B→B+ gir ikke en logisk implikasjon om supersession

- **claim_id:** `FORM-006`
- **alvorlighet:** Middels
- **angriper/støtter:** Angriper enhver implikasjon av at «declared companion upgrade» betyr fysisk forbedring eller at B er erstattet; støtter manuskriptets eksplisitte forsiktighet i linje 147–153 og 204.
- **Eksakt tekst:**
  - Linje 148: `\Gamma_C` er «declared companion upgrade» og relasjonen til `\Gamma_B` er «not established».
  - Linje 153: «one declared-but-undemonstrated relation (B $\to$ B$^{+}$)».
  - Linje 199: «declared companion upgrade --- asserted to replace a prior form».
  - Linje 204: «declaring that B$^{+}$ supersedes B is a declared relation until a discriminating test selects between them.»
- **Matematisk/logisk detalj:** Fra at C/B+ er en ledsagende form, eller at den er «asserted to replace» B, følger verken `C`-formen som grense, en derivert korrespondanse, bedre fit, mer korrekt dimensjon, eller at B ikke lenger er tillatt. Forholdet er en metadata-/provenienspåstand, ikke en matematisk implikasjon. Dessuten er B+ ikke en åpenbar transformasjon av B: B er ikke-saturerende og dimensjonelt forskjellig fra C under de oppgitte variablene.
- **Foreslått rettelse:** Definer B→B+ som en eksplisitt hypotese/relasjon med nødvendige betingelser: mapping av variabler, normalisering, felles parameterdomene og beslutningskriterium. Bruk «proposed companion form» eller «claimed replacement» i stedet for «upgrade» med mindre en test eller derivation viser forbedring. Behold `supersession_status=not_established` og si uttrykkelig at ingen implikasjon B⇒B+ eller B+⇒¬B er etablert.

## Støttede deler

- Linje 131s kjerneregel er algebraisk korrekt **for en enkelt, eksplisitt definert** `S(\rho)` og med `\Gamma=\mathrm dS/\mathrm d\rho`.
- Linje 153, 190, 204 og 221–225 er logisk forsiktige når de sier at B→B+ ikke er demonstrert, at ingen ny fit er utført, og at ingen fysisk seleksjon hevdes.
- Forholdet `d_L^{\rm GW}/d_L^{\rm EM}=\sqrt{F(\phi_0)/F(\phi_z)}` i linje 213 er dimensjonsløst på venstresiden og formelt plausibelt dersom `F` er dimensjonsløs og positiv; dette krever likevel dimensjonskonvensjonen `[\alpha\phi]=1` og de nødvendige regularitets-/positivitetsantakelsene.

## Minimumskrav før matematisk konsistent publisering

1. Normaliser `\Gamma_B` eller erklær separate dimensjonale modellfamilier.
2. Definer dimensjonene til `S`, `\rho`, `\rho_c` og `\sigma_s` eksplisitt.
3. Utvid `\Gamma`-aksetabellen med B og skill realiserte kombinasjoner fra hypotetiske kombinasjoner.
4. Erstatt «orthogonal» med en svakere term, eller definer parameterrom, metrikk og faktorisering som underbygger ordet.
5. Skill `\alpha`-symbolene i screening- og sirenformlene.
6. Formuler B→B+ som en utestet relasjon uten implisert supersession, og oppgi en konkret test-/mappingregel dersom supersession fortsatt skal være en mulig konklusjon.
