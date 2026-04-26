"""
Fetch bar/no-bar labels for SPARC galaxies via SIMBAD.

For each galaxy:
  - Query http://simbad.cds.unistra.fr/simbad/sim-id?Ident=<name>&output.format=ASCII
  - Parse "Morphological type:" field
  - Classify per de Vaucouleurs bar code:
      SA  → no_bar
      SB  → bar
      SAB → mixed (DROPPED in first-pass per Mortens directive)
      S?  → unknown (no useful classifier in morph string)
      Im, Sm, BCD, irregulars without disk dynamics → not_disk (drop)

Output: data/sparc/sparc_bar_labels.json
       (and a console summary)

Source provenance recorded per galaxy:
  - raw_simbad: raw morphology string from SIMBAD
  - reference_bibcode: e.g. "2019MNRAS.488..590B" (Buta+2019)
  - classifier: "SIMBAD (de Vaucouleurs bar code)"
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

SIMBAD_URL = "https://simbad.cds.unistra.fr/simbad/sim-id"
TIMEOUT = 15
SLEEP_BETWEEN = 0.4   # be polite to SIMBAD


def fetch_simbad(name: str) -> dict:
    """Query SIMBAD by name. Returns dict with raw_text and parsed fields."""
    params = {"Ident": name, "output.format": "ASCII"}
    url = f"{SIMBAD_URL}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
            text = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return {"name": name, "ok": False, "error": type(e).__name__, "raw": ""}

    # Parse Morphological type line
    m = re.search(r"^Morphological type:\s*(\S+)\s*(?:[A-Z]\s+(\S+))?",
                  text, flags=re.MULTILINE)
    if m:
        morph = m.group(1)
        bibcode = m.group(2) or ""
    else:
        morph = ""
        bibcode = ""
    return {
        "name": name,
        "ok": True,
        "morph_raw": morph,
        "bibcode": bibcode,
        "_text_len": len(text),
    }


def classify_bar(morph: str) -> tuple[str, str]:
    """
    Map SIMBAD morphology string → (bar_class, reason).
    Conservative: returns 'unknown' when in doubt.
    Bar class: 'bar' | 'no_bar' | 'mixed' | 'unknown' | 'not_disk'.

    Decision algorithm:
      1. Empty or pure T-type number → unknown
      2. Early-type (E*, S0*, cD, dE, BCD) → not_disk
      3. Irregular (Im, IB, IAB, dI, dIrr, Irr) → not_disk
      4. Range (contains '-') or transition ('/') → unknown
      5. Strip parentheses content: "SA(s)cd" → "SAcd"
      6. Extract bar segment (uppercase letters and underscores after leading "S"
         and any leading "."): e.g. "SAB_a" → "AB", "S_AB" → "AB",
         ".SBT5*." → "B", "SAdm" → "A".
      7. If 'AB' substring or 'X' in segment → mixed
         If segment is 'A' (alone or with separators) → no_bar
         If segment is 'B' (alone or with separators) → bar
      8. "S" alone or "S<lowercase>" with no bar code → unknown
    """
    if not morph:
        return "unknown", "no_morph_string"

    s = morph.strip()
    if not s:
        return "unknown", "empty"

    # Step 1: Pure T-type number
    if re.fullmatch(r"-?\d+(\.\d+)?", s):
        return "unknown", f"only_T_type:{s}"

    su = s.upper()

    # Step 2-3: Non-disk
    if re.match(r"^(E|S0|CD|DE|BCD)\b", su):
        return "not_disk", f"early:{s}"
    if re.match(r"^(IM|IRR|DIRR|DI|IAB|IB|IA)\b", su) or su == "I":
        return "not_disk", f"irregular:{s}"

    # Step 4: Range / transition
    if "-" in s:
        return "unknown", f"range:{s}"
    if "/" in s:
        return "unknown", f"slash:{s}"

    # S alone
    if su == "S":
        return "unknown", "S_alone"

    # Step 5: Strip parenthetical content
    s_clean = re.sub(r"\([^)]*\)", "", s)
    su_clean = s_clean.upper()

    # Step 6: Extract bar segment after leading "." and "S"
    m = re.match(r"^\.?S([A-Z_]*)", s_clean)
    if not m:
        # Not S-family — bare lowercase like "spiral"
        return "unknown", f"not_S_family:{s}"
    seg = m.group(1)            # e.g. "AB", "A", "B", "AB_", "" (for "S")

    # Strip surrounding/internal underscores
    seg_clean = seg.replace("_", "")

    # Step 7: Decide
    if "AB" in seg_clean or "X" in seg_clean:
        return "mixed", f"bar_seg='{seg}':{s}"
    if seg_clean == "A":
        return "no_bar", f"bar_seg=A:{s}"
    if seg_clean == "B":
        return "bar", f"bar_seg=B:{s}"
    if seg_clean == "":
        # Bare "S" followed by nothing or RC3 stage code — unknown
        # e.g. "Sb", "Sbc", "Sa" — bar status not given
        return "unknown", f"S_no_bar_code:{s}"

    # Multi-char with neither AB nor pure A/B (e.g. "SR" for "SR..."?)
    return "unknown", f"unparsed_seg='{seg}':{s}"


def main(use_full_sparc: bool = True):
    if use_full_sparc:
        # Full SPARC-175 sample — load names from .dat
        from sparc_loader import parse_sparc_dat
        from run_pilot import DAT_PATH
        raw = parse_sparc_dat(DAT_PATH)
        names = sorted(raw.keys())
    else:
        pilot_path = HERE / "output" / "n20_shear.json"
        if pilot_path.exists():
            with open(pilot_path) as fh:
                data = json.load(fh)
            names = data["pilot_galaxies"]
        else:
            names = ["NGC2841", "NGC3198"]

    print(f"Querying SIMBAD for {len(names)} galaxies...")
    results = []
    for i, name in enumerate(names):
        # Try with space variant if first attempt fails (e.g. "NGC2841" → "NGC 2841")
        for query_name in (name, name.replace("NGC", "NGC ").replace("UGC", "UGC ")
                           .replace("ESO", "ESO ").replace("IC", "IC ")
                           .replace("DDO", "DDO ").replace("F", "F").strip()):
            r = fetch_simbad(query_name)
            if r["ok"] and r.get("morph_raw"):
                r["query_used"] = query_name
                break
        bar_class, reason = classify_bar(r.get("morph_raw", ""))
        r.update({
            "sparc_name": name,
            "bar_class": bar_class,
            "classify_reason": reason,
        })
        results.append(r)
        print(f"  [{i+1:2d}/{len(names)}] {name:14s} → "
              f"morph='{r.get('morph_raw',''):8s}' bib={r.get('bibcode',''):20s} "
              f"→ {bar_class}  ({reason})")
        time.sleep(SLEEP_BETWEEN)

    # Summary
    counts = {}
    for r in results:
        counts[r["bar_class"]] = counts.get(r["bar_class"], 0) + 1
    print(f"\nClass counts: {counts}")

    # Save
    outdir = Path("/Users/morpheus/Documents/Claud Code/AGI-Test/data/sparc")
    outdir.mkdir(parents=True, exist_ok=True)
    out = {
        "version": "sparc_bar_labels_v0.1",
        "source": "SIMBAD (https://simbad.cds.unistra.fr) — 'Morphological type' field",
        "classifier": "de Vaucouleurs bar code: SA→no_bar, SAB→mixed, SB→bar, S?→unknown",
        "n_queried": len(names),
        "counts": counts,
        "labels": {r["sparc_name"]: {
            "bar_class": r["bar_class"],
            "morph_raw": r.get("morph_raw", ""),
            "bibcode": r.get("bibcode", ""),
            "reason": r["classify_reason"],
        } for r in results},
    }
    out_path = outdir / "sparc_bar_labels.json"
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"\nWrote: {out_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-only", action="store_true",
                        help="Only query the 21-galaxy pilot (default: full SPARC-175)")
    args = parser.parse_args()
    main(use_full_sparc=not args.pilot_only)
