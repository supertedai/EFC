#!/usr/bin/env python3
"""
EFC AI Brain — Full Autonomous Paper Processing Pipeline
=========================================================

The single script that does EVERYTHING when a PDF is uploaded:

1. Reads PDF text (pdftotext)
2. Sends to GPT-5 for COMPLETE analysis:
   - 10/10 metadata (key_results, core_equations, sealed_predictions,
     kill_criteria, related_packages, parameters)
   - Classification (empirical test, sealed prediction, methodology, theory)
   - Public page updates (ALL 6 pages)
3. Writes enriched index.json + metadata.json + CITATION.cff + README.md + jsonld
4. Updates ALL public pages:
   - Validation Ledger (new row if empirical test)
   - Changelog (new entry always)
   - Stage-IV Roadmap (if pipeline/prediction)
   - White Paper Series (if sealed prediction)
   - Elevator Pitch (update stats)
   - Gap Analysis (if closes a gap)
5. Updates README.md stats

Requires: at least ONE of OPENAI_API_KEY or ANTHROPIC_API_KEY.
Requires: poppler-utils (pdftotext) for PDF extraction.

LLM providers (in priority order, picks whichever has a key):
  1. OpenAI GPT-5     (env: OPENAI_API_KEY, model: OPENAI_MODEL=gpt-5)
  2. Anthropic Claude (env: ANTHROPIC_API_KEY, model: ANTHROPIC_MODEL=claude-opus-4-6)
Set EFC_LLM_PROVIDER=openai|anthropic to force one if both keys are set.

Usage:
  python3 scripts/maintenance/efc_ai_brain.py
  python3 scripts/maintenance/efc_ai_brain.py --dry-run
  python3 scripts/maintenance/efc_ai_brain.py --max 5
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from efc_identity import served_id as _served_id  # noqa: E402


REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
PUBLIC = os.path.join(REPO, "docs", "public")

PUBLIC_PAGES = {
    "ledger": os.path.join(PUBLIC, "EFC_Validation_Ledger.html"),
    "changelog": os.path.join(PUBLIC, "EFC_Changelog.html"),
    "roadmap": os.path.join(PUBLIC, "EFC_Stage-IV_Data_Roadmap.html"),
    "whitepaper": os.path.join(PUBLIC, "EFC_White_Paper_Series.html"),
    "elevator": os.path.join(PUBLIC, "EFC_Elevator_Pitch.html"),
    "gap": os.path.join(PUBLIC, "EFC_Gap_Analysis.html"),
}

MODEL = os.environ.get("OPENAI_MODEL", "gpt-5")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-6")
LLM_PROVIDER_OVERRIDE = os.environ.get("EFC_LLM_PROVIDER", "").strip().lower()
MAX_PDF_CHARS = 8000
AUTHOR = "Morten Magnusson"
ORCID = "0009-0002-4860-5095"
AFFILIATION = "Symbiose Research, Sandnes, Norway"

SKIP_TOP = {
    "README.md", "cover_letter-2.pdf", "efc_graph_edges.json",
    "efc_graph_schema.json", "efc_index.json", "efc_index.jsonld",
    "ai_friendly_index.json",
}


# ═══════════════════════════════════════════════════════════
# PDF + repo scanning
# ═══════════════════════════════════════════════════════════

def _find_pdftotext():
    """Find pdftotext binary, checking common paths."""
    import shutil
    path = shutil.which("pdftotext")
    if path:
        return path
    # Fallback: common install locations
    for p in ["/usr/bin/pdftotext", "/usr/local/bin/pdftotext"]:
        if os.path.isfile(p):
            return p
    return None


def extract_pdf_text(paper_dir, max_chars=MAX_PDF_CHARS):
    pdfs = [f for f in os.listdir(paper_dir) if f.lower().endswith(".pdf")]
    if not pdfs:
        return ""
    pdftotext_bin = _find_pdftotext()
    if not pdftotext_bin:
        print("    [FAIL] pdftotext not found (poppler-utils)")
        return ""
    for f in pdfs:
        pdf_path = os.path.join(paper_dir, f)
        try:
            result = subprocess.run(
                [pdftotext_bin, pdf_path, "-"],
                capture_output=True, text=True, timeout=15)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout[:max_chars]
            if result.returncode != 0:
                print(f"    [WARN] pdftotext rc={result.returncode} for {f}: {result.stderr[:100]}")
        except subprocess.TimeoutExpired:
            print(f"    [WARN] pdftotext timeout for {f}")
        except Exception as e:
            print(f"    [WARN] pdftotext failed: {type(e).__name__}: {e}")
    return ""


# ── Holistic Impact Analysis (Step 1.5) ─────────────────────────────

SYMBIOSE_API = os.environ.get("SYMBIOSE_API_URL", "http://localhost:3001")
LEDGER_DATA = os.path.join(REPO, "docs", "validation-ledger", "data")


def _query_neo4j(cypher, params=None):
    """Query Neo4j via Symbiose API. Returns list of records or []."""
    import urllib.request
    import urllib.error
    url = f"{SYMBIOSE_API}/api/v1/neo4j"
    body = json.dumps({"cypher": cypher, "params": params or {}}).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("records", data.get("result", []))
    except Exception:
        return []


def _query_graph_context(idx):
    """Query Neo4j for 1-2 hop connections from this paper's concepts.

    Returns dict with related_papers, related_validations, concept_cluster,
    and bridge_potential. Gracefully returns empty dict if Neo4j unavailable.
    """
    doi = idx.get("doi", "")
    if not doi:
        return {}

    result = {
        "concepts": [],
        "related_papers": [],
        "related_validations": [],
        "bridge_potential": [],
    }

    # Filter out personal/generic concepts that pollute graph traversal
    NOISE_CONCEPTS = {
        "morten magnusson", "symbiose research", "sandnes", "norway",
        "cc-by-4.0", "figshare", "energy-flow cosmology", "efc",
        "morten", "author", "researcher",
    }

    # 1-hop: What concepts does this DOI document?
    # Graph uses DOCUMENTS (not MENTIONS) for DOI→Concept edges
    concepts = _query_neo4j(
        "MATCH (d)-[:DOCUMENTS|MENTIONS]->(c:Concept) "
        "WHERE d.doi CONTAINS $doi "
        "AND NOT c:User "
        "RETURN c.name AS name, c.domain AS domain, "
        "c.concept_type AS type LIMIT 30",
        {"doi": doi.split("/")[-1]},
    )
    result["concepts"] = [
        {"name": r.get("name", "?"), "domain": r.get("domain", ""),
         "type": r.get("type", "")}
        for r in concepts
        if r.get("name", "").lower().strip() not in NOISE_CONCEPTS
    ][:20]

    if not result["concepts"]:
        # Try keywords from index.json as fallback
        kw = idx.get("keywords", [])
        result["concepts"] = [{"name": k, "domain": "", "type": "keyword"}
                              for k in kw[:10]]

    # 2-hop: What other documents share these concepts?
    # Exclude personal/generic concepts to avoid "everything connects via author"
    related = _query_neo4j(
        "MATCH (d)-[:DOCUMENTS|MENTIONS]->(c:Concept)"
        "<-[:DOCUMENTS|MENTIONS]-(other) "
        "WHERE d.doi CONTAINS $doi AND other <> d "
        "AND NOT c:User "
        "AND toLower(c.name) NOT IN $noise "
        "RETURN DISTINCT other.name AS name, other.doi AS doi, "
        "c.name AS shared LIMIT 15",
        {"doi": doi.split("/")[-1],
         "noise": list(NOISE_CONCEPTS)},
    )
    result["related_papers"] = [
        {"name": r.get("name", "?"), "doi": r.get("doi", ""),
         "shared_concept": r.get("shared", "")}
        for r in related
    ]

    # KC/Validation connections (filtered for noise)
    validations = _query_neo4j(
        "MATCH (d)-[:DOCUMENTS|MENTIONS]->(c:Concept)"
        "<-[:TESTS|VALIDATES]-(v:EFCValidation) "
        "WHERE d.doi CONTAINS $doi "
        "AND NOT c:User "
        "AND toLower(c.name) NOT IN $noise "
        "RETURN v.test_id AS test_id, v.name AS name, "
        "c.name AS shared LIMIT 10",
        {"doi": doi.split("/")[-1],
         "noise": list(NOISE_CONCEPTS)},
    )
    result["related_validations"] = [
        {"test_id": r.get("test_id", ""), "name": r.get("name", ""),
         "shared": r.get("shared", "")}
        for r in validations
    ]

    return result


def _gather_efc_state():
    """Read current EFC state from public HTML pages and ledger.json.

    Uses data-*-id attributes for machine-readable extraction.
    """
    state = {
        "kc_statuses": {},
        "priority_actions": {},
        "test_counts": {},
        "open_gaps": [],
        "bottom_line": "",
    }

    # Test counts from ledger.json
    ledger_path = os.path.join(LEDGER_DATA, "ledger.json")
    if os.path.exists(ledger_path):
        with open(ledger_path, encoding="utf-8", errors="replace") as f:
            ld = json.load(f)
        s = ld.get("stats", {})
        total = s.get("total_public", 0)
        planned = s.get("planned_pipeline", 0)
        falsified = s.get("n_falsified", 0)
        state["test_counts"] = {
            "total": total, "active": total - planned,
            "survived": total - planned - falsified,
            "falsified": falsified, "pipeline": planned,
        }

    # KC statuses from Gap Analysis
    gap_path = PUBLIC_PAGES.get("gap", "")
    if os.path.exists(gap_path):
        with open(gap_path, encoding="utf-8", errors="replace") as f:
            gap_html = f.read()
        for m in re.finditer(
            r'data-kc-id="(KC\d)"[^>]*>.*?'
            r'(SEALED|DONE|PREDICTION READY|P3 PASS|PIPELINE NEEDED|'
            r'NOT STARTED|Monitoring|HIGH|ACTIVE)',
            gap_html, re.DOTALL | re.IGNORECASE,
        ):
            state["kc_statuses"][m.group(1)] = m.group(2)

        # Priority actions
        for m in re.finditer(
            r'data-action-id="(action-\d)"[^>]*>.*?'
            r'(DONE|ACTIVE|PLANNED|SEALED)',
            gap_html, re.DOTALL | re.IGNORECASE,
        ):
            state["priority_actions"][m.group(1)] = m.group(2)

        # Open theory gaps
        for m in re.finditer(
            r'data-gap-id="([^"]+)"[^>]*>(.*?)</tr>',
            gap_html, re.DOTALL,
        ):
            if "CLOSED" not in m.group(2) and "DONE" not in m.group(2):
                name_match = re.search(r'<td[^>]*>(.*?)</td>', m.group(2), re.DOTALL)
                if name_match:
                    name = re.sub(r'<[^>]+>', '', name_match.group(1)).strip()
                    state["open_gaps"].append({"id": m.group(1), "name": name})

        # Bottom line
        bl_match = re.search(
            r'data-section="bottom-line"[^>]*>.*?Biggest gap[^<]*</td>\s*<td>(.*?)</td>',
            gap_html, re.DOTALL | re.IGNORECASE,
        )
        if bl_match:
            state["bottom_line"] = re.sub(
                r'<[^>]+>', '', bl_match.group(1)).strip()[:300]

    return state


def analyze_holistic_impact(idx, pdf_text, graph_ctx, efc_state):
    """Single holistic LLM call that understands the full EFC picture.

    Combines paper content + graph intelligence + current EFC state
    to generate a complete ledger_impact with page_updates.
    """
    # Build context strings
    concepts_str = ", ".join(
        c["name"] for c in graph_ctx.get("concepts", [])[:10]
    ) or "(no graph data)"

    related_str = "\n".join(
        f"  - {r['name']} (DOI {r.get('doi', '?')}) via '{r.get('shared_concept', '?')}'"
        for r in graph_ctx.get("related_papers", [])[:8]
    ) or "  (none found)"

    validations_str = "\n".join(
        f"  - {r['test_id']}: {r.get('name', '?')} (shared: {r.get('shared', '?')})"
        for r in graph_ctx.get("related_validations", [])[:8]
    ) or "  (none found)"

    kc_str = "\n".join(
        f"  - {kc}: {status}"
        for kc, status in sorted(efc_state.get("kc_statuses", {}).items())
    ) or "  (not available)"

    actions_str = "\n".join(
        f"  - {aid}: {status}"
        for aid, status in sorted(efc_state.get("priority_actions", {}).items())
    ) or "  (not available)"

    tc = efc_state.get("test_counts", {})
    tests_str = (
        f"total={tc.get('total', '?')}, active={tc.get('active', '?')}, "
        f"survived={tc.get('survived', '?')}, falsified={tc.get('falsified', '?')}, "
        f"pipeline={tc.get('pipeline', '?')}"
    )

    gaps_str = "\n".join(
        f"  - {g['id']}: {g['name']}"
        for g in efc_state.get("open_gaps", [])[:10]
    ) or "  (all closed)"

    # Paper info
    kr = idx.get("key_results", {})
    sp_list = idx.get("sealed_predictions", [])
    sp_str = "\n".join(
        f"  - {sp.get('id', '?')}: {sp.get('statement', '')[:150]}"
        for sp in sp_list[:5]
    ) if sp_list else "  (none)"

    kc_paper = idx.get("kill_criteria", [])
    kc_paper_str = "\n".join(
        f"  - {kc}" for kc in kc_paper[:5]
    ) if kc_paper else "  (none)"

    prompt = f"""You are the EFC (Energy-Flow Cosmology) project lead — Morten Magnusson.
You know every paper, every kill criterion, every sealed prediction, every validation test.
A new paper has just been deposited. You also have graph intelligence from Neo4j
showing how this paper connects to the existing knowledge structure.

Think like Morten: Where does this belong? What does it cover? What does it point toward?
What does it prove? What is the goal? What is implicit?

## Graph Intelligence (from Neo4j knowledge graph)
Concepts this paper touches: {concepts_str}
Related papers (1-2 hops):
{related_str}
Validation tests sharing observables:
{validations_str}

## Current EFC State
Kill Criteria statuses:
{kc_str}
Priority Actions:
{actions_str}
Test counts: {tests_str}
Bottom line biggest gap: {efc_state.get('bottom_line', '?')[:200]}
Open theory gaps:
{gaps_str}

## New Paper
Title: {idx.get('title', '?')}
DOI: {idx.get('doi', '?')}
Type: {idx.get('paper_type', '?')}
Tier: {idx.get('tier', '?')}
Description: {idx.get('description', '')[:400]}
Key Result: {kr.get('main_finding', kr) if isinstance(kr, str) else kr.get('main_finding', '?') if isinstance(kr, dict) else '?'}
Kill Criteria declared:
{kc_paper_str}
Sealed Predictions:
{sp_str}

PDF excerpt (first 4000 chars):
{pdf_text[:4000]}

## Your Analysis — Think Holistically

### Forward coupling (paper → existing elements)
1. What does this paper ESTABLISH or PROVE for EFC?
2. Which Stage-IV KC (KC1-KC5) does it address? Does it CLOSE a KC gap?
3. Does it close any theory gap (data-gap-id)?
4. Does it complete any priority action (action-1 through action-7)?
5. Should the "biggest gap" in Bottom Line change?
6. What test-count changes does it imply (new tests added)?
7. What are the IMPLICIT consequences — things the paper doesn't say
   explicitly but that follow logically from the graph connections?
8. Which public pages (gap, roadmap, elevator, whitepaper) need updating?

### Backward coupling (paper → earlier results)
9. Does this paper CHANGE the interpretation of any EXISTING published
   DOI? (e.g., reattribution between channels, mechanism shift,
   robustness downgrade of a previous point prediction)
10. For each affected prior DOI, specify what was the OLD interpretation,
    what is the NEW interpretation, and why the shift follows from this
    paper's content.

### Language discipline
11. Inspect the paper's strong claims. For each, check:
    - Is it a PROOF or a numerical SCAN? → hedge "proves / cannot" to
      "strongly disfavored / strongly disfavored within class"
    - Is it a UNIVERSALITY claim or a WITHIN-CLASS claim? → hedge
      "no other model" to "distinctive within current class"
    - Is it a POINT prediction or a STRUCTURAL one? → if the point
      value is fragile under Monte Carlo (<50% robustness), demote
      it from central role
12. Return `language_hedges` array documenting each hedge applied.

### Hierarchy effects
13. Does the PREDICTION HIERARCHY change? Rank existing + new kill
    criteria by observational robustness (observables > structural
    signatures > fragile point predictions).
14. Does the "most distinctive observable" shift? If the earlier
    central prediction becomes fragile, what replaces it as the
    primary discriminator?

### Narrative framing
15. Is this result NEGATIVE, POSITIVE, CLARIFYING, or RESTRUCTURING
    for EFC? Choose one and justify in one sentence.
16. What ONE sentence captures the essence for the Bottom Line?

### Structural changes, not just updates
17. What NEW rows/items need ADDING to which tables? (distinct from
    UPDATING existing rows — use action="add_row")
18. What SECTIONS need restructuring (reordering lists, splitting
    sections, merging tables) rather than sentence-level edits?

Return ONLY a JSON object (no markdown, no explanation outside JSON):
{{
  "analysis": "2-3 sentence holistic summary of what this means for EFC",
  "narrative_frame": "clarifying|restructuring|positive|negative",
  "narrative_frame_reason": "one sentence justification",
  "bottom_line_sentence": "one sentence for the Bottom Line table",
  "kc_addressed": ["KC4"],
  "gaps_closed": ["theory-gap-id-here"],
  "priority_actions_completed": ["action-4"],
  "tests_added": [
    {{
      "test_id": "short_snake_case_id",
      "category": "physics_test|consistency_check|phenomenological|framework_constraint|planned_pipeline",
      "name": "Human-readable test name",
      "description": "What this test validates",
      "result": "PASS|MARGINAL|COLLAPSED|Planned",
      "status": "success|partial|failed|pending",
      "data_source": "Dataset used",
      "prediction": "What EFC predicts"
    }}
  ],
  "tests_updated": [],
  "reinterpreted_dois": [
    {{
      "doi": "10.6084/m9.figshare.XXXXXXXX",
      "old_interpretation": "what that paper was understood to show",
      "new_interpretation": "what it means in light of the new paper",
      "reason": "why this reattribution follows"
    }}
  ],
  "language_hedges": [
    {{
      "raw_claim": "verbatim quote or close paraphrase from paper",
      "hedged_version": "how it should be written in public pages",
      "reason": "proof vs scan / universal vs within-class / point vs structural"
    }}
  ],
  "new_hierarchy": [
    "1. Most robust observational criterion (DOI ref)",
    "2. Structural signature (DOI ref)",
    "3. ...",
    "N. Previously-central but now-fragile prediction (DOI ref)"
  ],
  "primary_discriminator_shift": {{
    "old": "what was the central distinctive prediction",
    "new": "what replaces it",
    "reason": "why"
  }},
  "page_updates": [
    {{
      "page": "gap|roadmap|elevator|whitepaper",
      "target": "data-kc-id=\\"KC4\\"",
      "action": "update_badge|mark_done|update_text|add_row|restructure_section",
      "new_badge": "SEALED",
      "new_text": "Description with DOI refs",
      "doi_refs": ["32023788"],
      "reasoning": "Why this update is correct",
      "hedges_applied": ["if any hedges from language_hedges apply here"]
    }}
  ],
  "new_rows": [
    {{
      "page": "roadmap",
      "table_id": "section-2-5-predictions",
      "content_html": "<tr>...full new row HTML...</tr>",
      "reason": "why a new row (not an update) is needed"
    }}
  ],
  "structural_edits": [
    {{
      "page": "elevator",
      "section": "kill-criteria-list",
      "change_type": "reorder|split|merge|demote_item",
      "description": "what changes structurally",
      "reason": "why"
    }}
  ],
  "implicit_consequences": ["consequence 1", "consequence 2"],
  "bottom_line_change": null,
  "graph_insights": ["insight from graph traversal"]
}}

Guardrails:
- If the paper does NOT affect any KC, gap, or action, return empty arrays.
- Be conservative about *claims*; be honest about *hedging*. Hedging
  REDUCES overclaiming and should not be omitted to avoid rejection.
- For `reinterpreted_dois`, require clear textual evidence from THIS
  paper that the reinterpretation follows. If the paper only *mentions*
  an earlier DOI without restructuring its meaning, do NOT list it.
- For `language_hedges`, quote or closely paraphrase the raw claim; the
  hedged version should preserve the scientific content but remove
  universal/proof language not supported by scan-based evidence.
- For `new_rows`, provide complete valid HTML matching the table's
  existing row structure.
- For `structural_edits`, the change_type must be one of the listed
  types; arbitrary restructuring is not supported.
- Do NOT invent test results or claim things the paper doesn't establish."""

    result_text = call_llm(prompt, max_tokens=4000)
    if not result_text:
        return None

    # Parse JSON from response
    try:
        # Strip markdown fences if present
        clean = re.sub(r'^```(?:json)?\s*', '', result_text.strip())
        clean = re.sub(r'\s*```$', '', clean)
        return json.loads(clean)
    except json.JSONDecodeError:
        # Try to find JSON object in response
        m = re.search(r'\{.*\}', result_text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
        print(f"    [WARN] Could not parse holistic impact JSON")
        return None


def _has_field(idx, *aliases):
    """Check if index.json has any of the given field names (schema compat)."""
    return any(bool(idx.get(a)) for a in aliases)


def _is_10_10(idx, dirpath):
    """Check if a package meets the full 10/10 standard.

    Accepts both schema variants:
      - Standard: key_results, kill_criteria, paper_type, tier
      - Legacy:   tests/falsification_criteria, type, status
    """
    has_key_results = _has_field(idx, "key_results", "tests", "numerical_table")
    has_kill_criteria = _has_field(idx, "kill_criteria", "falsification_criteria")
    has_paper_type = _has_field(idx, "paper_type", "type")
    has_tier = _has_field(idx, "tier", "status")
    has_src = os.path.isdir(os.path.join(dirpath, "src"))
    has_examples = os.path.isdir(os.path.join(dirpath, "examples"))
    has_data = os.path.isdir(os.path.join(dirpath, "data"))
    desc = idx.get("description", idx.get("abstract", ""))
    no_auto = "Auto-generated" not in desc
    return all([has_key_results, has_kill_criteria, has_paper_type,
                has_tier, has_src, has_examples, has_data, no_auto])


def find_papers_needing_enrichment():
    """Find papers not yet at 10/10 standard.

    10/10 requires ALL of:
      - key_results, kill_criteria, paper_type, tier in index.json
      - src/, examples/, data/ directories
      - No 'Auto-generated' placeholder description
    """
    needs_work = []
    for name in sorted(os.listdir(PAPERS)):
        if name in SKIP_TOP:
            continue
        d = os.path.join(PAPERS, name)
        if not os.path.isdir(d):
            continue
        idx_path = os.path.join(d, "index.json")
        if not os.path.exists(idx_path):
            continue
        try:
            with open(idx_path, encoding="utf-8", errors="replace") as f:
                idx = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"  [WARN] Skipping {name}: {e}")
            continue
        if not _is_10_10(idx, d):
            doi = idx.get("doi", "")
            missing = []
            if not _has_field(idx, "key_results", "tests", "numerical_table"):
                missing.append("key_results")
            if not _has_field(idx, "kill_criteria", "falsification_criteria"):
                missing.append("kill_criteria")
            if not _has_field(idx, "paper_type", "type"):
                missing.append("paper_type")
            if not _has_field(idx, "tier", "status"):
                missing.append("tier")
            if not os.path.isdir(os.path.join(d, "src")):
                missing.append("src/")
            if not os.path.isdir(os.path.join(d, "examples")):
                missing.append("examples/")
            if not os.path.isdir(os.path.join(d, "data")):
                missing.append("data/")
            needs_work.append({
                "directory": name,
                "path": d,
                "title": idx.get("title", name),
                "doi": doi,
                "has_pdf": any(f.endswith(".pdf") for f in os.listdir(d)),
                "missing": missing,
            })
    return needs_work


def load_unprocessed_for_pages():
    """Find papers with DOIs not in Ledger."""
    # Always run the detector fresh to get current state
    detector = os.path.join(os.path.dirname(__file__), "efc_unprocessed.py")
    subprocess.run([sys.executable, detector], capture_output=True)
    path = os.path.join(REPO, ".claude", "unprocessed_papers.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []


def read_page(key):
    path = PUBLIC_PAGES.get(key, "")
    if os.path.exists(path):
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    return ""


def write_page(key, text):
    path = PUBLIC_PAGES.get(key, "")
    if path:
        # Defensive: ensure nav block is canonical (short labels +
        # External Research link) on every HTML write. Idempotent.
        try:
            import sys as _sys
            import os as _os
            _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
            from _nav_helper import ensure_nav as _ensure_nav
            text = _ensure_nav(text)
        except Exception:
            pass  # never let nav sanitation block a real write
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)


# ═══════════════════════════════════════════════════════════
# GPT-5 API
# ═══════════════════════════════════════════════════════════

def _strip_fences(content):
    content = re.sub(r'^```(?:json)?\s*', '', content.strip())
    content = re.sub(r'\s*```$', '', content.strip())
    return content


def _call_openai(prompt, max_tokens, retries, api_key):
    """POST to OpenAI chat/completions. Returns text or None."""
    import urllib.request, urllib.error, ssl
    import time as _time
    ctx = ssl.create_default_context()
    for attempt in range(1, retries + 1):
        body = json.dumps({
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_completion_tokens": max_tokens,
        })
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=body.encode(),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=300) as resp:
                data = json.loads(resp.read())
                choice = data["choices"][0]
                content = choice.get("message", {}).get("content")
                finish = choice.get("finish_reason", "")
                if not content:
                    reason = f"finish_reason={finish}" if finish else "no content"
                    print(f"    [WARN] OpenAI empty ({reason}) attempt {attempt}/{retries}")
                    if attempt < retries:
                        _time.sleep(5 * (2 ** (attempt - 1)))
                        continue
                    return None
                return _strip_fences(content)
        except urllib.error.HTTPError as e:
            body_text = ""
            try:
                body_text = e.read().decode()[:300]
            except Exception:
                pass
            if e.code in (429, 500, 502, 503) and attempt < retries:
                wait = 5 * (2 ** (attempt - 1))
                print(f"    [RETRY] OpenAI HTTP {e.code} — waiting {wait}s ({attempt}/{retries})")
                _time.sleep(wait)
                continue
            print(f"    [FAIL] OpenAI HTTP {e.code}: {e.reason} -- {body_text}")
            return None
        except Exception as e:
            if attempt < retries:
                wait = 5 * (2 ** (attempt - 1))
                print(f"    [RETRY] OpenAI {type(e).__name__} — waiting {wait}s ({attempt}/{retries})")
                _time.sleep(wait)
                continue
            print(f"    [FAIL] OpenAI: {type(e).__name__}: {e}")
    return None


def _call_anthropic(prompt, max_tokens, retries, api_key):
    """POST to Anthropic messages API. Returns text or None."""
    import urllib.request, urllib.error, ssl
    import time as _time
    ctx = ssl.create_default_context()
    # Anthropic caps max_tokens per model; 8192 is safe across 4.x family.
    req_max = min(max_tokens, 8192)
    for attempt in range(1, retries + 1):
        body = json.dumps({
            "model": ANTHROPIC_MODEL,
            "max_tokens": req_max,
            "messages": [{"role": "user", "content": prompt}],
        })
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body.encode(),
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=300) as resp:
                data = json.loads(resp.read())
                # content is a list of blocks; collect text blocks
                blocks = data.get("content", [])
                text = "".join(
                    b.get("text", "") for b in blocks if b.get("type") == "text"
                )
                stop = data.get("stop_reason", "")
                if not text:
                    print(f"    [WARN] Claude empty (stop_reason={stop}) attempt {attempt}/{retries}")
                    if attempt < retries:
                        _time.sleep(5 * (2 ** (attempt - 1)))
                        continue
                    return None
                return _strip_fences(text)
        except urllib.error.HTTPError as e:
            body_text = ""
            try:
                body_text = e.read().decode()[:300]
            except Exception:
                pass
            if e.code in (429, 500, 502, 503, 529) and attempt < retries:
                wait = 5 * (2 ** (attempt - 1))
                print(f"    [RETRY] Claude HTTP {e.code} — waiting {wait}s ({attempt}/{retries})")
                _time.sleep(wait)
                continue
            print(f"    [FAIL] Claude HTTP {e.code}: {e.reason} -- {body_text}")
            return None
        except Exception as e:
            if attempt < retries:
                wait = 5 * (2 ** (attempt - 1))
                print(f"    [RETRY] Claude {type(e).__name__} — waiting {wait}s ({attempt}/{retries})")
                _time.sleep(wait)
                continue
            print(f"    [FAIL] Claude: {type(e).__name__}: {e}")
    return None


def _select_providers():
    """Return ordered list of (name, api_key) tuples to try.

    Priority: EFC_LLM_PROVIDER override > OpenAI > Anthropic.
    Providers without a key are skipped. If override points at a
    provider with no key, falls through to the other.
    """
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    providers = []
    if LLM_PROVIDER_OVERRIDE == "anthropic":
        if anthropic_key:
            providers.append(("anthropic", anthropic_key))
        if openai_key:
            providers.append(("openai", openai_key))
    else:
        if openai_key:
            providers.append(("openai", openai_key))
        if anthropic_key:
            providers.append(("anthropic", anthropic_key))
    return providers


def call_llm(prompt, max_tokens=8000, retries=4):
    """Call an LLM (OpenAI GPT-5 preferred, Anthropic Claude fallback).

    Returns text content, or None if all configured providers fail.
    Providers are selected based on which API keys are present; if
    the primary provider errors out, the next one is tried with the
    same prompt before giving up.
    """
    providers = _select_providers()
    if not providers:
        print("    [FAIL] No LLM key available (set OPENAI_API_KEY or ANTHROPIC_API_KEY)")
        return None

    for name, key in providers:
        if name == "openai":
            result = _call_openai(prompt, max_tokens, retries, key)
        else:
            result = _call_anthropic(prompt, max_tokens, retries, key)
        if result:
            return result
        if len(providers) > 1:
            print(f"    [INFO] {name} exhausted — trying fallback provider")
    return None


# Backward-compat alias so older imports still work.
call_gpt5 = call_llm


def _repair_json(text):
    """Try to fix truncated JSON from GPT-5 (missing closing braces)."""
    text = text.strip()
    # Count unmatched braces/brackets
    opens = text.count('{') + text.count('[')
    closes = text.count('}') + text.count(']')
    if opens > closes:
        # Try adding missing closers
        diff = opens - closes
        # Remove any trailing partial key/value
        last_comma = text.rfind(',')
        last_brace = max(text.rfind('}'), text.rfind(']'))
        if last_comma > last_brace:
            text = text[:last_comma]
        # Add closers in reverse order
        for ch in reversed(text):
            if diff <= 0:
                break
            if ch == '{':
                text += '}'
                diff -= 1
            elif ch == '[':
                text += ']'
                diff -= 1
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    return None


# ═══════════════════════════════════════════════════════════
# Step 1: Enrich metadata to 10/10
# ═══════════════════════════════════════════════════════════

def enrich_metadata(dirname, dirpath, title, doi, missing_fields=None):
    """Send PDF to GPT-5, get back 10/10 index.json content.

    Merges GPT-5 output with existing index.json — never overwrites
    fields that are already populated and valid.
    Falls back to title+existing metadata if PDF text extraction fails.
    """
    text = extract_pdf_text(dirpath)
    if not text:
        print(f"    [INFO] No PDF text extracted — using title + existing metadata")

    # Load existing index.json to preserve good data
    existing = {}
    idx_path = os.path.join(dirpath, "index.json")
    if os.path.exists(idx_path):
        try:
            with open(idx_path, encoding="utf-8", errors="replace") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    missing_str = ", ".join(missing_fields) if missing_fields else "all fields"

    # Build context from what we have
    source_text = text if text else ""
    existing_context = json.dumps(existing, indent=2)[:4000] if existing else "{}"

    prompt = f"""You are processing an EFC (Energy-Flow Cosmology) research paper for the AI-friendly archive.

PAPER TITLE: {title}
DOI: {doi}
DIRECTORY: {dirname}

FIELDS THAT NEED FILLING: {missing_str}

EXISTING index.json (preserve anything already good):
{existing_context}

{"PAPER TEXT (first " + str(MAX_PDF_CHARS) + " chars):" + chr(10) + source_text if source_text else "NOTE: No PDF text available. Generate metadata based on the title, directory name, and existing index.json above. For fields you cannot determine from the title alone, use reasonable defaults based on the EFC framework context."}

Generate a COMPLETE, RICH index.json for this paper. Respond with ONLY valid JSON:

{{
  "$schema": "./schema.json",
  "id": "{dirname.lower().replace('_', '-')}",
  "title": "exact title from paper",
  "description": "2-3 sentence description of what the paper does and its key contribution",
  "version": "version from paper or 1.0",
  "date": "YYYY-MM-DD from paper",
  "doi": "{doi}",
  "keywords": ["8-12 specific keywords"],
  "author": {{
    "name": "{AUTHOR}",
    "orcid": "{ORCID}",
    "affiliation": "{AFFILIATION}"
  }},
  "core_equations": {{
    "eq_name": {{
      "latex": "LaTeX equation",
      "description": "what it means"
    }}
  }},
  "key_results": {{
    "main_finding": "one sentence",
    "delta_chi2": null or number,
    "significance_sigma": null or number,
    "parameters_tested": ["list"],
    "datasets_used": ["list"],
    "verdict": "PASS | MARGINAL | FAIL | SEALED | PLANNED | N/A"
  }},
  "sealed_predictions": [
    {{"id": "P1", "statement": "prediction", "falsifiable_by": "what test"}}
  ],
  "kill_criteria": ["KC1: specific condition that would kill EFC", "KC2: another kill condition"],
  "tier": "T1 | T2 | T3 | N/A",
  "paper_type": "empirical_test | sealed_prediction | methodology | theory | infrastructure | observational_pipeline",
  "related_packages": [
    {{"id": "short-id", "doi": "10.6084/m9.figshare.NNNNNNN", "role": "description"}}
  ],
  "files": {{
    "pdf": "filename.pdf",
    "readme": "README.md"
  }},
  "figshare_url": "https://doi.org/{doi}"
}}

IMPORTANT:
- kill_criteria MUST be a non-empty list of specific falsification conditions
- paper_type MUST be one of: empirical_test, sealed_prediction, methodology, theory, infrastructure, observational_pipeline
- tier MUST be one of: T1, T2, T3, N/A
- Extract REAL equations, results, predictions from the paper text. Do not invent data.
- Preserve any existing good data from the EXISTING index.json above."""

    result = call_llm(prompt)
    if not result:
        print(f"    [FAIL] GPT-5 returned no response")
        return None
    try:
        enriched = json.loads(result)
    except json.JSONDecodeError:
        # Try to repair truncated JSON (GPT-5 sometimes cuts off)
        repaired = _repair_json(result)
        if repaired:
            enriched = repaired
        else:
            print(f"    [WARN] GPT-5 returned invalid JSON: {result[:200]}")
            return None

    # Merge: GPT-5 output fills gaps, existing data takes priority
    merged = dict(enriched)
    for key, val in existing.items():
        if key in ("$schema", "id", "doi", "author", "files", "figshare_url"):
            # Always keep existing for identity fields
            merged[key] = val
        elif val and key not in merged:
            merged[key] = val
        elif val and isinstance(val, (dict, list)) and val and not merged.get(key):
            merged[key] = val

    return merged


def write_enriched_package(dirpath, idx):
    """Write all package files from enriched index.json."""
    title = idx.get("title", "")
    doi = idx.get("doi", "")
    pub_date = idx.get("date", date.today().isoformat())
    short_id = idx.get("id", "")

    # index.json
    with open(os.path.join(dirpath, "index.json"), "w") as f:
        json.dump(idx, f, indent=2)

    # metadata.json
    meta = {
        "title": title, "short_id": short_id, "version": idx.get("version", "1.0"),
        "date": pub_date,
        "author": {"name": AUTHOR, "orcid": ORCID, "affiliation": AFFILIATION},
        "license": "CC-BY-4.0", "doi": doi,
        "abstract": idx.get("description", ""),
        "keywords": idx.get("keywords", []),
        "files": idx.get("files", {}),
        "paper": {"doi": doi, "figshare_url": f"https://doi.org/{doi}"} if doi else {},
    }
    with open(os.path.join(dirpath, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    # CITATION.cff
    cff = f"""cff-version: 1.2.0
title: "{title}"
message: "If you use this work, please cite it as below."
authors:
  - family-names: "Magnusson"
    given-names: "Morten"
    orcid: "https://orcid.org/{ORCID}"
    affiliation: "{AFFILIATION}"
date-released: "{pub_date}"
version: "{idx.get('version', '1.0')}"
{f'doi: "{doi}"' if doi else '# doi: pending'}
license: "CC-BY-4.0"
repository-code: "https://github.com/supertedai/EFC"
"""
    with open(os.path.join(dirpath, "CITATION.cff"), "w") as f:
        f.write(cff)

    # jsonld
    jsonld = {
        "@context": {"@vocab": "https://schema.org/"},
        "@type": "ScholarlyArticle",
        "name": title,
        "author": {"@type": "Person", "name": AUTHOR,
                   "identifier": f"https://orcid.org/{ORCID}"},
        "datePublished": pub_date,
        "license": "https://creativecommons.org/licenses/by/4.0/",
    }
    # @id on every document (C12): the DOI URL when the paper has one, else
    # the served identifier of this file (`doi:` CURIEs were not resolvable).
    if doi:
        jsonld["@id"] = f"https://doi.org/{doi}"
        jsonld["identifier"] = f"https://doi.org/{doi}"
        jsonld["doi"] = doi
    else:
        jsonld["@id"] = _served_id(os.path.relpath(os.path.join(dirpath, f"{short_id}.jsonld"), _REPO_ROOT).replace(os.sep, "/"))

    with open(os.path.join(dirpath, f"{short_id}.jsonld"), "w") as f:
        json.dump(jsonld, f, indent=2)

    # README.md
    kr = idx.get("key_results", {})
    preds = idx.get("sealed_predictions", [])
    readme = f"# {title}\n\n## AI-Friendly Package\n\n"
    readme += f"- **DOI:** [{doi}](https://doi.org/{doi})\n" if doi else ""
    readme += f"- **Version:** {idx.get('version', '1.0')}\n"
    readme += f"- **Author:** {AUTHOR} (ORCID: [{ORCID}](https://orcid.org/{ORCID}))\n"
    readme += f"- **Date:** {pub_date}\n- **License:** CC-BY-4.0\n\n---\n\n"
    readme += f"## Overview\n\n{idx.get('description', '')}\n"
    if kr.get("main_finding"):
        readme += f"\n## Key Result\n\n{kr['main_finding']}\n"
    if preds:
        readme += "\n## Sealed Predictions\n\n| ID | Prediction | Falsifiable by |\n|---|---|---|\n"
        for p in preds:
            readme += f"| {p.get('id','')} | {p.get('statement','')} | {p.get('falsifiable_by','')} |\n"

    with open(os.path.join(dirpath, "README.md"), "w") as f:
        f.write(readme)


def generate_code_package(dirpath, title, doi, pdf_text):
    """Use GPT-5 to generate src/, examples/, data/ for 10/10 standard."""
    # Skip if already has src/
    if os.path.isdir(os.path.join(dirpath, "src")):
        return

    short_id = os.path.basename(dirpath).lower().replace("_", "-").replace(" ", "-")
    module_name = re.sub(r'[^a-z0-9_]', '_', short_id.replace('-', '_'))[:40]

    prompt = f"""You are generating a complete Python reference implementation for an EFC research paper.

PAPER TITLE: {title}
DOI: {doi}

PAPER TEXT (excerpt):
{pdf_text[:6000]}

Generate THREE files. Respond with ONLY valid JSON:

{{
  "src_code": "Complete Python module with the paper's key equations implemented as functions. Include docstrings, type hints, constants from the paper, and a self-test at the bottom (if __name__ == '__main__'). Use numpy. Name the module {module_name}.py",
  "example_code": "A demo script (demo_{module_name}.py) that imports from src, runs the key calculation, prints results, and optionally generates a plot. Should be runnable standalone.",
  "data_json": "A JSON object containing the paper's key numerical values: parameters, best-fit values, predictions, thresholds, calibration constants. Structure it clearly with descriptions."
}}

Rules:
- src_code must implement the ACTUAL equations from the paper, not placeholders
- Extract real constants and parameter values from the text
- example_code should demonstrate the main result
- data_json should contain every numerical value mentioned in the paper
- Keep each file under 200 lines"""

    result = call_llm(prompt, max_tokens=8000)
    if not result:
        return

    files = None
    candidate = _strip_fences(result)
    try:
        files = json.loads(candidate)
    except json.JSONDecodeError as e:
        repaired = _repair_json(candidate)
        if repaired:
            files = repaired
        else:
            m = re.search(r'\{.*\}', candidate, re.DOTALL)
            if m:
                try:
                    files = json.loads(m.group(0))
                except json.JSONDecodeError:
                    files = None
        if not files:
            print(f"    [WARN] Could not parse code generation response ({e})")
            print(f"           First 200 chars: {candidate[:200]!r}")

    if not files:
        # One retry with a stricter prompt before giving up.
        strict = prompt + "\n\nIMPORTANT: Respond with ONLY the JSON object. No markdown fences. No prose."
        result = call_llm(strict, max_tokens=8000)
        if not result:
            return
        candidate = _strip_fences(result)
        try:
            files = json.loads(candidate)
        except json.JSONDecodeError:
            files = _repair_json(candidate)
        if not files:
            m = re.search(r'\{.*\}', candidate, re.DOTALL)
            if m:
                try:
                    files = json.loads(m.group(0))
                except json.JSONDecodeError:
                    pass
        if not files:
            print(f"    [WARN] Code generation failed after retry for {os.path.basename(dirpath)}")
            return

    # Write src/
    src_dir = os.path.join(dirpath, "src")
    os.makedirs(src_dir, exist_ok=True)
    init_path = os.path.join(src_dir, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w") as f:
            f.write(f'"""{title} — reference implementation."""\n')
    if files.get("src_code"):
        with open(os.path.join(src_dir, f"{module_name}.py"), "w") as f:
            f.write(files["src_code"])
        print(f"    Created src/{module_name}.py")

    # Write examples/
    ex_dir = os.path.join(dirpath, "examples")
    os.makedirs(ex_dir, exist_ok=True)
    if files.get("example_code"):
        with open(os.path.join(ex_dir, f"demo_{module_name}.py"), "w") as f:
            f.write(files["example_code"])
        print(f"    Created examples/demo_{module_name}.py")

    # Write data/
    data_dir = os.path.join(dirpath, "data")
    os.makedirs(data_dir, exist_ok=True)
    if files.get("data_json"):
        data = files["data_json"]
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                data = {"raw": data}
        with open(os.path.join(data_dir, "parameters.json"), "w") as f:
            json.dump(data, f, indent=2)
        print(f"    Created data/parameters.json")


# ═══════════════════════════════════════════════════════════
# Step 2: Update ALL public pages
# ═══════════════════════════════════════════════════════════

def update_all_pages(paper_list):
    """Update each public page separately with targeted GPT-5 calls.

    Instead of one massive prompt for all 6 pages, makes separate focused
    calls: Changelog, Ledger, Elevator, Roadmap, Whitepaper, Gap.
    """
    if not paper_list:
        return

    import time as _time

    # Build paper descriptions (shared context)
    paper_descs = []
    for p in paper_list[:20]:
        dirpath = os.path.join(PAPERS, p["directory"])
        idx_path = os.path.join(dirpath, "index.json")
        if os.path.exists(idx_path):
            with open(idx_path, encoding="utf-8", errors="replace") as f:
                idx = json.load(f)
            paper_descs.append({
                "directory": p["directory"],
                "title": idx.get("title", ""),
                "doi": idx.get("doi", ""),
                "description": idx.get("description", "")[:200],
                "paper_type": idx.get("paper_type", idx.get("type", "unknown")),
                "tier": idx.get("tier", idx.get("status", "N/A")),
            })

    papers_json = json.dumps(paper_descs, indent=2)[:6000]
    today = date.today().isoformat()

    # --- 1. CHANGELOG ---
    changelog_text = read_page("changelog")
    if changelog_text:
        prompt = f"""Add a changelog entry for {len(paper_descs)} new EFC papers registered on {today}.

PAPERS:
{papers_json}

Respond with ONLY the HTML <li> element to insert. Example format:
<li><strong>{today}</strong> &mdash; Registered {len(paper_descs)} papers: [list titles with DOI links].</li>

Use &mdash; not —. DOI links: <a href="https://doi.org/DOI">short-id</a>"""

        result = call_llm(prompt, max_tokens=2000)
        if result:
            result = result.strip()
            if result.startswith("<li"):
                if "<ol reversed>" in changelog_text:
                    changelog_text = changelog_text.replace(
                        "<ol reversed>", "<ol reversed>\n  " + result)
                    write_page("changelog", changelog_text)
                    print("    Updated Changelog")

    _time.sleep(3)

    # --- 2. LEDGER (only empirical tests) ---
    empirical = [p for p in paper_descs if p.get("paper_type") in
                 ("empirical_test", "sealed_prediction")]
    if empirical:
        ledger_text = read_page("ledger")
        if ledger_text:
            # Find existing table format
            last_tr = ledger_text.rfind("<tr>")
            sample_row = ledger_text[last_tr:last_tr + 500] if last_tr > 0 else ""

            prompt = f"""Add rows to the EFC Validation Ledger HTML table for these empirical test papers.

PAPERS TO ADD:
{json.dumps(empirical, indent=2)}

EXISTING TABLE ROW FORMAT (match this exactly):
{sample_row[:300]}

Respond with ONLY the <tr>...</tr> elements, one per paper. Use &Delta; not Δ, &mdash; not —."""

            result = call_llm(prompt, max_tokens=3000)
            if result and "<tr>" in result:
                idx_pos = ledger_text.rfind("</tbody>")
                if idx_pos >= 0:
                    ledger_text = ledger_text[:idx_pos] + result + "\n" + ledger_text[idx_pos:]
                    write_page("ledger", ledger_text)
                    print(f"    Updated Ledger ({len(empirical)} papers)")

    _time.sleep(3)

    # --- 3. ELEVATOR PITCH (update stats) ---
    elevator_text = read_page("elevator")
    if elevator_text:
        # Count current papers and tests
        import re as _re
        paper_count = len([d for d in os.listdir(PAPERS)
                          if os.path.isdir(os.path.join(PAPERS, d))
                          and d not in SKIP_TOP])

        prompt = f"""Update the paper count and test count in this EFC Elevator Pitch HTML.

Current paper count in archive: {paper_count}
New papers just registered: {len(paper_descs)}

Current Elevator Pitch HTML (first 3000 chars):
{elevator_text[:3000]}

Find any number that represents the paper count or test count and update it.
Respond with JSON: {{"old_text": "text to find", "new_text": "replacement text"}}
If no update needed, respond with {{"old_text": null, "new_text": null}}"""

        result = call_llm(prompt, max_tokens=500)
        if result:
            try:
                upd = json.loads(result)
                if upd.get("old_text") and upd["old_text"] in elevator_text:
                    elevator_text = elevator_text.replace(upd["old_text"], upd["new_text"])
                    write_page("elevator", elevator_text)
                    print("    Updated Elevator Pitch")
            except (json.JSONDecodeError, KeyError):
                pass

    _time.sleep(3)

    # --- 4. ROADMAP (if pipeline/prediction papers) ---
    pipeline_papers = [p for p in paper_descs if p.get("paper_type") in
                       ("observational_pipeline", "sealed_prediction")]
    if pipeline_papers:
        roadmap_text = read_page("roadmap")
        if roadmap_text:
            prompt = f"""These new EFC papers may need Roadmap updates:
{json.dumps(pipeline_papers, indent=2)}

Current Roadmap HTML (first 3000 chars):
{roadmap_text[:3000]}

If any paper adds a new dataset, pipeline, or prediction to track, respond with:
{{"html": "<tr>new row HTML</tr>", "insert_before": "exact text to find in page"}}

If no update needed: {{"html": null}}"""

            result = call_llm(prompt, max_tokens=1000)
            if result:
                try:
                    r = json.loads(result)
                    if r.get("html") and r.get("insert_before"):
                        if r["insert_before"] in roadmap_text:
                            roadmap_text = roadmap_text.replace(
                                r["insert_before"], r["html"] + "\n" + r["insert_before"])
                            write_page("roadmap", roadmap_text)
                            print("    Updated Roadmap")
                except (json.JSONDecodeError, KeyError):
                    pass

    _time.sleep(3)

    # --- 5. WHITE PAPER SERIES (sealed predictions) ---
    sealed_papers = [p for p in paper_descs if p.get("paper_type") == "sealed_prediction"]
    if sealed_papers:
        wp_text = read_page("whitepaper")
        if wp_text:
            prompt = f"""These EFC papers contain sealed predictions for the White Paper Series:
{json.dumps(sealed_papers, indent=2)}

Current White Paper Series HTML (first 3000 chars):
{wp_text[:3000]}

If any paper should be added, respond with:
{{"html": "<li>new entry HTML</li>", "insert_before": "exact text to find"}}

If no update: {{"html": null}}"""

            result = call_llm(prompt, max_tokens=1000)
            if result:
                try:
                    r = json.loads(result)
                    if r.get("html") and r.get("insert_before"):
                        if r["insert_before"] in wp_text:
                            wp_text = wp_text.replace(
                                r["insert_before"], r["html"] + "\n" + r["insert_before"])
                            write_page("whitepaper", wp_text)
                            print("    Updated White Paper Series")
                except (json.JSONDecodeError, KeyError):
                    pass

    _time.sleep(3)

    # --- 6. GAP ANALYSIS + ROADMAP GAP CLOSURE ---
    # This is the CONTEXTUAL step — checks if any new paper closes a known gap.
    # Needs full description (not truncated) and the actual gap table.
    gap_text = read_page("gap")
    roadmap_text = read_page("roadmap")

    if gap_text and paper_descs:
        # Build richer paper context for gap matching
        rich_descs = []
        for p in paper_list[:20]:
            dirpath = os.path.join(PAPERS, p["directory"])
            idx_path = os.path.join(dirpath, "index.json")
            if os.path.exists(idx_path):
                with open(idx_path, encoding="utf-8", errors="replace") as f:
                    idx = json.load(f)
                rich_descs.append({
                    "directory": p["directory"],
                    "title": idx.get("title", ""),
                    "doi": idx.get("doi", ""),
                    "description": idx.get("description", "")[:500],
                    "paper_type": idx.get("paper_type", idx.get("type", "")),
                    "key_results": {
                        "main_finding": idx.get("key_results", {}).get("main_finding", "") if isinstance(idx.get("key_results"), dict) else "",
                    },
                    "kill_criteria": idx.get("kill_criteria", [])[:3],
                    "keywords": idx.get("keywords", [])[:8],
                })

        # Extract gap table section specifically
        gap_table = ""
        for marker in ["<thead><tr><th>Gap</th>", "Theory Gaps", "Gap Analysis"]:
            pos = gap_text.find(marker)
            if pos > 0:
                gap_table = gap_text[pos:pos + 3000]
                break
        if not gap_table:
            gap_table = gap_text[3000:6000]  # fallback to middle section

        # Also extract roadmap gap table
        roadmap_gaps = ""
        if roadmap_text:
            for marker in ["<thead><tr><th>Gap</th>", "Theory Gaps"]:
                pos = roadmap_text.find(marker)
                if pos > 0:
                    roadmap_gaps = roadmap_text[pos:pos + 2000]
                    break

        prompt = f"""You are checking if any new EFC paper CLOSES a known gap in the Gap Analysis or Roadmap.

NEW PAPERS (with full descriptions and keywords):
{json.dumps(rich_descs, indent=2)[:6000]}

CURRENT GAP TABLE (from Gap Analysis):
{gap_table[:3000]}

CURRENT ROADMAP GAPS:
{roadmap_gaps[:2000]}

IMPORTANT: A paper closes a gap if its description, keywords, or key_results directly address the gap's topic.
For example: a paper about "Bellini-Sawicki alpha functions" closes the gap "Bellini-Sawicki α-function mapping: Not started".

For EACH gap that is closed by a new paper, respond with a JSON array of updates:
[
  {{
    "page": "gap" or "roadmap",
    "old_text": "exact text to find in the HTML (the gap row or cell text)",
    "new_text": "replacement with CLOSED status and DOI link",
    "reason": "why this paper closes this gap"
  }}
]

If no gaps are closed: respond with []
Be precise with old_text — it must match exactly."""

        result = call_llm(prompt, max_tokens=2000)
        if result:
            try:
                updates = json.loads(result)
                if isinstance(updates, list):
                    for upd in updates:
                        page = upd.get("page", "gap")
                        old = upd.get("old_text", "")
                        new = upd.get("new_text", "")
                        reason = upd.get("reason", "")
                        if old and new:
                            text = gap_text if page == "gap" else (roadmap_text or "")
                            if old in text:
                                text = text.replace(old, new)
                                if page == "gap":
                                    gap_text = text
                                    write_page("gap", gap_text)
                                else:
                                    roadmap_text = text
                                    write_page("roadmap", roadmap_text)
                                print(f"    Closed gap ({page}): {reason[:60]}")
            except (json.JSONDecodeError, KeyError):
                pass


# ═══════════════════════════════════════════════════════════
# Auto-register DOIs in evidence register
# ═══════════════════════════════════════════════════════════

def update_evidence_register(paper_list):
    """Add new DOIs to the evidence register if not already present."""
    er_path = os.path.join(REPO, "docs", "validation-ledger", "data", "evidence-register.json")
    if not os.path.exists(er_path):
        return

    with open(er_path) as f:
        er = json.load(f)

    empirical = er.get("categories", {}).get("empirical", [])
    existing_dois = {e.get("doi") for e in empirical}

    added = 0
    for p in paper_list:
        dirpath = os.path.join(PAPERS, p["directory"])
        idx_path = os.path.join(dirpath, "index.json")
        if not os.path.exists(idx_path):
            continue
        with open(idx_path, encoding="utf-8", errors="replace") as f:
            idx = json.load(f)
        doi = idx.get("doi", "")
        if not doi:
            continue
        # Extract the bare numeric Figshare article ID.  The evidence
        # register and efc_verify.py (C2) require 7–9 digits only — any
        # prefix like "10.6084/m9.figshare." must be stripped.  Using
        # split("/")[-1] here silently leaked "m9.figshare.XXX" strings
        # whenever the input was the canonical DOI form, so match the
        # numeric tail explicitly.
        m = re.search(r"(\d{7,9})", doi)
        doi_id = m.group(1) if m else ""
        if not doi_id:
            continue
        if doi_id not in existing_dois:
            paper_type = idx.get("paper_type", idx.get("type", "unknown"))
            cat = "empirical" if paper_type in ("empirical_test", "sealed_prediction") else "structural"
            empirical.append({
                "doi": doi_id,
                "name": idx.get("title", p["directory"])[:80],
                "category": cat,
            })
            existing_dois.add(doi_id)
            added += 1

    if added > 0:
        er["categories"]["empirical"] = empirical
        with open(er_path, "w") as f:
            json.dump(er, f, indent=2)
        print(f"    Added {added} DOI(s) to evidence register")


# ═══════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════

def main():
    dry_run = "--dry-run" in sys.argv
    max_papers = 200
    for i, arg in enumerate(sys.argv):
        if arg == "--max" and i + 1 < len(sys.argv):
            try:
                max_papers = int(sys.argv[i + 1])
            except ValueError:
                pass

    providers = _select_providers()
    has_any_key = bool(providers)
    provider_labels = {"openai": f"OpenAI/{MODEL}", "anthropic": f"Anthropic/{ANTHROPIC_MODEL}"}
    provider_summary = (
        " → ".join(provider_labels[p] for p, _ in providers) if providers else "NONE"
    )

    pdftotext_bin = _find_pdftotext()

    print("=" * 60)
    print("EFC AI BRAIN — Full Autonomous Processing")
    print(f"LLM providers: {provider_summary}")
    print(f"Mode: {'DRY-RUN' if dry_run else 'LIVE'}")
    print(f"pdftotext: {pdftotext_bin or 'NOT FOUND'}")
    print("=" * 60)

    if not has_any_key and not dry_run:
        print("[SKIP] No LLM key set (need OPENAI_API_KEY or ANTHROPIC_API_KEY).")
        return 0

    if not has_any_key and dry_run:
        print("[DRY-RUN] No LLM key set — showing what would be processed.\n")

    # Step 1: Find papers needing 10/10 enrichment
    needs_enrichment = find_papers_needing_enrichment()
    needs_enrichment = [p for p in needs_enrichment if p["has_pdf"]][:max_papers]

    if needs_enrichment:
        import time as _time
        print(f"\n>>> Step 1: Enriching {len(needs_enrichment)} paper(s) to 10/10 <<<\n")
        enriched_count = 0
        for idx_num, p in enumerate(needs_enrichment):
            # Rate limit: 3s pause between API calls to avoid empty responses
            if idx_num > 0 and not dry_run:
                _time.sleep(3)
            missing = p.get("missing", [])
            print(f"  {p['directory']}  (missing: {', '.join(missing)})")
            if dry_run:
                print(f"    [DRY-RUN] Would enrich via {provider_summary}")
                continue
            # Only call GPT-5 for metadata if index.json fields are missing
            meta_missing = [m for m in missing if m not in ("src/", "examples/", "data/")]
            if meta_missing:
                enriched = enrich_metadata(
                    p["directory"], p["path"], p["title"], p["doi"],
                    missing_fields=meta_missing)
                if enriched:
                    write_enriched_package(p["path"], enriched)
                    print(f"    Enriched metadata ({', '.join(meta_missing)})")
                    enriched_count += 1
                else:
                    print(f"    [SKIP] Could not enrich metadata")
            # Generate src/, examples/, data/ if missing
            dir_missing = [m for m in missing if m in ("src/", "examples/", "data/")]
            if dir_missing:
                pdf_text = extract_pdf_text(p["path"])
                if pdf_text:
                    generate_code_package(p["path"], p["title"], p["doi"], pdf_text)
                    print(f"    Generated {', '.join(dir_missing)}")
                    enriched_count += 1
                else:
                    print(f"    [SKIP] No PDF text for code generation")
        print(f"\n  Enriched: {enriched_count}/{len(needs_enrichment)}")
    else:
        print("\n>>> Step 1: All papers at 10/10 <<<")

    # Step 1.5: Holistic Impact Analysis with Graph Intelligence
    # Run on enriched papers that have DOIs but no ledger_impact yet
    impact_candidates = []
    for name in os.listdir(PAPERS):
        if name in SKIP_TOP:
            continue
        d = os.path.join(PAPERS, name)
        if not os.path.isdir(d):
            continue
        idx_path = os.path.join(d, "index.json")
        if not os.path.exists(idx_path):
            continue
        try:
            with open(idx_path, encoding="utf-8", errors="replace") as f:
                idx_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        # Only process papers with DOI, no existing ledger_impact,
        # and paper_type that warrants impact analysis
        if (idx_data.get("doi")
                and not idx_data.get("ledger_impact")
                and idx_data.get("paper_type") in (
                    "sealed_prediction", "empirical_test",
                    "empirical_analysis", "observational_pipeline",
                    "empirical_validation")):
            impact_candidates.append({
                "directory": name, "path": d,
                "idx_path": idx_path, "idx": idx_data,
            })

    impact_candidates = impact_candidates[:max_papers]

    if impact_candidates and has_any_key and not dry_run:
        import time as _time2
        print(f"\n>>> Step 1.5: Holistic Impact Analysis for "
              f"{len(impact_candidates)} paper(s) <<<\n")
        efc_state = _gather_efc_state()
        for ic in impact_candidates:
            _time2.sleep(3)  # Rate limit
            print(f"  {ic['directory']}:")
            graph_ctx = _query_graph_context(ic["idx"])
            n_concepts = len(graph_ctx.get("concepts", []))
            n_related = len(graph_ctx.get("related_papers", []))
            print(f"    Graph: {n_concepts} concepts, {n_related} related papers")

            pdf_text = extract_pdf_text(ic["path"])
            impact = analyze_holistic_impact(
                ic["idx"], pdf_text, graph_ctx, efc_state)

            if impact:
                ic["idx"]["ledger_impact"] = {
                    "status": "ready",
                    "holistic_analysis": impact.get("analysis", ""),
                    "graph_insights": impact.get("graph_insights", []),
                    "kc_addressed": impact.get("kc_addressed", []),
                    "gaps_closed": impact.get("gaps_closed", []),
                    "priority_actions_completed": impact.get(
                        "priority_actions_completed", []),
                    "tests_added": impact.get("tests_added", []),
                    "tests_updated": impact.get("tests_updated", []),
                    "page_updates": impact.get("page_updates", []),
                    "new_rows": impact.get("new_rows", []),
                    "structural_edits": impact.get("structural_edits", []),
                    "reinterpreted_dois": impact.get("reinterpreted_dois", []),
                    "language_hedges": impact.get("language_hedges", []),
                    "new_hierarchy": impact.get("new_hierarchy", []),
                    "primary_discriminator_shift": impact.get(
                        "primary_discriminator_shift"),
                    "narrative_frame": impact.get("narrative_frame"),
                    "narrative_frame_reason": impact.get(
                        "narrative_frame_reason", ""),
                    "bottom_line_sentence": impact.get(
                        "bottom_line_sentence", ""),
                    "implicit_consequences": impact.get(
                        "implicit_consequences", []),
                    "bottom_line_change": impact.get("bottom_line_change"),
                    "kill_criteria_addressed": impact.get("kc_addressed", []),
                }
                with open(ic["idx_path"], "w", encoding="utf-8") as f:
                    json.dump(ic["idx"], f, indent=2, ensure_ascii=False)
                n_updates = len(impact.get("page_updates", []))
                n_tests = len(impact.get("tests_added", []))
                print(f"    Impact: {impact.get('analysis', '?')[:100]}")
                print(f"    KCs: {impact.get('kc_addressed', [])}, "
                      f"page_updates: {n_updates}, tests: {n_tests}")
            else:
                print(f"    [SKIP] No impact generated")
    elif impact_candidates and dry_run:
        print(f"\n>>> Step 1.5: [DRY-RUN] Would analyze {len(impact_candidates)} "
              f"paper(s) for holistic impact <<<")
        for ic in impact_candidates:
            print(f"  {ic['directory']} ({ic['idx'].get('paper_type', '?')})")
    else:
        print("\n>>> Step 1.5: No papers needing holistic impact analysis <<<")

    # Step 2: Find papers not in public pages
    unprocessed = load_unprocessed_for_pages()
    page_papers = [p for p in unprocessed if "Ledger" in p.get("missing_from", [])][:max_papers]

    if page_papers:
        print(f"\n>>> Step 2: Registering {len(page_papers)} paper(s) in public pages <<<\n")
        if not dry_run:
            update_all_pages(page_papers)
            update_evidence_register(page_papers)
        else:
            for p in page_papers:
                print(f"  [DRY-RUN] Would register: {p['directory']}")
    else:
        print("\n>>> Step 2: All papers registered in public pages <<<")

    # Step 3: Register DOIs from enriched papers (even if already in public pages)
    all_papers = load_unprocessed_for_pages() or []
    if not dry_run and needs_enrichment:
        update_evidence_register(needs_enrichment)

    print(f"\n{'=' * 60}")
    print("EFC AI BRAIN — done")
    print(f"{'=' * 60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
