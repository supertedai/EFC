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

**Aksen er FIKSAKT:** kontekst-lengden (det enkleste monotone
R_c-instrumentet i dagens arkitekturer). Ikke modellstørrelse, ikke
lag — kontekst-lengde alene.

**Prediksjon:** for DE TO FØRSTE uavhengige arkitekturene som testes
på denne aksen, skal ytelsen på selv-refererende oppgaver ha et
knekkpunkt innen ΔR_c = ±0.05 rundt 1/e ≈ 0.3679 — en regime-bryter,
ikke en glatt kurve.

**Falsifikator:** et glatt, knekkløst ytelsesforløp gjennom
R_c ∈ [0.25, 0.5] i BEGGE de to første testede arkitekturene dreper
prediksjonen. (Prediksjonen gjelder uttrykkelig bare de to første —
ikke «enhver» arkitektur; det gjør den falsifiserbar.)

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

**Referanseverktøy:** PyPhi (eller publiserte Φ-verdier fra
IIT-litteraturen) — ikke vår egen implementasjon av Φ.

**Datasett:** publiserte nettverk der IIT-verdier allerede finnes
(i silico-nettverk fra IIT-artikler). Ingen ny datainnsamling.

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
  temperatur 1.0, 5 prøver per prompt.
- In-distribusjon: prompt-bank fra modellkortets oppgitte
  treningsdomene (f.eks. MMLU-lignende). Out-distribusjon: to
  disjunkte domener (f.eks. GSM8K-lignende + en kreativ skrivebank).
- RLHF-styrke: publiserte sjekkpunkt-nummer (SFT → RLHF-steg
  k=1,2,3...). Sammenlignbare sjekkpunkter fra samme modellfamilie.
- ΔS = S_out − S_in, midlet over de to out-domenene.

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

## Forsegling

SHA-256 av denne filen ved forsegling registreres i
`docs/validation-ledger/data/evidence-register.json` og testes av
`tests/test_prereg_l043_l044.py` — endringer etter forsegling
krever et nytt dokument, ikke redigering av dette.
