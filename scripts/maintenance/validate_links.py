#!/usr/bin/env python3
"""validate_links.py — dead internal and external links in the public surfaces.

THE RULE (declared here, not only in the card that built it)
------------------------------------------------------------
The surfaces that are read:

  * HTML: ``docs/public/*.html`` and ``docs/index.html``.
  * Markdown: every ``wiki/**/*.md`` page. The wiki is a reader-facing
    explanation surface of this repository (it is what a visitor is sent to
    first), so a dead internal link there is the same reader-facing defect as
    a dead link on a public page.

An INTERNAL (relative) link is a HARD error (exit 1) when its target does not
exist in the tree. What counts as existing differs by surface, and the
difference is deliberate:

  * HTML: the target must be a FILE. A page that links to a directory without
    an index is a dead link for the reader.
  * Markdown: the target may be a FILE **or a DIRECTORY** — wiki pages link to
    directories on purpose (``../theory/formal/``, ``../methodology/``), and a
    directory that exists is a usable target on a code host.

Fragment-only links (``#section``), ``mailto:``, ``tel:``, ``javascript:`` and
``data:`` do not name a path in the tree and are skipped. Query strings and
fragments on an otherwise internal link are stripped before the check.

Supported Markdown syntax: inline links and images ``[text](path)`` and
reference definitions ``[id]: path``. Both forms are read, so a page that uses
reference-style links is not silently unmeasured. Fenced code blocks and inline
code spans are NOT read: a page may document link syntax without the
documentation becoming a link.

An EXTERNAL link (http/https) is a FINDING, never hard: remote sites rate-limit
and answer 403 to HEAD. The number of external ones per run is capped to keep
CI friendly.

Usage: python3 scripts/maintenance/validate_links.py [--json] [--maks-eksterne N]
Exit: 0 = no hard findings, 1 = at least one dead internal link.
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
# The Markdown surface. Sorted so the report is stable between runs; a missing
# wiki/ yields an empty list (Path.glob does not raise on a missing directory).
WIKI_SIDER = sorted((ROT / "wiki").glob("**/*.md"))
HREF = re.compile(r'(?:href|src)=["\']([^"\'#]+)["\']')
MD_LENKE = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
MD_DEF = re.compile(r"^ {0,3}\[[^\]]+\]:\s*(\S+)", re.MULTILINE)
# A fence (``` or ~~~) and an inline code span. What is shown as code is not a
# link, so a page may document link syntax without being failed by it.
MD_GJERDE = re.compile(r"^ {0,3}(`{3,}|~{3,})[^\n]*\n.*?^ {0,3}\1[^\n]*$",
                       re.MULTILINE | re.DOTALL)
MD_KODE = re.compile(r"`[^`\n]*`")
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


def _uten_kode(tekst: str) -> str:
    """The page with fenced blocks and inline code spans removed.

    What is shown as code is not a link. Removing it before the scan keeps a
    page that documents link syntax from failing on its own example.
    """
    tekst = MD_GJERDE.sub("", tekst)
    return MD_KODE.sub("", tekst)


def _hrefs(tekst: str, markdown: bool) -> list[str]:
    """The raw link targets in one page. Both Markdown forms are read, so a
    reference-style link is measured like an inline one."""
    if not markdown:
        return [m.group(1) for m in HREF.finditer(tekst)]
    tekst = _uten_kode(tekst)
    return [m.group(1) for m in MD_LENKE.finditer(tekst)] + \
           [m.group(1) for m in MD_DEF.finditer(tekst)]


def _rel(side: Path) -> str:
    """Path as it is reported. A page outside the repo root (a fixture tree in
    the tests) is reported by its own path instead of raising: the finding is
    the dead link, not where the tree happens to sit."""
    try:
        return side.relative_to(ROT).as_posix()
    except ValueError:
        return side.as_posix()


def sjekk_side(side: Path, tekst: str, markdown: bool = False) -> tuple[list[dict], list[str]]:
    """Split one page's links into HARD findings and external targets.

    The surface decides what "exists" (see the module docstring): a FILE for
    HTML, a FILE or a DIRECTORY for Markdown. Kept as a function so the rule is
    measured by tests instead of only used by the CLI.
    """
    harde: list[dict] = []
    eksterne: list[str] = []
    for href in _hrefs(tekst, markdown):
        href = href.strip()
        if href.startswith(("http://", "https://")):
            eksterne.append(href)
            continue
        if href.startswith(("mailto:", "javascript:", "tel:", "#", "data:")):
            continue
        sti = (side.parent / urllib.parse.unquote(
            href.split("?")[0].split("#")[0])).resolve()
        finnes = (sti.is_file() or sti.is_dir()) if markdown else sti.is_file()
        if not finnes:
            harde.append({"type": "broken_internal",
                          "side": _rel(side), "href": href})
    return harde, eksterne


def hoved() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument("--maks-eksterne", type=int, default=25)
    a = p.parse_args()
    harde: list[dict] = []
    funn: list[dict] = []
    eksterne: list[str] = []
    sider = [(side, False) for side in SIDER] + [(side, True) for side in WIKI_SIDER]
    for side, markdown in sider:
        if not side.is_file():
            harde.append({"type": "missing_page", "msg": str(side)})
            continue
        tekst = side.read_text(encoding="utf-8", errors="replace")
        side_harde, side_eksterne = sjekk_side(side, tekst, markdown)
        harde.extend(side_harde)
        eksterne.extend(side_eksterne)
    sett = sorted(set(eksterne))
    for url in sett[:a.maks_eksterne]:
        _u, status = _sjekk_ekstern(url)
        if status is None:
            funn.append({"type": "external_unreachable", "url": url})
        elif status >= 400:
            funn.append({"type": "external_broken", "url": url, "status": status})
    if a.json:
        print(json.dumps({"harde": harde, "funn": funn,
                          "sider_sjekket": len(SIDER), "markdown_sjekket": len(WIKI_SIDER),
                          "eksterne_sjekket": min(len(sett), a.maks_eksterne),
                          "eksterne_totalt": len(sett)}, ensure_ascii=False, indent=1))
    else:
        print(f"links: {len(harde)} hard (internal dead), {len(funn)} external findings "
              f"({min(len(sett), a.maks_eksterne)} of {len(sett)} checked; "
              f"{len(SIDER)} HTML + {len(WIKI_SIDER)} Markdown pages)")
        for f in harde[:15]:
            print("  HARD:", f)
        for f in funn[:10]:
            print("  FOUND:", f)
    return 1 if harde else 0


if __name__ == "__main__":
    raise SystemExit(hoved())
