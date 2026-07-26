"""
CLI Runner: SPARC Rotation Curve Inference

Usage:
    python -m efc_inference.runs.run_sparc --config config.yaml
    python -m efc_inference.runs.run_sparc --galaxy NGC2403 --data path/to/sparc_data.dat
    python -m efc_inference.runs.run_sparc --dry-run  # Quick 100-step test
"""

import argparse
import logging
import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from efc_inference.core.parameters import EFCParameterVector
from efc_inference.core.priors import LogUniformPrior, GaussianPrior, UniformPrior
from efc_inference.core.sampler import EFCSampler, MetaController
from efc_inference.core.ppc import ppc_report
from efc_inference.engine.rotation import EFCRotation
from efc_inference.modules.sparc_module import SPARCModule
from efc_inference.meta.epistemic_levels import EpistemicWeighting, EpistemicLevel
from efc_inference.meta.ebe_boundary import EBEBoundary
from efc_inference.meta.rbc_regime import RBCRegime
from efc_inference.reports.report_generator import ReportGenerator
from efc_inference.reports.neo4j_publisher import Neo4jPublisher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger("efc_inference.sparc")


def build_parameters() -> EFCParameterVector:
    """Build the EFC parameter vector for rotation curve fitting."""
    pv = EFCParameterVector()

    pv.add("entropy_scale", 1e-24,
           bounds=(1e-28, 1e-20),
           prior=LogUniformPrior(1e-28, 1e-20))

    pv.add("length_scale", 8.0,
           bounds=(0.1, 100.0),
           prior=GaussianPrior(8.0, 5.0))

    pv.add("flow_constant", 1.0,
           bounds=(0.01, 100.0),
           prior=LogUniformPrior(0.01, 100.0))

    pv.add("velocity_scale", 200.0,
           bounds=(10.0, 500.0),
           prior=GaussianPrior(200.0, 100.0))

    return pv


def build_meta() -> MetaController:
    """Build meta-control layers."""
    meta = MetaController()

    # L0-L3 epistemic weighting
    ew = EpistemicWeighting(default_level=EpistemicLevel.L1)
    ew.set_level("entropy_scale", EpistemicLevel.L0)  # Speculative
    ew.set_level("length_scale", EpistemicLevel.L2)   # Some evidence
    ew.set_level("flow_constant", EpistemicLevel.L0)  # Speculative
    ew.set_level("velocity_scale", EpistemicLevel.L2)  # SPARC-constrained
    meta.add_layer("epistemic_L0L3", ew.log_penalty)

    # EBE boundary enforcement (stub — returns 0.0)
    ebe = EBEBoundary()
    meta.add_layer("ebe_boundary", ebe.log_penalty)

    # RBC regime (galactic scale)
    rbc = RBCRegime(scale="galactic")
    meta.add_layer("rbc_regime", rbc.log_penalty)

    return meta


def load_config(config_path: str) -> dict:
    """Load YAML or JSON config."""
    path = Path(config_path)
    if not path.exists():
        logger.warning("Config not found: %s — using defaults", config_path)
        return {}

    if path.suffix in (".yaml", ".yml"):
        try:
            import yaml
            with open(path) as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not installed — trying JSON fallback")

    with open(path) as f:
        return json.load(f)


def run(args):
    """Main inference run."""
    config = {}
    if args.config:
        config = load_config(args.config)

    # Data path
    data_path = args.data or config.get("data_path")
    if data_path is None:
        # Default: look for SPARC data in common locations
        candidates = [
            "data/sparc/sparc_rotation_curves.dat",
            "../EFC/docs/papers/efc/Comprehensive-analysis-of-175-SPARC-galaxies-under-EFC-with-Global-Parameter-Optimization/sparc-n175-extended/sparc_rotation_curves.dat",
        ]
        for c in candidates:
            if Path(c).exists():
                data_path = c
                break
        if data_path is None:
            logger.error("No SPARC data found. Use --data or set data_path in config.")
            sys.exit(1)

    galaxy = args.galaxy or config.get("galaxy", "NGC2403")

    # Sampling config
    n_walkers = config.get("n_walkers", 32)
    n_steps = config.get("n_steps", 5000)
    burn_in = config.get("burn_in", 1000)

    if args.dry_run:
        n_walkers = 16
        n_steps = 100
        burn_in = 20
        logger.info("DRY RUN: 16 walkers, 100 steps, 20 burn-in")

    # Build components
    params = build_parameters()
    engine = EFCRotation()
    module = SPARCModule(engine)
    module.load_data(data_path=data_path, galaxy=galaxy)
    meta = build_meta()

    logger.info("Parameters: %s", params)
    logger.info("Module: %s (%d data points)", module.name, module.n_data)
    logger.info("Meta layers: %s", meta.layer_names)

    # Run sampler
    sampler = EFCSampler(params, modules=[module], meta=meta,
                          n_walkers=n_walkers)
    sampler.run(n_steps=n_steps, burn_in=burn_in, progress=not args.quiet)

    # Results
    results = sampler.results()

    # PPC
    ppc = ppc_report(module, results["best_fit"])
    logger.info("chi2_reduced: %.3f", ppc.get("chi2_reduced", -1))

    # Report
    rg = ReportGenerator(results, ppc_results=ppc, module_name=module.name)

    if args.output_dir:
        saved = rg.save(args.output_dir)
        logger.info("Reports saved: %s", saved)
    else:
        print(rg.to_markdown())

    # Neo4j publish
    if args.publish:
        publisher = Neo4jPublisher()
        pub_result = publisher.publish(results, ppc_results=ppc,
                                        module_name=module.name)
        logger.info("Neo4j publish: %s", pub_result)

        if ppc.get("chi2_reduced") is not None:
            publisher.update_publication_support(
                module.name, ppc["chi2_reduced"]
            )

    return results, ppc


def main():
    parser = argparse.ArgumentParser(
        description="EFC SPARC Rotation Curve Inference"
    )
    parser.add_argument("--config", type=str, default=None,
                        help="Path to YAML/JSON config file")
    parser.add_argument("--data", type=str, default=None,
                        help="Path to SPARC data file")
    parser.add_argument("--galaxy", type=str, default=None,
                        help="Galaxy name (for multi-galaxy files)")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Output directory for reports")
    parser.add_argument("--publish", action="store_true",
                        help="Publish results to Neo4j")
    parser.add_argument("--dry-run", action="store_true",
                        help="Quick test run (100 steps)")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress progress bar")
    args = parser.parse_args()

    run(args)


if __name__ == "__main__":
    main()
