#!/usr/bin/env python3
"""gamma_flrw_consistency.py — read-only dimensional/asymptotic audit of the
published Γ(ρ) forms in DOI 10.6084/m9.figshare.31942821.

A DIAGNOSTIC, not a physical gate. It reports what the published source
declares, and the asymptotics of those declared forms (the source function
is not executed), plus whether each Γ(ρ) prefactor's units are pinned,
without choosing among them and without writing anything to disk.

WHY (observed 2026-09-20, fanout deleg_65a996ff): the published corpus carries
three competing Γ(ρ) realisations for one intended target quantity —

    A  phenomenological     Γ = Γ0 · r/(1+r)                 (r = ρ/ρcrit)
    B  derived (Scenario B)  Γ = Γ0 · r^(3/2)/(1+r)          (gamma_total)
    C  companion (B+)        Γ = Γ0 · y/(1+y),  y = sqrt(r)  (31942800)

and two BE exponents (exp(g/a0) vs exp(sqrt(g/a0))). This script audits only
the Γ forms. It is the paradigm-independent layer: it reads no data and no
ΛCDM measure — only the published source text and arithmetic.

It reports, per form:
    - the low- and high-density asymptotics (does it saturate?),
    - whether the prefactor Γ0's units are pinned (and which),
    - whether the source's σ_s mapping is established.

That last point is decisive and is NOT asserted as an identity: the source
defines Γ = dS/dρ and Ṡ = Γ ρ̇, but the per-mode → physical entropy-density
bridge is not written down there, so the FLRW relation

    σ_s = Γ(ρ) · ρ̇ = -3Hρ · Γ(ρ)        (dust)

is a CANDIDATE only. The audit labels it candidate_FLRW_relation_only and the
σ_s mapping mapping_to_sigma_s_not_established.

Usage:
    python3 scripts/maintenance/gamma_flrw_consistency.py        # report
    python3 scripts/maintenance/gamma_flrw_consistency.py --json

Exit: 0 = computed_from_declared_forms (source text read, declared forms re-implemented); 2 = could_not_read_source.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs" / "papers" / "efc" / "Derivation_of_the_Entropy_Production" / "src" / "entropy_production.py"

DOI = "10.6084/m9.figshare.31942821"

# Needles that pin the published source text. Each is a literal string that
# must appear in entropy_production.py for the audit to count the form as
# "source-pinned" (the literal text is present in the published source).
# (The rho_ratio/(1+rho_ratio) needle is shared by d_eff and
# gamma_phenomenological; that is fine — it pins the form, not a method.)
SOURCE_NEEDLES = {
    "gamma_total_implements_B": "rho_ratio**1.5",
    "header_declares_B": "ρ^(3/2)",
    "phenomenological_A_present": "rho_ratio / (1.0 + rho_ratio)",
    "B_non_saturating_R2": "not saturation",
    "companion_upgrade_declared": "upgrades to Scenario B+",
}


def read_source(path: Path) -> str | None:
    """Return the source text at ``path``, or None if it cannot be read."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def verify_needles(text: str) -> dict[str, bool]:
    return {name: needle in text for name, needle in SOURCE_NEEDLES.items()}


# ── the three forms, re-implemented on a dimensionless r = ρ/ρcrit ─────────
# They are trivial and re-derived here so the audit does not depend on being
# able to import the DOI package (docs/** is off sys.path and outside pytest
# collection). Γ0 is carried as a symbolic prefactor; only asymptotics and
# unit requirements matter.
def gamma_A(r: float) -> float:
    """Γ_A = Γ0 · r/(1+r)."""
    return r / (1.0 + r)


def gamma_B(r: float) -> float:
    """Γ_B = Γ0 · r^(3/2)/(1+r)."""
    return r ** 1.5 / (1.0 + r)


def gamma_C(r: float) -> float:
    """Γ_C = Γ0 · y/(1+y), y = sqrt(r)."""
    y = math.sqrt(r)
    return y / (1.0 + y)


def _loglog_slope(fn, r1: float, r2: float) -> float:
    """Local power-law exponent p such that Γ ~ r^p between r1 and r2."""
    f1, f2 = fn(r1), fn(r2)
    if f1 <= 0 or f2 <= 0:
        return float("nan")
    return math.log(f2 / f1) / math.log(r2 / r1)


def asymptotics() -> dict:
    """Low- and high-density behaviour of each form, COMPUTED FROM SOURCE.

    The exponents are computed as log-log slopes from probe pairs, not
    transcribed from labels, so the test verifies the functions themselves
    rather than echoing a hardcoded expectation. ``shape_family`` is derived
    from the computed saturation, so it cannot drift independently.
    """
    low_lo, low_hi = 1e-6, 1e-4      # deep in the low-density regime
    high_lo, high_hi = 1e4, 1e6      # deep in the high-density regime
    SATURATION_TOL = 0.1             # |high-r slope| below this = saturating
    out = {}
    for name, fn in (("A", gamma_A), ("B", gamma_B), ("C", gamma_C)):
        low_exp = _loglog_slope(fn, low_lo, low_hi)
        high_exp = _loglog_slope(fn, high_lo, high_hi)
        saturates = abs(high_exp) < SATURATION_TOL
        out[name] = {
            "low_density_exponent": round(low_exp, 6),
            "high_density_exponent": round(high_exp, 6),
            "saturates_high_density": saturates,
            "high_density_behavior": (
                "→ Γ0 (saturates)" if saturates
                else "∝ √ρ (grows; non-saturating)"
            ),
            "shape_family": (
                "saturating_rational" if saturates else "non_saturating_power"
            ),
        }
    return out


def dimensional_classification() -> dict:
    """Whether each form's Γ0 prefactor is fully pinned, per the source.

    A and C take a dimensionless argument (r, or y=sqrt(r)); Γ0 carries [Γ].
    B is *displayed* as ρ^(3/2)/(ρ+ρcrit), which carries (density)^(1/2), but
    the code implements it as Gamma_0 · r^(3/2)/(1+r) on a dimensionless
    r = ρ/ρcrit, so Γ0 can carry [Γ]. The two are NOT shown to be reconciled
    in the source; the honest label is a normalization convention left
    unresolved, not a demonstrated unit error.
    """
    return {
        "A": {
            "argument": "r = ρ/ρcrit (dimensionless)",
            "prefactor_units": "[Γ]",
            "classification": "dimensionless_argument",
            "normalization_status": "explicit",
        },
        "B": {
            "argument": "rho_ratio**1.5/(1+rho_ratio) on dimensionless r; displayed as ρ^(3/2)/(ρ+ρcrit)",
            "raw_displayed_form": "carries √ρ unless normalized",
            "implemented_ratio_form": "dimensionless shape, Γ0 carries [Γ]",
            "classification": "normalization_convention_unresolved",
            "normalization_status": "not_explicitly_reconciled",
        },
        "C": {
            "argument": "y = √(ρ/ρcrit) (dimensionless)",
            "prefactor_units": "[Γ]",
            "classification": "dimensionless_argument",
            "normalization_status": "explicit",
        },
    }


def build_report(text: str | None, source_path: Path) -> tuple[int, dict]:
    if text is None:
        return 2, {
            "mode": "gamma_flrw_audit",
            "status": "could_not_read_source",
            "doi": DOI,
            "source": str(source_path),
            "error": "source file could not be read",
        }
    needles = verify_needles(text)
    if not needles["gamma_total_implements_B"] or not needles["header_declares_B"]:
        return 2, {
            "mode": "gamma_flrw_audit",
            "status": "could_not_read_source",
            "doi": DOI,
            "source": str(source_path),
            "needles": needles,
            "error": "the derived B form was not found in the source text",
        }
    return 0, {
        "mode": "gamma_flrw_audit",
        "status": "computed_from_declared_forms",
        "doi": DOI,
        "source": str(source_path),
        "form_provenance": {
            "A": "literal_present_in_source_text (31942821)",
            "B": "literal_present_in_source_text (31942821)",
            "C": "reimplemented_from_companion_declaration — declared in 31942800, "
                 "not read here; closed form y/(1+y) re-implemented for shape "
                 "comparison only",
        },
        "needles": needles,
        "asymptotics": asymptotics(),
        "dimensional_classification": dimensional_classification(),
        "flrw_relation": "σ_s = Γ(ρ)·ρ̇ = -3Hρ·Γ(ρ) (dust)",
        "flrw_relation_status": "candidate_FLRW_relation_only",
        "sigma_s_mapping": "mapping_to_sigma_s_not_established",
        "notes": [
            "B is non-saturating at high density; the source itself records this "
            "in requirement row R2 as 'Partial — not saturation'.",
            "B is displayed as ρ^(3/2)/(ρ+ρcrit) but implemented on a dimensionless "
            "r = ρ/ρcrit; the reconciliation is not shown in the source, so the "
            "normalization convention is left unresolved rather than declared a "
            "unit error.",
            "No data and no ΛCDM measure enter this audit: it reads only source "
            "text and arithmetic, which is the paradigm-independent layer.",
        ],
    }


def print_report(rc: int, report: dict) -> None:
    print(f"gamma FLRW / dimensional audit — {report.get('status')}")
    print(f"  source: {report.get('source')}")
    if rc == 2:
        print(f"  ERROR: {report.get('error')}")
        return
    print("  source needles:")
    for name, hit in report["needles"].items():
        print(f"    {name:32s} {'FOUND' if hit else 'missing'}")
    print("  asymptotics:")
    for name, a in report["asymptotics"].items():
        print(f"    {name}: low-ρ ∝ ρ^{a['low_density_exponent']}; high-ρ {a['high_density_behavior']}")
    print("  dimensional classification:")
    for name, d in report["dimensional_classification"].items():
        if "prefactor_units" in d:
            print(f"    {name}: {d['classification']} — Γ0 carries {d['prefactor_units']}")
        else:
            print(f"    {name}: {d['classification']} — "
                  f"normalization {d.get('normalization_status', '?')}; "
                  f"displayed {d.get('raw_displayed_form', '?')} vs "
                  f"implemented {d.get('implemented_ratio_form', '?')}")
    print(f"  FLRW relation: {report['flrw_relation']}")
    print(f"    status: {report['flrw_relation_status']}")
    print(f"    σ_s mapping: {report['sigma_s_mapping']}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    p.add_argument("--json", action="store_true")
    p.add_argument("--source", default=str(SOURCE),
                   help="override the source path (tests use this)")
    a = p.parse_args(argv)
    source_path = Path(a.source)
    rc, report = build_report(read_source(source_path), source_path)
    if a.json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
    else:
        print_report(rc, report)
    return rc


if __name__ == "__main__":
    sys.exit(main())
