# SPARC N=175 Extended Dataset

## Status: ✅ INGESTET I NEO4J + QDRANT

This directory contains the complete SPARC (Spitzer Photometry and Accurate Rotation Curves) dataset.

## Contents

- `sparc_catalog.dat` - Galaxy properties (175 galaxies)
- `sparc_rotation_curves.dat` - Rotation curve measurements (3391 points)
- `SPARC_DATASET.md` - Full documentation (INGESTET in Qdrant)
- `galaxies.json` - Parsed galaxy data
- `metadata.json` - Dataset metadata

## Source

**Paper**: Lelli, F., McGaugh, S. S., & Schombert, J. M. (2016)  
**Journal**: Astronomical Journal, 152, 157  
**VizieR**: J/AJ/152/157  
**Downloaded**: 2026-01-10

## Ingestion Status

✅ **Qdrant**: SPARC_DATASET.md ingestet (1 chunk, 5 concepts)  
✅ **Neo4j**: Dataset fact created with full metadata  
✅ **Files**: All raw data files preserved in this directory

## Usage

The data is now queryable through:
1. Symbiose `ask` tool for natural language queries
2. Direct Neo4j queries for graph relationships
3. Qdrant search for semantic similarity

