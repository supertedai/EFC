"""
EFC Inference Engine
Modular Bayesian inference system for Energy-Flow Cosmology.

Architecture:
  - core/    : Mathematics (parameters, priors, likelihoods, sampler, PPC)
  - engine/  : Physics (EFC computation engines — stubs for Morten to fill)
  - modules/ : Data (standardized observation modules — SPARC, BAO, etc.)
  - meta/    : Epistemic control (L0-L3 weighting, EBE, RBC)
  - reports/ : Output (JSON/Markdown reports, Neo4j publishing)
  - runs/    : CLI runners and configs
"""

__version__ = "0.1.0"
