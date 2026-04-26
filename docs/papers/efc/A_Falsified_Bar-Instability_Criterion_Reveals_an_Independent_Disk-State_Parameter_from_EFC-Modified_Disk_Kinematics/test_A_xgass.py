"""
Stage A — external sample validation on xGASS (Catinella+ 2018).

xGASS = SDSS optical (M_*, Σ_*, R_e, SFR) + Arecibo HI (W50, M_HI).
Sample completely independent of SPARC: 1179 stellar-mass-selected galaxies
at z=0.01-0.05, mostly massive disks.

Pipeline modification: snapshot Π_proxy at R_e (not radial-min over disk window).
Per Mortens directive: same trend, not perfect Π. Same Σ-based Jeans σ_R formula.

Π_proxy(R_e) = V_rot · σ_Jeans(R_e) / (G · Σ(R_e))

V_rot = W50c / (2 sin i)      from HI line width
σ_Jeans = √(π G Σ R_e)        same Jeans formula as SPARC pipeline
Σ at R_e from logSuBr          (M_*/2πR50_z² in M_sun/kpc² per xGASS convention)

External f_gas = M_HI / (M_HI + M_*)   (independent of any rotation curve decomposition)

Reports: ρ(Π_proxy, log Σ_*) and ρ(Π_proxy, f_gas), N, sign.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from disk_state_analysis import spearman

XGASS_DIR = Path("/Users/morpheus/Documents/Claud Code/AGI-Test/data/external/xgass")
OUTDIR = HERE / "output"

# -- SI constants
G_SI = 6.6743e-11
KPC_TO_M = 3.0857e19
KMS_TO_MS = 1.0e3
MSUN_PER_KPC2_TO_KG_PER_M2 = 1.989e30 / (3.0857e19) ** 2  # ~ 2.09e-9
DEG_TO_RAD = np.pi / 180.0


def parse_tsv(path: Path, fields: list[tuple[str, type]]) -> list[dict]:
    """Parse VizieR TSV output (skip metadata lines starting with #)."""
    rows = []
    with open(path) as fh:
        for line in fh:
            stripped = line.rstrip("\n")
            if not stripped or stripped.startswith("#"):
                continue
            # Skip header lines (column names) and dividers
            if "\t" not in stripped:
                continue
            parts = stripped.split("\t")
            # Header rows: first parse fails or contain only column names
            try:
                row = {}
                for i, (name, typ) in enumerate(fields):
                    if i >= len(parts):
                        row[name] = None
                        continue
                    val = parts[i].strip()
                    if val == "" or val == "?":
                        row[name] = None
                    else:
                        try:
                            row[name] = typ(val)
                        except (ValueError, TypeError):
                            row[name] = None
                # Reject if all numeric fields are None (likely header)
                numeric = [v for k, v in row.items() if isinstance(v, (int, float))]
                if numeric:
                    rows.append(row)
            except Exception:
                continue
    return rows


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    # tablea1: GASS, SDSS, z, logM*, R50z, R50r, R90r, logSuBr, extr, rmag, (b/a), incl, NUV-r, SFR
    a1_fields = [
        ("GASS", str), ("SDSS", str), ("z", float),
        ("logM_star", float), ("R50z_kpc", float), ("R50r_kpc", float),
        ("R90r_kpc", float), ("logSuBr", float), ("extr", float),
        ("rmag", float), ("ba_r", float), ("incl_deg", float),
        ("NUV_r", float), ("SFR", float),
    ]
    # tablea2: GASS, W50, W50c, FHI, logMHI, logMHI/M*, q
    a2_fields = [
        ("GASS", str), ("W50_kms", float), ("W50c_kms", float),
        ("FHI", float), ("logMHI", float), ("logMHI_over_Mstar", float),
        ("q", int),
    ]
    a1 = parse_tsv(XGASS_DIR / "tablea1.tsv", a1_fields)
    a2 = parse_tsv(XGASS_DIR / "tablea2.tsv", a2_fields)
    print(f"tablea1 rows: {len(a1)}, tablea2 rows: {len(a2)}")

    a1_by = {r["GASS"]: r for r in a1 if r["GASS"]}
    a2_by = {r["GASS"]: r for r in a2 if r["GASS"]}
    print(f"  unique GASS keys: a1={len(a1_by)}, a2={len(a2_by)}")
    common = set(a1_by) & set(a2_by)
    print(f"  cross-matched: {len(common)}")

    # Compute Π_proxy
    rows = []
    skip_reasons = {}
    for gass in common:
        r1, r2 = a1_by[gass], a2_by[gass]
        # Required fields
        required = [r1.get("logM_star"), r1.get("R50r_kpc"), r1.get("logSuBr"),
                    r1.get("incl_deg"), r2.get("W50c_kms"), r2.get("logMHI")]
        if any(v is None for v in required):
            skip_reasons["missing_field"] = skip_reasons.get("missing_field", 0) + 1
            continue
        incl_deg = r1["incl_deg"]
        if incl_deg < 30:    # face-on, unreliable W50→V_rot
            skip_reasons["face_on"] = skip_reasons.get("face_on", 0) + 1
            continue
        if r2.get("q", 5) > 2:   # quality flag — keep only good HI detections
            skip_reasons["bad_HI"] = skip_reasons.get("bad_HI", 0) + 1
            continue

        # V_rot = W50c / (2 sin i)
        sin_i = np.sin(incl_deg * DEG_TO_RAD)
        V_rot_kms = r2["W50c_kms"] / (2.0 * sin_i)
        # Σ in M_sun/pc² (logSuBr is log10(M_*/2πR50²) in M_sun/kpc²)
        # 1 M_sun/kpc² = 1e-6 M_sun/pc²
        Sigma_Msun_kpc2 = 10.0 ** r1["logSuBr"]
        Sigma_Msun_pc2 = Sigma_Msun_kpc2 * 1e-6
        # SI for σ_Jeans calculation
        Sigma_SI = Sigma_Msun_kpc2 * MSUN_PER_KPC2_TO_KG_PER_M2  # kg/m²
        R_e_SI = r1["R50r_kpc"] * KPC_TO_M
        if Sigma_SI <= 0 or R_e_SI <= 0 or V_rot_kms <= 0:
            skip_reasons["nonpositive"] = skip_reasons.get("nonpositive", 0) + 1
            continue
        # σ_Jeans = √(π G Σ R_e) in m/s
        sigma_jeans_ms = np.sqrt(np.pi * G_SI * Sigma_SI * R_e_SI)
        sigma_jeans_kms = sigma_jeans_ms / 1000.0
        # Π_proxy in SI: V_rot · σ_Jeans / (G · Σ · R_e)  [dimensionless]
        V_SI = V_rot_kms * KMS_TO_MS
        Pi_proxy = V_SI * sigma_jeans_ms / (3.36 * G_SI * Sigma_SI * R_e_SI)

        # External f_gas: M_HI / (M_HI + M_*)
        M_HI = 10.0 ** r2["logMHI"]
        M_star = 10.0 ** r1["logM_star"]
        f_gas_ext = M_HI / (M_HI + M_star)

        # Other
        log_Sigma = np.log10(max(Sigma_Msun_pc2, 1e-3))   # log M_sun/pc²
        rows.append({
            "GASS":      gass,
            "logM_star": r1["logM_star"],
            "R50r_kpc":  r1["R50r_kpc"],
            "incl_deg":  incl_deg,
            "V_rot":     V_rot_kms,
            "sigma_jeans": sigma_jeans_kms,
            "Sigma_Msun_pc2": Sigma_Msun_pc2,
            "log_Sigma":     log_Sigma,
            "Pi_proxy":  Pi_proxy,
            "f_gas":     f_gas_ext,
            "logMHI":    r2["logMHI"],
            "logMHI_over_Mstar": r2.get("logMHI_over_Mstar"),
            "SFR":       r1.get("SFR"),
        })

    print(f"\nUsable: N={len(rows)}, skipped: {skip_reasons}")
    if len(rows) < 30:
        print("WARNING: N too small for robust correlation")

    pi   = np.array([r["Pi_proxy"]  for r in rows])
    logS = np.array([r["log_Sigma"] for r in rows])
    fg   = np.array([r["f_gas"]     for r in rows])
    fg_log = np.array([r["logMHI_over_Mstar"] for r in rows])

    rho_logS, p_logS, n_logS = spearman(pi, logS)
    rho_fg,   p_fg,   n_fg   = spearman(pi, fg)
    rho_fg_log, p_fg_log, _  = spearman(pi, fg_log)

    print(f"\n=== A (xGASS): Π_proxy at R_e ===")
    print(f"  ρ(Π, log Σ_*)        = {rho_logS:+.3f}   (N={n_logS}, p~{p_logS:.3g})")
    print(f"  ρ(Π, f_gas linear)   = {rho_fg:+.3f}   (N={n_fg}, p~{p_fg:.3g})")
    print(f"  ρ(Π, log MHI/M*)     = {rho_fg_log:+.3f}")

    # Sign check
    sign_logS = "−" if rho_logS < 0 else ("+" if rho_logS > 0 else "0")
    sign_fg   = "+" if rho_fg > 0 else ("−" if rho_fg < 0 else "0")
    print(f"\n  signs: log Σ {sign_logS}, f_gas {sign_fg}")

    # Verdict per criterion: PASS if signs match SPARC and |ρ|>0.4
    pass_logS = (rho_logS < 0) and abs(rho_logS) >= 0.4
    pass_fg   = (rho_fg > 0)   and abs(rho_fg) >= 0.4
    soft_pass_logS = (rho_logS < 0) and abs(rho_logS) >= 0.3
    soft_pass_fg   = (rho_fg > 0)   and abs(rho_fg) >= 0.3
    if pass_logS and pass_fg:
        verdict = "PASS"
    elif soft_pass_logS and soft_pass_fg:
        verdict = "SOFT_PASS (sign correct, |ρ| in [0.3, 0.4))"
    elif (rho_logS < 0) and (rho_fg > 0):
        verdict = "WEAK (signs correct but |ρ| < 0.3)"
    else:
        verdict = "FAIL (sign-flip)"
    print(f"\n  Verdict A: {verdict}")

    out = {
        "version": "test_A_xgass_v0.1",
        "N": len(rows),
        "skip_reasons": skip_reasons,
        "rho_Pi_logSigma": rho_logS,
        "rho_Pi_fgas":     rho_fg,
        "rho_Pi_logfgas":  rho_fg_log,
        "sign_logSigma_negative": bool(rho_logS < 0),
        "sign_fgas_positive":     bool(rho_fg > 0),
        "verdict": verdict,
        "per_galaxy": rows,
    }
    out_path = OUTDIR / "test_A_xgass.json"
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2, default=str)
    print(f"\nWrote: {out_path}")
    return out


if __name__ == "__main__":
    main()
