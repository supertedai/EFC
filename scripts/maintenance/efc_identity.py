#!/usr/bin/env python3
"""
Schema identity and JSON-LD form (C12) — one $id authority, one dialect, @id on top
====================================================================================

Authority:  https://supertedai.github.io/EFC/
Path form:  the SERVED path. GitHub Pages serves main:/docs as the site root
            (measured 2026-09-06: …/EFC/index.jsonld -> 200,
            …/EFC/docs/index.jsonld -> 404), so a file under docs/ is
            identified by its path with the docs/ prefix stripped, and that
            identifier dereferences today — the same form the vocabulary
            (…/EFC/ontology#, C9) and the concept registry
            (…/EFC/concepts.jsonld, C11) already use. Files outside docs/
            (schema/, meta/, methodology/, theory/, jsonld/, api/, figshare/,
            src/) keep their repository path: identifiers, not URLs, until
            the Pages source changes. --check prints that count, and refuses
            a collision between docs/X and a root-level X (docs/meta/ and
            meta/ both exist; 0 colliding files today). Paths are
            percent-encoded (spaces, commas, non-ASCII), so every identifier
            is a valid URI reference.
Dialect:    https://json-schema.org/draft/2020-12/schema

Why this exists (measured 2026-09-05 against origin/main a64b9627): $id was
missing on 336 of 400 schema-like files; the 64 that had one used four
authorities, five of them under efc-project.org (NXDOMAIN) and 39 under a
github.com path that serves HTML; one pointed at a doi-map.schema.json that
did not exist. Dialects: 118× 2020-12, 21× draft-07 in two spellings, 78
schema-named files with no $schema at all. 260 of 482 JSON-LD documents had
no top-level @id (blank nodes). Four data files carried "$schema":
"kill_test_v6_universality" — not a URI. codemeta used the 2.0 context (3.0
since 2023).

What is enforced, per file class
--------------------------------
JSON Schema files — *.json without @context that (a) declare a
json-schema.org dialect, or (b) carry a `properties` object together with
`type: object` or `required`, or a `$defs` object, or (c) are NAMED
*schema*.json and carry properties/required/$defs/definitions. A bare
`definitions` LIST is paper content, not a schema (a paper's index.json was
misclassified that way once). Enforced: $schema is the dialect; $id is the
served identifier; no draft-07 `definitions` (-> $defs) and no draft-04
top-level `id`. Files named *schema*.json that carry none of those keys are
not schemas; --check lists them.
JSON-LD documents — *.jsonld whose top level is an object WITHOUT `@graph`:
  a top-level @id exists. Values that were already there are kept (a
  schema.org WebSite whose @id is the site is right as it is); values this
  script ADDS are the DOI URL (https://doi.org/…) when the document carries
  a DOI in identifier/sameAs/doi, else the served identifier. An @id under
  the authority must be the served identifier (drift check). Documents that
  carry `@graph` are exempt: a top-level @id beside @graph makes the graph a
  NAMED graph in JSON-LD, which moves every triple out of the default graph
  — the vocabulary's identity is its owl:Ontology node inside the graph.
Instances that point at a schema with "$schema" — an editor convention
  (VS Code reads it; no validator does; the binding validators use is the
  C10 registry): the value must be https://schema.org/, or resolve
  (relative path, or served/authority URL) to a file in the tree that IS a
  schema by the rule above.
codemeta.json: @context is https://w3id.org/codemeta/3.0 with no 2.0-only
  property names (contIntegration, embargoDate). CITATION.cff `type` vs
  codemeta @type is REPORTED, not enforced: which of the two files is right
  about the work is a human word, not this script's.
Not maintained, by declaration: _archived/ (its manifests would drift
otherwise) and the EFC-R-SPARC case-colliding pair (t_e505c64c).

Modes
-----
  --check    (default) exit 1 on any deviation; notes list the declared
             counts (identifiers outside docs/, exempt @graph documents,
             non-schema schema-named files, the CFF/codemeta state).
  --rewrite  one-time migration, textual and targeted: a $schema/$id/@id
             line replaced or inserted (comma-aware), definitions -> $defs
             with refs, the draft-04 top-level id dropped, non-URI and
             dead pointers dropped or retargeted, codemeta moved to 3.0.
             Indentation and line endings of every file survive (measured
             on the CRLF files under methodology/).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
AUTHORITY = "https://supertedai.github.io/EFC/"
DIALECT = "https://json-schema.org/draft/2020-12/schema"
PAGES_PREFIX = "docs/"
SKIP_DIRS = {".git", "node_modules", "__pycache__", "_archived"}
NON_URI_POINTERS = {"kill_test_v6_universality", "kill_test_v6_universality_curves"}
DOI_MAP_POINTER = "../schema/doi-map.schema.json"
# docs/papers/efc/EFC-R-SPARC/ holds EFC-R-SPARC.jsonld AND efc-r-sparc.jsonld —
# a case-colliding pair that a case-insensitive filesystem cannot edit
# separately (kanban t_e505c64c). Both are skipped, by check and by rewrite.
SKIP_FILES = {"docs/papers/efc/EFC-R-SPARC/EFC-R-SPARC.jsonld", "docs/papers/efc/EFC-R-SPARC/efc-r-sparc.jsonld"}
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"']+")
CODEMETA_2_ONLY = ("contIntegration", "embargoDate")


def served_id(rel: str) -> str:
    """The identifier of a repository path: served form for docs/, quoted."""
    if rel.startswith(PAGES_PREFIX):
        rel = rel[len(PAGES_PREFIX):]
    return AUTHORITY + quote(rel, safe="/")


def _files(root: Path, suffixes):
    for p in sorted(root.rglob("*")):
        if p.suffix not in suffixes or any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.relative_to(root).as_posix() in SKIP_FILES:
            continue
        yield p


def _load(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def is_schema(doc, path: Path | None = None) -> bool:
    if not isinstance(doc, dict) or "@context" in doc:
        return False
    if "json-schema.org" in str(doc.get("$schema", "")):
        return True
    props = isinstance(doc.get("properties"), dict)
    if props and (doc.get("type") == "object" or isinstance(doc.get("required"), list)):
        return True
    if isinstance(doc.get("$defs"), dict):
        return True
    if path is not None and "schema" in path.name.lower():
        return props or isinstance(doc.get("required"), list) or isinstance(doc.get("definitions"), dict)
    return False


def schema_files(root: Path):
    for p in _files(root, {".json"}):
        d = _load(p)
        if is_schema(d, p):
            yield p, d


def schema_named_non_schemas(root: Path):
    for p in _files(root, {".json"}):
        if "schema" in p.name.lower():
            d = _load(p)
            if isinstance(d, dict) and not is_schema(d, p):
                yield p


def jsonld_files(root: Path):
    for p in _files(root, {".jsonld"}):
        d = _load(p)
        if isinstance(d, dict):
            yield p, d


def instance_pointers(root: Path):
    """(path, $schema value) for JSON documents that are not schemas."""
    for p in _files(root, {".json"}):
        d = _load(p)
        if isinstance(d, dict) and isinstance(d.get("$schema"), str) and not is_schema(d, p):
            yield p, d["$schema"]


def expected_id(root: Path, p: Path) -> str:
    return served_id(p.relative_to(root).as_posix())


def doi_of(doc: dict):
    for k in ("identifier", "sameAs", "doi", "@id"):
        v = doc.get(k)
        for x in (v if isinstance(v, list) else [v]):
            m = DOI_RE.search(x) if isinstance(x, str) else None
            if m:
                return m.group(0).rstrip(".,;)")
    return None


def pointer_target(root: Path, p: Path, value: str):
    """The file a "$schema" pointer names, or None."""
    if value.startswith(AUTHORITY):
        rest = value[len(AUTHORITY):]
        for cand in (root / PAGES_PREFIX / rest, root / rest):
            if cand.is_file():
                return cand
        return None
    if "://" in value or not value.endswith(".json"):
        return None
    cand = (p.parent / value).resolve()
    return cand if cand.is_file() else None


def pointer_ok(root: Path, p: Path, value: str) -> bool:
    if value == "https://schema.org/":
        return True
    t = pointer_target(root, p, value)
    return t is not None and is_schema(_load(t), t)


def check(root: Path = ROOT, notes=None) -> list[str]:
    problems: list[str] = []
    outside = graphs = 0
    ids: dict[str, str] = {}
    for p, d in schema_files(root):
        rel = p.relative_to(root).as_posix()
        want = expected_id(root, p)
        if d.get("$schema") != DIALECT:
            problems.append(f"{rel}: $schema is {d.get('$schema')!r}, not the 2020-12 dialect")
        if d.get("$id") != want:
            problems.append(f"{rel}: $id is {d.get('$id')!r}, expected {want}")
        if isinstance(d.get("definitions"), dict) or "#/definitions/" in json.dumps(d):
            problems.append(f"{rel}: draft-07 `definitions` — use $defs")
        if isinstance(d.get("id"), str):
            problems.append(f"{rel}: draft-04 top-level `id` — use $id")
        if not rel.startswith(PAGES_PREFIX):
            outside += 1
        ids.setdefault(want, rel)
        if ids[want] != rel:
            problems.append(f"{rel}: identifier {want} collides with {ids[want]} (docs/X shadows X)")
    for p, d in jsonld_files(root):
        rel = p.relative_to(root).as_posix()
        if "@graph" in d:
            graphs += 1
            continue
        want = expected_id(root, p)
        if "@id" not in d:
            problems.append(f"{rel}: no top-level @id (blank node)")
        elif isinstance(d["@id"], str) and d["@id"].startswith(AUTHORITY):
            if d["@id"] != want:
                problems.append(f"{rel}: @id {d['@id']} is under the authority but is not the served identifier {want}")
            if not rel.startswith(PAGES_PREFIX):
                outside += 1
            ids.setdefault(want, rel)
            if ids[want] != rel:
                problems.append(f"{rel}: identifier {want} collides with {ids[want]} (docs/X shadows X)")
    for p, v in instance_pointers(root):
        rel = p.relative_to(root).as_posix()
        if not pointer_ok(root, p, v):
            problems.append(f"{rel}: \"$schema\": {v!r} does not resolve to a schema in the tree")
    cm = _load(root / "codemeta.json")
    cff_note = None
    if isinstance(cm, dict):
        if cm.get("@context") != "https://w3id.org/codemeta/3.0":
            problems.append(f"codemeta.json: @context is {cm.get('@context')!r}, expected https://w3id.org/codemeta/3.0")
        for old in CODEMETA_2_ONLY:
            if old in cm:
                problems.append(f"codemeta.json: 2.0 property `{old}`")
        cff = root / "CITATION.cff"
        if cff.is_file():
            m = re.search(r"^type:\s*(\S+)", cff.read_text(encoding="utf-8"), re.M)
            want = {"SoftwareSourceCode": "software", "Dataset": "dataset"}.get(str(cm.get("@type")))
            got = m.group(1) if m else None
            cff_note = (f"CITATION.cff type `{got}` and codemeta @type `{cm.get('@type')}` " + ("agree" if got == want else "DISAGREE — which is right about the work is a human word; change one of them, not this script"))
    if notes is not None:
        notes.append(f"{outside} identifier(s) under {AUTHORITY} outside {PAGES_PREFIX} — identifiers, not URLs, until the Pages source changes")
        notes.append(f"{graphs} @graph document(s) exempt from a top-level @id (a named graph is a different thing)")
        named = [q.relative_to(root).as_posix() for q in schema_named_non_schemas(root)]
        notes.append(f"{len(named)} file(s) named *schema*.json are not schemas (no properties/required/$defs): {', '.join(named)}")
        notes.append(f"{len(SKIP_FILES)} file(s) skipped: the EFC-R-SPARC case-colliding pair (t_e505c64c); _archived/ not maintained")
        if cff_note:
            notes.append(cff_note)
    return problems


# ── rewrite (textual, targeted, format-preserving) ──────────────────────────

def _nl_and_indent(text: str):
    nl = "\r\n" if "\r\n" in text else "\n"
    m = re.search(r"\n( +)\"", text)
    return nl, (m.group(1) if m else "  ")


def _set_top_key(text: str, key: str, value: str, after_keys=("$schema",), before_keys=("@type",)) -> str:
    """Replace the top-level `"key": "..."` line or insert one — after the
    first of after_keys present, else before the first of before_keys, else
    right after the opening brace. Comma-aware: an anchor that was the last
    member gets the comma and the new line does not."""
    nl, ind = _nl_and_indent(text)
    line = f'{ind}"{key}": {json.dumps(value, ensure_ascii=False)},'
    pat = re.compile(r"^" + re.escape(ind) + r'"' + re.escape(key) + r'":\s*"[^"\r\n]*",?[ \t]*$', re.M)
    if pat.search(text):
        return pat.sub(lambda m: line if m.group(0).rstrip().endswith(",") else line[:-1], text, count=1)
    for k in after_keys:
        m = re.search(r"^" + re.escape(ind) + r'"' + re.escape(k) + r'":[^\r\n]*$', text, re.M)
        if m:
            anchor = m.group(0)
            if anchor.rstrip().endswith(","):
                return text[:m.end()] + nl + line + text[m.end():]
            return text[:m.start()] + anchor.rstrip() + "," + nl + line[:-1] + text[m.end():]
    for k in before_keys:
        m = re.search(r"^" + re.escape(ind) + r'"' + re.escape(k) + r'":', text, re.M)
        if m:
            return text[:m.start()] + line + nl + text[m.start():]
    m = re.search(r"\{[ \t]*\r?\n", text)
    rest = text[m.end():]
    empty = rest.lstrip().startswith("}")
    return text[:m.end()] + (line[:-1] if empty else line) + nl + rest


def _drop_top_key(text: str, key: str) -> str:
    nl, ind = _nl_and_indent(text)
    m = re.search(r"^" + re.escape(ind) + r'"' + re.escape(key) + r'":[^\r\n]*\r?\n', text, re.M)
    if not m:
        return text
    dropped = m.group(0)
    out = text[:m.start()] + text[m.end():]
    if not dropped.rstrip().endswith(","):
        head = out[:m.start()]
        out = re.sub(r",([ \t]*\r?\n)$", r"\1", head, count=1) + out[m.start():]
    return out


def rewrite(root: Path = ROOT) -> list[str]:
    changed: list[str] = []

    def write(p: Path, old: str, new: str):
        if new != old:
            json.loads(new)  # never write a file that no longer parses
            p.write_bytes(new.encode("utf-8"))
            changed.append(p.relative_to(root).as_posix())

    for p, d in list(schema_files(root)):
        old = p.read_bytes().decode("utf-8")
        new = old
        if d.get("$schema") != DIALECT:
            new = _set_top_key(new, "$schema", DIALECT)
        if d.get("$id") != expected_id(root, p):
            new = _set_top_key(new, "$id", expected_id(root, p))
        if isinstance(d.get("id"), str):
            new = _drop_top_key(new, "id")
        if isinstance(d.get("definitions"), dict) or "#/definitions/" in old:
            nl, ind = _nl_and_indent(new)
            new = re.sub(r"^" + re.escape(ind) + r'"definitions":', ind + '"$defs":', new, count=1, flags=re.M)
            new = new.replace("#/definitions/", "#/$defs/")
        write(p, old, new)
    for p, d in list(jsonld_files(root)):
        if "@graph" in d:
            continue
        want = expected_id(root, p)
        old = p.read_bytes().decode("utf-8")
        if "@id" not in d:
            doi = doi_of(d)
            write(p, old, _set_top_key(old, "@id", f"https://doi.org/{doi}" if doi else want, after_keys=(), before_keys=("@type",)))
        elif isinstance(d["@id"], str) and d["@id"].startswith(AUTHORITY) and d["@id"] != want:
            write(p, old, _set_top_key(old, "@id", want, after_keys=(), before_keys=("@type",)))
    for p, v in list(instance_pointers(root)):
        old = p.read_bytes().decode("utf-8")
        if v in NON_URI_POINTERS:
            write(p, old, _drop_top_key(old, "$schema"))
        elif v.endswith("doi-map.schema.json") and pointer_target(root, p, v) is None:
            write(p, old, _set_top_key(old, "$schema", DOI_MAP_POINTER))
        elif not pointer_ok(root, p, v):
            write(p, old, _drop_top_key(old, "$schema"))  # a pointer to a non-schema binds nothing
    cm = root / "codemeta.json"
    if cm.is_file():
        old = cm.read_text(encoding="utf-8")
        new = _set_top_key(old, "@context", "https://w3id.org/codemeta/3.0")
        new = re.sub(r'^(\s*)"contIntegration":', r'\1"continuousIntegration":', new, count=1, flags=re.M)
        write(cm, old, new)
    return changed


def main(argv: list[str]) -> int:
    if "--rewrite" in argv:
        ch = rewrite()
        print(f"[efc-identity] rewrote {len(ch)} file(s)")
        for c in ch[:20]:
            print(f"  {c}")
        if len(ch) > 20:
            print(f"  … and {len(ch) - 20} more")
        return 0
    notes: list[str] = []
    problems = check(notes=notes)
    for p in problems:
        print(f"[efc-identity] {p}")
    for n in notes:
        print(f"[efc-identity] note: {n}")
    if problems:
        print(f"[efc-identity] FAIL — {len(problems)} problem(s)")
        return 1
    print(f"[efc-identity] OK — one $id authority ({AUTHORITY}, served form), one dialect, every JSON-LD document without @graph has a top-level @id, every $schema pointer resolves to a schema, codemeta 3.0")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
