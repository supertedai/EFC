#!/usr/bin/env python3
"""Apply the desired Hindsight configuration to the `efc` bank.

Dry run by default: prints the current overrides, what would change, which
directives and pages are missing, and writes nothing. Pass --apply to write.

    pip install hindsight-client
    python3 integrations/hindsight/apply_efc_bank.py --bank efc-test
    python3 integrations/hindsight/apply_efc_bank.py --bank efc-test --apply

Defaults fit the Hetzner host: URL http://10.9.0.2:8006 (WireGuard to byopus12),
token MCP_HINDSIGHT_<BANK>_API_KEY (falls back to MCP_HINDSIGHT_EFC_API_KEY)
from ~/.hermes/.env. Override with HINDSIGHT_URL / HINDSIGHT_API_KEY.

Safe by construction: entity_labels are merged additively (existing label
groups, e.g. `lesson`, are never dropped or changed); missions the bank
already overrides are kept unless --replace-missions; the full config is
backed up to ~/.hermes/bankconfig-backup/ before any write and read back after.

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
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = HERE / "efc_bank.config.json"
# Hindsight API on byopus12 over the WireGuard tunnel (as in hermes-opus/metrikk/lesson-label.py).
DEFAULT_URL = "http://10.9.0.2:8006"
HERMES_ENV = Path.home() / ".hermes" / ".env"
BACKUP_DIR = Path.home() / ".hermes" / "bankconfig-backup"
PROTECTED_TEXT = ("retain_mission", "observations_mission", "reflect_mission")


def hermes_env_token(name: str) -> str:
    """Read a token from ~/.hermes/.env without printing it."""
    try:
        for line in HERMES_ENV.read_text(encoding="utf-8").splitlines():
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return ""


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
    ap.add_argument("--replace-missions", action="store_true",
                    help="replace retain/observations/reflect missions the bank already overrides")
    args = ap.parse_args()

    try:
        from hindsight_client import Hindsight
    except ImportError:
        print("pip install hindsight-client", file=sys.stderr)
        return 2

    url = os.environ.get("HINDSIGHT_URL") or os.environ.get("HINDSIGHT_API_URL") or DEFAULT_URL
    token = (os.environ.get("HINDSIGHT_API_KEY")
             or hermes_env_token("MCP_HINDSIGHT_" + args.bank.upper().replace("-", "_") + "_API_KEY")
             or hermes_env_token("MCP_HINDSIGHT_EFC_API_KEY"))
    kwargs = {"base_url": url}
    if token:
        kwargs["api_key"] = token
    client = Hindsight(**kwargs)
    spec = load_spec()
    bank = args.bank
    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"== {mode} on bank '{bank}' at {url} (token: {'yes' if token else 'none'})")

    # --- 1. config overrides ------------------------------------------------
    current = as_dict(client.get_bank_config(bank))
    resolved = current.get("config", {}) or {}
    overrides = current.get("overrides", {}) or {}

    if args.apply:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        backup = BACKUP_DIR / f"{bank}-config-{time.strftime('%Y%m%d_%H%M%S')}-{time.time_ns()}.json"
        # "x": never overwrite an earlier snapshot; fails before any API write.
        with backup.open("x", encoding="utf-8") as fh:
            fh.write(json.dumps(current, ensure_ascii=False, indent=1))
        print(f"\n[backup] {backup}")

    changes, kept = {}, []
    for k, v in spec["config"].items():
        if k == "entity_labels":
            have = [x for x in (resolved.get(k) or []) if isinstance(x, dict)]
            have_keys = {x.get("key") for x in have}
            new = [x for x in v if x["key"] not in have_keys]
            clash = [x["key"] for x in v if x["key"] in have_keys]
            print(f"\n[entity_labels] existing: {sorted(have_keys - {None})}")
            if clash:
                print(f"  same key already present, left untouched: {clash}")
            if new:
                print(f"  + adding: {[x['key'] for x in new]}")
                changes[k] = have + new          # additive: never drop existing labels
            continue
        if resolved.get(k) == v:
            continue
        if k in PROTECTED_TEXT and overrides.get(k) is not None and not args.replace_missions:
            kept.append(k)                        # a hand-written mission is never overwritten silently
            continue
        changes[k] = v

    short = lambda x: (json.dumps(x, ensure_ascii=False)[:110] + "…") if len(json.dumps(x, ensure_ascii=False)) > 110 else json.dumps(x, ensure_ascii=False)
    print(f"\n[config] {len(changes)} field(s) to change")
    for k, v in changes.items():
        if k != "entity_labels":
            print(f"  {k}: {short(resolved.get(k, '<unset>'))}  ->  {short(v)}")
    for k in kept:
        print(f"  = {k}: bank already has its own override, kept. Current:\n      {short(overrides[k])}\n"
              f"    (pass --replace-missions to replace it with the spec text)")
    if args.apply and changes:
        client.update_bank_config(bank, **changes)
        after = as_dict(client.get_bank_config(bank)).get("config", {}) or {}
        bad = [k for k in changes if k != "entity_labels" and after.get(k) != changes[k]]
        got = {x.get("key"): x for x in (after.get("entity_labels") or []) if isinstance(x, dict)}
        # Every group we sent (existing ones included) must come back with every
        # field we sent unchanged; the server may add defaults, so compare a subset.
        missing = sorted(w["key"] for w in changes.get("entity_labels", [])
                         if any(got.get(w["key"], {}).get(f) != val for f, val in w.items()))
        if bad or missing:
            print(f"  read back: NOT CONFIRMED fields={bad} labels={missing}. "
                  f"Stopping before directives/pages. Restore from {backup} if needed.")
            return 1
        print("  read back: OK")

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
