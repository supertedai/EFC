# RELEASE-protokoll — L-043/L-044 pre-registreringen

**Mortens orden (2026-09-17, bindende):** DOI lages FØR papiret går i
git. Git syncer tilbake til minnet i efc-banken. Mappen i git skal ha
AI-optimalisert innhold basert på PDF-en, og PDF-en skal ha samme
form hver gang: DOI, navn, e-post og ORCID.

## Steg 0 — Verifiser vertens Figshare-tilgang (MÅLES, ikke antas)

Maskin-topologi (Mortens korreksjon 2026-09-17):
- **Hermes på Hetzner** — datasenter-egress. Målt 403 fra
  api.figshare.com (nginx-blokkering); DataCite svarer 200.
- **.12** — LOKAL LLM-boks (2× RTX 6000, 48 GB VRAM), ikke
  Hetzner. Lokal egress: sannsynligvis IKKE blokkert, men uverifisert
  — boksen nekter fjerne kommandoer via den nåværende policyen.
- **.13 (Morpheus)** — den designede draft-kjøreren.

Regelen: draft/publish-kallene kjøres fra en vert som MÅLER 200.
Målingen er steg 0 hver gang — aldri en antakelse om .12/.13/Hetzner.
Hvis .12 måler 200 (når policyen tillater målingen), kan hele
draft-stien gå lokalt — og .12 kan dessuten kjøre P1-silico-testene
på egne GPU-er.

## Steg 1 — DOI FØR git

```
efc_release_helper.py draft-create \
  --title "..." --description "..." --defined-type preprint \
  --reserve-doi        # DOI-en reserveres NÅ — før PDF-bygg og commit
```

DOI-en returneres av draft-status og brukes i steg 2. Ingen
git-commit uten reservert DOI.

## Steg 2 — PDF med fast form

Bygg PDF-en med den kanoniske malen (mønster: `efc_val_2026_005.tex`):
- `\usepackage{orcidlink}` — forfatter med ORCID-lenke
- `pdfauthor={Morten Magnusson}` + `pdfsubject={... DOI <doi>}`
- DOI i header (`\href{https://doi.org/<doi>}{<doi>}`)
- Forfatterlinje: navn + `\orcidlink{0009-0002-4860-5095}`
- Footer: ORCID · e-post · github.com/supertedai/EFC
Samme form hver gang — bare DOI, tittel og dato skifter.

## Steg 3 — AI-optimalisert mappe-innhold BASERT PÅ PDF-en

Mappen `docs/papers/efc/EFC_L043_L044_PreRegistration/` skal bære
det maskinlesbare speilet av PDF-en (mønster: `Closing_the_EFC_
Consciousness_Bridge/`):
- `README.md` — menneske-lesbar inngang
- `ai_manifest.json` — maskin-manifest (felt, proveniens, DOI)
- `<slug>.jsonld` — semantisk graf av papirets påstander
- `index.json` + `schema.json` + `metadata.json`
- `CITATION.cff` + `citations.bib`
- `LICENSE`
PDF-en er kilden; artefaktene genereres FRA den, ikke ved siden av.

## Steg 4 — Commit til git (med DOI inne)

Først nå: commit + push + PR + uavhengig review + merge. DOI-en står
i PDF-en, i README-en, i CITATION.cff og i JSON-LD-en — git bærer
publikasjonens fulle identitet.

## Steg 5 — Sync til minnet (efc-banken)

Etter merge: retain til efc-banken med DOI, tittel, publiseringsdato
og sammendrag — git-papiret synces tilbake til minnet. Uten DOI i
git finnes det ingen synkekilde; derfor steg 1 først.

## Steg 6 — Publish (menneskeord) + uavhengig verifisering

```
efc_release_helper.py upload/publish --confirmed-by morten
efc_release_helper.py verify-*
```

`--confirmed-by morten` er obligatorisk — publiseringssignaturen er
Mortens. Etter hver ekstern skriving verifiseres Figshare OG GitHub
uavhengig: et lokalt commit er ikke bevis for et eksternt artefakt.
