# DEPRECATED (2026-09-17, publish-fanout deleg_f566784a): this one is
# GitHub-only and knows nothing of Figshare/DOI/release binding/human gate.
# CANONICAL: the efc-preprint-release helper (/opt/agent-work/Hetzner/hermes-skills/
# efc-preprint-release/scripts/efc_release_helper.py) via the efc-publisering MCP.
# Do not use this for new releases; removed once callers are migrated.
#!/usr/bin/env python3
"""Fail-closed GitHub publisher for a verified EFC release candidate.

This adapter intentionally does not alter the review-only public agent. It
publishes a clean, already-validated local commit through the GitHub Contents
/ Git Data API using GITHUB_TOKEN from the actual publisher runtime.

It never prints the token. A missing token, dirty worktree, stale base, or
failed remote readback is a hard failure. Use --dry-run to inspect the planned
publication without making remote writes.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class PublishError(RuntimeError):
    pass


@dataclass(frozen=True)
class Config:
    owner: str
    repo: str
    branch: str
    base_branch: str
    title: str
    body: str


def run_git(repo: str, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", repo, *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if p.returncode:
        raise PublishError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout.strip()


def api(token: str, method: str, url: str, payload: dict[str, Any] | None = None) -> Any:
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "efc-release-publisher/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:500]
        raise PublishError(f"GitHub API {method} {url} returned HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise PublishError(f"GitHub API unavailable: {exc.reason}") from exc


def parse_remote(repo: str) -> tuple[str, str]:
    remote = run_git(repo, "remote", "get-url", "origin")
    if "github.com" in remote:
        suffix = remote.split("github.com", 1)[-1].lstrip(":/")
    elif ":" in remote and remote.startswith("git@"):
        suffix = remote.split(":", 1)[1]
    else:
        raise PublishError(f"origin is not a GitHub owner/repo remote: {remote}")
    suffix = suffix.removesuffix(".git")
    parts = suffix.split("/")
    if len(parts) != 2 or not all(parts):
        raise PublishError(f"origin is not a GitHub owner/repo remote: {remote}")
    return parts[0], parts[1]


def verify_local(repo: str, commit: str, base_branch: str) -> tuple[str, str, list[tuple[str, str]]]:
    if run_git(repo, "status", "--porcelain"):
        raise PublishError("release worktree is dirty")
    actual = run_git(repo, "rev-parse", "HEAD")
    if actual != commit:
        raise PublishError(f"HEAD mismatch: expected {commit}, found {actual}")
    base = run_git(repo, "rev-parse", base_branch)
    statuses = run_git(repo, "diff", "--name-status", f"{base}..{commit}")
    changes: list[tuple[str, str]] = []
    for line in statuses.splitlines():
        if not line:
            continue
        bits = line.split("\t", 1)
        if len(bits) != 2:
            raise PublishError(f"unsupported git diff line: {line}")
        changes.append((bits[0], bits[1]))
    if not changes:
        raise PublishError("release has no changes relative to base")
    return actual, base, changes


def build_tree(repo: str, changes: list[tuple[str, str]], base_tree: str) -> list[dict[str, Any]]:
    tree: list[dict[str, Any]] = []
    for status, path in changes:
        if status.startswith("D"):
            tree.append({"path": path, "mode": "100644", "type": "blob", "sha": None})
            continue
        raw = open(os.path.join(repo, path), "rb").read()
        blob = {"content": base64.b64encode(raw).decode(), "encoding": "base64"}
        tree.append({"path": path, "mode": "100644", "type": "blob", "content": blob["content"], "encoding": "base64"})
    return tree


def publish(repo: str, cfg: Config, commit: str, dry_run: bool = False) -> dict[str, Any]:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise PublishError("CAPABILITY_BLOCKED: GITHUB_TOKEN is not available in publisher runtime")
    actual, base, changes = verify_local(repo, commit, cfg.base_branch)
    owner, project = cfg.owner, cfg.repo
    root = f"https://api.github.com/repos/{owner}/{project}"
    base_ref = api(token, "GET", f"{root}/git/ref/heads/{cfg.base_branch}")
    base_sha = base_ref["object"]["sha"]
    local_base_sha = run_git(repo, "rev-parse", cfg.base_branch)
    if base_sha != local_base_sha:
        raise PublishError(f"stale base: local={local_base_sha}, remote={base_sha}")
    if dry_run:
        return {"dry_run": True, "owner": owner, "repo": project, "branch": cfg.branch, "base": base_sha, "commit": actual, "changes": [p for _, p in changes]}

    base_commit = api(token, "GET", f"{root}/git/commits/{base_sha}")
    tree_payload = {"base_tree": base_commit["tree"]["sha"], "tree": build_tree(repo, changes, base_commit["tree"]["sha"])}
    new_tree = api(token, "POST", f"{root}/git/trees", tree_payload)
    new_commit = api(token, "POST", f"{root}/git/commits", {"message": cfg.title, "tree": new_tree["sha"], "parents": [base_sha]})
    try:
        api(token, "POST", f"{root}/git/refs", {"ref": f"refs/heads/{cfg.branch}", "sha": new_commit["sha"]})
    except PublishError as exc:
        if "HTTP 422" not in str(exc):
            raise
        api(token, "PATCH", f"{root}/git/refs/heads/{cfg.branch}", {"sha": new_commit["sha"], "force": False})
    prs = api(token, "GET", f"{root}/pulls?head={owner}:{cfg.branch}&base={cfg.base_branch}&state=open")
    pr = prs[0] if prs else api(token, "POST", f"{root}/pulls", {"title": cfg.title, "head": cfg.branch, "base": cfg.base_branch, "body": cfg.body})
    remote_ref = api(token, "GET", f"{root}/git/ref/heads/{cfg.branch}")
    if remote_ref["object"]["sha"] != new_commit["sha"]:
        raise PublishError("remote readback mismatch after publish")
    return {"published": True, "commit": new_commit["sha"], "branch": cfg.branch, "pr_url": pr.get("html_url"), "pr_number": pr.get("number"), "changes": [p for _, p in changes]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--base-branch", default="origin/main")
    parser.add_argument("--branch", required=True)
    parser.add_argument("--title", default="chore(efc): verified public-surface maintenance")
    parser.add_argument("--body", default="Automated Tier A/B EFC maintenance candidate. Gates and provenance were verified before publication.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    owner, project = parse_remote(args.repo)
    base_branch = args.base_branch.removeprefix("origin/")
    cfg = Config(owner, project, args.branch, base_branch, args.title, args.body)
    try:
        result = publish(args.repo, cfg, args.commit, args.dry_run)
        print(json.dumps(result, sort_keys=True))
        return 0
    except PublishError as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
