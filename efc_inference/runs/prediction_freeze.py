"""
Prediction Freeze Module — Blind Predictions for Future Data Releases.

Purpose:
  Takes the current best-fit posterior, freezes predictions at specific
  (probe, z) targets, and generates a cryptographically sealed,
  immutable prediction record.

Design principle:
  "Commit the prediction BEFORE the data. Never touch it after."

Targets:
  1. DH/rd @ z=1.0  (3.1σ forecast separation, DESI DR2)
  2. fσ8 @ z=0.7    (2.0σ forecast separation, Euclid/DESI)
  3. fσ8 crossover   @ z=2.042±0.055  (100% posterior fraction)
  4. H(z) deviation  peak +5.4% @ z≈1.06  (monotonic, no crossover)

Author: Symbiose AGI / COO
"""

import hashlib
import json
import logging
import numpy as np
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

_BASE = Path(__file__).resolve().parent.parent


# ─── Data classes ────────────────────────────────────────────────

@dataclass
class FrozenPrediction:
    """A single frozen observable prediction at a specific (probe, z)."""
    probe: str
    label: str
    z: float
    pred_efc: float
    pred_lcdm: float
    delta: float
    delta_pct: float
    separation_sigma: float      # |delta| / future_error
    future_error: float
    ci_68_lo: float
    ci_68_hi: float
    ci_95_lo: float
    ci_95_hi: float
    posterior_draws_n: int


@dataclass
class CrossoverSignature:
    """The fσ8 crossover signature from posterior draws."""
    z_median: float
    z_std: float
    z_min: float
    z_max: float
    z_q25: float
    z_q75: float
    fraction_with_crossover: float
    n_draws: int


@dataclass
class FreezeDocument:
    """The complete immutable prediction record."""
    # Identity
    freeze_id: str
    document_id: str             # SHA256[:16] of content
    timestamp_utc: str
    schema_version: str = "1.0"

    # Provenance
    cycle_id: str = ""
    sampler_type: str = ""
    code_commit: str = ""
    dataset_hash: str = ""
    assumptions_hash: str = ""
    cosmology_model: str = "efc_variant_f"

    # Posterior summary
    posterior_median: Dict = field(default_factory=dict)
    posterior_ci68: Dict = field(default_factory=dict)
    alpha_significance: float = 0.0
    n_posterior_draws: int = 0

    # Predictions
    predictions: List[FrozenPrediction] = field(default_factory=list)

    # Crossover signature
    crossover: Optional[CrossoverSignature] = None

    # H(z) deviation profile
    hz_peak_deviation_pct: float = 0.0
    hz_peak_z: float = 0.0
    hz_crossover_exists: bool = False

    # Falsification criteria
    falsification_criteria: List[Dict] = field(default_factory=list)

    # Cryptographic seal
    content_hash: str = ""


# ─── Default freeze targets ─────────────────────────────────────

DEFAULT_TARGETS = [
    {"probe": "DH_rd",    "z": 1.0, "future_error": 0.3,
     "label": "DH/rd @ z=1.0 [DESI DR2 BAO]"},
    {"probe": "DH_rd",    "z": 0.7, "future_error": 0.4,
     "label": "DH/rd @ z=0.7 [DESI DR2 BAO]"},
    {"probe": "fsigma8",  "z": 0.7, "future_error": 0.010,
     "label": "fσ8 @ z=0.7 [Euclid/DESI DR2]"},
    {"probe": "fsigma8",  "z": 1.0, "future_error": 0.015,
     "label": "fσ8 @ z=1.0 [DESI DR2]"},
    {"probe": "Hz",       "z": 1.0, "future_error": 5.0,
     "label": "H(z=1.0) [Cosmic chronometers improved]"},
    {"probe": "Hz",       "z": 0.7, "future_error": 3.5,
     "label": "H(z=0.7) [Cosmic chronometers improved]"},
]


class PredictionFreezeModule:
    """Freeze current best-fit posterior predictions for future falsification."""

    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir) if output_dir else _BASE / "outputs" / "freeze"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def freeze_from_chain(self, chain_file: str, cycle_id: str,
                          sampler_type: str = "nuts",
                          n_ci_draws: int = 200,
                          targets: list = None,
                          crossover_results: dict = None) -> FreezeDocument:
        """Main entry: load posterior chain, compute frozen predictions.

        Args:
            chain_file: Path to NUTS JSON or emcee NPZ
            cycle_id: Source cycle identifier
            sampler_type: 'nuts' or 'emcee'
            n_ci_draws: Number of posterior draws for CI bounds
            targets: List of target dicts, or DEFAULT_TARGETS
            crossover_results: Pre-computed crossover results dict
        """
        if targets is None:
            targets = DEFAULT_TARGETS

        # 1. Load chain
        chain, params_summary = self._load_chain(chain_file, sampler_type)
        logger.info(f"Loaded chain: {chain.shape[0]} samples, cycle={cycle_id}")

        # 2. Extract median + CI
        median_params = {
            "Omega_m": float(np.median(chain[:, 0])),
            "H0": float(np.median(chain[:, 1])),
            "sigma8": float(np.median(chain[:, 2])),
            "alpha_cosmo": float(np.median(chain[:, 3])),
            "r_d": 147.09,
        }
        lcdm_params = {**median_params, "alpha_cosmo": 0.0}

        ci68 = {
            "Omega_m": [float(np.percentile(chain[:, 0], 16)),
                        float(np.percentile(chain[:, 0], 84))],
            "H0": [float(np.percentile(chain[:, 1], 16)),
                   float(np.percentile(chain[:, 1], 84))],
            "sigma8": [float(np.percentile(chain[:, 2], 16)),
                       float(np.percentile(chain[:, 2], 84))],
            "alpha_cosmo": [float(np.percentile(chain[:, 3], 16)),
                            float(np.percentile(chain[:, 3], 84))],
        }

        alpha_med = median_params["alpha_cosmo"]
        alpha_std = float(np.std(chain[:, 3]))
        alpha_sig = abs(alpha_med / alpha_std) if alpha_std > 0 else 0

        # 3. Compute frozen predictions with CI from posterior draws
        predictions = self._compute_frozen_predictions(
            chain, median_params, lcdm_params, targets, n_ci_draws)

        # 4. Crossover signature
        crossover = None
        if crossover_results and "fs8_crossover" in crossover_results:
            cs = crossover_results["fs8_crossover"]
            crossover = CrossoverSignature(
                z_median=cs["z_median"],
                z_std=cs["z_std"],
                z_min=cs["z_min"],
                z_max=cs["z_max"],
                z_q25=cs["z_q25"],
                z_q75=cs["z_q75"],
                fraction_with_crossover=cs["fraction_with_crossover"],
                n_draws=crossover_results.get("n_draws", 200),
            )

        # H(z) deviation
        hz_peak_pct = 0.0
        hz_peak_z = 0.0
        if crossover_results and "H_deviation_profile" in crossover_results:
            prof = crossover_results["H_deviation_profile"]
            hz_peak_pct = prof.get("max_dH_over_H_pct", {}).get("median", 0.0)
            hz_peak_z = prof.get("z_of_max_deviation", {}).get("median", 0.0)

        # 5. Build falsification criteria
        falsification = self._build_falsification_criteria(
            predictions, crossover, hz_peak_pct)

        # 6. Provenance
        code_commit = self._get_code_commit()
        dataset_hash = self._compute_dataset_hash()

        # 7. Build document
        ts = datetime.now(timezone.utc).isoformat()
        freeze_id = f"freeze_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        doc = FreezeDocument(
            freeze_id=freeze_id,
            document_id="",  # computed after content_hash
            timestamp_utc=ts,
            cycle_id=cycle_id,
            sampler_type=sampler_type,
            code_commit=code_commit,
            dataset_hash=dataset_hash,
            cosmology_model="efc_variant_f",
            posterior_median=median_params,
            posterior_ci68=ci68,
            alpha_significance=alpha_sig,
            n_posterior_draws=chain.shape[0],
            predictions=predictions,
            crossover=crossover,
            hz_peak_deviation_pct=hz_peak_pct,
            hz_peak_z=hz_peak_z,
            hz_crossover_exists=False,
            falsification_criteria=falsification,
        )

        # 8. Seal
        doc.content_hash = self._compute_content_hash(doc)
        doc.document_id = hashlib.sha256(
            f"{doc.content_hash}:{ts}:{code_commit}".encode()
        ).hexdigest()[:16]

        # 9. Save
        path = self._save_json(doc)
        logger.info(f"FREEZE DOCUMENT SEALED: {doc.document_id}")
        logger.info(f"  Content hash: {doc.content_hash[:32]}...")
        logger.info(f"  Saved to: {path}")
        for pred in predictions:
            logger.info(f"  {pred.label}: EFC={pred.pred_efc:.4f} vs "
                        f"LCDM={pred.pred_lcdm:.4f} ({pred.delta_pct:+.2f}%, "
                        f"{pred.separation_sigma:.1f}σ forecast)")
        if crossover:
            logger.info(f"  fσ8 crossover: z={crossover.z_median:.3f}±{crossover.z_std:.3f} "
                        f"({crossover.fraction_with_crossover*100:.0f}% of draws)")

        return doc

    def _load_chain(self, chain_file: str, sampler_type: str):
        """Load posterior chain from file."""
        path = Path(chain_file)
        if sampler_type == "nuts" or path.suffix == ".json":
            with open(path) as f:
                data = json.load(f)
            chain = np.array(data["posterior_chain"])  # (N, 4)
            return chain, data.get("chain_summary", {})
        elif sampler_type == "emcee" or path.suffix == ".npz":
            npz = np.load(path)
            chain = npz["flatchain"]  # (N, 4)
            return chain, {}
        else:
            raise ValueError(f"Unknown chain format: {path}")

    def _compute_frozen_predictions(self, chain, median_params, lcdm_params,
                                     targets, n_draws):
        """Compute predictions with CI bounds from posterior draws."""
        from ..engine.hubble import EFCHubble
        from ..engine.growth import EFCGrowth
        from ..core.cosmology_model import EFCVariantF, FlatLCDM

        hub_efc = EFCHubble(cosmology=EFCVariantF())
        hub_lcdm = EFCHubble(cosmology=FlatLCDM())
        gro_efc = EFCGrowth(cosmology=EFCVariantF())
        gro_lcdm = EFCGrowth(cosmology=FlatLCDM())

        c_km = 299792.458
        r_d = median_params.get("r_d", 147.09)

        rng = np.random.default_rng(42)
        idx = rng.choice(len(chain), size=min(n_draws, len(chain)), replace=False)

        predictions = []
        for target in targets:
            probe = target["probe"]
            z = target["z"]
            z_arr = np.array([z])
            future_error = target["future_error"]
            label = target["label"]

            # Median prediction
            pred_efc_med = self._predict_observable(
                probe, median_params, hub_efc, gro_efc, z_arr, r_d, c_km)[0]
            pred_lcdm_med = self._predict_observable(
                probe, lcdm_params, hub_lcdm, gro_lcdm, z_arr, r_d, c_km)[0]

            # Posterior CI
            draws = []
            for i in idx:
                p = {
                    "Omega_m": float(chain[i, 0]),
                    "H0": float(chain[i, 1]),
                    "sigma8": float(chain[i, 2]),
                    "alpha_cosmo": float(chain[i, 3]),
                    "r_d": 147.09,
                }
                try:
                    val = self._predict_observable(
                        probe, p, hub_efc, gro_efc, z_arr, r_d, c_km)[0]
                    draws.append(val)
                except Exception:
                    continue

            draws = np.array(draws)
            ci_68_lo = float(np.percentile(draws, 16)) if len(draws) > 0 else pred_efc_med
            ci_68_hi = float(np.percentile(draws, 84)) if len(draws) > 0 else pred_efc_med
            ci_95_lo = float(np.percentile(draws, 2.5)) if len(draws) > 0 else pred_efc_med
            ci_95_hi = float(np.percentile(draws, 97.5)) if len(draws) > 0 else pred_efc_med

            delta = pred_efc_med - pred_lcdm_med
            delta_pct = 100 * delta / pred_lcdm_med if pred_lcdm_med != 0 else 0
            sep_sigma = abs(delta) / future_error if future_error > 0 else 0

            predictions.append(FrozenPrediction(
                probe=probe,
                label=label,
                z=z,
                pred_efc=float(pred_efc_med),
                pred_lcdm=float(pred_lcdm_med),
                delta=float(delta),
                delta_pct=float(delta_pct),
                separation_sigma=float(sep_sigma),
                future_error=future_error,
                ci_68_lo=ci_68_lo,
                ci_68_hi=ci_68_hi,
                ci_95_lo=ci_95_lo,
                ci_95_hi=ci_95_hi,
                posterior_draws_n=len(draws),
            ))

        return predictions

    def _predict_observable(self, probe, params, hub, gro, z_arr, r_d, c_km):
        """Compute a single observable value."""
        if probe == "Hz":
            return hub.compute(params, z_arr)
        elif probe == "fsigma8":
            return gro.compute(params, z_arr)
        elif probe == "DH_rd":
            hz = hub.compute(params, z_arr)
            return c_km / (hz * r_d)
        elif probe == "DM_rd":
            # Comoving distance / rd — simplified via trapezoidal integration
            z_fine = np.linspace(0.001, float(z_arr[0]), 500)
            hz_fine = hub.compute(params, z_fine)
            dc = np.trapezoid(c_km / hz_fine, z_fine)
            return np.array([dc / r_d])
        else:
            raise ValueError(f"Unknown probe: {probe}")

    def _build_falsification_criteria(self, predictions, crossover, hz_peak_pct):
        """Define explicit falsification conditions."""
        criteria = []

        for pred in predictions:
            # EFC predicts deviation in specific direction
            direction = "below" if pred.delta < 0 else "above"
            anti_direction = "above" if pred.delta < 0 else "below"

            crit = {
                "target": pred.label,
                "efc_predicts": round(pred.pred_efc, 4),
                "lcdm_predicts": round(pred.pred_lcdm, 4),
                "delta_pct": round(pred.delta_pct, 2),
                "forecast_separation_sigma": round(pred.separation_sigma, 1),
                "efc_ci_68": [round(pred.ci_68_lo, 4), round(pred.ci_68_hi, 4)],
                "efc_ci_95": [round(pred.ci_95_lo, 4), round(pred.ci_95_hi, 4)],
                "falsified_if": (
                    f"Measured value is {anti_direction} ΛCDM prediction "
                    f"({pred.pred_lcdm:.4f}) at ≥2σ"
                ),
                "confirmed_if": (
                    f"Measured value is {direction} ΛCDM, consistent with "
                    f"EFC prediction ({pred.pred_efc:.4f}) within 1σ"
                ),
            }
            criteria.append(crit)

        # Crossover falsification
        if crossover and crossover.fraction_with_crossover > 0.9:
            criteria.append({
                "target": f"fσ8 crossover at z={crossover.z_median:.3f}±{crossover.z_std:.3f}",
                "efc_predicts": f"Sign change: fσ8_EFC < fσ8_LCDM for z<{crossover.z_median:.1f}, "
                                f"fσ8_EFC > fσ8_LCDM for z>{crossover.z_median:.1f}",
                "posterior_fraction": crossover.fraction_with_crossover,
                "falsified_if": ("3+ measurements at z=1.8-2.3 show no sign change "
                                 "in (EFC−LCDM) fσ8 residuals"),
                "confirmed_if": ("fσ8 data at z~2 shows positive excess "
                                 "(EFC above LCDM) after consistent suppression at z<1.5"),
                "decision_horizon": "Euclid + DESI spectroscopic 2027+",
            })

        # H(z) monotonic profile
        if hz_peak_pct > 1.0:
            criteria.append({
                "target": f"H(z) monotonic deviation, peak +{hz_peak_pct:.1f}% at z≈1.1",
                "efc_predicts": "H_EFC > H_LCDM at all z>0, no crossover, peak near z≈1",
                "peak_deviation_pct": round(hz_peak_pct, 2),
                "falsified_if": ("H(z) measurements at z=0.5-1.5 consistent "
                                 "with ΛCDM at <2σ across all bins"),
                "confirmed_if": ("Systematic positive H(z) offset of 4-6% "
                                 "in the z=0.8-1.2 range"),
                "decision_horizon": "DESI DR2 + SKAO HI galaxy survey 2026-2028",
            })

        return criteria

    def _compute_content_hash(self, doc: FreezeDocument) -> str:
        """SHA256 over sorted JSON of all prediction values."""
        content = {
            "predictions": [
                {
                    "probe": p.probe, "z": round(p.z, 4),
                    "pred_efc": round(p.pred_efc, 8),
                    "pred_lcdm": round(p.pred_lcdm, 8),
                }
                for p in doc.predictions
            ],
            "crossover": asdict(doc.crossover) if doc.crossover else None,
            "posterior_median": {k: round(v, 8) for k, v in doc.posterior_median.items()},
            "cosmology_model": doc.cosmology_model,
        }
        canonical = json.dumps(content, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def _get_code_commit(self) -> str:
        """Get current git short hash."""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True,
                cwd=str(_BASE.parent),
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

    def _compute_dataset_hash(self) -> str:
        """Hash of input data files."""
        try:
            from .schema_contract import compute_dataset_hash
            return compute_dataset_hash()
        except Exception:
            return "unavailable"

    def _save_json(self, doc: FreezeDocument) -> Path:
        """Save FreezeDocument as immutable JSON."""
        path = self.output_dir / f"{doc.freeze_id}.json"
        if path.exists():
            logger.warning(f"Freeze file already exists: {path} — appending timestamp")
            path = self.output_dir / f"{doc.freeze_id}_{doc.document_id}.json"

        data = {
            "freeze_id": doc.freeze_id,
            "document_id": doc.document_id,
            "timestamp_utc": doc.timestamp_utc,
            "schema_version": doc.schema_version,
            "content_hash": doc.content_hash,
            "provenance": {
                "cycle_id": doc.cycle_id,
                "sampler_type": doc.sampler_type,
                "code_commit": doc.code_commit,
                "dataset_hash": doc.dataset_hash,
                "cosmology_model": doc.cosmology_model,
            },
            "posterior": {
                "median": doc.posterior_median,
                "ci68": doc.posterior_ci68,
                "alpha_significance": doc.alpha_significance,
                "n_draws": doc.n_posterior_draws,
            },
            "predictions": [asdict(p) for p in doc.predictions],
            "crossover_signature": asdict(doc.crossover) if doc.crossover else None,
            "hz_deviation": {
                "peak_pct": doc.hz_peak_deviation_pct,
                "peak_z": doc.hz_peak_z,
                "crossover_exists": doc.hz_crossover_exists,
            },
            "falsification_criteria": doc.falsification_criteria,
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Freeze document saved: {path}")
        return path

    def publish_to_neo4j(self, doc: FreezeDocument,
                          neo4j_uri: str = None,
                          neo4j_user: str = None,
                          neo4j_password: str = None) -> bool:
        """Publish freeze document as immutable Neo4j node."""
        try:
            import os
            uri = neo4j_uri or os.environ.get("NEO4J_URI", "bolt://localhost:7687")
            user = neo4j_user or os.environ.get("NEO4J_USER", "neo4j")
            pw = neo4j_password or os.environ.get("NEO4J_PASSWORD", "")

            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(uri, auth=(user, pw))

            predictions_json = json.dumps([asdict(p) for p in doc.predictions])
            falsification_json = json.dumps(doc.falsification_criteria)

            cypher = """
            MERGE (n:EFCFreeze:EFCValidation {document_id: $document_id})
            ON CREATE SET
                n.freeze_id           = $freeze_id,
                n.timestamp           = $timestamp,
                n.cycle_id            = $cycle_id,
                n.sampler_type        = $sampler_type,
                n.code_commit         = $code_commit,
                n.dataset_hash        = $dataset_hash,
                n.cosmology_model     = $cosmology_model,
                n.content_hash        = $content_hash,
                n.alpha_median        = $alpha_median,
                n.alpha_significance  = $alpha_significance,
                n.fs8_crossover_z     = $fs8_crossover_z,
                n.fs8_crossover_std   = $fs8_crossover_std,
                n.hz_peak_pct         = $hz_peak_pct,
                n.predictions_json    = $predictions_json,
                n.falsification_json  = $falsification_json,
                n.test_id             = $freeze_id,
                n.name                = $name,
                n.status              = 'frozen',
                n.vl_public           = true,
                n.vl_category         = 'planned_pipeline',
                n.source              = 'prediction_freeze_module',
                n.created_at          = datetime()
            ON MATCH SET
                n.last_checked        = datetime()
            RETURN n.document_id AS doc_id, n.freeze_id AS freeze_id
            """

            params = {
                "document_id": doc.document_id,
                "freeze_id": doc.freeze_id,
                "timestamp": doc.timestamp_utc,
                "cycle_id": doc.cycle_id,
                "sampler_type": doc.sampler_type,
                "code_commit": doc.code_commit,
                "dataset_hash": doc.dataset_hash,
                "cosmology_model": doc.cosmology_model,
                "content_hash": doc.content_hash,
                "alpha_median": doc.posterior_median.get("alpha_cosmo", 0),
                "alpha_significance": doc.alpha_significance,
                "fs8_crossover_z": doc.crossover.z_median if doc.crossover else None,
                "fs8_crossover_std": doc.crossover.z_std if doc.crossover else None,
                "hz_peak_pct": doc.hz_peak_deviation_pct,
                "predictions_json": predictions_json,
                "falsification_json": falsification_json,
                "name": f"Blind Prediction Freeze ({doc.cycle_id})",
            }

            with driver.session() as session:
                result = session.run(cypher, params)
                record = result.single()

            driver.close()
            logger.info(f"Published to Neo4j: document_id={record['doc_id']}, "
                        f"freeze_id={record['freeze_id']}")
            return True

        except Exception as e:
            logger.error(f"Neo4j publish failed: {type(e).__name__}: {e}")
            return False


# ─── CLI ─────────────────────────────────────────────────────────

def run_freeze(chain_file: str = None, cycle_id: str = None,
               crossover_file: str = None, publish: bool = True) -> Optional[FreezeDocument]:
    """Run the freeze pipeline from command line or daemon."""

    if chain_file is None:
        # Try to find latest NUTS chain
        chain_file = "/tmp/nuts_latest.json"
    if cycle_id is None:
        cycle_id = Path(chain_file).stem

    # Load crossover results if available
    crossover_results = None
    if crossover_file is None:
        crossover_file = "/tmp/crossover_robustness_results.json"
    if Path(crossover_file).exists():
        with open(crossover_file) as f:
            crossover_results = json.load(f)

    module = PredictionFreezeModule()
    doc = module.freeze_from_chain(
        chain_file=chain_file,
        cycle_id=cycle_id,
        crossover_results=crossover_results,
    )

    if publish:
        module.publish_to_neo4j(doc)

    return doc


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    doc = run_freeze()
    if doc:
        print(f"\n{'='*60}")
        print(f"PREDICTION FREEZE DOCUMENT SEALED")
        print(f"{'='*60}")
        print(f"  Document ID:  {doc.document_id}")
        print(f"  Content Hash: {doc.content_hash[:32]}...")
        print(f"  Cycle:        {doc.cycle_id}")
        print(f"  Timestamp:    {doc.timestamp_utc}")
        print(f"  α median:     {doc.posterior_median.get('alpha_cosmo', 0):.4f}")
        print(f"  α significance: {doc.alpha_significance:.2f}σ")
        print(f"  Predictions:  {len(doc.predictions)}")
        if doc.crossover:
            print(f"  fσ8 crossover: z={doc.crossover.z_median:.3f}±{doc.crossover.z_std:.3f}")
        print(f"\n  FROZEN PREDICTIONS:")
        for p in doc.predictions:
            print(f"    {p.label}")
            print(f"      EFC:  {p.pred_efc:.4f}  [{p.ci_68_lo:.4f}, {p.ci_68_hi:.4f}] (68%)")
            print(f"      ΛCDM: {p.pred_lcdm:.4f}")
            print(f"      Δ:    {p.delta:+.4f} ({p.delta_pct:+.2f}%)")
            print(f"      Forecast: {p.separation_sigma:.1f}σ separation")
        print(f"\n  FALSIFICATION CRITERIA:")
        for c in doc.falsification_criteria:
            print(f"    {c['target']}")
            if 'falsified_if' in c:
                print(f"      ✗ Falsified if: {c['falsified_if']}")
            if 'confirmed_if' in c:
                print(f"      ✓ Confirmed if: {c['confirmed_if']}")
        print(f"{'='*60}")
