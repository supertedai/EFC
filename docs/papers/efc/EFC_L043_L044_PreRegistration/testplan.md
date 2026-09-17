# Testplan — Lag B (forsegles FØR motorbygging)

**Status: IKKE LÅST.** Denne filen er plassholderen for Lag B.
Ingen måling kan skje før status her skiftes til FORSEGLET og
SHA-en registreres i evidence-registeret. Testen
`test_lag_b_maaler_ingen_trengsel` i tests/test_prereg_l043_l044.py
håndhever dette maskinelt.

## P1 — feltene som låses her

- **Prompt-bank** (3 oppgavetyper × 20 prompt, mal-generert): IKKE
  SKREVET ENNÅ — filene publiseres og SHA-forsegles her.
- **De to første uavhengige arkitekturene** (ulike utviklere, ≥ 4
  kontekst-trinn hver): IKKE VALGT ENNÅ — valget registreres her
  med navn og kilde.
- **Kontekst-trinnene**: 2k, 4k, 8k, 16k, 32k, 64k, 128k (fiksert i
  Lag A).

## P2 — feltene som låses her

- **Nettverkslisten** (≥ 8 IIT-nettverk med kilde-DOI-er): IKKE
  SKREVET ENNÅ.
- **PyPhi-versjons-pinnen** (1.x, eksakt commit/tag): IKKE PINNET
  ENNÅ.

## P3 — feltene som låses her

- **Prompt-bankene** (100 prompt × 3 domener, som filer): IKKE
  SKREVET ENNÅ.
- **Modellfamilien** (≥ 3 sjekkpunkter langs RLHF-stigen, med
  publiserte navn): IKKE VALGT ENNÅ.
- **Seed-konvensjonen**: 0–4 (fiksert i Lag A).

## Forseglingsprosedyre

1. Skriv feltene over (fjern «IKKE»-linjene).
2. `sha256sum testplan.md` → registrer i evidence-registeret under
   `forseglinger` med `dok: "docs/papers/efc/EFC_L043_L044_
   PreRegistration/testplan.md"` og `status: "forseglet"`.
3. Testen slipper da målingen gjennom; før det feiler den.
