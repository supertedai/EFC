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

---

## Reproducibility note — appended 2026-09-20, after the seal

*(In English per the language rule: new text is written in English; the
Norwegian above is historical and is not translated.)*

**This is a CLOSED, DATED measurement.** Its input is not «the atlas» — it is
the atlas as it stood when `key.json` was sealed. Both readers read
`origin/main` at run time, which quietly made every sealed answer depend on a
bank that is still being edited. That is the defect this note records.

* Sealed input: `schema/regime_nodes.jsonld` at commit
  `c70e004d508dbd341271bd3f272e656e8d14db1a` (the commit that added `key.json`,
  both readers and this file), sha256
  `f61049c40463e3eaa22d6d822f165faba59b85d1c28864caba2a6df38f014b2a`.
* The pin lives in `bank.py`, and `test_repro.py` re-derives the table below
  from it.

### What the break was

Measured 2026-09-19 on `origin/main` (`bbc2c3b1`): `pytest
docs/efc-atlas/eksperiment -q` gave **4 failed, 8 passed**. The key was intact
(`key.json` sha256 unchanged, matching `KEY_SHA256`); the bank under the
readers had moved. Two commits landed on 2026-09-18, **68 and 75 minutes after
the seal (21:26)**:

| commit | when | what it did | questions it falsifies |
|---|---|---|---|
| `10087393` (#567) | 2026-09-18 22:34 | the six `OBSERVED_IN` rows with an **engine as subject** became `obs.X --OBSERVED_THROUGH--> efc.motor`; the duplicated `ANALOGOUS_TO` row was removed and the predicate's symmetry declared | Q1, Q4, Q5 |
| `fe865b95` (#568) | 2026-09-18 22:41 | ADR-086 §3.1, adopted by Morten 2026-09-18: the optional `usikkerhet` field came in — `obs.rar` k = 0.415 ± 0.029, `obs.bao` β = 0.16 as a HOLE | Q7 |

The direction matters: **the bank was not broken, it was repaired.** `#567`
closes K6 (`t_efcfe7f0`) and measures exactly the defect Q4 measured here — six
engine-subject edges, one pair stated in both directions. It does not cite this
experiment; the two findings are independent and agree. `#568` is the
uncertainty layer coming in, the question the §"Hva det betyr for ADR-086"
section above fed.

Per-reference measurement (reader B):

| ref | Q1 `observasjon` | Q4 | Q5 `syklus` | Q7 `antall` |
|---|---|---|---|---|
| `c70e004d`, and its parent | `[obs.fsigma8, obs.s8]` | finds `efc.hubble_engine OBSERVED_IN obs.bao` | true | 0 |
| `10087393` | `[]` | abstains (no inverted edge) | false | 0 |
| `fe865b95` … `origin/main` | `[]` | abstains | false | **1** |

### What reproduces, and what does not

**Reproduces — on the sealed bank, exactly.** Re-derived with `scorer.py`, not
asserted by hand:

```text
A: {"korrekt": 5, "feil": 1, "avstaaelse": 2, "falske_stoettepastander": 0, "proveniens": 6}
B: {"korrekt": 7, "feil": 1, "avstaaelse": 0, "falske_stoettepastander": 0, "proveniens": 8}
```

That is the table at the top of this file, number for number. The argument that
survives is the one about the instrument: the decisive criterion could not fire
because system A was allowed to abstain, and that is a property of the design,
reproducible forever.

**Does NOT reproduce — on the living atlas.** Measured on `origin/main`
2026-09-20: A `{"korrekt": 3, "feil": 3, "avstaaelse": 2, "falske_stoettepastander": 0, "proveniens": 6}`,
B `{"korrekt": 4, "feil": 3, "avstaaelse": 1, "falske_stoettepastander": 0, "proveniens": 8}`.
Everything in this file that describes the *state of the bank* is a statement
about 2026-09-18 and nothing else:

* the row counts in Q3 and the inverted-edge count in Q4 — the six edges are
  gone;
* Q5's «2 rows for the pair» — the pair now stands once, with symmetry declared
  in the predicate;
* Q7's «no node carries an uncertainty field» — one does;
* the coverage gain that survived the run («B answers two questions A abstains
  from, Q3 and Q7, both correctly») no longer holds on the living atlas: the
  bank has the field, B answers 1 where the sealed key says 0, and A still
  abstains on Q7 by construction.

**No new key was written, and that is deliberate.** A re-run against today's
bank is a *different* experiment with a new key: the §"Neste iterasjon" rule
above requires key → verify → freeze → build, and both systems already exist.
Writing a key now would repeat the ordering error this file lists as its second
self-inflicted finding, and would erase the dated measurement.

### How to run it

```sh
/opt/venvs/t_123ed6d9/bin/python -m pytest docs/efc-atlas/eksperiment -q   # 18 passed
make eksperiment PYTHON=/opt/venvs/t_123ed6d9/bin/python
```

`bank.py` reads the seal commit; a shallow clone cannot see it and says so
instead of falling back to another ref. The readers keep `--ref` for honest
runs against the living atlas:

```sh
/opt/venvs/t_123ed6d9/bin/python docs/efc-atlas/eksperiment/leser_b.py --ref origin/main
```

`test_repro.py` asserts both claims: that the sealed table reproduces on the
snapshot, and that the living atlas has drifted in exactly the two ways named
above. If the drift is undone, that test fails and points back to this note —
so this note cannot quietly stop being true.

