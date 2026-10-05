# NATS connection map — which bus subjects feed which engines

Step 9 (2026-09-16), updated after steps 10–12. The map is an
**observation**, not a taxonomy: it describes which subjects
the world bus actually carries, and which EFC engines they can feed.
The division of the world into domains is a decision for the owners — this
map merely MIRRORS that decision as it stands on the bus today.

## The bus

One NATS server («the world server») carries five streams by layer:

| Stream | Layer | Meaning |
|---|---|---|
| VERDEN_OBS | observasjon | instrument-borne raw data (GDELT GKG, MAST/CAOM) |
| VERDEN_TILSTAND | tilstand | aggregated now-state (energy, weather, economy, cosmos catalogues) |
| VERDEN_PROGNOSE | prediksjon / oppgjør | forecasts and settled predictions (weather forecast, ENTSO-E, EFC-fs8) |
| VERDEN_TOLKET | diskusjon / hendelse | interpreted events (GDELT mentions/export, GCN, ALeRCE) |
| OPUS_SELV | — | own judgement ledger (action ledger) |

The subjects have the form `<root>.<domain>.<layer>.<source>` where `root` is `verden`
(societal reality) or `kosmos` (physical reality beyond
it).

## Connections: subject → engine

### Connected (data source exists and is built)

| Subject | Engine | Status |
|---|---|---|
| `verden.energi.tilstand.victron` | `VictronChargeEngine` | **Connected via victron-nats-bro** (outside this repo, read-only). Live on the bus: `batteri_spenning` (V) and `batteri_ladning` (SOC). `batteri_stroem` (A, VRM code `CI`, measured) is **built, not deployed** — the producer code is merged in step 10, but deployment to the bus is the owners' step. Hourly resolution, anonymised site code. The knee detection reports `found=False` (payload: `found`, `t_knee`, `v_knee`, `i_knee` — NaN when not found — plus the counters `n_samples`, `n_cc`, `n_cv`; no reason field; the explanation of the reason stands in the bridge's run artefact). |

**The engine's contract vs the bridge's schema — two different things.** The engine
is injectable and requires per run:

1. `v_series` — voltage over time (V). The bus carries it today
   (`batteri_spenning`).
2. `i_series` — current over time (A). Built in step 10
   (`batteri_stroem`); the producer code is merged (PR #969, in the
   operations repo) and **deployment to the bus is the owners' step** — until then
   the series is absent from the bus.
3. The thresholds `v_knee_tol`, `di_threshold`, `cc_flat_threshold` —
   the engine's own, never the bus's responsibility.

The bridge's schema is the bus's own series; what the bridge does is translate them
into the contract. **Auto-detection of the CC→CV knee requires all three
parts of the contract** — the v-series exists, the i-series is built but
deployment-dependent, the thresholds are the engine's. In addition the knee requires a
time resolution fine enough to see the current plateau: the knee is measured to be invisible in
15-min averages (step 8), so an I-series at hourly resolution will still
give `found=False` — just with a different reason.

### Live on the bus (measured)

| Subject | Content | Engine |
|---|---|---|
| `kosmos.kosmologi.tilstand.efc-fs8` | Sealed fσ8-**baseline**: OBSERVED measurements (DESI DR1, eBOSS) with L/S classification — reference values, not EFC outcomes | none — the baseline is the arbiter's basis, not engine output |
| `kosmos.kosmologi.diskusjon.arxiv` | arXiv papers | (source basis, not measurement) |

### Contracts defined — publication awaits write access

These subjects have a defined schema and an implemented producer side,
but are **not verified live on the bus** — publishing back requires
write access the owners have not yet granted.

| Subject | Content | Producer |
|---|---|---|
| `kosmos.kosmologi.prediksjon.efc-fs8` | EFC **prediction** (modelled fσ8) | `growth` produces the prediction (fσ8(z=0.7), parameter-derived); `SealedFs8Arbiter` (step 12) judges it against the baseline |
| `kosmos.kosmologi.oppgjoer.efc-fs8-arbiter` | The arbiter's **outcome** (PASS/FAIL/VENTER with rule and source) | the arbiter itself — payload format defined in step 12 |

### Candidates (subjects that exist, connection not built)

| Subject | Content | Engine candidate |
|---|---|---|
| `kosmos.hoper.observasjon.mast-caom` | Clusters (MAST/CAOM) | `cluster` |
| `kosmos.galakser.observasjon.mast-caom` | Galaxies | `lensing` (weak lensing) |
| `kosmos.stjerner.observasjon.mast-caom` | Stars | `rotation` (galaxy rotation is the L2 domain; stellar rotation is an analogy candidate) |
| `verden.energi.prediksjon.entsoe-dayahead` | Power price forecasts | (energy economics — no engine yet) |

### Connected via the weather bridge (L-008)

| Subject | Engine | Status |
|---|---|---|
| `verden.vaer.tilstand.metar` | `water` (WaterPhaseEngine) | **Connected via vaer-nats-bro** (outside this repo, read-only). Measured 2026-09-16, 14-day window: **42 stations, 23 688 points**, 6 094 near-condensation, 1 815 with 0,0 °C spread (full saturation) and **12 0 °C crossings** — 3 of the 42 stations went below zero (ENRO, ENDU, ENNA). The series are kept **per station**: joining the airports into one series would turn a jump between two cities into a phase transition that never happened. Below 0 °C the curve is over ice, not over supercooled water (the engine is calibrated 0–100 °C and does not extrapolate). |
| `verden.vaer.tilstand.ecowitt` | `water` (WaterPhaseEngine) | **Connected via vaer-nats-bro** — 3 836 messages, **14 series**, hourly resolution (`opploesning: H`), anonymised site code: `duggpunkt_ute`, `foelt_temperatur_ute`, `luftfuktighet_inne`, `luftfuktighet_ute`, `lufttrykk`, `lynavstand`, `lynnedslag_doegn`, `nedboer_doegn`, `solinnstraaling`, `temperatur_inne`, `temperatur_ute`, `uv_indeks`, `vindkast`, `vindstyrke`. 274 measurements of `temperatur_ute.sola` in the window 2026-09-05T12:00Z → 2026-09-16T21:00Z, all in the liquid regime. **0 crossings** — the minimum in the window is 8,5 °C; that is an answer about the window, not about the year. |

**Correction 2026-09-16: the ecowitt series DO have humidity.** An earlier
edition of this map said the ecowitt channel «has only temperature (no
humidity)», and that the saturation distance therefore could not be computed.
That was measured wrong, and the error was the reader: it fetched five messages
from the subject instead of the subject's series, and came away with one
temperature measurement. `luftfuktighet_ute.sola` (percent) and
`duggpunkt_ute.sola` (°C) stand on the subject at hourly resolution, and the
saturation distance is therefore **computed**: median 113,48 Pa over 274
measurements (11,33–706,21 Pa), with the dew point as an independent control
channel for the same quantity — largest relative deviation between the channels
0,63 %, median 0,17 %. (Saturation distance is P_sat(T) − e, where e is the
water-vapour pressure; it is not the same as relative humidity, and it is not a
phase transition.) The bridge nonetheless carries the `found: false` path with
its reason and with the requirement that would activate the analysis, and a
selftest feeds a synthetic series through EXACTLY the same code and finds the
signal — so a `found: false` is a property of the data, not of the code.

**0 °C crossings: zero is a STATE of its own, not a sign.** A measurement that
lands on exactly 0,0 °C is neither positive nor negative. The rule looks at the
side before and after each zero sequence: + → 0 → − is one crossing down,
− → 0 → + is one up, + → 0 → + is a touch without a crossing. It is not
cosmetics: METAR reports temperature in whole degrees, and a rule that required
NEIGHBOURING MEASUREMENTS to change sign gave **zero** crossings for the three
stations that actually went below zero — until it was corrected. The crossing
time is interpolated between the measurements and tagged `estimert: true`: a
crossing is a between-sampling at hourly resolution, not an observed transition.
Latent heat, phase fraction and latent-heat energy cannot be measured from air
temperature alone — the crossing says that the water would have been
below/above freezing there and then, not that water froze.

Note: near-condensation is a phase-transition PROXY, not the transition itself —
analogy, not identity (the same discipline as the rest of the map).

### Connected via the bridge layer (2026-09-17, kosmos_nats_bro/jord_nats_bro/sol_nats_bro)

| Subject | Engine | Status |
|---|---|---|
| `kosmos.sol.tilstand.swpc-goes-xray` + `kosmos.sol.hendelse.nasa-donki` | `solar_flare` (SolarFlareEngine) | **Connected via sol-nats-bro** — GOES flux to class, DONKI eruptions as trigger events. Candidate status: idealised holding→release model, NOT a flare predictor. |
| `kosmos.jord.tilstand.usgs-seismikk` | `jordskjelv` (JordskjelvEngine) | **Connected via jord-nats-bro** — magnitude → moment (Kanamori inverse), b-value from the event sequence. Candidate status: idealised elastic rebound, NOT an earthquake predictor. |
| `kosmos.romvaer.tilstand.swpc-kp` | `romvaer` (RomvaerEngine) | **Connected via kosmos-nats-bro** — Kp read directly, G level from the NOAA scale. Correlation model, Newell caveat. |
| `kosmos.transienter.hendelse.alerce` | `transient` (TransientEngine) | **Connected via kosmos-nats-bro** — class distribution, stellar-death count. ALeRCE's own classification, not the engine's prediction. |
| `kosmos.planetsystem.prediksjon.jpl-horizons` | `orbital` (OrbitalEngine) | **Connected via kosmos-nats-bro** — avstand_sol_au as an a-proxy (declared). Kepler reproduces the planetary periods. |
| `kosmos.maane.prediksjon.jpl-horizons` | `tidevann` (TidevannEngine) | **Connected via kosmos-nats-bro** — avstand_jord_au → tidal height (open ocean ~0.62 m). |
| `verden.miljo.tilstand.ecowitt` | `klima` (KlimaEngine) | **CO2 observation via kosmos-nats-bro** — greenhouse proxy, NOT forced through the engine (CO2→emissivity is a separate, unasserted chain). |

The bridge round runs every hour (cron e8c6fd64b23f) and publishes on
`opus.dommekraft.tilstand.broer`. All the bridges are external and
read-only (the same design as the weather bridge).

### Not connected, and not an obvious engine candidate (as of today)

The societal subjects (`verden.*` apart from energy/weather: arbeid, demografi, finans,
geopolitikk, helse, handel, lov, miljø, økonomi, politikk, sikkerhet,
teknologi, transport, utdanning) are GDELT/Eurostat/World-Bank data. They are
not phase transitions in the EFC sense — a connection here would be a
category error. They belong in other forms of analysis, not in the regime atlas.

## The reader's limits

This repo **never reads the bus itself** — the engine is injectable and
site-anonymous (the step 8 design). The bridge that reads the bus is an external
data source with a read-only consumer role. The separation is deliberate: the atlas
must not depend on a live bus; the bus is one of several sources that
can feed it. It applies both ways: **publishing back to
the bus** (e.g. the arbiter's outcome) is not built in — it is a
door the owners can open, not a door the repo closes.
