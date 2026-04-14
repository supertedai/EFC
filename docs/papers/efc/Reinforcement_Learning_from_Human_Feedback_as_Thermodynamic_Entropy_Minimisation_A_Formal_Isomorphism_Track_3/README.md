# Reinforcement Learning from Human Feedback as Thermodynamic Entropy Minimisation: A Formal Isomorphism and Testable Predictions

## AI-Friendly Package

- **DOI:** [10.6084/m9.figshare.31940535](https://doi.org/10.6084/m9.figshare.31940535)
- **Version:** v1.0
- **Author:** Morten Magnusson (ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095))
- **Date:** 2026-03-31
- **License:** CC-BY-4.0

---

## Overview

The paper shows that the RLHF objective with a KL penalty is algebraically identical to minimizing Helmholtz free energy in statistical mechanics, mapping reward to negative energy, policy to a Boltzmann distribution, and the KL coefficient to temperature. From this formal isomorphism it derives three falsifiable predictions about optimal temperature scaling with task entropy, grokking as a first‑order phase transition, and a universal alignment–capability bound, offering testable thermodynamic design principles for RLHF.

## Key Result

RLHF with a KL penalty is exactly isomorphic to thermodynamic free-energy minimization, yielding Boltzmann-optimal policies and three falsifiable predictions about temperature scaling, grokking dynamics, and an alignment–capability bound.

## Sealed Predictions

| ID | Prediction | Falsifiable by |
|---|---|---|
| P1 | Optimal KL temperature scales with task entropy: \beta_{\mathrm{KL}}^* \propto H_{\mathrm{task}}^{-1/2}. | Train comparable models across task families with systematically varied entropy; if the optimum \beta_{KL} shows no dependence on H_task (or opposite scaling), the prediction is falsified. |
| P2 | Grokking is a first-order-like transition with a latent period that scales as \Delta t_{\mathrm{grok}} \propto (H_{\mathrm{mem}} - H_{\mathrm{gen}})/T_{\mathrm{eff}}. | Construct controlled datasets (e.g., modular arithmetic with varying modulus) and measure stall periods; a correlation r < 0.3 between predicted and observed latencies falsifies the claim. |
| P3 | A universal alignment–capability bound holds: A\cdot C \le 1 - \exp(-(F_0 - F^*)/T), setting a maximum attainable product across \beta_{KL} sweeps. | Across families of models varying \beta_{KL}, if empirical A\cdot C reliably exceeds the bound (beyond uncertainty) or grows monotonically without saturating below the bound, the prediction is falsified. |
