#!/usr/bin/env python3
"""
Concept candidates — fill everything mechanical, leave every judgement open
==========================================================================

The C11 registry holds five concepts. The tree carries many more terms that
someone has proposed registering: EFC-R/S/D/C, S0/S1, L0–L3, Core Lock, EBE,
RCMP, Homo Fluxus, and the cognition and ASI vocabularies. Writing those by
hand is where errors come from — two drafts of efc:HME were wrong before the
third, both times because a source was chosen by association rather than by
reading.

So this tool does the reading and none of the choosing. Per term it reports:

  identity      is the term already declared in docs/ontology.jsonld (C9)
  forms         which spellings were searched, and which ones matched
  occurrences   how many tracked files carry each form, and where
  sources       DOIs the tree PUBLISHES for papers that NAME the term, from
                figshare/doi-map.json alone. Measured 2026-09-06: every
                docs/papers/efc/*/index.json with a top-level `doi` is also
                in doi-map, so there is no gap today — but a paper that had
                one would be invisible here while C11 accepts its DOI
  definitions   candidate sentences, each with a GitHub line anchor, ranked
                by whether the sentence defines rather than merely uses
  open          the decisions a person must make, listed explicitly

and then stops. It never writes docs/concepts.jsonld.

What that does and does not protect: C11 refuses a canonical entry, and any
entityType finer than `concept`, without an efc:attested entry. It does NOT
refuse a `candidate` entry whose skos:definition is one of these sentences —
review built one mechanically from this tool's own output and the gate passed
it. Choosing WHICH sentence defines a term is judgement — for RCMP there are 78
candidates today — and only a reader stands between the ranking and the
registry. Do not read the top of
the list as an answer.

Why forms matter (measured 2026-09-06): "oscillering" has 0 occurrences while
"oscillat" is in 23 of the 610 files this tool reads, and in 60 tracked files
altogether. A null on one spelling is a search, not an
absence, so a NOT-FOUND result here carries the list of forms tried.

DECLARED LIMIT: the forms are spellings, NOT translations. `oscillering` still
comes back NOT IN TREE even though `oscillat*` is there, because no dictionary
is consulted. Card 8/11 asked for English forms; this delivers the second half
of that card — that negative evidence names what was searched. Read a
NOT-IN-TREE result as "these spellings are absent", never as "the concept is
absent".

Ranking is a heuristic and says so. A sentence that contains "is a", "is
defined as", "we define", "refers to", "denotes" or "introduces the" near the
term scores above one that merely mentions it, and a sentence from a paper's
own abstract scores above one from a note. The tool prints the score so a
reader can disagree with it; it never picks.

Usage:
  efc_candidates.py                 the terms in TERMS, human-readable
  efc_candidates.py --json          the same as JSON, for a later step
  efc_candidates.py TERM [TERM …]   any term, including one not in TERMS
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = "https://github.com/supertedai/EFC/blob/main/"
ONTOLOGY = "docs/ontology.jsonld"
REGISTRY = "docs/concepts.jsonld"
TEXT_SUFFIXES = (".md", ".tex", ".txt")
SKIP_DIRS = ("/.git/", "node_modules/", "/_archived/")
# This tool's own documentation quotes terms as examples, and became the top
# definition candidate for efc:HME (review finding). A tool must not cite
# itself as a source about the thing it reports on.
SKIP_FILES = ("scripts/maintenance/README.md",)

# The terms proposed for registration. Present in the tree 2026-09-06 EXCEPT
# `ASI`, which occurs only in JSON and HTML and not in the .md/.tex/.txt this
# tool reads — kept so the report says so out loud. Not a promise that any of
# them should be registered.
TERMS = (
    "EFC-R", "EFC-S", "EFC-D", "EFC-C", "S0", "S1", "L0", "L1", "L2", "L3",
    "Core Lock", "EBE", "RCMP", "Homo Fluxus", "resonance", "self-model",
    "agency", "intention", "episenter", "proxy", "regime", "constraint",
    "world model", "validation ledger", "ASI",
)

DEFINING = (
    r"\bis a\b", r"\bis an\b", r"\bis the\b", r"\bis defined as\b", r"\bwe define\b",
    r"\brefers to\b", r"\bdenotes\b", r"\bintroduces the\b", r"\bpresents the\b",
    r"\bstands for\b",
)   # `models` was here and matched the noun: `regime`'s top candidate was a
    # plain use, "standard models succeed or fail" (review finding).


def forms(term: str) -> list[str]:
    """Spellings to search for. A null on one of them is not an absence."""
    out = {term, term.lower(), term.upper()}
    out.add(term.replace("-", " "))
    out.add(term.replace(" ", "-"))
    out.add(term.replace(" ", "_"))
    out.add(term.replace("–", "-"))          # en dash, which the tree uses
    out.add(term.replace("-", "–"))
    ord_ = [w for w in re.split(r"[^A-Za-z0-9]+", term) if w]
    if len(ord_) > 1:                         # acronym of a multi-word term,
        acronym = "".join(w[0] for w in ord_).upper()   # split on punctuation
        if len(acronym) >= 3:                 # too, or Grid–Higgs gives GF
            out.add(acronym)                  # and "CL" for Core Lock matched CLASS
    if not term.endswith("s"):
        out.add(term + "s")
    if term.endswith("y"):
        out.add(term[:-1] + "ies")
    return sorted(f for f in out if f)


class NotAGitTree(RuntimeError):
    """Raised rather than answered. A failing `git ls-files` used to produce
    an empty file list, and every term then came back NOT IN TREE — a search
    reported as an absence, over the whole tree at once, which is the error
    class this tool exists to kill (review finding)."""


def tracked_text_files(root: Path) -> list[str]:
    """Tracked text files, read with -z: a path with a space or a non-ASCII
    character is a path, and text-mode git output loses both."""
    out = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True)
    if out.returncode != 0:
        raise NotAGitTree(f"git ls-files failed in {root}: {out.stderr.decode('utf-8', 'replace').strip()}")
    files = [p for p in out.stdout.decode("utf-8", "surrogateescape").split("\0")
             if p.endswith(TEXT_SUFFIXES) and p not in SKIP_FILES
             and not any(s in "/" + p for s in SKIP_DIRS)]
    if not files:
        raise NotAGitTree(f"no tracked {'/'.join(TEXT_SUFFIXES)} files under {root} — refusing to report an absence")
    return files


def whole_word(form: str, text: str) -> bool:
    """A form matches only as a whole token. Without this, `CL` matched CLASS
    and `S0` matched S01 — measured on the first run of this tool. The
    boundary is `\\w`, not `[A-Za-z0-9]`, so `lock` does not match inside
    `blaalock` in a Norwegian note (review finding).

    Declared limits, measured 2026-09-06 under THIS boundary and not the
    previous one. `_` is a word character, so `rcmp` does NOT match in
    `src/rcmp_check.py`; two earlier drafts of this docstring said it did, and
    carried counts taken under the old boundary and described the wrong set.

    What still matches, with the counting rule written out so it can be
    re-run: lines where the matching form is the lowercase `rcmp` and the
    uppercase `RCMP` does not also match on that line. That is 10 lines in 5
    files — 6 in one paper's .tex source (LaTeX identifiers such as
    `\\texttt{rcmp\\_run/...}`) and 4 in four different MANIFEST.md files, each
    of the form "- `rcmp` - <description>". Counted any other way the number
    differs, which is why the rule is here and not just the number.

    The same boundary silently drops a term inside a subscripted name:
    `proxy` does not match in `alpha_proxy`, which cost a real candidate
    sentence, because the underscore and a Greek letter are both word
    characters. The ranking pushes identifier uses down; the tool does not
    pretend to exclude either class."""
    return re.search(rf"(?<!\w){re.escape(form)}(?!\w)", text) is not None


def sentences(line: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", line.strip()) if s.strip()]


def score(sentence: str, form: str, path: str, term: str) -> int:
    s = 0
    if any(re.search(p, sentence, re.I) for p in DEFINING):
        s += 3
    if re.match(rf"^\W*{re.escape(form)}\b", sentence, re.I):
        s += 2                                 # the sentence is about the term
    if path.endswith("README.md"):
        s += 1                                 # a package's own abstract
    # A sentence from the paper NAMED after the term beats one from a paper
    # that merely mentions it. Without this the RCMP definition lost a tie to
    # a sentence in the EBE paper, on alphabetical order (review finding).
    # Matched as a whole token against the path: splitting the term and
    # requiring every part longer than two characters gave `EFC` a +2 on any
    # path containing "efc" (4 of 25 terms) and gave L0/S0 nothing at all,
    # not even the paper literally named L0–L3-Regime-Architecture.
    # Case-insensitively: a path is not prose. Case-sensitive matching gave
    # the bonus to RCMP, L0, S0, Core Lock and EFC-R but not to `proxy` in
    # meta/Proxy, `regime` in EFC-Regime-Transition-Framework, `resonance` in
    # Resonance-Note or `constraint` in Structural-Constraints — and `regime`
    # then lost its definition to a rhetorical question (review finding).
    if any(whole_word(f.lower(), path.lower()) for f in forms(term)):
        s += 2
    if len(sentence.split()) < 8:
        s -= 2                                 # too short to define anything
    return s


def occurrences(root: Path, term: str):
    """(hits per form, files carrying the term, candidates, files skipped).

    The file set is collected from the WHOLE text, before the line filters
    that produce definition candidates. Feeding the candidate list to source
    attribution lost 82 sources across 25 terms, because a term that appears
    only in a heading or a table row is still carried by that paper (review
    finding)."""
    per_form: dict[str, int] = {f: 0 for f in forms(term)}
    carriers: set[str] = set()
    cands: list[tuple[str, int, str, int]] = []
    skipped = 0
    for rel in tracked_text_files(root):
        try:
            text = (root / rel).read_text(encoding="utf-8")
        except OSError:
            skipped += 1
            continue
        except UnicodeDecodeError:
            skipped += 1                        # counted, never silent
            continue
        hit_here = False
        for f in per_form:
            if whole_word(f, text):
                per_form[f] += 1
                hit_here = True
        if hit_here:
            carriers.add(rel)
        for n, line in enumerate(text.split("\n"), 1):
            if line.startswith(("|", "#", "    ", "```")):
                continue                        # tables, headings, code
            for f in per_form:
                if not whole_word(f, line):
                    continue
                for s in sentences(line):
                    if whole_word(f, s):
                        cands.append((rel, n, s, score(s, f, rel, term)))
    seen: set[str] = set()
    uniq = []
    for rel, n, s, sc in sorted(cands, key=lambda x: (-x[3], x[0], x[1])):
        if s in seen:
            continue
        seen.add(s)
        uniq.append((rel, n, s, sc))
    return per_form, carriers, uniq, skipped


def declared_terms(root: Path) -> set[str]:
    try:
        graph = json.loads((root / ONTOLOGY).read_text(encoding="utf-8")).get("@graph", [])
    except (OSError, ValueError):
        return set()
    return {n["@id"][4:] for n in graph if isinstance(n.get("@id"), str) and n["@id"].startswith("efc:")}


def registered(root: Path) -> set[str]:
    try:
        graph = json.loads((root / REGISTRY).read_text(encoding="utf-8")).get("@graph", [])
    except (OSError, ValueError):
        return set()
    return {n["@id"] for n in graph if "skos:Concept" in (n.get("@type") if isinstance(n.get("@type"), list) else [n.get("@type")])}


def published_dois(root: Path) -> dict[str, str]:
    """{paper directory: doi} for what the tree publishes."""
    out: dict[str, str] = {}
    try:
        for p in json.loads((root / "figshare/doi-map.json").read_text(encoding="utf-8")).get("papers", []):
            if p.get("doi") and p.get("repo_dir"):
                out[p["repo_dir"]] = p["doi"]
    except (OSError, ValueError):
        pass
    return out


def sources_for(carriers: set[str], dois: dict[str, str]) -> list[dict]:
    """DOIs of papers that NAME the term. Proximity is not a source: a paper
    counts only when one of its OWN files carries it (the efc:HME lesson,
    where three cluster papers were listed because they were about halos and
    none used the word).

    Each file is attributed to the LONGEST matching repo_dir. One paper
    directory is a strict prefix of four others in doi-map.json, and prefix
    matching gave the container credit for its children's terms — the same
    mistake in structural form (review finding)."""
    owned: dict[str, int] = {}
    dirs = sorted(dois, key=len, reverse=True)
    for rel in carriers:
        for repo_dir in dirs:
            if rel.startswith(repo_dir + "/"):
                owned[repo_dir] = owned.get(repo_dir, 0) + 1
                break
    return [{"doi": f"https://doi.org/{dois[d]}", "paper": d, "files": owned[d]} for d in sorted(owned)]


def draft(root: Path, term: str, limit: int = 5) -> dict:
    per_form, carriers, cands, skipped = occurrences(root, term)
    dois = published_dois(root)
    local = re.sub(r"[^A-Za-z0-9]", "", term)
    decl = declared_terms(root)
    sources = sources_for(carriers, dois)
    return {
        "term": term,
        "suggested_id_not_a_decision": f"efc:{local}",
        "already_declared_in_vocabulary": local in decl or term in decl,
        "already_registered": f"efc:{local}" in registered(root),
        "forms_searched": sorted(per_form),
        "forms_found": {f: n for f, n in sorted(per_form.items()) if n},
        "in_tree": any(per_form.values()),
        "files_carrying_the_term": len(carriers),
        "files_unreadable": skipped,
        "sources_naming_the_term": sources,
        "sources_total": len(sources),
        "definition_candidates_total": len(cands),
        "definition_candidates": [
            {"anchor": f"{GH}{rel}#L{n}", "score": sc, "sentence": s}
            for rel, n, s, sc in (cands if limit == 0 else cands[:limit])
        ],
        "open_decisions": [
            "skos:definition — pick one candidate anchor, or declare a gap in a scopeNote",
            "efc:entityType — anything finer than `concept` needs efc:attested",
            "efc:registryStatus — `candidate` is free; `canonical` needs efc:attested",
            "skos:broader — only if a source in the tree says so",
        ],
    }


def render(d: dict, limit: int = 5) -> str:
    lines = [f"── {d['term']}  →  {d['suggested_id_not_a_decision']} (a suggestion, not a decision)"]
    id_state = ("registered in C11" if d["already_registered"]
                else "declared in the vocabulary (C9), meaning not yet registered" if d["already_declared_in_vocabulary"]
                else "not a vocabulary term yet")
    lines.append(f"   identity     {id_state}")
    if not d["in_tree"]:
        lines.append(f"   NOT IN TREE  searched {len(d['forms_searched'])} forms: {', '.join(d['forms_searched'])}")
        lines.append("                registering it would be inventing EFC vocabulary — find a source first")
        return "\n".join(lines)
    lines.append("   forms        " + ", ".join(f"{f} ({n})" for f, n in d["forms_found"].items()))
    if d["sources_naming_the_term"]:
        vist = d["sources_naming_the_term"] if limit == 0 else d["sources_naming_the_term"][:limit]
        for s in vist:
            lines.append(f"   source       {s['doi']}  {s['paper'].split('/')[-1][:46]} ({s['files']} file(s))")
        if d["sources_total"] > len(vist):
            lines.append(f"                … {len(vist)} of {d['sources_total']} shown; --all for the rest")
    else:
        lines.append("   source       none — no published paper's own files carry the term")
    vist = d["definition_candidates"] if limit == 0 else d["definition_candidates"][:limit]
    for c in vist:
        lines.append(f"   candidate {c['score']:+d}  {c['anchor'][len(GH):]}")
        kutt = c["sentence"][:104]
        lines.append(f"                «{kutt}{'…' if len(c['sentence']) > 104 else ''}»")
    if d["definition_candidates_total"] > len(vist):
        lines.append(f"                … {len(vist)} of {d['definition_candidates_total']} shown; --all for the rest")
    if not d["definition_candidates"]:
        lines.append("   candidate    none — a declared gap is the honest entry")
    if d["files_unreadable"]:
        lines.append(f"   note         {d['files_unreadable']} file(s) were not readable as UTF-8 and were not searched")
    lines.append("   yours        " + "; ".join(x.split(" — ")[0] for x in d["open_decisions"]))
    return "\n".join(lines)


USAGE = """usage: efc_candidates.py [--json] [--all | --limit N] [TERM …]

Reads the tree for a concept term and reports what can be measured. Chooses
nothing: the four judgements are printed as open decisions. With no TERM the
list in TERMS is used.

  --json      machine-readable drafts
  --all       every candidate and source, not the first few
  --limit N   show N candidates and sources per term (default 5; 0 = all)
"""


def main(argv: list[str]) -> int:
    if "--help" in argv or "-h" in argv:
        print(USAGE)
        return 0
    limit = 0 if "--all" in argv else 5
    if "--limit" in argv:
        i = argv.index("--limit")
        try:
            limit = int(argv[i + 1])
        except (IndexError, ValueError):
            print("--limit needs a number", file=sys.stderr)
            return 2
        argv = argv[:i] + argv[i + 2:]
    ukjent = [a for a in argv if a.startswith("-") and a not in ("--json", "--all")]
    if ukjent:
        print(f"unknown option(s): {' '.join(ukjent)}\n\n{USAGE}", file=sys.stderr)
        return 2
    terms = [a for a in argv if not a.startswith("-")] or list(TERMS)
    try:
        drafts = [draft(ROOT, t, limit) for t in terms]
    except NotAGitTree as e:
        print(f"[efc-candidates] {e}", file=sys.stderr)
        return 2
    if "--json" in argv:
        print(json.dumps(drafts, indent=2, ensure_ascii=False))
        return 0
    for d in drafts:
        print(render(d, limit))
        print()
    n_gap = sum(1 for d in drafts if not d["definition_candidates"])
    n_out = sum(1 for d in drafts if not d["in_tree"])
    print(f"[efc-candidates] {len(drafts)} term(s): {n_out} not in the tree, {n_gap} with no definition candidate. "
          f"Nothing was written; the registry takes none of this without an efc:attested entry.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
