#!/usr/bin/env python3
"""
EFC Wiki Builder
================

Regenerates docs/wiki/03-Papers-by-Topic.md from every
docs/papers/efc/<slug>/index.json.

Grouping:
    Primary: paper_type  (theory / empirical_test / sealed_prediction /
                          methodology / infrastructure /
                          observational_pipeline / other)
    Within:  tier sort (T1 > T2 > T3 > N/A), then title alpha

Also emits a topic section grouped by common keyword clusters
(SPARC, BAO, CMB, Lensing, Clusters, EFC-C / neural, etc.).

Run:
    python3 scripts/maintenance/efc_build_wiki.py

The output file is entirely auto-generated — do not edit by hand.
"""

from __future__ import annotations

import json
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[2]
PAPERS_DIR = REPO_ROOT / "docs" / "papers" / "efc"
OUT_PATH = REPO_ROOT / "docs" / "wiki" / "03-Papers-by-Topic.md"

PAPER_TYPE_ORDER = [
    ("theory", "Theory"),
    ("empirical_test", "Empirical tests"),
    ("sealed_prediction", "Sealed predictions"),
    ("methodology", "Methodology"),
    ("observational_pipeline", "Observational pipelines"),
    ("infrastructure", "Infrastructure"),
    ("other", "Other / unclassified"),
]

TIER_RANK = {"T1": 0, "T2": 1, "T3": 2, "N/A": 3, "": 4, None: 4}

TOPIC_CLUSTERS = [
    ("SPARC / rotation curves", {"sparc", "galaxy rotation curves", "rotation curves"}),
    ("BAO / background expansion", {"bao", "boss dr12", "desi", "baryon acoustic oscillations"}),
    ("CMB", {"cmb", "cosmic microwave background", "planck"}),
    ("Weak lensing / cosmic shear", {"weak lensing", "gravitational lensing", "cosmic shear",
                                      "kids-1000", "gravitational slip"}),
    ("Galaxy clusters", {"galaxy clusters", "bullet cluster", "lensing cluster"}),
    ("Growth / RSD / σ8", {"growth rate", "rsd", "s8 tension", "σ8", "sigma_8"}),
    ("Modified gravity / screening", {"modified gravity", "screening", "μ", "mu-sigma", "slip"}),
    ("Entropy / thermodynamics", {"entropy", "thermodynamics", "entropy gradient"}),
    ("EFC-C / neural / consciousness", {"efc-c", "neural", "consciousness", "cognitive",
                                         "rlhf", "psychiatric"}),
    ("Discrete gravity / Grid", {"discrete", "grid", "graph", "aqual", "lattice"}),
    ("Varying constants / ontology", {"variable speed of light", "varying alpha",
                                       "running constants", "ontology"}),
]


def load_papers():
    """Return list of (slug, meta_dict) for every paper with an index.json."""
    out = []
    if not PAPERS_DIR.exists():
        return out
    for d in sorted(PAPERS_DIR.iterdir()):
        if not d.is_dir():
            continue
        idx = d / "index.json"
        if not idx.exists():
            continue
        try:
            data = json.loads(idx.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"[efc-build-wiki] skipping {d.name}: {exc}")
            continue
        out.append((d.name, data))
    return out


def title_of(meta: dict) -> str:
    t = meta.get("short_title") or meta.get("title") or meta.get("id") or "(untitled)"
    return str(t).strip()


def doi_of(meta: dict) -> str | None:
    d = meta.get("doi")
    if not d:
        return None
    d = str(d).strip()
    return d or None


def doi_url(doi: str) -> str:
    return f"https://doi.org/{doi}"


def paper_link(slug: str, meta: dict) -> str:
    t = title_of(meta).replace("|", "\\|")
    return f"[{t}](../papers/efc/{slug}/)"


def row(slug: str, meta: dict) -> str:
    tier = str(meta.get("tier") or "—")
    doi = doi_of(meta)
    doi_cell = f"[{doi}]({doi_url(doi)})" if doi else "—"
    return f"| {tier} | {paper_link(slug, meta)} | {doi_cell} |"


def group_by_paper_type(papers):
    buckets = defaultdict(list)
    for slug, meta in papers:
        pt_raw = str(meta.get("paper_type") or "other").strip().lower().replace(" ", "_")
        if pt_raw not in {k for k, _ in PAPER_TYPE_ORDER}:
            pt_raw = "other"
        buckets[pt_raw].append((slug, meta))
    for key in buckets:
        buckets[key].sort(key=lambda sm: (TIER_RANK.get(str(sm[1].get("tier") or ""), 9),
                                          title_of(sm[1]).lower()))
    return buckets


def cluster_by_keyword(papers):
    clusters = defaultdict(list)
    for slug, meta in papers:
        kws = {str(k).lower() for k in meta.get("keywords") or []}
        for label, probes in TOPIC_CLUSTERS:
            if kws & probes:
                clusters[label].append((slug, meta))
    for key in clusters:
        clusters[key].sort(key=lambda sm: (TIER_RANK.get(str(sm[1].get("tier") or ""), 9),
                                           title_of(sm[1]).lower()))
    return clusters


def render(papers) -> str:
    buckets = group_by_paper_type(papers)
    topics = cluster_by_keyword(papers)
    total = len(papers)

    lines = [
        "# 03 · Papers by topic",
        "",
        "> ⚙️ **Auto-generated** by [`scripts/maintenance/efc_build_wiki.py`](../../scripts/maintenance/efc_build_wiki.py).",
        "> Do not edit this file by hand — rerun the generator instead.",
        "",
        "[🏠 Home](./Home.md) · [← Evidence](./02-Evidence.md) · [→ Reproduce](./04-Reproduce.md)",
        "",
        "---",
        "",
        f"**Total papers indexed:** {total}  ",
        "**Tiers:** T1 = canonical anchor · T2 = core support · T3 = subsidiary / working note  ",
        "**Sorted:** tier ascending, then title alphabetical within each group.",
        "",
        "---",
        "",
        "## Jump to",
        "",
    ]
    for key, label in PAPER_TYPE_ORDER:
        n = len(buckets.get(key, []))
        if n:
            lines.append(f"- [{label}](#{key}) ({n})")
    lines.append("- [By research topic](#by-research-topic)")
    lines.append("")
    lines.append("---")
    lines.append("")

    for key, label in PAPER_TYPE_ORDER:
        rows = buckets.get(key, [])
        if not rows:
            continue
        lines.append(f"## {label}")
        lines.append("")
        lines.append(f'<a id="{key}"></a>')
        lines.append("")
        lines.append("| Tier | Paper | DOI |")
        lines.append("|---|---|---|")
        for slug, meta in rows:
            lines.append(row(slug, meta))
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## By research topic")
    lines.append("")
    lines.append('<a id="by-research-topic"></a>')
    lines.append("")
    lines.append("A paper can appear in several topics; clusters are derived from its `keywords`.")
    lines.append("")
    for label, _ in TOPIC_CLUSTERS:
        rows = topics.get(label, [])
        if not rows:
            continue
        lines.append(f"### {label}  ({len(rows)})")
        lines.append("")
        lines.append("| Tier | Paper | DOI |")
        lines.append("|---|---|---|")
        for slug, meta in rows:
            lines.append(row(slug, meta))
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("[🏠 Back to Home](./Home.md)")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    papers = load_papers()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(render(papers), encoding="utf-8")
    print(f"[efc-build-wiki] {len(papers)} papers -> {OUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
