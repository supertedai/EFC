#!/usr/bin/env python3
"""validate_links.py — dead internal and external links in the public pages.

Internal (relative) links must point at files that exist in the repo — HARD error.
External ones are checked with HEAD (GET fallback) with a ceiling; 4xx/5xx count
as findings (not hard — external sites have rate limits and false 403s). The number
of external ones per run is capped to keep CI friendly.

Usage: python3 scripts/maintenance/validate_links.py [--json] [--maks-eksterne N]
"""
from __future__ import annotations

import argparse
import json
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from ipaddress import ip_address
from pathlib import Path

ROT = Path(__file__).resolve().parents[2]
SIDER = list((ROT / "docs" / "public").glob("*.html")) + [ROT / "docs" / "index.html"]
HREF = re.compile(r'(?:href|src)=["\']([^"\'#]+)["\']')
UA = "hermes-efc-links/1.0 (+supertedai/EFC)"


def _safe_host(url: str) -> bool:
    """SSRF guard: only http/https, no credentials, and ALL resolved
    IPs must be globally routable (not loopback/private/link-local/
    reserved/multicast/metadata). The URLs come from the repo's own
    HTML files — and that is precisely why they are attacker-controlled in a PR."""
    p = urllib.parse.urlsplit(url)
    if p.scheme not in ("http", "https"):
        return False
    if p.username or p.password:
        return False
    host = p.hostname
    if not host:
        return False
    if host == "169.254.169.254":
        return False
    try:
        ip = ip_address(host)  # is it an IP literal?
    except ValueError:
        try:
            ip = None
            infos = socket.getaddrinfo(host, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
            for info in infos:
                adr = ip_address(info[4][0])
                if not (adr.is_global and not adr.is_reserved and not adr.is_multicast):
                    return False
        except OSError:
            return False
        return True
    return ip.is_global and not ip.is_reserved and not ip.is_multicast


class _SikkerHandler(urllib.request.HTTPRedirectHandler):
    """Follows at most 3 redirects and re-validates EVERY new host."""
    MAKS_HOPP = 3

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not hasattr(req, "_ssrf_hopp"):
            req._ssrf_hopp = 0
        if req._ssrf_hopp >= self.MAKS_HOPP:
            raise urllib.error.HTTPError(req.full_url, code, "too many redirects",
                                         headers, fp)
        if not _safe_host(newurl):
            raise urllib.error.HTTPError(req.full_url, code, "unsafe redirect destination",
                                         headers, fp)
        req._ssrf_hopp += 1
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _aapner():
    """Opener WITHOUT proxy (HTTP_PROXY/HTTPS_PROXY can bypass the validated
    network path) and with an SSRF-validating redirect handler."""
    return urllib.request.build_opener(_SikkerHandler(),
                                       urllib.request.ProxyHandler({}))


def _sjekk_ekstern(url: str, tidsfrist: int = 8) -> tuple[str, int | None]:
    if not _safe_host(url):
        return url, -1  # blocked by the SSRF guard
    try:
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": UA})
        with _aapner().open(req, timeout=tidsfrist) as r:
            return url, r.status
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):  # HEAD refused — try GET
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with _aapner().open(req, timeout=tidsfrist) as r2:
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
        print(f"links: {len(harde)} hard (internal dead), {len(funn)} external findings "
              f"({min(len(sett), a.maks_eksterne)} of {len(sett)} checked)")
        for f in harde[:15]:
            print("  HARD:", f)
        for f in funn[:10]:
            print("  FOUND:", f)
    return 1 if harde else 0


if __name__ == "__main__":
    raise SystemExit(hoved())
