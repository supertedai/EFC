#!/usr/bin/env python3
"""EFC rootfile-consistency checker.

Verifies that every Ledger-version string appearing in the agent-facing
rootfiles (``README.md``, ``AGENTS.md``, ``llms.txt``) matches the
authoritative version published by ``docs/public/EFC_Validation_Ledger.html``.

The Ledger uses a dual-version scheme:
* **public HTML version** — declared by tags such as
  ``<strong>v3.18 (public HTML)</strong>``. This is what readers cite when
  they reference "the Validation Ledger".
* **internal/data version** — declared by tags such as
  ``<strong>v4.6 update</strong>``. This indexes the underlay ledger
  (``docs/validation-ledger/data/ledger.json``) and is incremented on
  every internal data update.

This checker is **read-only**. It surfaces drift; it never rewrites files.
The companion ``efc_drift_detector.py --fix`` already covers paper/test
counts; this script complements it on the orthogonal axis of version
strings.

Exit codes
----------
0 = all rootfile version mentions match Ledger
2 = drift detected
3 = unable to extract authoritative version

Usage
-----
    python3 scripts/maintenance/efc_rootfile_consistency.py            # report
    python3 scripts/maintenance/efc_rootfile_consistency.py --json     # machine
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_HTML = REPO_ROOT / "docs" / "public" / "EFC_Validation_Ledger.html"

ROOTFILES = {
    "README.md": REPO_ROOT / "README.md",
    "AGENTS.md": REPO_ROOT / "AGENTS.md",
    "llms.txt": REPO_ROOT / "llms.txt",
}


@dataclass
class Drift:
    file: str
    line: int
    found: str
    expected: str
    detail: str


@dataclass
class Report:
    public_version: str = ""
    internal_version: str = ""
    drifts: list[Drift] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.drifts


PUBLIC_HTML_VERSION_RE = re.compile(
    r"v(\d+\.\d+)\s*\(public\s*HTML\)", re.IGNORECASE
)
INTERNAL_UPDATE_TAG_RE = re.compile(
    r"<strong>\s*v(\d+\.\d+)\s+update", re.IGNORECASE
)


def _max_version(values: Iterable[str]) -> str:
    """Return the highest semver-like X.Y string from an iterable."""
    best: tuple[int, int] | None = None
    best_str = ""
    for v in values:
        try:
            major, minor = (int(x) for x in v.split("."))
        except ValueError:
            continue
        key = (major, minor)
        if best is None or key > best:
            best = key
            best_str = v
    return best_str


def extract_authoritative_versions() -> tuple[str, str]:
    if not LEDGER_HTML.exists():
        raise SystemExit(f"[rootfile-consistency] Ledger HTML missing: {LEDGER_HTML}")
    text = LEDGER_HTML.read_text(encoding="utf-8", errors="replace")
    public = _max_version(m.group(1) for m in PUBLIC_HTML_VERSION_RE.finditer(text))
    internal = _max_version(m.group(1) for m in INTERNAL_UPDATE_TAG_RE.finditer(text))
    if not public:
        raise SystemExit(
            "[rootfile-consistency] could not extract '(public HTML)' version"
            f" from {LEDGER_HTML.relative_to(REPO_ROOT)}"
        )
    if not internal:
        raise SystemExit(
            "[rootfile-consistency] could not extract internal v-update tag"
            f" from {LEDGER_HTML.relative_to(REPO_ROOT)}"
        )
    return public, internal


def _scan_file_for_versions(path: Path) -> list[tuple[int, str, str]]:
    """Return a list of (line_no, raw_match, kind) tuples where kind ∈
    {"public", "internal"} based on contextual clues."""
    if not path.exists():
        return []
    out: list[tuple[int, str, str]] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    # Patterns that clearly identify a Ledger version reference.
    patterns = [
        # README badge: "Validation_Ledger-v3.17"
        (re.compile(r"Validation_Ledger-v(\d+\.\d+)", re.IGNORECASE), "public"),
        # README quick-ref / prose: "(v3.17 public / v4.8 internal)"
        (re.compile(r"\(v(\d+\.\d+)\s+public\b"), "public"),
        (re.compile(r"/\s*v(\d+\.\d+)\s+internal\)"), "internal"),
        # README prose: "v3.17 / v4.8 internal"
        (re.compile(r"v(\d+\.\d+)\s*/\s*v\d+\.\d+\s+internal"), "public"),
        (re.compile(r"v\d+\.\d+\s*/\s*v(\d+\.\d+)\s+internal"), "internal"),
        # AGENTS / llms.txt yaml-style fields
        (re.compile(r"validation_ledger_public:\s*v(\d+\.\d+)", re.IGNORECASE), "public"),
        (re.compile(r"validation_ledger_internal:\s*v(\d+\.\d+)", re.IGNORECASE), "internal"),
        # llms.txt header "## VALIDATION STATUS (v3.16 / v4.7)"
        (re.compile(r"VALIDATION STATUS\s*\(v(\d+\.\d+)\s*/\s*v\d+\.\d+\)"), "public"),
        (re.compile(r"VALIDATION STATUS\s*\(v\d+\.\d+\s*/\s*v(\d+\.\d+)\)"), "internal"),
        # README/AGENTS tree map: "Validation Ledger (v3.15)"
        (re.compile(r"Validation Ledger\s*\(v(\d+\.\d+)\)"), "public"),
        (re.compile(r"public/.*?Validation Ledger\s*\(v(\d+\.\d+)", re.IGNORECASE), "public"),
        # llms.txt prose: "Validation Ledger (v3.16), Master Spec"
        (re.compile(r"Validation Ledger\s*\(v(\d+\.\d+)\),\s*Master Spec", re.IGNORECASE), "public"),
    ]
    for pat, kind in patterns:
        for m in pat.finditer(text):
            line_no = text[: m.start()].count("\n") + 1
            out.append((line_no, m.group(1), kind))
    return out


def detect_drift() -> Report:
    public, internal = extract_authoritative_versions()
    report = Report(public_version=public, internal_version=internal)
    expected = {"public": public, "internal": internal}
    for name, path in ROOTFILES.items():
        seen: set[tuple[int, str, str]] = set()
        for line_no, found, kind in _scan_file_for_versions(path):
            key = (line_no, found, kind)
            if key in seen:
                continue
            seen.add(key)
            if found != expected[kind]:
                report.drifts.append(
                    Drift(
                        file=name,
                        line=line_no,
                        found=f"v{found}",
                        expected=f"v{expected[kind]}",
                        detail=(
                            f"{kind} Ledger version on line {line_no} is"
                            f" v{found}; Ledger HTML publishes"
                            f" v{expected[kind]}"
                        ),
                    )
                )
    return report


def run(json_out: bool) -> int:
    report = detect_drift()
    if json_out:
        out = {
            "public_version": report.public_version,
            "internal_version": report.internal_version,
            "drifts": [
                {
                    "file": d.file,
                    "line": d.line,
                    "found": d.found,
                    "expected": d.expected,
                    "detail": d.detail,
                }
                for d in report.drifts
            ],
            "ok": report.ok,
        }
        print(json.dumps(out, indent=2))
    else:
        print(
            f"[rootfile-consistency] Ledger truth: public=v{report.public_version}"
            f", internal=v{report.internal_version}"
        )
        if report.ok:
            print("[rootfile-consistency] all rootfile version mentions match ✓")
        else:
            print(f"[rootfile-consistency] {len(report.drifts)} drift(s):")
            for d in report.drifts:
                print(f"  {d.file}:{d.line}: {d.found} → {d.expected} ({d.detail})")
            print(
                "\nFix manually (this checker is read-only). Cross-reference"
                f" line numbers above against {LEDGER_HTML.relative_to(REPO_ROOT)}."
            )
    return 0 if report.ok else 2


def main(argv: Iterable[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="EFC rootfile-consistency checker")
    p.add_argument("--json", action="store_true", help="machine-readable JSON output")
    args = p.parse_args(list(argv) if argv is not None else None)
    return run(json_out=args.json)


if __name__ == "__main__":
    sys.exit(main())
