# Preregistration proposal — Axis 2: propagation distance (dL^GW vs dL^EM)

**Status:** `proposed — awaiting author freeze` (not executed, not fitted, not published)
**Related register:** `docs/validation-ledger/data/form_status_register.json`
**Related open mapping:** F5 (η_grav vs the two-velocity motor lag is an undeclared hypothesis)

## 1. What is being tested

Whether the gravitational-wave luminosity distance dL^GW and the electromagnetic luminosity
distance dL^EM, measured for the same source, are equal. ΛCDM/GR predicts exact equality;
a deviation would be a signal that the propagation sector carries a model field (the class of
deviation the motor/slip picture predicts, but does not yet specify).

## 2. Hypothesis under test

**H0 (ΛCDM/GR null):** dL^GW = dL^EM at all redshifts.
**H1 (EFC deviation):** dL^GW ≠ dL^EM, with a sign/shape/z-dependence IF EFC provides one.

**Honesty requirement:** EFC does not currently supply an explicit dL^GW/dL^EM formula. Until
one is derived, this is a **test candidate**, not a finished preregistered prediction. This
document records the candidate and the protocol; it does not claim a predicted deviation.

## 3. Frozen observable

The ratio r(z) = dL^GW / dL^EM as a function of redshift z, for standard-siren events with a
host-galaxy identification.

## 4. Measurement chain (raw data → instrument → measurer → target → proxy)

| Layer | Content |
|---|---|
| Raw data | GW strain waveform (amplitude); host-galaxy redshift; EM distance estimate |
| Instrument | GW detector network (amplitude calibration); optical/IR spectroscopy (redshift, host) |
| Measurer (GW) | dL^GW from the waveform amplitude (self-calibrating, no cosmic distance ladder) |
| Measurer (EM) | dL^EM from redshift via the cosmic distance ladder / standard calibrators |
| Target | the ratio r(z) = dL^GW / dL^EM |
| Proxy | none beyond the two distance estimators; the ratio is the near-direct observable |

## 5. What is frozen vs what is a declared nuisance

**Frozen:**

- The observable r(z) and its definition.
- The null model: r(z) = 1 exactly (GR/ΛCDM).
- The event-selection criteria, redshift binning, and frequency range, declared before data.

**Declared nuisance:**

- Astrophysical systematics: host misidentification, lensing, peculiar velocities, waveform
  systematics, EM distance calibration. Each gets a pre-declared prior or treatment.

## 6. Protocol discipline

- No post hoc selection of sirens, redshift intervals, or frequency bands.
- Pre-declared holdout / sample-splitting where the data volume permits.
- The two distance estimators are kept distinct; their uncertainties are propagated, not
  merged.

## 7. Self-inclusion matrix

| Field | Value |
|---|---|
| raw data | GW strain + host spectroscopy + EM distance |
| instrument | GW detector + optical/IR spectrograph |
| measurer | waveform amplitude → dL^GW; redshift + ladder → dL^EM |
| target | r(z) = dL^GW/dL^EM |
| proxy | near-direct ratio (minimal proxy) |
| paradigm content | **resistant** — the GW side is self-calibrating; the EM side carries the ladder, but the ratio isolates the propagation difference rather than the absolute distance |
| holdout | required where data permit |
| falsifier | see §8 |

## 8. Falsifier and threshold

- **For the null:** H0 (equality) is rejected if r(z) deviates from 1 beyond a pre-declared
  combined-significance threshold across the sample.
- **For EFC:** a specific deviation is only tested once a derived r(z) prediction exists;
  until then a null result (r = 1) is a legitimate and informative outcome that constrains
  the slip hypothesis.

## 9. What this test does NOT decide

- It does not identify the internal motor-lag η as the cause of any deviation; it only
  detects a propagation-distance difference (F5 remains an open mapping).
- It does not test the E(g) exponent (Axis 1) or the Γ(ρ) density form.

## 10. Compute-gate note

No `.14` compute mode exists for this test. Running it (or even a synthetic null simulation)
requires a **new human-authorized allowlist mode**. This document registers the intent; it
does not authorize the run.

## 11. Open author decisions (blocking)

1. Whether to derive a specific EFC dL^GW/dL^EM prediction first (making this a real
   preregistration) or register it as a null-constraint candidate now.
2. Whether this axis runs before, after, or in parallel with Axis 1.
