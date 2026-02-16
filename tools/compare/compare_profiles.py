#!/usr/bin/env python3
"""
Compare output profiles across pipelines.

Reads JSON outputs from KT runs and produces summary tables + delta plots.

Usage:
    python compare_profiles.py <run_dir_1> [run_dir_2] [...]
"""
import sys
import os
import json


def load_run(run_dir):
    """Load all KT results from a run directory."""
    results = {}
    for fname in os.listdir(run_dir):
        if fname.endswith('.json') and fname.startswith('kt'):
            with open(os.path.join(run_dir, fname)) as f:
                results[fname.replace('.json', '')] = json.load(f)
    summary_path = os.path.join(run_dir, 'run_summary.json')
    if os.path.exists(summary_path):
        with open(summary_path) as f:
            results['_summary'] = json.load(f)
    return results


def print_comparison(runs):
    """Print comparison table across runs."""
    print("\n" + "=" * 70)
    print("PIPELINE COMPARISON")
    print("=" * 70)

    for run_name, data in runs.items():
        print(f"\n--- {run_name} ---")
        for test_name, test_data in sorted(data.items()):
            if test_name.startswith('_'):
                continue
            verdict = test_data.get('verdict', {})
            print(f"  {test_name}: {json.dumps(verdict, indent=None)}")


def main():
    if len(sys.argv) < 2:
        print("Usage: compare_profiles.py <run_dir> [run_dir_2] ...")
        sys.exit(1)

    runs = {}
    for path in sys.argv[1:]:
        if os.path.isdir(path):
            name = os.path.basename(path)
            runs[name] = load_run(path)
        else:
            print(f"  Warning: {path} is not a directory")

    print_comparison(runs)


if __name__ == '__main__':
    main()
