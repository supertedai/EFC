# Speilretningen mellom motor og atlas — og `efc.klima_engine`-noden

**Kort**: t_6ec0b913 (researcher)
**Dato**: 2026-09-18
**Status**: beslutningen staar (skrevet ned to steder, se §2); maalingene i
denne notatet er kjort, ikke resonnert. Fixen for `efc.klima_engine` ligger i
**PR #504** (aapen, ikke landet) — ikke i denne notatet.

---

## 1. Hva som ble maalt, og hvorfor

Kortet ble laget fordi `KlimaEngine().regime_node(PARAMS)` og noden
`efc.klima_engine` i `schema/regime_nodes.jsonld` ikke var like — maalt paa
ren `main`. Denne notatet fastslaar hvilken vei sannheten gaar, og etterproever
beslutningen mot alle motorer, ikke bare klima.

## 2. Speilretningen — hvor den staar

Beslutningen er ikke tatt i denne notatet; den staar i koden, i to lag:

1. **I `main`**: docstringen til `scripts/maintenance/efc_bro_synk.py`
   (fra PR #477). Den smale varianten: motoren eier den parameteravledede
   teksten (`regime.validity`, `regime.law_form`); resten av noden —
   `nivaa`, `buss_domene`, `stipulasjoner`, epistemikk-tekstene — er kuratert
   i atlaset og skal ikke skrives av en motor.
2. **I PR #504** (`wt/t_b5d8643c`, head `703a664a`, ikke i `main` per
   2026-09-18): den fulle konvensjonen — `docs/bro-konvensjon.md` pluss den
   maskinlesbare eiertabellen i `scripts/maintenance/efc_bro_konvensjon.py`,
   laast av `tests/test_bro_konvensjon.py` (dekning, feltvis enighet delt paa
   eier, ingen ueid felt i bruk).

Denne notatet gjentar ikke tabellen. Den er etterproevbar der den staar —
og naar #504 lander, er den etterproevbar maskinelt.

## 3. Sterkeste evidens for retningen: en haandskrevet verdi var gal

`efc.orbital_engine`, maalt mot `main` (`392ec766`):

| | verdi |
|---|---|
| atlasets `regime.validity` | Hill-sfaeren `1.496e+09 m` |
| motoren, kanoniske PARAMS (`tests/test_orbital_engine.py`, jord-maane) | `6.151e+07 m` |

`1.496e9 m` er jordas Hill-radius mot **solen**, ikke mot jorda. Tallet er
altsaa ikke bare eldre enn motorens — det er feil for systemet noden
beskriver. Et parameteravledet felt som skrives for haand driver, og naar det
driver, er det motoren som regner. Det er hele argumentet for §2.

## 4. Premisset i kortet holder ikke: den foreslåtte vakta er blind for dette

Kortet foreslo en generisk vakt paa `id`, `regime.name`, `phase`, `perspektiv`.
Maalt over alle 20 motorer med `regime_node()` mot `main`:

* de fire feltene avviker for **1 av 20 noder**: `efc.efc_background_engine`,
  der motoren utsteder id-en `efc.background_engine` som ikke finnes i atlaset;
* for `efc.klima_engine` er de fire feltene **identiske** — ogsaa foer synken.

Vakta ville fanget id-feilen, men **ikke** divergensen den ble foreslått for:
avviket laa i `regime.validity`, en parameteravledet tekst som ikke er blant
de fire. En vakt maa bygges paa eierskapet (§2), ikke paa de fire feltene.
Tallet er tatt med her for at ingen skal bygge den blinde varianten om igjen.

## 5. Etterproeving av PR #504 (uavhengig av kortet som eier den)

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

## 6. Restrisiko

1. `main` divergerer fortsatt: hele klima-fixen ligger i #504, som ikke er
   landet. Landingen er menneskeord.
2. **#504 er `CONFLICTING` mot `main`** (`392ec766`): konflikt i
   `docs/efc-atlas/atlas.html`. Filen er generert — riktig opploesning er
   rebase + `efc_atlas_generator.py`, ikke haandmarg.
3. **PR #482 (`wt/t_a6a7619d`, i review) er roed som den staar.** Maalt: dens
   bro-test sammenligner hele `regime`-ordboken, mens node-endringen bare
   skriver «tau ~ 1 år» — AMOC-setningen som #481 la inn i motoren mangler
   (2 feilede tester naar deres egen node-endring legges paa `main`).
4. `schema/regime_nodes.jsonld` har mange skrivere (#504, #482, #464,
   t_9978fc90, t_a6a7619d, t_b251fdc5). Hotspot: ikke legg mer arbeid paa
   filen foer #504 er landet.

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

Skriptene laa i arbeidstreet for kortet
(`.worktrees/t_6ec0b913/scratch/`, uignorert og dermed ikke i historikken);
kommandoene og utfallene staar i §5 og paa kortet.
Kanonisk testpython: `/opt/venvs/t_123ed6d9/bin/python` (3.12, numpy 2.5.3,
jsonschema 4.26, pytest 8.4.2).
