# Physics review — EFC Model-Family Reconciliation

**Rolle:** blind physics critic  
**Kilde:** `docs/papers/efc/EFC_Model_Family_Reconciliation/EFC_Model_Family_Reconciliation.tex`  
**Linjehenvisninger:** linjenummer i manuskriptet lest i denne reviewen.  
**Overordnet vurdering:** Manuskriptet er ærlig om at testene ikke er utført, men den fysiske modellen er ikke lukket nok til å etablere GR/ΛCDM-grensetilfeller eller en entydig sirenprediksjon. De alvorligste problemene er manglende kobling fra `Γ(ρ)` til feltligningene, dimensjons-/normaliseringsproblemet i `Γ_B`, og at `a₀` og sirenkoblingene ikke er frosset.

## Funn

### PHYS-GAMMA-001 — Ingen demonstrert GR/ΛCDM-grense for noen `Γ`-form

- **Alvorlighet:** Kritisk for fysisk konsistens / modellidentifikasjon.
- **Angriper/støtter:** Angriper påstanden om at de tre formene kan behandles som realisasjoner av samme effektive respons uten ytterligere dynamikk; støtter kun den begrensede proveniensbeskrivelsen.
- **Eksakt sted:** Linje 127–141 definerer `Γ(ρ)=dS/dρ` og oppgir `Γ_A`, `Γ_B`, `Γ_C`. Linje 143–153 klassifiserer dem som familie/bifurkasjon. Linje 209 sier at sirentesten ikke tester `Γ`-formen.
- **Fysisk resonnement:** En funksjon `Γ(ρ)` alene er ikke en gravitasjonsteori. Manuskriptet oppgir ikke en feltligning eller eksplisitt regel som viser hvordan `Γ` endrer Friedmann-, Poisson-, vekst- eller linselikningen. Derfor kan `Γ→0` eller `Γ→1` ikke identifiseres med henholdsvis GR eller en modifisert-gravitasjonsregime. De nødvendige grensene er matematisk:
  - `Γ_A→0` for `ρ/ρ_crit→0`, `Γ_A→1` for `ρ/ρ_crit→∞`.
  - `Γ_B→0` som `ρ^(3/2)/ρ_crit` ved lav tetthet, men `Γ_B~√ρ` ved høy tetthet og dermed ingen metning.
  - `Γ_C→0` som `√(ρ/ρ_crit)` ved lav tetthet, `Γ_C→1` ved høy tetthet.
  Ingen av disse asymptotene er koblet til `G_eff→G`, GR-bakgrunn, `Λ`CDM-ekspansjon eller standard relativistisk perturbasjonssektor. Det er dermed ikke vist at noen form har et veldefinert GR-grensetilfelle i enten `ρ≪ρ_crit` eller `ρ≫ρ_crit`.
- **Manglende grense/krav:** Oppgi den komplette effektive handlingen/feltligningene og vis eksplisitt `G_eff/G→1`, `slip→0`, `c_T→1`, standard Friedmann-dynamikk og GR-vekst i den valgte grensen. Angi også om GR skal ligge ved lav eller høy tetthet; dette følger ikke av teksten.

### PHYS-GAMMA-002 — `Γ_B` har annen dimensjon og bryter den implisitte form-ekvivalensen

- **Alvorlighet:** Høy.
- **Angriper/støtter:** Angriper linje 133–151 sin behandling av `Γ_A`, `Γ_B` og `Γ_C` som direkte sammenlignbare former for samme respons.
- **Eksakt sted:** Linje 127–131 definerer `Γ=dS/dρ`; linje 135–140 oppgir de tre uttrykkene.
- **Fysisk resonnement:** `Γ_A` og `Γ_C` er dimensjonsløse. `Γ_B=ρ^(3/2)/(ρ+ρ_crit)` har dimensjon `√ρ` dersom `ρ` og `ρ_crit` har samme tetthetsdimensjon. Hvis `Γ` virkelig er `dS/dρ`, må alle tre ha samme dimensjon, eller det må finnes en eksplisitt prefaktor/normalisering (for eksempel en referansetetthet eller entropiskala). Uten den er `Γ_B` ikke bare en annen kurveform, men en annen-dimensjonal størrelse. Påstanden i linje 131 om `σ_s=Γ·dotρ` får tilsvarende ulik dimensjon mellom scenariene.
- **Manglende grense/krav:** Definer dimensjonene til `S`, `ρ`, `Γ`, og en felles normalisering for alle scenarier. Vis at `Γ_B` er invariant under enhetsbytte og at samme fysiske parameterisering brukes i feltligningene. Hvis `Γ_B` med vilje ikke skal mettes, må høy-`ρ`-regimet og dets fysiske cutoff oppgis.

### PHYS-GAMMA-003 — Lav- og høy-tetthetsgrenser er ikke fysisk selektert

- **Alvorlighet:** Høy.
- **Angriper/støtter:** Angriper linje 146–153 sin familieklassifikasjon som om den er tilstrekkelig fysisk avklart; støtter at teksten korrekt sier at empirisk seleksjon ikke er utført.
- **Eksakt sted:** Linje 146–149 beskriver `Γ_A` som mettet, `Γ_B` som ikke-mettet og `Γ_C` som kvadratrotmettet; linje 151–153 beskriver dette som en formbifurkasjon.
- **Fysisk resonnement:** `Γ_A` og `Γ_C` har samme endepunkter (`0→1`) men ulik overgangsrate; `Γ_B` har et annet høy-ρ-endepunkt (`∞`). Dersom `Γ` representerer en fysisk respons som skal være begrenset, er `Γ_B` patologisk uten en ny skala eller regulator. Dersom `Γ` ikke representerer en direkte koblingsstyrke, må teksten si hva som tillater divergensen. En «companion upgrade» er ikke en fysisk begrunnelse for endret asymptotikk.
- **Manglende grense/krav:** For hver form: oppgi stabilitets-, positivitet- og regularitetsbetingelser, fysisk domene, valgt GR-regime og eventuelt cutoff. Vis at bakgrunns- og perturbasjonsligninger er endelige i begge tetthetsgrenser.

### PHYS-A0-001 — MOND-`a₀` blandes med EFC-parametere og er ikke frosset

- **Alvorlighet:** Høy for testens falsifiserbarhet; middels for ren dimensjonskonsistens.
- **Angriper/støtter:** Angriper formuleringen i linje 211 om et «normativt screening scale»; støtter at teksten faktisk erkjenner author-gating og anti-shopping-problemet.
- **Eksakt sted:** Linje 186 bruker `a₀` i KC1; linje 211 fastsetter foreløpig `a₀=1.2×10^{-10} m s^{-2}`; linje 213 sier at sirenparametre ikke er frosset. Den tilhørende preregistreringen (`axis_e_sparc_rar.md`, linje 48–56) oppgir dessuten `1.2e-10`, `6.5e-10` og `a₀,eff=C²a₀≈5.4a₀` som konkurrerende kandidater.
- **Fysisk resonnement:** `1.2×10^{-10} m s^{-2}` er den empiriske MOND-akselerasjonsskalaen, ikke automatisk en EFC-derivert konstant. Hvis EFC bruker samme tall, må det enten utledes fra EFC-parametere eller behandles som en lånt/fittet kalibrering. `a₀,eff=C²a₀` viser at en normaliseringskonstant kan flytte den effektive overgangsskalaen; da er det ikke nok å kalle grunnverdien «normativ» uten å spesifisere hvilken akselerasjon som står i eksponenten og hvor `C` kommer fra.
- **Manglende grense/krav:** Frys én verdi før fitting, definer om `a₀` er MOND-input, EFC-output eller nuisance-parameter, og utled forholdet mellom `a₀`, `a₀,eff` og alle øvrige normaliseringer. Rapporter en dimensjonsløs parameterisering (`g/a₀`) og en uavhengig bestemmelse av baryonisk masse/M/L.

### PHYS-A0-002 — BE-screeningen er ikke vist å ha riktig MOND/RAR-asymptotikk

- **Alvorlighet:** Høy.
- **Angriper/støtter:** Angriper at `a₀`-låsing alene gjør SPARC-testen til en fysisk retrodiksjon; støtter at manuskriptet korrekt skiller testen fra `Γ`-aksen.
- **Eksakt sted:** Linje 186 omtaler `μ(g)=1/(exp(g/a₀)-1)` som lineær eksponent; linje 160 omtaler `E∝g^α`; linje 211 omtaler SPARC/RAR-retrodiksjonen. Den eksplisitte konkurransen er dokumentert i `axis_e_sparc_rar.md`, linje 12–24.
- **Fysisk resonnement:** For `g≪a₀` gir den lineære formen `μ≈a₀/g`, mens kvadratrotformen gir `μ≈√(a₀/g)`. Dette kan bare sammenlignes med RAR dersom `g` og `μ` er entydig definert. Preregistreringen definerer `μ=g_obs/g_bar`; med `g=g_bar` har kvadratrotformen riktig type dyp-MOND/RAR-skalering (`μ∝√(a₀/g_bar)`), mens lineærformen har en annen potens (`∝g_bar^{-1}`). Hvis `g` derimot er `g_obs`, blir sammenligningen en annen. Manuskriptet selv oppgir ikke denne identifikasjonen eller en avledning fra BE-operatoren til `g_obs/g_bar`.
- **Manglende grense/krav:** Skriv eksplisitt hvilken akselerasjon som står i eksponenten, utled `g_obs(g_bar)` og vis Newtonsk grense (`g≫a₀`) og dyp-MOND-grense (`g≪a₀`). Kontroller også at `μ` ikke divergerer på en måte som gjør den til feil type interpolasjonsfunksjon.

### PHYS-SIREN-001 — `d_L^{GW}≠d_L^{EM}` er en gyldig observabelklasse, men ikke en lukket EFC-prediksjon

- **Alvorlighet:** Kritisk for påstanden om en spesifikk diskriminator; ikke nødvendigvis fatal for en fremtidig test.
- **Angriper/støtter:** Angriper siste del av linje 213 («single paradigm-resistant discriminator»); støtter linje 213 og linje 217–225 i at testen er uprøvd og ikke skal kalles bekreftelse.
- **Eksakt sted:** Linje 213 oppgir `d_L^{GW}/d_L^{EM}=√[F(φ₀)/F(φ_z)]`, `F(φ)=1+αφ`, og sier at `α,φ₀` ikke er frosset. Linje 209 sier samtidig at sirentesten ikke tester `Γ`-formen. Preregistreringen `axis_dl_gw_em.md`, linje 29–34, kaller uttrykket code/metadata-supported og parameterne illustrative defaults.
- **Fysisk resonnement:** En avvikende GW-luminositetsdistanse er en veldefinert observable i teorier med modifisert tensorfriksjon, men ulikhet alene er ikke spesifikk for EFC. Den oppgitte ratioen trenger en eksplisitt kovariant handling, tensorbølge-ligning og definisjon av `F` som effektiv Planck-massefunksjon. Det må også vises at `F>0`, at `φ` er en bakgrunnsfeltløsning, og at kilde-/detektorendepunktene gir akkurat den oppgitte retningen på ratioen. Et `r(z)`-avvik tester derfor en propagasjonssektor, ikke `Γ(ρ)` eller EFC som helhet.
- **Manglende grense/krav:** Vis GR-grensen `F(φ_z)=F(φ₀)` (eller `α→0`) som gir `r(z)→1`, og oppgi full bakgrunnsløsning `φ(z)`. Frys parametere og priorer før data. Definer en alternativmodelltelling som skiller EFC fra generisk modified-gravity friction.

### PHYS-SIREN-002 — `F(φ)=1+αφ` er bare dimensjonelt forsvarlig etter eksplisitt felt-normalisering

- **Alvorlighet:** Høy.
- **Angriper/støtter:** Angriper linje 213 som presentasjon av en komplett fysisk form; støtter uttrykket som en mulig effektiv parameterisering.
- **Eksakt sted:** Linje 213; preregistrering `axis_dl_gw_em.md`, linje 23–33 og 107–109.
- **Fysisk resonnement:** `F` må være dimensjonsløs og positiv. Hvis `φ` er et dimensjonert skalarfelt, må `α` ha inverse felt-enheter; hvis `φ` er dimensjonsløst, må dette erklæres. Feltreskalering `φ→Cφ` og `α→α/C` etterlater produktet `αφ` uendret. Derfor kan sirendata alene ikke identifisere `α` og felt-normaliseringen separat. I tillegg er en lineær `F` potensielt negativ for enkelte feltverdier og krever et eksplisitt tillatt domene.
- **Manglende grense/krav:** Angi feltets dimensjon, kanonisk normalisering, enheter og positivitetdomene for `F`; vis at parameteriseringen følger fra handlingen og ikke bare fra kode. Oppgi hvordan `φ₀` og `φ_z` beregnes.

### PHYS-DEG-001 — Sirenratioen har en fundamental endepunktsdegenerasjon

- **Alvorlighet:** Høy.
- **Angriper/støtter:** Angriper tolkningen av et eventuelt målt avvik som direkte måling av `α`; støtter at testen kan falsifisere en bestemt frosset funksjon.
- **Eksakt sted:** Linje 213 og preregistrering `axis_dl_gw_em.md`, linje 38–49.
- **Fysisk resonnement:** Observasjonen måler i første omgang `ln r(z)=½[ln F(φ₀)-ln F(φ_z)]`, altså et forhold mellom endpoint-verdier. Den bestemmer ikke separat `α`, `φ₀`, `φ_z`, feltets initialbetingelse eller eventuell skjerming. Selv lineariseringen `r≈1-(α/2)(φ_z-φ₀)` måler bare produktet `αΔφ`. Et avvik kan også degenerere med lensing, waveform-amplitude systematics, inclination, host/redshift-feil og EM-distance-kalibrering.
- **Manglende grense/krav:** Frys eller marginaliser hele feltbakgrunnen og alle amplitude-/distance-systematics i en felles likelihood. Demonstrer identifikasjon med flere redshift-bin og en eksplisitt nulltest; ikke rapporter `α` som målt uten en feltmodell.

### PHYS-DEG-002 — SPARC/RAR-testen har M/L-, avstands- og formdegenerasjoner

- **Alvorlighet:** Høy.
- **Angriper/støtter:** Angriper formuleringen i linje 211 om en ren locked-`a₀` retrodiksjon; støtter preregistreringens egen innrømmelse av at testen bare er «lean», ikke paradigm-free.
- **Eksakt sted:** Linje 211; preregistrering `axis_e_sparc_rar.md`, linje 37–42 og 61–75.
- **Fysisk resonnement:** `g_bar` er avledet fra baryonisk massemodell, avstand, gassmodell og stjerne-M/L; `g_obs` påvirkes av inklinasjon og systematiske rotasjonskurveeffekter. Fri eller etterjustert M/L kan absorbere forskjellen mellom lineær og kvadratrot-BE-form, mens `a₀` kan kompensere for masse- og avstandsskala. Derfor er låst `a₀` nødvendig, men ikke tilstrekkelig for en diskriminerende test.
- **Manglende grense/krav:** Frys M/L-prior, distanser, inklinasjon og gassmodell før likelihood; bruk samme nuisance-modell og holdout for begge eksponenter. Rapporter parameterkorrelasjoner og vis at preferansen ikke forsvinner når baryoniske systematikker marginaliseres.

### PHYS-DEG-003 — Kosmologiske parametere kan absorbere en bakgrunnsrespons

- **Alvorlighet:** Middels–høy.
- **Angriper/støtter:** Angriper implisitt fysisk diskriminasjon mellom EFC og `Λ`CDM når `Γ` ikke er koblet til bakgrunnsligningene; støtter manuskriptets begrensede påstand om at ingen fit er utført.
- **Eksakt sted:** Linje 87–91 beskriver modellfamilien; linje 209–213 skiller siren- og SPARC-aksene; linje 220–225 sier at ingen ny fit er utført.
- **Fysisk resonnement:** Dersom `Γ(ρ)` endrer bakgrunnsekspansjon eller effektiv gravitasjonsstyrke, kan effekten delvis absorberes av `Ω_m`, `H_0`, baryonfraksjon, mørk-energi-/`Λ`-parametere eller en fri overgangsskala `ρ_crit`. Uten en felles likelihood med eksplisitte priors og samme observables er det ikke mulig å vite om den observerte effekten er en ny fysisk respons eller en omdefinert standardparameter.
- **Manglende grense/krav:** Skriv bakgrunnsligningene, vis parameterkartet til `Λ`CDM (`Γ`-kobling av, eller relevant grense), og test EFC mot `Λ`CDM med samme nuisance- og priorstruktur. `ρ_crit` må enten være uavhengig bestemt eller telles som fri modellparameter.

## Støttende observasjon

- Manuskriptet er metodisk korrekt når det eksplisitt sier at ingen ny fit er utført (linje 217–226), at `Γ`-akse og `E`-akse ikke skal blandes (linje 155–164), og at sirentesten ikke avgjør `Γ`-formen (linje 209, 213). Dette reduserer evidens-overclaim, men erstatter ikke manglende feltligninger og grensetilfeller.

## Minimumskrav før fysisk konsistens kan hevdes

1. Gi én dimensjonskonsistent handling/feltligning som kobler `Γ` til observabler.
2. Velg og vis eksplisitt GR/ΛCDM-grense for alle tre `Γ`-formene, inkludert perturbasjoner og stabilitet.
3. Frys `a₀` og skill MOND-kalibrering fra enhver EFC-derivert `a₀,eff`.
4. Utled RAR-asymptotikk fra den oppgitte BE-formen med entydig definisjon av `g` og `μ`.
5. Deriver sirenratioen fra handlingen, spesifiser feltets enheter/normalisering og frys `α,φ(z)`-modellen.
6. Kvantifiser M/L-, cosmologi-, feltreskalering- og amplitude-systematikker i samme likelihood.

**Konklusjon:** Manuskriptet kan stå som en provenance-/statusreconciliation, men ikke som en fysisk lukket modellreconciliation. Per de eksplisitte tekstene er `Γ_A`, `Γ_B`, `Γ_C` og sirenformelen kandidatrepresentasjoner; ingen av dem har et demonstrert GR-grensetilfelle, og sirenuttrykket er foreløpig en ikke-frosset, dimensjonsmessig ufullstendig parameterisering snarere enn en numerisk EFC-prediksjon.
