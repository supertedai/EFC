"""Isolert verifikasjon av growth.py - ingen pipeline, ingen GRAV."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import numpy as np
from efc.perturbation.growth import solve_growth

print("=" * 60)
print("STEG A: Struktur")
print("=" * 60)
r = solve_growth(Omega_m=0.30, A=0.0, B=0.0)
print("type:", type(r))
print("keys:" if hasattr(r, "keys") else "no keys:",
      list(r.keys()) if hasattr(r, "keys") else "N/A")
print()

print("=" * 60)
print("STEG B: Grid og integrasjon")
print("=" * 60)
a = r["a"] if "a" in r else None
if a is not None:
    print("len(a):", len(a))
    print("a[0], a[-1]:", a[0], a[-1])
print()

print("=" * 60)
print("STEG C: D(a) oppførsel")
print("=" * 60)
if "D" in r:
    D = np.asarray(r["D"])
elif "ln_D" in r:
    D = np.exp(np.asarray(r["ln_D"]))
elif "lnD" in r:
    D = np.exp(np.asarray(r["lnD"]))
else:
    D = None
    print("INGEN D eller ln_D felt funnet!")

if D is not None:
    print("D[0]:", D[0])
    print("D[-1]:", D[-1])
    print("D monotonic:", bool(np.all(np.diff(D) >= 0)))
print()

print("=" * 60)
print("STEG D: f(a) sanity")
print("=" * 60)
if "f" in r:
    f = np.asarray(r["f"])
    print("f[0]:", f[0], "(forvent ~ Omega_m^0.55 ~ 0.52 ved z=50)")
    print("f[-1]:", f[-1], "(forvent ~ 0.5 ved z=0 for LCDM)")
print()

print("=" * 60)
print("STEG E: sigma8 hvis tilgjengelig")
print("=" * 60)
if "sigma8" in r:
    print("sigma8 baseline:", r["sigma8"])
else:
    print("sigma8 ikke i retur - maa beregnes eksternt")
print()

print("=" * 60)
print("STEG F: Omega_m-avhengighet (sjekker at det ikke er hardkodet)")
print("=" * 60)
r_03 = solve_growth(Omega_m=0.30, A=0.0, B=0.0)
r_05 = solve_growth(Omega_m=0.50, A=0.0, B=0.0)

def get_D1(res):
    if "D" in res:
        return np.asarray(res["D"])[-1]
    elif "ln_D" in res:
        return np.exp(np.asarray(res["ln_D"])[-1])
    elif "lnD" in res:
        return np.exp(np.asarray(res["lnD"])[-1])
    return None

D1_03 = get_D1(r_03)
D1_05 = get_D1(r_05)
print("D(a=1) ved Omega_m=0.30:", D1_03)
print("D(a=1) ved Omega_m=0.50:", D1_05)
print("Forskjell:", abs(D1_03 - D1_05) if D1_03 and D1_05 else "N/A")
print("(hvis forskjell < 1e-6 -> mistanke om cache/hardkoding)")
print()

print("=" * 60)
print("STEG G: B-sweep (mu-modifikasjon)")
print("=" * 60)
# LCDM reference for sigma8 scaling
ref = solve_growth(Omega_m=0.30, A=0.0, B=0.0)
# raw D at a=1 before normalization is inaccessible; instead we track
# f(a=1) and growth-history integral as the B-signal.
def growth_signal(res):
    """Mean D(a) over a>=0.5 — sensitive to mu modification."""
    a = np.asarray(res["a"])
    D = np.asarray(res["D"])
    mask = a >= 0.5
    return float(np.trapezoid(D[mask], a[mask]) / (a[mask][-1] - a[mask][0]))

sigma8_LCDM = 0.811
ref_ln_D_raw_end = float(np.asarray(ref["ln_D_raw"])[-1])
print(f"{'B':>6s}  {'D(a=1)':>10s}  {'f(a=1)':>10s}  "
      f"{'D_raw(1)':>10s}  {'sigma8':>8s}")
for B in [0.0, 0.05, 0.087, 0.1]:
    res = solve_growth(Omega_m=0.30, A=0.0, B=B)
    D1 = get_D1(res)
    f1 = float(np.asarray(res["f"])[-1])
    ln_D_raw_end = float(np.asarray(res["ln_D_raw"])[-1])
    D_raw_end = float(np.exp(ln_D_raw_end))
    sigma8 = sigma8_LCDM * np.exp(ln_D_raw_end - ref_ln_D_raw_end)
    print(f"{B:6.3f}  {D1:10.6f}  {f1:10.6f}  {D_raw_end:10.6f}  "
          f"{sigma8:8.4f}")
print()

print("=" * 60)
print("STEG H: mu(a) faktisk brukt?")
print("=" * 60)
try:
    from efc.perturbation.mu import mu_of_a
    print("mu(a=1, B=0.0):", mu_of_a(1.0, 0.0))
    print("mu(a=1, B=0.087):", mu_of_a(1.0, 0.087))
    print("(skal vaere forskjellige)")
except Exception as e:
    print("Kunne ikke importere mu_of_a:", e)

print()
print("=" * 60)
print("FERDIG - kopier hele outputen")
print("=" * 60)
