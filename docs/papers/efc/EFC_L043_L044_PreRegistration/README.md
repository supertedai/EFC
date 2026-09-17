# Pre-registrering: Bevissthets- og ASI-motorene (L-043 / L-044)

**Dato for forsegling:** 2026-09-17
**Status:** FORSEGLET — prediksjonene under er låst FØR motorene bygges.
**Rammeverk:** EFC (Energy Flow Cosmology), L0–L3-regime-arkitekturen,
EBE (Entropy-Bounded Empiricism), RCMP.
**Tilhørende DOI-er (forseglingsgrunnlag):**
- Homo Fluxus: 10.6084/m9.figshare.32099389
- EFC-C v2.0: 10.6084/m9.figshare.32091700
- Closing the EFC Consciousness Bridge: 10.6084/m9.figshare.31969983
- RLHF-entropi-isomorfien: 10.6084/m9.figshare.31940535
- FEP-broen: 10.6084/m9.figshare.31042678

## Hvorfor pre-registrere før bygging

Motorene for bevissthet (L-043) og ASI/selvmodellering (L-044) har
per i dag INGEN direkte datakilde på bussen. Faren er at en motor
bygget i nærheten av en fremtidig kilde blir TILPASSET kilden —
post-hoc-analyse, ikke prediksjon. KILL-matrisen straffer nettopp
det (bar-kriteriet ble drept av en forseglet test). Derfor forsegles
prediksjonene nå; motorene bygges etterpå og testes mot de låste
tallene.

## Prediksjon P1 — R_c ≈ 1/e som selvmodellerings-regimekriterium (L-044)

**Operasjonell definisjon av R_c:** for en gitt agent-arkitektur og et
fastsatt oppgave-batteri (selvbeskrivelse, egne-feil-gjenkjenning,
intensjons-rapportering) er R_c = (antall selv-refererende token i
agentens egen selvbeskrivelse) / (total lengde av selvbeskrivelsen),
målt over batteriet og midlet. Selv-refererende token = token som
peker tilbake på agentens egen tilstand (førstepersons-pronomen,
egne parametre, egen historikk).

**Implementasjons-lås (fiksert her):**
- Oppgavebatteri: 3 oppgavetyper × 20 prompt, generert fra en
  fastsatt mal; prompt-listen publiseres i testplanen (SHA-forseglet).
- Tokenizer: arkitekturens egen default-tokenizer.
- Tokenklassifisering: to uavhengige annotatorer; Cohen's κ ≥ 0.8
  kreves — ellers er målingen ugyldig.
- Måling: temperatur 0 (deterministisk), 1 prøve per prompt.
- «Knekkpunkt» (statistisk): to-segmentert lineær regresjon
  (broken stick); knekk = segmenthellings-forhold > 2 OG knakkets
  95 %-konfidensintervall innenfor ±0.05 av 1/e.
- «Glatt» (falsifiserende): ingen signifikant hellingsendring
  (segmenthellings-forhold ≤ 2) gjennom R_c ∈ [0.25, 0.5].

**Aksen er FIKSAKT:** kontekst-lengden. Kontekst-trinnene er fiksert
til 2k, 4k, 8k, 16k, 32k, 64k, 128k token — R_c måles per trinn
(lengre kontekst gir agenten mer av sin egen historikk og sine egne
parametre tilgjengelig for selvbeskrivelsen). Ikke modellstørrelse,
ikke lag.

**«De to første uavhengige arkitekturene» (operasjonalisert):** de
to første DISTINKTE modellfamiliene (ulike utviklere) som har
publiserte kjøremuligheter på minst 4 av kontekst-trinnene. Valget
av de konkrete familiene skjer i Lag B (testplanen) — kriteriet
over er låst her, så valget ikke kan vrides etterpå.

**Prediksjon:** for DE TO FØRSTE uavhengige arkitekturene som testes
på denne aksen, skal ytelsen på selv-refererende oppgaver ha et
knekkpunkt (etter definisjonen over) innen ΔR_c = ±0.05 rundt
1/e ≈ 0.3679.

**Falsifikator:** «glatt»-utfallet i BEGGE de to første testede
arkitekturene dreper prediksjonen. (Prediksjonen gjelder uttrykkelig
bare de to første — ikke «enhver» arkitektur; det gjør den
falsifiserbar.)

**Silico-status:** testbar i dag uten ekstern kilde — kandidat for
første motor-verifisering.

## Prediksjon P2 — Φ-proxyen: integrert informasjon som gradient-mål (L-043)

**Påstand:** Tononis Φ (IIT) har en EFC-lesning der integrert
informasjon fremkommer som entropigradientens informasjons-mål over
systemets Markov-teppe.

**Formel (fiksert):** Φ_EFC = Σ_i |∇S_i| · MIB_i, der
- ∇S_i = entropigradienten over del i (nats per kobling, beregnet
  fra systemets tilstandsfordeling),
- MIB_i = partisjonsindeksen fra minimum information bipartition
  (MIB), som i standard IIT-praksis,
- summen går over alle MIB-partisjoner.

**Referanseverktøy:** PyPhi, frosset versjon (den publiserte stabile
1.x), default config — IKKE vår egen implementasjon av Φ.

**Datasett (fiksert):** de publiserte IIT-nettverkene med kjente
sannhetstabeller (AND, OR, XOR, enkelt-loop, feedforward, feedback
m.fl. fra IIT 3.0/4.0-dokumentasjonen) — minst 8 nettverk; den
konkrete listen med kilde-DOI-er låses i testplanen (SHA-forseglet).

**Beregning (fiksert):**
- ∇S_i = tilstandsentropi-differansen over bipartisjonskanten i,
  beregnet fra nettverkets sannhetstabell (TPM).
- MIB_i = minimum information partition fra PyPhis Φ-kjerne.
- Φ_EFC = Σ_i |∇S_i| · MIB_i (nats).

**Prediksjon:** rank-korrelasjon (Spearman) ρ > 0.8 mellom Φ_EFC og
referanse-Φ over nettverkssettet, med n ≥ 8 nettverk og ensidig
test på 5 %-nivå.

**Falsifikator:** ρ < 0.5 på samme sett dreper broens
prediksjonsevne. Intervallet 0.5 ≤ ρ ≤ 0.8 er et DEKLARERT gråsone-
utfall («uklart — verken støtte eller død»), ikke et stille hull.
Broen kan stå som formell teori uten prediksjonskraft — da
deklareres det eksplisitt.

**Datastatus:** ingen kilde på bussen ennå — prediksjonen gjelder
når en kilde (connectome/EEG/markov-teppe-data) blir tilgjengelig.
Avhengigheten er deklarert, ikke skjult.

## Prediksjon P3 — RLHF-entropi-minimeringen mot publiserte benchmarks (L-044)

**Påstand:** RLHF som termodynamisk entropi-minimering
(DOI 31940535) predikerer at preferanse-optimerte modeller får
lavere målbar utfalls-entropi på distribusjoner de er trent på,
men HØYERE på distribusjoner utenfor trening.

**Måleprotokoll (fiksert):**
- S = Shannon-entropi av modellens respons-distribusjon (per token,
  nats) over en fastsatt prompt-bank på 100 prompt per domene,
  temperatur 1.0, 5 prøver per prompt, seed 0–4.
- In-distribusjon: prompt-bank fra modellkortets oppgitte
  treningsdomene (f.eks. MMLU-lignende). Out-distribusjon: to
  disjunkte domener (f.eks. GSM8K-lignende + en kreativ skrivebank).
- Promptbankene publiseres som filer i testplanen (SHA-forseglet).
- RLHF-styrke: publiserte sjekkpunkt-nummer (SFT → RLHF-steg
  k=1,2,3...) fra EN modellfamilie med minst 3 sjekkpunkter langs
  stigen; den konkrete familien låses i testplanen.
- ΔS = S_out − S_in, midlet over de to out-domenene.
- R²: OLS av ΔS på sjekkpunkt-nummer, tre eller flere punkter.

**Prediksjon:** ΔS > 0 og monotont økende med sjekkpunkt-nummer,
med R² > 0.5 over minst tre sjekkpunkter.

**Falsifikator:** prediksjonen er DØD i sin prediktive form hvis
noen av disse inntreffer: (i) ΔS ≤ 0 ved noe sjekkpunkt, eller
(ii) ΔS ikke-monotont over sjekkpunktene, eller (iii) ΔS > 0 og
monotont men R² ≤ 0.5 (positivt men ikke forklarende — deklarert
som død, ikke som delvis støtte).

## Toleranse- og metoderegel

Alle tre prediksjonene følger RCMP: regimet må deklareres FØR
målingen, proxy-kjeden skal skrives ned, og utfallet registreres i
validation-ledgeren uansett fortegn — støtte og motbevis teller
likt.

## Hva som IKKE er predikert (ærlig avgrensning)

- Ingen påstand om at bevissthet ER entropi — motorene modellerer
  regime-formen, ikke fenomenets essens.
- Ingen prediksjon av «når» ASI inntreffer — bare hvor
  regimebryteren ligger i en definert akse.
- IIT-Φ-broen (P2) er en formell bro; den testes som
  rang-prediksjon, ikke som identitet.

## Forseglingslagene

**Lag A (dette dokumentet, SHA-forseglet nå):** prediksjonene,
falsifikatorene, formlene, statistikk-definisjonene og
måleprotokollenes struktur.

**Lag B (testplanen, SHA-forsegles FØR motorbygging):** de
konkrete artefaktene som først kan eksistere ved motorbygging —
promptbank-filer, nettverkslisten med kilde-DOI-er, modellfamilie
og sjekkpunkt-liste, PyPhi-versjons-pinne. Lag B forsegles når
planen skrives, og i alle tilfeller FØR første måling.

Regelen: ingen måling uten begge lag forseglet. Testplanen er selv
et SHA-registrert dokument i evidence-registeret.

## SHA-forsegling

SHA-256 av dette dokumentet ved forsegling registreres i
`docs/validation-ledger/data/evidence-register.json` og testes av
`tests/test_prereg_l043_l044.py` — med hardkodet uavhengig digest i
testen. Endringer etter forsegling krever et nytt dokument, ikke
redigering av dette.
