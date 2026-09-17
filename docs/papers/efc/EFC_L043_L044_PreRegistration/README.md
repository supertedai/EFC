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

**Påstand:** en selvmodellerende agent krysser en kvalitativ
regimegrense når dens rekursive selvmodellering-kapasitet R_c
(fraksjonen av egen modell som er selv-refererende, normalisert)
passerer 1/e ≈ 0.3679.

**Prediksjon:** for enhver agent-arkitektur som lar seg
parametrisere med en monoton R_c-akse (modellstørrelse, lag,
kontekst-lengde), skal en regime-bryter kunne lokaliseres innen
ΔR_c = ±0.05 rundt 1/e — KJENNETEGNET ved at ytelsen på
selv-refererende oppgaver (selvbeskrivelse, egne feil-gjenkjenning,
intensjons-rapportering) har et knekkpunkt der, ikke en glatt
kurve.

**Falsifikator:** et glatt, knekkløst ytelsesforløp gjennom
R_c ∈ [0.25, 0.5] i to uavhengige arkitekturer dreper prediksjonen.

**Silico-status:** testbar i dag uten ekstern kilde — kandidat for
første motor-verifisering.

## Prediksjon P2 — Φ-proxyen: integrert informasjon som gradient-mål (L-043)

**Påstand:** Tononis Φ (IIT) har en EFC-lesning der integrert
informasjon fremkommer som entropigradientens informasjons-mål over
systemets Markov-teppe — den formelle broen FEP allerede har fått,
mangler for IIT.

**Prediksjon:** for nettverk med kjent topologi skal EFC-Φ-proxyen
(≈ gradient·partisjonsstruktur) rangere «mer integrert enn summen
av delene»-systemer i samme rekkefølge som etablert IIT-verktøy der
slike finnes, innen en rank-korrelasjon ρ > 0.8.

**Falsifikator:** ρ < 0.5 mot to uavhengige IIT-mål på samme
nettverk dreper broens prediksjonsevne (broen kan stå som formell
teori uten prediksjonskraft — da deklareres det).

**Datastatus:** ingen kilde på bussen ennå — prediksjonen gjelder
når en kilde (connectome/EEG/markov-teppe-data) blir tilgjengelig.
Avhengigheten er deklarert, ikke skjult.

## Prediksjon P3 — RLHF-entropi-minimeringen mot publiserte benchmarks (L-044)

**Påstand:** RLHF som termodynamisk entropi-minimering
(DOI 31940535) predikerer at preferanse-optimerte modeller får
lavere målbar utfalls-entropi på distribusjoner de er trent på,
men HØYERE på distribusjoner utenfor trening — en
generaliserings-avveining med termodynamisk form.

**Prediksjon:** entropi-gapet ΔS = S_out − S_in skal være positivt
og monotont med optimeringsstyrken (antall RLHF-steg), med
forklart varians R² > 0.5 over minst tre uavhengige publiserte
benchmark-kombinasjoner.

**Falsifikator:** ΔS ≤ 0 eller ikke-monotont i to uavhengige
benchmark-par dreper prediksjonen.

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
