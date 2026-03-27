#!/usr/bin/env python3
"""
Demo: EFC Relativistic Action — Perturbation Theory and mu, Sigma, eta Extraction
Runs the full perturbation framework with illustrative parameters.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.efc_relativistic import run_perturbation_demo

if __name__ == "__main__":
    run_perturbation_demo()
