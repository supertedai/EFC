# v3 rottert-mandat gap-fylling review — plan

artifact_type: orchestrator_navigation_metadata (NOT reviewer output)
run_id: deleg_v3_rotated
claim_map_version: 3.1-neutral (claimene er noeytrale; retningen avgjoeres av reviewer)
parent: deleg_d21ed669 (frosset, hash-bundet, IKKE rørt)
model: gpt-5.6-luna (same-model-family caveat gjelder)

## Hvorfor denne runden
v2 feilet gate 1 fordi claimene var sammensatte. v3.0 atomiserte til 16 claims, men ba inn orkestratorens EGNE konklusjoner i claimene («overlappende, ikke disjunkte», «ikke uavhengig fordi», «contradicting», «ikke en recovery»). En blind reviewer som faar en konklusjon i claimet bekrefter resonnementet, ikke sannheten — ekkokammer. v3.1 noeytraliserer: 15 claims, ett predikat hver, retningen ukjent for reviewer.

## Noeytralitetsregel
Reviewer skal AVGJOERE retningen (supported/contradicted/open), ikke bekrefte en innebygd konklusjon. Hvis et claim fortsatt ser ut til aa baere en konklusjon, flagg is_compound/leading i stedet for aa bekrefte.

## Den aerlige innsnevringen (fem ikke-lesbare items — RUTES, ikke LØSES)
1. Er sqrt(u)=x? -> dimensjonsutledning av beta/r_* (G2a, G2b)
2. Er C=2.32 avledet? -> Watson-integral / Green-funksjonsderivasjon (A2)
3. Hvilken a0 er kanonisk? -> input/output-frys (A1a, A1b)
4. Er den kovariante broen lukkbar? -> faktisk reduksjon S_grid->relativistisk (B2, B3, B4)
5. Er recovery-kantene ekte? -> utført likelihood/holdout (L1, L2)

Disse er ARBEID, ikke beslutninger. v3 dokumenterer og ruter dem — den løser ingenting.

## D1 er IKKE en claim
Fem kalibreringsfrie diskriminatorer (E_G, RAR med frosset a0, bullet delta_kappa, f_sigma8/BAO, lensing-slip/sirene) er et TESTDESIGN, ikke en proposisjon som skal «satisfies/open». Den er fjernet fra claim_map og lever her som design-artefakt.

## Runde 1: 8 blinde, roterte reviewers (parallell)
1. Dimensjonsanalytiker -> G2a, G2b
2. Asymptotiker -> G1a, G1b
3. Regime/fase-mapper -> G1c
4. Proveniens-regnskap -> A1a, A1b, A2
5. Målekjede-teoretiker -> A3
6. Alternativt-paradigme-komparator -> L1, L2
7. Kovariant bro-analytiker -> B1, B2, B3, B4
8. Reprodusent/falsifikator -> G1a, G1b, A1a, A2 (kjører kode)

## Runde 2: advocate + attacker (etter runde 1)
Attacker rettes EKSPLISITT mot orkestrator-syntesen (ledende claims, a0-bro-uavhengighet, «kode-struktur forkledd som fysisk forening»), ikke bare manuskriptet.

## Runde 3: rolle 9 meta-synthesizer (syntetiserer 1+2, gate-applicability, overlap/motsigelse)

## Definition of done (v3)
v3 er ferdig naar:
(a) de 15 claimene har reviewer-tildelt status + gate_applicability,
(b) v2-vs-v3-deltaet er skrevet,
(c) de fem ikke-lesbare items er rutet til navngitte artefakt-oppgaver,
(d) release-gaten fortsatt er REFUSED (fail-closed).

## Konfidens-tall aggregeres IKKE
confidence er per-lesning-sikkerhet, ikke uavhengige sannsynligheter. Ingen multiplikasjon/gjennomsnitt som om de var uavhengige bevis (AI_REVIEW_NOTICE).

## Sperrer (fail-closed)
- Ikke rør deleg_d21ed669, verdict.json, claim_gate_matrix.json (tracked), findings_index.json (tracked).
- Ikke kjør findings_index.py --apply.
- Ikke promotér RECOVERED_BY_LIMIT_OF til empirisk recovery.
- Ikke kall C=2.32 «avledet» uten selvstendig analytisk kjede.
- Ikke kall Gamma_B en fase uten u->S-mapping.
- Ikke kall box(phi)=Gamma(rho) samme Gamma som dS/drho uten typet identitetsmap.
- Ikke bruk sqrt-formen som positiv KC1-seier.
- Ingen SPARC/a0-data brukt både til kalibrering OG diskriminering.
- Human gate forblir urørt og fail-closed.
- Orkestrator forfatter IKKE funn/disposisjon/verdict/claim-status — det er reviewer-output.
