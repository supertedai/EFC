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

import json
import sys
from pathlib import Path


# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
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

<div style="background:#f8f9fa; border:1px solid #d0d7e3; border-radius:6px; padding:12px 18px; margin-bottom:1.5rem; font-size:0.92rem;">
  <a href="EFC_Elevator_Pitch.html" style="margin-right:1.5rem; font-weight:600;">Pitch</a>
  <a href="EFC_Validation_Ledger.html" style="margin-right:1.5rem; font-weight:600;">Ledger</a>
  <a href="EFC_White_Paper_Series.html" style="margin-right:1.5rem; font-weight:600;">White Paper</a>
  <a href="EFC_Stage-IV_Data_Roadmap.html" style="margin-right:1.5rem; font-weight:600;">Roadmap</a>
  <a href="EFC_Gap_Analysis.html" style="margin-right:1.5rem; font-weight:600;">Gaps</a>
  <a href="EFC_External_Research_Ledger.html" style="margin-right:1.5rem; font-weight:600;">External</a>
  <a href="EFC_Predictions.html" style="margin-right:1.5rem; font-weight:600;">Predictions</a>
  <a href="EFC_Atlas.html" style="margin-right:1.5rem; font-weight:600;">Atlas</a>
  <a href="EFC_Changelog.html" style="font-weight:600;">Changelog</a>
</div>

<p style="font-size:0.95em; color:#555; margin-bottom:1.2em;">
Morten Magnusson &middot; Symbiose Research, Sandnes, Norway &middot;
ORCID: <a href="https://orcid.org/0009-0002-4860-5095">0009-0002-4860-5095</a> &middot;
__GENERATED_DATE__ &middot; CC-BY-4.0
</p>

<p style="font-size:0.93rem; color:#1a3a6b; background:#f0f5fc; border:1px solid #c9d4e4; border-radius:5px; padding:10px 14px;">
The Atlas joins two data sources: the immutable sealed <strong>Validation Ledger</strong>
(EFC's own predictions with DOI, hash, freeze-timestamp) and the
<strong>Framework Atlas</strong> (<strong>__FW_COUNT__</strong> rival cosmology/gravity
frameworks with their RCMP regime participation, ontological lens, and mechanism-level
predictions across <strong>__PHEN_COUNT__</strong> phenomena). Together they make
cross-framework discrimination explicit: for every phenomenon the Atlas records which
frameworks address it, with what mechanism, and with what role.
</p>

<div class="nav-tabs" role="tablist">
  <button class="nav-tab active" data-tab="demo">Demo (KILL prediction)</button>
  <button class="nav-tab" data-tab="predictions">All predictions</button>
  <button class="nav-tab" data-tab="phenomena">Phenomena</button>
  <button class="nav-tab" data-tab="frameworks">Frameworks</button>
</div>

<!-- =========================================================
     TAB 1: DEMO (P1 phi_psi_slip)
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


def render_demo(demo: dict, addressings: list, phenomena: dict) -> str:
    phen_id = demo["phenomenon"]
    phen_name = phenomena.get(phen_id, {}).get("name", phen_id)

    # rival rows (exclude EFC itself)
    rivals = [a for a in addressings if a["phenomenon"] == phen_id and a["framework"] != "EFC"]
    rivals.sort(key=lambda x: x["framework"])
    rows = []
    for r in rivals:
        rows.append(
            f'    <tr>'
            f'<td>{_esc(r["framework"])}</td>'
            f'<td>{_esc(r["role"])}</td>'
            f'<td><span class="mechanism-pill">{_esc(r["mechanism"])}</span></td>'
            f'</tr>'
        )
    rival_table = "\n".join(rows)

    sandwich = "".join(
        f'<li><strong>{_esc(s["survey"])}</strong> ({_esc(s["role"])}): '
        f'{_esc(s["result"])}</li>'
        for s in demo.get("stage_iii_sandwich", [])
    )

    return f"""
<div class="hero">
  <div style="margin-bottom:0.4rem;">
    <span class="badge-kill">KILL</span>
    <span class="regime-chip L2">L2 &mdash; LSS / lensing</span>
    <span style="font-size:0.82rem; color:#5b6a7a; margin-left:6px;">Preregistered &middot; sealed DOI</span>
  </div>
  <h2>{_esc(demo["title"])}</h2>
  <p style="margin-top:0.5rem; color:#1a3a6b;">
    {_esc(demo["narrative_intro"])}
  </p>

  <div class="hero-meta">
    <div class="cell"><span class="lbl">EFC prediction</span><span class="val">{_esc(demo["efc_value"])}</span></div>
    <div class="cell"><span class="lbl">Mechanism</span><span class="val" style="font-size:0.82rem;">{_esc(demo["mechanism"])}</span></div>
    <div class="cell"><span class="lbl">Hash</span><span class="val">{_esc(demo["hash"])}</span></div>
    <div class="cell"><span class="lbl">Frozen at</span><span class="val" style="font-size:0.82rem;">{_esc(demo["frozen_at"])}</span></div>
    <div class="cell"><span class="lbl">Seal DOI</span><span class="val" style="font-size:0.82rem;"><a href="https://doi.org/{_esc(demo["seal_doi"])}">{_esc(demo["seal_doi"])}</a></span></div>
    <div class="cell"><span class="lbl">Arbiter</span><span class="val" style="font-size:0.82rem;">{_esc(demo["arbiter_instrument"])}</span></div>
  </div>

  <h3 style="color:#0d1b3e;">Falsifier &mdash; {_esc(demo["falsifier_id"])}</h3>
  <p style="background:#fff; border:1px solid #eac2bb; border-left:4px solid #c22; border-radius:4px; padding:8px 12px; margin:0.4rem 0 0.9rem;">
    <strong>If observed:</strong> {_esc(demo["falsifier_condition"])} &rarr; EFC killed on this prediction.
  </p>

  <h3 style="color:#0d1b3e;">Rival frameworks &mdash; {len(rivals)} monotonic, relative divergence = {_esc(demo["relative_divergence"])}</h3>
  <table style="margin-top:0.5rem;">
    <thead><tr><th>Framework</th><th>Role</th><th>Mechanism</th></tr></thead>
    <tbody>
{rival_table}
    </tbody>
  </table>

  <h3 style="color:#0d1b3e;">Exclusion lemma</h3>
  <p style="background:#f0f5fc; border:1px solid #c9d4e4; border-radius:4px; padding:8px 12px; margin:0.4rem 0 0.9rem;">
    {_esc(demo["exclusion_lemma"])}
  </p>

  <h3 style="color:#0d1b3e;">Stage-III empirical sandwich</h3>
  <ul>
    {sandwich}
  </ul>
  <p style="font-size:0.88rem; color:#5b6a7a;">
    Lower- and upper-half of the &Sigma;<sub>eff</sub>(z) profile are already anchored by Stage-III
    data. Euclid DR1 is expected to resolve the crossover position directly in October 2026.
  </p>
</div>
"""


def render_ledger_rows(ledger: dict):
    rows_html = []
    cats = set()
    total = 0
    for cat, items in ledger.get("tests", {}).items():
        cats.add(cat)
        for item in items:
            total += 1
            result = item.get("result", "") or ""
            rows_html.append(
                f'    <tr data-category="{_esc(cat)}" data-result="{_esc(result)}">'
                f'<td>{_result_badge(result)}</td>'
                f'<td>{_esc(cat)}</td>'
                f'<td><strong>{_esc(item.get("name", ""))}</strong></td>'
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

    # Demo content (first tier-1 prediction; expect phi_psi_slip)
    demo_list = atlas.get("tier1_demo_predictions", [])
    if not demo_list:
        sys.stderr.write("ERROR: atlas.json missing tier1_demo_predictions\n")
        sys.exit(1)
    demo = demo_list[0]
    demo_content = render_demo(demo, addressings, phenomena)

    ledger_rows, total, cats, cat_options = render_ledger_rows(ledger)
    phenomena_blocks = render_phenomena_blocks(phenomena, addressings)
    framework_cards, lens_options = render_framework_cards(frameworks)

    generated_date = atlas.get("generated_at", "")[:10] or "generated"

    html = HTML_TEMPLATE
    replacements = {
        "__GENERATED_DATE__": generated_date,
        "__FW_COUNT__": str(len(frameworks)),
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
