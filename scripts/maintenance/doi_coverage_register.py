#!/usr/bin/env python3
"""doi_coverage_register.py — canonical-DOI coverage and consistency registers.

Produces three additive, machine-readable registers under
``docs/validation-ledger/data/`` from the canonical inventory
(``figshare/doi-map.json``), the authoritative classification
(``docs/validation-ledger/data/evidence-register.json``) and the two atlas
surfaces (``schema/regime_nodes.jsonld``, ``docs/validation-ledger/data/atlas.json``):

  1. ``doi_coverage_matrix.json``   — one row per canonical DOI.
  2. ``doi_coverage_open_findings.json`` — curated findings, each with a status
     from a closed vocabulary and an explicit next step.
  3. ``doi_coverage_pending.json``  — atlas-scope DOIs missing from the atlas
     union, queued for semantic (human or reviewed-agent) node mapping.

Scope honesty: this is a BIBLIOGRAPHIC inventory plus curated findings and a
mapping backlog. It is NOT a scientific consistency audit of every package,
and it is NOT atlas ingestion. It only records which DOIs appear as literal
Figshare URLs in the two atlas surfaces; it does not assert anything about a
DOI that is absent from those surfaces beyond "not found as a literal URL".

Reproducibility: output is a pure function of the four source files plus this
generator's own source. The deterministic ``input_digest`` is the SHA-256 of
those five inputs, so identical inputs reproduce byte-identical output with no
git-HEAD dependence; provenance of when it was generated is carried by the
commit itself, never embedded in the artefact.

The failure rule: this generator writes only the three files named above.
It never edits the atlas node bank, never edits the schema, and never touches
generator-owned public HTML.

Usage:
    python3 scripts/maintenance/doi_coverage_register.py

Exit: 0 on success, 1 on a measurement that could not be made.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOI_MAP = ROOT / "figshare" / "doi-map.json"
EVIDENCE_REGISTER = ROOT / "docs" / "validation-ledger" / "data" / "evidence-register.json"
REGIME_NODES = ROOT / "schema" / "regime_nodes.jsonld"
PUBLIC_ATLAS = ROOT / "docs" / "validation-ledger" / "data" / "atlas.json"
OUT = ROOT / "docs" / "validation-ledger" / "data"

FIGSHARE_URL = re.compile(r"10\.6084/m9\.figshare\.\d{8}")
DOI_8 = re.compile(r"(\d{8})$")

# Closed status vocabulary for findings.
STATUS_VOCAB = ("open", "reviewed_no_conflict_found", "conditional")


def _load(path: Path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _doi8(doi: str | None) -> str | None:
    if not doi:
        return None
    m = DOI_8.search(str(doi))
    return m.group(1) if m else None


def _urls(text: str) -> set[str]:
    return set(FIGSHARE_URL.findall(text))


def _input_digest() -> str:
    h = hashlib.sha256()
    for p in (DOI_MAP, EVIDENCE_REGISTER, REGIME_NODES, PUBLIC_ATLAS):
        h.update(p.name.encode("utf-8"))
        h.update(b"\x00")
        h.update(p.read_bytes())
    # The curated findings live in this generator's source, so the generator
    # itself is part of the reproducibility contract (outputs are not solely
    # a function of the four data inputs).
    h.update(b"generator\x00")
    h.update(Path(__file__).read_bytes())
    return h.hexdigest()


def _classify(evidence: dict) -> dict[str, set[str]]:
    """Map 8-digit DOI -> set of categories, preserving ALL labels.

    Multi-label classification is legitimate: a DOI may be both empirical and
    methodological. Overlap is recorded as such, never as a contradiction.
    """
    out: dict[str, set[str]] = defaultdict(set)
    for list_cat, entries in (evidence.get("categories") or {}).items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            d8 = _doi8(entry.get("doi"))
            if not d8:
                continue
            # The entry-level label wins where present; otherwise the list key.
            cat = entry.get("category") or list_cat
            out[d8].add(cat)
    return out


def _findings() -> list[dict]:
    """Curated findings. Statuses are from the closed vocabulary.

    The DOI identifiers here were verified against figshare/doi-map.json on
    2026-09-19: 31348411 (Discrete Entropic Gravity), 31348417 (Regime
    Structure), 30642497 (variable-light-s0-s1), 31305421 (c_eff_parameterization).
    """
    return [
        {
            "id": "F1",
            "title": "31942821 metadata drift: ansatz presented as derived, plus two sqrt transcriptions (x_of_rho, be_occupation)",
            "location": "docs/papers/efc/Derivation_of_the_Entropy_Production/index.json (metadata only; PDF + code are unambiguous)",
            "claim": (
                "index.json description (line 5) and main_finding (line 55) present the "
                "phenomenological ansatz rho/(rho+rho_crit) as the 'derived' result, while key_result "
                "(line 108), the code (gamma_total = rho^1.5/(1+rho), gamma_phenomenological = "
                "rho/(1+rho)) and the PDF Section 5-6 all state the derived form is Scenario B "
                "rho^(3/2)/(rho+rho_crit) with the ansatz as an approximation (~20%). Separately there "
                "are TWO sqrt transcriptions: (a) x_of_rho (line 38) writes 'x = g/a0 = sqrt(beta*rho/a0)' "
                "but the middle term should be sqrt(g/a0) (with g = beta*rho, x = sqrt(g/a0) = "
                "sqrt(beta*rho/a0)), matching the code's x_from_rho; (b) be_occupation (line 30) writes "
                "'n(g) = 1/(exp(g/a0) - 1)' but the exponent should be sqrt(g/a0), matching the code "
                "header's 'n(g) = 1/(exp(sqrt(g/a0)) - 1)'. All three are index.json-metadata-only "
                "deviations from the normative PDF + code; the provenance/corrections register "
                "(doi_metadata_correction_proposals.json) expands F1 into four per-field proposals."
            ),
            "status": "open",
            "next": (
                "Metadata-only reconciliation: in index.json, label rho/(rho+rho_crit) as the "
                "phenomenological approximation and point description/main_finding at the Scenario B "
                "rho^(3/2) key_result; correct the x_of_rho middle term to sqrt(g/a0) and the "
                "be_occupation exponent to sqrt(g/a0). PDF and code are normative and stay untouched."
            ),
        },
        {
            "id": "F2",
            "title": "31876324 default code does not reach the survival valley (pedagogical, not a defect)",
            "location": "docs/papers/efc/EFC_Relativistic_Action_Field_Equations_Perturbation_Theory_and_Extraction/src/efc_relativistic.py",
            "claim": (
                "Default parameters give epsilon ~ 1e-12..1e-18, hence mu=Sigma=0.9995 and "
                "eta=1.000000 everywhere; the survival valley (mu in [0.93,0.96], eta ~ 1.1, "
                "Sigma in [1.03,1.07]) is not reached. The module is declared 'pedagogical "
                "implementation, not production-ready'. eta=1.000000 is six-decimal rounding, "
                "NOT evidence of zero slip."
            ),
            "status": "reviewed_no_conflict_found",
            "next": (
                "Not a defect. Document that reaching the valley requires targeted parameters, "
                "not defaults; report eta-1 analytically where slip is claimed."
            ),
        },
        {
            "id": "F3",
            "title": "epsilon ~ k^-2 holds only in the quasi-static regime",
            "location": "31876324 Eq. 24-26 (compute_epsilon_*)",
            "claim": (
                "The epsilon terms scale as 1/k^2 (measured ratio 10000.00 under k/10). This is a "
                "quasi-static sub-horizon result and cannot be extrapolated to horizon/CMB scales. "
                "Any earlier statement that the slip grows toward large scales contradicts "
                "the motor intuition is an over-interpretation of that regime restriction."
            ),
            "status": "reviewed_no_conflict_found",
            "next": (
                "Formulate eta(k,z) only inside the quasi-static validity domain; no horizon "
                "extrapolation without a full ADM/Boltzmann treatment."
            ),
        },
        {
            "id": "F4",
            "title": "a0 = 6.5e-10 appears in no index.json; a0_eff = C^2 a0 ~ 5.4 a0 is derived in two DOIs",
            "location": "figshare/doi-map.json + schema/framework_atlas.jsonld + EFC-VAL-2026-006/atlas_seed.json",
            "claim": (
                "The value 6.5e-10 m/s^2 appears only in a framework_atlas.jsonld note, the "
                "EFC-VAL-2026-006 atlas seed and a test comment — not in any paper index.json. "
                "The papers carry 1.2e-10 (MOND). Two DOIs (31348411 Discrete Entropic Gravity, "
                "31348417 Regime Structure) derive a0_eff = C^2 a0 ~ 5.4 a0 (C ~ 2.32). The "
                "'5x divergence' is therefore simultaneously a derived relation and an "
                "unreconciled flag; the derivation explains the relationship between the two "
                "scales but does not by itself establish observational agreement with MOND."
            ),
            "status": "open",
            "next": (
                "Reconcile whether 6.5e-10 is intended as a0_eff = C^2 a0, and whether the "
                "atlas 'divergence' flag is a residual or an open contradiction. Human decision."
            ),
        },
        {
            "id": "F5",
            "title": "eta_grav (Phi/Psi) vs the motor 'lag' is a mapping hypothesis, not an identity",
            "location": "31876324 observables.eta + session 2026-09-19",
            "claim": (
                "Gravitational slip eta = Phi/Psi is a measurable modified-gravity parameter. "
                "That it equals the two-velocity 'lag' of the garn/flow picture is an undeclared "
                "hypothesis (an 'A -> C without B' gap), not an established identity."
            ),
            "status": "open",
            "next": (
                "Separate proof obligation: define the lag operationally before it can be tested "
                "against eta_grav."
            ),
        },
        {
            "id": "F6",
            "title": "'variable c' vs c_T=c: only propagation-speed equality is locked",
            "location": "31876324 tensor_sector (c_T=c, FA3 PASSED) + 30642497 + 31305421",
            "claim": (
                "c_T=c establishes that gravitational waves and light share the model's "
                "propagation speed under its conventions; it does not by itself lock absolute "
                "light speed or a time-invariant effective speed. A 'variable effective speed' "
                "over the grid is a distinct quantity and requires separate analysis; it only "
                "contradicts c_T=c if it is claimed to be the signal speed."
            ),
            "status": "open",
            "next": (
                "Separate 'c' (signal speed, locked to c) from a flow speed over the grid "
                "(undefined). No conflation."
            ),
        },
        {
            "id": "F7",
            "title": "Survival valley is overdetermined: Sigma = mu(1+eta)/2 is an exact identity",
            "location": "31876324 observables.sigma + survival_valley (source: 31368433 fit, not a derivation)",
            "claim": (
                "Sigma = mu(1+eta)/2 is an EXACT identity in the linear parameterisation, "
                "not a fit relation: once mu and eta are chosen, Sigma is already fixed. "
                "The survival valley therefore states three boxes (mu in [0.93,0.96], eta ~ 1.10, "
                "Sigma in [1.03,1.07]) where only two are free. With mu in [0.93,0.96] and "
                "eta=1.10, the identity gives Sigma in [0.9765,1.008], which does NOT overlap the "
                "declared [1.03,1.07]; forcing Sigma >= 1.03 at mu <= 0.96 requires eta >= 1.1458. "
                "survival_valley.source points to 31368433 (systematic localisation), so the valley "
                "is a fit artefact, not a derivation — the three numbers were never checked against "
                "the identity."
            ),
            "status": "conditional",
            "next": (
                "Two reconciliation options, both require Morten's word (touches published DOI "
                "content): (1) reduce the valley to (mu, eta) and derive Sigma from the identity "
                "(cleanest); or (2) admit the fit treated Sigma independently and report the tension "
                "against the identity as its own finding. Do NOT silently change eta to 1.146 to "
                "force agreement."
            ),
        },
        {
            "id": "F8",
            "title": "ontology.source is a single string; multi-source provenance needs a decision, not a proof of absence",
            "location": "schema/regime_node.schema.json (ontology.source: type string)",
            "claim": (
                "The regime-node schema stores ontology.source as a single string. This does not "
                "prove that no multi-source provenance mechanism exists elsewhere (relations, "
                "references, provenance registers). It does mean that, if this register becomes "
                "the canonical DOI-chain source, a decision is needed: extend the field to an "
                "array, or keep a single source and record the chain in a side register."
            ),
            "status": "open",
            "next": (
                "Design decision (human word): array, or side register? This PR ships the "
                "register, not a schema change."
            ),
        },
        {
            "id": "F9",
            "title": "Gamma(rho) form split (bifurcation) and BE exponent split; KC1 is an unexecuted conjecture",
            "location": (
                "31942821 + 31942800 + 31941465 + 31878760 + 31878334 + 31941543; "
                "docs/validation-ledger/reviews/deleg_65a996ff/; "
                "docs/validation-ledger/data/form_status_register.json"
            ),
            "claim": (
                "Three Gamma(rho) forms are published for one intended target: "
                "A = rho/(rho+rho_crit), B = rho^(3/2)/(rho+rho_crit), "
                "C/B+ = sqrt(rho/rho_crit)/(1+sqrt(rho/rho_crit)). A and C share a saturating "
                "rational shape (argument r vs sqrt(r)); B alone is a non-saturating power "
                "(grows as sqrt(rho) at high density; the source's own requirement row R2 records "
                "'not saturation'). This is a shape BIFURCATION, not a trifurcation. A separate "
                "two-way split exists in the Bose-Einstein exponent: exp(g/a0) (linear) vs "
                "exp(sqrt(g/a0)) (sqrt, derived in 31878334/31878760/31941465). KC1 in 31941465 "
                "claims >=5sigma exclusion of the sqrt form, but that package's own fields record "
                "delta_chi2=null, significance_sigma=null, 'no new fit performed' — an analytical "
                "conjecture, not an executed test. No physical falsification is established: this "
                "is a provenance/representation/version split plus an unexecuted empirical "
                "discrimination."
            ),
            "status": "open",
            "next": (
                "Author word required to: (1) fix B's final claim status (derived + internal "
                "non-saturation conflict vs superseded by B+); (2) confirm the KC1 downgrade to "
                "conjectured/not executed; (3) choose the discriminating test(s). See "
                "docs/validation-ledger/reviews/deleg_65a996ff/synthesis.md and "
                "docs/validation-ledger/data/form_status_register.json. Do NOT edit any published "
                "index.json without author word."
            ),
        },
    ]


def build() -> tuple[dict, dict, dict]:
    """Pure build: returns (matrix, findings_doc, backlog). No file writes."""
    dmap = _load(DOI_MAP)
    evidence = _load(EVIDENCE_REGISTER)
    regime = _load(REGIME_NODES)
    public_atlas = _load(PUBLIC_ATLAS)

    input_digest = _input_digest()

    # Canonical inventory: one row per unique DOI, with every repo-dir alias.
    papers = dmap.get("papers", [])
    groups: dict[str, list[dict]] = defaultdict(list)
    for p in papers:
        doi = p.get("doi")
        if doi:
            groups[doi].append(p)
    no_doi_dirs = sorted({
        p.get("repo_dir", "").replace("docs/papers/efc/", "").split("/")[0]
        for p in papers if not p.get("doi")
    })
    duplicate_groups = {d: v for d, v in groups.items() if len(v) > 1}

    # Classification (all labels preserved).
    doi_cats = _classify(evidence)

    # Atlas union coverage: literal Figshare URLs only, from both surfaces.
    atlas_urls = _urls(json.dumps(regime, ensure_ascii=False))
    atlas_urls |= _urls(json.dumps(public_atlas, ensure_ascii=False))

    rows = []
    for doi in sorted(groups):
        plist = groups[doi]
        d8 = _doi8(doi)
        cats = sorted(doi_cats.get(d8 or "", set()))
        is_empirical = "empirical" in cats
        in_atlas = doi in atlas_urls
        n_dirs = len(plist)
        duplicate = n_dirs > 1
        # Class: atlas scope iff empirical. Duplicate is an ORTHOGONAL
        # inventory attribute, never a reason to drop a DOI from atlas scope.
        klass = "atlas_scope" if is_empirical else "changelog"
        if klass == "atlas_scope" and not in_atlas:
            disposition = "atlas_candidate"
        elif klass == "atlas_scope" and in_atlas:
            disposition = "atlas_covered"
        else:
            disposition = "changelog_only"
        rows.append({
            "doi": doi,
            "id8": d8,
            "title": (plist[0].get("title") or ""),
            "repo_dirs": sorted({
                p.get("repo_dir", "").replace("docs/papers/efc/", "") for p in plist
            }),
            "n_dirs": n_dirs,
            "duplicate_dir": duplicate,
            "categories": cats,
            "category_overlap": len(cats) > 1,
            "class": klass,
            "in_atlas_literal_url": in_atlas,
            "disposition": disposition,
        })

    n_emp = sum(1 for r in rows if "empirical" in r["categories"])
    n_meth = sum(1 for r in rows if "methodological" in r["categories"])
    n_struct = sum(1 for r in rows if "structural" in r["categories"])
    n_atlas_scope = sum(1 for r in rows if r["class"] == "atlas_scope")
    n_atlas_candidate = sum(1 for r in rows if r["disposition"] == "atlas_candidate")

    matrix = {
        "name": "EFC DOI coverage and consistency matrix",
        "schema": "efc-doi-coverage-matrix/1",
        "input_digest": input_digest,
        "sources": {
            "inventory": "figshare/doi-map.json",
            "classification": "docs/validation-ledger/data/evidence-register.json",
            "atlas_union": [
                "schema/regime_nodes.jsonld",
                "docs/validation-ledger/data/atlas.json",
            ],
        },
        "metric_note": (
            "in_atlas_literal_url measures only whether the DOI appears as a literal "
            "Figshare URL in the two atlas surfaces. Absence is not proof of absence of "
            "representation (bare numeric ids, references, or indirect links are not "
            "counted)."
        ),
        "measured": {
            "paper_entries": len(papers),
            "unique_dois": len(groups),
            "duplicate_doi_groups": len(duplicate_groups),
            "dirs_without_doi": len(no_doi_dirs),
            "atlas_union_literal_urls": len(atlas_urls),
            "empirical": n_emp,
            "methodological": n_meth,
            "structural": n_struct,
            "atlas_scope": n_atlas_scope,
            "atlas_candidate_missing_from_atlas": n_atlas_candidate,
        },
        "_note": (
            "Category counts are DOI-set counts: a DOI carrying N categories is counted in "
            "each, so empirical+methodological+structural may exceed unique_dois. That is "
            "multi-label overlap, recorded per row as category_overlap, not a contradiction. "
            "'empirical' is the evidence register's own label, not a physics verdict: the "
            "atlas-scope rule (empirical -> atlas candidate) is a triage heuristic, and "
            "atlas_candidate rows require semantic node mapping."
        ),
        "dirs_without_doi": no_doi_dirs,
        "duplicate_groups": {
            d: sorted({p.get("repo_dir", "").replace("docs/papers/efc/", "") for p in v})
            for d, v in sorted(duplicate_groups.items())
        },
        "rows": rows,
    }

    findings = _findings()

    pending = [
        {
            "doi": r["doi"],
            "id8": r["id8"],
            "title": r["title"],
            "categories": r["categories"],
            "repo_dirs": r["repo_dirs"],
            "reason_not_auto_mapped": (
                "Atlas enrichment is semantic: each DOI must be linked to the correct "
                "obs.* node or efc.* engine based on the observable it tests. That is not "
                "mechanically derivable without reading each paper's claims. In addition, "
                "ontology.source is single-string (see F8), so multi-DOI provenance needs "
                "a schema decision. Queued for semantic mapping, not auto-applied."
            ),
        }
        for r in rows
        if r["disposition"] == "atlas_candidate"
    ]

    backlog = {
        "name": "EFC DOI atlas-ingest backlog (atlas scope, missing from atlas)",
        "schema": "efc-doi-coverage-pending/1",
        "input_digest": input_digest,
        "count": len(pending),
        "disposition": "semantic_mapping",
        "note": (
            "Every atlas-scope (empirical) DOI that does not appear as a literal Figshare URL "
            "in the atlas union. Node mapping is semantic and is not auto-applied here. Each "
            "entry is pre-computed with DOI, title, categories and repo dirs so the mapping "
            "step only needs to approve a node link."
        ),
        "pending": pending,
    }

    findings_doc = {
        "name": "EFC DOI coverage and consistency — findings",
        "schema": "efc-doi-coverage-findings/1",
        "input_digest": input_digest,
        "status_vocabulary": list(STATUS_VOCAB),
        "counts": {
            "open": sum(1 for f in findings if f["status"] == "open"),
            "conditional": sum(1 for f in findings if f["status"] == "conditional"),
            "reviewed_no_conflict_found": sum(
                1 for f in findings if f["status"] == "reviewed_no_conflict_found"
            ),
        },
        "findings": findings,
    }

    return matrix, findings_doc, backlog


def main() -> int:
    try:
        matrix, findings_doc, backlog = build()
    except (OSError, json.JSONDecodeError) as exc:
        print(f"could not read a source: {exc}", file=sys.stderr)
        return 1

    (OUT / "doi_coverage_matrix.json").write_text(
        json.dumps(matrix, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (OUT / "doi_coverage_pending.json").write_text(
        json.dumps(backlog, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (OUT / "doi_coverage_open_findings.json").write_text(
        json.dumps(findings_doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    m = matrix["measured"]
    print(
        f"doi-coverage-register: {len(matrix['rows'])} unique DOIs, "
        f"{len(matrix['duplicate_groups'])} duplicate groups, "
        f"{m['dirs_without_doi']} dirs without DOI; atlas union "
        f"{m['atlas_union_literal_urls']} literal URLs; atlas_scope {m['atlas_scope']}, "
        f"missing-from-atlas {m['atlas_candidate_missing_from_atlas']}; "
        f"findings {len(findings_doc['findings'])} "
        f"(open {findings_doc['counts']['open']}, conditional "
        f"{findings_doc['counts']['conditional']}, no-conflict "
        f"{findings_doc['counts']['reviewed_no_conflict_found']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
