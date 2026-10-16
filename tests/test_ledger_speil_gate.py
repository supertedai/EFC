"""The ledger-twins gate must stay a gate: it watches everything that can
drift, it fails on drift, and it writes nothing.

`scripts/maintenance/efc_ledger_speil.py` is the only writer of the two
projections and `tests/test_ledger_speil.py` locks the identities, but neither
had an automatic path until `.github/workflows/efc-ledger-speil.yml` (card
t_42ce76dd). This file locks the GATE itself, in the shape the house uses for a
new gate (cf. `tests/test_spraakvakt.py`):

* the trigger set is every file that can drift, plus the workflow itself — a
  narrowed path filter must be a red gate, not a silent hole;
* the job runs the check, the writer-in-fixpoint and the lock, and no subset
  of them: dropping a step is a red gate;
* the workflow is read-only;
* and the CLI contract is proven where the gate uses it: a mutated twin makes
  the command exit 1, a restored twin makes it exit 0 — repeated, because a
  verdict that flaps between runs is not a verdict.

The probes run the SCRIPT as a subprocess on a synthetic tree of real copies —
the gate's step is a command, and it is the exit code of that command that
fails a PR. A copy, never a symlink: the writer step rewrites its two inputs,
and a symlink would carry that write into the checkout under test.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import yaml
except ImportError:  # pragma: no cover - requirements.txt carries PyYAML
    raise SystemExit(
        "PyYAML is required: the gate's shape (triggers, steps, read-only) is "
        "asserted from the workflow file, and a lock that skips is not a lock. "
        "requirements.txt and the gate's own CI job install it.")

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "efc-ledger-speil.yml"
MIRROR = ROOT / "scripts" / "maintenance" / "efc_ledger_speil.py"
LEDGER = ROOT / "docs" / "validation-ledger" / "data" / "ledger.json"
GRAV = ROOT / "docs" / "validation-ledger" / "data" / "grav.json"
INDEX = ROOT / "docs" / "validation-ledger" / "index.md"

SELV = ".github/workflows/efc-ledger-speil.yml"
DRIFT_FILES = {
    "docs/validation-ledger/data/ledger.json",
    "docs/validation-ledger/data/grav.json",
    "docs/validation-ledger/index.md",
    "scripts/maintenance/efc_ledger_speil.py",
    "tests/test_ledger_speil.py",
    "tests/test_ledger_speil_gate.py",
}

CHECK = "python3 scripts/maintenance/efc_ledger_speil.py"
WRITE = "python3 scripts/maintenance/efc_ledger_speil.py --skriv"
LOCK = "python3 -m pytest tests/test_ledger_speil.py tests/test_ledger_speil_gate.py -q"

CLAIM_ROW = re.compile(r"^\| (\d+) \| (.*) \| ([^|]*) \| ([^|]*) \|\s*$")


# --------------------------------------------------------------------------
# the gate's shape: triggers, steps, and no writes
# --------------------------------------------------------------------------

def _workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _runs(doc: dict) -> list[str]:
    return [step.get("run", "") for step in doc["jobs"]["ledger-speil"]["steps"]]


def test_the_workflow_watches_every_file_that_can_drift():
    """The canonical ledger, both projections, the mirror and its lock — plus
    the workflow itself, so that narrowing the filter makes this test red."""
    doc = _workflow()
    triggers = doc[True] if True in doc else doc["on"]
    paths = triggers["pull_request"]["paths"]
    assert paths == triggers["push"]["paths"], (
        "push and pull_request must watch the same files (t_0d65ccdf)")
    assert set(paths) == DRIFT_FILES | {SELV}, sorted(set(paths))


def test_the_job_runs_the_check_the_writer_and_the_lock():
    """Three steps, one source. Each one is named here: dropping any of them
    narrows the gate, and a narrowed gate is the drift class coming back."""
    linjer = [ln.strip() for gruppe in _runs(_workflow()) for ln in gruppe.splitlines()]
    assert CHECK in linjer, "the mirror's own check must run"
    assert WRITE in linjer, "the writer must run, or the byte-level class is blind"
    assert "git diff --quiet" in "\n".join(linjer), (
        "the writer is only a gate when its output is compared with the commit")
    assert LOCK in linjer, "the locked identities must run"


def test_the_workflow_is_read_only():
    """A PR gate may inspect and refuse; it may not commit, push or open PRs.

    The canonical read-only list is `tests/test_workflows_parse.py`, which
    names the long-standing gates; this one keeps its own lock so the property
    travels with the gate — and pins the permission scope as well."""
    text = WORKFLOW.read_text(encoding="utf-8")
    for forbudt in ("git push", "git commit", "gh pr create"):
        assert forbudt not in text, f"{forbudt} has no place in a validation gate"
    assert "contents: read" in text


# --------------------------------------------------------------------------
# the probes: the command the gate runs, on a tree that drifts
# --------------------------------------------------------------------------

def _tree(tmp_path: Path, git: bool = False) -> Path:
    """Real copies of the twins and the mirror, optionally in a git repo."""
    rot = tmp_path / "repo"
    (rot / "docs" / "validation-ledger" / "data").mkdir(parents=True)
    (rot / "scripts" / "maintenance").mkdir(parents=True)
    for ekte in (LEDGER, GRAV, INDEX):
        shutil.copy2(ekte, rot / ekte.relative_to(ROOT))
    shutil.copy2(MIRROR, rot / MIRROR.relative_to(ROOT))
    if git:
        _git(rot, "init", "-q")
    return rot


def _git(rot: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-c", "user.email=gate@test", "-c", "user.name=gate",
                        *args], cwd=rot, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, f"git {' '.join(args)}: {r.stdout}{r.stderr}"
    return r


def _skriv(rot: Path, ekte: Path, tekst: str) -> None:
    (rot / ekte.relative_to(ROOT)).write_text(tekst, encoding="utf-8")


def _kjor(rot: Path, *flagg: str) -> subprocess.CompletedProcess:
    """The gate's command, exactly as the workflow spells it."""
    return subprocess.run(
        [sys.executable, str(rot / MIRROR.relative_to(ROOT)), *flagg],
        cwd=rot, capture_output=True, text=True, timeout=180)


def _mutert_grav() -> str:
    doc = json.loads(GRAV.read_text(encoding="utf-8"))
    for claim in doc["claims"]:
        if claim.get("text"):
            claim["text"] = claim["text"] + " x"   # one character of drift
            return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    raise AssertionError("grav.json carries no claim text to mutate")


def _mutert_index() -> str:
    linjer = INDEX.read_text(encoding="utf-8").split("\n")
    for n, ln in enumerate(linjer):
        m = CLAIM_ROW.match(ln)
        if not m or m.group(2) == "—" or not m.group(2).endswith("..."):
            continue
        celle = m.group(2)[:10] + "X" + m.group(2)[11:]
        linjer[n] = f"| {m.group(1)} | {celle} | {m.group(3)} | {m.group(4)} |"
        return "\n".join(linjer)
    raise AssertionError("index.md carries no claim row to mutate")


@pytest.mark.parametrize("runde", [1, 2, 3])
@pytest.mark.parametrize("tvilling", ["grav.json", "index.md"])
def test_a_mutated_twin_fails_the_command_and_a_restored_twin_passes(
        tmp_path, tvilling, runde):
    """mutated = exit 1, restored = exit 0 — repeated on purpose."""
    rot = _tree(tmp_path)
    ekte = GRAV if tvilling == "grav.json" else INDEX
    ren = _kjor(rot)
    assert ren.returncode == 0, ren.stdout + ren.stderr

    _skriv(rot, ekte, _mutert_grav() if tvilling == "grav.json" else _mutert_index())
    mutert = _kjor(rot)
    assert mutert.returncode == 1, (
        f"the gate passed a drifted {tvilling}: {mutert.stdout}{mutert.stderr}")
    assert "ERROR" in mutert.stdout, mutert.stdout

    _skriv(rot, ekte, ekte.read_text(encoding="utf-8"))
    tilbake = _kjor(rot)
    assert tilbake.returncode == 0, tilbake.stdout + tilbake.stderr


def test_the_writer_step_sees_the_class_the_identities_cannot(tmp_path):
    """A re-encoded twin: every identity still holds (the claim texts are equal
    as strings), so the check is green — but the bytes are not what the mirror
    emits, and without the writer step `--skriv` would produce a spurious
    whole-file diff the next time anything regenerated the pair."""
    rot = _tree(tmp_path, git=True)
    _git(rot, "add", "-A")
    _git(rot, "commit", "-q", "-m", "clean twins")

    doc = json.loads(GRAV.read_text(encoding="utf-8"))
    _skriv(rot, GRAV, json.dumps(doc, ensure_ascii=True, indent=2) + "\n")
    identiteter = _kjor(rot)
    assert identiteter.returncode == 0, (
        "the identities alone cannot see a re-encoding — that is the point of "
        f"the second step: {identiteter.stdout}{identiteter.stderr}")

    _git(rot, "add", "-A")
    _git(rot, "commit", "-q", "-m", "re-encoded twin")

    # step 2: run the writer, then compare with the commit.
    skriv = _kjor(rot, "--skriv")
    assert skriv.returncode == 0, skriv.stdout + skriv.stderr
    diff = subprocess.run(["git", "diff", "--quiet", "--",
                           str(GRAV.relative_to(ROOT)), str(INDEX.relative_to(ROOT))],
                          cwd=rot, capture_output=True, text=True, timeout=60)
    assert diff.returncode == 1, "the writer step must refuse a re-encoded twin"

    # and once the writer's own output is committed, the same step is green:
    # the gate demands the emitter's bytes, not merely a parseable twin.
    _git(rot, "add", "-A")
    _git(rot, "commit", "-q", "-m", "the emitter's bytes")
    assert _kjor(rot, "--skriv").returncode == 0
    diff = subprocess.run(["git", "diff", "--quiet", "--",
                           str(GRAV.relative_to(ROOT)), str(INDEX.relative_to(ROOT))],
                          cwd=rot, capture_output=True, text=True, timeout=60)
    assert diff.returncode == 0, "the writer's own output must be a fixpoint"
