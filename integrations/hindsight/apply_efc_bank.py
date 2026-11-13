#!/usr/bin/env python3
"""Apply the desired Hindsight configuration to the `efc` bank.

Dry run by default: prints the current overrides, what would change, which
directives and pages are missing, and writes nothing. Pass --apply to write.

    pip install hindsight-client
    export HINDSIGHT_URL=http://<host>:8888   # your Hindsight API
    export HINDSIGHT_API_KEY=...              # if the server requires one
    python3 integrations/hindsight/apply_efc_bank.py --bank efc-test
    python3 integrations/hindsight/apply_efc_bank.py --bank efc-test --apply

Recommended order: clone `efc` to `efc-test`
(POST /v1/default/banks/efc/clone?target_bank_id=efc-test&include_bank_config=false),
apply there, compare recall/entities, then apply to `efc`.

Entity labels only apply to memories retained AFTER the change. To clean up
existing entities that are whole claims, reprocess the bank's documents.
Existing directives are matched by name only; anything already there is left
untouched and listed so you can retire duplicates by hand.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = HERE / "efc_bank.config.json"


def load_spec() -> dict:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    spec["config"] = {k: v for k, v in spec["config"].items() if not k.startswith("_")}
    return spec


def as_dict(obj):
    if isinstance(obj, dict):
        return obj
    for attr in ("model_dump", "to_dict", "dict"):
        if hasattr(obj, attr):
            return getattr(obj, attr)()
    return dict(obj)


def walk_tree(nodes, path=""):
    for n in nodes or []:
        n = as_dict(n)
        full = f"{path}/{n['name']}"
        yield full, n
        yield from walk_tree(n.get("children"), full)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bank", default="efc")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--skip-pages", action="store_true")
    args = ap.parse_args()

    try:
        from hindsight_client import Hindsight
    except ImportError:
        print("pip install hindsight-client", file=sys.stderr)
        return 2

    url = os.environ.get("HINDSIGHT_URL") or os.environ.get("HINDSIGHT_API_URL")
    if not url:
        print("Set HINDSIGHT_URL to the Hindsight API base URL.", file=sys.stderr)
        return 2
    kwargs = {"base_url": url}
    if os.environ.get("HINDSIGHT_API_KEY"):
        kwargs["api_key"] = os.environ["HINDSIGHT_API_KEY"]
    client = Hindsight(**kwargs)
    spec = load_spec()
    bank = args.bank
    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"== {mode} on bank '{bank}' at {url}")

    # --- 1. config overrides ------------------------------------------------
    current = as_dict(client.get_bank_config(bank))
    resolved = current.get("config", {})
    changes = {k: v for k, v in spec["config"].items() if resolved.get(k) != v}
    print(f"\n[config] {len(changes)} of {len(spec['config'])} fields differ from the resolved config")
    for k, v in changes.items():
        old = resolved.get(k, "<unset>")
        short = lambda x: (json.dumps(x, ensure_ascii=False)[:110] + "…") if len(json.dumps(x, ensure_ascii=False)) > 110 else json.dumps(x, ensure_ascii=False)
        print(f"  {k}: {short(old)}  ->  {short(v)}")
    if args.apply and changes:
        client.update_bank_config(bank, **changes)
        print("  written.")

    # --- 2. directives ------------------------------------------------------
    existing = [as_dict(d) for d in as_dict(client.list_directives(bank_id=bank)).get("items", [])]
    names = {d.get("name") for d in existing}
    print(f"\n[directives] {len(existing)} existing:")
    for d in existing:
        print(f"  - {d.get('name')} (active={d.get('is_active', True)}): {str(d.get('content'))[:90]}")
    for d in spec["directives"]:
        if d["name"] in names:
            continue
        print(f"  + missing: {d['name']}")
        if args.apply:
            client.create_directive(bank_id=bank, name=d["name"], content=d["content"])
            print("    created.")

    # --- 3. pages (knowledge tree roots) -------------------------------------
    if not args.skip_pages:
        tree = as_dict(client.get_page_tree(bank))
        have = {p: n for p, n in walk_tree(tree.get("roots"))}
        print(f"\n[pages] {len(have)} existing nodes")
        for group in spec["pages"]:
            fpath = f"/{group['folder']}"
            folder = have.get(fpath)
            if folder is None:
                print(f"  + folder {fpath}")
                if args.apply:
                    folder = as_dict(client.create_page_folder(bank, name=group["folder"]))
            for p in group["pages"]:
                if f"{fpath}/{p['name']}" in have:
                    continue
                print(f"  + page {fpath}/{p['name']}")
                if args.apply:
                    client.create_page(bank, name=p["name"], source_query=p["source_query"],
                                       parent_id=folder["id"], tags=["efc"])

    print("\nDone." if args.apply else "\nNothing written. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
