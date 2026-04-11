#!/usr/bin/env python3
"""
efc_verify.py — [PHASE2_STAGED] Phase 2 C1–C8 verifier.

⚠️  STAGED. Drops Phase 1 epistemic checks (arXiv-leakage,
    forbidden-phrase guard, §4b tags). See
    scripts/maintenance/phase2/README.md.  ⚠️

Read-only (no file modifications), but semantically incompatible
with the Phase 1 data layout — it expects ledger.json at the Phase 2
path and a different schema than what the live repo uses.

Execution is blocked unless --i-know-this-is-staged is passed.
"""

from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ledger_schema import Status  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[3]


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


class VerifyResult:
    def __init__(self) -> None:
        self.checks: list[dict] = []

    def add(self, check_id: str, passed: bool, message: str) -> None:
        self.checks.append({"id": check_id, "passed": passed, "message": message})
        status = "✅" if passed else "❌"
        print(f"  {status} {check_id}: {message}")

    @property
    def all_passed(self) -> bool:
        return all(c["passed"] for c in self.checks)

    @property
    def failures(self) -> list[dict]:
        return [c for c in self.checks if not c["passed"]]


def check_c1_manifests(root: Path, result: VerifyResult) -> None:
    papers_dir = root / "docs" / "papers" / "efc"
    if not papers_dir.exists():
        result.add("C1", False, f"Papers directory not found: {papers_dir}")
        return
    missing = []
    for d in papers_dir.rglob("*"):
        if d.is_dir() and list(d.glob("*.pdf")):
            for required in ("metadata.json", "index.json"):
                if not (d / required).exists():
                    missing.append(f"{d.name}/{required}")
    if missing:
        result.add("C1", False, f"Missing manifests: {', '.join(missing[:10])}")
    else:
        result.add("C1", True, "All paper directories have required manifests")


def check_c2_ledger_dois_exist(root: Path, result: VerifyResult) -> None:
    ledger = load_json(root / "docs" / "validation-ledger" / "ledger.json")
    papers_dir = root / "docs" / "papers" / "efc"
    if not ledger:
        result.add("C2", False, "ledger.json not found")
        return
    ledger_dois: set = set()
    for entry in ledger.get("entries", []):
        ledger_dois.update(entry.get("evidence_dois", []))
    paper_dois: set = set()
    if papers_dir.exists():
        for meta_file in papers_dir.rglob("metadata.json"):
            meta = load_json(meta_file)
            fig_id = meta.get("figshare_id", "")
            if fig_id:
                paper_dois.add(fig_id)
    orphans = ledger_dois - paper_dois
    if orphans:
        result.add(
            "C2",
            False,
            f"{len(orphans)} DOIs in ledger without paper dirs: "
            f"{', '.join(sorted(orphans)[:5])}",
        )
    else:
        result.add("C2", True, f"All {len(ledger_dois)} ledger DOIs have paper directories")


def check_c3_no_orphan_papers(root: Path, result: VerifyResult) -> None:
    ledger = load_json(root / "docs" / "validation-ledger" / "ledger.json")
    papers_dir = root / "docs" / "papers" / "efc"
    all_ledger_dois: set = set()
    for entry in ledger.get("entries", []):
        all_ledger_dois.update(entry.get("evidence_dois", []))
    for cat in ("evidence_empirical", "evidence_structural", "evidence_methodological"):
        all_ledger_dois.update(ledger.get(cat, []))
    orphans = []
    if papers_dir.exists():
        for meta_file in papers_dir.rglob("metadata.json"):
            meta = load_json(meta_file)
            fig_id = meta.get("figshare_id", "")
            if fig_id and fig_id not in all_ledger_dois:
                orphans.append(fig_id)
    if orphans:
        result.add(
            "C3",
            False,
            f"{len(orphans)} papers not referenced in ledger: {', '.join(orphans[:5])}",
        )
    else:
        result.add("C3", True, "All papers referenced in ledger")


def check_c4_html_current(root: Path, result: VerifyResult) -> None:
    ledger_path = root / "docs" / "validation-ledger" / "ledger.json"
    html_path = root / "docs" / "public" / "EFC_Validation_Ledger.html"
    if not html_path.exists():
        result.add("C4", False, "HTML file not found")
        return
    if not ledger_path.exists():
        result.add("C4", False, "ledger.json not found")
        return
    ledger = load_json(ledger_path)
    version = ledger.get("version", "")
    html_text = html_path.read_text(encoding="utf-8")
    if version and f"Version {version}" not in html_text and f"v{version}" not in html_text:
        result.add("C4", False, f"HTML version mismatch: ledger says v{version}")
    else:
        result.add("C4", True, f"HTML matches ledger version {version}")


def check_c5_readme_counts(root: Path, result: VerifyResult) -> None:
    ledger = load_json(root / "docs" / "validation-ledger" / "ledger.json")
    readme_path = root / "README.md"
    if not readme_path.exists():
        result.add("C5", True, "No README.md (skipped)")
        return
    readme = readme_path.read_text(encoding="utf-8")
    m = re.search(r"<!-- EFC-LEDGER-START -->(.*?)<!-- EFC-LEDGER-END -->", readme, re.DOTALL)
    if not m:
        result.add("C5", False, "No EFC ledger badge found in README")
        return
    badge = m.group(1)
    passed = ledger.get("passed", 0)
    total = ledger.get("total_tests", 0)
    issues = []
    if str(passed) not in badge:
        issues.append(f"passed count mismatch (ledger: {passed})")
    if str(total) not in badge:
        issues.append(f"total count mismatch (ledger: {total})")
    if issues:
        result.add("C5", False, f"README badge issues: {'; '.join(issues)}")
    else:
        result.add("C5", True, "README badge matches ledger counts")


def check_c6_falsification(root: Path, result: VerifyResult) -> None:
    ledger = load_json(root / "docs" / "validation-ledger" / "ledger.json")
    conditions = ledger.get("falsification_conditions", [])
    if not conditions:
        result.add("C6", True, "No falsification conditions defined (skipped)")
        return
    ids = [c.get("id") for c in conditions]
    dupes = [x for x in ids if ids.count(x) > 1]
    if dupes:
        result.add("C6", False, f"Duplicate falsification IDs: {set(dupes)}")
    else:
        result.add("C6", True, f"{len(conditions)} falsification conditions, no duplicates")


def check_c7_status_hierarchy(root: Path, result: VerifyResult) -> None:
    ledger = load_json(root / "docs" / "validation-ledger" / "ledger.json")
    entries = ledger.get("entries", [])
    issues = []
    for entry in entries:
        status = entry.get("status", "")
        tier = entry.get("tier", "")
        if status in (Status.PLANNED_READY, Status.CONCEPTUAL) and tier:
            issues.append(f"{entry.get('id')}: planned but has tier {tier}")
        completed = {
            Status.CONSISTENT_ROBUST,
            Status.COMPLETED_LIKELIHOOD,
            Status.COMPLETED_CONSISTENCY,
            Status.COMPLETED_STRUCTURAL,
        }
        if status in completed and not tier:
            issues.append(f"{entry.get('id')}: completed ({status}) but no tier assigned")
    if issues:
        result.add("C7", False, f"Status hierarchy issues: {'; '.join(issues[:5])}")
    else:
        result.add("C7", True, "All status-tier combinations valid")


def check_c8_doi_consistency(root: Path, result: VerifyResult) -> None:
    ledger = load_json(root / "docs" / "validation-ledger" / "ledger.json")
    ledger_dois: set = set()
    for entry in ledger.get("entries", []):
        ledger_dois.update(entry.get("evidence_dois", []))
    for cat in ("evidence_empirical", "evidence_structural", "evidence_methodological"):
        ledger_dois.update(ledger.get(cat, []))
    html_path = root / "docs" / "public" / "EFC_Validation_Ledger.html"
    if html_path.exists():
        html_text = html_path.read_text(encoding="utf-8")
        html_dois = set(re.findall(r"figshare\.(\d{8})", html_text))
        missing_in_html = ledger_dois - html_dois
        extra_in_html = html_dois - ledger_dois
        if missing_in_html:
            result.add("C8", False, f"{len(missing_in_html)} DOIs in ledger missing from HTML")
        elif extra_in_html:
            result.add(
                "C8",
                True,
                f"DOIs consistent (HTML has {len(extra_in_html)} additional external refs)",
            )
        else:
            result.add("C8", True, "DOIs consistent across ledger and HTML")
    else:
        result.add("C8", True, "No HTML file to check (skipped)")


def _phase2_safety_guard(args: argparse.Namespace) -> None:
    if not getattr(args, "i_know_this_is_staged", False):
        print(
            "ERROR: This is a PHASE 2 STAGED verifier with semantics "
            "incompatible with the Phase 1 data layout.",
            file=sys.stderr,
        )
        print(
            "       It drops the Phase 1 arXiv-leakage / forbidden-phrase "
            "/ §4b-tag invariants.",
            file=sys.stderr,
        )
        print(
            "       Use scripts/maintenance/efc_verify.py (Phase 1) for "
            "real verification.",
            file=sys.stderr,
        )
        print(
            "       Pass --i-know-this-is-staged to run read-only.",
            file=sys.stderr,
        )
        sys.exit(2)


def main() -> None:
    parser = argparse.ArgumentParser(description="[PHASE2_STAGED] EFC C1–C8 verifier")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--i-know-this-is-staged", action="store_true")
    args = parser.parse_args()

    _phase2_safety_guard(args)

    print("EFC Archive Verification (Phase 2 — STAGED, read-only)")
    print("=" * 56)
    result = VerifyResult()
    check_c1_manifests(args.root, result)
    check_c2_ledger_dois_exist(args.root, result)
    check_c3_no_orphan_papers(args.root, result)
    check_c4_html_current(args.root, result)
    check_c5_readme_counts(args.root, result)
    check_c6_falsification(args.root, result)
    check_c7_status_hierarchy(args.root, result)
    check_c8_doi_consistency(args.root, result)

    print()
    if result.all_passed:
        print("✅ All checks passed")
    else:
        failures = result.failures
        print(f"❌ {len(failures)} check(s) failed:")
        for f in failures:
            print(f"   {f['id']}: {f['message']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
