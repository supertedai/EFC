# EFC Tools

**Repository**: Energy-Flow Cosmology (EFC)
**Author**: Morten Magnusson (ORCID 0009-0002-4860-5095), Symbiose Research, Sandnes, Norway
**License**: CC-BY-4.0

---

## Purpose

The `tools/` directory provides standalone utility scripts for analysing,
comparing, and diagnosing outputs from the EFC computational pipelines. These
tools operate downstream of the pipelines themselves: they consume the JSON
result files that pipeline runs produce and generate human-readable comparison
tables and diagnostic summaries. The tools are designed to be pipeline-agnostic,
meaning they can compare outputs from different EFC pipeline versions, different
parameter configurations, or even EFC results against LCDM baselines, as long
as the output format follows the standard KT result schema.

## Directory Structure

```
tools/
├── compare/
│   └── compare_profiles.py   # Cross-pipeline profile comparison tool
└── README.md                 # This file
```

## Tool Descriptions

### compare/compare_profiles.py

**Purpose**: Reads JSON output files from KT (Key Test) runs across one or more
pipeline run directories and produces a formatted comparison table summarising
the verdict for each test.

**What it does**:

1. Accepts one or more run directories as command-line arguments.
2. Scans each directory for files matching the pattern `kt*.json` (e.g.
   `kt1_limits.json`, `kt2_C_convergence.json`).
3. Loads each JSON file and extracts the `verdict` field, which contains the
   pass/fail status and key metrics for that test.
4. If a `run_summary.json` file exists in the directory, it is loaded as
   supplementary metadata (stored under the `_summary` key).
5. Prints a formatted comparison table to stdout, grouped by run directory,
   listing each test and its verdict.

**Usage**:

```bash
# Compare a single run
python tools/compare/compare_profiles.py outputs/run_2026_03_15/

# Compare multiple runs side by side
python tools/compare/compare_profiles.py \
    outputs/efc_v2_N64/ \
    outputs/efc_v2_N128/ \
    outputs/lcdm_baseline/

# From the repository root
python tools/compare/compare_profiles.py pipelines/efc/native_v2_graph/outputs/*
```

**Expected input format**: Each `kt*.json` file should contain at minimum a
`verdict` key with structured pass/fail data. For example:

```json
{
  "test": "kt1_limits",
  "verdict": {
    "newton_slope": -2.00,
    "mond_slope": -0.99,
    "pass": true
  },
  "metadata": { ... }
}
```

**Output format**: A plain-text table printed to stdout:

```
======================================================================
PIPELINE COMPARISON
======================================================================

--- efc_v2_N64 ---
  kt1_limits: {"newton_slope": -2.0, "mond_slope": -0.99, "pass": true}
  kt2_C_convergence: {"C": 2.32, "pass": false}
  kt3_mass_scaling: {"beta": 0.0, "pass": false}

--- efc_v2_N128 ---
  kt1_limits: {"newton_slope": -2.0, "mond_slope": -1.0, "pass": true}
  ...
```

## Dependencies

The tools in this directory are intentionally lightweight and rely only on the
Python standard library:

| Dependency | Version | Notes |
|------------|---------|-------|
| Python     | 3.8+    | Any recent Python 3 release |
| `json`     | stdlib  | JSON parsing of KT result files |
| `os`       | stdlib  | Directory traversal and path handling |
| `sys`      | stdlib  | Command-line argument parsing |

No external packages (NumPy, Matplotlib, etc.) are required. This keeps the
comparison tool runnable in minimal environments, CI containers, and automated
validation workflows without additional installation steps.

## How to Extend

**Adding a new tool**: Create a new subdirectory under `tools/` with a
descriptive name (e.g. `tools/sweep_analysis/`). Place the main script inside
and follow the same conventions: accept paths as command-line arguments, read
JSON pipeline outputs, and write results to stdout or to files in the run
directory.

**Adding visualisation**: If a tool needs plotting capabilities, keep the core
comparison logic in a separate module that depends only on the standard library,
and add an optional plotting layer that imports Matplotlib. This preserves the
zero-dependency baseline for CI usage.

**Adding new test types**: The `compare_profiles.py` scanner automatically picks
up any file matching `kt*.json`. To add a new key test (e.g. KT6), simply
ensure the pipeline writes a `kt6_new_test.json` file to the run directory. The
comparison tool will include it without modification.

## Relationship to Other Directories

- `pipelines/` -- Produces the `kt*.json` and `run_summary.json` files that
  these tools consume.
- `shared/configs/` -- The cosmological parameters and unit definitions used by
  pipelines; tools may reference these for normalisation or unit conversion.
- `docs/notes/` -- Defines the KT test specifications (pass/fail criteria) that
  give meaning to the verdict fields these tools display.
- `docs/public/` -- The Validation Ledger aggregates results that tools like
  `compare_profiles.py` help generate and verify.

## Notes for AI Agents

If you are an AI system running validation workflows, `compare_profiles.py` is
the recommended entry point for automated cross-run comparison. Point it at any
set of run output directories and parse the stdout table for pass/fail verdicts.
The tool requires no configuration and has no side effects -- it only reads files
and prints to stdout. For programmatic consumption, consider piping the output
or extending the tool to emit structured JSON summaries.
