# efc_rcmp_convergence_observation.py
# Reference implementation for: Magnusson (2026), DOI: 10.6084/m9.figshare.32080080
# Scope: Encodes RCMP checklist mechanics, regime tagging, and reported S8-tension sensitivity
#         under IA-model choices; exposes phenomenological (mu, Sigma) amplitude handling
#         consistent with the paper's constraints. No action-to-phenomenology mapping is
#         implemented because the paper flags it as an open task.

from __future__ import annotations
import numpy as np
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple, Union

# Numerics explicitly present in the paper excerpt and minimal derived quantities.
PAPER_NUMERICS: Dict[str, object] = {
    "metadata": {
        "title": "Methodological Convergence in Stage-IV Cosmology: The Emergence of Epistemic Holism Under Precision Constraints, and Its Operationalization via RCMP",
        "author": "Morten Magnusson",
        "year": 2026,
        "doi": "10.6084/m9.figshare.32080080",
        "orcid": "0009-0002-4860-5095",
        "status": "PUBLISHED v0.2",
        "license": "CC-BY-4.0",
        "figshare_ids": {
            "this_note": 32080080,
            "rcmp": 31222900,
            "efc_companion": 31112536
        }
    },
    "timeline": {
        "stage_iv_precision_years": {"start": 2023, "end": 2026},
        "kids_legacy_year": 2025
    },
    "rcmp": {
        "components_count": 5,
        "components": [
            "driver_proximity",
            "regime_tagging",
            "proxy_accounting",
            "coordinate_humility",
            "cross_validation"
        ],
        "output_rule": "problem_definition_not_resolution",
        "regime_levels": {
            "labels": ["L0", "L1", "L2", "L3"],
            "ints": [0, 1, 2, 3]
        }
    },
    "cosmic_shear_observation": {
        "des_y6_s8_tension": {
            "nla_sigma_range": [2.4, 2.7],
            "tatt_sigma": 1.7
        }
    },
    "mg_parametrization": {
        "phenomenology_params": ["mu", "Sigma"],
        "amplitudes": ["A_mu", "A_Sigma"],
        "action_level_params": ["K0", "V_prime", "alpha"],
        "mapping_one_to_one": False
    },
    "sections": {
        "test_plan_section": 6,
        "release_conditions_section": 9
    }
}

RCMP_COMPONENTS: Tuple[str, ...] = tuple(PAPER_NUMERICS["rcmp"]["components"])  # type: ignore[index]


def rcmp_compliance(checks: Mapping[str, bool]) -> Dict[str, object]:
    """
    Evaluate RCMP compliance against the five required components.

    Required keys (exact):
      - driver_proximity
      - regime_tagging
      - proxy_accounting
      - coordinate_humility
      - cross_validation

    Returns a dict with:
      - compliant (bool): all checks True and no missing keys
      - score (int): number of True components (0..5)
      - missing (list[str]): any required components not provided
      - failed (list[str]): components provided but False
    """
    required = set(RCMP_COMPONENTS)
    provided = set(checks.keys())
    missing = sorted(list(required - provided))
    failed = sorted([k for k, v in checks.items() if (k in required and not bool(v))])
    score = int(sum(bool(checks.get(k, False)) for k in RCMP_COMPONENTS))
    compliant = (len(missing) == 0) and (score == len(RCMP_COMPONENTS))
    return {
        "compliant": compliant,
        "score": score,
        "missing": missing,
        "failed": failed,
    }


def regime_level(normalized: Union[int, str]) -> Tuple[int, str]:
    """
    Normalize a regime tag to (level_int, label_str) using the paper's L0..L3 convention.
    Accepts either an int in {0,1,2,3} or a case-insensitive label like 'L2'.
    """
    if isinstance(normalized, int):
        if normalized not in (0, 1, 2, 3):
            raise ValueError("Regime integer must be in {0,1,2,3} corresponding to L0..L3")
        return normalized, f"L{normalized}"
    s = str(normalized).strip().upper()
    if s in {"L0", "L1", "L2", "L3"}:
        return int(s[1]), s
    raise ValueError("Regime label must be one of 'L0','L1','L2','L3' or an integer 0..3")


def s8_significance_metrics(nla_sigma_range: Sequence[float], tatt_sigma: float) -> Dict[str, float]:
    """
    Compute basic sensitivity metrics for DES Y6 S8-tension reporting as described in the paper:
      - NLA intrinsic-alignment model yields a 2.4–2.7 sigma tension range
      - TATT model yields 1.7 sigma

    Returns:
      - nla_min, nla_max, nla_mean, nla_width
      - tatt
      - reduction_abs: nla_mean - tatt
      - reduction_frac: (nla_mean - tatt) / nla_mean
    """
    if len(nla_sigma_range) != 2:
        raise ValueError("nla_sigma_range must be length-2 [min, max]")
    nla_min = float(nla_sigma_range[0])
    nla_max = float(nla_sigma_range[1])
    if not (nla_min <= nla_max):
        raise ValueError("nla_sigma_range must satisfy min <= max")
    nla_mean = float((nla_min + nla_max) / 2.0)
    nla_width = float(nla_max - nla_min)
    tatt = float(tatt_sigma)
    reduction_abs = float(nla_mean - tatt)
    reduction_frac = float(reduction_abs / nla_mean) if nla_mean != 0.0 else np.nan
    return {
        "nla_min": nla_min,
        "nla_max": nla_max,
        "nla_mean": nla_mean,
        "nla_width": nla_width,
        "tatt": tatt,
        "reduction_abs": reduction_abs,
        "reduction_frac": reduction_frac,
    }


def mu_sigma_amplitudes(A_mu: float, A_Sigma: float, z: Union[float, Sequence[float], np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Phenomenological (mu, Sigma) amplitude evaluation consistent with the paper's scope.

    The note specifies operating at the MGCAMB/MGCLASS-native phenomenological (mu, Sigma)
    parametrization level for tests, and explicitly does NOT provide a redshift dependence or
    action-to-phenomenology mapping. Therefore this function returns constant-amplitude arrays
    for mu and Sigma evaluated on the provided redshift grid.

    Inputs:
      - A_mu, A_Sigma: phenomenological amplitudes (no redshift dependence assumed here)
      - z: scalar or array-like of redshifts at which to report the amplitudes

    Returns:
      - mu(z) array, Sigma(z) array (both same shape as np.atleast_1d(z)) filled with constants
    """
    z_arr = np.atleast_1d(z).astype(float)
    mu = np.full_like(z_arr, float(A_mu))
    Sigma = np.full_like(z_arr, float(A_Sigma))
    return mu, Sigma


def action_to_phenomenology_mapping(action_params: Mapping[str, float]) -> Tuple[float, float]:
    """
    Placeholder per paper constraints: The note states that the action-level EFC parameters
    (K0, V', alpha) are not in one-to-one correspondence with phenomenological (A_mu, A_Sigma),
    and that this mapping is a separate open task flagged in a companion paper.

    This function intentionally raises NotImplementedError to reflect the paper's explicit status.
    """
    raise NotImplementedError(
        "Action-to-phenomenology mapping (K0, V', alpha) -> (A_mu, A_Sigma) is a separate open task per Magnusson 2026 and is not defined here."
    )


def rcmp_problem_definition(measurement_name: str, regime: Union[int, str], proxy_dependencies: Iterable[str]) -> str:
    """
    Compose an RCMP-compliant conclusion in the "problem definition, not resolution" style.

    Returns a sentence describing what can be reported given the specified regime tag and
    explicit proxy-chain dependencies.
    """
    lvl, lab = regime_level(regime)
    proxies = ", ".join(sorted(set(map(str, proxy_dependencies)))) if proxy_dependencies else "none"
    return (
        f"Under RCMP, the reportable status for '{measurement_name}' at {lab} (level {lvl}) is a problem definition: "
        f"quantities are conditional on proxies [{proxies}], with interpretation confined to the declared regime."
    )


if __name__ == "__main__":
    # Self-test demonstrating the main numerical content available in the note
    print("Magnusson (2026) RCMP/Convergence: minimal numeric self-test")

    # 1) RCMP compliance demo
    checks = {
        "driver_proximity": True,
        "regime_tagging": True,
        "proxy_accounting": True,
        "coordinate_humility": True,
        "cross_validation": True,
    }
    compliance = rcmp_compliance(checks)
    print("RCMP compliance:", compliance)

    # 2) S8 tension sensitivity under IA-model choice (DES Y6, per note)
    des = PAPER_NUMERICS["cosmic_shear_observation"]["des_y6_s8_tension"]  # type: ignore[index]
    metrics = s8_significance_metrics(des["nla_sigma_range"], des["tatt_sigma"])  # type: ignore[index]
    print("DES Y6 S8-tension metrics:")
    for k in ["nla_min", "nla_max", "nla_mean", "nla_width", "tatt", "reduction_abs", "reduction_frac"]:
        print(f"  {k}: {metrics[k]}")

    # 3) Phenomenological amplitudes as constants across z (no mapping provided in note)
    z = np.linspace(0.0, 2.0, 5)
    mu_arr, Sigma_arr = mu_sigma_amplitudes(1.0, 1.0, z)
    print("mu(z) first->last:", float(mu_arr[0]), float(mu_arr[-1]))
    print("Sigma(z) first->last:", float(Sigma_arr[0]), float(Sigma_arr[-1]))

    # 4) RCMP-style problem definition sentence
    sentence = rcmp_problem_definition(
        measurement_name="S8 from cosmic shear (DES Y6)",
        regime="L2",
        proxy_dependencies=["baryonic_feedback_model", "intrinsic_alignment_model"],
    )
    print(sentence)
