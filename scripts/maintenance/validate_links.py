#!/usr/bin/env python3
"""validate_links.py — døde interne og eksterne lenker i de offentlige sidene.

Interne (relative) lenker må peke på filer som finnes i repoet — HARD feil.
Eksterne sjekkes med HEAD (GET-fallback) med tak; 4xx/5xx telles som funn
(ikke harde — eksterne sider har rate-limits og uekte 403-er). Antall
eksterne per kjøring er kapret for å holde CI snill.

Bruk: python3 scripts/maintenance/validate_links.py [--json] [--maks-eksterne N]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROT = Path(__file__).resolve().parents[2]
SIDER = list((ROT / "docs" / "public").glob("*.html")) + [ROT / "docs" / "index.html"]
HREF = re.compile(r'(?:href|src)=["\']([^"\'#]+)["\']')
UA = "hermes-efc-links/1.0 (+supertedai/EFC)"


def _sjekk_ekstern(url: str, tidsfrist: int = 8) -> tuple[str, int | None]:
    try:
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=tidsfrist) as r:
            return url, r.status
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):  # HEAD nektet — prøv GET
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=tidsfrist) as r2:
                    return url, r2.status
            except urllib.error.HTTPError as e2:
                return url, e2.code
            except Exception:
                return url, None
        return url, e.code
    except Exception:
        return url, None


def hoved() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument("--maks-eksterne", type=int, default=25)
    a = p.parse_args()
    harde: list[dict] = []
    funn: list[dict] = []
    eksterne: list[str] = []
    for side in SIDER:
        if not side.is_file():
            harde.append({"type": "missing_page", "msg": str(side)})
            continue
        tekst = side.read_text(encoding="utf-8", errors="replace")
        for m in HREF.finditer(tekst):
            href = m.group(1).strip()
            if href.startswith(("http://", "https://")):
                eksterne.append(href)
                continue
            if href.startswith(("mailto:", "javascript:", "#", "data:")):
                continue
            sti = (side.parent / urllib.parse.unquote(href.split("?")[0])).resolve()
            if not sti.is_file():
                harde.append({"type": "broken_internal",
                              "side": str(side.relative_to(ROT)), "href": href})
    sett = sorted(set(eksterne))
    for url in sett[:a.maks_eksterne]:
        _u, status = _sjekk_ekstern(url)
        if status is None:
            funn.append({"type": "external_unreachable", "url": url})
        elif status >= 400:
            funn.append({"type": "external_broken", "url": url, "status": status})
    if a.json:
        print(json.dumps({"harde": harde, "funn": funn,
                          "eksterne_sjekket": min(len(sett), a.maks_eksterne),
                          "eksterne_totalt": len(sett)}, ensure_ascii=False, indent=1))
    else:
        print(f"lenker: {len(harde)} harde (interne døde), {len(funn)} eksterne funn "
              f"({min(len(sett), a.maks_eksterne)} av {len(sett)} sjekket)")
        for f in harde[:15]:
            print("  HARDT:", f)
        for f in funn[:10]:
            print("  FUNN:", f)
    return 1 if harde else 0


if __name__ == "__main__":
    raise SystemExit(hoved())
