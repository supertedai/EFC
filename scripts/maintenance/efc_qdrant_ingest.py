#!/usr/bin/env python3
"""
EFC Qdrant Ingest — Semantic Vector Layer for Framework Atlas
=============================================================

Builds a Qdrant collection indexing:
  - All EFC paper packages (docs/papers/efc/*/index.json + *.md)
  - The committed Framework Atlas (schema/framework_atlas.jsonld)
    — one point per framework, one per prediction, one per relation

This gives any Claude session a semantic search layer over the 150-paper
corpus and the 42-framework atlas, complementing the topological graph
(Symbiose/Neo4j) with nearest-neighbour retrieval.

Requirements:
  - QDRANT_URL and QDRANT_API_KEY in env (cloud) OR
    QDRANT_URL=http://localhost:6333 for a local instance
  - EMBEDDING_PROVIDER: "openai" | "voyage" | "local"
    - openai   → OPENAI_API_KEY, model text-embedding-3-large
    - voyage   → VOYAGE_API_KEY, model voyage-3
    - local    → sentence-transformers (installed separately)

Usage:
  python3 scripts/maintenance/efc_qdrant_ingest.py --dry-run
  python3 scripts/maintenance/efc_qdrant_ingest.py --apply
  python3 scripts/maintenance/efc_qdrant_ingest.py --apply --only atlas
  python3 scripts/maintenance/efc_qdrant_ingest.py --apply --only papers

Collections created:
  efc_papers       — paper packages with rich metadata payload
  efc_atlas        — atlas entries (frameworks, predictions, relations)

This script is a scaffolding: it enumerates what WOULD be ingested and
computes deterministic point IDs. Actual embedding + upsert calls are
gated behind credentials so the script is safe to run in CI/sandbox
without pushing data anywhere.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

REPO = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
PAPERS_DIR = REPO / "docs" / "papers" / "efc"
ATLAS_PATH = REPO / "schema" / "framework_atlas.jsonld"

SKIP_PAPER_NAMES = {
    "README.md", "cover_letter-2.pdf", "efc_graph_edges.json",
    "efc_graph_schema.json", "efc_index.json", "efc_index.jsonld",
    "ai_friendly_index.json",
}

COLLECTION_PAPERS = "efc_papers"
COLLECTION_ATLAS = "efc_atlas"


def stable_point_id(*parts: str) -> str:
    h = hashlib.sha256("::".join(parts).encode("utf-8")).hexdigest()
    return h[:32]


def enumerate_paper_points() -> list[dict]:
    points: list[dict] = []
    if not PAPERS_DIR.exists():
        return points
    for name in sorted(os.listdir(PAPERS_DIR)):
        if name in SKIP_PAPER_NAMES:
            continue
        d = PAPERS_DIR / name
        if not d.is_dir():
            continue
        idx_path = d / "index.json"
        if not idx_path.exists():
            continue
        try:
            with open(idx_path) as f:
                idx = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        text_parts: list[str] = [str(idx.get("title", name))]
        abstract = idx.get("abstract")
        if isinstance(abstract, str):
            text_parts.append(abstract)
        elif isinstance(abstract, dict):
            text_parts.append(json.dumps(abstract, ensure_ascii=False))
        for md_candidate in ("README.md", "index.md", "paper.md"):
            md_path = d / md_candidate
            if md_path.exists():
                try:
                    text_parts.append(md_path.read_text(encoding="utf-8")[:8000])
                except OSError:
                    pass
                break
        text = "\n\n".join(text_parts)
        points.append({
            "id": stable_point_id("paper", name),
            "collection": COLLECTION_PAPERS,
            "payload": {
                "slug": name,
                "title": idx.get("title"),
                "doi": idx.get("doi"),
                "regimes": idx.get("regimes", []),
                "status": idx.get("status"),
                "sealed_predictions": idx.get("sealed_predictions", []),
                "path": str(d.relative_to(REPO)),
            },
            "text": text,
        })
    return points


def enumerate_atlas_points() -> list[dict]:
    if not ATLAS_PATH.exists():
        return []
    with open(ATLAS_PATH) as f:
        atlas = json.load(f)

    points: list[dict] = []

    for fw in atlas.get("frameworks", []):
        fid = fw["id"]
        text = f"Framework: {fw.get('name', fid)}. " \
               f"Category: {fw.get('category')}. Role: {fw.get('role')}. " \
               f"Regimes: {', '.join(fw.get('regimes', []))}. " \
               f"Key primitives: {', '.join(fw.get('key_primitives', []))}. " \
               f"{fw.get('notes', '')}"
        points.append({
            "id": stable_point_id("framework", fid),
            "collection": COLLECTION_ATLAS,
            "payload": {"kind": "framework", "framework": fid, **fw},
            "text": text,
        })

    for i, pred in enumerate(atlas.get("predictions", [])):
        key = f"{pred.get('framework')}::{pred.get('phenomenon')}::{pred.get('regime')}::{i}"
        text = f"Prediction: {pred.get('framework')} predicts " \
               f"{pred.get('phenomenon')} = {pred.get('value')} " \
               f"{pred.get('unit', '')} at regime {pred.get('regime')}. " \
               f"{pred.get('note', '')}"
        points.append({
            "id": stable_point_id("prediction", key),
            "collection": COLLECTION_ATLAS,
            "payload": {"kind": "prediction", **pred},
            "text": text,
        })

    for i, rel in enumerate(atlas.get("relations", [])):
        key = f"{rel.get('subject')}::{rel.get('predicate')}::{rel.get('object')}::{i}"
        text = f"Relation: {rel.get('subject')} {rel.get('predicate')} " \
               f"{rel.get('object')}. {rel.get('note', '')}"
        points.append({
            "id": stable_point_id("relation", key),
            "collection": COLLECTION_ATLAS,
            "payload": {"kind": "relation", **rel},
            "text": text,
        })

    return points


def ingest(points: list[dict], apply: bool) -> dict:
    qdrant_url = os.environ.get("QDRANT_URL")
    qdrant_key = os.environ.get("QDRANT_API_KEY")
    provider = os.environ.get("EMBEDDING_PROVIDER", "").lower()

    if not apply:
        return {
            "mode": "dry_run",
            "would_upsert": len(points),
            "qdrant_url_set": bool(qdrant_url),
            "qdrant_api_key_set": bool(qdrant_key),
            "embedding_provider": provider or None,
        }

    if not qdrant_url:
        print("ERROR: --apply requires QDRANT_URL in environment.", file=sys.stderr)
        return {"mode": "apply_blocked", "reason": "QDRANT_URL missing"}
    if not provider:
        print("ERROR: --apply requires EMBEDDING_PROVIDER in environment.", file=sys.stderr)
        return {"mode": "apply_blocked", "reason": "EMBEDDING_PROVIDER missing"}

    try:
        from qdrant_client import QdrantClient  # type: ignore
    except ImportError:
        print("ERROR: qdrant-client not installed. pip install qdrant-client",
              file=sys.stderr)
        return {"mode": "apply_blocked", "reason": "qdrant-client missing"}

    _client = QdrantClient(url=qdrant_url, api_key=qdrant_key)

    # NOTE: embedding + upsert intentionally left unimplemented here to
    # avoid silently pushing data without an explicit embedding-model
    # decision. A follow-up PR should add provider-specific embedder
    # adapters (openai / voyage / local) and collection bootstrap
    # (create_collection with matching vector dim).
    return {
        "mode": "apply_pending_embedder",
        "client_ready": True,
        "points_prepared": len(points),
        "next_step": "Implement embedder for EMBEDDING_PROVIDER and upsert into collections.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", choices=["papers", "atlas", "all"], default="all")
    args = ap.parse_args()

    print("=" * 60)
    print("EFC QDRANT INGEST")
    print("=" * 60)

    points: list[dict] = []
    if args.only in ("papers", "all"):
        paper_points = enumerate_paper_points()
        print(f"Enumerated {len(paper_points)} paper points -> {COLLECTION_PAPERS}")
        points.extend(paper_points)
    if args.only in ("atlas", "all"):
        atlas_points = enumerate_atlas_points()
        print(f"Enumerated {len(atlas_points)} atlas points  -> {COLLECTION_ATLAS}")
        points.extend(atlas_points)

    result = ingest(points, apply=args.apply and not args.dry_run)
    print("\nResult:")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
