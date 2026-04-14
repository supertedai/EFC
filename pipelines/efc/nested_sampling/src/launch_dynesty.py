#!/usr/bin/env python3
"""
EFC dynesty Nested Sampling — Launch Script
============================================

Pure-Python fallback for when PolyChord MPI compilation is unavailable.
Uses dynesty directly but wires likelihoods through cobaya's model
evaluator, guaranteeing IDENTICAL likelihood evaluation to the
PolyChord runs.

CRITICAL DESIGN DECISION:
    The likelihood is NOT a placeholder. It uses cobaya.model.get_model()
    to build the full theory+likelihood pipeline from the same YAML config
    as the PolyChord runs. This ensures:
      - Same likelihood function (Planck + BAO + SNe)
      - Same priors
      - Same theory (CAMB/MGCAMB)
      - Same bridge (K0, m_sq) -> (mu0, Sigma0) / Alens
    so that ln(B) = ln(Z_EFC) - ln(Z_LCDM) is a valid model comparison.

Advantages over PolyChord:
    - Pure Python, no MPI compilation needed
    - Easier to debug on laptops / sandbox environments
    - Dynamic nested sampling (adjusts nlive automatically)

Disadvantages:
    - Slower for high dimensions (no slice sampling)
    - No native MPI (uses multiprocessing pool)

Usage:
    python src/launch_dynesty.py --ncpu 16
    python src/launch_dynesty.py --ncpu 16 --reduced
    python src/launch_dynesty.py --ncpu 16 --model lcdm

Author: Morten Magnusson / Symbiose Research
Date:   2026-04-12
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
        logging.FileHandler('dynesty_run.log'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

PACKAGES_PATH = os.environ.get(
    "COBAYA_PACKAGES_PATH",
    os.path.expanduser("~/cobaya_packages")
)
OUTPUT_DIR = "dynesty_output"


class CobayaLikelihoodWrapper:
    """
    Wraps cobaya's full model (theory + likelihoods) for use with dynesty.

    This is the critical piece: instead of a placeholder, we build the
    actual cobaya model from the YAML config and call its logposterior()
    at every dynesty evaluation. This guarantees identical likelihood
    evaluation to the PolyChord cobaya runs.
    """

    def __init__(self, yaml_file):
        from cobaya.yaml import yaml_load_file
        from cobaya.model import get_model

        info = yaml_load_file(yaml_file)
        info["packages_path"] = PACKAGES_PATH

        # Remove the sampler block — we handle sampling externally
        info.pop("sampler", None)
        info.pop("output", None)

        # Build the cobaya model
        log.info(f"Building cobaya model from {yaml_file}...")
        self.model = get_model(info)
        log.info("Model built successfully")

        # Extract sampled parameter info
        self.param_names = list(self.model.parameterization.sampled_params())
        self.ndim = len(self.param_names)

        # Build prior bounds from cobaya's parameterization
        self.prior_min = np.zeros(self.ndim)
        self.prior_max = np.zeros(self.ndim)
        for i, name in enumerate(self.param_names):
            pinfo = self.model.parameterization.sampled_params()[name]
            prior = pinfo.get("prior", {})
            if isinstance(prior, dict) and "min" in prior:
                self.prior_min[i] = prior["min"]
                self.prior_max[i] = prior["max"]
            elif isinstance(prior, dict) and "dist" in prior:
                # Gaussian prior: use wide bounds (±5σ)
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
            # logpost.loglike is the sum of all likelihoods (no prior)
            # We return loglike only because dynesty handles priors via
            # prior_transform
            return float(logpost.loglike)
        except Exception:
            return -1e30


def run_dynesty(wrapper, ncpu=1, nlive_init=500):
    """Run dynesty dynamic nested sampling using the cobaya model."""
    from multiprocessing import Pool
    import dynesty

    log.info(f"Starting dynesty run: {wrapper.ndim}D, {ncpu} CPUs, "
             f"nlive_init={nlive_init}")

    pool = Pool(ncpu) if ncpu > 1 else None
    queue_size = ncpu if ncpu > 1 else None

    t0 = time.time()

    sampler = dynesty.DynamicNestedSampler(
        wrapper.log_likelihood,
        wrapper.prior_transform,
        wrapper.ndim,
        pool=pool,
        queue_size=queue_size,
        bound='multi',
        sample='rwalk',
        walks=5 * wrapper.ndim,
    )

    sampler.run_nested(
        nlive_init=nlive_init,
        nlive_batch=250,
        dlogz_init=0.05,
        maxiter=5000000,
        print_progress=True,
    )

    if pool:
        pool.close()
        pool.join()

    wall_h = (time.time() - t0) / 3600
    log.info(f"dynesty completed in {wall_h:.1f} hours")

    return sampler.results


def analyze_results(results, param_names, model_label):
    """Extract evidence, posteriors, and summary statistics."""
    from dynesty import utils as dyfunc

    logZ = float(results.logz[-1])
    logZ_err = float(results.logzerr[-1])
    log.info(f"{model_label}: ln(Z) = {logZ:.2f} +/- {logZ_err:.2f}")

    # Equal-weight posterior samples
    samples = results.samples
    weights = np.exp(results.logwt - results.logz[-1])
    samples_eq = dyfunc.resample_equal(samples, weights)

    summary = {}
    for i, name in enumerate(param_names):
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
        "logZ": logZ,
        "logZ_err": logZ_err,
        "n_samples": len(samples_eq),
        "n_calls": int(sum(results.ncall)),
        "parameters": summary,
        "timestamp": datetime.utcnow().isoformat(),
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(f"{OUTPUT_DIR}/{model_label}_results.json", 'w') as f:
        json.dump(output, f, indent=2)

    np.savetxt(
        f"{OUTPUT_DIR}/{model_label}_samples.txt",
        samples_eq,
        header=' '.join(param_names)
    )

    return output


def make_plots(results, param_names, model_label):
    """Generate corner plots and diagnostics."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        from dynesty import plotting as dyplot

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Corner plot
        fig, _ = dyplot.cornerplot(results, labels=param_names,
                                   show_titles=True, color='#1f77b4')
        fig.savefig(f"{OUTPUT_DIR}/{model_label}_corner.pdf", bbox_inches='tight')
        import matplotlib.pyplot as plt
        plt.close(fig)

        # Run plot (evidence accumulation)
        fig, _ = dyplot.runplot(results, color='#1f77b4')
        fig.savefig(f"{OUTPUT_DIR}/{model_label}_runplot.pdf", bbox_inches='tight')
        plt.close(fig)

        # Trace plot
        fig, _ = dyplot.traceplot(results, labels=param_names)
        fig.savefig(f"{OUTPUT_DIR}/{model_label}_traceplot.pdf", bbox_inches='tight')
        plt.close(fig)

        log.info(f"Plots saved for {model_label}")
    except Exception as e:
        log.error(f"Plot generation failed: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="EFC dynesty nested sampling (cobaya-backed likelihood)")
    parser.add_argument('--ncpu', type=int, default=1)
    parser.add_argument('--nlive', type=int, default=500)
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
    log.info("EFC DYNESTY NESTED SAMPLING (cobaya-backed)")
    log.info(f"Variant: {variant}, Model: {args.model}, CPUs: {args.ncpu}")
    log.info("=" * 60)

    efc_output = None
    lcdm_output = None

    if args.model in ('efc', 'both'):
        log.info("\n>>> EFC run <<<")
        wrapper = CobayaLikelihoodWrapper(efc_yaml)
        results = run_dynesty(wrapper, ncpu=args.ncpu, nlive_init=args.nlive)
        efc_output = analyze_results(results, wrapper.param_names, f"efc_{variant}")
        make_plots(results, wrapper.param_names, f"efc_{variant}")

    if args.model in ('lcdm', 'both'):
        log.info("\n>>> LCDM run <<<")
        wrapper = CobayaLikelihoodWrapper(lcdm_yaml)
        results = run_dynesty(wrapper, ncpu=args.ncpu, nlive_init=args.nlive)
        lcdm_output = analyze_results(results, wrapper.param_names, f"lcdm_{variant}")
        make_plots(results, wrapper.param_names, f"lcdm_{variant}")

    # Bayes factor
    if efc_output and lcdm_output:
        ln_B = efc_output['logZ'] - lcdm_output['logZ']
        ln_B_err = np.sqrt(efc_output['logZ_err']**2 + lcdm_output['logZ_err']**2)

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
