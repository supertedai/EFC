"""
CLI Runner: BAO Distance Inference

Usage:
    python -m efc_inference.runs.run_bao --config config_bao.yaml
    python -m efc_inference.runs.run_bao --data efc_inference/data/bao/bao_starter.csv
    python -m efc_inference.runs.run_bao --dry-run --data efc_inference/data/bao/bao_smoketest.csv
"""

import argparse
import logging
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from efc_inference.core.parameters import EFCParameterVector
from efc_inference.core.priors import GaussianPrior, UniformPrior
from efc_inference.core.sampler import EFCSampler, MetaController
from efc_inference.core.ppc import ppc_report
from efc_inference.engine.hubble import EFCHubble
from efc_inference.modules.bao_module import BAOModule
from efc_inference.meta.epistemic_levels import EpistemicWeighting, EpistemicLevel
from efc_inference.meta.ebe_boundary import EBEBoundary
from efc_inference.meta.rbc_regime import RBCRegime
from efc_inference.reports.report_generator import ReportGenerator
from efc_inference.reports.neo4j_publisher import Neo4jPublisher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger("efc_inference.bao")


def build_parameters() -> EFCParameterVector:
    """Build parameters for BAO inference."""
    pv = EFCParameterVector()

    pv.add("H0", 67.4,
           bounds=(50.0, 90.0),
           prior=GaussianPrior(67.4, 5.0))

    pv.add("Omega_m", 0.315,
           bounds=(0.1, 0.6),
           prior=GaussianPrior(0.315, 0.05))

    pv.add("alpha_cosmo", 0.0,
           bounds=(-1.0, 1.0),
           prior=GaussianPrior(0.0, 0.5))

    pv.add("r_d", 147.09,
           bounds=(130.0, 160.0),
           prior=GaussianPrior(147.09, 5.0))

    return pv


def build_meta() -> MetaController:
    """Build meta-control layers."""
    meta = MetaController()

    ew = EpistemicWeighting(default_level=EpistemicLevel.L1)
    ew.set_level("H0", EpistemicLevel.L3)            # Well measured
    ew.set_level("Omega_m", EpistemicLevel.L2)        # CMB + LSS
    ew.set_level("alpha_cosmo", EpistemicLevel.L0)    # Speculative EFC
    ew.set_level("r_d", EpistemicLevel.L2)            # CMB-calibrated
    meta.add_layer("epistemic_L0L3", ew.log_penalty)

    ebe = EBEBoundary()
    meta.add_layer("ebe_boundary", ebe.log_penalty)

    rbc = RBCRegime(scale="cosmological")
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
    """Main BAO inference run."""
    config = {}
    if args.config:
        config = load_config(args.config)

    data_path = args.data or config.get("data_path",
                                         "efc_inference/data/bao/bao_smoketest.csv")

    n_walkers = config.get("n_walkers", 32)
    n_steps = config.get("n_steps", 5000)
    burn_in = config.get("burn_in", 1000)

    if args.dry_run:
        n_walkers = 16
        n_steps = 100
        burn_in = 20
        logger.info("DRY RUN: 16 walkers, 100 steps, 20 burn-in")

    params = build_parameters()
    engine = EFCHubble()
    module = BAOModule(engine)
    module.load_data(data_path=data_path)
    meta = build_meta()

    logger.info("Parameters: %s", params)
    logger.info("Module: %s (%d data points)", module.name, module.n_data)
    logger.info("Meta layers: %s", meta.layer_names)

    sampler = EFCSampler(params, modules=[module], meta=meta,
                          n_walkers=n_walkers)
    sampler.run(n_steps=n_steps, burn_in=burn_in, progress=not args.quiet)

    results = sampler.results()

    ppc = ppc_report(module, results["best_fit"])
    logger.info("chi2_reduced: %.3f", ppc.get("chi2_reduced", -1))

    rg = ReportGenerator(results, ppc_results=ppc, module_name=module.name)

    if args.output_dir:
        saved = rg.save(args.output_dir)
        logger.info("Reports saved: %s", saved)
    else:
        print(rg.to_markdown())

    if args.publish:
        publisher = Neo4jPublisher()
        pub_result = publisher.publish(results, ppc_results=ppc,
                                        module_name=module.name)
        logger.info("Neo4j publish: %s", pub_result)

    return results, ppc


def main():
    parser = argparse.ArgumentParser(
        description="EFC BAO Distance Inference"
    )
    parser.add_argument("--config", type=str, default=None)
    parser.add_argument("--data", type=str, default=None)
    parser.add_argument("--output-dir", type=str, default=None)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    run(args)


if __name__ == "__main__":
    main()
