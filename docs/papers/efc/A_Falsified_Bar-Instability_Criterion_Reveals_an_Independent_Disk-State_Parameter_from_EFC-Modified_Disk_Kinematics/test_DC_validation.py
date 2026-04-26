"""
Stage D + C validation tests for the disk-state CANDIDATE claim.

D — SPARC random half-split:
    Split N=112 into two halves with fixed seeds (42, 7, 13).
    Compute Spearman ρ(Π_min, log Σ) and ρ(Π_min, f_gas) per half.
    PASS if signs agree across halves and seeds.

C — Independent f_gas from SPARC table1 (M_HI, L[3.6]):
    Replace V_gas-derived f_gas with f_gas_HI = (1.4·M_HI) / (1.4·M_HI + Υ·L[3.6]).
    Recompute ρ(Π_min, f_gas_HI).
    PASS if sign agrees with internal f_gas (positive).
    Tests whether the f_gas signal is real or a kinematic-decomposition artefact.

NB: Pipeline UNCHANGED. Π_min computation identical. σ_R unchanged. ζ=1.0 unchanged.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from disk_state_analysis import spearman, ZETA
from sparc_loader import load_classification, parse_sparc_dat, load_sparc_pilot
from run_pilot import DAT_PATH, CLS_PATH, OUTDIR
from classify_fit import pi_min_disk
from disk_state_analysis import galaxy_features

TABLE1_PATH = Path("/Users/morpheus/Documents/Claud Code/AGI-Test/data/external/sparc/SPARC_Lelli2016c.mrt")
DISK_STATE_JSON = OUTDIR / "disk_state.json"

# SPARC table1 column byte ranges (from header)
T1_COLS = [
    ("Galaxy",  ( 0, 11), str),
    ("T",       (11, 13), int),
    ("D",       (13, 19), float),
    ("e_D",     (19, 24), float),
    ("f_D",     (24, 26), int),
    ("Inc",     (26, 30), float),
    ("e_Inc",   (30, 34), float),
    ("L36",     (34, 41), float),    # 10^9 L_sun
    ("e_L36",   (41, 48), float),
    ("Reff",    (48, 53), float),
    ("SBeff",   (53, 61), float),
    ("Rdisk",   (61, 66), float),
    ("SBdisk",  (66, 74), float),
    ("MHI",     (74, 81), float),    # 10^9 M_sun
    ("RHI",     (81, 86), float),
    ("Vflat",   (86, 91), float),
    ("e_Vflat", (91, 96), float),
    ("Q",       (96, 99), int),
]


FIELD_NAMES = ["Galaxy", "T", "D", "e_D", "f_D", "Inc", "e_Inc",
               "L36", "e_L36", "Reff", "SBeff", "Rdisk", "SBdisk",
               "MHI", "RHI", "Vflat", "e_Vflat", "Q"]
FIELD_TYPES = [str, int, float, float, int, float, float,
               float, float, float, float, float, float,
               float, float, float, float, int]


def parse_table1(path: Path) -> dict[str, dict]:
    """
    Parse SPARC Lelli2016c.mrt by whitespace tokens.
    Skips header (lines without numeric tokens after position 0) and notes.
    Returns dict keyed by Galaxy name.
    """
    out = {}
    with open(path) as fh:
        for line in fh:
            stripped = line.rstrip("\n").strip()
            if not stripped:
                continue
            tokens = stripped.split()
            if len(tokens) < 18:
                continue
            # First token must look like a galaxy name (alphanumeric, may contain - +)
            name = tokens[0]
            if not re.match(r"^[A-Za-z][A-Za-z0-9\-\+]*$", name):
                continue
            # Tokens 1..17 must all parse as numbers (T..Q). If not, skip (likely header text).
            try:
                values = []
                for t, typ in zip(tokens[1:18], FIELD_TYPES[1:]):
                    values.append(typ(t))
            except (ValueError, TypeError):
                continue
            row = {"Galaxy": name}
            for fn, v in zip(FIELD_NAMES[1:], values):
                row[fn] = v
            out[name] = row
    return out


# --------------------------------------------------------------------------
# D: random half-splits
# --------------------------------------------------------------------------

def test_D(rows: list[dict], seeds=(42, 7, 13)) -> dict:
    """Random-split each seed; check sign consistency."""
    results = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        idx = np.arange(len(rows))
        rng.shuffle(idx)
        h1 = idx[: len(idx) // 2]
        h2 = idx[len(idx) // 2 :]
        for label, sub_idx in [("half1", h1), ("half2", h2)]:
            sub = [rows[i] for i in sub_idx]
            pi   = np.array([r["Pi_min"]    for r in sub])
            logS = np.array([r["log_Sigma"] for r in sub])
            fgas = np.array([r["f_gas"]     for r in sub])
            r_logS, p_logS, n1 = spearman(pi, logS)
            r_fgas, p_fgas, n2 = spearman(pi, fgas)
            results.append({
                "seed": seed,
                "half": label,
                "n": int(len(sub_idx)),
                "rho_log_Sigma": r_logS,
                "rho_f_gas":     r_fgas,
                "p_log_Sigma":   p_logS,
                "p_f_gas":       p_fgas,
                "sign_log_Sigma_negative": bool(r_logS < 0),
                "sign_f_gas_positive":     bool(r_fgas > 0),
            })
    # Sign-consistency aggregate
    all_logS_neg = all(r["sign_log_Sigma_negative"] for r in results)
    all_fgas_pos = all(r["sign_f_gas_positive"]     for r in results)
    return {
        "results": results,
        "all_seeds_log_Sigma_negative": all_logS_neg,
        "all_seeds_f_gas_positive":     all_fgas_pos,
        "verdict": "PASS" if (all_logS_neg and all_fgas_pos) else "FAIL",
    }


# --------------------------------------------------------------------------
# C: external f_gas from SPARC table1
# --------------------------------------------------------------------------

UPSILON_DISK = 0.5  # M_sun/L_sun at 3.6μm
HE_FACTOR = 1.4     # gas mass = 1.4·MHI (helium correction)


def test_C(rows: list[dict], table1: dict) -> dict:
    """Replace V_gas-derived f_gas with M_HI / (M_HI + M_*) from independent SPARC table1."""
    pi   = []
    f_gas_internal = []
    f_gas_external = []
    log_Sigma = []
    matched_names = []
    unmatched = []
    for r in rows:
        name = r["name"]
        t1 = table1.get(name)
        if t1 is None or t1.get("MHI") is None or t1.get("L36") is None:
            unmatched.append(name)
            continue
        L36_solLum  = t1["L36"] * 1e9     # 10^9 L_sun
        MHI_solMass = t1["MHI"] * 1e9     # 10^9 M_sun
        if L36_solLum <= 0 and MHI_solMass <= 0:
            unmatched.append(name)
            continue
        M_star = UPSILON_DISK * L36_solLum
        M_gas  = HE_FACTOR * MHI_solMass
        denom = M_star + M_gas
        if denom <= 0:
            unmatched.append(name)
            continue
        f_ext = M_gas / denom
        pi.append(r["Pi_min"])
        f_gas_internal.append(r["f_gas"])
        f_gas_external.append(f_ext)
        log_Sigma.append(r["log_Sigma"])
        matched_names.append(name)
    pi = np.array(pi); f_int = np.array(f_gas_internal); f_ext = np.array(f_gas_external)
    logS = np.array(log_Sigma)

    rho_int, p_int, n_int = spearman(pi, f_int)
    rho_ext, p_ext, n_ext = spearman(pi, f_ext)
    rho_logS, p_logS, n_logS = spearman(pi, logS)
    # Sanity check: how well do internal vs external f_gas agree with each other?
    rho_int_ext, p_int_ext, _ = spearman(f_int, f_ext)

    return {
        "n_matched":     int(len(matched_names)),
        "n_unmatched":   int(len(unmatched)),
        "unmatched_names_sample": unmatched[:10],
        "rho_Pi_vs_f_gas_internal":   rho_int,
        "rho_Pi_vs_f_gas_external":   rho_ext,
        "rho_Pi_vs_log_Sigma":        rho_logS,
        "rho_internal_vs_external_f_gas": rho_int_ext,
        "sign_external_positive": bool(rho_ext > 0),
        "verdict": "PASS" if rho_ext > 0 else "FAIL",
    }


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> dict:
    if not DISK_STATE_JSON.exists():
        print("Run disk_state_analysis.py first."); sys.exit(1)
    data = json.load(open(DISK_STATE_JSON))
    rows = data["per_galaxy"]
    print(f"Loaded N={len(rows)} galaxies from disk_state.json")

    # Headline numbers from the original analysis (reference)
    pi   = np.array([r["Pi_min"]    for r in rows])
    logS = np.array([r["log_Sigma"] for r in rows])
    fg   = np.array([r["f_gas"]     for r in rows])
    r_logS_full, _, _ = spearman(pi, logS)
    r_fgas_full, _, _ = spearman(pi, fg)
    print(f"\nFull-sample reference (N={len(rows)}):")
    print(f"  ρ(Π, log Σ) = {r_logS_full:+.3f}")
    print(f"  ρ(Π, f_gas) = {r_fgas_full:+.3f}")

    # D
    print("\n" + "=" * 70)
    print("D: SPARC random half-splits")
    print("=" * 70)
    d = test_D(rows)
    print(f"\n{'seed':>5s} {'half':>6s} {'N':>4s} {'ρ(logΣ)':>10s} {'ρ(f_gas)':>10s}  signs OK?")
    for r in d["results"]:
        ok_S = "−" if r["sign_log_Sigma_negative"] else "✗"
        ok_g = "+" if r["sign_f_gas_positive"]     else "✗"
        print(f"{r['seed']:>5d} {r['half']:>6s} {r['n']:>4d} "
              f"{r['rho_log_Sigma']:+10.3f} {r['rho_f_gas']:+10.3f}   {ok_S} {ok_g}")
    print(f"\nVerdict D: {d['verdict']}  "
          f"(all halves: log Σ negative={d['all_seeds_log_Sigma_negative']}, "
          f"f_gas positive={d['all_seeds_f_gas_positive']})")

    # C
    print("\n" + "=" * 70)
    print("C: Independent f_gas from SPARC table1 (M_HI, L[3.6])")
    print("=" * 70)
    table1 = parse_table1(TABLE1_PATH)
    print(f"  Parsed table1: {len(table1)} galaxies")
    c = test_C(rows, table1)
    print(f"\n  Matched:   {c['n_matched']}/{len(rows)}")
    print(f"  Unmatched: {c['n_unmatched']} (sample: {c['unmatched_names_sample'][:5]})")
    print(f"  ρ(Π, f_gas internal/V_gas-derived):  {c['rho_Pi_vs_f_gas_internal']:+.3f}")
    print(f"  ρ(Π, f_gas EXTERNAL/M_HI-derived):   {c['rho_Pi_vs_f_gas_external']:+.3f}")
    print(f"  ρ(Π, log Σ) on matched subset:       {c['rho_Pi_vs_log_Sigma']:+.3f}")
    print(f"  ρ(internal vs external f_gas):       {c['rho_internal_vs_external_f_gas']:+.3f}")
    print(f"\nVerdict C: {c['verdict']}  (external f_gas correlation positive: {c['sign_external_positive']})")

    out = {
        "version": "DC_validation_v0.1",
        "n_total": len(rows),
        "reference_full_sample": {
            "rho_log_Sigma": r_logS_full,
            "rho_f_gas":     r_fgas_full,
        },
        "D_random_split": d,
        "C_observable_independence": c,
    }
    out_path = OUTDIR / "test_DC.json"
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2, default=str)
    print(f"\nWrote: {out_path}")
    return out


if __name__ == "__main__":
    main()
