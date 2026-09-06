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
            concept IRI is declared in docs/ontology.jsonld (C9). A field the
            model may not fill by itself — efc:registryStatus other than
            `candidate`, any efc:entityType finer than `concept`,
            empiricalStatus, mappingStrength, falsifier,
            alternativeExplanation — is accepted ONLY with an efc:attested
            entry naming an ORCID from the authors: block of CITATION.cff, a real
            calendar date, a basis and the same value. The gate cannot judge
            the science; it can refuse to let the science be asserted without
            a human behind it. Declared omissions from the card's attestation
            record: `attestation_source` and `scope` are not carried, since
            the concept's own dcterms:source and skos:inScheme already say
            those; efc:reviewAt is optional, because an attestation that can
            never expire is a claim without an end; once set it is enforced,
            and an expired attestation is a problem, not a note. One
            attestation carries one field. A node whose entityType is not a
            concept at all is reported with that alone and nothing else on
            that node is checked — the entry fails either way, and a second
            message would only suggest a remedy that does not exist.
            And a
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

import datetime
import hashlib
import json
import re
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

# Where an entry is in its life. `candidate` is a proposal and costs nothing;
# `canonical` is a claim and needs a human (see ATTESTABLE).
REGISTRY_STATUS = ("candidate", "canonical", "contested", "deprecated", "superseded")
RETIRED = ("deprecated", "superseded")

# Fields a model must never fill by itself: each is a judgement about the
# science or about EFC's own structure, which ADR-024 puts outside its reach.
# The gate accepts the value ONLY with an efc:attested entry carrying it.
#   efc:registryStatus is on this list because the first draft exempted
#   entityType `concept` as "true by construction", and review measured the
#   hole: a model could register a PAPER as a concept, fill every other field
#   mechanically and pass. Registry membership is exactly what a model can
#   grant itself. Now `candidate` is free and `canonical` is attested, which
#   is what the card asked the status axis to mean.
ATTESTABLE = ("efc:registryStatus", "efc:entityType", "efc:empiricalStatus",
              "efc:mappingStrength", "efc:falsifier", "efc:alternativeExplanation")
FREE_VALUES = {"efc:registryStatus": ("candidate",), "efc:entityType": ("concept",)}
ATTESTATION_BASIS = ("explicit_decision", "quoted_source", "prior_publication")


def attesters(root: Path) -> tuple[set[str], str | None]:
    """(ORCIDs that may attest, note). The tree's declared author identities,
    read from the `authors:` block of CITATION.cff so a second copy cannot go
    stale. Measured 2026-09-06: CITATION.cff, codemeta.json and 1557 tracked
    files agree on 0009-0002-4860-5095, while three paper packages carry a
    different ORCID under the same name — drift that predates this gate.

    The whole block, not the first match: widening the author list widens who
    may attest an EFC judgement, and that is a wider set than "author" —
    declare it when it happens. And only that block: a CITATION.cff may carry
    a `references:` section with other people's ORCIDs, and a line-anchored
    regex would happily take one of those as the signing authority (review
    finding). Falling back to the constant is reported, never silent."""
    try:
        text = (root / "CITATION.cff").read_text(encoding="utf-8")
    except OSError:
        return {ATTESTER_FALLBACK}, f"no CITATION.cff — falling back to {ATTESTER_FALLBACK}"
    found: set[str] = set()
    in_authors = False
    for line in text.split("\n"):
        if re.match(r"^\S", line):
            in_authors = line.startswith("authors:")
            continue
        if in_authors:
            if line.lstrip().startswith("#"):
                continue  # a commented-out ORCID is not an author
            m = re.search(r"orcid:\s*['\"]?(https://orcid\.org/[0-9X-]+)", line)
            if m:
                found.add(m.group(1))
    if not found:
        return {ATTESTER_FALLBACK}, f"CITATION.cff has no ORCID under authors: — falling back to {ATTESTER_FALLBACK}"
    return found, None


def iso_date(v: str) -> bool:
    """YYYY-MM-DD and a real calendar date. Both halves are needed: a regex
    alone accepts 2026-13-45, and date.fromisoformat on Python 3.11 accepts
    20260906 and 2026-W36-7, so the tolerated shapes would depend on the
    interpreter version (review findings, two rounds)."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        return False
    try:
        datetime.date.fromisoformat(v)
    except ValueError:
        return False
    return True


def attestations(c: dict) -> list[dict]:
    v = c.get("efc:attested")
    return [x for x in (v if isinstance(v, list) else [v]) if isinstance(x, dict)]


def attested_value(c: dict, field: str):
    for a in attestations(c):
        if (_ids(a.get("efc:attests")) or [_lit(a.get("efc:attests"))])[0] == field:
            return _lit(a.get("efc:attestedValue"))
    return None
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
ATTESTER_FALLBACK = "https://orcid.org/0009-0002-4860-5095"
FRAGMENT_RE = re.compile(r"^(?P<path>[^#]+)#L(?P<start>\d+)(?:-L(?P<end>\d+))?$")
DOI_RE = re.compile(r"10\.\d{4,9}/[A-Za-z0-9._;()/:\-]+")


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
                             ("registryStatus", _lit(c.get("efc:registryStatus"))),
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
    who, who_note = attesters(root)
    if who_note:
        problems.append(f"{REGISTRY}: {who_note}")
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
        rs = _lit(c.get("efc:registryStatus"))
        if rs not in REGISTRY_STATUS:
            problems.append(f"{REGISTRY}: {cid}: efc:registryStatus {rs!r} is not one of {', '.join(REGISTRY_STATUS)}")
        if rs in RETIRED:
            for r in _ids(c.get("dcterms:isReplacedBy")) or [None]:
                if r is None:
                    problems.append(f"{REGISTRY}: {cid}: registryStatus {rs} needs dcterms:isReplacedBy — a retired concept says what took its place")
                elif r not in cids:
                    problems.append(f"{REGISTRY}: {cid}: dcterms:isReplacedBy {r} is not a concept in the registry")
        sett: set[str] = set()
        for a in attestations(c):
            attests = _ids(a.get("efc:attests")) or [_lit(a.get("efc:attests"))]
            if len(attests) != 1:
                problems.append(f"{REGISTRY}: {cid}: an attestation names {len(attests)} fields — one attestation, one field, or half a claim goes unread")
                continue
            felt = attests[0]
            if felt in sett:
                problems.append(f"{REGISTRY}: {cid}: two attestations for {felt} — only the first would be read")
            sett.add(felt)
            if felt not in ATTESTABLE:
                problems.append(f"{REGISTRY}: {cid}: attestation for {felt!r}, which is not an attestable field ({', '.join(ATTESTABLE)})")
            elif not _lit(c.get(felt)):
                problems.append(f"{REGISTRY}: {cid}: attestation for {felt}, but the field is not set")
            elif _lit(a.get("efc:attestedValue")) != _lit(c.get(felt)):
                problems.append(f"{REGISTRY}: {cid}: attestation for {felt} says {_lit(a.get('efc:attestedValue'))!r} but the field says {_lit(c.get(felt))!r}")
            by = _ids(a.get("efc:attestedBy"))
            if len(by) != 1 or by[0] not in who:
                problems.append(f"{REGISTRY}: {cid}: attestation for {felt} must name one efc:attestedBy from CITATION.cff ({', '.join(sorted(who))})")
            if not iso_date(_lit(a.get("dcterms:date"))):
                problems.append(f"{REGISTRY}: {cid}: attestation for {felt} needs a real calendar date as YYYY-MM-DD, not {_lit(a.get('dcterms:date'))!r}")
            review = _lit(a.get("efc:reviewAt"))
            if review:
                # An expiry the gate never reads is a date without a
                # consequence — the half-connection this house keeps finding.
                # Setting efc:reviewAt is opt-in; once set, it is enforced.
                if not iso_date(review):
                    problems.append(f"{REGISTRY}: {cid}: attestation for {felt} has an efc:reviewAt that is not a real date")
                elif iso_date(_lit(a.get("dcterms:date"))) and review <= _lit(a.get("dcterms:date")):
                    problems.append(f"{REGISTRY}: {cid}: attestation for {felt} has efc:reviewAt {review} on or before the date it was made")
                elif review < datetime.date.today().isoformat():
                    problems.append(f"{REGISTRY}: {cid}: the attestation for {felt} expired on {review} — renew it or drop the claim")
            if _lit(a.get("efc:basis")) not in ATTESTATION_BASIS:
                problems.append(f"{REGISTRY}: {cid}: attestation for {felt} needs efc:basis, one of {', '.join(ATTESTATION_BASIS)}")
        for felt in ATTESTABLE:
            verdi = _lit(c.get(felt))
            if not verdi or verdi in FREE_VALUES.get(felt, ()):
                continue
            if attested_value(c, felt) is None:
                problems.append(f"{REGISTRY}: {cid}: {felt} = {verdi!r} is a judgement the model may not make (ADR-024) — it needs an efc:attested entry from {', '.join(sorted(who))}")
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
