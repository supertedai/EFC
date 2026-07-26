#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EFC PAPER BUILDER v5.0
======================

Stabile fix:
- Ren LaTeX-stripper (fjerner ALLE \commands og commands)
- 3-trinns DOI-henting:
    1. metadata.json
    2. jsonld
    3. Figshare API
- DOI-injeksjon i PDF metadata
- Oppdaterer README, metadata, index, jsonld
- Idempotent og trygg
"""

import os
import re
import json
import subprocess
import requests
from datetime import date


# --------------------------------------------------------------
# Konfig
# --------------------------------------------------------------

ROOT = os.path.dirname(os.path.dirname(__file__))
DOCS_ROOT = os.path.join(ROOT, "docs", "papers", "efc")

GITHUB_REPO_RAW_BASE = (
    "https://raw.githubusercontent.com/supertedai/EFC/main"
)

FIGSHARE_API = "https://api.figshare.com/v2"

DOMAIN_DEFAULT = "META-systems"
DOMAIN_BY_SUBDIR = {}   # utvid ved behov


# --------------------------------------------------------------
# Shell / PDF build
# --------------------------------------------------------------

def run(cmd, cwd=None):
    res = subprocess.run(
        cmd, shell=True, cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    print(res.stdout)
    if res.returncode != 0:
        raise RuntimeError(f"[ERROR] Failed cmd: {cmd}")


def latex_build(tex_path):
    tex_dir = os.path.dirname(tex_path)
    tex_file = os.path.basename(tex_path)

    run(f"pdflatex -interaction=nonstopmode {tex_file}", cwd=tex_dir)
    run(f"pdflatex -interaction=nonstopmode {tex_file}", cwd=tex_dir)

    pdf = tex_path.replace(".tex", ".pdf")
    if not os.path.exists(pdf):
        raise RuntimeError(f"[ERROR] PDF missing: {pdf}")

    return pdf


# --------------------------------------------------------------
# LaTeX stripper (final cut)
# --------------------------------------------------------------

def strip_latex(text):
    if not text:
        return text

    # Fanger ALLE varianter: \cmd{...} og cmd{...}
    # Eksempel matcher:
    #   \textbf{Hello}
    #   textbf{Hello}
    #   \Large{Hello}
    #   Large{Hello}
    text = re.sub(r"(\\?[A-Za-z]+)\{([^{}]*)\}", r"\2", text)

    # Fjern backslashes
    text = text.replace("\\", "")

    # Rydd whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# --------------------------------------------------------------
# Ekstraher metadata
# --------------------------------------------------------------

def extract_meta(tex_path):
    with open(tex_path, "r", encoding="utf-8") as f:
        content = f.read()

    def match(cmd):
        m = re.search(rf"\\{cmd}\{{(.*?)\}}", content, re.DOTALL)
        return m.group(1).strip() if m else ""

    title_raw = match("title")
    title = strip_latex(title_raw)
    if not title:
        title = os.path.splitext(os.path.basename(tex_path))[0]

    kw_raw = match("keywords")
    keywords = []
    if kw_raw:
        for k in re.split(r"[;,]", kw_raw):
            if k.strip():
                keywords.append(strip_latex(k.strip()))

    m_abs = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", content, re.DOTALL)
    abstract = strip_latex(m_abs.group(1)) if m_abs else ""

    return {
        "title": title,
        "keywords": keywords,
        "abstract": abstract
    }


# --------------------------------------------------------------
# DOI-resolver (tre-trinns)
# --------------------------------------------------------------

def doi_from_metadata(dir):
    path = os.path.join(dir, "metadata.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            return d.get("doi")
        except:
            pass
    return None


def doi_from_jsonld(dir, slug):
    path = os.path.join(dir, f"{slug}.jsonld")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            candidate = d.get("identifier")
            if candidate and ("10." in candidate or candidate.startswith("https://doi.org/")):
                return candidate
        except:
            pass
    return None


def doi_from_figshare(title):
    try:
        r = requests.get(
            f"{FIGSHARE_API}/articles/search",
            params={"search_for": title},
            timeout=6
        )
        r.raise_for_status()

        for item in r.json():
            if item.get("title", "").strip().lower() == title.lower().strip():
                if item.get("doi"):
                    return item["doi"]

    except Exception as e:
        print(f"[warning] Figshare lookup failed: {e}")

    return None


def resolve_doi(dir, slug, title):
    d1 = doi_from_metadata(dir)
    if d1:
        return d1

    d2 = doi_from_jsonld(dir, slug)
    if d2:
        return d2

    d3 = doi_from_figshare(title)
    if d3:
        return d3

    return None


# --------------------------------------------------------------
# DOI → injiseres i PDF (LaTeX preamble)
# --------------------------------------------------------------

def inject_doi_into_tex(tex_path, doi):
    if not doi:
        return

    with open(tex_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new = []
    injected = False

    for line in lines:
        new.append(line)
        if not injected and line.strip().startswith("\\documentclass"):
            new.append("\\usepackage{hyperref}\n")
            new.append(f"\\newcommand{{\\paperdoi}}{{{doi}}}\n")
            new.append("\\hypersetup{pdfinfo={DOI={\\paperdoi}}}\n")
            injected = True

    with open(tex_path, "w", encoding="utf-8") as f:
        f.writelines(new)


# --------------------------------------------------------------
# Domain
# --------------------------------------------------------------

def detect_domain(dir, meta):
    last = os.path.basename(dir)
    for key, domain in DOMAIN_BY_SUBDIR.items():
        if key in last or key in meta["title"]:
            return domain
    return DOMAIN_DEFAULT


def pdf_url(slug):
    return f"{GITHUB_REPO_RAW_BASE}/docs/papers/efc/{slug}/{slug}.pdf"


# --------------------------------------------------------------
# Writers
# --------------------------------------------------------------

def write_readme(dir, slug, meta, domain, doi):
    year = date.today().year
    dline = f"DOI: {doi}" if doi else "DOI: pending"
    kw = ", ".join(meta["keywords"]) if meta["keywords"] else ""

    out = f"""# {meta["title"]}

This directory contains the paper **“{meta["title"]}”**, part of the EFC series.

{meta["abstract"][:120]}...

---

## Context in the EFC framework
- Framework: Energy-Flow Cosmology (EFC)
- Domain: {domain}
- Role: Links entropic structure, information flow and observable cosmological behaviour.
- {dline}

---

## Abstract
{meta["abstract"]}

---

## Keywords
{kw}

---

## Files
- {slug}.tex
- {slug}.pdf
- {slug}.jsonld
- metadata.json
- index.json
- citations.bib

---

## Citation
Magnusson, M. ({year}). *{meta["title"]}*.  
{dline}  
GitHub: docs/papers/efc/{slug}/{slug}.pdf
"""

    with open(os.path.join(dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(out)


def write_metadata(dir, slug, meta, domain, doi):
    now = str(date.today())
    data = {
        "id": slug,
        "slug": slug,
        "title": meta["title"],
        "description": meta["abstract"][:500],
        "domain": domain,
        "keywords": meta["keywords"],
        "version": "1.0.0",
        "authors": [{
            "name": "Morten Magnusson",
            "orcid": "https://orcid.org/0009-0002-4860-5095"
        }],
        "files": {
            "pdf": f"{slug}.pdf",
            "tex": f"{slug}.tex",
            "readme": "README.md",
            "jsonld": f"{slug}.jsonld"
        },
        "created": now,
        "updated": now
    }
    if doi: data["doi"] = doi

    with open(os.path.join(dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def write_index(dir, slug, meta, domain, doi):
    now = str(date.today())
    data = {
        "id": slug,
        "slug": slug,
        "title": meta["title"],
        "path": f"docs/papers/efc/{slug}",
        "pdf": f"{slug}.pdf",
        "tex": f"{slug}.tex",
        "readme": "README.md",
        "layer": "docs",
        "domain": domain,
        "type": "paper",
        "version": "1.0.0",
        "keywords": meta["keywords"],
        "summary": meta["abstract"][:300],
        "created": now,
        "updated": now
    }
    if doi: data["doi"] = doi

    with open(os.path.join(dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def write_jsonld(dir, slug, meta, domain, doi):
    data = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "identifier": doi or slug,
        "name": meta["title"],
        "description": meta["abstract"],
        "version": "1.0.0",
        "author": [{
            "@type": "Person",
            "name": "Morten Magnusson",
            "identifier": "https://orcid.org/0009-0002-4860-5095"
        }],
        "keywords": meta["keywords"],
        "url": pdf_url(slug),
        "isPartOf": {"@type": "CreativeWorkSeries", "name": "EFC Papers"},
        "about": {"@type": "Thing", "name": domain}
    }

    with open(os.path.join(dir, f"{slug}.jsonld"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def ensure_citations(dir):
    p = os.path.join(dir, "citations.bib")
    if not os.path.exists(p):
        with open(p, "w", encoding="utf-8") as f:
            f.write("% bibliography\n")


# --------------------------------------------------------------
# Pipeline
# --------------------------------------------------------------

def process(tex_path):
    tex_path = os.path.abspath(tex_path)
    dir = os.path.dirname(tex_path)
    slug = os.path.splitext(os.path.basename(tex_path))[0]

    print(f"[builder] Processing {slug}")

    meta = extract_meta(tex_path)
    domain = detect_domain(dir, meta)

    doi = resolve_doi(dir, slug, meta["title"])

    inject_doi_into_tex(tex_path, doi)

    latex_build(tex_path)

    write_readme(dir, slug, meta, domain, doi)
    write_metadata(dir, slug, meta, domain, doi)
    write_index(dir, slug, meta, domain, doi)
    write_jsonld(dir, slug, meta, domain, doi)
    ensure_citations(dir)

    print(f"[builder] DONE — {slug} (DOI={doi or 'pending'})")


def main():
    print(f"[builder] Scanning {DOCS_ROOT}")
    for root, dirs, files in os.walk(DOCS_ROOT):
        for f in files:
            if f.endswith(".tex"):
                process(os.path.join(root, f))


if __name__ == "__main__":
    main()
