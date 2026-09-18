# Speilretningen mellom motor og atlas — og `efc.klima_engine`-noden

**Kort**: t_6ec0b913 (researcher)
**Dato**: 2026-09-18 (oppdatert etter review runde 1)
**Status**: beslutningen staar i koden, og klima-fixen er **LANDET**. Per
2026-09-18 er #477 (vann-broen), #481 (AMOC-avgrensningen), #482
(klima-validity + de tre koblingene) og #504 (eierkonvensjonen) alle merget
inn i `main`. Maalingene nedenfor er kjort mot `main`, ikke resonnert. Dette
notatet endrer ingen kode; det etterproever og dokumenterer beslutningen.

---

## 1. Hva som ble maalt, og hvorfor

Kortet ble laget fordi `KlimaEngine().regime_node(PARAMS)` og noden
`efc.klima_engine` i `schema/regime_nodes.jsonld` ikke var like — maalt paa
ren `main`. Dette notatet fastslaar hvilken vei sannheten gaar, og etterproever
beslutningen mot alle motorer, ikke bare klima.

## 2. Speilretningen — hvor den staar

Beslutningen er ikke tatt i dette notatet; den staar i koden, i to lag:

1. **I `main`**: docstringen til `scripts/maintenance/efc_bro_synk.py`
   (fra PR #477). Den smale varianten: motoren eier den parameteravledede
   teksten (`regime.validity`, `regime.law_form`); resten av noden —
   `nivaa`, `buss_domene`, `stipulasjoner`, epistemikk-tekstene — er kuratert
   i atlaset og skal ikke skrives av en motor.
2. **I `main`** (merget #504, `8856e831`, 2026-09-18 09:30): den fulle
   konvensjonen — `docs/bro-konvensjon.md` pluss den maskinlesbare
   eiertabellen i `scripts/maintenance/efc_bro_konvensjon.py`, laast av
   `tests/test_bro_konvensjon.py` (dekning, feltvis enighet delt paa eier,
   ingen ueid felt i bruk).

Dette notatet gjentar ikke tabellen. Den er etterproevbar der den staar —
maskinelt: `pytest tests/test_bro_konvensjon.py` (7 passed paa `main` i dag,
`tests/test_klima_engine.py` ytterlegare 10).

## 3. Sterkeste evidens for retningen: en haandskrevet verdi var gal

`efc.orbital_engine`, maalt mot `main` (`392ec766`), foer #504 landet:

| | verdi |
|---|---|
| atlasets `regime.validity` | Hill-sfaeren `1.496e+09 m` |
| motoren, kanoniske PARAMS (`tests/test_orbital_engine.py`, jord-maane) | `6.151e+07 m` |

`1.496e9 m` er jordas Hill-radius mot **solen**, ikke mot jorda. Tallet er
altsaa ikke bare eldre enn motorens — det er feil for systemet noden
beskriver. Et parameteravledet felt som skrives for haand driver, og naar det
driver, er det motoren som regner. Det er hele argumentet for §2. Tallet er
rettet i `main` naa (#504): motorens `6.151e+07 m` staar i atlaset.

## 4. Premisset i kortet holder ikke: den foreslåtte vakta er blind for dette

Kortet foreslo en generisk vakt paa `id`, `regime.name`, `phase`, `perspektiv`.
Maalt over alle 20 motorer med `regime_node()` mot `main`:

* de fire feltene avviker for **1 av 20 noder**: `efc.efc_background_engine`,
  der motoren utsteder id-en `efc.background_engine` som ikke finnes i atlaset;
* for `efc.klima_engine` er de fire feltene **identiske** — ogsaa foer synken.

Vakta ville fanget id-feilen, men **ikke** divergensen den ble foreslått for:
avviket laa i `regime.validity`, en parameteravledet tekst som ikke er blant
de fire. En vakt maa bygges paa eierskapet (§2), ikke paa de fire feltene.

Dette er **én instans** av en langt bredere toveis-divergens, ikke hele
bildet. Konvensjonen som naa ligger i `main` ble forfattet mot et UFIKSERT
tre som maalte «20 motorer, 20 atlas-noder — 20 med avvik, i BEGGE
retninger» og «111 feltavvik i klassen» (`docs/bro-konvensjon.md`). Den
fire-felts-vakten kortet foreslo ville sett 1 av de 111 — og ikke den
parameteravledede som faktisk drev klima-noden. Tallet er tatt med her for at
ingen skal bygge den blinde varianten om igjen.

## 5. Etterproeving av PR #504 (historisk, foer den ble merget)

Verifikasjonen nedenfor ble kjort 2026-09-18 morgen mot PR #504s head
(`703a664a`), uavhengig av kortet som eide den. Den er en historisk rekord:
PR-en er merget siden, og `main` er synkronisert.

| Proven | Resultat |
|---|---|
| `pytest tests/ -q` @ `703a664a` | 796 passed |
| 12 vedlikeholdsgater (`efc_bro_synk --sjekk`, `efc_ontology`, `efc_concepts`, `efc_identity`, `efc_gen_ai_friendly`, `efc_schema_check`, `statement_graph_check`, `efc_verify`, `efc_sync_dois --check`, `validate_repo`, `validate_risk_register`, `verifier_bench`) | alle rc=0, treet urort etterpaa |
| `efc_bro_synk.py --sjekk` | «ingen avvik mellom motor og atlas» |
| `efc.klima_engine` mot motoren | `regime.validity`, `regime.law_form`, `nivaa`, `epistemikk.sosial_mekanisme` identiske; `buss_domene` (`verden.klima`) staar bare i atlaset — som er vedtaket |
| AMOC-avgrensningen | i **baade** nodens og motorens validity |
| TDD: atlas rullet tilbake til `392ec766` | 3 tester roede, deretter groenne |
| Mutasjon: AMOC-klausulen fjernet fra motoren | drept (bro-testen + `test_amoc_bryteren_er_bevisst_utelatt_ikke_glemt`) |
| Mutasjon: `nivaa.indeks` 1 → 2 | drept (`1 avvik: efc.klima_engine [ATLAS-EIDE] /nivaa/indeks`) |
| Mutasjon: motoren utsteder `buss_domene` | drept |

Historisk, ikke aapent: ved PR-ens foerste commit (`8ed292d9`) var den roed paa
`test_efc_atlas_generator` og `efc_ontology` (utdaterte `docs/efc-atlas/*` og
`docs/ontology.*`). PR-ens andre commit (`0f277c10`) regenererte dem.

## 6. Hva som gjenstaar

De tre restrisikoene fra foerste runde er lukket av mergene 09:30: #504 er
landet (ikke `CONFLICTING` lenger), #482 er landet og groenn, og `main` er
synkronisert paa klima-noden. Det som FAKTISK gjenstaar, maalt i dag:

1. **`efc_bro_synk.py --sjekk` exit 1 paa format-drift.** Fila
   `schema/regime_nodes.jsonld` staar ikke lenger i synkens kanoniske format
   (`indent=1`); den ble reformatert til `indent=2` av #545 («close atlas
   stream rest list», `d826235b` — en hel-fil reformat i tillegg til
   innholdet). Synken nekter aa skrive for aa unngaa formatstoy, og
   kortslutter foer den maaler feltavvik. Felt-nivaaet dekkes likevel av
   `pytest tests/test_bro_konvensjon.py` (7 passed i dag). Dette er et
   separat formatfunn, ikke en speilretning.
2. **Hotspot vedvarer, men av en annen grunn.** `schema/regime_nodes.jsonld`
   er fortsatt det tettest skrevne punktet i atlaset: 15 commits har roert
   fila siden #504 landet. Advarselen «ikke legg mer arbeid foer #504 er
   landet» er moen — men format-drift-klassen (punkt 1) er et symptom paa at
   fila fortsatt skrives fra mange kanter samtidig.

## 7. Reproduser

    # de fire feltene, alle motorer
    python3 maal_broer.py            # + maal_resten.py (kosmologi + bakgrunn)
    # de avledede feltene (regime.validity / law_form)
    python3 maal_avledede.py
    # AC2 for klima-noden i et vilkaarlig worktree
    python3 ac2.py <worktree>
    # vedlikeholdsgatene i et worktree
    bash gater.sh <worktree> "<etikett>"
    # mutasjonsprovene og TDD-roed-foer
    bash mutasjon504.sh ; bash tdd_roed.sh
    # #482s rekkefolge-risiko
    python3 pr482_rekkefolge.py

Skriptene under var utforskende og laa i arbeidstreet for kortet
(`.worktrees/t_6ec0b913/scratch/`, uignorert og dermed ikke i historikken).
Den varige reproduserbarheten er ikke dem: #504 har landet, og den kanoniske
proven er `pytest tests/test_bro_konvensjon.py` (felt-nivaaet) og
`python3 scripts/maintenance/efc_bro_synk.py --sjekk` (naar fila igjen staar
i kanonisk format, se §6.1) — verktoyet og vakten som eier konvensjonen,
ikke et engangsskript.
Kanonisk testpython: `/opt/venvs/t_123ed6d9/bin/python` (3.12, numpy 2.5.3,
jsonschema 4.26, pytest 8.4.2).
