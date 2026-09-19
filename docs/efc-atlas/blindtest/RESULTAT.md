# Blindtest — RESULTAT

Kjørt 2026-09-19 mot `origin/main` = `58f0e127`. Protokoll og nøkkel ligger i
`NOKKEL.md` (committet **før** noen svar fantes: `49988eae`).

## Kort fortalt

**Kravet er ikke innfridd. Den hevdede nytten er ikke observerbar på disse 12
oppgavene.**

| | første atlas-kall | ett grep i repoet |
|---|---|---|
| traff nøkkelens anker | **5 av 12** | **10 av 12** |

Og det ene treffet bare atlaset ga (`S08`, 0 av 22 krav uten leser — målt ved
**mutasjon**) tok **30,4 s** mot greps 0,12 s.

## Målt, scenario for scenario

`A` = ett atlas-kall (`atlas_lesing.py` / `atlas_arbeidskoe.py` / `atlas_volum.py`
/ `atlas_feltvekt.py`), `B` = ett `grep -rn` i repoet. Begge med den mest
nærliggende kommandoen, og begge talt som **ett steg**.

| | anker | A | B |
|---|---|---|---|
| S01 | `kosmos.kosmologi_desi_bao` (hvilken strøm venter på konnektor) | bom | TREFF |
| S02 | `verden.vaer` navngir ingen motor | TREFF | TREFF |
| S03 | `OBSERVED_THROUGH` (relasjonsretningen) | bom | TREFF |
| S04 | `efc_inference/engine` (formen til `stipulasjoner.motor`) | TREFF | TREFF |
| S05 | falsifiserbarhets-tallene (31/4/91) | bom | bom |
| S06 | `0 of 16` workflows kjører bussmålingen | bom | TREFF |
| S07 | `20 observasjoner` (de gruppeløse) | bom | TREFF |
| S08 | `0 of 22` krav uten leser | TREFF (30,4 s) | bom\* |
| S09 | `feilgrense` på `β = 0.16` | TREFF | TREFF |
| S10 | `OBSERVED_IN` / predikatene | bom | TREFF |
| S11 | `2026-09-17` (snapshotets proveniens) | bom | TREFF |
| S12 | `obs.bao` (motbeviset mot eget regime) | TREFF | TREFF |

\* B bommet bare fordi strengen «0 of 22» ikke står ordrett i repoet; **ett kall
til** (lese `tests/test_atlas_feltvekt.py`) gir svaret. Det er kostnaden, ikke
tilgjengeligheten, som skiller.

## Hvorfor — og det er dette som er funnet

Atlasets informasjon **ligger i repoet**. De genererte visningene er filer
(`docs/efc-atlas/SYSTEM.md`, `INDEKS.md`), banken er en fil
(`schema/regime_nodes.jsonld`), og invariantene er tester. Derfor når `grep` dem
alle sammen. Atlas-CLI-ene legger **ikke til rekkevidde** — de legger til
*struktur*: `--node`, `--hop` og `--akser` svarer kompakt med node-id-en hengende
på, der et grep-treff må leses i sin sammenheng for å bety noe.

Det er en reell, men **liten** fordel. Den er ikke 20 %. Og den slår ikke ut på
spørsmålene som betyr noe: relasjonspredikater (`S03`, `S10`), hull og
konnektor-prioritering (`S01`, `S06`, `S07`, `S11`) og falsifiserbarhets-tallene
(`S05`) er **ikke** eksponert av noen CLI. De finnes bare som prosa eller som rå
JSON.

## Dommen mot terskelen som ble satt på forhånd

- minst 20 % høyere gjennomsnittssum for A: **nei** (A når færre ankere i ett steg)
- ingen økning i ubegrunnede påstander: **ja** — A siterer node-id i selve
  utdataene, B må lese filen for å vite hva treffet er
- ett tilfelle der A finner et riktig neste steg som B bommer på: **ett**
  (`S08`, mutasjonsinstrumentet — og det koster 30 s)

Protokollen sier det selv: ett lite forsøk kan ikke bevise at atlaset aldri
hjelper, men det kan vise at **nytten ikke er observerbar på representative
oppgaver — og det er nok til å flytte kravet fra «antatt» til «ikke demonstrert».**

## Hva dette IKKE måler, og svakhetene ved kjøringen

- **Én agent, ikke 12 isolerte økter.** Protokollen krever ett scenario per økt.
  Det er ikke oppfylt. Jeg hadde dessuten målt alle tallene tidligere samme dag,
  så jeg var ikke et naivt forsøkssubjekt.
- **Derfor måler dette rekkevidde og kostnad, ikke dømmekraft.** Det jeg kan
  måle er: kommer svaret ut, hvor mange steg tar det, og følger kilden med. Det
  jeg *ikke* kan måle her er om en forsker uten forhåndskunnskap beslutter bedre.
- **Ankerfølsomhet:** «0 av 16» bommet bare fordi visningen skriver «0 of 16»
  (K5 oversatte den). Strengen, ikke innholdet, avgjorde.
- **Én kommando per betingelse.** En kyndig bruker ville prøvd `--oversikt` og
  `--alle` etterpå; to kall ville gitt A omtrent 11 av 12. Poenget står likevel:
  B trenger ikke det andre kallet for 10 av 12.

## Det dette peker mot

Atlasets verdi i dag ligger **ikke i oppslaget**. Den ligger der dagens arbeid
faktisk la den:

1. **Vaktene** — 1147 grønne tester som feller deg når et tall, en form eller en
   retning driver (`test_motor_traaden`, `test_atlas_relasjonsretning`,
   `test_usikkerhetslag`, `test_atlas_byggestatus`).
2. **Mutasjonsinstrumentet** — `atlas_feltvekt.py` svarer noe ingen telling kan:
   om et krav faktisk leses. 30 sekunder, og det er den eneste målingen i dag som
   ikke kunne erstattes av et grep.
3. **De ærlige flatene** — `53 uten gruppe (20 observasjoner …)`, `0 of 16
   workflows`, `consumed by no schedule`. De er ikke oppslag; de er *standpunkter*
   som gjør et hull umulig å overse.

Det neste som bør måles er derfor ikke «hjelper atlaset?» én gang til, men om
**vaktene** feller en fremmed endring. Det er en test som kan kjøres av noen
andre, på en oppgave ingen har sett på forhånd.
