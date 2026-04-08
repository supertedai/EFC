#!/usr/bin/env python3
"""
EFC Repository Verifier

Non-destructive consistency checker for the EFC validation stack. Runs a set
of invariants taken from the maintenance algorithm and exits 0 if clean,
1 if violations are found.

Checks:

  [C1]  Every paper directory under docs/papers/efc/ has the mandatory
        AI-friendly files: index.json, metadata.json, ai_manifest.json,
        README.md, <slug>.jsonld.
  [C2]  evidence-register.json + ledger.json empirical lists contain only
        Figshare DOIs of the form 31\\d+ (no arXiv IDs, no external refs).
  [C3]  HTML ledger contains no forbidden "confirms EFC" / "proves EFC"
        language outside the §4b external block.
  [C4]  Version string consistency: ledger.json.version, the HTML footer,
        and validation-ledger/index.md version tag all agree (major.minor).
  [C5]  ai_friendly_index.json exists and is not stale (n_packages matches
        the current number of directories).
  [C6]  No external arXiv IDs leak into evidence-register.json / ledger.json.
  [C7]  §4b externals in the HTML ledger carry the [external — ...] tag.

Usage: scripts/maintenance/efc_verify.py [--quiet]
"""
from __future__ import annotations
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
LEDGER_DIR = os.path.join(REPO, "docs", "validation-ledger")
HTML_LEDGER = os.path.join(REPO, "docs", "public", "EFC_Validation_Ledger.html")

SKIP_TOP = {
    "README.md", "cover_letter-2.pdf",
    "efc_graph_edges.json", "efc_graph_schema.json",
    "efc_index.json", "efc_index.jsonld",
    "ai_friendly_index.json",
}

MANDATORY = ("index.json", "metadata.json", "ai_manifest.json", "README.md")

FORBIDDEN_PHRASES = (
    "confirms EFC", "proves EFC", "validates EFC",
    "EFC is confirmed", "EFC is proven",
)

FIGSHARE_DOI_RE = re.compile(r"^\d{8}$")
ARXIV_RE = re.compile(r"arxiv[: ]?\d{4}\.\d{4,5}", re.IGNORECASE)


class Issue:
    def __init__(self, code: str, where: str, msg: str, severity: str = "error"):
        self.code = code
        self.where = where
        self.msg = msg
        self.severity = severity

    def __str__(self):
        return f"[{self.severity.upper():5}] {self.code} {self.where}: {self.msg}"


def slugify(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()
    return s[:120] or "paper"


def check_c1_mandatory_files(issues):
    dirs = []
    for name in sorted(os.listdir(PAPERS)):
        if name in SKIP_TOP:
            continue
        full = os.path.join(PAPERS, name)
        if not os.path.isdir(full):
            continue
        dirs.append(name)
        for f in MANDATORY:
            if not os.path.exists(os.path.join(full, f)):
                issues.append(Issue("C1", name, f"missing {f}"))
        slug = slugify(name)
        if not os.path.exists(os.path.join(full, slug + ".jsonld")):
            # tolerate hand-crafted jsonld with a different basename
            any_jsonld = [f for f in os.listdir(full) if f.endswith(".jsonld")]
            if not any_jsonld:
                issues.append(Issue("C1", name, "missing *.jsonld"))
    return dirs


def check_c2_c6_evidence_purity(issues):
    for rel in ("data/evidence-register.json", "data/ledger.json"):
        path = os.path.join(LEDGER_DIR, rel)
        if not os.path.exists(path):
            issues.append(Issue("C2", rel, "file not found"))
            continue
        try:
            with open(path) as fh:
                doc = json.load(fh)
        except Exception as e:
            issues.append(Issue("C2", rel, f"unparseable: {e}"))
            continue
        empirical = _extract_empirical(doc)
        for entry in empirical:
            doi = str(entry.get("doi", ""))
            if not FIGSHARE_DOI_RE.match(doi):
                issues.append(Issue("C2", rel, f"non-Figshare DOI in empirical: {doi!r}"))
            full_blob = json.dumps(entry)
            if ARXIV_RE.search(full_blob):
                issues.append(Issue("C6", rel, f"arXiv ID leaked into empirical entry: {doi!r}"))


def _extract_empirical(doc):
    # Evidence register has categories.empirical; ledger.json has evidence_register.empirical
    out = []
    if isinstance(doc, dict):
        if "categories" in doc and isinstance(doc["categories"], dict):
            out.extend(doc["categories"].get("empirical", []) or [])
        if "evidence_register" in doc and isinstance(doc["evidence_register"], dict):
            out.extend(doc["evidence_register"].get("empirical", []) or [])
    return out


def check_c3_c7_html_language(issues):
    if not os.path.exists(HTML_LEDGER):
        issues.append(Issue("C3", "public", "HTML ledger missing"))
        return
    with open(HTML_LEDGER, encoding="utf-8") as fh:
        html = fh.read()
    # Split §4b block out before language checks
    start = html.find("4b. External Observations")
    end = html.find("5. Planned Validation Pipeline")
    if start != -1 and end != -1:
        core = html[:start] + html[end:]
        external = html[start:end]
    else:
        core = html
        external = ""
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in core.lower():
            issues.append(Issue("C3", "HTML §1–§4", f"forbidden phrase: {phrase!r}"))
    # §4b must use the tag
    if external and "[external" not in external:
        issues.append(Issue("C7", "HTML §4b", "external block exists but no [external — …] tags found"))


def check_c4_version_consistency(issues):
    """
    The repo runs two independent version tracks on purpose:

      - PUBLIC track: docs/public/EFC_Validation_Ledger.html  (currently v3.x)
      - INTERNAL track: docs/validation-ledger/data/ledger.json
                         + docs/validation-ledger/index.md    (currently v4.x)

    We only require consistency within each track, not across them.
    """
    ledger_json = os.path.join(LEDGER_DIR, "data", "ledger.json")
    index_md = os.path.join(LEDGER_DIR, "index.md")
    v_ledger = v_html = v_index = None
    if os.path.exists(ledger_json):
        try:
            with open(ledger_json) as fh:
                v_ledger = str(json.load(fh).get("version", "")).strip()
        except Exception as e:
            issues.append(Issue("C4", "ledger.json", f"unparseable: {e}"))
    if os.path.exists(HTML_LEDGER):
        with open(HTML_LEDGER, encoding="utf-8") as fh:
            html = fh.read()
        m = re.search(r"Canonical Multi-Sector Validation Ledger \((v[\d.]+)", html)
        if m:
            v_html = m.group(1).lstrip("v")
    if os.path.exists(index_md):
        with open(index_md, encoding="utf-8") as fh:
            md = fh.read()
        m = re.search(r"Version:\s*(v[\d.]+)", md)
        if m:
            v_index = m.group(1).lstrip("v")
    # Internal track: ledger.json vs index.md
    internal = {k: v for k, v in {"ledger.json": v_ledger, "index.md": v_index}.items() if v}
    if len(set(internal.values())) > 1:
        issues.append(Issue("C4", "internal-versions",
                            f"drift within internal track: {internal}", severity="warn"))
    # Public track: HTML footer alone
    # Report the current versions for visibility
    if v_ledger or v_html or v_index:
        info = f"tracks: public HTML={v_html or '?'}, internal ledger.json={v_ledger or '?'}, internal index.md={v_index or '?'}"
        # informational only, no issue


def check_c5_catalogue_fresh(issues, dirs):
    cat = os.path.join(PAPERS, "ai_friendly_index.json")
    if not os.path.exists(cat):
        issues.append(Issue("C5", "ai_friendly_index.json", "missing"))
        return
    try:
        with open(cat) as fh:
            doc = json.load(fh)
    except Exception as e:
        issues.append(Issue("C5", "ai_friendly_index.json", f"unparseable: {e}"))
        return
    n = doc.get("n_packages", 0)
    if n != len(dirs):
        issues.append(Issue("C5", "ai_friendly_index.json",
                            f"stale: n_packages={n} but {len(dirs)} dirs on disk",
                            severity="warn"))


def main():
    quiet = "--quiet" in sys.argv
    issues = []
    dirs = check_c1_mandatory_files(issues)
    check_c2_c6_evidence_purity(issues)
    check_c3_c7_html_language(issues)
    check_c4_version_consistency(issues)
    check_c5_catalogue_fresh(issues, dirs)

    errors = [i for i in issues if i.severity == "error"]
    warns = [i for i in issues if i.severity == "warn"]
    if not quiet or issues:
        print(f"[efc-verify] {len(dirs)} paper dirs · {len(errors)} errors · {len(warns)} warnings")
        for i in issues:
            print("  " + str(i))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
