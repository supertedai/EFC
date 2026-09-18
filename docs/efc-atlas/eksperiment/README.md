# Eksperimentet: gir evidenslaget noe — eller ser det bare komplett ut?

Dette er ADR-086 §4 satt i drift. Spørsmålet det skal svare på er ikke om et
usikkerhetslag og støtte-kanter *kan* bygges. Det er om de **endrer en
avgjørelse til det bedre**.

Fila er skrevet før noen kjøring, sammen med `key.json`. Nøkkelens sha256 står
i commit-meldingen til `eefed0b3`.

## Hva som måles

Samme åtte spørsmål stilles til to systemer, og scoreren sammenligner mekanisk
mot nøkkelen — ikke ved min vurdering.

| | System A: dagens leser | System B: minimalt evidenslag |
|---|---|---|
| Bygget på | felter og relasjoner som de står | et sidefil-lag, ikke en skjemaendring |
| `ANALOGOUS_TO` | en kobling | **aldri** støtte |
| «Støttet» | relasjon til noe som måler eller observerer | krever en eksplisitt `STOETTER`-kant |
| Usikkerhet | ordet i prosa teller ikke som felt | lest fra evidenslaget; mangler den, er svaret `null` |
| Kan ikke svare | avstår | avstår |

Måltall: korrekt svarandel, avståelser, **falske støttepåstander**, proveniens,
tid, og kalibrering (når systemet sier «støttet», hvor ofte stemmer det).

## Beslutningsregelen, skrevet før resultatet

- **Støtte-kanter inn** hvis B har 0 falske støttepåstander, A ikke taper noe
  der begge svarer, og B svarer korrekt der A avstår.
- **Støtte-kanter ut** hvis B har like mange eller flere falske
  støttepåstander enn A, eller taper nøyaktighet der A svarer korrekt.
- **Usikkerhetslaget vurderes separat:** det er verdt noe hvis det gir minst ett
  svar A ikke kan gi, uten å fylles med gjetting.

## Spørsmålene og fellene

Åtte spørsmål over fem typer — kjede, oppgjør, analogi-mot-støtte, feilrettet
kant, syklus, falsifikator, usikkerhet. Alle nøklene er lest fra
`schema/regime_nodes.jsonld`, ikke fra hukommelsen.

To spørsmål **kan ikke besvares i dag**, og det står i nøkkelen:

- **Q3:** hvor mange av de åtte nodene er empirisk støttet? Sannheten er **0** —
  0 av 86 relasjoner i banken bærer støtte eller motsigelse.
- **Q7:** bærer noen av dem et strukturert usikkerhetsfelt? Sannheten er **0**.

Poenget med dem er ikke tallet. Det er om systemet **sier** 0, eller finner på
noe. Et system som svarer «3 støttet» på Q3 har ikke løyet med vilje — det har
svart på koblinger fordi det ikke har noen term for støtte.

Tre feller, alle målt og ikke konstruert:

1. `efc.rotation_engine` har verken `ville_falsifisere` eller
   `ikke_falsifiserbar_grunn`. Den har **den tredje formen**:
   `falsifiserbarhet.status = terskel_ikke_fastsatt`. Et oppslag som bare ser
   etter det første feltet melder noden som udekket — og tar feil.
2. `efc.hubble_engine --OBSERVED_IN--> obs.bao` har **invertert retning**. I
   alle andre 29 tilfeller går `OBSERVED_IN` observasjon → regime.
3. `homo.aksjonspotensial` ↔ `homo.hjerte_syklus` er `ANALOGOUS_TO` **begge
   veier**, og begge retninger er duplisert: 4 rader for 2 relasjoner.

## Blindheten, og hva den ikke dekker

**Dekket:** nøkkelen er skrevet og committet før prototypen finnes.
Scoreringen er mekanisk. Et eget spor prøver å felle nøkkelen mot banken og
leter etter spørsmål som bare kan besvares av det nye laget — altså spørsmål
som måler sin egen konklusjon.

**Ikke dekket, og det skal stå i rapporten:** jeg har valgt spørsmålene *og*
bygget B. Det er den svake leddet. System A er dessuten en **regel jeg har
skrevet**, ikke atlaset selv — eksperimentet måler A-som-spesifisert. Står A
svakt, er funnet «regelen er for naiv», ikke «atlaset er ubrukelig». Begge
utfall er nyttige, men de skal ikke blandes.

Retter en verifisering en nøkkel, gjøres det i en egen commit med grunn, og
antallet rettede nøkler rapporteres. Aldri stille.

## Filer

| Fil | Hva |
|---|---|
| `key.json` | spørsmålene og den objektive nøkkelen — skrevet først |
| `leser_a.py` | system A |
| `leser_b.py` | system B |
| `evidenslag.json` | Bs sidefil: usikkerhet per tallpåstand og eksplisitte støtte-/motsigelseskanter |
| `scorer.py` | mekanisk sammenligning mot nøkkelen |
| `test_eksperiment.py`, `test_leser_b.py` | selftester |

```sh
/opt/venvs/t_123ed6d9/bin/python -m pytest tests/ -q -k eksperiment -p no:randomly
```
