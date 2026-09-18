# Bro-konvensjonen — hvem eier hvilket felt mellom motor og atlas

**Regelen er kode: `scripts/maintenance/efc_bro_konvensjon.py`. Les den der.**
Dette dokumentet forklarer *hvorfor* — og hvorfor nettopp de grensene. En
regel som staar to steder kan drive fra hverandre; en tabell kan testes.

## Problemet, maalt

Hver motor har en `regime_node(params)` — selvbeskrivelsen — og atlaset har
en instans av samme node i `schema/regime_nodes.jsonld`. To beskrivelser av
én ting, vedlikeholdt for haand paa begge sider. Maalt 2026-09-17
(t_2dcd2d82) og igjen 2026-09-18:

    20 motorer, 20 atlas-noder — 20 med avvik, i BEGGE retninger
    111 feltavvik i klassen (test_bro_konvensjon, ufiksert tre)

Derfor er ikke «motoren vinner» et svar: for `regime.validity`, `law_form`,
`stipulasjoner.terskler` og `maale_paradigme.koordinater` er motoren kilden;
for `nivaa`, `epistemikk`, `ontology` og `perspektiv` er atlaset kilden, og
det er motoren som skal rettes.

## Konvensjonen

**Motoren eier** felt som er avledet av motorens parametre eller av maaten
motoren regner paa. De SKRIVES fra motoren til atlaset
(`efc_bro_synk.py --skriv`):

| Felt | Hvorfor motoren |
|---|---|
| `regime.validity`, `regime.law_form`, `regime.name` | bygges av de effektive parametrene — en hardkodet tekst lyver naar motoren kalles med andre |
| `stipulasjoner.terskler`, `stipulasjoner.motor` | terskelen står i koden; navnet er kodens eget |
| `maale_paradigme.koordinater`, `enheter`, `status` | hvilke akser motoren klassifiserer paa |
| `measure.*`, `phase`, `episenter`, `buffer.*`, `emergence.*`, `fractal.*`, `coupling.*`, `observer.*`, `synlighet` | motorens egen beskrivelse av hvordan den maaler og hva den ikke er |

**Atlaset eier** felt som er kuraterte påstander OM noden: hvor den hører i
plataaet, hvordan konsensusen bæres, hvilke analogier den er knyttet til, hva
den ikke sier, og hvilken kilde plasseringen hviler på. Motoren kan ikke
utlede dem av parametrene sine. Utsteder den dem likevel, maa den si det
SAMME som atlaset — og naar de to gaar fra hverandre, rettes motoren:

| Felt | Hvorfor atlaset |
|---|---|
| `id` | identiteten er registrert; en motor som utsteder en uregistrert id er ikke koblet til noe |
| `nivaa.*` | plataa-grafen er atlasets struktur (regel 49-invariantene leser den), og en motor som bare kjenner sine egne parametre kan ikke plassere seg i stigen |
| `epistemikk.*`, `perspektiv` | sannhets-, evidens- og konsensusstatus er epistemiske påstander om noden |
| `ontology.source` | kilden plasseringen hviler på |
| `maale_paradigme.alternativer` | hvilke rammer som ble VALGT BORT |
| `buss_domene`, `ville_falsifisere`, `falsifiserbarhet.*`, `analogi.*`, `prediction.*` | kuratert: hva noden ikke sier, hva som ville felle den, hvilken analogi den staar i, og en forseglet prediksjon |

**To unntak fra likhet**, begge i `DELMENGDE`: `ontology.assumes` og
`maale_paradigme.alternativer` er lister der atlaset skal kunne bære mer enn
motoren (en kuratert antakelse motoren ikke kjenner er lov; en motoren
PÅSTÅR og atlaset ikke har tatt stilling til, er ikke lov). Da feiler testen
til noen har kuratert den inn i atlaset.

## Ingen tredje eier

Et felt motoren utsteder som ingen av tabellene nevner, er et HULL — ikke en
fri sone. Baade testen og `--sjekk` stopper til noen har tatt stilling.
Skjemaet rommer ogsaa node-typer som ikke er motornoder (`/settlement/*`,
`/revisjon`, `/observer/maalepavirkning`); de er navngitt i `UTENFOR_BROEN`
fordi en utelatelse skal være deklarert, ikke stille.

## Hvorfor ikke bare regenerere alt fra motoren

Fordi atlaset da ville mistet det motoren ikke vet: at bakgrunnsloeseren er
en hypotese uten maalt evidens (`efc.efc_background_engine` sa «proxy» om en
avledning som ikke er maalt), at `efc.lensing_engine` staar paa platå 0, at
rotasjonsmotoren kjører LCDM-grensen av EFC-rammen. Og motsatt: `regime.validity`
kan ikke kurateres uten aa bli feil den dagen parametrene endres.

## Verktøyene

| Verktøy | Gjør |
|---|---|
| `efc_bro_synk.py --sjekk` | maaler hele klassen, delt paa eier; exit 1 ved avvik |
| `efc_bro_synk.py --skriv` | skriver de motoreide feltene tilbake (idempotent, formatvakt) |
| `efc_bro_synk.py --json` | maskinlesbar rapport (til vedlikeholdsrunden) |
| `tests/test_bro_konvensjon.py` | binder hele klassen: dekning, feltvis likhet, ingen hull, skjema-dekning |

Kanoniske parametre leses fra testmodulen som eier dem — én kilde for testen
og synken. Motorer der parametrene konstrueres (victron: serier ->
`params_for`; bakgrunnen: `EFC = {**LCDM, ...}`) erklærer dem i en
`bro_kanoniske()` i sin egen testmodul, slik at verken synken eller testen
gjetter hvilket modulnivaa-dict som er «det kanoniske».

## Den gamle rekonosansen ble ikke et eget skript

`bro_drift_audit.py` (t_2dcd2d82) fant motorer ved aa skanne testmodulene og
gjettet parametre fra modulnivaa-dict-er. Det den kunne — listeformede
parametre (`KANONISKE`) og `params_for(...)` — ligger naa i den ENE
resolveren (`efc_bro_konvensjon.kanoniske_parametre`), brukt av baade synken
og testen, og alle 20 motorer maales. Dekningen testes i stedet: en ny motor
uten bro, eller en bro uten atlas-node, feiler `test_bro_konvensjon.py`. Et
eget audit-skript ved siden av ville vært et andre verktøy som maaler den
samme virkeligheten — den klassen drift dette kortet finnes for aa stoppe.

## Kjente funn som ikke er lukket her

* `epistemikk.sosial_mekanisme` er en MAL paa alle 20 motor-noder i atlaset
  (17 med lang tekst, 3 med kort). Regel 46 krever individualisert tekst;
  konvensjonen binder motor til atlas, men sier ikke at teksten er god.
* `efc.efc_background_engine`s kuraterte korttekst ble erstattet av motorens
  fyldigere selvbeskrivelse da noden ble regenerert (den hadde aldri vært
  avledet). Proveniensen er beholdt i `ontology.source`.
