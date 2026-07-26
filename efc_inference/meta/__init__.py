"""
EFC Meta-Control Layers.

These are NOT data modules. They are epistemic control layers
that wrap around the inference engine:
  - L0-L3: Prior width scaling based on epistemic confidence
  - EBE: Empirical Boundary Enforcement (post-inference constraint)
  - RBC: Regime Boundary Controller (alpha-based regime switching)
"""
