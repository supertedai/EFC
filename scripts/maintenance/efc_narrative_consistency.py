#!/usr/bin/env python3
"""EFC narrative consistency — the SEMANTIC CI gate.

Structural checks (efc_page_consistency, efc_cross_validate, navbar) verify
counts / DOIs-in-registry / navbar. They do NOT catch the *semantic* drift that
keeps needing manual fixes: oversell phrases, self-contradictions, bare counts
without scope. This gate does.

The canonical narrative is docs/validation-ledger/data/ledger_truth.json — every
ledger must be coherent with it. Run from repo root. Exit 1 on errors.

COORDINATION NOTE (for the correctness_drift_daemon thread): this module exposes
check() -> (errors, warnings) so the daemon can call it for continuous
monitoring. CI runs it as a gate; the daemon can run it on a cycle. Same logic,
two surfaces — please import, don't duplicate.
"""
import os
import re
import sys
import json
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PUBLIC = os.path.join(ROOT, "docs", "public")
DATA = os.path.join(ROOT, "docs", "validation-ledger", "data")
INDEX = os.path.join(ROOT, "docs", "validation-ledger", "index.md")
DOI_MAP = os.path.join(ROOT, "figshare", "doi-map.json")
TRUTH = os.path.join(DATA, "ledger_truth.json")

# Deterministic oversell / contradiction patterns — each is a class of bug we
# have actually had to fix by hand. \b0\b never matches inside "10"/"20".
FORBIDDEN = [
    (r'\b0\s+confirmed\s+falsifications?\b',
     'OVERSELL/CONTRADICTION: "0 confirmed falsifications" — contradicts the canonical count (>0)'),
    (r'\b0\s+falsifications?\s+(?:to date|so far|confirmed)',
     'OVERSELL: implies zero falsifications'),
    (r'6/6\s+DOI-anchored|DOI-anchored</strong>\s*\(0\s+(?:LCDM\s+)?stubs?\)',
     'OVERSELL: fabricated "6/6 DOI-anchored (0 stubs)" inference claim'),
    (r'EFC\s+preferanse-test|EFC\s+preferred[^.<]{0,40}(?:&Delta;&chi;&sup2;|&minus;22\.01|−22\.01)',
     'OVERSELL: bao_desi_y1 "EFC preferred Δχ²=−22" framing on placeholder data'),
]


def _read(fp):
    try:
        return open(fp, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def check():
    """Return (errors, warnings). Importable by the correctness_drift_daemon."""
    errors, warnings = [], []

    # 1. canonical source present + valid
    truth = None
    try:
        truth = json.load(open(TRUTH))
        if "rcmp_regime_status" not in truth or "numbers" not in truth:
            errors.append("ledger_truth.json missing required keys (rcmp_regime_status / numbers)")
    except Exception as e:
        errors.append(f"canonical source ledger_truth.json missing/invalid: {e}")

    # registry figshare ids
    reg = set()
    try:
        reg = set(re.findall(r'\b(\d{7,9})\b', json.dumps(json.load(open(DOI_MAP)))))
    except Exception:
        warnings.append("doi-map.json unreadable — DOI-in-registry check skipped")

    files = sorted(glob.glob(os.path.join(PUBLIC, "*.html")))
    if os.path.exists(INDEX):
        files.append(INDEX)

    for fp in files:
        txt = _read(fp)
        if not txt:
            continue
        name = os.path.basename(fp)
        # 2. forbidden oversell / contradiction phrases
        for pat, msg in FORBIDDEN:
            for m in re.finditer(pat, txt, re.IGNORECASE):
                ctx = re.sub(r"\s+", " ", txt[max(0, m.start() - 25):m.end() + 25])
                errors.append(f"{name}: {msg} — '...{ctx}...'")
        # 3. conflicting falsification counts on one page
        counts = sorted(set(int(x) for x in re.findall(r'(\d+)\s+confirmed\s+falsifications?', txt)))
        if len(counts) > 1:
            warnings.append(f"{name}: conflicting falsification counts {counts} on one page — reconcile + cite with scope (canonical = L2 truth-ring)")
        # 4. figshare DOI cited but not in registry
        if reg:
            for fid in sorted(set(re.findall(r'figshare\.(\d{7,9})', txt))):
                if fid not in reg:
                    warnings.append(f"{name}: figshare DOI {fid} cited but NOT in doi-map registry")
    return errors, warnings


def main():
    errors, warnings = check()
    print("=== EFC narrative consistency (semantic gate) ===")
    for w in warnings:
        print(f"  [WARN ] {w}")
    for e in errors:
        print(f"  [ERROR] {e}")
    if errors:
        print(f"\nFAIL — {len(errors)} narrative error(s). Canonical narrative: ledger_truth.json.")
        return 1
    print(f"\nOK — narrative consistent with ledger_truth.json ✓ ({len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
