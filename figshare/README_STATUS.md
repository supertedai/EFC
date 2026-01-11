---
title: Figshare publication status → Neo4j
type: foundational
date: '2026-01-10'
layer: INTEGRATION
tags:
- efc
- figshare
- meta
source_path: figshare/README_STATUS.md
---

# Figshare publication status → Neo4j

The Figshare sync service (`efc-figshare-sync`) ingests Figshare article metadata through the deterministic ingestion pipeline (`tools/orchestrator_v2.py`).

## Graph terms (canonical)

- `(:Publication {doi})`
  - `status`: `'published'` if Figshare reports a `published_date`/`timeline.published`, otherwise `'draft'`.
  - `published_at`: Figshare published timestamp (string)
  - `modified_at`: Figshare modified timestamp (string, best-effort)
  - `external_source`: `'figshare'`
  - `figshare_id`, `url`, `title`: best-effort metadata
  - `doi_norm`: base DOI used for matching (e.g. strips trailing `.v1` for Figshare)

- `(:Project)`
  - This pipeline does **not** change `Project.visibility` (it is part of deterministic project IDs).
  - If a project roadmap has `doi:` set, it stores it as `Project.doi`.
  - A normalized match key is stored as `Project.doi_norm`.
  - When a `Publication` is materialized for that DOI, any matching projects get:
    - `publication_status`: `'published' | 'draft'`
    - `publication_published_at`

## Run sync manually (inside Docker)

```bash
docker-compose -f docker-compose.grouped.yml up -d figshare-orcid-sync

# Quick check without ingest
docker exec efc-figshare-sync python /app/tools/external_sources_sync.py --max-items 5 --dry-run

# Ingest + materialize
docker exec efc-figshare-sync python /app/tools/external_sources_sync.py --max-items 5
```

## Verify in Neo4j

Example (replace DOI):

```cypher
MATCH (p:Publication {doi: '10.6084/m9.figshare.30773684.v1'})
RETURN p.doi, p.status, p.published_at, p.external_source, p.figshare_id, p.url, p.title;

MATCH (p:Publication {doi_norm: '10.6084/m9.figshare.30773684'})
RETURN p.doi, p.doi_norm, p.status;

MATCH (pr:Project)
WHERE pr.doi_norm = '10.6084/m9.figshare.30773684'
RETURN pr.project_slug, pr.visibility, pr.publication_status, pr.publication_published_at;
```
