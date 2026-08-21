#!/usr/bin/env python3
"""Fail-closed, review-only public-agent planner for EFC.

The agent reads an explicit JSON source and emits a deterministic review plan.
It never writes docs/public, invokes git/GitHub, publishes, or performs network
calls. ``--mode pr`` means "prepare PR-oriented output", not "open a PR".
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import stat
import sys
from pathlib import Path
from typing import Any

VERSION = "1.0"
OUTPUT_DIR = Path("reports/efc-public-agent")
FORBIDDEN_OPS = {"publish", "delete", "overwrite_public_html", "automerge", "push"}
LOGGER = logging.getLogger("efc-public-agent")


class AgentError(ValueError):
    """An unsafe, ambiguous, or unsupported request."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def load_config(path: Path) -> dict[str, Any]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AgentError(f"cannot read config: {path}: {exc}") from exc
    if not isinstance(config, dict):
        raise AgentError("config must be a JSON object")
    required = {"version", "review_only", "publish", "permissions", "source_files", "output_dir"}
    missing = sorted(required - set(config))
    if missing:
        raise AgentError(f"config missing required keys: {', '.join(missing)}")
    if config["version"] != VERSION or config["review_only"] is not True:
        raise AgentError("only review-only config version 1.0 is supported")
    if config["publish"] is not False:
        raise AgentError("publish must be explicitly false (fail closed)")
    if config["permissions"] != {"contents": "read", "pull_requests": "none"}:
        raise AgentError("permissions must be read-only and must not create pull requests")
    if (not isinstance(config["source_files"], list) or not config["source_files"]
            or not all(isinstance(item, str) and item for item in config["source_files"])):
        raise AgentError("source_files must be a non-empty list")
    if config["output_dir"] != str(OUTPUT_DIR):
        raise AgentError(f"output_dir must be the fixed allowlisted path: {OUTPUT_DIR}")
    if config.get("operations") != ["review"]:
        raise AgentError("operations must be exactly ['review']")
    return config


def _has_symlink_component(root: Path, target: Path) -> bool:
    """Return true if an existing component between root and target is a symlink."""
    current = root
    for part in target.relative_to(root).parts:
        current /= part
        if current.is_symlink():
            return True
    return False


def safe_output(repo: Path, output_dir: str) -> Path:
    root = repo.resolve()
    if output_dir != str(OUTPUT_DIR):
        raise AgentError(f"output_dir must be the fixed allowlisted path: {OUTPUT_DIR}")
    target = root / OUTPUT_DIR
    if _has_symlink_component(root, target):
        raise AgentError("output_dir may not contain symlinked components")
    return target


def read_records(repo: Path, entries: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw in entries:
        source_parts = raw.split("/")
        if (not raw or "\\" in raw or Path(raw).is_absolute()
                or any(part in {"", ".", ".."} for part in source_parts)):
            raise AgentError(f"unsafe source path: {raw}")
        path = repo / raw
        resolved = path.resolve()
        if repo.resolve() not in resolved.parents or _has_symlink_component(repo.resolve(), path):
            raise AgentError(f"source path escapes repository: {raw}")
        if not path.exists() or path.is_symlink() or not stat.S_ISREG(path.stat().st_mode):
            raise AgentError(f"source file is missing: {raw}")
        try:
            data = json.loads(resolved.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise AgentError(f"invalid source JSON {raw}: {exc}") from exc
        if isinstance(data, dict):
            data = data.get("records", data.get("items"))
        if not isinstance(data, list):
            raise AgentError(f"source {raw} must contain a records/items list")
        for record in data:
            if not isinstance(record, dict):
                raise AgentError(f"source {raw} contains a non-object record")
            enriched = dict(record)
            enriched["_source_file"] = raw
            records.append(enriched)
    return records


def opus_adapter() -> dict[str, str]:
    """Describe the optional Opus boundary without making a network call.

    V1 is deterministic and disabled by default. A future adapter may use
    ``OPUS_API_URL`` and ``OPUS_API_KEY``; enabling an unknown adapter fails
    closed rather than silently ignoring the operator's configuration.
    """
    selected = os.environ.get("EFC_OPUS_ADAPTER", "disabled")
    if selected not in {"disabled", ""}:
        raise AgentError(f"unsupported Opus adapter: {selected}")
    return {"adapter": "disabled", "configured": "false"}


def build_plan(repo: Path, config: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    operations = config.get("operations", ["review"])
    if operations != ["review"]:
        unsupported = sorted(set(operations) - {"review"}) if isinstance(operations, list) else [str(operations)]
        raise AgentError(f"unsupported operations: {', '.join(unsupported)}")
    normalized = []
    seen: set[str] = set()
    for record in records:
        identifier = record.get("id")
        title = record.get("title")
        target = record.get("target")
        if not all(isinstance(v, str) and v.strip() for v in (identifier, title, target)):
            raise AgentError("each record requires non-empty string id, title, and target")
        if identifier in seen:
            raise AgentError(f"ambiguous duplicate id: {identifier}")
        seen.add(identifier)
        target_parts = target.split("/")
        public = repo.resolve() / "docs" / "public"
        target_path = repo.resolve() / Path(*target_parts)
        if (target_parts[:2] != ["docs", "public"] or len(target_parts) < 3
                or not target.endswith(".html")
                or any(part in {"", ".", ".."} for part in target_parts)
                or "\\" in target or not target_path.is_file()
                or target_path.is_symlink() or _has_symlink_component(repo.resolve(), target_path)
                or public not in target_path.resolve().parents):
            raise AgentError(f"unsafe or unsupported target: {target}")
        citations = record.get("citations", [record["_source_file"]])
        if (not isinstance(citations, list) or not citations
                or not all(isinstance(item, str) and item.strip() for item in citations)):
            raise AgentError(f"record {identifier} requires non-empty string citations")
        normalized.append({"id": identifier, "target": target, "title": title.strip(),
                           "citations": sorted(set(item.strip() for item in citations))})
    normalized.sort(key=lambda item: (item["target"], item["id"]))
    plan = {
        "agent": "efc-public-agent",
        "version": VERSION,
        "mode": "review-only",
        "operations": ["review"],
        "records": normalized,
        "public_html_mutation": False,
        "autonomous_publish": False,
        "review_required": True,
        "opus": opus_adapter(),
    }
    plan["plan_sha256"] = hashlib.sha256(_canonical(plan).encode()).hexdigest()
    return plan


def run(repo: Path, config_path: Path, mode: str, write: bool) -> dict[str, Any]:
    LOGGER.info("starting mode=%s repo=%s", mode, repo)
    config = load_config(config_path)
    if any(op in FORBIDDEN_OPS for op in config.get("operations", [])):
        raise AgentError("forbidden operation requested")
    output = safe_output(repo, config["output_dir"])
    plan = build_plan(repo, config, read_records(repo, config["source_files"]))
    plan["requested_mode"] = mode
    if mode not in {"dry-run", "pr"}:
        raise AgentError(f"unsupported mode: {mode}")
    if write:
        output.mkdir(parents=True, exist_ok=True)
        (output / "public-agent-plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (output / "public-agent-pr.md").write_text(
            "# EFC public-agent review plan\n\n"
            "This is review-only output. A maintainer must inspect and apply any change.\n\n"
            f"Plan SHA-256: `{plan['plan_sha256']}`\n\n"
            + "\n".join(f"- `{r['target']}` — {r['title']} ({r['id']})" for r in plan["records"])
            + "\n",
            encoding="utf-8",
        )
    LOGGER.info("completed mode=%s records=%d plan_sha256=%s", mode, len(plan["records"]), plan["plan_sha256"])
    return plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config/efc-public-agent.json"))
    parser.add_argument("--mode", choices=("dry-run", "pr"), default="dry-run")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    logging.basicConfig(level=os.environ.get("EFC_LOG_LEVEL", "WARNING"), format="%(levelname)s %(message)s")
    args = parser.parse_args(argv)
    try:
        plan = run(args.repo.resolve(), args.config if args.config.is_absolute() else args.repo / args.config, args.mode, args.mode == "pr")
    except AgentError as exc:
        print(f"efc-public-agent: ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(plan, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
