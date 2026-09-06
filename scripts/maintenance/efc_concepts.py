#!/usr/bin/env python3
"""
EFC concept registry — one source (SKOS), two generated views, checked in CI (C11)
=================================================================================

Source:     docs/concepts.jsonld          SKOS ConceptScheme, hand-maintained
Generated:  schema/concepts.json          schema.org DefinedTermSet view
            api/concept-index.json        schema.org ItemList view (the index)

Why this exists (measured 2026-09-05 against origin/main a64b9627): the
concept layer was three lists that disagreed, and one of them was dead.
api/concept-index.json named the five core concepts and pointed all five at
files in api/v1/concept/ that did not exist; that directory held four
ARTICLES. schema/concepts.json was a DefinedTermSet whose every DefinedTerm
was a publication, with identifier "" and url "" and HTML in description;
api/v1/concepts.json was a byte-identical copy, api/v1/terms.json a third
list whose ids were energyflow-cosmology.com paths that 404. No termCode, no inDefinedTermSet,
no alternateName, no source.

What the registry asserts, and what it does not
-----------------------------------------------
The registry is SKOS (prefLabel/altLabel/notation, broader, inScheme,
definition, scopeNote) with dcterms:source for provenance — not a tenth
private JSON form. Concept IRIs live in the efc: namespace
(https://supertedai.github.io/EFC/ontology#, C9), so identity comes from the
vocabulary and MEANING from here; `efc_ontology.py --apply` lists every
concept as a skos:Concept once it is used.

Every skos:definition in the registry is a VERBATIM sentence from a document
in this repository (a paper's own abstract), and carries the document as
dcterms:source. The registry does not paraphrase and does not author
definitions (EFC ADR-024: plumbing, never commentary). Where no defining
sentence exists in the tree, the concept carries sources and a scopeNote
saying so — an absent definition is a measurement, not a gap to fill by hand.

DOIs are dcterms:source, not sameAs: a concept is not identical to the paper
that introduces it.

Modes
-----
  --check   (default) the registry parses; @ids are unique; every concept
            has an efc: IRI, an efc:entityType from a closed list (a
            publication, dataset, artifact, person or organization is refused
            outright — both errors review caught here were that category
            mistake), a prefLabel, a notation, inScheme, and at least
            one dcterms:source that is a doi.org URL the tree PUBLISHES
            (figshare/doi-map.json papers, top-level doi of a paper's
            index.json — an invented or merely cited DOI fails); every
            skos:definition names efc:definitionQuotedFrom, a file inside
            this tree (resolved — no ../ escape) WITH a #L<n> or #L<a>-L<b>
            line fragment, and is a non-empty VERBATIM substring of exactly
            those lines — "somewhere in the file" is not evidence in a file
            of thousands of lines, and the fragment is a GitHub anchor, so
            the identifier is the clickable evidence. An optional
            efc:quoteSha256 must be the SHA-256 of the quote if present.
            (The ADR-024 guard lives here, in the gate, not only in the
            tests.) broader targets and hasTopConcept members
            exist, a concept with a broader is not a top concept, and only
            skos:Concept nodes carry topConceptOf/inScheme/broader; the two generated views are
            byte-identical to what --apply would write; the dead copies
            (api/v1/concepts.json, api/v1/terms.json) are absent; and every
            concept IRI is declared in docs/ontology.jsonld (C9); and a
            concept with no definition carries a skos:scopeNote saying what
            was measured — an absent definition is a finding, not a blank.
            Exit 1 on any deviation. Runs in CI (efc-verify.yml).
            Not mechanically guarded: the TEXT of a scopeNote. A reader is
            the only gate for a note that smuggles a definition, and whether
            the quoted file is a DEFINING document rather than one that
            merely uses the term.
  --apply   regenerate the two views from the registry. Deterministic.
"""
from __future__ import annotations

import hashlib
import json
import sys
from urllib.parse import unquote
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = "docs/concepts.jsonld"
VIEW_TERMSET = "schema/concepts.json"
VIEW_INDEX = "api/concept-index.json"
DEAD = ["api/v1/concepts.json", "api/v1/terms.json"]

# What a registered entry IS. Closed on purpose: both errors review caught in
# this registry were a category mistake — schema/concepts.json was a
# DefinedTermSet whose every term was a PUBLICATION, and a draft of efc:HME
# quoted a DATASET row as its definition.
#   `measurement_principle` is not on the card's list; RCMP is the case that
#   needs it and neither `method` nor `concept` says what it is.
ENTITY_TYPES = (
    "concept", "term", "method", "measurement_principle", "module",
    "observable", "proxy", "parameter", "regime", "boundary_condition",
    "architecture", "hypothesis", "claim", "workflow",
)
# The five kinds that are not concepts at all. Refused with their own message
# and nothing else: no attestation makes a publication a concept, so the gate
# must not suggest one.
NOT_A_CONCEPT = ("publication", "dataset", "artifact", "person", "organization")
ONTOLOGY = "docs/ontology.jsonld"
NS = "https://supertedai.github.io/EFC/ontology#"
SCHEME_IRI = "https://supertedai.github.io/EFC/concepts.jsonld"


def _load(root: Path, rel: str, problems: list[str]):
    try:
        with open(root / rel, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError) as e:
        problems.append(f"{rel}: unreadable — {e}")
        return None


def _lit(v) -> str:
    """A JSON-LD literal (plain string or {"@value": ...}) as text."""
    if isinstance(v, dict):
        return str(v.get("@value", ""))
    return "" if v is None else str(v)


def _list(v) -> list:
    return v if isinstance(v, list) else ([] if v is None else [v])


def _ids(v) -> list[str]:
    return [x["@id"] if isinstance(x, dict) else str(x) for x in _list(v)]


def iri(local_or_iri: str) -> str:
    return NS + local_or_iri[4:] if local_or_iri.startswith("efc:") else local_or_iri


GH = "https://github.com/supertedai/EFC/blob/main/"
FRAGMENT_RE = __import__("re").compile(r"^(?P<path>[^#]+)#L(?P<start>\d+)(?:-L(?P<end>\d+))?$")
DOI_RE = __import__("re").compile(r"10\.\d{4,9}/[A-Za-z0-9._;()/:\-]+")


def known_dois(root: Path) -> set[str]:
    """DOIs the tree itself PUBLISHES: every `doi` in figshare/doi-map.json's
    papers and the top-level `doi` of each paper's index.json. Not every
    DOI-shaped string in those files — reference lists cite external works
    (review finding: 12 of 187 were cited, not published). A dcterms:source
    DOI outside this set is invented or borrowed."""
    out: set[str] = set()
    try:
        for paper in json.loads((root / "figshare" / "doi-map.json").read_text(encoding="utf-8")).get("papers", []):
            if isinstance(paper, dict) and paper.get("doi"):
                out.add(str(paper["doi"]))
    except (OSError, ValueError):
        pass
    for p in sorted((root / "docs" / "papers" / "efc").glob("*/index.json")):
        try:
            doi = json.loads(p.read_text(encoding="utf-8")).get("doi")
        except (OSError, ValueError, AttributeError):
            continue
        if isinstance(doi, str) and doi:
            out.add(doi.replace("https://doi.org/", ""))
    return out


def concepts(registry: dict) -> list[dict]:
    return [n for n in registry.get("@graph", []) if "skos:Concept" in _list(n.get("@type"))]


def render_termset(registry: dict) -> str:
    terms = []
    for c in concepts(registry):
        t = {
            "@type": "DefinedTerm",
            "@id": iri(c["@id"]),
            "identifier": iri(c["@id"]),
            "url": iri(c["@id"]),
            "name": _lit(c.get("skos:prefLabel")),
            "termCode": _lit(c.get("skos:notation")),
            "alternateName": [_lit(a) for a in _list(c.get("skos:altLabel"))],
            "inDefinedTermSet": SCHEME_IRI,
            "additionalProperty": [
                {"@type": "PropertyValue", "name": k, "value": v}
                for k, v in (("entityType", _lit(c.get("efc:entityType"))),
                             ("definition_status", "explicit" if c.get("skos:definition") else "gap"))
                if v
            ],
        }
        if c.get("skos:definition"):
            t["description"] = _lit(c["skos:definition"])
        t["citation"] = [s for s in _ids(c.get("dcterms:source")) if s.startswith("https://doi.org/")]
        terms.append(t)
    doc = {
        "@context": "https://schema.org",
        "@type": "DefinedTermSet",
        "@id": SCHEME_IRI,
        "name": "Energy-Flow Cosmology (EFC) — core concepts",
        "description": f"schema.org view of the SKOS registry at {SCHEME_IRI}; generated by scripts/maintenance/efc_concepts.py — edit the registry, not this file.",
        "hasDefinedTerm": terms,
    }
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def render_index(registry: dict) -> str:
    items = []
    for n, c in enumerate(concepts(registry), 1):
        label = _lit(c.get("skos:prefLabel"))
        code = _lit(c.get("skos:notation"))
        items.append({
            "@type": "ListItem",
            "position": n,
            "item": {
                "@type": "DefinedTerm",
                "@id": iri(c["@id"]),
                "name": f"{label} ({code})" if code and code != label else label,
                "termCode": code,
                "url": iri(c["@id"]),
                "inDefinedTermSet": SCHEME_IRI,
            },
        })
    doc = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "@id": "https://supertedai.github.io/EFC/api/concept-index.json",
        "name": "Energy-Flow Cosmology (EFC) – Concept Index",
        "description": f"The five core EFC concepts; each item resolves to its IRI in the efc: vocabulary and is defined in the SKOS registry at {SCHEME_IRI}. Generated by scripts/maintenance/efc_concepts.py. The @id of this document is an identifier under the project authority, not a served URL (the Pages source is docs/) — see t_141136b1.",
        "numberOfItems": len(items),
        "itemListElement": items,
    }
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def check(root: Path = ROOT) -> list[str]:
    problems: list[str] = []
    reg = _load(root, REGISTRY, problems)
    if reg is None:
        return problems
    cs = concepts(reg)
    if not cs:
        problems.append(f"{REGISTRY}: no skos:Concept in @graph")
    schemes = [n for n in reg.get("@graph", []) if "skos:ConceptScheme" in _list(n.get("@type"))]
    if len(schemes) != 1 or schemes[0].get("@id") != SCHEME_IRI:
        problems.append(f"{REGISTRY}: expected exactly one skos:ConceptScheme with @id {SCHEME_IRI}")
    ont = _load(root, ONTOLOGY, problems)
    declared = {n.get("@id") for n in (ont or {}).get("@graph", [])}
    ids = [n.get("@id") for n in reg.get("@graph", [])]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        problems.append(f"{REGISTRY}: duplicate @id {dup!r}")
    for n in reg.get("@graph", []):
        if "skos:Concept" not in _list(n.get("@type")):
            for k in ("skos:topConceptOf", "skos:inScheme", "skos:broader"):
                if k in n:
                    problems.append(f"{REGISTRY}: {n.get('@id')}: {k} on a node that is not a skos:Concept (SKOS S7–S9)")
    cids = {c.get("@id") for c in cs}
    dois = known_dois(root)
    for c in cs:
        cid = c.get("@id", "")
        if not cid.startswith("efc:"):
            problems.append(f"{REGISTRY}: concept {cid!r} is not in the efc: namespace")
        if not _lit(c.get("skos:prefLabel")):
            problems.append(f"{REGISTRY}: {cid}: no skos:prefLabel")
        if not _lit(c.get("skos:notation")):
            problems.append(f"{REGISTRY}: {cid}: no skos:notation")
        et = _lit(c.get("efc:entityType"))
        if et in NOT_A_CONCEPT:
            problems.append(f"{REGISTRY}: {cid}: efc:entityType {et!r} is not a concept and cannot be registered here")
            continue
        if not et:
            problems.append(f"{REGISTRY}: {cid}: no efc:entityType — pick one of {', '.join(ENTITY_TYPES)}")
        elif et not in ENTITY_TYPES:
            problems.append(f"{REGISTRY}: {cid}: efc:entityType {et!r} is not in the closed list ({', '.join(ENTITY_TYPES)})")
        if SCHEME_IRI not in _ids(c.get("skos:inScheme")):
            problems.append(f"{REGISTRY}: {cid}: skos:inScheme is not the scheme")
        sources = _ids(c.get("dcterms:source"))
        doi_sources = [s for s in sources if s.startswith("https://doi.org/")]
        if not doi_sources:
            problems.append(f"{REGISTRY}: {cid}: no dcterms:source that is a doi.org URL")
        for s in doi_sources:
            if s[len("https://doi.org/"):] not in dois:
                problems.append(f"{REGISTRY}: {cid}: dcterms:source {s} is not a DOI the tree records (figshare/doi-map.json, papers' index.json)")
        for b in _ids(c.get("skos:broader")):
            if b not in cids:
                problems.append(f"{REGISTRY}: {cid}: skos:broader {b} is not a concept in the registry")
        if c.get("skos:broader") and SCHEME_IRI in _ids(c.get("skos:topConceptOf")):
            problems.append(f"{REGISTRY}: {cid}: has skos:broader and is skos:topConceptOf — a top concept is topmost (SKOS §4.6.3)")
        if c.get("skos:definition"):
            nodes = _list(c.get("efc:definitionQuotedFrom"))
            quoted = [n.get("@id") if isinstance(n, dict) else n for n in nodes]
            quoted = [q for q in quoted if isinstance(q, str)]
            m = FRAGMENT_RE.match(unquote(quoted[0][len(GH):])) if len(quoted) == 1 and len(nodes) == 1 and quoted[0].startswith(GH) else None
            if len(quoted) != 1 or not quoted[0].startswith(GH):
                problems.append(f"{REGISTRY}: {cid}: a skos:definition must name exactly one efc:definitionQuotedFrom under {GH}")
            elif m is None:
                problems.append(f"{REGISTRY}: {cid}: efc:definitionQuotedFrom needs a line fragment, #L<n> or #L<a>-L<b>")
            else:
                rel = m.group("path")
                start = int(m.group("start"))
                end = int(m.group("end") or start)
                # resolve() itself raises on a NUL byte, which percent-decoding
                # can now produce (%00) — a crash here would swallow every
                # other problem in the registry (review finding, round 2).
                try:
                    target = (root / rel).resolve()
                    inside = target.is_relative_to(root.resolve())
                    text = target.read_text(encoding="utf-8") if inside else None
                    lines = (text[:-1] if text.endswith("\n") else text).split("\n") if text is not None else None
                except (OSError, UnicodeDecodeError, ValueError):
                    inside, lines = True, None
                quote = _lit(c["skos:definition"])
                if not inside:
                    problems.append(f"{REGISTRY}: {cid}: efc:definitionQuotedFrom {rel} resolves outside the tree")
                elif lines is None:
                    problems.append(f"{REGISTRY}: {cid}: efc:definitionQuotedFrom {rel} is not a readable file in the tree")
                elif not quote.strip():
                    problems.append(f"{REGISTRY}: {cid}: skos:definition is empty")
                elif start < 1:
                    problems.append(f"{REGISTRY}: {cid}: efc:definitionQuotedFrom names line {start}; lines are numbered from 1")
                elif end < start:
                    problems.append(f"{REGISTRY}: {cid}: efc:definitionQuotedFrom names lines {start}-{end}, which runs backwards")
                elif end > len(lines):
                    problems.append(f"{REGISTRY}: {cid}: efc:definitionQuotedFrom names lines {start}-{end}, but {rel} has {len(lines)}")
                elif quote not in "\n".join(lines[start - 1:end]):
                    where = "somewhere else in the file" if quote in "\n".join(lines) else "nowhere in the file"
                    problems.append(f"{REGISTRY}: {cid}: skos:definition is not a verbatim substring of {rel} lines {start}-{end} — it is {where} (ADR-024)")
                else:
                    quote_hash = _lit(nodes[0].get("efc:quoteSha256") if isinstance(nodes[0], dict) else None)
                    if quote_hash and quote_hash != hashlib.sha256(quote.encode("utf-8")).hexdigest():
                        problems.append(f"{REGISTRY}: {cid}: efc:quoteSha256 does not match the quote")
        if not c.get("skos:definition") and not _lit(c.get("skos:scopeNote")).strip():
            problems.append(f"{REGISTRY}: {cid}: no skos:definition and no skos:scopeNote — an absent definition is a measurement, and it has to say so")
        if ont is not None and cid not in declared:
            problems.append(f"{ONTOLOGY}: {cid} is not declared — run efc_ontology.py --apply (C9)")
    if schemes:
        for t in _ids(schemes[0].get("skos:hasTopConcept")):
            if t not in cids:
                problems.append(f"{REGISTRY}: skos:hasTopConcept {t} is not a concept in the registry")
        tops = {c["@id"] for c in cs if not c.get("skos:broader")}
        if set(_ids(schemes[0].get("skos:hasTopConcept"))) != tops:
            problems.append(f"{REGISTRY}: skos:hasTopConcept must list exactly the concepts without skos:broader: {sorted(tops)}")
    for rel, render in ((VIEW_TERMSET, render_termset), (VIEW_INDEX, render_index)):
        try:
            current = (root / rel).read_text(encoding="utf-8")
        except OSError:
            current = None
        if current != render(reg):
            problems.append(f"{rel} is stale — run efc_concepts.py --apply")
    for rel in DEAD:
        if (root / rel).exists():
            problems.append(f"{rel}: dead copy still present — the registry is {REGISTRY}")
    return problems


def apply(root: Path = ROOT) -> None:
    reg = json.loads((root / REGISTRY).read_text(encoding="utf-8"))
    for rel, render in ((VIEW_TERMSET, render_termset), (VIEW_INDEX, render_index)):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(render(reg), encoding="utf-8")


def main(argv: list[str]) -> int:
    if "--apply" in argv:
        apply()
        n = len(concepts(json.loads((ROOT / REGISTRY).read_text(encoding="utf-8"))))
        print(f"[efc-concepts] wrote {VIEW_TERMSET} and {VIEW_INDEX}: {n} concepts from {REGISTRY}")
        return 0
    problems = check()
    for p in problems:
        print(f"[efc-concepts] {p}")
    if problems:
        print(f"[efc-concepts] FAIL — {len(problems)} problem(s)")
        return 1
    n = len(concepts(json.loads((ROOT / REGISTRY).read_text(encoding="utf-8"))))
    print(f"[efc-concepts] OK — {n} concepts in {REGISTRY}, views fresh, dead copies absent, all declared in {ONTOLOGY}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
