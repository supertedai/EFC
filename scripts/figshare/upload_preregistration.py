#!/usr/bin/env python3
"""Upload the EFC E_G SO x Euclid pre-registration to Figshare.

Reads ``figshare/preregistration-eg-so-euclid-2026-04-15/metadata.json``,
creates a Figshare article via API v2, uploads the listed files, publishes
(which assigns a DOI), then writes the DOI/article_id/url back into
metadata.json and appends an entry to ``figshare/doi-map.json``.

Idempotent: if metadata.json already has a non-empty ``doi`` field the
script exits successfully without re-publishing.

Environment:
    FIGSHARE_TOKEN  Personal token with write scope on articles.
                    (In the GitHub Actions workflow this is injected from
                    ``secrets.API_FIGSHARE_EFC``.)
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import requests

BASE_URL = "https://api.figshare.com/v2"
REPO_ROOT = Path(__file__).resolve().parents[2]
ARTICLE_DIR = REPO_ROOT / "figshare" / "preregistration-eg-so-euclid-2026-04-15"
METADATA_PATH = ARTICLE_DIR / "metadata.json"
DOI_MAP_PATH = REPO_ROOT / "figshare" / "doi-map.json"

TOKEN = os.environ.get("FIGSHARE_TOKEN") or os.environ.get("API_FIGSHARE_EFC")
if not TOKEN:
    print("ERROR: FIGSHARE_TOKEN / API_FIGSHARE_EFC not set", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/json",
}


def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def api(method: str, path: str, **kwargs) -> dict | list:
    url = path if path.startswith("http") else BASE_URL + path
    resp = requests.request(method, url, headers=HEADERS, timeout=60, **kwargs)
    if not resp.ok:
        die(f"{method} {url} -> {resp.status_code}: {resp.text}")
    if not resp.content:
        return {}
    try:
        return resp.json()
    except ValueError:
        return {}


def md5sum(path: Path) -> tuple[str, int]:
    h = hashlib.md5()
    size = 0
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size


def upload_file(article_id: int, fpath: Path) -> None:
    checksum, size = md5sum(fpath)
    print(f"  initiating upload: {fpath.name} ({size} bytes, md5={checksum})")
    init = api(
        "POST",
        f"/account/articles/{article_id}/files",
        json={"name": fpath.name, "md5": checksum, "size": size},
    )
    file_id = int(init["location"].rsplit("/", 1)[-1])
    finfo = api("GET", f"/account/articles/{article_id}/files/{file_id}")
    upload_url = finfo["upload_url"]

    parts_resp = api("GET", upload_url)
    parts = parts_resp["parts"]
    with fpath.open("rb") as fh:
        for part in parts:
            start = part["startOffset"]
            end = part["endOffset"]
            fh.seek(start)
            chunk = fh.read(end - start + 1)
            r = requests.put(
                f"{upload_url}/{part['partNo']}",
                headers=HEADERS,
                data=chunk,
                timeout=120,
            )
            if not r.ok:
                die(f"part {part['partNo']} upload failed: {r.status_code} {r.text}")
            print(f"    part {part['partNo']}/{len(parts)} uploaded")
    api("POST", f"/account/articles/{article_id}/files/{file_id}")
    print(f"  file complete: {fpath.name} (id={file_id})")


def main() -> None:
    meta = json.loads(METADATA_PATH.read_text())

    if meta.get("doi"):
        print(f"Already published: DOI={meta['doi']} — nothing to do.")
        return

    # 1. Create article
    article_payload = {
        "title": meta["title"],
        "description": meta["description"],
        "defined_type": meta.get("defined_type", "preprint"),
        "license": meta.get("license", 1),
        "keywords": meta.get("keywords", []),
        "authors": meta["authors"],
    }
    if meta.get("categories_by_source_id"):
        article_payload["categories_by_source_id"] = meta["categories_by_source_id"]
    if meta.get("categories"):
        article_payload["categories"] = meta["categories"]

    print(f"Creating article: {meta['title']!r}")
    created = api("POST", "/account/articles", json=article_payload)
    article_id = int(created["location"].rsplit("/", 1)[-1])
    print(f"  article_id={article_id}")

    # 2. Upload each file that exists on disk
    for fname in meta.get("files", []):
        fpath = ARTICLE_DIR / fname
        if not fpath.exists():
            print(f"  skipping {fname}: not present on disk")
            continue
        upload_file(article_id, fpath)

    # 3. Publish (assigns DOI)
    print("Publishing article…")
    api("POST", f"/account/articles/{article_id}/publish")

    published = api("GET", f"/account/articles/{article_id}")
    doi = published.get("doi") or ""
    url = published.get("url_public_html") or f"https://figshare.com/articles/preprint/_/{article_id}"
    print(f"Published: DOI={doi} URL={url}")

    # 4. Write DOI back into metadata.json
    meta["doi"] = doi
    meta["article_id"] = article_id
    meta["url"] = url
    meta["published"] = published.get("published_date")
    METADATA_PATH.write_text(json.dumps(meta, indent=2) + "\n")
    print(f"Updated {METADATA_PATH.relative_to(REPO_ROOT)}")

    # 5. Append entry to figshare/doi-map.json
    if DOI_MAP_PATH.exists() and DOI_MAP_PATH.stat().st_size:
        try:
            doi_map = json.loads(DOI_MAP_PATH.read_text())
        except json.JSONDecodeError:
            doi_map = {}
    else:
        doi_map = {}
    if doi:
        doi_map[doi] = {
            "figshare_id": article_id,
            "title": meta["title"],
            "path": str(ARTICLE_DIR.relative_to(REPO_ROOT)),
            "url": f"https://doi.org/{doi}",
        }
        DOI_MAP_PATH.write_text(json.dumps(doi_map, indent=2) + "\n")
        print(f"Updated {DOI_MAP_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
