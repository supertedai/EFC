# EFC Master Sync-Protocol & Maintenance Constitution

**Version:** 1.0 (verified 2026-05-04)
**Status:** Working specification — supersedes earlier fragmented drafts.
**Mandate:** Public canonical pages must never be edited without 8-systems
cross-validation. Energy flows along entropy gradients; so does the repo.

This document captures a single agent-led verification pass against eight truth
sources. It records what was confirmed, what was disproved, and what still
requires a maintainer decision. Numbers below are measurements, not assumptions.

---

## 1. The 8-systems truth ring

| ID | System | Authority |
|---|---|---|
| **S1** | ORCID `0009-0002-4860-5095` | Author identity per DOI |
| **S2** | Figshare `authors_id=20477774` | Published content per DOI |
| **S3** | Repo `docs/papers/efc/<paper>/` | Reproducible 10-file packages |
| **S4** | Repo `docs/public/*.html` (13 pages) | Narrative claims |
| **G1** | Symbiose Neo4j | Discrete graph state |
| **G2** | Symbiose Qdrant `efc` collection | Text/vector semantics |
| **G3** | Symbiose GNN R-GCN | Implicit concept associations |
| **G4** | Symbiose Framework Atlas | Cross-framework cosmology |

Inclusion rule: S1 ⊂ S2 ⊂ S3 ⊂ S4. Authority for "did X happen": S1 > S2 > S3 > S4.
The pipe-ledger at `docs/validation-ledger/` is auto-generated output — not
canonical, drift here is allowed.

---

## 2. Verified snapshot (2026-05-04 20:16 UTC)

### S1 ORCID (cached via `efc_orcid_sync.py`)
- **162** works · 162 figshare-DOIs
- 5 missing in repo: `28098350`, `28102772`, `31970898`, `31970904`, `31970907`
- DOI `32162706` does **not** exist on ORCID (earlier draft assumed it did)

Note: live `pub.orcid.org` API blocked from current sandbox (HTTP 403); cache
is the working ground truth.

### S2 Figshare
Live `api.figshare.com` blocked from sandbox. `efc_orcid_sync.py` cache used
as proxy. No DOI-typo discovered in repo.

### S3 Repository
- `find docs/papers/efc -maxdepth 2 -name 'index.json'` → **159** packages
- 158 with DOI, 1 without (`efc_master/`)
- `figshare/doi-map.json` was a 19-byte `PLACEHOLDER_DOI_MAP` stub — replaced
  by the real generator output committed alongside this document
- Drift detector reported "Changelog claims 158, actual 159" — auto-fix did
  not apply

### S4 Public pages — drift matrix (CRITICAL)

13 pages exist (the earlier draft assumed 9). Headline counts diverge across
four mutually inconsistent sets:

| Page | Version | Tests | Active | Survived | Falsified | Pipeline |
|---|---|---|---|---|---|---|
| Pitch | v1.0 | 135 | 113 | 105 | **8** *and* "Ten" ⚠ | 22 |
| Validation Ledger | v3.17 (HTML) / v4.5 (data) | 135 header / 102 mid / 0 footer ⚠ | 113 | — | "8" header *and* "n_falsified from 10 to 11" v4.5-update ⚠ | — |
| White Paper Series | v4.9 | 135 | 113 | 105 | 8 | — |
| Stage-IV Roadmap | v3.9 | 135 | 113 | 105 | 8 | — |
| **Gap Analysis** | **v3.9 (stale)** | 119 | 101 | 91-101 | **10** | 1 |
| **Changelog** | **v2.2 (stale)** | 100 | 88 | 88-103 | **9** | 1 |
| External Research | — | — | — | — | — | — |
| Predictions | v2.0 | — | — | — | — | — |
| Atlas | v3.3 | — | — | — | — | — |
| Evaluation Ledger 🆕 | empty | — | — | — | — | — |
| Likelihood Ledger 🆕 | empty | — | — | — | — | — |
| Master v1.1 🆕 | v1.1 | — | — | — | — | — |
| Model Comparison 🆕 | empty | — | — | — | — | — |

Inconsistent count sets observed:
- **Set A** (Pitch, White Paper, Roadmap): 135 / 113 / 105 / **8** / 22
- **Set B** (Ledger v4.5-update text): "127 across 5 categories" + "n_falsified from 10 to **11**"
- **Set C** (Gap Analysis): 119 / 101 / **10** / 1 — v3.9 stale
- **Set D** (Changelog): 100 / 88 / **9** / 1 — v2.2 very stale

No single page agrees with Ledger v4.5-update's claim that there are 11
falsified probes.

Ledger arithmetic: v4.5-update paragraph names "44 physics_test, 21
consistency_check, 16 phenomenological, 28 framework_constraint, 22
planned_pipeline" → sum **131** (not 127 as stated, not 130 as the earlier
draft computed). Three internally inconsistent totals on one page: 135 / 127 / 131.

### G1 Neo4j (live)
- `MATCH (v:EFCValidation)` → **308** nodes
- 17 distinct status strings (drift-creep): `unknown` 73, `success` 67,
  `planned` 60, `pending` 58, `failed` 16, `partial` 13, `falsified` 6, `pass` 3,
  `collapsed_in_expected_direction` 3, `frozen` 2, plus 7 singletons including
  case-duplicate `FALSIFIED` (1) and `failure` (1)
- **15 744** unique Publication DOIs (up from 15 667 in earlier draft); 266
  Document DOIs

### G2 Qdrant
- Top White Paper Part 3 chunk indexed at score 0.81 (good coverage)
- DOI metadata field empty in returned chunks; the earlier draft's claim that
  Part 2 carried Part 3's DOI could not be verified on this pass

### G3 GNN
- 24 127 concepts · 128-dim · `has_collapse_alarm: false` ✅
- ⚠ `eval_pass.overall: false` (recall@10 = 0.216, cohen_d fails)

### G4 Framework Atlas
- 43 frameworks · 35 phenomena · 200 addresses · 10 convergences · 29 divergences
- EFC vs ΛCDM: `S8_tension` rel_diff 0.0153, `sigma8_growth` rel_diff 0.0487

### Live state (Symbiose research_status)
- Health score: **62/100**
- 20 candidates pending (down from 84 in earlier draft)
- 14 NEEDS_REVIEW knowledge gaps
- 4 ESCALATED cases (3 with degeneracy_persists stop-conditions)
- 6/7 learning loops connected (`gap_to_fill ❌`)
- 2 sealed predictions: `freeze_20260221_160857` (α=−0.702),
  `freeze_20260218_050713` (α=−0.689)
- KT3 Mass-Scaling MARGINAL across last 4 GRAV runs

---

## 3. Identified breaches (verification-grade)

### Confirmed
| # | Breach | Stage | Detail |
|---|---|---|---|
| **B1** | `figshare/doi-map.json` placeholder | C | Was 19-byte stub; replaced by real generator output in this PR |
| **B4** | Pitch internal contradiction | C | "Ten probes have been falsified" (1×) vs `8 falsified` (3×) — needs maintainer call on canonical value |
| **B5** | Ledger arithmetic mismatch | C | 135 (header) / 127 (v4.5-update) / 131 (sum-of-categories) — three values |
| **B8** | White Paper container vs spec | C | `efc_white_paper_part_1_to_4/` violates "one paper per 8-digit DOI" invariant |
| **B10** | `efc_master/` has no DOI | C | Single dir, decision needed: assign DOI or archive |
| **B12** | 76 % publications without `:HAS_VALIDATION` binding | G1 | `gap_to_fill` learning loop blocked |
| **B13** | 17 status strings, case-duplicates | G1 | `FALSIFIED`/`falsified`, `failure`/`failed`, `pass`/`success` |
| **B14** | 20 candidates pending | G1 | Down from 84; still > 0 |

### Disproved (earlier draft was wrong)
| Earlier claim | Actual |
|---|---|
| ORCID has 163 works | 162 |
| DOI 32162706 missing from repo | DOI does not exist on ORCID |
| README badge v3.17 is drift | v3.17 = public-HTML version (intentional dual-version with v4.5 data) |
| 9 public pages | 13 (4 newer pages: Evaluation/Likelihood/Master_v1.1/Model_Comparison) |
| Sum of categories = 130 | Sum = 131 (44+21+16+28+22) |
| 6 missing from ORCID-not-in-repo | 5 |
| White Paper Part 2 has Part 3 DOI in Qdrant | Could not verify — DOI field empty in chunks |

### Newly observed
- Drift detector reports "Changelog claims 158, actual 159" — auto-fix
  silently failed
- GNN evaluation suite is failing recall@10 and cohen_d despite no collapse alarm
- 4 new public pages exist with no content; not referenced by README/AGENTS/llms.txt

---

## 4. 8-systems guard pre-condition

For each public-page diff that introduces or changes a DOI X:

```
1. S1: curl pub.orcid.org/v3.0/0009-0002-4860-5095/works | grep <X>
   → Yes: author confirmed
   → No:  STOP — DOI is typo or not Morten's
2. S2: curl api.figshare.com/v2/articles/<X>
   → 200 + Morten in authors[]: confirmed
   → 404 or wrong author: STOP
3. S3: find docs/papers/efc -name 'index.json' -exec grep -l '<X>' {} \;
   → exists: 10-file package present
   → missing: STOP, create package first
4. G1: MATCH (n) WHERE n.doi CONTAINS '<X>' RETURN labels(n), n.doi
   → exists: graph node confirmed
   → missing: trigger Symbiose ingest, wait
5. G2: search_documents(query='<title>')
   → chunks present + DOI metadata correct
   → otherwise: re-ingest
6. G4 (cross-framework only): framework_atlas_query(mode='zoom', framework='EFC', phenomenon=<X>)
7. S4: grep '<X>' docs/public/*.html — verify cross-page consistency
8. Internal: category sums = totals; falsified counts match in all paragraphs
```

Implementation candidate: `.github/workflows/efc-public-edit-guard.yml`
calling `scripts/maintenance/eight_systems_guard.py` (not yet written).

---

## 5. Open decisions (require maintainer call)

The following cannot be resolved autonomously without changing claims about
EFC. Each needs an explicit decision before downstream sync proceeds:

1. **Canonical falsified count.** Is it `8` (Pitch/WP/Roadmap/Ledger header) or
   `11` (Ledger v4.5-update text)? All cascading page sync depends on this.
2. **Canonical test total.** `135` (header), `127` (v4.5-update), or `131`
   (sum-of-categories)? Pick one and adjust the other two.
3. **White Paper architecture.** Container `efc_white_paper_part_1_to_4/` or
   four split directories per AGENTS invariant?
4. **Missing DOIs.** Five papers exist on ORCID without repo packages
   (`28098350`, `28102772`, `31970898`, `31970904`, `31970907`). Register or
   archive each?
5. **`efc_master/`.** Assign DOI or archive?
6. **Four new public pages.** Document `EFC_Evaluation_Ledger.html`,
   `EFC_Likelihood_Ledger.html`, `EFC_Master_v1.1.html`,
   `EFC_Model_Comparison.html` in README/AGENTS/llms.txt, or remove?
7. **Single source of truth.** Designate Ledger as master and auto-derive
   rootfiles, or keep manual sync?

---

## 6. Roadmap (effort × impact, post-decision)

### Week 19 (acute, after decisions 1–6 above)
- Sync Pitch / WP / Roadmap / Ledger header to chosen canonical falsified count
- Resolve `efc_master/` DOI question
- Decide White Paper architecture and execute
- Manual metadata fix on the 7 papers warned by `efc_ledger_impact_sync`
- Process 5 newest validation candidates

### Week 20
- Workflow `efc-derive-rootfiles.yml` (auto-sync README badge to Ledger)
- Workflow `efc-public-edit-guard.yml` (8-systems guard)
- Workflow `efc-page-consistency.yml` (per-page arithmetic + cross-page DOI)
- Sealed-prediction immutability guard (pre-commit + CI)

### Week 21
- Status-string normalising daemon (Cypher trigger + nightly batch)
- Publication → EFCValidation auto-binding daemon (fixes 76 % gap)
- Multi-model audit quorum (GPT-5 + Claude-Opus-4.7 + Gemini)
- LLM router (GPT-5 → gpt-5-mini for trivial; ~85 % cost reduction)

### Week 22
- `EFC_System_Health.html` dashboard (auto-generated hourly)
- Cache layer for paper metadata
- Cost meter on daemons
- Mattermost real-time failure logging

---

## 7. Per-session checklist

```text
[ ] efc_orcid_sync.py output → catch new DOIs
[ ] find docs/papers/efc -maxdepth 2 -name 'index.json' | wc -l
[ ] figshare/doi-map.json size > 19 bytes
[ ] grep -E "v[0-9]+\.[0-9]+" docs/public/EFC_Validation_Ledger.html | head
[ ] git status / gh pr list
[ ] Symbiose: get_research_status (health ≥ 60/100)
[ ] Symbiose: gnn_query(mode='health') — has_collapse_alarm?
[ ] Symbiose: list_validation_candidates — count
[ ] Mattermost #system-health: 24h errors
[ ] Surface drift, do not write without consent
```

---

## 8. Per-page checklist (for each public-page edit)

```text
[ ] Trigger eight_systems_guard
[ ] S1 ORCID: every DOI is Morten's
[ ] S2 Figshare: every DOI returns 200
[ ] S3 Repo: every DOI has a package directory
[ ] G1 Neo4j: every DOI has a node
[ ] G2 Qdrant: every DOI has chunks
[ ] G4 Atlas: framework claims have phenomenon binding
[ ] S4 Cross-page: DOI consistent across all 13 pages
[ ] Internal: arithmetic sums = totals
[ ] Language: no "confirms", "proves", "validates"
[ ] Pre-registration: PRIOR DOI cited
```

---

## 9. Index

### S4 public pages (verified 13)
`EFC_Atlas.html`, `EFC_Changelog.html`, `EFC_Elevator_Pitch.html`,
`EFC_Evaluation_Ledger.html`, `EFC_External_Research_Ledger.html`,
`EFC_Gap_Analysis.html`, `EFC_Likelihood_Ledger.html`, `EFC_Master_v1.1.html`,
`EFC_Model_Comparison.html`, `EFC_Predictions.html`,
`EFC_Stage-IV_Data_Roadmap.html`, `EFC_Validation_Ledger.html`,
`EFC_White_Paper_Series.html`.

### Key DOIs (verified on ORCID)
| DOI | Title | Role |
|---|---|---|
| `30656828` | AUTH Layer | Primary framework anchor |
| `31943361` | ΛCDM as a Special Case | Consolidation reference |
| `31964847` | Kill-Test v6 | "Non-rejectable" backbone |
| `31333414` | Background No-Go | Structural exclusion |
| `31986762` | Kill-Test v6 SPARC 175 | Refutes cherry-picking |
| `31990053` | Euclid DR1 Pre-Registration | Sealed for Oct 2026 |
| `32037990` | Perturbation Sector v4.0 | Re-orders kill-criteria |
| `32101111` | Bar-Instability falsified | First formal EFC falsification |
| `32113399` | Three-Window H0 | `H0_tension` upgraded |

### Cross-validation commands
```bash
# S3 repo count
find docs/papers/efc -maxdepth 2 -name 'index.json' | wc -l

# S1 ORCID (cached)
python3 -c "import json; d=json.load(open('.claude/orcid_sync_report.json')); print(d['orcid_works_count'])"

# G1 Neo4j status drift
# (via Symbiose neo4j_execute)
MATCH (v:EFCValidation) RETURN v.status, count(*) ORDER BY count(*) DESC

# G3 GNN health
# (via Symbiose gnn_query mode='health')

# G4 Atlas summary
# (via Symbiose framework_atlas_query mode='summary')
```

---

*Generated as agent for the EFC research programme. Numbers above are
measurements. Decisions in §5 await maintainer judgement; nothing has been
written to public pages from this audit.*
