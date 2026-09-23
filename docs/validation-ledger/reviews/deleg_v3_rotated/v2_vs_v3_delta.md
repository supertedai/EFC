# v2 → v3.1 delta

artifact_type: orchestrator_navigation_metadata (NOT reviewer output)
run_id: deleg_v3_rotated
parent: deleg_d21ed669 (v2, frozen, hash-bound, UNTOUCHED)

## Hva endret seg mellom rundene

| Akse | v2 | v3.1 |
|---|---|---|
| Claims | 12 (C1–C12), alle sammensatte | 15 atomiserte, én predikat hver |
| Gate-celler | 120 (12×10) | 150 (15×10) |
| Fordeling | 31 satisfied / 35 open / 54 n/a | 45 satisfied / 63 open / 42 n/a |
| Gate 1 (claim-identitet) | Feilet blanket (compound) | 7 satisfied, 8 open (atomisert) |
| Modell | gpt-5.6-luna (9 roller) | gpt-5.6-luna (8 roterte + rolle 9 meta) |
| Funn | 55 | 15 claims × status + 6 pakker + 5 artefaktruter |
| Status | Verdict bygget av orkestrator (autoritetsbrudd, senere renset) | Rolle 9 = reviewer-disposisjon, mekanisk matrise |

**Merk:** som *andel* er v3 mer åpen enn v2 (42 % vs 29 % open) — ikke mindre. Det er ærlig, ikke over-grønt; det er poenget.

## Hva som ble atomisert / omskapt

v3.1 er en *re-skopering*, ikke en re-nummerering av v2s C1–C12. Mappingen:

- v2 C1/C2/C3 (Γ-former + «ikke lineær modning» + √[ρ]-residual) → v3 G1a/G1b (eksakt algebra) + G2a/G2b (dimensjonsnormalisering, *refinert*: √[ρ]-residualen viste seg å være β/r_*-hullet) + G1c (domene).
- v2 C9 (a₀-diskriminator foreslått) → v3 A1a/A1b/A2/A3 (a₀-stigen *ekspandert* til 6+ verdier med proveniens + C=2.32-prefaktor + ancestry-vurdering).
- **Nytt i v3** (fra generativ runde, ikke i v2): B1–B4 (transportbroen grid→kovariant) + L1/L2 (paradigme-limits som deklarasjoner).

## Nøkkelstatusendringer (ikke bare bedre oppløsning)

1. **C=2.32 er numerisk konvergert lattice-måling, ikke analytisk Watson/Green.** (v2 omtalte det som «fit»; v3 presiserer: verken statistisk fit eller avledet konstant.)
2. **Den kovariante EFT → μ_BE-kanten er `contradicted`.** (v2 flagget den bare som «declared»; v3 etablerer trendbruddet: klassisk korreksjon *øker* med g, μ_BE *avtar*, og μ_BE er postulert.)
3. **β/r_*-hullet er et dimensjonsdefekt, ikke bare en «residualdimensjon».** (x²/u = 4π/(3·l_g) = 2.59e35 m⁻¹; √u=x krever l_g = 4π/3 ≈ 4.19 m.)
4. **To latente enhetsfeil verifisert** (cosmology.yaml:18 a0_kpc avvik ~974k; efc_integration_test.py:48 Lambda_cosmo faktor 1e6) — begge uten downstream-konsument, severity medium.

## Compound claims som krever v3.2 (rolle 9s anbefaling)

G2a, G2b, A1a, B1, B2, B3, L1, L2 — totalt **8 compound**. De er `is_compound=true` og kan ikke lukkes som helhet. Rolle 9 anbefalte eksplisitte sub-claims (G2a.1–3, G2b.1–3, A1a-per-verdi, B1.1–3, B2.1–4, B3.1–4, L1.1–4, L2.1–4).

## Dekningshull (rolle 9s vurdering)

1. **F-prov-7 (`related_packages` heterogen)** — ikke blant de 15 v3.1-claimene. Rolle 9: *må* legges til som atomisk v3.2-claim, ikke absorberes i pakke-prosa.
2. **Γ-aliasene er ikke bokstavelige fellesidentifikatorer** — v3.2-proveniens-claim må fryse kilde→alias-kart, normalisering, measurand, regime-navnerom.
3. De to latente enhetsfeilene må repareres før noen numerisk a₀-bro brukes.
4. De fem diskriminator-designene er ikke evidens-noder før målekjeder/likelihoods/holdouts er utført.

## De fem rutede artefakt-oppgavene (ikke lukkbare ved lesing)

| Artefakt | Type |
|---|---|
| β/r_* dimensjonsutledning | Forfatter/matematikk-arbeid |
| C=2.32 Watson/Green-derivasjon | Forfatter/matematikk-arbeid |
| Kanonisk a₀ author-freeze | Forfatter/human gate |
| Kovariant reduksjon S_grid → relativistisk handling | Forfatter/matematikk-arbeid |
| Equal-footing holdout likelihood | Eksekverings-artefakt |

## Proveniens-advarsel (båret videre fra runde 2)

- Rolle 9 var *delvis seedet*: prompten bar 12 «etablerte fysiske vurderinger» som skulle bevares. Dens bekreftelse av *disse spesifikke punktene* er seedet korroborasjon, ikke frisk test. Dette er dokumentert i `role9_provenance_note.json` og må ikke senere presenteres som uavhengig validering.
- Runde-2-attacker var seedet (5 mål med bevis). Adversarielt materiale, ikke uavhengig evidens.
- Alle roller er gpt-5.6-luna. Enighet = lesningskonsistens, aldri uavhengig validering.
