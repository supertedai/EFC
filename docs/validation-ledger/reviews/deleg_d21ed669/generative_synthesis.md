# Generativ syntese — fem sømmer, fire pakker, ett nav

artifact_type: orchestrator_generative_synthesis
not_reviewer_output: true
run_id: deleg_d21ed669
delegation_id: deleg_90025b05
model: gpt-5.6-luna (alle fem; enighet = reading consistency, IKKE uavhengig validering)
status: IKKE funn, IKKE verdict, IKKE claim-status — kandidat-hypoteser til ny claim-map-runde

---

## Navet (ett spørsmål driver alt)

> **Hvilket fysisk objekt — med hvilken enhet, normalisering, tetthetsvariabel og observabel — kalles Γ i hver gren?**

Tre sømmer stråler ut fra det:

1. **Γ-sømmen** — form A/B/C + BE-normaliseringen
2. **a₀-sømmen** — MOND-input → lattice-prefaktor → kosmisk skala
3. **Transport-sømmen** — statisk galaktisk respons vs relativistisk kosmologisk felt

---

## Pakke 1 · Γ-responskjernen (formen, dimensjonen, fase-vs-artefakt)

**Hører sammen:** Γ_A, Γ_B, Γ_C, BE-variabelen x, u=ρ/ρcrit, l_g, β, fortegn/enhet/normalisering.

**Verifisert algebra:** f(q)=q/(1+q) → Γ_A=f(u), Γ_C=f(√u), Γ_B=√u·f(u).

**Det skarpe funnet (sa-0):** et reelt dimensjonshull. β=4πG_N/3 mangler referanselengden r_* (som står i docstringen men ikke i koden), så x²/u = 4π/(3·l_g) = **2.59e35 m⁻¹** ved l_g=Planck. √u=x krever l_g=4π/3 ≈ 4.19 m. Koordinat-identiteten er derfor **dimensjonelt blokkert**, ikke etablert.

**Korreksjon av mitt stillas (viktig):** at Γ_B divergerer som √u mens A/C metter, beviser at B er en *annen funksjon* — men **ikke** at B er en separat fase. sa-2 fant at kildene bruker A/B/C på **overlappende domener** og beskriver A som en effektiv approksimasjon til B; ingen u→S-mapping finnes. Γ_B's √u-vekst er en **høy-u-ekstrapolasjonsartefakt**, ikke en S→1-fasegrense.

**Status:** A/B/C = overlappende konkurrerende former for samme Γ(ρ)-mål; modellseleksjon ueksekvert (delta_chi2=null i alle pakker). Separat fase = hypotese, ikke kildeunderstøttet.

**Falsifikator:** frys én Γ0, ρcrit, l_g, β, enhet, observabel; kjør A/B/C mot samme data + nuisance + likelihood.

---

## Pakke 2 · a₀-stigen (fem verdier, C=2.32 fit-ikke-avledet)

**Hører sammen:** alle akselerasjonsskalaene + «5.4× MOND»-påstanden.

**Provenienstabell (sa-1):**

| Verdi | Opphav | Status |
|---|---|---|
| 1.2e-10 | MOND/SPARC-input (a0_base) | empirisk importert |
| 1.1e-10 | Verlinde 2016-skala | ekstern ramme |
| 6.5e-10 | EFC atlasverdi, sealed=false/flag | ikke frosset |
| 6.459e-10 | C²·a₀ = 2.32²·1.2e-10 | algebraisk reskalering |
| 9.469e-10 | c²√Λ (lambda_screening.py faktisk) | separat Λ-rute |
| 5.097e-9 | C²·c²√Λ | enda en rute |
| 6.544e-10 | cH₀(67.36) | kosmisk referanse |

**Det avgjørende (sa-1):** C=2.32 er **numerisk konvergert** (2.443→2.354→2.320) men **ikke analytisk avledet** — ingen Watson-integral/Green-funksjonsderivasjon finnes i repoet. En separat ledger-rute gir C_vw=2.2895.

**Derfor:** `a₀,eff=C²a₀` er en **beregnet reskalering**, ikke en fri prediksjon. «EFC predikerer 5.4× MOND» er for sterkt. Den numeriske nærheten (atlas 6.5e-10 = cH₀ til 0,7 %, C²a₀ til 1,3 %) er **ikke-uavhengig**: a₀ er MOND/SPARC-input, C er intern lattice-måling, atlasverdien er selv uavklart.

**Falsifikator:** utled C fra kubisk Green-funksjon/Watson-integral uten H₀/Λ/SPARC i input; varier H₀ og Λ uavhengig og se om C står fast.

---

## Pakke 3 · Den brutte broen (grid → RAR → relativistisk)

**Hører sammen:** S_grid, κeff=κ0+αg, E∝√g, μ_BE(g), G_eff(g), RAR, φ, □φ=Γrel(ρ), μ(k,z), Σ, η, dL^GW/dL^EM.

**Dette er IKKE én kjede — det er to, med et brudd:**

1. **grid→RAR** (mest sammenhengende mikrokjede, men bare til galaktisk respons): grid-action→mode `verified`; mode→BE→RAR `declared` (kilden sier selv at BE-occupation er input og a₀ ikke er avledet).
2. **relativistisk→kosmologi** (ny gren): `declared`, ikke eksekvert (datasets_used=[]).

**To skarpe funn (sa-3):**

- **Fortegn/trend-kontradiksjon:** den kovariante EFT-en (31878334) gir en klassisk korreksjon som **øker** med g; den galaktiske responsen μ_BE(g) må **avta**. Kilden sier selv at μ_BE måtte postuleres for hånd fordi den klassiske virkningen ga feil trend. Edge: `contradicted`.
- **Objekt-/enhetsbrudd:** Γ i □φ=Γ(ρ) har enhet [1/tid], positiv, mettende. dS/dρ er **negativ** under synkende tetthet (dn/dρ<0). Samme greske bokstav, to ulike objekter. Edge: `contradicted` (inntil typed map foreligger).

**√g-eksponenten overlever ikke** inn i den relativistiske handlingen som samme objekt (√(-g) der er metrisk mål, urelatert til E∝√g). Edge: `open_mapping`.

**Sirenen (dL^GW/dL^EM) må holdes separat** — den er en erklært relativistisk prediksjon, ikke en konsekvens av RAR eller lattice-Γ.

**Falsifikator:** én kovariant reduksjon S_grid→relativistisk handling + Newton-grense som gir samme μ_BE(g); typed map ξ→φ og (m_eff,κ0,α,lg,a₀)→(F,K,V,λ,Γ).

---

## Pakke 4 · Paradigmekartet (ΛCDM / MOND / EFC som målekart)

**Hører sammen:** koordinatkart, measurand, instrument, proxy, nuisance, regime/fase, likelihood, out-of-sample.

**Status for recovery-kantene (sa-4):**

- **EFC→ΛCDM (L0/L1):** `declared_formal_limit`, delvis sektorstøtte, **ikke** equal-footing empirisk recovery. Overlapp på H₀-bakgrunn; CMB pending (Boltzmann-solver). fσ8-drift: 0.430 (EFC) vs 0.449/0.452 (ΛCDM).
- **EFC→MOND (L3):** `declared_deep_MOND_limit`, fenomenologisk RAR-overlapp, **ikke** matematisk limit; a₀-avvik ~5× uløst (6.5e-10 vs 1.2e-10). Bullet: EFC 0.9993 vs MOND 0.

**Dette er brukerens eget krav, gjort konkret:** MOND/ΛCDM/EFC er tolkningsforskjeller via ulike instrumenter/proxyer på overlappende data — men det er **ikke bevist** at de er samme sannhet før de kjøres i én felles målekjede. RECOVERED_BY_LIMIT_OF er i dag en atlas-deklarasjon, ikke en utført likelihood.

**Kalibreringsfrie diskriminatorer (holdout, ikke løse observabler):**

1. **L0/L1:** E_G-statistikk (felles SO/Euclid-data, covarians, nuisance, instrument).
2. **L3/RAR:** SPARC/RAR med frosset a₀ + felles M/L-priorer.
3. **Bullet:** Δκ som holdout.
4. **Dynamikk:** fσ8, BAO, k-avhengig vekst.
5. **Relativistisk:** lensing-slip + sireneforhold.

---

## Korreksjoner til mitt eget stillas (gjort, synlig)

1. **G4 var for sterk:** «disjunkte regimer» → «overlappende konkurrerende former, modellseleksjon ueksekvert». Divergensen til B er funksjonsforskjell, ikke fasebevis.
2. **F1 ommerket** (kode-struktur, ikke oppdaget fysisk forening).
3. **F2 ommerket** (C=2.32 er fit, ikke avledet; a₀~cH₀ er arv, ikke EFC-funn).

## Kandidat-claims til NY claim-map-versjon (atomisert)

- C-Γ1: Γ_A/B/C deler metningskjerne f men er overlappende former (ikke disjunkte faser).
- C-Γ2: BE-normaliseringen er dimensjonelt ufullstendig (β mangler r_*).
- C-a₀1: a₀ er en stige av minst 6 verdier med blandet proveniens.
- C-a₀2: C=2.32 er numerisk konvergert fit, ikke analytisk avledet.
- C-bro1: grid→RAR er declared; kovariant EFT→μ_BE er contradicted (feil trend).
- C-bro2: Γ i □φ=Γ(ρ) ≠ dS/dρ (enhet + fortegn ulikt).
- C-bro3: √g-eksponenten overlever ikke inn i relativistisk handling som samme objekt.
- C-lim1: EFC→ΛCDM er formal limit, ikke equal-footing recovery.
- C-lim2: EFC→MOND er fenomenologisk overlapp, ikke matematisk limit; a₀-avvik uløst.
- C-disc: 5 kalibreringsfrie diskriminatorer (E_G, RAR, bullet, fσ8, sirene).

Disse skal IKKE inn i verdict/claim_gate_matrix — de går til en NY 9-rolle-runde med roterte mandater (dimensjonsanalyse, asymptotikk, regime, proveniens, måleteori, alternativt paradigme, kovariant bro, reproduksjon, meta).
