# proposals/ — forslag som patcher, ikke som endringer

Denne mappa holder forslag til endringer i atlaset og skjemaet. Ingenting her er
anvendt. Det er poenget: et forslag skal kunne leses, prøves og avvises uten å ha
vært innom grenen.

| Fil | Forslag |
|---|---|
| `H4-MIN-01-korrigendum-A-schema-og-node.patch` | nytt valgfritt nodefelt `korrigendum` i `schema/regime_node.schema.json` + feltet satt på `efc.growth_engine` |
| `H4-MIN-01-korrigendum-B-revisjon.patch` | gjenbruker eksisterende `revisjon` (array av strenger); ingen skjemaendring |
| `verifiser_forslag.py` | anvender hvert forslag, validerer, kjører testene og setter treet tilbake |
| `h4_min01_remaal.py` | remåler tallene notatet bygger på |

Notatet som legger forslagene fram:
`docs/notes/EFC_H4-MIN-01_fire_frys_beslutningsnotat_2026-09-18.md`.

## Reglene

1. **Et forslag er en fil, ikke en tilstand.** Patcher skal ikke anvendes i en gren
   før menneskeordet foreligger. Forslaget som ligger anvendt er ikke et forslag.
2. **Et forslag må kunne prøves.** `python3 docs/notes/proposals/verifiser_forslag.py`
   anvender og ruller tilbake, og sier hva den målte. Kjør med den python-en som har
   `jsonschema` og `pytest` — uten dem hopper skriptet over de punktene og sier det.
3. **Et forslag som rører et lukket skjema må ta med skjemaendringen.**
   `schema/regime_node.schema.json` har `additionalProperties: false`, og C10-porten
   (`scripts/maintenance/efc_schema_check.py`) avviser et felt uten skjemaoppføring.
   Et feltforslag uten skjemahunk er ikke et forslag, det er en feilmelding som
   venter.
4. **Patchene er generert, ikke håndskrevet.** Filformatet i begge filer er
   `json.dumps(..., indent=1|2, ensure_ascii=False)`, som er det formatet
   `scripts/maintenance/efc_bro_synk.py` krever for å kunne skrive tilbake uten å
   reformatere 320 kB. En håndredigert atlasfil ville brutt den kontrakten.
