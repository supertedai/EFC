"""
Neo4j Publisher for EFC Inference Results

Publishes inference results as EFCValidation:InferenceResult nodes
in Neo4j. These nodes are automatically read by breakthrough_tracker_v2
for evidence scoring.

Node format (matches breakthrough_tracker_v2 expectations):
    (:EFCValidation:InferenceResult {
        test_id: "inference_sparc_NGC2403",
        name: "SPARC NGC2403 Inference",
        description: "EFC rotation curve fit",
        result: "chi2_red=1.23",
        status: "completed",
        chi2_reduced: 1.23,
        p_value: 0.45,
        n_data: 42,
        n_params: 4,
        converged: true,
        best_fit: "{...}",
        timestamp: "2026-02-08T..."
    })
"""

import json
import logging
import os
import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class Neo4jPublisher:
    """Publish inference results to Neo4j as EFCValidation nodes."""

    def __init__(self, neo4j_uri: str = None, neo4j_user: str = None,
                 neo4j_password: str = None):
        self.uri = neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = neo4j_user or os.getenv("NEO4J_USER", "neo4j")
        self.password = neo4j_password or os.getenv("NEO4J_PASSWORD", "")

    def _get_driver(self):
        try:
            from neo4j import GraphDatabase
            return GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        except ImportError:
            raise ImportError("neo4j driver required: pip install neo4j")

    def publish(self, results: dict, ppc_results: Optional[dict] = None,
                module_name: str = "unknown",
                test_id: Optional[str] = None) -> dict:
        """
        MERGE an EFCValidation:InferenceResult node in Neo4j.

        Parameters:
            results:      Output from EFCSampler.results()
            ppc_results:  Output from ppc_report()
            module_name:  Module identifier (e.g. "sparc_NGC2403")
            test_id:      Unique test identifier (auto-generated if None)

        Returns:
            Dict with node info and status.
        """
        if test_id is None:
            test_id = f"inference_{module_name}"

        timestamp = datetime.datetime.utcnow().isoformat() + "Z"

        # Determine result status
        bf = results.get("best_fit", {})
        conv = results.get("convergence", {})
        chi2_red = ppc_results.get("chi2_reduced", None) if ppc_results else None

        if chi2_red is not None:
            if chi2_red < 2.0:
                status = "success"
                result_str = f"chi2_red={chi2_red:.3f} (good fit)"
            elif chi2_red < 5.0:
                status = "partial"
                result_str = f"chi2_red={chi2_red:.3f} (moderate fit)"
            else:
                status = "poor_fit"
                result_str = f"chi2_red={chi2_red:.3f} (poor fit)"
        else:
            status = "completed"
            result_str = "inference completed (no PPC)"

        # Build node properties
        props = {
            "test_id": test_id,
            "name": f"EFC Inference: {module_name}",
            "description": f"Bayesian inference result for {module_name}",
            "result": result_str,
            "status": status,
            "timestamp": timestamp,
            "source": "efc_inference_engine",
            "converged": conv.get("converged", False),
            "acceptance_fraction": conv.get("acceptance_fraction", 0.0),
            "n_samples": results.get("n_samples", 0),
            "best_fit_json": json.dumps(bf, default=str),
        }

        if chi2_red is not None:
            props["chi2_reduced"] = chi2_red
        if ppc_results and "bayesian_p_value" in ppc_results:
            props["p_value"] = ppc_results["bayesian_p_value"]

        # Posterior summary
        ps = results.get("posterior_summary", {})
        if ps:
            props["posterior_summary_json"] = json.dumps(ps, default=str)

        # MERGE into Neo4j — skip nodes that are DOI-locked (manually curated)
        cypher = """
        MERGE (v:EFCValidation:InferenceResult {test_id: $test_id})
        WITH v, coalesce(v.doi_locked, false) AS locked
        // Only update if NOT doi_locked — preserves manually curated DOI data
        FOREACH (_ IN CASE WHEN NOT locked THEN [1] ELSE [] END |
            SET v.name = $name,
                v.description = $description,
                v.result = $result,
                v.status = $status,
                v.timestamp = $timestamp,
                v.source = $source,
                v.converged = $converged,
                v.acceptance_fraction = $acceptance_fraction,
                v.n_samples = $n_samples,
                v.best_fit_json = $best_fit_json,
                v.chi2_reduced = $chi2_reduced,
                v.p_value = $p_value,
                v.posterior_summary_json = $posterior_summary_json
        )
        RETURN elementId(v) as node_id, v.test_id as test_id, locked as was_locked
        """

        # Fill optional fields with defaults
        props.setdefault("chi2_reduced", None)
        props.setdefault("p_value", None)
        props.setdefault("posterior_summary_json", "{}")

        try:
            driver = self._get_driver()
            with driver.session() as session:
                record = session.run(cypher, **props).single()
                driver.close()

                node_id = record["node_id"] if record else None
                was_locked = record["was_locked"] if record else False
                if was_locked:
                    logger.info(f"Skipped DOI-locked InferenceResult: {test_id} "
                                f"(doi_locked=true, node_id={node_id})")
                else:
                    logger.info(f"Published InferenceResult: {test_id} "
                                f"(status={status}, node_id={node_id})")

                return {
                    "published": True,
                    "test_id": test_id,
                    "node_id": node_id,
                    "status": status,
                    "chi2_reduced": chi2_red,
                }

        except Exception as e:
            logger.error(f"Failed to publish to Neo4j: {e}")
            return {
                "published": False,
                "test_id": test_id,
                "error": str(e),
            }

    def update_publication_support(self, module_name: str,
                                    chi2_red: float) -> bool:
        """
        Update Publication.empirical_support based on inference results.

        Maps chi2_red to support level:
            < 1.5: "strong"
            < 3.0: "moderate"
            < 5.0: "weak"
            >= 5.0: "unsupported"
        """
        if chi2_red < 1.5:
            support = "strong"
        elif chi2_red < 3.0:
            support = "moderate"
        elif chi2_red < 5.0:
            support = "weak"
        else:
            support = "unsupported"

        cypher = """
        MATCH (p:Publication)
        WHERE toLower(p.title) CONTAINS toLower($module_name)
           OR toLower(p.name) CONTAINS toLower($module_name)
        SET p.empirical_support = $support,
            p.empirical_support_updated = $timestamp
        RETURN count(p) as updated
        """

        try:
            driver = self._get_driver()
            with driver.session() as session:
                result = session.run(
                    cypher,
                    module_name=module_name,
                    support=support,
                    timestamp=datetime.datetime.utcnow().isoformat() + "Z",
                ).single()
                driver.close()

                updated = result["updated"] if result else 0
                logger.info(f"Updated {updated} Publications with "
                            f"empirical_support={support}")
                return updated > 0

        except Exception as e:
            logger.error(f"Failed to update Publication support: {e}")
            return False
