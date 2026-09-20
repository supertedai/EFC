#!/usr/bin/env python3
"""validate_risk_register.py — fail-closed control of the risk register.

The register is append-only and lives in governance/risiko/risiko-register.jsonl.
One line = one risk post. This control is the register's own guard:

  1. Schema: every field exists, has the right type, and UNKNOWN fields are
     rejected. The register is closed — a field that is not in the
     specification is a change of the register, not a piece of information in
     a post.
  2. Enums: type, klasse, sannsynlighet, alvorlighet, status, gate_decision,
     registerversjon. An unknown value = error (no «unknown» escape hatch).
  3. Identity: risk_id is unique, has the form RISK-<TYPE>-<4 digits>, and the
     TYPE segment must agree with `type`. supersedes/related_ids must point at
     risk_ids that exist in the register — a dangling reference is an error.
  4. Fail-closed coupling between score and class: a score of 16+ may NOT be
     called green, and 4+ not green. The class may be stricter than the score
     (a qualitative judgement), never laxer.
  5. The gate: a red class requires gate_required=true; gate_required=true
     requires gate_decision in {venter, godkjent, avslått}; a CLOSED post
     requires a decided decision; and a decided decision requires
     gate_besluttet_av = «menneske». No automation can close a gate.
  6. Ownership: `eier` must be one of the owners in the ownership register,
     every id in `berorte_komponenter` must be found there, and every file
     under governance/risiko/ must hit a component glob («0 files without an
     owner» applies to the register itself).
  7. No self-review: the reviewer must differ from the performer.
  8. Evidence: every link is prefixed `repo:` (the path must exist in the
     tree), `url:` (http/https) or `ekstern:` (a source outside the tree —
     honest marking instead of a false repo path).
  9. Append-only is a git property: with --base <ref> a diff that removes or
     changes a line in risiko-register.jsonl is rejected — with ONE exception:
     the closing fields (status, gate_decision, gate_besluttet_av,
     sist_vurdert) on an existing post may be changed instead of appended,
     because that is the human decision path. Everything else (deletion,
     rewriting another field, reordering) is still forbidden. The measurement
     is hermetic: which repo it reads comes from `rot`, and the diff is read
     with --no-ext-diff, --no-textconv and --text, so a local git config
     (diff.external, textconv, binary) cannot blind the gate.

Usage:
  python3 scripts/maintenance/validate_risk_register.py [--json] [--base origin/main]
Exit: 0 = OK, 1 = error (including a tool error — the register is fail-closed).
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

ROT = Path(__file__).resolve().parents[2]
REGISTER = "governance/risiko/risiko-register.jsonl"
EIERREGISTER = "governance/ownership-register.json"

# Environment variables that move which repo git talks to. The gate measures
# the repo at a KNOWN path (`rot`), so an inherited GIT_DIR/GIT_WORK_TREE from
# the surroundings — another test process, a CI wrapper, a shell — points it
# elsewhere.
AMBARTE_REPO_VARS = (
    "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_CEILING_DIRECTORIES",
)

SKJEMA_VERSJON = "1.0"

FELTER: dict[str, str] = {
    "risk_id": "str",
    "type": "str",
    "hazard_or_deviation": "str",
    "source_change_id": "str",
    "release_id": "str|null",
    "berorte_komponenter": "list[str]",
    "arsak": "str",
    "konsekvens": "str",
    "barrierer": "list[str]",
    "sannsynlighet": "str",
    "alvorlighet": "str",
    "blast_radius_score": "int",
    "klasse": "str",
    "eier": "str",
    "utforer": "str",
    "reviewer": "str",
    "status": "str",
    "tiltak": "list[str]",
    "kanban_card_id": "str",
    "gate_required": "bool",
    "gate_decision": "str",
    "gate_besluttet_av": "str|null",
    "evidenslenker": "list[str]",
    "opprettet_tid": "str",
    "forfall": "str|null",
    "sist_vurdert": "str",
    "rest_risiko": "str",
    "supersedes": "list[str]",
    "related_ids": "list[str]",
    "registerversjon": "str",
}
VALGFRIE = {"gate_besluttet_av"}

TYPE_VERDIER = ("HAZID", "HAZOP", "BLAST_RADIUS", "GAP")
KLASSE_VERDIER = ("grønn", "gul", "rød")
SANNSYNLIGHET = ("lav", "middels", "høy")
ALVORLIGHET = ("lav", "middels", "høy", "kritisk")
STATUS_VERDIER = ("oppdaget", "lukket", "superseded")
GATE_DECISION = ("venter", "godkjent", "avslått", "ikke_nodvendig")
RISK_ID = re.compile(r"^RISK-(HAZID|HAZOP|BLAST_RADIUS|GAP)-[0-9]{4}$")
CARD_ID = re.compile(r"^(t_[0-9a-f]{8,}|pr[0-9]+)$")
CHANGE_ID = re.compile(r"^(t_[0-9a-f]{8,}|pr[0-9]+|[0-9a-f]{4,40}\.\.[0-9a-f]{4,40})$")
MAKS_SCORE = 256  # 4×4×4×4 — taket i blast-radius-modellen

# Minimumsklassen en gitt score kan ha. Strengere er lov, laxere er feil.
SCORE_MIN_KLASSE = ((16, "rød"), (4, "gul"))

# The closing fields are the ONLY fields that may be changed on an existing
# post instead of appended. They make up the human decision path: a red post
# goes from «venter» to «godkjent»/«avslått» by flipping status, gate_decision
# and gate_besluttet_av, and sist_vurdert is updated to the decision date.
# Everything else is immutable finding data — a change there is still
# not_append_only.
LUKKE_FELTER = ("status", "gate_decision", "gate_besluttet_av", "sist_vurdert")


def _er_tekst(v: object) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _type_feil(spes: str, v: object) -> bool:
    if spes == "str":
        return not _er_tekst(v)
    if spes == "str|null":
        return v is not None and not _er_tekst(v)
    if spes == "int":
        return not (isinstance(v, int) and not isinstance(v, bool))
    if spes == "bool":
        return not isinstance(v, bool)
    if spes == "list[str]":
        return not (isinstance(v, list) and all(_er_tekst(x) for x in v))
    return True


def _iso(verdi: str) -> bool:
    try:
        datetime.fromisoformat(str(verdi).replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def _dato(verdi: str) -> bool:
    try:
        date.fromisoformat(str(verdi))
        return True
    except ValueError:
        return False


def valider_post(post: object, linje: int, eierregister: dict,
                 kjente_ider: set[str]) -> list[dict]:
    feil: list[dict] = []

    def f(type_: str, **kw: object) -> None:
        feil.append({"type": type_, "linje": linje, **kw})

    if not isinstance(post, dict):
        f("not_object")
        return feil

    for navn, spes in FELTER.items():
        if navn not in post:
            if navn not in VALGFRIE:
                f("missing_field", felt=navn)
            continue
        if _type_feil(spes, post[navn]):
            f("bad_type", felt=navn, forventet=spes, fikk=type(post[navn]).__name__)
    for navn in post:
        if navn not in FELTER:
            f("unknown_field", felt=navn)

    rid = post.get("risk_id")
    if isinstance(rid, str) and rid.strip() and not RISK_ID.match(rid):
        f("bad_risk_id", risk_id=rid)
    if isinstance(rid, str) and isinstance(post.get("type"), str) and RISK_ID.match(rid):
        if rid.split("-")[1] != post["type"]:
            f("risk_id_type_mismatch", risk_id=rid, id_type=post["type"])

    for navn, gyldige in (("type", TYPE_VERDIER), ("klasse", KLASSE_VERDIER),
                          ("sannsynlighet", SANNSYNLIGHET),
                          ("alvorlighet", ALVORLIGHET),
                          ("status", STATUS_VERDIER),
                          ("gate_decision", GATE_DECISION)):
        v = post.get(navn)
        if _er_tekst(v) and v not in gyldige:
            f("bad_enum", felt=navn, verdi=v, gyldige=list(gyldige))

    if post.get("registerversjon") != SKJEMA_VERSJON:
        f("unknown_registerversjon", verdi=post.get("registerversjon"),
          forventet=SKJEMA_VERSJON)

    br = post.get("blast_radius_score")
    if isinstance(br, int) and not isinstance(br, bool) and not 1 <= br <= MAKS_SCORE:
        f("score_out_of_range", score=br, maks=MAKS_SCORE)
        br = None
    kls = post.get("klasse")
    if isinstance(br, int) and kls in KLASSE_VERDIER:
        min_klasse = next((k for grense, k in SCORE_MIN_KLASSE if br >= grense), "grønn")
        rang = {"grønn": 0, "gul": 1, "rød": 2}
        if rang[kls] < rang[min_klasse]:
            f("klasse_laxere_enn_score", score=br, klasse=kls, minst=min_klasse)

    gate_krevd = post.get("gate_required")
    avgjorelse = post.get("gate_decision")
    if kls == "rød" and gate_krevd is not True:
        f("rod_uten_gate", risk_id=rid)
    if gate_krevd is True and avgjorelse == "ikke_nodvendig":
        f("gate_krevd_men_ikke_nodvendig", risk_id=rid)
    if gate_krevd is False and avgjorelse != "ikke_nodvendig":
        f("gate_ikke_krevd_men_besluttet", risk_id=rid, gate_decision=avgjorelse)
    if post.get("status") == "lukket" and gate_krevd is True and avgjorelse not in ("godkjent", "avslått"):
        f("lukket_uten_gatebeslutning", risk_id=rid, gate_decision=avgjorelse)
    if avgjorelse in ("godkjent", "avslått") and post.get("gate_besluttet_av") != "menneske":
        f("gate_besluttet_av_ikke_menneske", risk_id=rid,
          gate_besluttet_av=post.get("gate_besluttet_av"))

    if _er_tekst(post.get("utforer")) and post.get("reviewer") == post.get("utforer"):
        f("selv_review", utforer=post.get("utforer"))

    eiere = eierregister.get("owners") or []
    if _er_tekst(post.get("eier")) and post["eier"] not in eiere:
        f("ukjent_eier", eier=post["eier"], gyldige=eiere)
    komp_ider = {c.get("id") for c in (eierregister.get("components") or [])}
    for kid in post.get("berorte_komponenter") or []:
        if kid not in komp_ider:
            f("ukjent_komponent", komponent=kid)

    for lenke in post.get("evidenslenker") or []:
        if not _er_tekst(lenke):
            continue
        if lenke.startswith("repo:"):
            sti = lenke[5:].split("#")[0]
            if not (ROT / sti).exists():
                f("evidens_sti_finnes_ikke", lenke=lenke)
        elif lenke.startswith("url:"):
            if not lenke[4:].startswith(("http://", "https://")):
                f("evidens_url_ugyldig", lenke=lenke)
        elif lenke.startswith("ekstern:"):
            if not lenke[8:].strip():
                f("evidens_ekstern_tom", lenke=lenke)
        else:
            f("evidens_uten_prefiks", lenke=lenke)

    for navn in ("opprettet_tid", "sist_vurdert"):
        v = post.get(navn)
        if isinstance(v, str) and v.strip() and not _iso(v):
            f("ugyldig_tid", felt=navn, verdi=v)
    forfall = post.get("forfall")
    if isinstance(forfall, str) and forfall.strip() and not _dato(forfall):
        f("ugyldig_dato", felt="forfall", verdi=forfall)

    if _er_tekst(post.get("kanban_card_id")) and not CARD_ID.match(post["kanban_card_id"]):
        f("bad_kanban_card_id", kanban_card_id=post["kanban_card_id"])
    if _er_tekst(post.get("source_change_id")) and not CHANGE_ID.match(post["source_change_id"]):
        f("bad_source_change_id", source_change_id=post["source_change_id"])

    for navn in ("supersedes", "related_ids"):
        for ref in post.get(navn) or []:
            if ref == rid:
                f("selvreferanse", felt=navn, risk_id=ref)
            elif ref not in kjente_ider:
                f("ukjent_referanse", felt=navn, risk_id=ref)

    return feil


def valider_innhold(register: Path, eierregister: dict, rot: Path) -> list[dict]:
    feil: list[dict] = []
    if not register.is_file():
        return [{"type": "missing_file", "msg": str(register)}]

    poster: list[tuple[int, object]] = []
    for nr, linje in enumerate(register.read_text(encoding="utf-8").splitlines(), 1):
        if not linje.strip():
            continue
        try:
            poster.append((nr, json.loads(linje)))
        except json.JSONDecodeError as ex:
            feil.append({"type": "invalid_json", "linje": nr, "msg": str(ex)[:100]})

    ider: set[str] = set()
    for _, post in poster:
        if isinstance(post, dict) and _er_tekst(post.get("risk_id")):
            if post["risk_id"] in ider:
                feil.append({"type": "duplicate_risk_id", "risk_id": post["risk_id"]})
            ider.add(post["risk_id"])

    for nr, post in poster:
        feil += valider_post(post, nr, eierregister, ider)

    # The files under governance/risiko/ are the register's own artefacts: they
    # must have an owner like everything else in the repo (validate_ownership.py
    # covers governance/**, and this is the register's own check that the rule
    # holds here).
    komponenter = eierregister.get("components") or []
    base = rot / "governance" / "risiko"
    if base.is_dir():
        for p in sorted(base.rglob("*")):
            if not p.is_file():
                continue
            rel = str(p.relative_to(rot))
            if not any(fnmatch.fnmatch(rel, g) for c in komponenter
                       for g in (c.get("coverage_glob") or [])):
                feil.append({"type": "unowned_file", "file": rel})
    return feil


def _uten_lukkefelter(post: dict) -> dict:
    return {k: v for k, v in post.items() if k not in LUKKE_FELTER}


def _lukkefelter_endret(gammel: dict, ny: dict) -> bool:
    return any((k in gammel) != (k in ny) or gammel.get(k) != ny.get(k)
               for k in LUKKE_FELTER)


def _git_miljo() -> dict[str, str]:
    """A git environment where «which repo» comes from the call, not the surroundings."""
    return {k: v for k, v in os.environ.items() if k not in AMBARTE_REPO_VARS}


def append_only(base: str, rot: Path) -> list[dict]:
    """The diff of risiko-register.jsonl shall ONLY add lines — with ONE exception.

    The closing fields (status, gate_decision, gate_besluttet_av, sist_vurdert)
    on an existing post may be changed instead of appended: that is the human
    decision path, and it happens as a line change («venter» → «godkjent»/«avslått»),
    not as a new line. Everything else — deleting a post, changing another
    field, or an identical line merely moved (reordering) — is not_append_only.

    The call is hermetic on purpose: a gate whose verdict can be changed by the
    git configuration outside the process is not a gate. `--no-ext-diff`
    closes `diff.external`/`GIT_EXTERNAL_DIFF`, `--no-textconv` closes a
    textconv driver, `--text` closes `diff.<driver>.binary` (which would
    otherwise let git answer «Binary files differ» without any removed line),
    and `_git_miljo()` drops the inherited GIT_* variables that point git at a
    repo other than `rot`.
    """
    r = subprocess.run(["git", "diff", "-U0", "--no-ext-diff", "--no-textconv",
                        "--text", base, "--", REGISTER],
                       cwd=str(rot), capture_output=True, timeout=60,
                       env=_git_miljo())
    if r.returncode != 0:
        return [{"type": "tool_error",
                 "msg": f"git diff against «{base}» failed: "
                        f"{r.stderr.decode('utf-8', 'replace').strip()[:200]}"}]
    linjer = r.stdout.decode("utf-8", errors="replace").splitlines()
    fjernet = [ln for ln in linjer if ln.startswith("-") and not ln.startswith("---")]
    lagt_til = [ln for ln in linjer if ln.startswith("+") and not ln.startswith("+++")]
    if not fjernet:
        return []

    def _post(ln: str) -> dict | None:
        try:
            post = json.loads(ln[1:])
        except (json.JSONDecodeError, IndexError):
            return None
        return post if isinstance(post, dict) else None

    ny_etter_rid: dict[str, dict] = {}
    for ln in lagt_til:
        post = _post(ln)
        if post is not None and isinstance(post.get("risk_id"), str):
            ny_etter_rid[post["risk_id"]] = post

    for ln in fjernet:
        gammel = _post(ln)
        rid = gammel.get("risk_id") if (gammel is not None
                                        and isinstance(gammel.get("risk_id"), str)) else None
        if gammel is None or rid is None or rid not in ny_etter_rid:
            # Deleted post, unreadable line, or rewritten to another risk_id.
            return [{"type": "not_append_only", "base": base,
                     "fjernede_linjer": len(fjernet), "eksempel": ln[:120]}]
        ny = ny_etter_rid[rid]
        if _uten_lukkefelter(gammel) != _uten_lukkefelter(ny):
            # A field other than the closing fields was changed.
            return [{"type": "not_append_only", "base": base, "risk_id": rid,
                     "fjernede_linjer": len(fjernet), "eksempel": ln[:120]}]
        if not _lukkefelter_endret(gammel, ny):
            # An identical line removed and added again = pure reordering.
            return [{"type": "not_append_only", "base": base, "risk_id": rid,
                     "fjernede_linjer": len(fjernet), "eksempel": ln[:120]}]
    return []


def hoved() -> int:
    p = argparse.ArgumentParser(description="Fail-closed kontroll av risikoregisteret")
    p.add_argument("--json", action="store_true")
    p.add_argument("--base", default=None,
                   help="git ref to require append-only against (e.g. origin/main or the PR base SHA)")
    p.add_argument("--register", default=None)
    p.add_argument("--eierregister", default=None)
    p.add_argument("--rot", default=None)
    a = p.parse_args()
    rot = Path(a.rot).resolve() if a.rot else ROT
    register = Path(a.register) if a.register else rot / REGISTER
    eiersti = Path(a.eierregister) if a.eierregister else rot / EIERREGISTER
    try:
        eierregister = json.loads(eiersti.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as ex:
        feil = [{"type": "tool_error", "msg": f"the ownership register could not be read: {a.eierregister or EIERREGISTER}: {ex}"}]
    else:
        feil = valider_innhold(register, eierregister, rot)
    if a.base:
        feil += append_only(a.base, rot)
    if a.json:
        print(json.dumps({"feil": feil}, ensure_ascii=False, indent=1))
    else:
        print(f"risikoregister: {len(feil)} feil")
        for x in feil[:20]:
            print("  ", x)
    return 1 if feil else 0


if __name__ == "__main__":
    raise SystemExit(hoved())
