# EFC External Research Delta-Scan

Kjør en delta-scan av ekstern forskning som treffer EFC.

1. Les `docs/public/external_research_watch.json`. Bygg et sett SEEN av
   alle `items[].key`. Ikke rapporter noe som allerede ligger der.
2. Søk etter nytt materiale publisert etter `last_updated`: DESI DR2/DR3,
   Euclid Q1/DR1, DES Y6, KiDS Legacy, ACT DR7, SPT-3G, Simons Obs,
   SPARC/BIG-SPARC modifisert-gravitasjon-fits, JWST cluster-lensing,
   entropic/emergent/informational gravity-preprints, og papers som
   siterer EFC DOI `10.6084/m9.figshare.30656828`.
3. Drop alt med `key` i SEEN, publisert før `last_updated`, eller uten
   konkret EFC-impact.
4. For hvert nytt treff: `key`, kort tittel, EFC-relevans (én setning),
   `ledger_action`.
5. Legg treffene inn i watchlist-filen, oppdater `last_updated` og bump
   `version` med 0.1, commit og push til aktiv branch.

Ingen treff → svar "ingen delta siden {last_updated}" og ikke rør filen.

Svar på norsk.
