#!/usr/bin/env python3
"""
Run orchestrator for EFC Native v2 Graph pipeline.

Usage:
    python run_efc_graph.py                    # run all KTs
    python run_efc_graph.py kt1 kt2            # run specific tests
    python run_efc_graph.py --quick             # fast run (smaller grids)
"""
import sys
import os
import json
import time
from datetime import datetime

# Add this directory to path
sys.path.insert(0, os.path.dirname(__file__))


def run_suite(tests=None, quick=False):
    """Run the KT test suite."""
    from tests.kt1_limits import run_kt1
    from tests.kt2_C_convergence import run_kt2
    from tests.kt3_mass_scaling import run_kt3
    from tests.kt4_superposition import run_kt4
    from tests.kt5_EFE import run_kt5

    # Create run directory
    run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join(os.path.dirname(__file__),
                              'outputs', 'runs', run_id)
    os.makedirs(output_dir, exist_ok=True)

    all_tests = {
        'kt1': lambda: run_kt1(
            N=21 if quick else 31,
            a0_values=[2.0, 0.1, 0.001] if quick else None,
            output_dir=output_dir),
        'kt2': lambda: run_kt2(
            N_values=[21, 31] if quick else None,
            output_dir=output_dir),
        'kt3': lambda: run_kt3(
            M_values=[10, 50, 200] if quick else None,
            N=21 if quick else 31,
            output_dir=output_dir),
        'kt4': lambda: run_kt4(
            N=21 if quick else 31,
            output_dir=output_dir),
        'kt5': lambda: run_kt5(
            g_ext_ratios=[0.0, 1.0, 5.0] if quick else None,
            N=21 if quick else 31,
            output_dir=output_dir),
    }

    if tests is None:
        tests = list(all_tests.keys())

    print("=" * 60)
    print(f"EFC NATIVE v2 GRAPH — KT SUITE")
    print(f"Run ID: {run_id}")
    print(f"Tests: {', '.join(tests)}")
    print(f"Mode: {'quick' if quick else 'full'}")
    print("=" * 60)

    t0 = time.time()
    summary = {}

    for test_name in tests:
        if test_name in all_tests:
            try:
                result = all_tests[test_name]()
                summary[test_name] = result.get('verdict', {})
            except Exception as e:
                print(f"\n  ERROR in {test_name}: {e}")
                summary[test_name] = {'error': str(e)}
        else:
            print(f"\n  Unknown test: {test_name}")

    dt = time.time() - t0

    # Write summary
    run_summary = {
        'run_id': run_id,
        'tests': list(tests),
        'mode': 'quick' if quick else 'full',
        'total_time_s': round(dt, 1),
        'results': summary,
    }

    summary_path = os.path.join(output_dir, 'run_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(run_summary, f, indent=2)

    print("\n" + "=" * 60)
    print(f"SUITE DONE in {dt:.0f}s ({dt / 60:.1f} min)")
    print(f"Output: {output_dir}")
    print("=" * 60)
    print("\nSummary:")
    for test, verdict in summary.items():
        print(f"  {test}: {verdict}")

    return run_summary


if __name__ == '__main__':
    args = sys.argv[1:]
    quick = '--quick' in args
    tests = [a for a in args if not a.startswith('--')]
    if not tests:
        tests = None
    run_suite(tests=tests, quick=quick)
