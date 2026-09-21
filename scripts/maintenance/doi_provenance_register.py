#!/usr/bin/env python3
"""doi_provenance_register.py — canonical DOI provenance chain (side register).

Implements the F8 recommendation as a SIDE REGISTER: multi-DOI provenance
without migrating ``schema/regime_node.schema.json`` ``ontology.source`` from a
single string to an array. Additive; does not touch the 126-node bank, any
schema, or any published paper package.

Produces two additive, machine-readable files under
``docs/validation-ledger/data/``:

  1. ``doi_provenance_chain.json`` — DOI-to-DOI citation edges with a closed
     vocabulary. Every ``source_verified`` edge is machine-confirmed at build
     time: the source package's ``citations.bib`` (or code header, for the one
     COMPANION_TO edge) is actually read, and the target DOI's 8-digit id must
     be present. An unconfirmable edge ABORTS the build instead of degrading.
  2. ``doi_metadata_correction_proposals.json`` — metadata-only corrections with
     an explicit lifecycle. Each ``current`` value is read live from the
     package's ``index.json`` by JSON pointer at build time, so a drifted file
     changes the register instead of silently going stale, and ``status`` is
     COMPUTED by comparing that live value with the entry's ``expected_value``
     (``applied`` / ``proposed``). Every entry touches a published DOI package
     and therefore carries ``requires_author_word``; ``author_word_ref`` names
     the human instruction that licensed an edit. Tests own the gate: a licensed
     entry that is not applied is drift after the edit, and an unlicensed entry
     that IS applied is an edit without word. PDF and code are never a target.

Scope honesty:
  * A ``CITES`` edge records CITATION provenance, not empirical truth. "A cites
    B" is a provenance fact; it does not confirm either package's physics, and
    it does not prove A builds on B. Building-on is a stronger claim left to a
    human/reviewed pass.
  * ``OPEN_MAPPING`` marks a hypothesis not grounded in any citation and must
    never be reported as verified.
  * This register covers the VERIFIED CORE CHAIN only (~20 edges). The
    empirical test layer and the full 165-DOI graph are a separate pass.

Reproducibility: output is a pure function of the curated edges in this
generator's source, the canonical inventory, AND the source files it reads
(citations.bib, code header, index.json). ``input_digest`` hashes all of those;
no git-HEAD dependence is embedded.

Usage:
    python3 scripts/maintenance/doi_provenance_register.py

Exit: 0 on success, 1 on a measurement that could not be made, 2 on a curated
edge or correction that could not be confirmed against its source package.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOI_MAP = ROOT / "figshare" / "doi-map.json"
PAPERS = ROOT / "docs" / "papers" / "efc"
OUT = ROOT / "docs" / "validation-ledger" / "data"

DOI_8 = re.compile(r"(\d{8})$")

RELATION_VOCAB = (
    "CITES",            # machine-verified citation; does NOT assert "builds on"
    "COMPANION_TO",     # machine-verified code-header companion claim
    "OPEN_MAPPING",     # hypothesis, not grounded in any citation
)

# Reserved for a future reviewed pass; NOT emitted by this generator. They are
# declared here so a consumer that sees the closed vocabulary does not mistake
# their absence for an omission.
RESERVED_RELATIONS = (
    "DERIVES",
    "TESTS",
    "FALSIFIES",
    "CONSTRAINS",
    "SUPERSEDES",
)

STATUS_VOCAB = ("source_verified", "open_mapping")

# Correction lifecycle: ``proposed`` = the package does NOT carry the value yet
# (nothing has been edited); ``applied`` = the package DOES carry exactly the
# proposed value. The status is computed by build(), never hand-written, and
# ``author_word_ref`` says which human instruction licensed an edit. The gate
# is one-sided on purpose: an entry with a word MUST be applied (a re-drift of
# index.json flips it back to ``proposed`` and fails the test), and an entry
# WITHOUT a word must NOT be applied (an unlicensed edit of a published
# package fails the same way).
CORRECTION_STATUS_VOCAB = ("proposed", "applied")

# The author instruction this pass was carried out under (card t_3a2d983f,
# 2026-09-19): correct the machine-package metadata so the exact form reads as
# derived and the ansatz as phenomenological, fix the sqrt transcription, and
# keep the DOI rule (builds on, does not break). The published PDF is out of
# scope; only the machine package is corrected.
AUTHOR_WORD_CARD = "kanban card t_3a2d983f (2026-09-19): correct the machine package metadata"

# Exact target values for the 31942821 metadata corrections. These are the
# ONLY strings the register accepts as "applied"; they are compared with the
# value read live from index.json by JSON pointer.
DESC_CORRECTED = (
    "Derives the entropy production function \u0393(\u03c1) from first principles using "
    "Bose\u2013Einstein occupation statistics of grid modes and the von Neumann entropy "
    "functional. The derivation yields the Scenario B form \u0393(\u03c1) \u221d "
    "\u03c1^(3/2)/(\u03c1 + \u03c1crit), with \u03c1crit emerging from the grid-mode energy "
    "scale a0; it is sub-linear at low density (exponent 3/2, not 1) and non-saturating "
    "at high density (grows as \u03c1^(1/2)). The saturating form \u0393(\u03c1) = \u03930 "
    "\u00b7 \u03c1/(\u03c1 + \u03c1crit) is a phenomenological approximation to the derived "
    "result, valid to about 20% over the cosmologically relevant density range; it is not "
    "the derived output of the microphysics (\u00a75\u20136 of the paper). The work also "
    "clarifies that \u0393(\u03c1) and the gravitational response \u03bcBE(g) are distinct "
    "dynamical and static quantities, resolving potential double-counting."
)
MAIN_FINDING_CORRECTED = (
    "From BE occupation plus von Neumann entropy the derived form is Scenario B, "
    "\u0393(\u03c1) \u221d \u03c1^(3/2)/(\u03c1+\u03c1crit), with \u03c1crit emerging from "
    "the a0 grid-mode scale; the saturating \u03c1/(\u03c1+\u03c1crit) is a "
    "phenomenological approximation to it (~20% accuracy), not the derived result. \u0393 "
    "is shown to be distinct from \u03bcBE(g), resolving double-counting."
)
BE_OCCUPATION_LATEX = (
    "n(g) = \\mu_{\\mathrm{BE}}(g) = \\frac{1}{\\exp\\left(\\sqrt{g/a_0}\\right) - 1}"
)
X_OF_RHO_LATEX = (
    "x(\\rho) = \\sqrt{\\frac{g}{a_0}} = \\sqrt{\\frac{\\beta\\rho}{a_0}}"
)
ENTROPY_MARGINAL_LATEX = "\\frac{ds}{dn} = x = \\sqrt{\\frac{g}{a_0}}"
GAMMA_RESULT_LATEX = (
    "\\Gamma(\\rho) \\propto \\frac{\\rho^{3/2}}{\\rho + \\rho_{\\mathrm{crit}}}"
)
GAMMA_PHENOMENOLOGICAL_LATEX = (
    "\\Gamma(\\rho) \\simeq \\Gamma_0 \\, \\frac{\\rho}{\\rho + \\rho_{\\mathrm{crit}}}"
)
KC5_CORRECTED = (
    "KC5: Observational constraints decisively rule out \u03bcBE(g) = "
    "1/(e^{\u221a(g/a_0)}\u22121) as the grid-mode response, thereby invalidating the "
    "shared statistical basis used to derive \u0393(\u03c1)."
)


def _doi8(doi: str) -> str:
    m = DOI_8.search(doi)
    return m.group(1) if m else doi


def _doi_map() -> dict[str, dict]:
    dmap = json.loads(DOI_MAP.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for p in dmap.get("papers", []):
        doi = p.get("doi")
        if doi and doi not in out:
            out[doi] = p
    return out


def _repo_dir(p: dict) -> str:
    return p.get("repo_dir", "").replace("docs/papers/efc/", "")


# ---------------------------------------------------------------------------
# Curated edges. Each citation edge: (from_doi, to_doi, claim, source_file).
# ``source_file`` is relative to the SOURCE package dir. All were read on
# 2026-09-20 against origin/main @ b6547a27.
# ---------------------------------------------------------------------------
def _relations() -> list[dict]:
    return [
        # Density of States (31942800)
        _edge("10.6084/m9.figshare.31942800", "10.6084/m9.figshare.31878760",
              "grid microphysics cited", "citations.bib"),
        _edge("10.6084/m9.figshare.31942800", "10.6084/m9.figshare.31941465",
              "gradient-coupled grid action cited", "citations.bib"),
        _edge("10.6084/m9.figshare.31942800", "10.6084/m9.figshare.31876324",
              "relativistic action cited", "citations.bib"),
        _edge("10.6084/m9.figshare.31942800", "10.6084/m9.figshare.31941543",
              "regime-transition test cited", "citations.bib"),
        # Entropy Production (31942821)
        _edge("10.6084/m9.figshare.31942821", "10.6084/m9.figshare.31878760",
              "grid microphysics cited", "citations.bib"),
        _edge("10.6084/m9.figshare.31942821", "10.6084/m9.figshare.31941465",
              "gradient-coupled grid action cited", "citations.bib"),
        _edge("10.6084/m9.figshare.31942821", "10.6084/m9.figshare.31876324",
              "relativistic action cited", "citations.bib"),
        {
            "id": "rel-31942821-31942800",
            "from_doi": "10.6084/m9.figshare.31942821",
            "to_doi": "10.6084/m9.figshare.31942800",
            "to_label": None,
            "relation": "COMPANION_TO",
            "claim": "code header names Density of States as Scenario B+ upgrade",
            "status": "source_verified",
            "evidence_kind": "code_header",
            "required_marker": "Companion",
            "source_file": "src/entropy_production.py",
            "evidence_text": None,
        },
        # Relativistic Action (31876324)
        _edge("10.6084/m9.figshare.31876324", "10.6084/m9.figshare.31348411",
              "discrete entropic gravity cited", "citations.bib"),
        _edge("10.6084/m9.figshare.31876324", "10.6084/m9.figshare.31368433",
              "systematic localisation (survival-valley source) cited", "citations.bib"),
        _edge("10.6084/m9.figshare.31876324", "10.6084/m9.figshare.31333414",
              "sign-structure no-go note cited", "citations.bib"),
        # LCDM as special case (31943361)
        _edge("10.6084/m9.figshare.31943361", "10.6084/m9.figshare.31876324",
              "relativistic action cited", "citations.bib"),
        _edge("10.6084/m9.figshare.31943361", "10.6084/m9.figshare.31942800",
              "density of states cited", "citations.bib"),
        _edge("10.6084/m9.figshare.31943361", "10.6084/m9.figshare.31942821",
              "entropy production cited", "citations.bib"),
        _edge("10.6084/m9.figshare.31943361", "10.6084/m9.figshare.31941543",
              "regime-transition test cited", "citations.bib"),
        _edge("10.6084/m9.figshare.31943361", "10.6084/m9.figshare.31878760",
              "grid microphysics cited", "citations.bib"),
        _edge("10.6084/m9.figshare.31943361", "10.6084/m9.figshare.31941465",
              "gradient-coupled grid action cited", "citations.bib"),
        # Open mappings (hypotheses, NOT grounded in a citation)
        {
            "id": "rel-open-eta",
            "from_doi": "10.6084/m9.figshare.31876324",
            "to_doi": None,
            "to_label": "motor-lag concept (yarn/net two-velocity slip)",
            "relation": "OPEN_MAPPING",
            "claim": "eta_grav (Phi/Psi) == the two-velocity motor lag is an undeclared hypothesis (F5)",
            "status": "open_mapping",
            "evidence_kind": None,
            "source_file": None,
            "evidence_text": None,
        },
        {
            "id": "rel-open-a0",
            "from_doi": "10.6084/m9.figshare.31348411",
            "to_doi": None,
            "to_label": "MOND a0 = 1.2e-10 (observational scale)",
            "relation": "OPEN_MAPPING",
            "claim": "a0_eff = C^2 a0 ~ 5.4 a0 derived, but observational agreement with MOND scale is unreconciled (F4)",
            "status": "open_mapping",
            "evidence_kind": None,
            "source_file": None,
            "evidence_text": None,
        },
    ]


def _edge(frm: str, to: str, claim: str, src_file: str) -> dict:
    return {
        "id": f"rel-{_doi8(frm)}-{_doi8(to)}",
        "from_doi": frm,
        "to_doi": to,
        "to_label": None,
        "relation": "CITES",
        "claim": claim,
        "status": "source_verified",
        "evidence_kind": "citation",
        "source_file": src_file,
        "evidence_text": None,
    }


# ---------------------------------------------------------------------------
# Corrections. Each has a json_pointer into 31942821/index.json; build() reads
# the CURRENT value live so the register cannot silently drift, and COMPUTES
# the status by comparing that live value with ``expected_value``: "applied"
# when they are equal, "proposed" when they are not. ``proposed`` and
# ``problem`` are human text; ``current``, ``status`` and ``verified_against_file``
# are machine-populated. An entry with an ``author_word_ref`` must be applied;
# an entry without one must not be (see CORRECTION_STATUS_VOCAB above).
# ---------------------------------------------------------------------------
def _corrections() -> list[dict]:
    return [
        {
            "id": "corr-F1-description",
            "finding_id": "F1",
            "doi": "10.6084/m9.figshare.31942821",
            "file": "index.json",
            "json_pointer": "/description",
            "problem": (
                "presents the saturating ansatz rho/(rho+rho_crit) as the derived result; "
                "the derived form is Scenario B rho^(3/2)/(rho+rho_crit)"
            ),
            "proposed": (
                "State the derived form as Scenario B Gamma(rho) ~ rho^(3/2)/(rho+rho_crit) and "
                "label rho/(rho+rho_crit) as a phenomenological approximation (~20% deviation)."
            ),
            "normative_basis": [
                "PDF Section 5-6 (Scenario B rho^(3/2) is the derived form)",
                "src/entropy_production.py gamma_total vs gamma_phenomenological",
                "index.json key_result (Scenario B)",
            ],
            "mirrors": [
                "metadata.json:/abstract (same sentence)",
                "README.md:/Overview (same sentence)",
            ],
            "requires_author_word": True,
            "expected_value": DESC_CORRECTED,
            "author_word_ref": AUTHOR_WORD_CARD,
        },
        {
            "id": "corr-F1-mainfinding",
            "finding_id": "F1",
            "doi": "10.6084/m9.figshare.31942821",
            "file": "index.json",
            "json_pointer": "/key_results/main_finding",
            "problem": (
                "presents the saturating ansatz rho/(rho+rho_crit) as the derived result; "
                "the derived form is Scenario B rho^(3/2)/(rho+rho_crit)"
            ),
            "proposed": (
                "Derived form is Scenario B rho^(3/2)/(rho+rho_crit); "
                "rho/(rho+rho_crit) is the phenomenological approximation."
            ),
            "normative_basis": [
                "PDF Section 5-6",
                "src/entropy_production.py",
                "index.json key_result",
            ],
            "requires_author_word": True,
            "expected_value": MAIN_FINDING_CORRECTED,
            "author_word_ref": AUTHOR_WORD_CARD,
        },
        {
            "id": "corr-F1-xofrho",
            "finding_id": "F1",
            "doi": "10.6084/m9.figshare.31942821",
            "file": "index.json",
            "json_pointer": "/core_equations/x_of_rho/latex",
            "problem": "middle term g/a0 omits the sqrt; x = sqrt(g/a0) is the code's form",
            "proposed": "x(rho) = sqrt(g/a0) = sqrt(beta*rho/a0)",
            "normative_basis": [
                "src/entropy_production.py x_from_rho: x = sqrt(beta*rho/a0)",
                "g = beta*rho implies x = sqrt(g/a0), not g/a0",
                "PDF Eq. 4 and Eq. 11: x = sqrt(g/a0)",
            ],
            "requires_author_word": True,
            "expected_value": X_OF_RHO_LATEX,
            "author_word_ref": AUTHOR_WORD_CARD,
        },
        {
            "id": "corr-F1-beoccupation",
            "finding_id": "F1",
            "doi": "10.6084/m9.figshare.31942821",
            "file": "index.json",
            "json_pointer": "/core_equations/be_occupation/latex",
            "problem": "exponent g/a0 omits the sqrt; BE occupation uses sqrt(g/a0) in the code",
            "proposed": "n(g) = mu_BE(g) = 1/(exp(sqrt(g/a0)) - 1)",
            "normative_basis": [
                "src/entropy_production.py BEOccupation header: n(g) = 1/(exp(sqrt(g/a0)) - 1)",
                "occupation(x) = 1/(e^x - 1) with x = sqrt(beta*rho/a0)",
                "PDF Eq. 1: n(g) = mu_BE(g) = 1/(exp(sqrt(g/a0)) - 1)",
            ],
            "requires_author_word": True,
            "expected_value": BE_OCCUPATION_LATEX,
            "author_word_ref": AUTHOR_WORD_CARD,
        },
        {
            "id": "corr-F1-entropymarginal",
            "finding_id": "F1",
            "doi": "10.6084/m9.figshare.31942821",
            "file": "index.json",
            "json_pointer": "/core_equations/entropy_marginal/latex",
            "problem": (
                "third instance of the same sqrt transcription: the middle term is written "
                "g/a0, but ds/dn = x = sqrt(g/a0) (PDF Eq. 11; the code returns x)"
            ),
            "proposed": "ds/dn = x = sqrt(g/a0)",
            "normative_basis": [
                "PDF Eq. 11: ds/dn = ln(e^x) = x = sqrt(g/a0)",
                "src/entropy_production.py von_neumann_entropy.ds_dn_for_BE returns x",
            ],
            "scope_note": (
                "Not named individually in the card, which names the sqrt transcription for "
                "be_occupation; this is the same defect class in the same file and was "
                "corrected in the same pass. Revert alone if the author wants it out."
            ),
            "requires_author_word": True,
            "expected_value": ENTROPY_MARGINAL_LATEX,
            "author_word_ref": AUTHOR_WORD_CARD,
        },
        {
            "id": "corr-F1-gammaresult",
            "finding_id": "F1",
            "doi": "10.6084/m9.figshare.31942821",
            "file": "index.json",
            "json_pointer": "/core_equations/gamma_result/latex",
            "problem": (
                "the derived-result slot carried the saturating ansatz "
                "Gamma_0*rho/(rho+rho_crit) as if it were derived"
            ),
            "proposed": (
                "Derived (Scenario B) form Gamma(rho) ~ rho^(3/2)/(rho+rho_crit), matching "
                "PDF Eq. 37-38, key_result and src gamma_total"
            ),
            "normative_basis": [
                "PDF Eq. 37-38 (derived form is rho^(3/2)/(rho+rho_crit))",
                "src/entropy_production.py GammaDerivation.gamma_total",
                "index.json key_result",
            ],
            "requires_author_word": True,
            "expected_value": GAMMA_RESULT_LATEX,
            "author_word_ref": AUTHOR_WORD_CARD,
        },
        {
            "id": "corr-F1-gammaphenomenological",
            "finding_id": "F1",
            "doi": "10.6084/m9.figshare.31942821",
            "file": "index.json",
            "json_pointer": "/core_equations/gamma_phenomenological_approx/latex",
            "problem": (
                "the ansatz had no slot of its own, so it could only be read as the derived "
                "result; the paper calls it a phenomenological approximation (~20%)"
            ),
            "proposed": (
                "A separate gamma_phenomenological_approx entry holding the saturating "
                "ansatz, so 'derived' and 'phenomenological' cannot be confused again"
            ),
            "normative_basis": [
                "PDF Section 4.5 Eq. 35 and Section 5.3 (~20% approximation)",
                "src/entropy_production.py GammaDerivation.gamma_phenomenological",
            ],
            "requires_author_word": True,
            "expected_value": GAMMA_PHENOMENOLOGICAL_LATEX,
            "author_word_ref": AUTHOR_WORD_CARD,
        },
        {
            "id": "corr-F1-kc5",
            "finding_id": "F1",
            "doi": "10.6084/m9.figshare.31942821",
            "file": "index.json",
            "json_pointer": "/kill_criteria/4",
            "problem": (
                "KC5 restates the BE response with the exponent g/a0 instead of "
                "sqrt(g/a0) — the same transcription error as be_occupation, in prose"
            ),
            "proposed": "KC5 uses mu_BE(g) = 1/(e^{sqrt(g/a0)} - 1)",
            "normative_basis": [
                "PDF Eq. 1",
                "src/entropy_production.py BEOccupation",
            ],
            "scope_note": (
                "Transcription only; KC5's kill substance (mu_BE ruled out) is untouched. "
                "Not named individually in the card — same defect class, same pass."
            ),
            "requires_author_word": True,
            "expected_value": KC5_CORRECTED,
            "author_word_ref": AUTHOR_WORD_CARD,
        },
    ]


def _resolve_pointer(doc: dict, pointer: str):
    parts = [p for p in pointer.split("/") if p]
    cur = doc
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        elif isinstance(cur, list) and p.isdigit() and int(p) < len(cur):
            cur = cur[int(p)]
        else:
            raise SystemExit(f"json_pointer {pointer} not found in 31942821/index.json")
    return cur


def _verify_relation(rel: dict, dmap: dict[str, dict],
                     verified_files: dict[str, bytes]) -> None:
    """Confirm a citation/code-header edge; abort on failure."""
    src = dmap.get(rel["from_doi"])
    if not src:
        raise SystemExit(f"source DOI not in doi-map: {rel['from_doi']}")
    repo = _repo_dir(src)
    path = PAPERS / repo / rel["source_file"]
    if not path.is_file():
        raise SystemExit(f"source file missing for {rel['id']}: {path}")
    text = path.read_text(encoding="utf-8", errors="ignore")
    target_id = _doi8(rel["to_doi"])
    if target_id not in text:
        raise SystemExit(
            f"target DOI {rel['to_doi']} ({target_id}) NOT found in {path} — "
            f"curated edge {rel['id']} is unconfirmed"
        )
    marker = rel.get("required_marker")
    if marker and marker not in text:
        raise SystemExit(
            f"semantic marker {marker!r} NOT found in {path} — "
            f"curated edge {rel['id']} is unconfirmed"
        )
    for line in text.splitlines():
        if target_id in line:
            rel["evidence_text"] = line.strip()[:200]
            break
    rel["source_file"] = str(path.relative_to(ROOT))
    verified_files[rel["source_file"]] = path.read_bytes()


def build() -> tuple[dict, dict]:
    dmap = _doi_map()
    relations = _relations()

    verified_files: dict[str, bytes] = {}
    for rel in relations:
        if rel["status"] == "source_verified":
            _verify_relation(rel, dmap, verified_files)

    # Corrections: read current values live from 31942821/index.json.
    idx_path = PAPERS / "Derivation_of_the_Entropy_Production" / "index.json"
    if not idx_path.is_file():
        raise SystemExit(f"31942821 index.json missing: {idx_path}")
    idx_doc = json.loads(idx_path.read_text(encoding="utf-8"))
    corrections = _corrections()
    for c in corrections:
        c["current"] = _resolve_pointer(idx_doc, c["json_pointer"])
        c["verified_against_file"] = True
        # ``status`` is COMPUTED, never hand-written: "applied" means the
        # package already carries exactly the proposed value. A licensed entry
        # that is not applied is drift AFTER the edit, and an unlicensed entry
        # that IS applied is an edit without author word; tests own that gate.
        c["status"] = ("applied" if c["current"] == c["expected_value"]
                       else "proposed")
    n_applied = sum(1 for c in corrections if c["status"] == "applied")
    verified_files["docs/papers/efc/Derivation_of_the_Entropy_Production/index.json"] = \
        idx_path.read_bytes()

    # input_digest: generator source + doi-map + every source file actually read.
    h = hashlib.sha256()
    h.update(Path(__file__).read_bytes())
    h.update(b"\x00")
    h.update(DOI_MAP.read_bytes())
    for rel in sorted(verified_files):
        h.update(b"\x00")
        h.update(rel.encode("utf-8"))
        h.update(b"\x00")
        h.update(verified_files[rel])
    input_digest = h.hexdigest()

    n_cit = sum(1 for r in relations if r["status"] == "source_verified")
    n_open = sum(1 for r in relations if r["status"] == "open_mapping")

    chain = {
        "name": "EFC DOI provenance chain (side register)",
        "schema": "efc-doi-provenance-chain/1",
        "input_digest": input_digest,
        "relation_vocabulary": list(RELATION_VOCAB),
        "reserved_relations": list(RESERVED_RELATIONS),
        "status_vocabulary": list(STATUS_VOCAB),
        "direction_note": (
            "from_doi -> to_doi means the source package (from_doi) cites the target "
            "(to_doi). Direction is citation direction, not time."
        ),
        "scope_note": (
            "Verified core chain only. source_verified means the target DOI's 8-digit id "
            "appears in the source package's citations.bib (or code header for COMPANION_TO). "
            "CITES records citation provenance, NOT that the source builds on the target, and "
            "NOT empirical truth. open_mapping marks an ungated hypothesis and must never be "
            "reported as verified. The empirical test layer and the full 165-DOI graph are a "
            "separate mapping pass."
        ),
        "counts": {
            "total": len(relations),
            "source_verified": n_cit,
            "open_mapping": n_open,
        },
        "relations": relations,
    }

    corrections_doc = {
        "name": "EFC DOI metadata correction proposals",
        "schema": "efc-doi-metadata-corrections/1",
        "input_digest": input_digest,
        "status_vocabulary": list(CORRECTION_STATUS_VOCAB),
        "counts": {
            "total": len(corrections),
            "applied": n_applied,
            "proposed": len(corrections) - n_applied,
        },
        "note": (
            "Each 'current' value is read live from 31942821/index.json by JSON pointer at "
            "build time, so a drifted file changes this register instead of silently going "
            "stale; 'status' is computed by comparing that live value with 'expected_value' "
            "(applied = the package carries exactly the corrected value, proposed = it does "
            "not). Every entry touches a published DOI package, so each one needs author "
            "word; 'author_word_ref' names the instruction that licensed an edit, and a "
            "licensed entry that is not applied is drift after the edit. PDF and code are "
            "normative and are never the target of these corrections."
        ),
        "corrections": corrections,
    }

    return chain, corrections_doc


def main() -> int:
    try:
        chain, corrections_doc = build()
    except (OSError, json.JSONDecodeError) as exc:
        print(f"could not read a source: {exc}", file=sys.stderr)
        return 1
    except SystemExit as exc:
        print(f"curated edge or correction could not be confirmed: {exc}", file=sys.stderr)
        return 2

    (OUT / "doi_provenance_chain.json").write_text(
        json.dumps(chain, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (OUT / "doi_metadata_correction_proposals.json").write_text(
        json.dumps(corrections_doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    c = chain["counts"]
    cc = corrections_doc["counts"]
    print(
        f"doi-provenance-register: {c['total']} relations "
        f"(source_verified {c['source_verified']}, open_mapping {c['open_mapping']}); "
        f"{cc['total']} metadata corrections "
        f"(applied {cc['applied']}, proposed {cc['proposed']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
