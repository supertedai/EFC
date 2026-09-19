# Blindtest — NØKKEL (skrevet før noen har sett et generert svar)

Protokoll: `docs/efc-atlas/BLINDTEST.md`. Denne filen er låst før kjøringen.
Ett scenario per oppføring, med hva som er akseptabelt svar og hvilken kilde
som bærer det. Ankrene er hentet fra **generatorens egne utledede tall** og fra
banken — ikke fra mine egne gjenberegninger (to av dem ble felt av måling da
denne nøkkelen ble skrevet: «uten gruppe» er en PLASSERINGSfakta om kapittel,
ikke om buss-domene, og «21 av 116 navngir en rute» er ikke det samme som at
95 noder har et domene-felt).

Skala, per dimensjon 0–2 (sum 0–10): korrekthet · handlingsrettethet ·
evidensdisiplin · hullbevissthet · falsifiserbarhet. Tid og antall ubegrunnede
påstander rapporteres separat.

## Rubrikk med eksempler (låst før kjøring)

| Poeng | Korrekthet | Evidensdisiplin | Hullbevissthet |
|---|---|---|---|
| **2** | Treffer nøkkelen med det målbare ankret | Hver påstand har node-id/fil/emne som etterprøves | Skiller eksplisitt planlagt / observert / bygget / ukjent |
| **1** | Riktig retning, mangler ankret eller ett av flere tall | Siterer noe, men minst én påstand står uten kilde | Nevner ett skille, blander to |
| **0** | Feil navn, feil retning, eller «vet ikke» uten grunn | Påstand uten kilde, eller kilde som ikke finnes | Behandler planlagt som observert |

## Scenarioer

### S01 (vanskelig) — Hvilken av de to strømmene som venter på konnektor bør bygges først?
**Akseptabelt:** `kosmos.kosmologi_desi_bao` eller `verden.klima_isbre`, **forutsatt**
at grunnen er målt (strommen er navngitt i `open_questions` som «venter paa
konnektor»), ikke «viktigst». Full uttelling krever ett av de to id-ene **og**
at begrunnelsen peker på det registrerte spørsmålet.
**Bæres av:** `open_questions` på de to nodene i `schema/regime_nodes.jsonld`.

### S02 (lett) — Navngir `verden.vaer` en motor i dag?
**Akseptabelt:** Nei. Feltet `stipulasjoner.motor` er **utelatt** (ikke tomt), og
noden har `phase=instrument` og eget buss-domene `verden.vaer`.
**Bæres av:** `schema/regime_nodes.jsonld`.

### S03 (vanskelig) — Hvilken vei går relasjonen mellom `efc.hubble_engine` og `obs.bao`, og med hvilket predikat?
**Akseptabelt:** `obs.bao --OBSERVED_THROUGH--> efc.hubble_engine`. Retningen
**til** motoren, predikatet `OBSERVED_THROUGH`. Den omvendte (`OBSERVED_IN` med
motoren som subjekt) er defekten som ble rettet (K6, `10087393`).
**Bæres av:** `relations` i banken + `tests/test_atlas_relasjonsretning.py`.

### S04 (lett) — Hva er den deklarerte formen til `stipulasjoner.motor`?
**Akseptabelt:** motorens **modulnavn** — verdien er filnavnet uten ending under
`efc_inference/engine/<verdi>.py`. Ikke node-id, ikke fri tekst.
**Bæres av:** `scripts/maintenance/efc_bro_konvensjon.py`,
`tests/test_motor_traaden.py`.

### S05 (vanskelig) — Hvor mange noder har tatt stilling til falsifiserbarhet, og hva bærer svaret?
**Akseptabelt:** alle 126: **31** kan felles (`ville_falsifisere`), **4** bærer en
`falsifiserbarhet`-status, **91** bærer en grunn — og grunnen er en **deklarert
klasse** i tre tekster (63 instrument, 27 etablert fysikk, 1 selvbeskrivelse),
ikke en unik setning per node.
**Bæres av:** `tests/test_atlas_avgjorelse.py` + banken.

### S06 (lett) — Hvor stor del av atlaset navngir en buss-rute, og kjører noe målingen?
**Akseptabelt:** **21 av 116** navngir en rute, **95** er tause; snapshotet er
målt **2026-09-17T18:41:27Z av faber** (`scripts/atlas_volum.py`), og **0 av 16**
workflows kjører målingen.
**Bæres av:** generatorens statuslinje / `docs/efc-atlas/SYSTEM.md`.

### S07 (vanskelig) — Hvorfor står 53 noder «uten gruppe ennå», og hva er de?
**Akseptabelt:** det er en **plasseringsfakta** (ingen kapittelgruppe), ikke en
byggestatus: **20 observasjoner, 18 regimenoder, 10 med en motor, 5 øvrige**.
Poenget: en observasjon og en fase med fungerende motor er ikke «ubygd».
**Bæres av:** `docs/efc-atlas/SYSTEM.md` (utledet av generatoren).

### S08 (lett) — Hvor mange av kravene til en ny node leses av ingen?
**Akseptabelt:** **0 av 22** — målt ved **mutasjon** (nøkkelen fjernes på hver node
som bærer den, og alle fem leserne svares på nytt), ikke ved telling.
**Bæres av:** `scripts/atlas_feltvekt.py`, `tests/test_atlas_feltvekt.py`.

### S09 (vanskelig) — Bærer `β = 0.16` en feilgrense i atlaset?
**Akseptabelt:** Nei — `feilgrense: null`, med kilde til den ordrette linja
«β = 0.16 (free amplitude)». Kontrasten: `obs.rar` bærer `k = 0.415 ± 0.029`.
**Bæres av:** banken (`obs.bao`, `obs.rar`) + `tests/test_usikkerhetslag.py`.

### S10 (lett) — Hvilke relasjonspredikater finnes, og bærer noen støtte eller motsigelse?
**Akseptabelt:** åtte predikater (`OBSERVED_IN` 23, `COUPLED_TO` 20, `ANALOGOUS_TO`
15, `CARRIES` 9, `TRANSITIONS_TO` 7, `OBSERVED_THROUGH` 7, `EMERGES_FROM` 3,
`INSTANCE_OF` 1) — og **ingen** bærer støtte eller motsigelse.
**Bæres av:** `relations` i banken.

### S11 (vanskelig) — Hvor kommer buss-snapshotet fra, og hvor gammelt kan det bli før noe varsler?
**Akseptabelt:** målt **2026-09-17T18:41:27Z av faber** via `scripts/atlas_volum.py`;
**0 av 16** workflows kjører målingen, så det aldres av seg selv; eneste alarm er
`tests/test_atlas_dekning.py::test_snapshottet_har_ikke_gaatt_ut_paa_dato` ved **90 dager**.
**Bæres av:** `docs/efc-atlas/SYSTEM.md` + nevnte test.

### S12 (lett) — Hvilken node bærer motbeviset mot EFCs eget regime?
**Akseptabelt:** `obs.bao`.
**Bæres av:** banken (`obs.bao` er den eneste noden som bærer `β = 0.16` uten
feilgrense og er knyttet til motoren gjennom `OBSERVED_THROUGH`).

## Terskel (satt før resultatene ses)

Støtter kravet: minst **20 % høyere** gjennomsnittssum for A enn B, **ingen**
økning i ubegrunnede påstander, og minst ett tilfelle der A finner et riktig
neste steg som B bommer på. Falsifiserer: lik sum, eller A langsommere uten å
bli riktigere, eller planlagte noder tatt for evidens.

## Kjente svakheter ved denne kjøringen (skal stå i resultatet)

- **Én agent, ikke 12 isolerte økter.** Protokollen krever ett scenario per økt
  uten gjenbruk av samtale. Det kan ikke oppfylles i denne kjøringen, og det skal
  stå i resultatet som en svakhet ved målingen — ikke skjules.
- **Samme modell i begge betingelser**, og **selvvurdering** (protokollen
  avbøter med rubrikken over, låst på forhånd).
