# Reproduksjonssett — forseglet EFC-prediksjon fσ8(z≈0.7) = 0.430

Dette settet lar en person **utenfor byOpus** reprodusere den forseglede
EFC-prediksjonen direkte fra kildekoden.

## Hva du reproduserer

Den forseglede prediksjonen:

> fσ8(z ≈ 0.7) = **0.430**

Forseglet i `DOI 10.6084/m9.figshare.32013156` (DESI DR2 full-shape
fσ8-kriterium). Prediksjonen hviler på μ-kanalen («linear growth with
entropy damping»): μ(a) = 1 + (μ_0 − 1)·g(a) med μ_0 = 0.5 i
EFCVariantC, kjørt med kanoniske parametre (Ω_m = 0.3, H0 = 70,
σ8 = 0.8).

## Slik gjør du

```bash
git clone https://github.com/supertedai/EFC.git
cd EFC
python -m venv .venv && . .venv/bin/activate
pip install numpy
python scripts/repro/sealed_fs8_repro.py
```

Forventet resultat:

```
Forseglet verdi:       fσ8(z≈0.7) = 0.430
Beregnet:              fσ8(z=0.7) = 0.4301
Avvik:                 0.0001 (OK — innen 0.5 %)
```

## Hva reproduksjonen viser — og ikke viser

- **Viser:** at motoren gir den forseglede verdien med de deklarerte
  inngangene. Forseglingen ble gjort FØR denne koden var offentlig;
  reproduksjonen bekrefter konsistensen.
- **Viser ikke:** at prediksjonen er riktig mot data. Det er
  arbiterens dom: `efc_inference/arbiter/sealed_fs8.py` sammenligner
  med den faktiske DESI DR2-målingen når den foreligger.

## Kontakt

Spørsmål om settet eller resultatet: åpne en issue på
github.com/supertedai/EFC.
