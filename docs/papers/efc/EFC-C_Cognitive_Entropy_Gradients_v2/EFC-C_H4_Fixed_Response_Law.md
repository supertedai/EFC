# EFC-C H4: Fryst responslov på tvers av kognitive regimer

**Status:** formal test specification; no empirical H4 result is claimed here  
**Dato:** 2026-09-15  
**Oppgave:** `t_b9646902`  
**Kildegrunnlag:** EFC-C Track 2 package (DOI 10.6084/m9.figshare.31940505), den låste H1–H4-testprotokollen, og eksisterende `src/efc_cognition.py`.

## 1. Testpåstand og avgrensning

H4 tester om én responslov kan flyttes mellom to forhåndsdefinerte kognitive regimer ved å endre målte tilstandsvariabler, uten å estimere en ny mekanisme i testregimet.

Nullhypotesen er at responsloven er regimespesifikk: en modell som virker i kalibreringsregimet trenger ny form, nye parametre eller post-hoc terskeljustering i testregimet.

H4 er en prediktiv generaliseringstest. Den etablerer ikke at EFC-C er en fysisk teori om bevissthet, og en positiv transfer-test alene er ikke uavhengig evidens for den ontologiske tolkningen.

## 2. Notasjon og modellobjekt

La observasjon `i` ha:

- `A_i`: strukturvariabler, hentet fra dMRI/connectome (for eksempel regional styrke, gradheterogenitet og tensor-/kantvekter).
- `x_i`: målte tilstandsvariabler i det aktuelle regimet, særlig regional fMRI-LZC og eventuelt MSE. `x` måles på samme skala etter låst instrumentkalibrering.
- `q_i`: forhåndsdefinerte kovariater (alder, kjønn når relevant, motion, site, run length og signal-kvalitetsmål).
- `y_i`: responsvariabel, for eksempel regional funksjonell entropi/gradientrespons eller en forhåndsdefinert kognitiv ytelsesrespons.
- `r_i`: regimeindikator, bestemt før modelltilpasning.

EFC-C responsloven er:

```text
y_i = a + bᵀ z(A_i, x_i) + cᵀ h(A_i, x_i; θ) + dᵀ q_i + ε_i
```

`z` er den eksplisitte struktur–tilstand-interaksjonen. `h` er den fryste gradient-flow-mekanismen. `θ` er mekanismeparametrene og skal estimeres én gang i kalibreringsregimet. Den samme funksjonelle formen og samme betydning av `θ` brukes i testregimet.

### 2.1 H1-overgangsregel

H1s regimeskifte representeres av en glatt, monoton gate på den målte tilstandsvariabelen:

```text
g(x; x*, τ) = 1 / (1 + exp(-(x - x*) / τ))
```

Der:

- `x*` er terskelen for regimeovergang, estimert i kalibreringsdata eller forhåndslåst fra en separat treningskohort.
- `τ > 0` er overgangens bredde; liten `τ` gir et skarpere skifte.
- `g ∈ (0,1)` er ikke en ny mekanisme i testregimet, men den målte overgangsvekten.

Den regime-transformerte tilstanden er:

```text
T_r(x) = (1 - g(x; x*, τ)) x_low + g(x; x*, τ) x_high
```

I en normalisert implementasjon brukes i stedet `T_r(x) = g(x; x*,τ) x`; valget må registreres før kalibrering og holdes uendret. H4-modellen bruker `T_r(x)` som input til den fryste loven:

```text
ŷ_i(H4) = f_θ(A_i, T_{r_i}(x_i), q_i)
```

`x*`, `τ`, skalering, fortegn og hvilke komponenter som inngår i `A`, `x` og `q` er låste analysevalg. De kan ikke endres etter at testregimets fasit er åpnet.

## 3. Parameterbetydning og tillatte endringer

| Symbol | Betydning | Estimeres hvor? | Kan endres i testregimet? |
|---|---|---|---|
| `a` | globalt intercept/baseline | kalibrering | nei |
| `b` | struktur–tilstand-effekter | kalibrering | nei |
| `θ` | gradient-flow-mekanismens parametre | kalibrering | nei |
| `x*` | terskel i H1-gaten | kalibrering/separat treningssett | nei |
| `τ` | gatebredde | kalibrering/separat treningssett | nei |
| `d` | prespesifiserte nuisance-effekter | kalibrering | nei; kun samme kovariatsett |
| `q` | målte nuisance-kovariater | hvert individ | ja, observeres |
| `x` | målte tilstandsvariabler | hvert individ | ja, observeres |
| `r` | forhåndsdefinert regimeetikett | studiedesign | ikke post hoc |

Det eneste som skifter ved transfer er observasjonene `x`, `q` og eventuelt `A` for det nye individet; lovens form og parametrene forblir fryst. En kalibrering av en ren intercept- eller skalaoffset i testregimet teller som refitting og skal rapporteres som en separat, svekket variant — ikke som hovedtesten.

## 4. Kalibreringsregime og testregime

### 4.1 Regimevalg

Velg to regimer før tilgang til testutfall. Et eksempel er:

- `R_cal`: søvn eller hvilende våken tilstand, valgt som kalibreringsregime.
- `R_test`: våken oppgaveutførelse, valgt som testregime.

Regimene må ha ulike tilstandsfordelinger, men samme operasjonelle responsdefinisjon. Regimegrensen må defineres ved oppgave/tilstand og målt `x`, ikke ved hvor godt modellen passer.

### 4.2 Datasplitt

1. Del data på individnivå, aldri på tidsvinduer fra samme individ.
2. Hold en kalibreringskohort og en separat testkohort. Dersom begge regimer finnes hos samme individ, må individet fortsatt holdes helt ute av kalibreringssettet.
3. Bruk en intern kalibrerings-validering for å velge eventuelle hyperparametre.
4. Lås spesifikasjonen, parametrene og transformasjonen.
5. Åpne testregimet én gang for hovedanalysen.

Minimumsprotokollen fra H4 er separat kohort og separat regime. En ekstra site-/kohort-holdout er anbefalt og skal være den strengeste analysen når den finnes.

### 4.3 Hovedestimand

Primær estimand er testregimets forhåndsdefinerte out-of-sample-feil:

```text
E_cal = RMSE_cal,val eller MAE_cal,val
E_test = RMSE_test eller MAE_test
ρ_transfer = E_test / E_cal
```

Feil må beregnes på samme responsenhet, samme vekting og samme manglende-dataregel. Rapportér også prediktiv `R²`, kalibreringskurve og 95 % bootstrap-intervall med resampling på individnivå.

## 5. Låst instrumentkalibrering

Instrumentkalibrering er en del av modellen og må ikke få lov til å absorbere regimeskiftet.

Før kalibrering skal følgende låses:

- råsignalets preprocessing, filtrering, parcellering og tidsvindu;
- LZC-algoritme, symbolisering, sekvenslengde og håndtering av korte sekvenser;
- MSE-parametre dersom MSE inngår;
- dMRI-traktografi-/connectome-variant og terskling;
- regional nomenklatur og mapping mellom dMRI- og fMRI-parcellering;
- motion-/artefaktgrense, eksklusjonskriterier og missing-dataregel;
- site-/scanner-normalisering og rekkefølge på normalisering;
- hvilken kanal som er primær: fMRI-LZC. EEG/MSE er sekundær replikasjon, ikke en fri alternativ måling.

Estimer eventuelle instrumentparametre (for eksempel referansefordeling, z-skåring eller batch-korreksjon) kun i kalibreringskohorten. Anvend deretter den samme transformasjonen på testdata. Testdata må ikke brukes til å flytte middelverdi, varians, terskel eller skala.

Instrumentholdback: Gjenta analysen med en separat målemodalitet eller site som ikke bidro til kalibrering. Dette er en robusthetsanalyse, ikke tillatelse til å velge den modaliteten som gir best transfer.

## 6. Rivaler og kompleksitetsregnskap

H4 sammenlignes med minst to modeller:

1. **Regimeblind baseline (`B0`)**: samme struktur- og kovariatsett, men ingen regimegate, ingen `T_r` og ingen gradient-flow-interaksjon.
2. **Regimeindikator-modell (`B1`)**: får en fast indikator for regime, men estimerer ikke en ny mekanisme og har ikke tilstandsbasert overgang.
3. **EBH-scalar (`B2`)**: bruker bare skalar entropimagnitude, uten connectome-topologi eller gradientretning. Dette er den primære teoririvalen angitt i H4-protokollen.
4. **H4 (`M4`)**: struktur + målt tilstand + fryst H1-gate + fryst gradient-flow-lov.

For hver modell registreres:

```text
k = antall frie estimerte parametre
L = negativ log-likelihood på kalibreringsdata
AIC = 2k + 2L
BIC = k log(n) + 2L
C = k + k_regime + k_refit
```

`k_regime` teller eksplisitte regimeparametre eller regimeinteraksjoner. `k_refit` teller alle parametre som ble estimert på nytt etter at testregimet ble kjent. For hoved-H4 skal `k_refit = 0`. Et testregime-offset gir derfor en eksplisitt straff og kan ikke skjules som instrumentkalibrering.

Rapportér både:

- kalibrerings-AIC/BIC, som viser in-sample kompleksitet;
- testfeil, som er beslutningsmålet;
- differansen i feil per ekstra fri parameter;
- om kompleksitetsøkningen faktisk kjøper transfergevinst.

En regimeblind modell som matcher H4 på testfeil med færre parametre er foretrukket etter Occams regel, selv om H4 er mer fortolkbar.

## 7. Falsifikasjons- og beslutningsregel

H4 støttes bare betinget dersom alle punktene under er oppfylt:

1. `ρ_transfer ≤ 1.5` med estimert usikkerhet rapportert, i tråd med den låste H4-protokollen.
2. H4 slår den regimeblinde baseline på forhåndsdefinert testutfall etter kompleksitetsregnskap; forbedringen kan ikke komme fra post-hoc tuning.
3. Testfeilen er ikke forklart av residual motion, site, signal-kvalitet eller forskjell i måleprotokoll.
4. Parametrenes betydning og fortegn er bevart; bare målte `x`, `q` og `A` varierer mellom regimer.
5. Resultatet overlever den separate kohort-/site-holdouten.

H4 falsifiseres for den spesifiserte responsen hvis minst ett av følgende er robust:

- `ρ_transfer > 1.5` og feilen ikke skyldes en forhåndsdefinert datakvalitetsfeil;
- testregimet krever ny funksjonell form, nye parameterbetydninger eller terskeljustering etter fasit;
- regimeblind eller EBH-scalar rival matcher H4 uten høyere kompleksitet;
- transfergevinsten forsvinner etter låst motion-/site-korreksjon;
- instrumentholdouten reverserer eller opphever effekten.

Et mislykket transferforsøk falsifiserer denne EFC-C-responsloven under den valgte proxyen og regimeovergangen. Det falsifiserer ikke automatisk all EFC-C eller alle andre proxyer.

## 8. Rapporteringstabell

| Felt | Skal rapporteres |
|---|---|
| Kalibreringsregime | operasjonell definisjon, kohort, n |
| Testregime | operasjonell definisjon, kohort, n |
| Instrument | modalitet, estimator, preprocessing, låsing |
| Strukturinput | connectome- og parcelleringvariant |
| Gate | `x*`, `τ`, formel og kilde til terskel |
| Fryste parametre | `a`, `b`, `θ`, `d` og parameterbetydning |
| Transfer | `RMSE`, `MAE`, `R²`, `ρ_transfer`, intervall |
| Rivaler | `B0`, `B1`, `B2`, parameterantall og testfeil |
| Refitting | alle endringer; hovedtesten skal ha null |
| Holdout | separat individ/site/modalitet og resultat |
| Status | støttet, ikke støttet, eller uavklart for denne mappingen |

## 9. Hva som fortsatt er ukjent

Den eksisterende EFC-C-pakken definerer skalar neural entropiproduksjon, gradienttensor og terskelhypotese, men inneholder ikke et empirisk estimert H4-overføringsresultat eller en ferdig numerisk H1-overgangslov. Formelen over er derfor en eksplisitt testspesifikasjon og ikke en rapportert observasjon. `x*`, `τ`, den endelige responsvariabelen og nødvendig utvalgsstørrelse må låses i en preregistrering eller estimeres på en separat treningskohort før H4-testen kjøres.

## Kilder og proveniens

- EFC-C Track 2 package: `docs/papers/efc/EFC-C_A_Thermodynamic_Framework_for_Cognitive_Entropy_and_Psychiatric_Biomarkers_Track_2/README.md`, `data/framework.json`, `src/efc_cognition.py`; DOI: https://doi.org/10.6084/m9.figshare.31940505.
- Låst overordnet protokoll: `docs/papers/efc/EFC-C_Cognitive_Entropy_Gradients_v2/EFC-C_Hypothesis_Testing_Protocol.md` (parent task `t_5ca5e0aa`, 2026-09-15).
