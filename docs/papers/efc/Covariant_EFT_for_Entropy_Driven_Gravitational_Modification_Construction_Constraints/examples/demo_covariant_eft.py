#!/usr/bin/env python3
"""
Demo: Covariant EFT for Entropy-Driven Gravitational Modification
Runs structural results, solar-system test, and 17-iteration programme summary.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.covariant_eft import run_eft_demo

if __name__ == "__main__":
    run_eft_demo()
