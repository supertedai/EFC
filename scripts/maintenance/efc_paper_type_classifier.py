#!/usr/bin/env python3
"""
EFC Paper-Type Classifier (deterministic)
==========================================

A small heuristic that infers ``paper_type`` for any paper whose
``index.json`` doesn't carry one yet. Title + description text are
matched against keyword sets; the first matching category wins.

The classifier never overwrites an existing ``paper_type``. It only
fills in the field for papers that lack it. The full LLM-driven
``efc_ai_brain.analyze_holistic_impact()`` is more powerful, but
requires an API key. This deterministic fallback at least gives
every paper a sensible category so downstream sync steps
(efc_ledger_autofill, efc_evidence_mirror) don't drop the paper
on the floor.

Categories (priority order)
---------------------------
  empirical_validation  — title contains "validation", "validate",
                           "fit to <dataset>", "demonstrates"
  empirical_test        — "test of", "constraint on", "measurement"
  observational_pipeline — "pipeline", "DR1/DR2/DR3", "stage-iv"
  sealed_prediction     — "sealed prediction", "pre-registered"
  methodology           — "framework", "parameterization", "method"
  infrastructure        — "architecture", "schema", "manifest"
  theory                — fallback for everything else

Idempotent. Adds ``paper_type_inferred: true`` to flag heuristic
classification (so a future LLM enrichment can override).
"""
from __future__ import annotations
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
SKIP_TOP = {
    "README.md", "cover_letter-2.pdf", "efc_graph_edges.json",
    "efc_graph_schema.json", "efc_index.json", "efc_index.jsonld",
    "ai_friendly_index.json",
}

# Order matters: first match wins.
RULES = (
    ("empirical_validation", re.compile(
        r"\b(?:validation|validate[ds]?|cross[- ]validate|fit[s]? to|"
        r"demonstrate[ds]?|empirical(?:ly)? validate)\b", re.IGNORECASE)),
    ("observational_pipeline", re.compile(
        r"\b(?:pipeline|stage[- ]?iv|stage-iv|DR\d+|likelihood|"
        r"reduction (?:pipeline|chain)|cosmological pipeline)\b", re.IGNORECASE)),
    ("sealed_prediction", re.compile(
        r"\b(?:sealed prediction|pre[- ]registered|pre-registration|freeze|"
        r"hash[- ]locked|locked[- ]forecast)\b", re.IGNORECASE)),
    ("empirical_test", re.compile(
        r"\b(?:null[- ]test|null test|test of|constraint[s]? on|"
        r"falsif|kill[- ]test|measurement of|consistency test|"
        r"parameter inference|MCMC|fit\b|chi[- ]squared|log[- ]likelihood)\b",
        re.IGNORECASE)),
    ("methodology", re.compile(
        r"\b(?:framework|parameteri[sz]ation|method(?:ology)?|"
        r"derivation|algorithm|schema|implementation|protocol)\b",
        re.IGNORECASE)),
    ("infrastructure", re.compile(
        r"\b(?:architecture|manifest|registry|catalog(?:ue)?|"
        r"index\b|provenance|AUTH|ledger|infrastructure)\b",
        re.IGNORECASE)),
)


def classify(text):
    if not text:
        return "theory"
    for label, regex in RULES:
        if regex.search(text):
            return label
    return "theory"


def _load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main():
    classified = []
    for name in sorted(os.listdir(PAPERS)):
        if name in SKIP_TOP:
            continue
        full = os.path.join(PAPERS, name)
        if not os.path.isdir(full):
            continue
        idx_path = os.path.join(full, "index.json")
        idx = _load(idx_path)
        if not idx:
            continue
        if idx.get("paper_type"):
            continue  # already classified — never overwrite

        title = idx.get("title") or name
        desc = idx.get("description") or ""
        abstract = idx.get("abstract") or ""
        text = " ".join([str(title), str(desc), str(abstract), name])
        ptype = classify(text)

        idx["paper_type"] = ptype
        idx["paper_type_inferred"] = True
        _save(idx_path, idx)
        classified.append((name, ptype))

    if not classified:
        print("[efc-paper-type] all papers already classified")
        return 0

    print(f"[efc-paper-type] inferred paper_type for {len(classified)} paper(s):")
    for name, ptype in classified:
        print(f"  {ptype:<22}  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
