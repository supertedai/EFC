#!/usr/bin/env python3
"""verifiser_forslag — prøver et atlasforslag uten å etterlate det i treet.

For hver .patch i denne mappa: anvend, valider, kjør testene, sett treet tilbake.
Ingen av forslagene skal ligge i grenen; dette skriptet er beviset for at de
*kan* anvendes og at de er skjemagyldige.

    python3 docs/notes/proposals/verifiser_forslag.py            # begge
    python3 docs/notes/proposals/verifiser_forslag.py A           # bare A

Krav: git i PATH. jsonschema brukes hvis det finnes (samme krav som C10-porten).
pytest kjøres bare hvis det finnes; testlista hoppes over ellers og sier det.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROT = pathlib.Path(__file__).resolve().parents[3]
SCHEMA = ROT / "schema/regime_node.schema.json"
INSTANS = ROT / "schema/regime_nodes.jsonld"
MAPPE = ROT / "docs/notes/proposals"
BERØRTE = ("schema/regime_nodes.jsonld", "schema/regime_node.schema.json")
TESTER = [
    "tests/test_regime_node_schema.py",
    "tests/test_prediksjon_og_oppgjoer.py",
    "tests/test_efc_atlas_generator.py",
    "tests/test_atlas_dekning.py",
    "tests/test_falsifiserbarhet.py",
]

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None


def git(*a):
    return subprocess.run(["git", *a], cwd=ROT, capture_output=True, text=True)


def last(p):
    return json.loads(p.read_text(encoding="utf-8"))


def aapne_subschemaer(o, sti="$"):
    """Object-schemaer uten additionalProperties: false (C10-portens closure-krav)."""
    aapne = []
    if isinstance(o, dict):
        if (o.get("type") == "object" or "properties" in o or "patternProperties" in o) \
                and o.get("additionalProperties") is not False:
            aapne.append(sti)
        for k, v in o.items():
            if k in ("$defs", "definitions", "properties", "patternProperties") and isinstance(v, dict):
                for kk, vv in v.items():
                    aapne += aapne_subschemaer(vv, f"{sti}.{k}.{kk}")
            elif k in ("items", "allOf", "anyOf", "oneOf", "not", "additionalProperties"):
                aapne += aapne_subschemaer(v, f"{sti}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            aapne += aapne_subschemaer(v, f"{sti}[{i}]")
    return aapne


def proev(patch: pathlib.Path) -> bool:
    print(f"\n===== {patch.name} =====")
    git("checkout", "--", *BERØRTE)
    r = git("apply", "--check", str(patch))
    print(f"  git apply --check : {'OK' if r.returncode == 0 else 'FEIL: ' + r.stderr.strip()}")
    if r.returncode != 0:
        return False
    git("apply", str(patch))

    ok = True
    if jsonschema is None:
        print("  jsonschema mangler — hopper over skjemapunktene")
        ok = False
    else:
        s = last(SCHEMA)
        try:
            jsonschema.Draft202012Validator.check_schema(s)
            print("  metaschema        : OK (Draft202012)")
        except Exception as e:  # noqa: BLE001
            print(f"  metaschema        : FEIL {e}")
            ok = False
        inst = last(INSTANS)
        feil = sorted(jsonschema.Draft202012Validator(s).iter_errors(inst), key=lambda e: list(e.path))
        print(f"  instansen         : {'OK' if not feil else str(len(feil)) + ' FEIL'}"
              f" ({len(inst['nodes'])} noder)")
        for e in feil[:5]:
            print("      -", list(e.path), e.message[:140])
        ok = ok and not feil
        aapne = aapne_subschemaer(s)
        print(f"  C10-closure       : {'OK' if not aapne else 'AAPNE: ' + ', '.join(aapne[:5])}")
        ok = ok and not aapne

    pred = next(n for n in last(INSTANS)["nodes"] if n.get("id") == "efc.growth_engine")["prediction"]
    uroert = (pred.get("sealed_doi") == "10.6084/m9.figshare.32013156"
              and str(pred.get("sealing_sha256")).startswith("fbb53d61")
              and pred.get("arbiter_waiting_for") == "DESI DR2 full-shape"
              and len(pred) == 18)
    print(f"  prediksjonsblokken: {'urørt (18 nøkler)' if uroert else 'ENDRET'}")
    ok = ok and uroert

    fl = next((n.get("id") for n in last(INSTANS)["nodes"]
               if n.get("id") == "efc.growth_engine" and ("korrigendum" in n or "revisjon" in n)), None)
    print(f"  flaggfeltet       : {fl!r} satt")

    try:
        t = subprocess.run([sys.executable, "-m", "pytest", "-q", *TESTER],
                           cwd=ROT, capture_output=True, text=True)
        siste = [l for l in t.stdout.strip().splitlines() if l.strip()][-1:]
        print(f"  tester            : {siste[0] if siste else t.stdout[-200:] or t.stderr[-200:]}")
        ok = ok and t.returncode == 0
    except FileNotFoundError:
        print("  tester            : pytest finnes ikke her — ikke kjørt")

    git("checkout", "--", *BERØRTE)
    # Bare sporede endringer teller her: notatet og patchene i denne mappa er
    # nye filer i grenen, og skal ikke få «treet er ikke rent» til å lyse.
    status = git("status", "--short", "--untracked-files=no").stdout.strip()
    print(f"  treet tilbake     : {'OK (ingen sporede endringer igjen)' if not status else 'IKKE RENT: ' + status}")
    return ok


def main(argv):
    valg = (argv[1] if len(argv) > 1 else "AB").upper()
    patcher = sorted(MAPPE.glob("H4-MIN-01-korrigendum-*.patch"))
    if valg != "AB":
        patcher = [p for p in patcher if f"-{valg}-" in p.name]
    if not patcher:
        sys.exit("ingen patcher funnet")
    alle = {p.name: proev(p) for p in patcher}
    print("\n===== oppsummering =====")
    for navn, ok in alle.items():
        print(f"  {'OK  ' if ok else 'FEIL'} {navn}")
    return 0 if all(alle.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
