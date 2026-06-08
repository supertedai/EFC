# As-Found Inventory — supertedai/EFC — 2026-05-19

## Snapshot

- **Branch**: `main` (HEAD `56f64592`)
- **AGENTS.md version**: 3.6 (2026-04-12)
- **Validation Ledger**: v3.18 public / v4.6 internal
- **AI-friendly papers**: 165 (100% coverage of active set; 2 superseded in `_archived/`)
- **Stage**: `non_rejectable_model` (global verdict OPEN)
- **Repo bridge to Symbiose**: `SYMBIOSE_WEBHOOK_URL` secret POST on every drift-fix

## Master orchestrators (canonical EFC "daemons"): **4**

| ID | Path | Trigger | Notes |
|---|---|---|---|
| `cosmos.efc.maintain`        | `scripts/maintenance/efc_maintain.py`        | SessionStart hook + CI workflows | Top-level orchestrator |
| `cosmos.efc.full-sync`       | `scripts/maintenance/efc_full_sync.py`       | invoked from maintain | Fixpoint-convergence over `sync_engine/` |
| `cosmos.efc.qdrant-ingest`   | `scripts/maintenance/efc_qdrant_ingest.py`   | manual `--apply` only       | **Scaffolding** — upsert gated until embedder wired |
| `cosmos.efc.system-health`   | `scripts/maintenance/build_system_health.py` | cron hourly (efc-system-health.yml) | Builds `EFC_System_Health.html` |

## Maintenance script library: **~44 Python files**

Located in `scripts/maintenance/` + `scripts/maintenance/phase2/` (newer reimplementations) + `scripts/maintenance/sync_engine/` package.

Non-orchestrator highlights (≤24 grouped by function):

- **DOI/Metadata sync**: efc_sync_dois, efc_auto_metadata, efc_orcid_sync, efc_regen_index, efc_paper_type_classifier
- **Ledger/Drift**: efc_drift_detector, efc_rootfile_consistency, efc_page_consistency, efc_ledger_autofill, efc_ledger_impact_sync, efc_evidence_mirror, efc_navbar_sync, efc_unprocessed, efc_process_paper, efc_atlas_export
- **AI/LLM**: efc_ai_brain (70KB), efc_ai_audit, efc_ai_monitor, efc_council_gate, efc_precommit_gate, ledger_schema
- **Verification**: efc_verify, efc_cross_validate, efc_weekly_scan, efc_dataset_scanner, efc_symbiose_snapshot
- **Figshare/sealing**: efc_figshare_check, efc_seal_manifest, generate_doi_map, efc_auto_changelog
- **Changelogs/build**: build_system_health, build_atlas

## MCP server: **1**

- `integrations/mcp/efc_mcp_server.py` (21 KB, stdio MCP).
- **Capability ID**: `shared.efc.mcp`
- **Tools**: 15 across EFC repo + 2 WordPress sites (energyflow-cosmology.com, magnusson.as) + figshare.com + framework atlas.
- **Spec**: `integrations/mcp/server.json`
- **Tools list**: wp_list_posts, wp_create_post, wp_update_post, figshare_list_articles, figshare_create_article, figshare_upload_file, figshare_publish, validate_jsonld, update_doi_map, sync_metadata, check_links, atlas_list_frameworks, atlas_query, atlas_diff, atlas_summary, full_sync
- **Prompts**: publish_paper, update_website, validate_all
- **Resources**: `efc://schema/global`, `efc://doi/map`, `efc://auth/manifest`

## Cosmology pipelines: **6**

| ID | Path | Notes |
|---|---|---|
| `cosmos.pipelines.native-v2-graph`      | `pipelines/efc/native_v2_graph/`      | Graph-based AQUAL solver (KT1–KT5). Kernel: aqual/energy/fields/graph/observables/operators/solver. Configs base.yaml + sweeps.yaml. |
| `cosmos.pipelines.euclid-dr1`           | `pipelines/efc/euclid_dr1/`           | Stage-IV Euclid DR1 pre-registration. efc_mg_functions + efc_hiclass_bridge + euclid_mock_likelihood. cobaya + PolyChord via efc_cobaya.yaml. Sanity checks A–F. |
| `cognitive.pipelines.hcp-bridge-b1`     | `pipelines/efc/hcp_bridge_b1/`        | HCP neural connectome bridge B1* (η = C/(1+λ₂·τ_c)). The cognitive bridge. |
| `cosmos.pipelines.grav-bridge`          | `pipelines/efc/grav_bridge/`          | Gravitational bridge. |
| `cosmos.pipelines.nested-sampling`      | `pipelines/efc/nested_sampling/`      | Full Bayesian evidence (Hull #3). |
| `cosmos.pipelines.weak-lensing-case-b`  | `pipelines/efc/weak_lensing_case_b/`  | Growth-modified lensing constraints (Hull #4). |

Plus `tools/cobaya_bridge/` (MCMC bridge: bridge_theory.py, 6 YAML configs, efc_mu_table.json, install.sh, run.sh).

## GitHub Actions: **13 workflows, 6 with cron**

| Workflow | Trigger | Schedule (UTC) |
|---|---|---|
| efc-system-health.yml      | schedule + push + dispatch | hourly :05 |
| efc-sync.yml               | push to non-main + schedule + dispatch | nightly 05:30 |
| atlas-sync.yml             | push + schedule + dispatch | nightly 05:45 |
| efc-figshare-presence.yml  | schedule + PR + dispatch | weekly Mon 05:00 |
| efc-ai-monitor.yml         | schedule + dispatch | weekly Mon 06:00 |
| efc-ai-audit.yml           | schedule + push (public pages) | Wed 06:30 + Mon 07:00 |
| efc-main-sync.yml          | push to main + dispatch | — |
| efc-verify.yml             | PRs only | — |
| atlas-verify.yml           | PRs + atlas-input push | — |
| efc-page-consistency.yml   | push/PR | — |
| efc-rootfile-consistency.yml | push/PR | — |
| efc-sealed-prediction-guard.yml | PR | — |
| efc-backfill-pdfs.yml      | dispatch only | — |

## Top-level reproduction scripts: **5**

- `reproduce_bao.py` — BAO reproduction
- `reproduce_cmb_sanity.py` — CMB sanity
- `reproduce_efc.py` — Master EFC reproduction
- `reproduce_sparc.py` — SPARC rotation curves
- `efc_integration_test.py` — Top-level integration test

## Domain breakdown

- **cosmos**: ~95% — every script, every workflow, every paper directory under `docs/papers/efc/`
- **cognitive**: 1 dedicated pipeline (`hcp_bridge_b1`) + content under `docs/papers/cognitive/`
- **meta**: 0 dedicated services; content under `docs/papers/meta/` (HomoFluxus, Proxy, Autopoiesis)
- **shared**: 0 — this repo IS the cosmos research surface

## Important: `efc_repo_sync_daemon` is NOT here

The architectural reference's per-30min `efc_repo_sync_daemon` does NOT exist in this repo as a long-running daemon. Its function is split:

1. `efc-sync.yml` + `efc-main-sync.yml` — run maintenance + POST `{event: efc_push, commit, papers}` to `SYMBIOSE_WEBHOOK_URL`
2. `efc_qdrant_ingest.py` — scaffolding only (no upsert)
3. The receiving "per-30min worker" lives in `supertedai/AGI` at `tools/efc_repo_sync_daemon.py`

See `som/registry/daemons.yaml` in AGI for the receiver-side entry: `shared.ingestion.repo-sync`.
