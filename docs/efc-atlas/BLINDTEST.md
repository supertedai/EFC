# Blindtest: blir en forskningsbeslutning bedre MED atlaset?

Status: **KJORT 2026-09-19** (resultatet ligger i `blindtest/RESULTAT.md`:
kravet er ikke innfridd — ett grep i repoet traff nøkkelens anker 10 av 12 ganger
mot ett atlas-kall 5 av 12). Protokollen under er den som ble fulgt, med de
avvikene som står i resultatet. Scenariene ble hentet fra de 21
registrerte aapne spoersmaalene i banken (`schema/regime_nodes.jsonld`,
feltet `open_questions`) og fra motor-/buss-spoersmaal. Skrevet 2026-09-18 etter at en uavhengig
vurdering (annen modell, direkte API, `model_verified: true`) pekte paa
«ingenting er demonstrert» som det avgjoerende av seks maalte gap.

## Kravet som testes

> Gitt en definert forskningsoppgave: gir atlaset en mer korrekt, bedre
> begrunnet, mer handlingsrettet eller raskere beslutning enn en rimelig
> alternativ arbeidsmaate?

Atlaset trenger ikke forutsi en kosmologisk overgang for aa vaere et
forskningsinstrument. Det kvalifiserer hvis det paalitelig forbedrer
beslutninger som: hvilken konnektor bygges naa, hvilken node/motor er
relevant, om en paastand er stottet eller planlagt, og om en slutning gaar
ut over evidensen.

## Design

- **12 scenarier**, hentet fra de 21 registrerte aapne spoersmaalene og fra
  motor/buss-spoersmaal i banken. Matchet i par etter vanskelighetsgrad.
- **To betingelser, crossover:**
  - **A (atlas):** banken, `atlas_lesing.py`, `atlas_navigasjon.py`, de
    genererte visningene og de deklarerte motor-/buss-koblingene.
  - **B (baseline):** repoet og vanlig filsoek/-lesing. Baseline skal IKKE
    vaere kunstig svekket — README, kildekatalog og soek er tilgjengelig.
- **Isolerte kontekster** mellom forsok: ett scenario per oekt, ingen
  gjenbruk av samtale.
- **Tilfeldig rekkefoelge**, og halvparten av scenariene bytter betingelse,
  saa forskjellen ikke kan tilskrives scenariovalget.

## Hva assistenten skal levere per scenario

1. relevant(e) node(r)
2. epistemisk status (observert / bygget / planlagt / antatt / ukjent)
3. beste neste forskningshandling
4. forventet observasjon eller resultat
5. falsifikator
6. hvilke kilder som baerer svaret (node-id, fil, emne)
7. hva som fortsatt er ukjent

## Skala (0-2 per dimensjon, satt FOER resultatene leses)

- **korrekthet** — traff svaret noeglen?
- **handlingsrettethet** — kan forskeren faktisk gjoere neste steg?
- **evidensdisiplin** — er paastandene baaret av siterte kilder, uten
  usannsynliggjort ekstrapolasjon?
- **hullbevissthet** — skilte svaret paa ukjent / planlagt / observert /
  etablert?
- **falsifiserbarhet** — navngir svaret en meningsfull motsigelse?

Sum 0-10. Tid og antall ubegrunnede paastander rapporteres SEPARAT, ikke
skjult i summen.

## Prosedyre

1. Forskjellige svar paa forhaand: noekkel med akseptable alternativer,
   skrevet foer noen ser genererte svar.
2. Svarene merkes bare A/B, og vurderes i tilfeldig rekkefoelge.
3. Hver siterte kilde etterproeves.
4. Betingelsen avsloeres ETTER vurderingen.
5. En menneskelig vurderer er ikke fullt uavhengig. Avboetning: en fast
   rubrikk med eksempler paa full, delvis og null uttelling, skrevet ned
   paa forhaand.

## Hva som stotter kravet

- minst 20 % hoeyere gjennomsnittssum enn baseline
- ingen oekning i ubegrunnede paastander
- noe kortere tid til beslutning
- bedre skille mellom planlagt og observert
- minst ett tydelig tilfelle der atlaset finner et riktig neste steg som
  baseline bommer paa

Terskelen settes foer resultatene ses.

## Hva som FALSIFISERER kravet

- atlas og baseline scorer og bruker like lang tid
- atlaset er langsommere uten aa bli riktigere
- atlaset gir flere skraasikre, ubegrunnede svar
- feilene klynger seg om kjerneord som «energy flow»
- assistenten henter flere nodenavn, men velger ikke bedre handlinger
- planlagte noder blir tatt for aa vaere evidens

Ett lite forsok kan ikke bevise at atlaset aldri hjelper. Det kan vise at
den hevdede nytten ikke er observerbar paa representative oppgaver — og det
er nok til aa flytte kravet fra «antatt» til «ikke demonstrert».

## Hva som IKKE er testet her

- om atlaset forbedrer noe over TID (krever gjentatt bruk)
- om nodene er faglig riktig valgt (krever fagfellevurdering)
- om buss-snapshotet er representativt for den levende bussen


## Hvordan kjore den

1. Hent 12 scenarier: `python scripts/atlas_arbeidskoe.py --sakse` og
   `--ghost` navngir hvor det mangler noe; `open_questions` navngir hva som
   venter. Velg 12, match dem i par etter vanskelighetsgrad.
2. Skriv noekkelen (akseptable svar) for ALLE 12 for noen ser et generert svar.
3. Kjor hvert scenario i isolert oekt: 6 med `scripts/atlas_inngang.py` +
   `scripts/atlas_lesing.py` tilgjengelig, 6 med bare repo og filsoek.
4. Bytt betingelse for halvparten, saa forskjellen ikke kan tilskrives
   scenariovalget.
5. Vurder A/B blindt etter skalaen over, etterprov hver siterte kilde, og
   avslor betingelsen til slutt.

## Hva som allerede er maalt, og ikke skal maales om igjen

- Atlaset naar 118/118 emner, 39/39 domener og 32/32 motorfiler.
- 27 av 31 EFC-paastander kan felles; 85 noder maaler eller er etablert.
- 21 aapne spoersmaal er registrert og ordrett hentet fra banken.
- De fem kjernebegrepene er navneromsverdier uten node — det er maalt, ikke
  antatt, og er en del av det testen skal avdekke konsekvensene av.
