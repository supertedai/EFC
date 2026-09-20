"""Which node bank the sealed atlas experiment reads.

The experiment in this directory (`key.json`, the two readers, `RESULTAT.md`) is
a CLOSED, DATED measurement: the questions and the objective key were written
and committed BEFORE the prototype existed, and the key's sha256 is pinned in
the tests so a silent edit of the key fails.

Its INPUT is therefore not «the atlas» — it is the atlas as it stood when the
key was sealed. Both readers used to read `origin/main` at run time, which
quietly made every sealed answer depend on a bank that is still being edited.
Measured 2026-09-19 on `origin/main` (`bbc2c3b1`): 4 of 12 tests failed, 8
passed — the seal was intact (`key.json` sha256 unchanged), the bank under the
readers was not.

This module names that input once, for the readers, the tests and the CLIs:

* ``SEAL_COMMIT`` — the commit that sealed the experiment; `key.json`, both
  readers and `RESULTAT.md` were added in it.
* ``SEAL_BANK_SHA256`` — sha256 of `schema/regime_nodes.jsonld` at that commit.
  Pinned the same way ``KEY_SHA256`` pins the key: a different bank is a
  different measurement, and that must fail here instead of looking like a
  result.
* ``LIVE_REF`` — ``origin/main``. Legitimate as an explicit ``--ref``, never as
  the default: a run against the living atlas answers a different question, and
  its answers are expected to differ from ``key.json``.

The seal commit lives on `main` and resolves in any full clone. In a shallow
clone the object is absent; that is reported as ``BankUnavailable`` naming the
fix, and is never papered over by silently reading another ref — an instrument
that falls back to a tree it was not pointed at is the failure class this whole
directory exists to make visible.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

#: Repository root, computed from this file: the readers must not depend on the
#: caller's working directory to decide WHICH tree they read.
ROOT = Path(__file__).resolve().parents[3]

RELATION_FILE = "schema/regime_nodes.jsonld"

#: The commit that sealed the experiment (2026-09-18 21:26 +0200, PR #564).
SEAL_COMMIT = "c70e004d508dbd341271bd3f272e656e8d14db1a"

#: sha256 of RELATION_FILE at SEAL_COMMIT. Measured 2026-09-20:
#: `git show c70e004d:schema/regime_nodes.jsonld | sha256sum`.
SEAL_BANK_SHA256 = "f61049c40463e3eaa22d6d822f165faba59b85d1c28864caba2a6df38f014b2a"

#: The living atlas. Read only when a caller asks for it by name.
LIVE_REF = "origin/main"


class BankUnavailable(RuntimeError):
    """The bank at the requested ref cannot be read in this clone."""


def read_bytes(ref: str = SEAL_COMMIT, path: str = RELATION_FILE) -> bytes:
    """The bytes of ``path`` at ``ref``, or ``BankUnavailable`` saying why not."""
    try:
        return subprocess.check_output(
            ["git", "show", f"{ref}:{path}"], cwd=ROOT, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        raise BankUnavailable(
            f"cannot read {path} at {ref} in {ROOT}: {error}. "
            f"The sealed experiment needs commit {SEAL_COMMIT} present in the "
            f"clone — fetch full history (`fetch-depth: 0`) instead of reading "
            f"another ref.") from error


def load(ref: str = SEAL_COMMIT) -> dict:
    """The node bank at ``ref``. Verifies the pin when the seal commit is read."""
    raw = read_bytes(ref)
    if ref == SEAL_COMMIT:
        digest = hashlib.sha256(raw).hexdigest()
        if digest != SEAL_BANK_SHA256:
            raise BankUnavailable(
                f"{RELATION_FILE} at {SEAL_COMMIT} hashes to {digest}, not the "
                f"pinned {SEAL_BANK_SHA256}. The snapshot moved — re-measure and "
                f"re-pin deliberately, in its own commit.")
    return json.loads(raw)


def load_sealed() -> dict:
    """The bank the key was written against. The default for tests and CLIs."""
    return load(SEAL_COMMIT)


def load_live() -> dict:
    """The living atlas as of ``origin/main``."""
    return load(LIVE_REF)
