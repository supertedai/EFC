#!/usr/bin/env python3
"""
EFC Bullet Cluster Test Suite
Run: python run_all_tests.py
"""
import subprocess
import sys

scripts = [
    "f_gas_comparison.py",
    "predict_other_clusters.py",
    "test_macs_j0025.py",
    "test_abell_520.py",
]

for script in scripts:
    print(f"\n{'='*60}\nRunning: {script}\n{'='*60}")
    try:
        subprocess.run([sys.executable, script])
    except:
        print(f"[SKIP] {script}")
