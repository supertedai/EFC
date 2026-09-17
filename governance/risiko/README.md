# Risikoregisteret (reviewer-funksjonen, fase 1)

Dette er EFC-repoets ene, append-only risikoregister. Registeret er
**sannhetskilden** for risiko: et funn som bare ligger som rapporttekst
teller som åpent.

Beslutningsgrunnlaget: `/home/morten/hermes-filer/efc-reviewer-avgjorelse.md`
(2026-09-17, fanout `deleg_2465ee23`, fem perspektiver, konvergerende):
**ingen ny Reviewer-profil** — en reviewer-FUNKSJON eid av orchestrator-laget,
med ekstern attestant ved middels/høy risiko og mennesket som faglig godkjenner
for irreversibelt/kritisk.

## Filene

| Fil | Hva |
|---|---|
| `risiko-register.jsonl` | Selve registeret. Én linje = én post. **Append-only.** |
| `README.md` | Denne fila: skjema, terskler, gater, bruk. |

Append-only er en **git-egenskap**, ikke en fil-egenskap. CI krever at diffen
på `risiko-register.jsonl` bare legger til linjer
(`validate_risk_register.py --base <ref>`), og at hver post validerer
fail-closed. Alt under `governance/risiko/` er eid innhold som alt annet i
repoet (`governance/**` → komponenten `rotfiler`, eier `orchestrator`), og
validatoren kontrollerer det selv i tillegg til `validate_ownership.py`.

## Feltspesifikasjon (`registerversjon: "1.0"`)

Registeret er **lukket**: et felt som ikke står her er en feil, ikke en
opplysning. Norske etiketter fra bestillingen står i parentes der JSON-nøkkelen
er translitterert.

| Felt | Type | Krav |
|---|---|---|
| `risk_id` | str | `RISK-<TYPE>-<4 siffer>`, unik, TYPE må stemme med `type` |
| `type` | str | `HAZID` \| `HAZOP` \| `BLAST_RADIUS` \| `GAP` |
| `hazard_or_deviation` | str | Faren eller feilstanden, én setning |
| `source_change_id` | str | `t_<hex>` \| `pr<nummer>` \| `<base-sha>..<head-sha>` |
| `release_id` | str\|null | null når posten ikke hører til en release |
| `berorte_komponenter` (berørte komponenter) | list[str] | id-er fra `governance/ownership-register.json` — må finnes |
| `arsak` (årsak) | str | Hvorfor dette kan skje |
| `konsekvens` | str | Hva som står på spill |
| `barrierer` | list[str] | Hva som allerede står imot |
| `sannsynlighet` | str | `lav` \| `middels` \| `høy` |
| `alvorlighet` | str | `lav` \| `middels` \| `høy` \| `kritisk` |
| `blast_radius_score` | int | 1–256 (`F × E × P × I`) |
| `klasse` | str | `grønn` \| `gul` \| `rød` — **aldri laxere enn scoren** |
| `eier` | str | Én av `owners` i eierregisteret |
| `utforer` (utfører) | str | Den som registrerte posten |
| `reviewer` | str | **Må være forskjellig fra `utforer`** (ingen selv-review) |
| `status` | str | `oppdaget` → `lukket` \| `superseded` |
| `tiltak` | list[str] | Handlingsbare tiltak |
| `kanban_card_id` | str | `t_<hex>` \| `pr<nummer>` |
| `gate_required` | bool | Påkrevd (`true`) for rød klasse |
| `gate_decision` | str | `venter` \| `godkjent` \| `avslått` \| `ikke_nodvendig` |
| `gate_besluttet_av` | str\|null | Påkrevd når beslutningen er `godkjent`/`avslått`, og må da være `menneske` |
| `evidenslenker` | list[str] | Prefiks `repo:` (stien må finnes) \| `url:` (http/https) \| `ekstern:` (kilde utenfor treet) |
| `opprettet_tid` | str | ISO-8601 |
| `forfall` | str\|null | `YYYY-MM-DD`, `null` = ingen avtalt frist |
| `sist_vurdert` | str | `YYYY-MM-DD` |
| `rest_risiko` (rest-risiko) | str | Hva som fortsatt står åpent |
| `supersedes` | list[str] | risk_id-er denne posten erstatter — må finnes |
| `related_ids` | list[str] | Beslektede risk_id-er — må finnes |
| `registerversjon` | str | `1.0` (ukjent versjon = feil) |

`ekstern:`-prefikset er med vilje: HAZID/HAZOP-analysen som seedet registeret
ligger i dag utenfor treet. En falsk `repo:`-sti ville skjult det.

## Klasse, terskler og hva de krever

`blast_radius.py` regner `BR = F × E × P × I` (hver faktor 1–4, laveste verdi 1
så «ukjent» aldri maskerer risiko):

| Score | Klasse | Krav |
|---|---|---|
| 1–3 | liten | kan lande automatisk |
| 4–7 | material | uavhengig reviewer + rollbackplan + readback |
| 8–15 | høy | 2 uavhengige kontroller (eller reviewer + verifier), ADR |
| 16–31 | kritisk | eiersign-off + canary + **menneskegate** |
| 32+ | blokkerende | freeze/quarantine — bare mennesket kan beslutte |

En **kritisk trigger overstyrer tallet**: privilegium, produksjon
(`figshare/**`, `docs/public/**`), destruktiv (migrering/sletting),
gate-endring (`.github/**`, `governance/**`, `*gate*.py`, scheduler-skriptene)
og ukjent grenseflate (fil uten eier). De fire første gir blokkerende klasse,
ukjent grenseflate gir kritisk.

Registerets `klasse` er `grønn|gul|rød` og mappes slik: liten → grønn,
material/høy → gul, kritisk/blokkerende → rød. Validatoren håndhever at
klassen **aldri er laxere enn scoren**: 4+ kan ikke være grønn, 16+ kan ikke
være gul. Strengere er lov — en kvalitativ vurdering kan løfte en post.

## Gaten

`gate_required: true` + `gate_decision: "venter"` betyr: **endringen kan ikke
lukkes før mennesket har besluttet den.** En lukket post med gatekrav krever
`godkjent`/`avslått`, og begge krever `gate_besluttet_av: "menneske"`.
Ingen automatikk — verken CI, vedlikeholdsrunden eller en profil — kan skrive
en menneskelig beslutning. `blast_radius.py --gate` nekter (exit 1) å slippe
gjennom en kritisk/blokkerende endring uten en slik beslutning i registeret.

## Slik brukes det

```bash
# scorer en diff (rapport; --gate nekter kritisk/blokkerende uten beslutning)
python3 scripts/maintenance/blast_radius.py --diff origin/main
python3 scripts/maintenance/blast_radius.py --diff origin/main --gate

# validerer registeret fail-closed, og krever append-only mot en ref
python3 scripts/maintenance/validate_risk_register.py --json
python3 scripts/maintenance/validate_risk_register.py --json --base origin/main

# den ukentlige runden kjører begge og oppretter ett idempotent kort per funnklasse
python3 scripts/maintenance/vedlikeholdsrunde.py --dry-run

# statusordene i aktivitetsloggen
python3 scripts/maintenance/validate_activity_log.py --json
```

CI: `.github/workflows/efc-risiko.yml` (PR + push til main). Scoreren kjøres
der som **rapport** — gaten er menneskets merge på protected main, ikke en
grønn CI-jobb. Registervalidatoren kjører fail-closed.

## Statusordene (aktivitetsloggen)

`logs/activity.jsonl` kan bære `statusord`: en liste fra
`{maskinelt kontrollert, eksternt verifisert, faglig godkjent}`. Ordene er
**gjensidig uavhengige** — ingen av dem impliserer de to andre, og vakten
legger aldri til eller krever et ord som ikke står i posten. Det ene kravet:
`faglig godkjent` kan bare stå på en post med `role: "menneske"`, fordi
faglig godkjenning ikke kan delegeres til en etikett.

## Seed (2026-09-17)

To poster er seedet fra de eksisterende analysene
(HAZID: 29 farer, HAZOP: 70 feilstater), hver med sin analyses **topp-3**
navngitt i `tiltak`:

- `RISK-HAZID-0001` — privilegiekonsentrasjon, alvorlighet kritisk, score 64,
  rød, gaten venter på mennesket.
- `RISK-BLAST_RADIUS-0001` — kortets egen gate-endring, målt av scoreren
  (`F=3 × E=2 × P=1 × I=4 = 24`, trigger `gate-endring` → blokkerende).

## Hva registeret ikke er

Ærlighetslisten fra designet står: et register er ikke en sannhetsgaranti.
En post er sporbarhet, ikke bevis for at risikoen er håndtert; `superseded`
betyr erstattet, ikke borte; og «ingen registrerte avvik» betyr «ingen
registrerte» — ikke «ingen».
