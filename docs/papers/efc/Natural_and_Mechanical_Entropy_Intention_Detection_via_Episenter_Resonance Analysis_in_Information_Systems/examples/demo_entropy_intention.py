#!/usr/bin/env python3
"""
Demo: Natural and Mechanical Entropy Detection Framework
Runs the full episenter-resonance analysis pipeline with synthetic data.
"""

import sys
import os

# Allow running from examples/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.entropy_intention import run_detection_demo

if __name__ == "__main__":
    run_detection_demo()
