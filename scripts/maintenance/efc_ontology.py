#!/usr/bin/env python3
"""
EFC vocabulary (`efc:`) — one namespace, generated from use, checked in CI
==========================================================================

Namespace:  https://supertedai.github.io/EFC/ontology#
Documents:  docs/ontology.jsonld   (JSON-LD graph, machine-readable)
            docs/ontology.html     (same graph embedded, human-readable)
            — served by GitHub Pages (source: main:/docs). Pages serves
            `ontology.html` at `/EFC/ontology` with 200 and no redirect
            (measured 2026-09-06 on /EFC/public/<page>), so the namespace
            document IRI and the URL that serves it are the same string.

Why this exists (measured 2026-09-05 against origin/main a64b9627):
the prefix `efc:` was bound to NINE different namespace IRIs across 83
JSON-LD files — energyflow-cosmology.com/ontology#, github.com/…/ontology#,
…/schema/, …/schema#, …/vocab#, a paper directory, and one typo domain
(energyflow-cosmology.ORG). Three of them answered — a bare nginx
autoindex, its 301, a GitHub tree page — and none was a vocabulary; no term
dereferenced to a definition. `efc:X` in one file was therefore a different
RDF resource than `efc:X` in another. This script makes the identity ONE and
keeps it that way.

Modes
-----
  --check    (default) Every JSON-LD file that binds `efc`/`EFC` binds it to
             NS; no file uses an `efc:` prefix without binding it; every term
             in use — prefixed, `@vocab`-bound or context-aliased — is
             declared in docs/ontology.jsonld; and the generated documents
             are exactly what --apply would write today. Exit 1 on any
             deviation. Irregular strings (see below) are listed, not failed.
             Runs in CI (efc-verify.yml); efc_maintain.py runs --apply.
  --apply    Regenerate docs/ontology.jsonld and docs/ontology.html from the
             terms actually in use. Deterministic: same tree, same bytes (no
             timestamps in the output — CI diffs it).
  --rewrite  One-time migration: rewrite legacy bindings to NS and the
             `EFC:` prefix to `efc:`. Textual and targeted (only the binding
             inside `@context` and the term prefix), so file formatting and
             every other URL in the file survive. Idempotent.

What the vocabulary asserts, and what it does not
-------------------------------------------------
Terms are classified by USE, not by opinion: a term seen as `@type` is an
`rdfs:Class`; a term seen as a key is an `rdf:Property`; a term seen only as
a bare value is a `skos:Concept`. Labels are the local names. The document
asserts IDENTITY (one IRI per term, resolvable) — it does not yet assert
MEANING: definitions, aliases, supersession and "not to be confused with"
belong to the concept registry (kanban t_f513b2e7), which will be written
against this namespace. A vocabulary that invented definitions here would be
a tenth private form of the same thing the audit found nine of.

Scope of the scan: every *.json / *.jsonld under the repository that carries
a top-level `@context`, excluding .git, node_modules, __pycache__ and the
generated vocabulary itself. A term is bound three ways and all three are
counted: an explicit `efc:name` prefix; a context alias (`"name":
"efc:name"` or `{"@id": "efc:name"}`); and, when `@vocab` is the namespace
(schema/framework_atlas.jsonld), every plain key and unprefixed `@type`.

Declared limits: strings that start with `efc:` but are not a local name
(`efc:term/co-field` identifiers in meta/, an IRI with a space) and keys or
aliases that are not valid local names are LISTED on every check, neither
declared nor failed — the concept registry sorts them out. And a concept
"used as value" is the string literal "efc:Name" in the sources, not an
IRI, until the registry attaches it.
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
from pathlib import Path

NS = "https://supertedai.github.io/EFC/ontology#"
ROOT = Path(__file__).resolve().parents[2]
OUT_JSONLD = ROOT / "docs" / "ontology.jsonld"
OUT_HTML = ROOT / "docs" / "ontology.html"
VERSION = "0.1.0"

# The nine bindings measured 2026-09-05. Kept here so --check can name a
# regression precisely ("legacy binding X") instead of "not NS".
LEGACY = {
    "https://energyflow-cosmology.com/ontology#",
    "https://github.com/supertedai/EFC/ontology#",
    "https://energyflow-cosmology.com/schema/",
    "https://energyflow-cosmology.com/schema#",
    "https://github.com/supertedai/EFC/schema#",
    "https://github.com/supertedai/EFC/tree/main/docs/papers/efc/",
    "https://github.com/supertedai/EFC/vocab#",
    "https://energyflow-cosmology.com/ontology/",
    "https://energyflow-cosmology.org/ontology#",
}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
TERM_RE = re.compile(r"^(efc|EFC):([A-Za-z_][A-Za-z0-9_\-]*)$")


# ── scanning ─────────────────────────────────────────────────────────────
def jsonld_files(root: Path = ROOT):
    """(path, doc) for every JSON document with a top-level @context.

    The generated vocabulary itself is excluded: it binds `efc` and lists
    every term as a value, so scanning it would feed the generator its own
    output — --check then reported "stale" one second after --apply."""
    egen = (root / "docs" / "ontology.jsonld").resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            if not (fn.endswith(".json") or fn.endswith(".jsonld")):
                continue
            p = Path(dirpath) / fn
            if p.resolve() == egen:
                continue
            try:
                doc = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError, UnicodeDecodeError):
                continue
            if isinstance(doc, dict) and "@context" in doc:
                yield p, doc


def bindings(doc: dict) -> list[tuple[str, str]]:
    """[(prefix-key, iri)] for every efc/EFC binding in the @context."""
    out = []

    def scan(ctx):
        if isinstance(ctx, dict):
            for k, v in ctx.items():
                if k.lower() == "efc" and isinstance(v, str):
                    out.append((k, v))
        elif isinstance(ctx, list):
            for x in ctx:
                scan(x)

    scan(doc.get("@context"))
    return out


LOCAL_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_\-]*$")


def _context_view(ctx) -> tuple[bool, dict[str, str]]:
    """(vocab_is_ns, aliases): is `@vocab` the namespace, and which context
    keys are aliases for `efc:` terms (`"name": "efc:name"` or
    `{"@id": "efc:name"}`). Both bind terms WITHOUT an `efc:` prefix in the
    body text — the first --check missed 48 atlas keys and five
    meta_universe aliases that way (review finding)."""
    vocab = False
    aliases: dict[str, str] = {}

    def scan(c):
        nonlocal vocab
        if isinstance(c, dict):
            if c.get("@vocab") == NS:
                vocab = True
            for k, v in c.items():
                if k.startswith("@") or k.lower() == "efc":
                    continue  # prefix bindings are bindings(), not aliases
                iri = v.get("@id") if isinstance(v, dict) else v
                if isinstance(iri, str):
                    m = TERM_RE.match(iri)
                    if m:
                        aliases[k] = m.group(2)
                    elif iri.lower().startswith("efc:"):
                        aliases[k] = iri[4:]  # not a local name: terms() lists it as irregular
                    elif iri.startswith(NS):
                        aliases[k] = iri[len(NS):]
        elif isinstance(c, list):
            for x in c:
                scan(x)

    scan(ctx)
    return vocab, aliases


def terms(doc: dict) -> tuple[dict[str, dict[str, int]], list[str]]:
    """(term → {'class','property','individual'} by use, irregular strings).

    Three ways a body binds an `efc:` term, all counted: an explicit
    `efc:name` prefix; a context alias (`"name": "efc:name"`); and, when the
    context sets `@vocab` to the namespace, every plain key and every
    unprefixed `@type`. Strings that START with `efc:` but are not a local
    name (`efc:term/co-field`, an IRI with a space) are returned as
    IRREGULAR — they are references the registry has to sort out, not
    terms a vocabulary can declare."""
    found: dict[str, dict[str, int]] = {}
    irregular: list[str] = []
    vocab, aliases = _context_view(doc.get("@context"))
    for k, v in list(aliases.items()):
        if not LOCAL_RE.match(v or ""):
            irregular.append(f"@context alias {k!r} -> efc:{v}")
            del aliases[k]

    def hit(name: str, kind: str):
        found.setdefault(name, {"class": 0, "property": 0, "individual": 0})[kind] += 1

    def key_term(k: str):
        m = TERM_RE.match(k)
        if m:
            return m.group(2)
        if k in aliases:
            return aliases[k]
        if vocab and not k.startswith("@"):
            if LOCAL_RE.match(k):
                return k
            irregular.append(f"@vocab key {k!r}")
        return None

    def type_term(t: str):
        m = TERM_RE.match(t)
        if m:
            return m.group(2)
        if t in aliases:
            return aliases[t]
        if vocab and ":" not in t and not t.startswith("@"):
            if LOCAL_RE.match(t):
                return t
            irregular.append(f"@vocab @type {t!r}")
        return None

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                kt = key_term(k)
                if kt:
                    hit(kt, "property")
                elif re.match(r"^(efc|EFC):", k):
                    irregular.append(k)
                if k == "@type":
                    for t in (v if isinstance(v, list) else [v]):
                        if isinstance(t, str):
                            tt = type_term(t)
                            if tt:
                                hit(tt, "class")
                            elif re.match(r"^(efc|EFC):", t):
                                irregular.append(t)
                elif isinstance(v, str):
                    m = TERM_RE.match(v)
                    if m:
                        hit(m.group(2), "individual")
                    elif re.match(r"^(efc|EFC):", v):
                        irregular.append(v)
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk({k: v for k, v in doc.items() if k != "@context"})
    return found, irregular


def prefixed_without_binding(doc: dict) -> list[str]:
    """`efc:X` strings in a document that binds neither `efc` nor `@vocab`
    to NS. In JSON-LD those are absolute IRIs with the scheme `efc`, not
    terms in the namespace — the scan would otherwise absorb them silently
    (review finding, round 2). Aliases do not need the prefix."""
    vocab, _ = _context_view(doc.get("@context"))
    if vocab or bindings(doc):
        return []
    hits: list[str] = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if TERM_RE.match(k):
                    hits.append(k)
                if k == "@type":
                    for t in (v if isinstance(v, list) else [v]):
                        if isinstance(t, str) and TERM_RE.match(t):
                            hits.append(t)
                elif isinstance(v, str) and TERM_RE.match(v):
                    hits.append(v)
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk({k: v for k, v in doc.items() if k != "@context"})
    return sorted(set(hits))


def inventory(root: Path = ROOT):
    """Aggregate over the tree: (bindings per file, term → counts, files,
    irregular [(path, string)])."""
    per_file, agg, n, irregular = {}, {}, 0, []
    for p, doc in jsonld_files(root):
        n += 1
        b = bindings(doc)
        if b:
            per_file[p] = b
        found, irr = terms(doc)
        for t, kinds in found.items():
            a = agg.setdefault(t, {"class": 0, "property": 0, "individual": 0, "files": 0})
            for k in ("class", "property", "individual"):
                a[k] += kinds[k]
            a["files"] += 1
        irregular.extend((p, x) for x in irr)
    return per_file, agg, n, irregular


def classify(counts: dict) -> str:
    # Use decides. A term used as @type anywhere is a class even if it is
    # also (wrongly) used as a value somewhere — the class reading is the
    # stronger claim, and the check will surface the conflict in the HTML.
    if counts["class"]:
        return "rdfs:Class"
    if counts["property"]:
        return "rdf:Property"
    return "skos:Concept"


# ── generation ───────────────────────────────────────────────────────────
def build_graph(agg: dict) -> dict:
    ctx = {
        "efc": NS,
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "owl": "http://www.w3.org/2002/07/owl#",
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "dcterms": "http://purl.org/dc/terms/",
        "schema": "https://schema.org/",
        "label": "rdfs:label",
        "comment": "rdfs:comment",
        "isDefinedBy": {"@id": "rdfs:isDefinedBy", "@type": "@id"},
        "seeAlso": {"@id": "rdfs:seeAlso", "@type": "@id"},
        "usedAsClass": {"@id": "efc:usedAsClass", "@type": "http://www.w3.org/2001/XMLSchema#integer"},
        "usedAsProperty": {"@id": "efc:usedAsProperty", "@type": "http://www.w3.org/2001/XMLSchema#integer"},
        "usedAsValue": {"@id": "efc:usedAsValue", "@type": "http://www.w3.org/2001/XMLSchema#integer"},
        "inDocuments": {"@id": "efc:inDocuments", "@type": "http://www.w3.org/2001/XMLSchema#integer"},
    }
    head = {
        "@id": NS.rstrip("#"),
        "@type": "owl:Ontology",
        "dcterms:title": "Energy-Flow Cosmology vocabulary (efc)",
        "owl:versionInfo": VERSION,
        "dcterms:creator": {"@id": "https://orcid.org/0009-0002-4860-5095"},
        "dcterms:license": {"@id": "https://creativecommons.org/licenses/by/4.0/"},
        "seeAlso": ["https://energyflow-cosmology.com/", "https://github.com/supertedai/EFC"],
        "comment": (
            "Generated by scripts/maintenance/efc_ontology.py from the terms "
            "actually used in the repository's JSON-LD. Asserts identity (one "
            "IRI per term), not yet meaning: definitions, aliases and "
            "supersession belong to the concept registry."
        ),
        "skos:note": (
            "Terms typed skos:Concept appear in the sources as the STRING "
            "\"efc:Name\" (no property in the tree is @type:@id), so in the "
            "source graphs they are literals, not this IRI. The IRI is the "
            "identity the registry will attach them to; until then the "
            "mapping is by name."
        ),
    }
    # Bookkeeping properties the generator itself uses, declared so the
    # vocabulary does not use undeclared terms — the check would catch that.
    meta = [
        {"@id": f"efc:{n}", "@type": "rdf:Property", "label": n, "isDefinedBy": NS.rstrip("#"),
         "comment": c}
        for n, c in (
            ("usedAsClass", "How many times the term appears as @type in the repository."),
            ("usedAsProperty", "How many times the term appears as a key in the repository."),
            ("usedAsValue", "How many times the term appears as a bare value in the repository."),
            ("inDocuments", "In how many JSON-LD documents the term appears."),
        )
    ]
    nodes = []
    for t in sorted(agg):
        c = agg[t]
        nodes.append({
            "@id": f"efc:{t}",
            "@type": classify(c),
            "label": t,
            "isDefinedBy": NS.rstrip("#"),
            "usedAsClass": c["class"],
            "usedAsProperty": c["property"],
            "usedAsValue": c["individual"],
            "inDocuments": c["files"],
        })
    return {"@context": ctx, "@graph": [head, *meta, *nodes]}


def render_html(graph: dict, agg: dict) -> str:
    kinds = {"rdfs:Class": [], "rdf:Property": [], "skos:Concept": []}
    for t in sorted(agg):
        kinds[classify(agg[t])].append(t)
    rows = []
    for kind, title in (("rdfs:Class", "Classes"), ("rdf:Property", "Properties"), ("skos:Concept", "Concepts (used as values)")):
        rows.append(f"<h2>{title} <small>({len(kinds[kind])})</small></h2>\n<table><thead><tr><th>term</th><th>IRI</th><th>as @type</th><th>as key</th><th>as value</th><th>documents</th></tr></thead><tbody>")
        for t in kinds[kind]:
            c = agg[t]
            iri = NS + t
            rows.append(
                f'<tr id="{html.escape(t)}"><td><code>efc:{html.escape(t)}</code></td>'
                f'<td><a href="{html.escape(iri)}">{html.escape(iri)}</a></td>'
                f'<td>{c["class"]}</td><td>{c["property"]}</td><td>{c["individual"]}</td><td>{c["files"]}</td></tr>'
            )
        rows.append("</tbody></table>")
    embedded = json.dumps(graph, ensure_ascii=False, indent=2).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Energy-Flow Cosmology vocabulary (efc)</title>
<link rel="alternate" type="application/ld+json" href="ontology.jsonld">
<link rel="license" href="https://creativecommons.org/licenses/by/4.0/">
<style>
body{{font:15px/1.5 system-ui,sans-serif;max-width:64rem;margin:2rem auto;padding:0 1rem;color:#222}}
table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{border-bottom:1px solid #ddd;padding:.3rem .5rem;text-align:left}}
code{{background:#f4f4f4;padding:0 .2rem}}small{{color:#666;font-weight:normal}}
</style>
<script type="application/ld+json">
{embedded}
</script>
</head>
<body>
<h1>Energy-Flow Cosmology vocabulary <code>efc:</code></h1>
<p><strong>Namespace:</strong> <code>{NS}</code> &middot; version {VERSION} &middot;
<a href="ontology.jsonld">ontology.jsonld</a> (JSON-LD) &middot; author <a href="https://orcid.org/0009-0002-4860-5095">Morten Magnusson</a> &middot; license CC BY 4.0</p>
<p>This document is generated from the terms actually used in the JSON-LD of
<a href="https://github.com/supertedai/EFC">supertedai/EFC</a> by
<code>scripts/maintenance/efc_ontology.py</code>. It asserts <em>identity</em>
— one resolvable IRI per term — not yet <em>meaning</em>: definitions, aliases
and supersession belong to the concept registry. Terms are classified by use:
seen as <code>@type</code> → class; seen as a key → property; seen only as a
value → concept. {len(agg)} terms. <strong>Note:</strong> a term "used as value"
appears in the sources as the string <code>"efc:Name"</code>, not as an IRI
(no property in the tree is <code>@type: @id</code>) — the concept IRI is the
identity the registry will attach it to; until then the mapping is by name.</p>
{chr(10).join(rows)}
</body>
</html>
"""


def generate(root: Path = ROOT) -> tuple[str, str]:
    _, agg, _, _ = inventory(root)
    graph = build_graph(agg)
    return json.dumps(graph, ensure_ascii=False, indent=2) + "\n", render_html(graph, agg)


# ── rewrite (one-time migration, textual) ────────────────────────────────
def rewrite(root: Path = ROOT) -> list[str]:
    changed = []
    for p, doc in jsonld_files(root):
        b = bindings(doc)
        if not b:
            continue
        with open(p, encoding="utf-8", newline="") as fh:   # newline="": CRLF survives
            text = fh.read()
        new = text
        for key, iri in b:
            if iri == NS and key == "efc":
                continue
            # only the binding line inside @context — never a URL elsewhere
            pat = re.compile(r'"' + re.escape(key) + r'"(\s*:\s*)"' + re.escape(iri) + r'"')
            new = pat.sub(lambda m: '"efc"' + m.group(1) + '"' + NS + '"', new)
            if key == "EFC":
                # term prefix: `"EFC:Node"` → `"efc:Node"`; prose like
                # "EFC: a framework" has a space after the colon and is untouched
                new = re.sub(r'"EFC:([A-Za-z_])', r'"efc:\1', new)
        if new != text:
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(new)
            changed.append(str(p.relative_to(root)))
    return changed


# ── check ────────────────────────────────────────────────────────────────
def check(root: Path = ROOT, notes: list[str] | None = None) -> list[str]:
    """Problems (exit 1). `notes` collects non-fatal observations: irregular
    `efc:` strings that are references, not terms — listed every run so the
    limit is visible, left to the registry to resolve."""
    problems = []
    per_file, agg, n, irregular = inventory(root)
    if notes is not None:
        for p, x in irregular:
            notes.append(f"{p.relative_to(root)}: {x!r} — irregular efc: reference (not a local name); not declared, registry's job")
    for p, doc in jsonld_files(root):
        loose = prefixed_without_binding(doc)
        if loose:
            problems.append(f'{p.relative_to(root)}: uses {", ".join(loose[:4])}{" …" if len(loose) > 4 else ""} without binding "efc" — an IRI with scheme efc, not a term in {NS}')
    for p, b in sorted(per_file.items()):
        for key, iri in b:
            if iri != NS or key != "efc":
                tag = "legacy binding" if iri in LEGACY else "unknown binding"
                problems.append(f'{p.relative_to(root)}: "{key}": "{iri}" — {tag}; expected "efc": "{NS}"')
    try:
        declared = {
            node["@id"].split(":", 1)[1]
            for node in json.loads(OUT_JSONLD.read_text(encoding="utf-8")).get("@graph", [])
            if isinstance(node.get("@id"), str) and node["@id"].startswith("efc:")
        }
    except (OSError, ValueError, KeyError):
        problems.append(f"{OUT_JSONLD.relative_to(root)}: missing or unreadable — run --apply")
        declared = set()
    for t in sorted(set(agg) - declared):
        problems.append(f"efc:{t} is used in the tree but not declared in docs/ontology.jsonld — run --apply")
    want_jsonld, want_html = generate(root)
    for out, want in ((OUT_JSONLD, want_jsonld), (OUT_HTML, want_html)):
        try:
            have = out.read_text(encoding="utf-8")
        except OSError:
            have = None
        if have != want:
            problems.append(f"{out.relative_to(root)} is stale — run --apply and commit")
    if n == 0:
        problems.append("no JSON-LD documents found — scanning the wrong root?")
    return problems


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--apply" in argv:
        jl, h = generate()
        OUT_JSONLD.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSONLD.write_text(jl, encoding="utf-8")
        OUT_HTML.write_text(h, encoding="utf-8")
        _, agg, n, _ = inventory()
        print(f"[efc-ontology] wrote {OUT_JSONLD.relative_to(ROOT)} and {OUT_HTML.relative_to(ROOT)}: {len(agg)} terms from {n} JSON-LD documents")
        return 0
    if "--rewrite" in argv:
        changed = rewrite()
        print(f"[efc-ontology] rewrote {len(changed)} files to {NS}")
        for c in changed:
            print("  " + c)
        return 0
    notes: list[str] = []
    problems = check(notes=notes)
    if problems:
        print(f"[efc-ontology] {len(problems)} problem(s):")
        for x in problems:
            print("  " + x)
        return 1
    _, agg, n, _ = inventory()
    print(f"[efc-ontology] OK — one namespace ({NS}), {len(agg)} terms declared, {n} JSON-LD documents scanned"
          + (f"; {len(notes)} irregular efc: reference(s) listed, not declared (registry's job)" if notes else ""))
    for x in notes[:12]:
        print("  note: " + x)
    if len(notes) > 12:
        print(f"  note: … {len(notes) - 12} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
