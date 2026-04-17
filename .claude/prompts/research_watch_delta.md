# EFC External Research — Delta Scan Prompt

Paste this into a new Claude Code session to get ONLY new external
research since the last scan. Claude has no memory across sessions, so
the watchlist JSON is the source of truth for "what we have already seen".

---

## Prompt (copy everything below)

Kjør en delta-scan av ekstern forskning som treffer EFC.

**Steg 1 — les watchlist først.**
Les `docs/public/external_research_watch.json`. Bygg et sett `SEEN` av
alle `items[].key`-verdier. Ikke rapporter noe som allerede ligger der.

**Steg 2 — søk etter nytt materiale publisert etter `last_updated`
i watchlist-filen.** Søkedomener:
- DESI (DR2 full-shape / RSD, DR3 pre-release)
- Euclid (Q1, DR1, science-verification papers)
- DES Y6 / KiDS Legacy / HSC Y3 cosmic shear
- ACT DR7 / SPT-3G / Simons Observatory CMB + lensing
- SPARC / BIG-SPARC rotation-curve papers, modified gravity fits
- JWST Bullet Cluster og andre cluster-lensing studier
- Entropic / emergent / informational gravity preprints
- Arbeider som siterer EFC DOI 10.6084/m9.figshare.30656828

**Steg 3 — filtrer.** Drop alt som:
- har `key` i `SEEN`
- er publisert før `last_updated`
- ikke har konkret EFC-impact (ingen generelle review-artikler uten nye data)

**Steg 4 — rapport.** For hver nye treff:
- kanonisk key (arXiv-id eller DOI)
- kort tittel
- en setning om EFC-relevans
- konkret `ledger_action` (hvilken ledger/gap/WP endres)

**Steg 5 — oppdater watchlist.** Legg hvert nye treff inn som et item i
`docs/public/external_research_watch.json`, sett `date_seen` til i dag,
oppdater `last_updated`, og bump `version` med 0.1. Commit og push til
den aktive dev-branchen.

Hvis ingen nye treff: rapporter "ingen delta siden {last_updated}" og
ikke rør filen.

Svar på norsk.
