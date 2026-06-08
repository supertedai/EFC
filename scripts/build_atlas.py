#!/usr/bin/env python3
"""
build_atlas.py
==============

Build the EFC Atlas view (docs/public/EFC_Atlas.html) from two deterministic
sources:

    docs/validation-ledger/data/atlas.json   -- cross-framework atlas
                                               (42 frameworks, phenomena,
                                                mechanism-level addressings)
    docs/validation-ledger/data/ledger.json  -- sealed EFC validation ledger

The atlas.json file itself is produced by dumping the Symbiose knowledge graph
(Framework / Phenomenon / ADDRESSES relations). Regenerate it by running the
graph dump separately -- this script only consumes it. Keeping the two steps
separate means:

    graph state -> atlas.json   (via Symbiose dump, out of scope here)
    atlas.json + ledger.json -> EFC_Atlas.html   (this script)

The build is idempotent: same input JSON yields byte-identical HTML output,
so git diffs are signal, not noise.

Usage:

    python scripts/build_atlas.py

Outputs:

    docs/public/EFC_Atlas.html

No dependencies beyond the Python standard library.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]


# ------------------------------------------------------------------
# Single source of truth for the cross-page navbar
# ------------------------------------------------------------------
# The canonical 12-entry navbar lives in
# scripts/maintenance/efc_navbar_sync.py. We import its render_nav() so
# this script and the navbar-sync script can never disagree on order,
# labels, idempotency markers, or the active-page highlight.
_NAV_SCRIPT = REPO_ROOT / "scripts" / "maintenance" / "efc_navbar_sync.py"
_nav_spec = importlib.util.spec_from_file_location("efc_navbar_sync", _NAV_SCRIPT)
_nav_module = importlib.util.module_from_spec(_nav_spec)
_nav_spec.loader.exec_module(_nav_module)
render_canonical_navbar = _nav_module.render_nav
DATA_DIR = REPO_ROOT / "docs" / "validation-ledger" / "data"
PUBLIC_DIR = REPO_ROOT / "docs" / "public"

ATLAS_JSON = DATA_DIR / "atlas.json"
LEDGER_JSON = DATA_DIR / "ledger.json"
OUTPUT_HTML = PUBLIC_DIR / "EFC_Atlas.html"


# ------------------------------------------------------------------
# Loading
# ------------------------------------------------------------------
def load_json(path: Path) -> dict:
    if not path.exists():
        sys.stderr.write(f"ERROR: missing {path}\n")
        sys.exit(1)
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------
# HTML rendering
# ------------------------------------------------------------------
HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Energy-Flow Cosmology (EFC) &ndash; Framework Atlas</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    html { font-size: 16px; }
    body {
      font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      line-height: 1.7;
      color: #1a1a2e;
      background: #ffffff;
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem 2.5rem 3rem;
    }
    h1 {
      font-size: 1.8rem; font-weight: 700; color: #0d1b3e;
      border-bottom: 3px solid #007bff;
      padding-bottom: 0.6rem; margin-bottom: 1.2rem;
    }
    h2 {
      font-size: 1.35rem; font-weight: 600; color: #1a3a6b;
      margin-top: 2.2rem; margin-bottom: 0.8rem;
      border-left: 4px solid #007bff; padding-left: 0.7rem;
    }
    h3 {
      font-size: 1.1rem; font-weight: 600; color: #2a4a7f;
      margin-top: 1.6rem; margin-bottom: 0.5rem;
    }
    p { margin: 0.6rem 0; }
    a { color: #0056b3; text-decoration: none; }
    a:hover { text-decoration: underline; color: #003d80; }
    hr { border: none; border-top: 1px solid #d0d7e3; margin: 2rem 0; }
    ul, ol { padding-left: 1.6rem; }
    li { margin-bottom: 0.3rem; }
    table {
      width: 100%; border-collapse: collapse;
      margin-bottom: 1.5rem; font-size: 0.88rem;
      box-shadow: 0 1px 4px rgba(0,0,0,0.06);
      border-radius: 6px; overflow: hidden;
    }
    thead { background-color: #eaf0f9; }
    th {
      border: 1px solid #d0d7e3; padding: 10px 12px;
      text-align: left; font-weight: 600; color: #1a3a6b;
    }
    td { border: 1px solid #e2e6ed; padding: 8px 12px; vertical-align: top; }
    tbody tr:hover { background-color: #f5f8fd; }
    strong { color: #0d1b3e; }
    sub, sup { font-size: 0.78em; }
    code {
      font-family: 'Courier New', monospace; font-size: 0.90em;
      background: #f0f2f5; padding: 1px 5px; border-radius: 3px;
    }
    .badge-kill   { display:inline-block; background:#c22;    color:#fff; font-size:0.72em; padding:2px 7px; border-radius:3px; font-weight:600; letter-spacing:0.3px; }
    .badge-damage { display:inline-block; background:#d4a017; color:#fff; font-size:0.72em; padding:2px 7px; border-radius:3px; font-weight:600; letter-spacing:0.3px; }
    .badge-sealed { display:inline-block; background:#1a7a1a; color:#fff; font-size:0.72em; padding:2px 7px; border-radius:3px; font-weight:600; letter-spacing:0.3px; }
    .badge-open   { display:inline-block; background:#555;    color:#fff; font-size:0.72em; padding:2px 7px; border-radius:3px; font-weight:600; letter-spacing:0.3px; }
    .badge-pass   { display:inline-block; background:#1a7a1a; color:#fff; font-size:0.72em; padding:2px 7px; border-radius:3px; font-weight:600; }
    .badge-marginal { display:inline-block; background:#d4a017; color:#fff; font-size:0.72em; padding:2px 7px; border-radius:3px; font-weight:600; }
    .badge-planned { display:inline-block; background:#5b6a7a; color:#fff; font-size:0.72em; padding:2px 7px; border-radius:3px; font-weight:600; }
    .badge-fail   { display:inline-block; background:#c22; color:#fff; font-size:0.72em; padding:2px 7px; border-radius:3px; font-weight:600; }

    .regime-L0 { color:#1a7a1a; }
    .regime-L1 { color:#0056b3; }
    .regime-L2 { color:#a8200d; }
    .regime-L3 { color:#6d1a7a; }
    .regime-chip {
      display:inline-block; font-size:0.72em; font-weight:600;
      padding:1px 6px; border-radius:3px; margin-right:6px;
      background:#eef2f8; color:#1a3a6b; border:1px solid #c9d4e4;
    }
    .regime-chip.L0 { background:#e6f4e6; color:#1a5a1a; border-color:#b7d8b7; }
    .regime-chip.L1 { background:#e3edf9; color:#0056b3; border-color:#b9ceea; }
    .regime-chip.L2 { background:#f9e3df; color:#a8200d; border-color:#eac2bb; }
    .regime-chip.L3 { background:#efe3f9; color:#6d1a7a; border-color:#d7bfea; }

    .pred-card {
      background: #fafbfd; border: 1px solid #d0d7e3;
      border-left: 4px solid #007bff; border-radius: 6px;
      padding: 14px 18px; margin: 1rem 0 1.5rem;
    }
    .pred-card.kill  { border-left-color:#c22; }
    .pred-card.sealed { border-left-color:#1a7a1a; }
    .pred-card h3 { margin-top: 0; }
    .pred-card table { margin-bottom: 0.6rem; }

    .hero {
      background: linear-gradient(180deg, #f0f5fc 0%, #fafbfd 100%);
      border: 1px solid #c9d4e4; border-left: 5px solid #c22;
      border-radius: 8px; padding: 22px 26px; margin: 1rem 0 1.8rem;
    }
    .hero h2 {
      margin-top: 0; border: none; padding: 0;
      font-size: 1.5rem; color: #0d1b3e;
    }
    .hero-meta {
      display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px; margin: 1rem 0 1.2rem;
    }
    .hero-meta .cell {
      background:#fff; border:1px solid #d0d7e3; border-radius:5px;
      padding: 8px 12px; font-size: 0.86rem;
    }
    .hero-meta .cell .lbl {
      display:block; font-size:0.70rem; text-transform:uppercase;
      letter-spacing:0.5px; color:#5b6a7a; font-weight:600;
    }
    .hero-meta .cell .val {
      display:block; font-size:1.0rem; color:#0d1b3e; font-weight:600;
      font-family: 'Courier New', monospace;
    }

    .nav-tabs {
      display: flex; gap: 2px; margin: 1rem 0 1.3rem;
      border-bottom: 2px solid #d0d7e3;
    }
    .nav-tab {
      background: #eaf0f9; color: #1a3a6b;
      border: 1px solid #d0d7e3; border-bottom: none;
      padding: 9px 16px; cursor: pointer; font-weight: 600;
      font-size: 0.92rem; border-radius: 6px 6px 0 0;
      font-family: inherit;
    }
    .nav-tab:hover { background: #dfe7f3; }
    .nav-tab.active {
      background: #ffffff; color: #0d1b3e;
      border-bottom: 2px solid #ffffff; position: relative; top: 2px;
    }
    .tab-panel { display: none; }
    .tab-panel.active { display: block; }

    .filter-row {
      display:flex; flex-wrap:wrap; gap: 8px; align-items:center;
      margin: 0.8rem 0 1rem;
    }
    .filter-row label { font-size: 0.85rem; color: #5b6a7a; font-weight: 600; }
    .filter-row select, .filter-row input {
      font-size: 0.88rem; padding: 5px 8px;
      border: 1px solid #c9d4e4; border-radius: 4px;
      font-family: inherit; background: #fff;
    }

    .framework-grid, .phenomenon-grid {
      display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 12px; margin: 1rem 0;
    }
    .fw-card, .phen-card {
      background: #fafbfd; border: 1px solid #d0d7e3;
      border-left: 4px solid #007bff; border-radius: 5px;
      padding: 10px 14px; font-size: 0.86rem;
    }
    .fw-card.efc { border-left-color: #1a7a1a; background:#f1f9f1; }
    .fw-card .fw-name { font-weight: 600; color:#0d1b3e; font-size:0.95rem; }
    .fw-card .fw-meta { font-size:0.78rem; color:#5b6a7a; margin-top:4px; }

    .mechanism-pill {
      display:inline-block; font-size:0.74rem;
      background:#eef2f8; color:#1a3a6b;
      padding: 1px 6px; border-radius: 3px;
      font-family: 'Courier New', monospace;
    }

    @media (max-width: 768px) {
      body { padding: 1rem; }
      h1 { font-size: 1.4rem; }
      table { font-size: 0.8rem; }
      th, td { padding: 6px 8px; }
    }
  </style>
</head>

<body>

<h1>Energy-Flow Cosmology (EFC) &mdash; Framework Atlas</h1>

__CANONICAL_NAVBAR__

<p style="font-size:0.95em; color:#555; margin-bottom:1.2em;">
Morten Magnusson &middot; Symbiose Research, Sandnes, Norway &middot;
ORCID: <a href="https://orcid.org/0009-0002-4860-5095">0009-0002-4860-5095</a> &middot;
__GENERATED_DATE__ &middot; CC-BY-4.0
</p>

<p style="font-size:0.93rem; color:#1a3a6b; background:#f0f5fc; border:1px solid #c9d4e4; border-radius:5px; padding:10px 14px;">
The Atlas joins two data sources: the immutable sealed <strong>Validation Ledger</strong>
(EFC's own predictions with DOI, hash, freeze-timestamp) and the
<strong>Framework Atlas</strong> (<strong>__FW_COUNT__</strong> cosmology/gravity
frameworks &mdash; <strong>__RIVAL_COUNT__</strong> rivals plus EFC itself &mdash; with their
RCMP regime participation, ontological lens, and mechanism-level
predictions across <strong>__PHEN_COUNT__</strong> phenomena). Together they make
cross-framework discrimination explicit: for every phenomenon the Atlas records which
frameworks address it, with what mechanism, and with what role.
</p>

<div class="nav-tabs" role="tablist">
  <button class="nav-tab active" data-tab="demo">Sealed predictions</button>
  <button class="nav-tab" data-tab="predictions">All predictions</button>
  <button class="nav-tab" data-tab="phenomena">Phenomena</button>
  <button class="nav-tab" data-tab="frameworks">Frameworks</button>
</div>

<!-- =========================================================
     TAB 1: SEALED PREDICTIONS (all P1..P6 + KT-4, layer-grouped)
     ========================================================= -->
<section class="tab-panel active" id="tab-demo">
__DEMO_CONTENT__
</section>

<!-- =========================================================
     TAB 2: ALL PREDICTIONS (from ledger.json)
     ========================================================= -->
<section class="tab-panel" id="tab-predictions">
<h2>All validation tests</h2>
<p>
Sourced from the sealed <a href="EFC_Validation_Ledger.html">Validation Ledger</a>.
<strong>__LEDGER_TOTAL__</strong> public tests across __LEDGER_CATEGORIES__ categories.
Filter by category, result or regime.
</p>

<div class="filter-row">
  <label for="filter-category">Category:</label>
  <select id="filter-category">
    <option value="">All</option>
    __LEDGER_CATEGORY_OPTIONS__
  </select>
  <label for="filter-result">Result:</label>
  <select id="filter-result">
    <option value="">All</option>
    <option value="PASS">PASS</option>
    <option value="MARGINAL">MARGINAL</option>
    <option value="FAIL">FAIL</option>
    <option value="Planned">Planned</option>
  </select>
  <input type="text" id="filter-search" placeholder="Search name / prediction..." style="flex:1; min-width:180px;">
</div>

<table id="predictions-table">
  <thead>
    <tr>
      <th>Result</th>
      <th>Category</th>
      <th>Name</th>
      <th>Prediction</th>
      <th>Data source</th>
    </tr>
  </thead>
  <tbody>
__LEDGER_ROWS__
  </tbody>
</table>
</section>

<!-- =========================================================
     TAB 3: PHENOMENA (one card per phenomenon with addressings)
     ========================================================= -->
<section class="tab-panel" id="tab-phenomena">
<h2>Phenomena &mdash; cross-framework matrix</h2>
<p>
Every phenomenon in the Atlas with the list of frameworks that address it and the
mechanism each uses. The phenomenon regime (L0&ndash;L3) is shown as a chip &mdash; this
is the primary structural dimension of RCMP.
</p>

<div class="filter-row">
  <label for="phen-regime">Regime:</label>
  <select id="phen-regime">
    <option value="">All</option>
    <option value="L0">L0 &ndash; Background</option>
    <option value="L1">L1 &ndash; Linear perturbations</option>
    <option value="L2">L2 &ndash; LSS / lensing</option>
    <option value="L3">L3 &ndash; Strong regime</option>
  </select>
</div>

__PHENOMENA_BLOCKS__
</section>

<!-- =========================================================
     TAB 4: FRAMEWORKS (42 cards)
     ========================================================= -->
<section class="tab-panel" id="tab-frameworks">
<h2>Frameworks &mdash; 42 cosmology/gravity frameworks</h2>
<p>
Each card shows the framework's ontological lens, RCMP primary regime, year, and key
primitives. The EFC card is highlighted &mdash; all others are rivals tracked in the
Atlas for discrimination.
</p>

<div class="filter-row">
  <label for="fw-lens">Lens:</label>
  <select id="fw-lens">
    <option value="">All</option>
    __LENS_OPTIONS__
  </select>
  <label for="fw-layer">Primary layer:</label>
  <select id="fw-layer">
    <option value="">All</option>
    <option value="L0">L0</option>
    <option value="L1">L1</option>
    <option value="L2">L2</option>
    <option value="L3">L3</option>
  </select>
</div>

<div class="framework-grid">
__FRAMEWORK_CARDS__
</div>
</section>

<script>
(function(){
  // ---- tab switching ----
  var tabs = document.querySelectorAll('.nav-tab');
  var panels = document.querySelectorAll('.tab-panel');
  tabs.forEach(function(btn){
    btn.addEventListener('click', function(){
      tabs.forEach(function(b){ b.classList.remove('active'); });
      panels.forEach(function(p){ p.classList.remove('active'); });
      btn.classList.add('active');
      var t = btn.getAttribute('data-tab');
      var panel = document.getElementById('tab-' + t);
      if (panel) panel.classList.add('active');
    });
  });

  // ---- predictions table filter ----
  function applyPredictionFilter(){
    var cat = document.getElementById('filter-category').value;
    var res = document.getElementById('filter-result').value;
    var q   = document.getElementById('filter-search').value.toLowerCase();
    var rows = document.querySelectorAll('#predictions-table tbody tr');
    rows.forEach(function(row){
      var rowCat = row.getAttribute('data-category') || '';
      var rowRes = row.getAttribute('data-result') || '';
      var text = row.textContent.toLowerCase();
      var show = true;
      if (cat && rowCat !== cat) show = false;
      if (res && rowRes.toUpperCase().indexOf(res.toUpperCase()) < 0) show = false;
      if (q && text.indexOf(q) < 0) show = false;
      row.style.display = show ? '' : 'none';
    });
  }
  ['filter-category','filter-result','filter-search'].forEach(function(id){
    var el = document.getElementById(id);
    if (el) el.addEventListener('input', applyPredictionFilter);
    if (el) el.addEventListener('change', applyPredictionFilter);
  });

  // ---- phenomena regime filter ----
  var phenRegime = document.getElementById('phen-regime');
  if (phenRegime) phenRegime.addEventListener('change', function(){
    var r = phenRegime.value;
    document.querySelectorAll('.phen-block').forEach(function(b){
      var br = b.getAttribute('data-regime') || '';
      b.style.display = (!r || br.indexOf(r) >= 0) ? '' : 'none';
    });
  });

  // ---- framework grid filter ----
  function applyFwFilter(){
    var lens = document.getElementById('fw-lens').value;
    var layer = document.getElementById('fw-layer').value;
    document.querySelectorAll('.fw-card').forEach(function(c){
      var cl = c.getAttribute('data-lens') || '';
      var ly = c.getAttribute('data-layer') || '';
      var show = true;
      if (lens && cl !== lens) show = false;
      if (layer && ly !== layer) show = false;
      c.style.display = show ? '' : 'none';
    });
  }
  ['fw-lens','fw-layer'].forEach(function(id){
    var el = document.getElementById(id);
    if (el) el.addEventListener('change', applyFwFilter);
  });
})();
</script>

</body>
</html>
"""


def _esc(s):
    """HTML escape for text nodes. Handles already-escaped entities in ledger
    content (ledger.json stores some values with &lt;/&gt; already encoded) by
    first unescaping common named entities, then re-escaping. This avoids
    double-encoding like &amp;lt;."""
    if s is None:
        return ""
    text = str(s)
    # Unescape common pre-encoded entities first.
    text = (
        text.replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&quot;", '"')
            .replace("&#39;", "'")
    )
    # Now escape properly.
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )


def _result_badge(result: str) -> str:
    r = (result or "").upper()
    if "PASS" in r:
        return '<span class="badge-pass">PASS</span>'
    if "MARGINAL" in r or "PARTIAL" in r:
        return '<span class="badge-marginal">MARGINAL</span>'
    if "FAIL" in r:
        return '<span class="badge-fail">FAIL</span>'
    if "PLANNED" in r or r == "":
        return '<span class="badge-planned">Planned</span>'
    return f'<span class="badge-open">{_esc(result)}</span>'


_BADGE_CLASS = {
    "KILL": "badge-kill",
    "DAMAGE": "badge-damage",
    "PROVEN": "badge-sealed",
    "STRUCTURAL": "badge-sealed",
    "SEALED": "badge-sealed",
}

_HERO_BORDER = {
    "KILL": "#c22",
    "DAMAGE": "#d4a017",
    "PROVEN": "#1a7a1a",
    "STRUCTURAL": "#5b3a8a",
    "SEALED": "#1a7a1a",
}

_LAYER_LABEL = {
    "L0": "L0 &mdash; Background",
    "L1": "L1 &mdash; Linear perturbations",
    "L2": "L2 &mdash; LSS / lensing",
    "L3": "L3 &mdash; Strong regime",
}


def _render_single_prediction(pred: dict, addressings: list, phenomena: dict) -> str:
    """Render one sealed prediction as a hero card: metadata + rivals from
    atlas.addressings + Stage-III sandwich + narrative + exclusion lemma."""
    pid = pred.get("id", "")
    badge = (pred.get("badge") or "SEALED").upper()
    badge_cls = _BADGE_CLASS.get(badge, "badge-sealed")
    border = _HERO_BORDER.get(badge, "#1a7a1a")
    layer = pred.get("rcmp_layer", "")
    phen_id = pred.get("phenomenon", "")
    phen = phenomena.get(phen_id, {})

    # rivals for this phenomenon (exclude EFC)
    rivals = sorted(
        [a for a in addressings if a["phenomenon"] == phen_id and a["framework"] != "EFC"],
        key=lambda x: x["framework"],
    )
    efc_entry = next((a for a in addressings if a["phenomenon"] == phen_id and a["framework"] == "EFC"), None)

    rival_rows = []
    for r in rivals:
        rival_rows.append(
            f'<tr><td>{_esc(r["framework"])}</td>'
            f'<td>{_esc(r["role"])}</td>'
            f'<td><span class="mechanism-pill">{_esc(r["mechanism"])}</span></td></tr>'
        )
    if efc_entry:
        efc_row = (
            f'<tr style="background:#f1f9f1;"><td><strong style="color:#1a7a1a;">EFC</strong></td>'
            f'<td>{_esc(efc_entry["role"])}</td>'
            f'<td><span class="mechanism-pill">{_esc(efc_entry["mechanism"])}</span></td></tr>'
        )
    else:
        efc_row = ""
    rival_rows_html = efc_row + "\n".join(rival_rows)

    rival_count_label = (
        f"1 EFC + {len(rivals)} rival framework{'s' if len(rivals) != 1 else ''} tracked for this phenomenon"
    )

    # metric cells (only render cells where we have a value)
    cells = []
    if pred.get("efc_value"):
        cells.append(("EFC", pred["efc_value"]))
    if pred.get("lcdm_value"):
        cells.append(("\u039bCDM", pred["lcdm_value"]))
    if pred.get("seal_doi"):
        cells.append(("Seal DOI", f'<a href="https://doi.org/{_esc(pred["seal_doi"])}">{_esc(pred["seal_doi"])}</a>'))
    if pred.get("hash"):
        cells.append(("Hash", pred["hash"]))
    if pred.get("frozen_at"):
        cells.append(("Frozen at", pred["frozen_at"]))
    if pred.get("arbiter_instrument"):
        cells.append(("Arbiter", pred["arbiter_instrument"]))
    if pred.get("falsifier_id"):
        cells.append(("Falsifier", pred["falsifier_id"]))
    if pred.get("pass_window"):
        pw = pred["pass_window"]
        cells.append(("PASS window", f"[{pw.get('low')}, {pw.get('high')}]"))

    cell_html = "".join(
        f'<div class="cell"><span class="lbl">{_esc(lbl)}</span>'
        f'<span class="val" style="font-size:0.86rem;">{val if lbl=="Seal DOI" else _esc(val)}</span></div>'
        for (lbl, val) in cells
    )

    # sandwich
    sandwich_items = "".join(
        f'<li><strong>{_esc(s["survey"])}</strong> <em style="color:#5b6a7a;">({_esc(s["role"])})</em>: {_esc(s["result"])}</li>'
        for s in pred.get("stage_iii_sandwich", [])
    )

    # falsifier block
    falsifier_block = ""
    if pred.get("falsifier_condition"):
        fid = pred.get("falsifier_id") or "F?"
        falsifier_block = (
            f'<h4 style="color:#0d1b3e; margin-top:1rem;">Falsifier &mdash; {_esc(fid)}</h4>'
            f'<p style="background:#fff; border:1px solid #eac2bb; border-left:4px solid #c22; '
            f'border-radius:4px; padding:8px 12px; margin:0.3rem 0 0.8rem; font-size:0.90rem;">'
            f'<strong>If observed:</strong> {_esc(pred["falsifier_condition"])}</p>'
        )

    # exclusion lemma
    excl_block = ""
    if pred.get("exclusion_lemma"):
        excl_block = (
            '<h4 style="color:#0d1b3e; margin-top:1rem;">Exclusion lemma</h4>'
            f'<p style="background:#f0f5fc; border:1px solid #c9d4e4; border-radius:4px; '
            f'padding:8px 12px; margin:0.3rem 0 0.8rem; font-size:0.90rem;">'
            f'{_esc(pred["exclusion_lemma"])}</p>'
        )

    # claim
    claim_block = ""
    if pred.get("claim"):
        claim_block = (
            '<p style="font-size:0.92rem; color:#1a3a6b; background:#fafbfd; '
            'border-left:3px solid #c9d4e4; padding:8px 12px; margin:0.6rem 0;">'
            f'<strong>Claim:</strong> {_esc(pred["claim"])}</p>'
        )

    phen_name = _esc(phen.get("name", phen_id))
    phen_code = _esc(phen_id)

    return f"""
<div class="hero" style="border-left-color:{border};" id="pred-{_esc(pid)}">
  <div style="margin-bottom:0.4rem;">
    <span class="{badge_cls}">{_esc(badge)}</span>
    <span class="regime-chip {_esc(layer)}">{_LAYER_LABEL.get(layer, _esc(layer))}</span>
    <span style="font-size:0.82rem; color:#5b6a7a; margin-left:6px;">
      <strong>{_esc(pid)}</strong> &middot; phenomenon: {phen_name} <code style="color:#5b6a7a;">{phen_code}</code>
    </span>
  </div>
  <h3 style="margin-top:0.4rem; font-size:1.18rem; color:#0d1b3e;">{_esc(pred["title"])}</h3>
  <p style="margin-top:0.4rem; color:#1a3a6b; font-size:0.94rem;">{_esc(pred.get("narrative_intro", ""))}</p>

  <div class="hero-meta">{cell_html}</div>

  {claim_block}
  {falsifier_block}

  <h4 style="color:#0d1b3e; margin-top:1rem;">Rival frameworks &mdash; {rival_count_label}</h4>
  <table style="margin-top:0.4rem;">
    <thead><tr><th style="width:22%;">Framework</th><th style="width:24%;">Role</th><th>Mechanism</th></tr></thead>
    <tbody>
{rival_rows_html}
    </tbody>
  </table>

  {excl_block}

  <h4 style="color:#0d1b3e; margin-top:1rem;">Stage-III empirical sandwich</h4>
  <ul style="margin:0.4rem 0 0.2rem;">
    {sandwich_items}
  </ul>
</div>
"""


def render_demo(demos: list, addressings: list, phenomena: dict) -> str:
    """Render all sealed predictions, grouped by RCMP layer (L0..L3)."""
    if not demos:
        return "<p><em>No sealed predictions registered.</em></p>"

    # introduction
    by_badge = {}
    for d in demos:
        b = (d.get("badge") or "SEALED").upper()
        by_badge[b] = by_badge.get(b, 0) + 1
    badge_summary = " &middot; ".join(
        f'<span class="{_BADGE_CLASS.get(b, "badge-sealed")}">{b}: {n}</span>'
        for b, n in sorted(by_badge.items())
    )

    intro = f"""
<h2>Sealed predictions</h2>
<p style="font-size:0.94rem; color:#1a3a6b;">
{len(demos)} preregistered EFC predictions with sealed DOIs, grouped by RCMP layer.
Each card shows EFC's prediction, the {_LAYER_LABEL.get("L2", "L2")[:0]}full rival list from the
atlas (every framework that addresses the same phenomenon with its own mechanism), a
Stage-III empirical sandwich that brackets the prediction with already-observed survey
data, and the arbiter instrument scheduled to resolve it.
</p>
<p style="font-size:0.92rem; color:#5b6a7a;">Badge mix: {badge_summary}</p>
"""

    # group by layer
    layers = ["L0", "L1", "L2", "L3"]
    groups = {layer: [] for layer in layers}
    for d in demos:
        layer = d.get("rcmp_layer", "")
        groups.setdefault(layer, []).append(d)

    parts = [intro]
    for layer in layers:
        items = groups.get(layer, [])
        if not items:
            continue
        parts.append(
            f'<h3 style="margin-top:2rem; border-left:4px solid #007bff; padding-left:0.7rem;">'
            f'{_LAYER_LABEL.get(layer, layer)} <span style="font-size:0.88rem; color:#5b6a7a; font-weight:400;">'
            f'({len(items)} prediction{"s" if len(items) != 1 else ""})</span></h3>'
        )
        for pred in items:
            parts.append(_render_single_prediction(pred, addressings, phenomena))

    return "\n".join(parts)


def render_ledger_rows(ledger: dict):
    rows_html = []
    cats = set()
    total = 0
    for cat, items in ledger.get("tests", {}).items():
        cats.add(cat)
        for item in items:
            total += 1
            name = item.get("name", "") or ""
            if not name.strip():
                # Folded one-off tests (e.g. EFC-VAL reports) lack a public title
                # in ledger.json — counted in the total, but not rendered as a
                # blank row. Their detail lives in the formal validation reports.
                continue
            result = item.get("result", "") or ""
            rows_html.append(
                f'    <tr data-category="{_esc(cat)}" data-result="{_esc(result)}">'
                f'<td>{_result_badge(result)}</td>'
                f'<td>{_esc(cat)}</td>'
                f'<td><strong>{_esc(name)}</strong></td>'
                f'<td>{_esc(item.get("prediction", ""))}</td>'
                f'<td style="font-size:0.82rem; color:#5b6a7a;">{_esc(item.get("data_source", ""))}</td>'
                f"</tr>"
            )
    cat_options = "\n".join(
        f'    <option value="{_esc(c)}">{_esc(c)}</option>' for c in sorted(cats)
    )
    return "\n".join(rows_html), total, sorted(cats), cat_options


def render_phenomena_blocks(phenomena, addressings):
    by_phen = {}
    for a in addressings:
        by_phen.setdefault(a["phenomenon"], []).append(a)

    ordered = sorted(phenomena.values(), key=lambda p: p["id"])
    parts = []
    for p in ordered:
        pid = p["id"]
        regime = p.get("regime") or ""
        regime_class = regime.split("-")[0] if regime else ""
        entries = sorted(by_phen.get(pid, []), key=lambda x: x["framework"])
        if not entries:
            continue
        rows = []
        for e in entries:
            is_efc = e["framework"] == "EFC"
            name_cell = (
                f'<strong style="color:#1a7a1a;">{_esc(e["framework"])}</strong>'
                if is_efc
                else _esc(e["framework"])
            )
            rows.append(
                f"<tr><td>{name_cell}</td>"
                f"<td>{_esc(e['role'])}</td>"
                f'<td><span class="mechanism-pill">{_esc(e["mechanism"])}</span></td></tr>'
            )
        rows_html = "\n".join(rows)
        regime_chip = (
            f'<span class="regime-chip {regime_class}">{_esc(regime)}</span>'
            if regime
            else ""
        )
        parts.append(
            f"""
<div class="phen-block" data-regime="{_esc(regime)}" style="margin-bottom:1.5rem;">
  <h3>{regime_chip} {_esc(p["name"])} <code style="font-weight:400; color:#5b6a7a;">{_esc(pid)}</code></h3>
  <table>
    <thead><tr><th style="width:20%;">Framework</th><th style="width:22%;">Role</th><th>Mechanism</th></tr></thead>
    <tbody>
{rows_html}
    </tbody>
  </table>
</div>
"""
        )
    return "\n".join(parts)


def render_framework_cards(frameworks):
    parts = []
    lenses = set()
    for f in sorted(frameworks, key=lambda x: x["id"]):
        lens = f.get("lens", "")
        layer = f.get("rcmp_primary_layer", "")
        lenses.add(lens)
        is_efc = f["id"] == "EFC"
        extra_class = " efc" if is_efc else ""
        primitives = ", ".join(f.get("key_primitives", []) or [])
        parts.append(
            f"""
<div class="fw-card{extra_class}" data-lens="{_esc(lens)}" data-layer="{_esc(layer)}">
  <div class="fw-name">{_esc(f.get("full_name", f["id"]))}</div>
  <div class="fw-meta">
    <span class="regime-chip {_esc(layer)}">{_esc(layer)}</span>
    <span style="margin-right:6px;">{_esc(lens)}</span>
    <span style="color:#5b6a7a;">{_esc(f.get("year", ""))}</span>
  </div>
  <div style="margin-top:6px; font-size:0.80rem; color:#5b6a7a;">
    <strong>Primitives:</strong> <code>{_esc(primitives) or "&ndash;"}</code>
  </div>
  <div style="margin-top:4px; font-size:0.78rem; color:#5b6a7a;">
    EFC relation: <em>{_esc(f.get("efc_relation", ""))}</em>
  </div>
</div>
"""
        )
    lens_options = "\n".join(
        f'    <option value="{_esc(l)}">{_esc(l)}</option>' for l in sorted(lenses) if l
    )
    return "\n".join(parts), lens_options


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main():
    atlas = load_json(ATLAS_JSON)
    ledger = load_json(LEDGER_JSON)

    frameworks = atlas["frameworks"]
    phenomena_list = atlas["phenomena"]
    phenomena = {p["id"]: p for p in phenomena_list}
    addressings = atlas["addressings"]

    # Demo content — render ALL sealed predictions, grouped by RCMP layer
    demo_list = atlas.get("tier1_demo_predictions", [])
    if not demo_list:
        sys.stderr.write("ERROR: atlas.json missing tier1_demo_predictions\n")
        sys.exit(1)
    demo_content = render_demo(demo_list, addressings, phenomena)

    ledger_rows, total, cats, cat_options = render_ledger_rows(ledger)
    phenomena_blocks = render_phenomena_blocks(phenomena, addressings)
    framework_cards, lens_options = render_framework_cards(frameworks)

    generated_date = atlas.get("generated_at", "")[:10] or "generated"

    html = HTML_TEMPLATE
    rival_count = sum(1 for f in frameworks if f.get("id") != "EFC")
    replacements = {
        "__CANONICAL_NAVBAR__": render_canonical_navbar(active_href="EFC_Atlas.html"),
        "__GENERATED_DATE__": generated_date,
        "__FW_COUNT__": str(len(frameworks)),
        "__RIVAL_COUNT__": str(rival_count),
        "__PHEN_COUNT__": str(len(phenomena_list)),
        "__DEMO_CONTENT__": demo_content,
        "__LEDGER_TOTAL__": str(total),
        "__LEDGER_CATEGORIES__": str(len(cats)),
        "__LEDGER_CATEGORY_OPTIONS__": cat_options,
        "__LEDGER_ROWS__": ledger_rows,
        "__PHENOMENA_BLOCKS__": phenomena_blocks,
        "__FRAMEWORK_CARDS__": framework_cards,
        "__LENS_OPTIONS__": lens_options,
    }
    for k, v in replacements.items():
        html = html.replace(k, v)

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote {OUTPUT_HTML}")
    print(f"  frameworks: {len(frameworks)}  phenomena: {len(phenomena_list)}  addressings: {len(addressings)}")
    print(f"  ledger tests: {total} across {len(cats)} categories")


if __name__ == "__main__":
    main()
