"""
Repo state snapshot + canonical-source readers.

A `State` is a hashable, comparable description of the repo's relevant
sync surfaces. Two states being equal means the fixpoint is reached
(no further propagation needed).

Only the fields that drive cross-references go in here — generated_at
timestamps are deliberately excluded so re-runs without semantic
changes converge in one iteration.
"""
from __future__ import annotations

import glob
import json
import os
import re
from dataclasses import dataclass, field
from typing import Any

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
LEDGER_DATA = os.path.join(REPO, "docs", "validation-ledger", "data")
PUBLIC = os.path.join(REPO, "docs", "public")


def _safe_json(path: str) -> dict | list | None:
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def _bare_doi(s: str | None) -> str | None:
    """Strip 10.6084/m9.figshare. prefix, return digits-only DOI."""
    if not s:
        return None
    m = re.search(r"(\d{6,})", str(s))
    return m.group(1) if m else None


@dataclass(frozen=True)
class State:
    """Cross-checkable snapshot of the repo's sync surfaces."""

    n_paper_dirs: int
    paper_dois: frozenset[str]
    ledger_version: str | None
    index_md_version: str | None
    public_version: str | None
    n_ai_friendly: int | None
    total_public_tests: int | None
    n_falsified: int | None
    inference_modules: int | None
    doi_map_count: int
    evidence_register_count: int
    changelog_top_date: str | None
    ecosystem_date_modified: str | None

    @classmethod
    def snapshot(cls) -> "State":
        # Paper directories
        paper_dirs = sorted(
            d for d in glob.glob(os.path.join(PAPERS, "*"))
            if os.path.isdir(d) and os.path.exists(os.path.join(d, "index.json"))
        )
        dois: set[str] = set()
        for d in paper_dirs:
            idx = _safe_json(os.path.join(d, "index.json")) or {}
            doi = idx.get("doi") or (idx.get("identifiers") or {}).get("doi")
            bd = _bare_doi(doi)
            if bd:
                dois.add(bd)

        # Ledger version
        ledger_json = _safe_json(os.path.join(LEDGER_DATA, "ledger.json")) or {}
        ledger_version = str(ledger_json.get("version")) if ledger_json.get("version") else None
        stats = ledger_json.get("stats") or {}

        # Index.md version
        index_md_path = os.path.join(REPO, "docs", "validation-ledger", "index.md")
        index_md_version = None
        if os.path.exists(index_md_path):
            with open(index_md_path, encoding="utf-8") as fh:
                head = fh.read(2000)
            m = re.search(r"Version:\s*v?([\d.]+)", head)
            if m:
                index_md_version = m.group(1)

        # Public version
        codemeta = _safe_json(os.path.join(REPO, "codemeta.json")) or {}
        public_version = codemeta.get("version")

        # AI-friendly catalogue
        ai_idx = _safe_json(os.path.join(PAPERS, "ai_friendly_index.json")) or {}
        n_ai = ai_idx.get("n_packages")

        # DOI map
        doi_map = _safe_json(os.path.join(REPO, "figshare", "doi-map.json")) or {}
        doi_map_count = len(doi_map) if isinstance(doi_map, dict) else len(doi_map or [])

        # Evidence register
        ev = _safe_json(os.path.join(LEDGER_DATA, "evidence-register.json")) or {}
        ev_count = 0
        if isinstance(ev, dict):
            cats = ev.get("categories") or {}
            for v in cats.values():
                if isinstance(v, list):
                    ev_count += len(v)
        elif isinstance(ev, list):
            ev_count = len(ev)

        # Changelog top date
        cl = _safe_json(os.path.join(LEDGER_DATA, "changelog.json")) or {}
        cl_top = None
        entries = cl.get("entries") if isinstance(cl, dict) else cl
        if isinstance(entries, list) and entries:
            top = entries[0] if isinstance(entries[0], dict) else {}
            cl_top = top.get("date") or top.get("dateModified")

        # Ecosystem date
        eco = _safe_json(os.path.join(REPO, "ecosystem.jsonld")) or {}
        eco_date = eco.get("dateModified")

        # Inference modules
        inf = _safe_json(os.path.join(LEDGER_DATA, "inference.json")) or {}
        if isinstance(inf, dict):
            modules = inf.get("modules") or inf.get("entries") or []
        else:
            modules = inf if isinstance(inf, list) else []

        return cls(
            n_paper_dirs=len(paper_dirs),
            paper_dois=frozenset(dois),
            ledger_version=ledger_version,
            index_md_version=index_md_version,
            public_version=public_version,
            n_ai_friendly=n_ai,
            total_public_tests=stats.get("total_public"),
            n_falsified=stats.get("n_falsified"),
            inference_modules=len(modules) if modules else stats.get("inference_count"),
            doi_map_count=doi_map_count,
            evidence_register_count=ev_count,
            changelog_top_date=cl_top,
            ecosystem_date_modified=eco_date,
        )

    def diff(self, other: "State") -> dict[str, tuple[Any, Any]]:
        """Return {field: (self_val, other_val)} for fields that differ."""
        out: dict[str, tuple[Any, Any]] = {}
        for f in self.__dataclass_fields__:
            a, b = getattr(self, f), getattr(other, f)
            if a != b:
                out[f] = (a, b)
        return out
