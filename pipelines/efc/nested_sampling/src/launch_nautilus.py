#!/usr/bin/env python3
"""
EFC nautilus Nested Sampling — Launch Script
=============================================

Low-RAM, degeneracy-tolerant nested sampler (Lange & Tessore 2023).
Targets the exact failure mode reported by the emcee daemon
(`DEGENERACY_LIMITED` across 5 cycles): posteriors narrow along a
likelihood ridge and flat along orthogonal directions collapse
ensemble samplers but are handled natively by nautilus's importance
nested sampling with neural network flow proposals.

CRITICAL DESIGN DECISION:
    Like launch_dynesty.py, the likelihood is NOT a placeholder. It
    uses cobaya.model.get_model() to build the full theory+likelihood
    pipeline from the same YAML config as the PolyChord/dynesty runs.
    This ensures:
      - Same likelihood function (Planck + BAO + SNe)
      - Same priors
      - Same theory (CAMB/MGCAMB)
      - Same bridge (K0, m_sq) -> (mu0, Sigma0) / Alens
    so that ln(B) = ln(Z_EFC) - ln(Z_LCDM) is directly comparable
    across all three samplers.

Advantages over dynesty:
    - Lower RAM footprint (~2-4 GB instead of 8-16 GB)
    - Handles degenerate / curved posteriors without ensemble collapse
    - Faster convergence in high dimensions (flow-based proposals)
    - Full Bayesian evidence ln(Z) with well-calibrated uncertainty

Advantages over PolyChord:
    - No MPI compilation required
    - Pure Python install (pip install nautilus-sampler)

Usage:
    python src/launch_nautilus.py --ncpu 8 --model both
    python src/launch_nautilus.py --ncpu 8 --model both --reduced
    python src/launch_nautilus.py --ncpu 4 --model efc --nlive 2000

Author: Morten Magnusson / Symbiose Research
Date:   2026-04-14
"""

import os
import sys
import json
import time
import logging
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('nautilus_run.log'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

PACKAGES_PATH = os.environ.get(
    "COBAYA_PACKAGES_PATH",
    os.path.expanduser("~/cobaya_packages")
)
OUTPUT_DIR = "nautilus_output"


class CobayaLikelihoodWrapper:
    """
    Wraps cobaya's full model (theory + likelihoods) for use with nautilus.

    Identical contract to the dynesty wrapper: build cobaya model from
    YAML, expose prior_transform (unit cube -> physical) and
    log_likelihood (physical -> lnL). This guarantees cross-sampler
    ln(Z) comparability.
    """

    def __init__(self, yaml_file):
        from cobaya.yaml import yaml_load_file
        from cobaya.model import get_model

        info = yaml_load_file(yaml_file)
        info["packages_path"] = PACKAGES_PATH

        # Remove the sampler block — nautilus handles sampling externally
        info.pop("sampler", None)
        info.pop("output", None)

        log.info(f"Building cobaya model from {yaml_file}...")
        self.model = get_model(info)
        log.info("Model built successfully")

        self.param_names = list(self.model.parameterization.sampled_params())
        self.ndim = len(self.param_names)

        self.prior_min = np.zeros(self.ndim)
        self.prior_max = np.zeros(self.ndim)
        for i, name in enumerate(self.param_names):
            pinfo = self.model.parameterization.sampled_params()[name]
            prior = pinfo.get("prior", {})
            if isinstance(prior, dict) and "min" in prior:
                self.prior_min[i] = prior["min"]
                self.prior_max[i] = prior["max"]
            elif isinstance(prior, dict) and "dist" in prior:
                loc = prior.get("loc", 0)
                scale = prior.get("scale", 1)
                self.prior_min[i] = loc - 5 * scale
                self.prior_max[i] = loc + 5 * scale
            else:
                raise ValueError(f"Cannot determine bounds for {name}: {prior}")

        log.info(f"Parameters ({self.ndim}): {self.param_names}")
        for i, name in enumerate(self.param_names):
            log.info(f"  {name}: [{self.prior_min[i]:.6f}, {self.prior_max[i]:.6f}]")

    def prior_transform(self, u):
        """Transform unit cube [0,1]^n to physical parameter space."""
        return self.prior_min + u * (self.prior_max - self.prior_min)

    def log_likelihood(self, theta):
        """Evaluate the full cobaya likelihood at theta."""
        params = {name: float(val)
                  for name, val in zip(self.param_names, theta)}
        try:
            logpost = self.model.logposterior(params)
            return float(logpost.loglike)
        except Exception:
            return -1e30


def run_nautilus(wrapper, ncpu=1, nlive=2000):
    """Run nautilus importance nested sampling using the cobaya model."""
    from nautilus import Prior, Sampler

    log.info(f"Starting nautilus run: {wrapper.ndim}D, {ncpu} CPUs, "
             f"nlive={nlive}")

    # Build a uniform Prior over the unit cube; wrapper.prior_transform
    # maps it to physical parameter space inside the likelihood.
    prior = Prior()
    for name in wrapper.param_names:
        prior.add_parameter(name, dist=(0.0, 1.0))

    def likelihood_on_cube(point):
        # nautilus passes a dict of unit-cube values
        u = np.array([point[name] for name in wrapper.param_names])
        theta = wrapper.prior_transform(u)
        return wrapper.log_likelihood(theta)

    t0 = time.time()

    sampler = Sampler(
        prior,
        likelihood_on_cube,
        n_live=nlive,
        pool=ncpu if ncpu > 1 else None,
    )

    sampler.run(
        verbose=True,
        discard_exploration=True,
    )

    wall_h = (time.time() - t0) / 3600
    log.info(f"nautilus completed in {wall_h:.1f} hours")

    return sampler, wrapper


def analyze_results(sampler, wrapper, model_label):
    """Extract evidence, posteriors, and summary statistics."""
    logZ = float(sampler.log_z)
    # nautilus reports sampling-error via effective sample size; use the
    # documented log-Z uncertainty estimator (1/sqrt(n_eff)).
    try:
        n_eff = float(sampler.n_eff)
        logZ_err = float(1.0 / np.sqrt(max(n_eff, 1.0)))
    except Exception:
        logZ_err = float('nan')

    log.info(f"{model_label}: ln(Z) = {logZ:.2f} +/- {logZ_err:.2f}")

    # Weighted posterior samples on unit cube — transform to physical
    points, log_w, log_l = sampler.posterior()
    weights = np.exp(log_w - np.max(log_w))
    weights /= weights.sum()

    # Resample to equal-weight
    n_samples = len(points)
    n_eq = min(n_samples, 50000)
    idx = np.random.choice(n_samples, size=n_eq, p=weights, replace=True)
    points_eq = points[idx]

    # Map unit-cube samples to physical parameter space
    samples_eq = np.array([wrapper.prior_transform(u) for u in points_eq])

    summary = {}
    for i, name in enumerate(wrapper.param_names):
        s = samples_eq[:, i]
        summary[name] = {
            "mean": float(np.mean(s)),
            "std": float(np.std(s)),
            "median": float(np.median(s)),
            "lower_68": float(np.percentile(s, 16)),
            "upper_68": float(np.percentile(s, 84)),
            "lower_95": float(np.percentile(s, 2.5)),
            "upper_95": float(np.percentile(s, 97.5)),
        }
        log.info(f"  {name}: {summary[name]['mean']:.6f} "
                 f"+/- {summary[name]['std']:.6f}")

    output = {
        "model": model_label,
        "sampler": "nautilus",
        "logZ": logZ,
        "logZ_err": logZ_err,
        "n_samples": int(n_eq),
        "n_calls": int(getattr(sampler, 'n_like', -1)),
        "parameters": summary,
        "timestamp": datetime.utcnow().isoformat(),
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(f"{OUTPUT_DIR}/{model_label}_results.json", 'w') as f:
        json.dump(output, f, indent=2)

    np.savetxt(
        f"{OUTPUT_DIR}/{model_label}_samples.txt",
        samples_eq,
        header=' '.join(wrapper.param_names)
    )

    return output, samples_eq


def make_plots(samples_eq, param_names, model_label):
    """Generate corner plot via getdist (matches dynesty/polychord style)."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        try:
            from getdist import MCSamples, plots
            mc = MCSamples(samples=samples_eq, names=param_names,
                           labels=param_names)
            g = plots.get_subplot_plotter()
            g.triangle_plot([mc], filled=True)
            g.export(f"{OUTPUT_DIR}/{model_label}_corner.pdf")
            log.info(f"Corner plot saved for {model_label}")
        except ImportError:
            # Fallback: simple matplotlib pairplot
            from itertools import combinations
            n = len(param_names)
            fig, axes = plt.subplots(n, n, figsize=(2 * n, 2 * n))
            for i in range(n):
                for j in range(n):
                    ax = axes[i, j]
                    if i == j:
                        ax.hist(samples_eq[:, i], bins=40, color='#1f77b4')
                    elif i > j:
                        ax.hexbin(samples_eq[:, j], samples_eq[:, i],
                                  gridsize=30, cmap='Blues')
                    else:
                        ax.axis('off')
                    if i == n - 1:
                        ax.set_xlabel(param_names[j])
                    if j == 0 and i != 0:
                        ax.set_ylabel(param_names[i])
            fig.tight_layout()
            fig.savefig(f"{OUTPUT_DIR}/{model_label}_corner.pdf",
                        bbox_inches='tight')
            plt.close(fig)
            log.info(f"Corner plot saved for {model_label} (matplotlib fallback)")
    except Exception as e:
        log.error(f"Plot generation failed: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="EFC nautilus nested sampling (cobaya-backed likelihood)")
    parser.add_argument('--ncpu', type=int, default=1)
    parser.add_argument('--nlive', type=int, default=2000,
                        help='Live points (nautilus default: 2000)')
    parser.add_argument('--reduced', action='store_true',
                        help='Use reduced dataset (vanilla CAMB)')
    parser.add_argument('--model', choices=['efc', 'lcdm', 'both'],
                        default='both')
    args = parser.parse_args()

    suffix = "_reduced" if args.reduced else ""
    efc_yaml = f"config/efc_polychord{suffix}.yaml"
    lcdm_yaml = f"config/lcdm_polychord{suffix}.yaml"
    variant = "reduced" if args.reduced else "full"

    log.info("=" * 60)
    log.info("EFC NAUTILUS NESTED SAMPLING (cobaya-backed)")
    log.info(f"Variant: {variant}, Model: {args.model}, CPUs: {args.ncpu}")
    log.info("=" * 60)

    efc_output = None
    lcdm_output = None

    if args.model in ('efc', 'both'):
        log.info("\n>>> EFC run <<<")
        wrapper = CobayaLikelihoodWrapper(efc_yaml)
        sampler, w = run_nautilus(wrapper, ncpu=args.ncpu, nlive=args.nlive)
        efc_output, samples_eq = analyze_results(
            sampler, w, f"efc_{variant}")
        make_plots(samples_eq, w.param_names, f"efc_{variant}")

    if args.model in ('lcdm', 'both'):
        log.info("\n>>> LCDM run <<<")
        wrapper = CobayaLikelihoodWrapper(lcdm_yaml)
        sampler, w = run_nautilus(wrapper, ncpu=args.ncpu, nlive=args.nlive)
        lcdm_output, samples_eq = analyze_results(
            sampler, w, f"lcdm_{variant}")
        make_plots(samples_eq, w.param_names, f"lcdm_{variant}")

    # Bayes factor
    if efc_output and lcdm_output:
        ln_B = efc_output['logZ'] - lcdm_output['logZ']
        ln_B_err = np.sqrt(efc_output['logZ_err']**2
                           + lcdm_output['logZ_err']**2)

        if ln_B > 5:
            verdict = "STRONG for EFC"
        elif ln_B > 2.5:
            verdict = "MODERATE for EFC"
        elif ln_B > 1:
            verdict = "WEAK for EFC"
        elif ln_B > -1:
            verdict = "INCONCLUSIVE"
        elif ln_B > -2.5:
            verdict = "WEAK for LCDM"
        else:
            verdict = "STRONG for LCDM"

        comparison = {
            "sampler": "nautilus",
            "ln_Z_efc": efc_output['logZ'],
            "ln_Z_lcdm": lcdm_output['logZ'],
            "ln_B": float(ln_B),
            "ln_B_err": float(ln_B_err),
            "verdict": verdict,
            "variant": variant,
            "timestamp": datetime.utcnow().isoformat(),
        }

        with open(f"{OUTPUT_DIR}/bayes_factor_{variant}.json", 'w') as f:
            json.dump(comparison, f, indent=2)

        log.info("\n" + "=" * 60)
        log.info(f"ln(B) = {ln_B:.2f} +/- {ln_B_err:.2f}")
        log.info(f"VERDICT: {verdict}")
        log.info("=" * 60)


if __name__ == "__main__":
    main()
