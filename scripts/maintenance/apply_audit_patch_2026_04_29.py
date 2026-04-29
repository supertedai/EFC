#!/usr/bin/env python3
"""Apply DOI ledger consistency audit patch (2026-04-29).

Closes consistency gaps between three internal canonical sources:
  - figshare/doi-map.json
  - docs/papers/efc/efc_index.json
  - docs/validation-ledger/data/evidence-register.json

Audit found (DOI-first, repo-internal cross-validation):
  - 2 DOIs in evidence-register but missing from doi-map (32099389, 32113399)
  - 25 DOIs in doi-map but missing from efc_index
  - 10 doi-map entries with empty title
  - 1 orphan (28102772, null path) - kept as-is, needs human judgment

This script:
  1. Adds the 2 new DOIs to figshare/doi-map.json
  2. Fills 10 empty titles in figshare/doi-map.json (sourced from each
     paper's own canonical index.json)
  3. Adds 26 missing entries to docs/papers/efc/efc_index.json
     (24 already-in-doi-map + 32099389 + 32113399), each entry's
     id/path/type/doi sourced from the paper's index.json
  4. Bumps efc_index.json version 1.10 -> 1.11

Idempotent: re-running after applying is a no-op.

Usage:  python scripts/maintenance/apply_audit_patch_2026_04_29.py [--dry-run]
"""
from __future__ import annotations
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOI_MAP_PATH = os.path.join(REPO, "figshare", "doi-map.json")
EFC_IDX_PATH = os.path.join(REPO, "docs", "papers", "efc", "efc_index.json")
PAPERS_DIR = os.path.join(REPO, "docs", "papers", "efc")

DOI_RE = re.compile(r"10\.6084/m9\.figshare\.(\d{7,9})")


def bare(s):
    if not s:
        return None
    m = DOI_RE.search(str(s))
    return m.group(1) if m else None


# DOI -> path-relative-to-PAPERS_DIR for the 36 papers we touch
PATCH_PAPERS = {
    # 24 already in doi-map, missing from efc_index (skip 28102772 orphan)
    "31969983": "Closing_the_EFC_Consciousness_Bridge",
    "31970886": "efc_white_paper_part_1_to_4/White_paper_part_1_efc_recovery_limits",
    "31970898": "efc_white_paper_part_1_to_4/White_paper_part_2_efc_field_equations_observables",
    "31970904": "efc_white_paper_part_1_to_4/White_paper_part_3_efc_validation_falsification",
    "31970907": "efc_white_paper_part_1_to_4/White_paper_part_4_efc_regime_susceptibility",
    "31985163": "EFC_Background_NoGo_Theorem",
    "31985313": "Scale_Localised_Modified_Gravity",
    "31990053": "efc_euclid_prediction",
    "31990194": "efc_case_b_eigenmode",
    "31990212": "ISW_Void_SignFlip_Pipeline",
    "32010399": "EFC_PreRegistered_Predictions",
    "32011407": "EFC_Effective_Horndeski_Reduction",
    "32013156": "Sealed_Blind_Predictions_for_Growth_Rate_Observables_EFC_vs_LCDM",
    "32013738": "EFC_Rubin_DP2_PreRegistration",
    "32019723": "component_weighted_bias",
    "32023788": "efc_eg_preregistration",
    "32029704": "sparc175_elimination",
    "32037990": "efc_perturbation_sector",
    "32045592": "EFC_Outcome_Estimation_CrossSurvey",
    "32080059": "EFC_compound_paper",
    "32080080": "EFC_RCMP_Convergence_Observation",
    "32080083": "EFC_RCMP_Test_Specification",
    "32084670": "A_structural_closure_of_growth_sector_couplings",
    "32101111": (
        "A_Falsified_Bar-Instability_Criterion_Reveals_an_Independent_Disk-State_"
        "Parameter_from_EFC-Modified_Disk_Kinematics"
    ),
    # 2 new (missing from BOTH doi-map and efc_index)
    "32099389": "Homo Fluxus A Thermodynamic Framework",
    "32113399": "efc_redshift_decomposition",
    # 10 empty-title fills (already in efc_index, just missing title in doi-map)
    "31127380": "EFC-Phenomenology-vs-DESI-DR2-BAO-A-Comparative-Fit-Analysis",
    "31144030": (
        "Regime_Dependent_Growth_Enhancement___A_Transition_Metric_Interpretation_"
        "of_the_Fugaku_DESI_Matter_Density_Offset"
    ),
    "31190233": "Empirical-Validation-of-Energy-Flow-Cosmology-Cluster-Lensing-and-Galaxy-Rotation-Curves",
    "31222696": (
        "Energy_Flow_Cosmology__An_Effective_Phenomenological_Law_for_Gravitational_"
        "Response_in_Structure_Dominated_Regimes"
    ),
    "31222900": (
        "The-Regime-Consistent-Measurement-Principle-RCMP-A-Methodological-"
        "Framework-for-Multi-Scale-Physics"
    ),
    "31223668": "EFC_Ontological_Foundations",
    "31224466": "EFC_Closure_Conjectures",
    "31348414": "Cosmological_Growth_Constraints_on_Λ-Locked_Discrete_Entropic_Gravity",
    "31348417": "Regime_Structure_and_Entropic_Flow_Ontology_in_Discrete_Gravity_Models",
    "31562200": (
        "Minimal_EFC_Effective_Field_Theory_Ansatz_Scalar_Tensor_and_Vector_Tensor_"
        "Formulations_with_Gravitational_Slip_from_Entropy_Gradients"
    ),
}

ADD_TO_DOI_MAP = ["32099389", "32113399"]
EMPTY_TITLE_DOIS = [
    "31127380", "31144030", "31190233", "31222696", "31222900",
    "31223668", "31224466", "31348414", "31348417", "31562200",
]


def load_paper_index(rel_path):
    p = os.path.join(PAPERS_DIR, rel_path, "index.json")
    if not os.path.isfile(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def patch_doi_map(dm):
    changes = []
    for d in EMPTY_TITLE_DOIS:
        canon = f"10.6084/m9.figshare.{d}"
        if canon not in dm:
            print(f"  WARN: {canon} not in doi-map, skipping title fill")
            continue
        if dm[canon].get("title", "").strip():
            continue
        idx = load_paper_index(PATCH_PAPERS[d])
        if not idx or not idx.get("title"):
            print(f"  WARN: no title in {PATCH_PAPERS[d]}/index.json")
            continue
        dm[canon]["title"] = idx["title"]
        changes.append(f"  fill title: {d} -> {idx['title'][:60]}...")
    for d in ADD_TO_DOI_MAP:
        canon = f"10.6084/m9.figshare.{d}"
        if canon in dm:
            continue
        idx = load_paper_index(PATCH_PAPERS[d])
        if not idx:
            print(f"  WARN: no index.json at {PATCH_PAPERS[d]}, skipping")
            continue
        dm[canon] = {
            "figshare_id": int(d),
            "title": idx.get("title", ""),
            "path": f"docs/papers/efc/{PATCH_PAPERS[d]}",
            "url": f"https://doi.org/{canon}",
        }
        changes.append(f"  add: {d} -> {idx.get('title', '')[:60]}...")
    return changes


def patch_efc_index(ei):
    existing = {bare(p.get("doi")) for p in ei.get("papers", []) if bare(p.get("doi"))}
    changes = []
    new_entries = []
    for d, rel_path in PATCH_PAPERS.items():
        if d in EMPTY_TITLE_DOIS:
            continue
        if d in existing:
            continue
        idx = load_paper_index(rel_path)
        if not idx:
            print(f"  WARN: no index.json at {rel_path}, skipping")
            continue
        entry = {
            "id": idx.get("id") or rel_path.split("/")[-1],
            "path": rel_path,
            "type": idx.get("paper_type", "paper") or "paper",
            "doi": f"10.6084/m9.figshare.{d}",
        }
        new_entries.append(entry)
        changes.append(f"  add: {d:8s} type={entry['type']:25s} path={rel_path}")
    if new_entries:
        ei["papers"].extend(new_entries)
        old_v = str(ei.get("version", "1.0"))
        try:
            major, minor = old_v.split(".")
            ei["version"] = f"{major}.{int(minor) + 1}"
        except ValueError:
            pass
        ei["n_papers"] = len(ei["papers"])
        changes.append(f"  bump: version {old_v} -> {ei['version']}")
        changes.append(f"  bump: n_papers -> {ei['n_papers']}")
    return changes


def main(argv):
    dry_run = "--dry-run" in argv
    dm = load_json(DOI_MAP_PATH)
    ei = load_json(EFC_IDX_PATH)
    print(f"Before: doi-map={len(dm)} entries, efc_index.papers={len(ei.get('papers', []))}")
    print()
    print("Patching figshare/doi-map.json:")
    dm_changes = patch_doi_map(dm)
    for c in dm_changes:
        print(c)
    print()
    print("Patching docs/papers/efc/efc_index.json:")
    ei_changes = patch_efc_index(ei)
    for c in ei_changes:
        print(c)
    print()
    print(f"After: doi-map={len(dm)} entries, efc_index.papers={len(ei.get('papers', []))}")
    if not dm_changes and not ei_changes:
        print("\nNo changes - already up to date. Exit 0.")
        return 0
    if dry_run:
        print("\n[dry-run] not writing files. Re-run without --dry-run to apply.")
        return 0
    save_json(DOI_MAP_PATH, dm)
    save_json(EFC_IDX_PATH, ei)
    print("\nWrote both files. Run `python scripts/maintenance/efc_verify.py` to confirm.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
