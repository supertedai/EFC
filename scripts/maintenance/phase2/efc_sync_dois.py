#!/usr/bin/env python3
"""
efc_sync_dois.py — [PHASE2_STAGED] Phase 2 rewrite of the DOI sync engine.

⚠️  STAGED. See scripts/maintenance/phase2/README.md.  ⚠️

This is the BRAIN of the Phase 2 pipeline. It:
  1. Reads paper_extractions.json (from efc_gen_ai_friendly.py)
  2. Reads docs/validation-ledger/ledger.json (single source of truth)
  3. For each paper:
     a. Matches it to ledger entries via test_hints and DOI references
     b. Adds missing DOI references to matched entries
     c. Auto-updates entry status based on extracted quantitative results
     d. Updates checkbox states (efc_s, efc_d, efc_c, lcdm)
  4. Writes updated ledger.json
  5. Reports what changed

Modes:
  --check   Read-only — report inconsistencies, exit non-zero if found
  --apply   Apply corrections to ledger.json
  --report  Print detailed report

This rewrite assumes `docs/validation-ledger/ledger.json` follows the
Phase 2 schema (LedgerData dataclass). The current repo's
`docs/validation-ledger/data/ledger.json` uses a different schema
(name, version, tests.physics_test[], evidence_register.empirical[]).
Running this against the current data path will not produce useful
output until a bootstrap migrates the existing tests into the Phase 2
schema — see README.md Conflict 2.

Execution is blocked unless --i-know-this-is-staged is passed.
"""

from __future__ import annotations
import argparse
import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

# Import from the sibling ledger_schema (installed in Phase 1 maintenance dir)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ledger_schema import (  # noqa: E402
    SECTOR_MARK,
    STATUS_EMOJI,
    Status,
    Tier,
    determine_status_from_results,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class SyncReport:
    def __init__(self) -> None:
        self.doi_additions: list[dict] = []
        self.status_updates: list[dict] = []
        self.checkbox_updates: list[dict] = []
        self.missing_entries: list[dict] = []
        self.orphan_dois: list[str] = []
        self.inconsistencies: list[str] = []

    def has_changes(self) -> bool:
        return bool(self.doi_additions or self.status_updates or self.checkbox_updates)

    def has_issues(self) -> bool:
        return bool(self.inconsistencies or self.orphan_dois)

    def print_report(self) -> None:
        print("\n" + "=" * 60)
        print("EFC DOI SYNC REPORT (Phase 2)")
        print("=" * 60)
        if self.doi_additions:
            print(f"\n📎 DOI additions ({len(self.doi_additions)}):")
            for d in self.doi_additions:
                print(f"  + {d['doi']} → {d['entry_id']} ({d['entry_name']})")
        if self.status_updates:
            print(f"\n🔄 Status updates ({len(self.status_updates)}):")
            for s in self.status_updates:
                old_emoji = STATUS_EMOJI.get(s["old_status"], "?")
                new_emoji = STATUS_EMOJI.get(s["new_status"], "?")
                print(f"  {old_emoji} → {new_emoji} {s['entry_id']}: {s['reason']}")
        if self.checkbox_updates:
            print(f"\n☑️  Checkbox updates ({len(self.checkbox_updates)}):")
            for c in self.checkbox_updates:
                print(f"  {c['entry_id']}.{c['field']}: {c['old']} → {c['new']} ({c['reason']})")
        if self.missing_entries:
            print(f"\n⚠️  Papers without matching ledger entry ({len(self.missing_entries)}):")
            for m in self.missing_entries:
                print(f"  ? {m['title']} (DOI: {m['doi']})")
                if m.get("test_hints"):
                    print(f"    Hints: {', '.join(m['test_hints'])}")
        if self.orphan_dois:
            print(f"\n🔗 DOIs in papers but not in ledger ({len(self.orphan_dois)}):")
            for d in self.orphan_dois[:20]:
                print(f"  - {d}")
        if self.inconsistencies:
            print(f"\n❌ Inconsistencies ({len(self.inconsistencies)}):")
            for i in self.inconsistencies:
                print(f"  ! {i}")
        if not (self.has_changes() or self.has_issues()):
            print("\n✅ Everything consistent — no changes needed.")
        print()


def match_paper_to_entries(paper: dict, entries: list[dict]) -> list[dict]:
    matches = []
    paper_dois = set(paper.get("dois_referenced", []))
    paper_hints = set(paper.get("test_hints", []))
    paper_doi = paper.get("figshare_id", "")
    for entry in entries:
        score = 0
        entry_dois = set(entry.get("evidence_dois", []))
        if paper_doi and paper_doi in entry_dois:
            score += 10
        overlap = paper_dois & entry_dois
        if overlap:
            score += len(overlap) * 2
        if entry.get("id") in paper_hints:
            score += 5
        if score > 0:
            matches.append({"entry": entry, "score": score})
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches


def update_entry_from_paper(entry: dict, paper: dict, report: SyncReport) -> bool:
    changed = False
    entry_id = entry.get("id", "?")
    entry_name = entry.get("phenomenon", "?")
    paper_doi = paper.get("figshare_id", "")
    quant = paper.get("quantitative", {})

    existing_dois = set(entry.get("evidence_dois", []))
    if paper_doi and paper_doi not in existing_dois:
        entry.setdefault("evidence_dois", []).append(paper_doi)
        report.doi_additions.append(
            {"doi": paper_doi, "entry_id": entry_id, "entry_name": entry_name}
        )
        changed = True

    if quant:
        if "delta_chi2_values" in quant and entry.get("delta_chi2") is None:
            entry["delta_chi2"] = quant["delta_chi2_values"][0]
            changed = True
        if "delta_aic_values" in quant and entry.get("delta_aic") is None:
            entry["delta_aic"] = quant["delta_aic_values"][0]
            changed = True
        if quant.get("pre_registered"):
            entry["pre_registered"] = True
            changed = True
        if quant.get("frozen_params"):
            entry["frozen_params"] = True
            changed = True
        if quant.get("has_pass") and not quant.get("has_fail"):
            if entry.get("pass_fail") != "PASS":
                entry["pass_fail"] = "PASS"
                changed = True

    new_status = determine_status_from_results(entry)
    if new_status and new_status != entry.get("status"):
        old_status = entry.get("status", "?")
        upgrade_order = [
            Status.CONCEPTUAL,
            Status.PLANNED_READY,
            Status.FRAMEWORK_DIAGNOSTIC,
            Status.PHENOMENOLOGICAL,
            Status.CONSISTENT_PRELIMINARY,
            Status.COMPLETED_CONSISTENCY,
            Status.COMPLETED_STRUCTURAL,
            Status.COMPLETED_LIKELIHOOD,
            Status.CONSISTENT_ROBUST,
        ]
        old_rank = upgrade_order.index(old_status) if old_status in upgrade_order else -1
        new_rank = upgrade_order.index(new_status) if new_status in upgrade_order else -1
        if new_status == Status.DISCREPANT or new_rank > old_rank:
            report.status_updates.append(
                {
                    "entry_id": entry_id,
                    "old_status": old_status,
                    "new_status": new_status,
                    "reason": (
                        f"Auto from paper {paper_doi}: Δχ²={entry.get('delta_chi2')}, "
                        f"pass_fail={entry.get('pass_fail')}"
                    ),
                }
            )
            entry["status"] = new_status
            changed = True

    if changed:
        _update_checkboxes(entry, report)
        entry["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return changed


def _update_checkboxes(entry: dict, report: SyncReport) -> None:
    entry_id = entry.get("id", "?")
    status = entry.get("status", "")
    active = entry.get("active_sectors", "").upper()
    completed_statuses = {
        Status.CONSISTENT_ROBUST,
        Status.CONSISTENT_PRELIMINARY,
        Status.COMPLETED_LIKELIHOOD,
        Status.COMPLETED_CONSISTENCY,
        Status.COMPLETED_STRUCTURAL,
        Status.PHENOMENOLOGICAL,
    }
    if status in completed_statuses:
        if "BG" in active or "GRW" in active or "DGS" in active:
            if entry.get("efc_d") != "supported":
                report.checkbox_updates.append(
                    {
                        "entry_id": entry_id,
                        "field": "efc_d",
                        "old": entry.get("efc_d"),
                        "new": "supported",
                        "reason": f"Status={status}, active_sectors includes growth/bg",
                    }
                )
                entry["efc_d"] = "supported"
        if "SCR" in active:
            if entry.get("efc_s") != "supported":
                report.checkbox_updates.append(
                    {
                        "entry_id": entry_id,
                        "field": "efc_s",
                        "old": entry.get("efc_s"),
                        "new": "supported",
                        "reason": "Screening sector active",
                    }
                )
                entry["efc_s"] = "supported"
        new_lcdm = "supported"
        if status == Status.DISCREPANT:
            new_lcdm = "discrepant"
        if entry.get("lcdm") not in ("discrepant", "tension") or status == Status.DISCREPANT:
            if entry.get("lcdm") != new_lcdm:
                report.checkbox_updates.append(
                    {
                        "entry_id": entry_id,
                        "field": "lcdm",
                        "old": entry.get("lcdm"),
                        "new": new_lcdm,
                        "reason": "Completed test, ΛCDM support updated",
                    }
                )
                entry["lcdm"] = new_lcdm
    elif status == Status.DISCREPANT:
        for field in ("efc_s", "efc_d", "efc_c"):
            if entry.get(field) == "supported":
                report.checkbox_updates.append(
                    {
                        "entry_id": entry_id,
                        "field": field,
                        "old": "supported",
                        "new": "discrepant",
                        "reason": "Status changed to discrepant",
                    }
                )
                entry[field] = "discrepant"


def sync(ledger: dict, extractions: dict, report: SyncReport) -> dict:
    entries = ledger.get("entries", [])
    papers = extractions.get("papers", [])
    doi_to_entries: dict = {}
    for entry in entries:
        for doi in entry.get("evidence_dois", []):
            doi_to_entries.setdefault(doi, []).append(entry)
    all_ledger_dois: set = set()
    for entry in entries:
        all_ledger_dois.update(entry.get("evidence_dois", []))

    modified_count = 0
    for paper in papers:
        paper_doi = paper.get("figshare_id", "")
        paper_title = paper.get("title", "?")
        matches = match_paper_to_entries(paper, entries)
        if not matches:
            if paper_doi in doi_to_entries:
                for entry in doi_to_entries[paper_doi]:
                    if update_entry_from_paper(entry, paper, report):
                        modified_count += 1
            else:
                report.missing_entries.append(
                    {
                        "title": paper_title,
                        "doi": paper_doi,
                        "test_hints": paper.get("test_hints", []),
                    }
                )
        else:
            for match in matches:
                if match["score"] >= 3:
                    if update_entry_from_paper(match["entry"], paper, report):
                        modified_count += 1
        for ref_doi in paper.get("dois_referenced", []):
            if ref_doi not in all_ledger_dois and ref_doi != paper_doi:
                report.orphan_dois.append(ref_doi)

    _recount_ledger(ledger)
    ledger["last_generated"] = datetime.now(timezone.utc).isoformat()
    print(f"  Processed {len(papers)} papers, modified {modified_count} entries")
    return ledger


def _recount_ledger(ledger: dict) -> None:
    entries = ledger.get("entries", [])
    ledger["total_tests"] = len(entries)
    ledger["passed"] = sum(
        1
        for e in entries
        if e.get("status")
        in (
            Status.CONSISTENT_ROBUST,
            Status.COMPLETED_LIKELIHOOD,
            Status.COMPLETED_CONSISTENCY,
            Status.COMPLETED_STRUCTURAL,
        )
    )
    ledger["partial"] = sum(
        1
        for e in entries
        if e.get("status")
        in (
            Status.CONSISTENT_PRELIMINARY,
            Status.PHENOMENOLOGICAL,
            Status.FRAMEWORK_DIAGNOSTIC,
        )
    )
    ledger["failed"] = sum(
        1 for e in entries if e.get("status") in (Status.DISCREPANT, Status.FALSIFIED)
    )
    ledger["planned"] = sum(
        1 for e in entries if e.get("status") in (Status.PLANNED_READY, Status.CONCEPTUAL)
    )


def _phase2_safety_guard(args: argparse.Namespace) -> None:
    if not getattr(args, "i_know_this_is_staged", False):
        print(
            "ERROR: This is a PHASE 2 STAGED script.",
            file=sys.stderr,
        )
        print(
            "       The current repo uses Phase 1 schema; this sync would not "
            "match any entries.",
            file=sys.stderr,
        )
        print(
            "       See scripts/maintenance/phase2/README.md.",
            file=sys.stderr,
        )
        print(
            "       Pass --i-know-this-is-staged to bypass this guard.",
            file=sys.stderr,
        )
        sys.exit(2)


def main() -> None:
    parser = argparse.ArgumentParser(description="[PHASE2_STAGED] DOI sync")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--i-know-this-is-staged", action="store_true")
    args = parser.parse_args()

    _phase2_safety_guard(args)

    if not (args.check or args.apply or args.report):
        args.check = True

    ledger_path = args.root / "docs" / "validation-ledger" / "ledger.json"
    extractions_path = args.root / "docs" / "validation-ledger" / "paper_extractions.json"
    ledger = load_json(ledger_path)
    extractions = load_json(extractions_path)
    if not ledger:
        print(f"ERROR: ledger.json not found at {ledger_path}")
        sys.exit(1)
    if not extractions:
        print("WARNING: paper_extractions.json not found — run gen_ai_friendly first")
        if args.check:
            sys.exit(1)
        return

    report = SyncReport()
    updated_ledger = sync(deepcopy(ledger), extractions, report)
    report.print_report()
    if args.apply and report.has_changes():
        save_json(updated_ledger, ledger_path)
        print(f"✅ Applied changes to {ledger_path}")
    if args.check and (report.has_issues() or report.has_changes()):
        sys.exit(1)


if __name__ == "__main__":
    main()
