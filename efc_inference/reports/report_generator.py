"""
EFC Inference Report Generator

Produces JSON and Markdown reports from inference results.
Reports include: best-fit parameters, uncertainties, chi2, PPC, convergence.
"""

import json
import datetime
from pathlib import Path
from typing import Optional


class ReportGenerator:
    """Generate structured reports from EFC inference results."""

    def __init__(self, results: dict, ppc_results: Optional[dict] = None,
                 module_name: str = "unknown"):
        self.results = results
        self.ppc = ppc_results
        self.module_name = module_name
        self.timestamp = datetime.datetime.utcnow().isoformat() + "Z"

    def to_json(self) -> dict:
        """Full JSON report."""
        report = {
            "efc_inference_report": {
                "version": "0.1.0",
                "timestamp": self.timestamp,
                "module": self.module_name,
                "best_fit": self.results.get("best_fit", {}),
                "posterior_summary": self.results.get("posterior_summary", {}),
                "convergence": self.results.get("convergence", {}),
                "sampling": {
                    "n_walkers": self.results.get("n_walkers", 0),
                    "n_samples": self.results.get("n_samples", 0),
                    "modules": self.results.get("modules", []),
                    "meta_layers": self.results.get("meta_layers", []),
                },
            }
        }

        if self.ppc:
            report["efc_inference_report"]["ppc"] = self.ppc

        return report

    def to_markdown(self) -> str:
        """Markdown summary report."""
        r = self.results
        lines = [
            f"# EFC Inference Report: {self.module_name}",
            f"*Generated: {self.timestamp}*",
            "",
        ]

        # Best fit
        bf = r.get("best_fit", {})
        lines.append("## Best-Fit Parameters")
        lines.append("| Parameter | Value |")
        lines.append("|-----------|-------|")
        for k, v in bf.items():
            if not k.startswith("_"):
                lines.append(f"| {k} | {v:.6g} |")
        if "_log_posterior" in bf:
            lines.append(f"\nlog-posterior: {bf['_log_posterior']:.2f}")
        lines.append("")

        # Posterior summary
        ps = r.get("posterior_summary", {})
        if ps:
            lines.append("## Posterior Summary")
            lines.append("| Parameter | Median | -1sig | +1sig | Std |")
            lines.append("|-----------|--------|-------|-------|-----|")
            for name, stats in ps.items():
                lines.append(
                    f"| {name} | {stats['median']:.6g} | "
                    f"{stats['err_minus']:.3g} | {stats['err_plus']:.3g} | "
                    f"{stats['std']:.3g} |"
                )
            lines.append("")

        # PPC
        if self.ppc:
            lines.append("## Posterior Predictive Checks")
            lines.append(f"- chi2_reduced: {self.ppc.get('chi2_reduced', '?'):.3f}")

            cal = self.ppc.get("calibration", {})
            if cal:
                lines.append(f"- Within 1-sigma: {cal.get('within_1sigma', 0):.1%} "
                              f"(expected: 68.3%)")
                lines.append(f"- Within 2-sigma: {cal.get('within_2sigma', 0):.1%} "
                              f"(expected: 95.4%)")

            if "bayesian_p_value" in self.ppc:
                lines.append(f"- Bayesian p-value: {self.ppc['bayesian_p_value']:.3f}")
            lines.append("")

        # Convergence
        conv = r.get("convergence", {})
        if conv:
            lines.append("## Convergence")
            lines.append(f"- Converged: {'Yes' if conv.get('converged') else 'No'}")
            lines.append(f"- Acceptance fraction: {conv.get('acceptance_fraction', 0):.3f}")

            rhat = conv.get("r_hat", {})
            if rhat:
                lines.append("- R-hat: " + ", ".join(
                    f"{k}={v:.3f}" for k, v in rhat.items()))

            ess = conv.get("ess", {})
            if ess:
                lines.append("- ESS: " + ", ".join(
                    f"{k}={v:.0f}" for k, v in ess.items()))

        return "\n".join(lines)

    def save(self, output_dir: str, prefix: str = "efc_inference"):
        """Save JSON and Markdown reports to output directory."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        timestamp_str = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        base = f"{prefix}_{self.module_name}_{timestamp_str}"

        json_path = out / f"{base}.json"
        md_path = out / f"{base}.md"

        with open(json_path, "w") as f:
            json.dump(self.to_json(), f, indent=2, default=str)

        with open(md_path, "w") as f:
            f.write(self.to_markdown())

        return {"json": str(json_path), "markdown": str(md_path)}
