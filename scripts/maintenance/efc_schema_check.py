#!/usr/bin/env python3
"""
JSON Schema gate (C10) — declared (schema, instance) pairs, valid and CLOSED
==========================================================================

Why this exists (measured 2026-09-05 against origin/main a64b9627): the tree
carried ~400 schema-like .json files and 16 CI workflows, and no workflow ran
a schema validator. `efc_atlas_export.py` defined SCHEMA_PATH and never used
it; atlas-verify.yml hand-wrote key checks in inline Python instead. And 0 of
the schemas were closed: an invented key — a new synonym without a registry —
passed every one of them silently.

What this gate asserts, per registered pair:
  1. the schema is valid against its own metaschema ($schema dialect);
  2. the instance validates against the schema;
  3. the schema is CLOSED — every object schema (type object, or anything
     with properties/patternProperties, at any depth: $defs, items, allOf…)
     carries `additionalProperties: false`, and no subschema is `{}`/`true`
     (draft-07 has no `unevaluatedProperties`; false is the strongest form
     the dialect has). A typed map (`additionalProperties: {schema}`) is
     still open — an invented key with the right type passes it; use
     patternProperties + false instead.
Formats are enforced (`format: date-time` etc.) — `rfc3339-validator` is
installed in CI for that; without it, date-time is not checked.
Schemas registered without an instance are checked for (1) only, and named
with the instance path their README already promises: the day that file
appears the gate says so, and the pair is one line to register. Closing a
schema blind, with no data to measure it against, would assert nothing.

Registered (2026-09-06):
  docs/likelihood-ledger/schema.json   <- docs/likelihood-ledger/likelihoods.json
  schema/framework_atlas.schema.json   <- schema/framework_atlas.jsonld
  schema/doi-map.schema.json           <- figshare/doi-map.json   (t_141136b1: the pointer was dead)
  docs/evaluation-ledger/schema.json      (instance promised: data/evaluation.json — absent)
  docs/model-comparison/schema.json       (instance promised: data/comparisons.json — absent)

Declared limits, measured 2026-09-06 and NOT gated here: 162 paper
`index.json` files point at a sibling `./schema.json`; 48 of them validate,
and the 162 schemas are 115 distinct texts (each paper hand-rolls its own).
That population needs its own decision before it can be a gate. The
evaluation-ledger and model-comparison `index.jsonld` files are schema.org
Datasets, not instances of their sibling schema.

Adding a pair: put it in PAIRS, make it green locally, and close the schema.
The registry is explicit on purpose — a heuristic ("every schema.json next
to an index.json") would have registered 114 red pairs in one move.

Usage:  efc_schema_check.py [--list]      exit 1 on any deviation
Needs:  jsonschema>=4.18, rfc3339-validator (requirements.txt; efc-schema.yml
        installs both, plus pytest and PyYAML for the tests)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PAIRS: list[tuple[str, str]] = [
    ("docs/likelihood-ledger/schema.json", "docs/likelihood-ledger/likelihoods.json"),
    ("schema/framework_atlas.schema.json", "schema/framework_atlas.jsonld"),
    ("schema/doi-map.schema.json", "figshare/doi-map.json"),
]
# (schema, instance path its README promises) — checked as schemas only until
# the instance exists; then the gate says so and the pair moves to PAIRS.
INSTANCELESS: list[tuple[str, str]] = [
    ("docs/evaluation-ledger/schema.json", "docs/evaluation-ledger/data/evaluation.json"),
    ("docs/model-comparison/schema.json", "docs/model-comparison/data/comparisons.json"),
]


def _load(root: Path, rel: str, problems: list[str]):
    try:
        with open(root / rel, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError) as e:
        problems.append(f"{rel}: unreadable — {e}")
        return None


SUBSCHEMA_MAPS = ("properties", "patternProperties", "$defs", "definitions", "dependentSchemas")
SUBSCHEMA_ONE = ("items", "additionalProperties", "additionalItems", "unevaluatedProperties",
                 "unevaluatedItems", "contains", "propertyNames", "not", "if", "then", "else")
SUBSCHEMA_LIST = ("allOf", "anyOf", "oneOf", "prefixItems")


def open_schemas(schema, path: str = "") -> list[str]:
    """Paths of subschemas that let an invented key through: an object
    schema without `additionalProperties: false`, or an empty/true schema.
    Walks the schema by its KEYWORDS, so a property that happens to be
    named `properties` is a name, not a keyword (review finding)."""
    where = path or "<root>"
    if schema is True or schema == {}:
        return [f"{where} accepts anything ({{}} / true)"]
    if not isinstance(schema, dict):
        return []
    out: list[str] = []
    t = schema.get("type")
    types = t if isinstance(t, list) else [t]
    is_object = "object" in types or any(k in schema for k in ("properties", "patternProperties"))
    if is_object and schema.get("additionalProperties") is not False:
        out.append(f"{where} is open — add \"additionalProperties\": false")
    for kw in SUBSCHEMA_MAPS:
        for name, sub in (schema.get(kw) or {}).items():
            out.extend(open_schemas(sub, f"{path}/{kw}/{name}"))
    for kw in SUBSCHEMA_ONE:
        sub = schema.get(kw)
        if isinstance(sub, (dict, bool)):
            out.extend(open_schemas(sub, f"{path}/{kw}"))
    if isinstance(schema.get("items"), list):
        for i, sub in enumerate(schema["items"]):
            out.extend(open_schemas(sub, f"{path}/items[{i}]"))
    for kw in SUBSCHEMA_LIST:
        for i, sub in enumerate(schema.get(kw) or []):
            out.extend(open_schemas(sub, f"{path}/{kw}[{i}]"))
    return out


def check(root: Path = ROOT, pairs=None, instanceless=None) -> list[str]:
    try:
        import jsonschema
    except ImportError:
        return ["jsonschema is not installed — pip install 'jsonschema>=4.18,<5' (requirements.txt)"]
    pairs = PAIRS if pairs is None else pairs
    instanceless = INSTANCELESS if instanceless is None else instanceless
    problems: list[str] = []

    def valid_schema(rel: str):
        schema = _load(root, rel, problems)
        if schema is None:
            return None
        cls = jsonschema.validators.validator_for(schema, default=None)
        if cls is None:
            problems.append(f"{rel}: $schema dialect {schema.get('$schema')!r} is unknown to jsonschema")
            return None
        try:
            cls.check_schema(schema)
        except jsonschema.SchemaError as e:
            problems.append(f"{rel}: not a valid schema — {e.message}")
            return None
        return cls, schema

    for srel, irel in pairs:
        vs = valid_schema(srel)
        inst = _load(root, irel, problems)
        if vs is None or inst is None:
            continue
        cls, schema = vs
        validator = cls(schema, format_checker=cls.FORMAT_CHECKER)
        for err in sorted(validator.iter_errors(inst), key=lambda e: list(map(str, e.absolute_path))):
            where = "/".join(map(str, err.absolute_path)) or "<root>"
            problems.append(f"{irel}: {where}: {err.message[:160]}")
        for p in open_schemas(schema):
            problems.append(f"{srel}: schema at {p}")
    for srel, promised in instanceless:
        valid_schema(srel)
        if (root / promised).exists():
            problems.append(f"{promised} exists now — register ({srel}, {promised}) in PAIRS and close the schema")
    return problems


def main(argv: list[str]) -> int:
    if "--list" in argv:
        for s, i in PAIRS:
            print(f"{s}  <-  {i}")
        for s, promised in INSTANCELESS:
            print(f"{s}  (no instance yet; promised at {promised})")
        return 0
    problems = check()
    for p in problems:
        print(f"[efc-schema] {p}")
    if problems:
        print(f"[efc-schema] FAIL — {len(problems)} problem(s) across {len(PAIRS)} pair(s)")
        return 1
    print(f"[efc-schema] OK — {len(PAIRS)} schema/instance pair(s) valid and closed, {len(INSTANCELESS)} instanceless schema(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
