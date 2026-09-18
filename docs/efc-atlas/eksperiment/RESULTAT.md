# Resultat: eksperimentet felte instrumentet, ikke hypotesen

Kjørt 2026-09-18 mot `origin/main`. Nøkkel (rettet, `67938617`) og protokoll
(`f8bbd7c6`) ble skrevet og committet **før** kjøring.

## Tallene

| | A: dagens leser | B: prototype med evidenslag |
|---|---|---|
| Korrekt | **5** | **7** |
| Feil | 1 | 1 |
| Avståelser | **2** | 0 |
| Falske støttepåstander | **0** | **0** |
| Proveniens (fil:felt) | 6 av 8 | **8 av 8** |
| Tid | 0,08 s | 0,07 s |

```text
A: {"korrekt": 5, "feil": 1, "avstaaelse": 2, "falske_stoettepastander": 0, "proveniens": 6}
B: {"korrekt": 7, "feil": 1, "avstaaelse": 0, "falske_stoettepastander": 0, "proveniens": 8}
```

Begge systemer svarer likt og korrekt på Q1, Q2, Q5, Q6 og Q8. Begge feiler Q4.

## Dette avgjør ikke spørsmålet — og grunnen er min

Protokollen satte opp tre kriterier for å ta støtte-kantene inn. To av dem falt:

**Kriteriet som skulle avgjøre, skilte ikke.** «B skal ha færre falske
støttepåstander enn A» — begge har **0**. System A **løy ikke**; den avstod på
Q3 og Q7 i stedet for å svare på koblinger. Det var jeg som ga A lov til å avstå,
og dermed fjernet jeg nøyaktig den feilmodusen eksperimentet var bygget for å
finne. Instrumentet kan ikke avgjøre det det ble laget for.

**Q4 er ugyldig for begge.** Nøkkelen ble rettet fra «1 kant» til «3 kanter»
*etter* at systemene var bygget mot den gamle versjonen. Begge svarer én kant.
Det er min rekkefølgefeil, ikke en systemfeil — men observasjonen står: **ingen
av dem finner alle tre inverterte kantene.**

**Det som står igjen, er en dekningsgevinst — og den er smal.** B svarer på to
spørsmål A avstår fra (Q3 og Q7), begge korrekt. Det er ikke «bedre
oppslagsnøyaktighet»; det er at to spørsmål i dag ikke har noe svar å gi.

## Dette felte jeg selv på veien, og det skal stå

1. **Scoreren målte seg selv.** Første kjøring ga 3 korrekt for begge. Feilene
   var ordet `merknad` — forklarende prosa jeg selv hadde lagt inn i nøkkelen,
   som scoreren sammenlignet som om det var svaret. Det måler instrumentet, ikke
   systemene. Begge scoringer står her; rettingen er å **deklarere** i
   `key.json` hvilke nøkler som er forklaring.
2. **Nøkkelen hadde fire tellefeil.** Q3: 16 → 18 relasjonsrader. Q4: 1 → 3
   kanter. Q5: 4 rader og «duplisert» → 2 rader, ingen duplisering. Q7:
   `kan_besvares_i_dag` false → true. Funnet av to spor uavhengig av hverandre,
   rettet før kjøring i egen commit. Årsaken er min: jeg leste en utskrift som
   kuttet en liste med `[:4]` og behandlet kuttet som tallet.
3. **A ble sterkere enn spesifisert.** Jeg skrev «finnes feltet ikke, er svaret
   nei». Implementasjonen sjekket alle tre falsifikatorformene og svarte Q6
   korrekt — inkludert fellen med `efc.rotation_engine`. Det er ikke galt, men
   det betyr at A som ble målt ikke er den naive leseren jeg så for meg.

## Hva det betyr for ADR-086

- **Usikkerhetslaget:** svakt støttet. Det gir et svar A ikke kan gi (Q7 med
  begrunnelse), uten å fylle noe med gjetting. Ikke mer enn det.
- **Støtte-kantene:** **uavklart, ikke avvist.** Det avgjørende kriteriet kunne
  ikke fyre fordi A fikk avstå. Vedtaket i ADR §3 står uendret: nei nå.
- **Pipeline-omleggingen:** ikke berørt. Ingenting her taler for den.

## Neste iterasjon — det instrumentet må endres på

1. **Fjern A sin avståelsesrett på Q3 og Q7.** Tving A til å svare med en
   regel den faktisk har (koblinger = støtte), og mål hvor mange falske
   støttepåstander den da produserer. Først da kan kriteriet skille.
2. **Rett nøkkelen før systemene bygges** — eller bygg systemene etter at
   nøkkelen er frosset og verifisert. Kjeden var: nøkkel → bygg A/B → verifiser
   → rett nøkkel. Den skal være: nøkkel → verifiser → frys → bygg.
3. **Q4 skal kreve listen, ikke ett eksempel.** Tre kanter, ikke én.
4. **Legg til et spørsmål der A med sikkerhet svarer feil.** Kandidat målt i
   dag: `efc.rotation_engine` — et oppslag som bare ser etter
   `ville_falsifisere` melder den som udekket. Q6 fanger det bare hvis A er
   spesifisert til å være så naiv som den faktisk ville vært uten barnets
   velvillige implementasjon.

**Kort sagt: eksperimentet ga ikke støtte-kantene rett — og det ga ikke atlaset
urett. Det viste at jeg hadde bygget et instrument som lot begge slippe unna.**
