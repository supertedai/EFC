#!/usr/bin/env python3
"""
Research Policy — typed dataclass hierarchy loaded from YAML.

Single source of truth for all daemon thresholds and behavior.
Mirrors the structure of research_policy.yaml exactly.

Usage:
    policy = ResearchPolicy.from_yaml("efc_inference/configs/research_policy.yaml")
    print(policy.runtime.mcmc.rhat_max)  # 1.05
"""
import os
import yaml
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("research_policy")


# ═══════════════════════════════════════════════════════════════
#  RUNTIME
# ═══════════════════════════════════════════════════════════════

@dataclass
class MCMCConfig:
    """MCMC sampler parameters."""
    nwalkers: int = 48
    nsteps: int = 4000
    burnin: int = 1500
    seed: int = 42
    rhat_max: float = 1.05
    ess_min: int = 800
    acceptance_lo: float = 0.15
    acceptance_hi: float = 0.55
    retry_on_fail: bool = True
    retry_nsteps_multiplier: float = 2.0

@dataclass
class RuntimeConfig:
    """Top-level runtime configuration."""
    cycle_interval_sec: int = 21600
    mcmc: MCMCConfig = field(default_factory=MCMCConfig)


# ═══════════════════════════════════════════════════════════════
#  CASE LIFECYCLE
# ═══════════════════════════════════════════════════════════════

@dataclass
class CaseLifecycleConfig:
    """Case state machine configuration."""
    states: list = field(default_factory=lambda: [
        "OPEN", "RUNNING", "WATCHLIST", "CANDIDATE", "ROBUST", "CLOSED", "ESCALATED"
    ])
    initial_state: str = "OPEN"
    data_hash_determines_case: bool = True


# ═══════════════════════════════════════════════════════════════
#  DATA HYGIENE GATE
# ═══════════════════════════════════════════════════════════════

@dataclass
class DataHygieneGate:
    """Pre-flight data validation before MCMC."""
    enabled: bool = True
    schema_check: bool = True
    unit_sanity: bool = True
    nan_inf_reject: bool = True
    z_range_check: list = field(default_factory=lambda: [0.0, 3.0])
    error_positivity: bool = True
    baseline_sanity_fit: bool = True
    baseline_max_chi2_red: float = 10.0
    baseline_sanity_nsteps: int = 500
    compute_data_hash: bool = True


# ═══════════════════════════════════════════════════════════════
#  INFERENCE GATES
# ═══════════════════════════════════════════════════════════════

@dataclass
class ConvergenceGate:
    """Convergence checks on the MCMC sampler."""
    enabled: bool = True
    rhat_max: float = 1.05
    ess_min: int = 800
    acceptance_lo: float = 0.15
    acceptance_hi: float = 0.55

@dataclass
class SignalTier:
    """Thresholds for a signal tier (hint / candidate / robust)."""
    alpha_sigma_min: float = 0.0
    daic_max: float = 0.0
    p_negative_min: float = 0.0

@dataclass
class ModelComparisonGate:
    """Model comparison thresholds for signal classification."""
    hint: SignalTier = field(default_factory=lambda: SignalTier(
        alpha_sigma_min=1.5, daic_max=0.0, p_negative_min=0.80
    ))
    candidate: SignalTier = field(default_factory=lambda: SignalTier(
        alpha_sigma_min=1.7, daic_max=0.0, p_negative_min=0.90
    ))
    robust: SignalTier = field(default_factory=lambda: SignalTier(
        alpha_sigma_min=2.0, daic_max=-2.0, p_negative_min=0.95
    ))

@dataclass
class DegeneracyConfig:
    """Degeneracy detection thresholds."""
    collapse_sigma: float = 1.3
    max_correlation: float = 0.95

@dataclass
class InferenceGates:
    """All inference gates."""
    convergence: ConvergenceGate = field(default_factory=ConvergenceGate)
    model_comparison: ModelComparisonGate = field(default_factory=ModelComparisonGate)
    degeneracy: DegeneracyConfig = field(default_factory=DegeneracyConfig)


# ═══════════════════════════════════════════════════════════════
#  ROBUSTNESS SUITE
# ═══════════════════════════════════════════════════════════════

@dataclass
class N1Config:
    """N1 rd-control diagnostic configuration."""
    enabled: bool = True
    rd_ci_trigger: float = 20.0

@dataclass
class N2Config:
    """N2 sigma8-sweep diagnostic configuration."""
    enabled: bool = True
    modes: list = field(default_factory=lambda: ["stram", "middels", "flat"])

@dataclass
class T7Config:
    """T7 leave-one-out diagnostic configuration.

    v2: sign-consistency criterion replaces σ-threshold.
    """
    enabled: bool = True
    min_pass: int = 5
    total_points: int = 7
    criterion: str = "sign_consistency"  # v2
    pass_p_negative: float = 0.80        # P(α<0) >= 0.80 per LOO
    strength_strong: float = 0.95
    strength_medium: float = 0.90
    strength_weak: float = 0.80

@dataclass
class N3Config:
    """N3 gate-freedom diagnostic configuration.

    v2: use_aeff enables A_eff reparameterization (breaks α×gate degeneracy).
    """
    enabled: bool = True
    pass_sigma: float = 1.7
    collapse_sigma: float = 1.3
    degeneracy_corr_max: float = 0.80
    use_aeff: bool = True              # v2: A_eff reparameterization
    sweep_grid: list = field(default_factory=lambda: [
        {"label": "early",    "a_t": 0.35, "delta_a": 0.10},
        {"label": "baseline", "a_t": 0.50, "delta_a": 0.10},
        {"label": "late",     "a_t": 0.65, "delta_a": 0.10},
        {"label": "narrow",   "a_t": 0.50, "delta_a": 0.05},
        {"label": "wide",     "a_t": 0.50, "delta_a": 0.20},
    ])

@dataclass
class N4Config:
    """N4 modified-Poisson diagnostic configuration (D1 phase)."""
    enabled: bool = True
    pass_sigma: float = 1.7
    collapse_sigma: float = 1.3
    degeneracy_corr_max: float = 0.80
    mu_prior_mean: float = 1.0
    mu_prior_std: float = 0.3
    sweep_grid: list = field(default_factory=lambda: [
        {"label": "mu_0.80", "mu_0": 0.80},
        {"label": "mu_0.90", "mu_0": 0.90},
        {"label": "mu_1.00", "mu_0": 1.00},
        {"label": "mu_1.10", "mu_0": 1.10},
        {"label": "mu_1.20", "mu_0": 1.20},
    ])

@dataclass
class N5Config:
    """N5 sound horizon prior sweep (D2a phase).

    Tests whether α signal is robust to r_d prior choice.
    Runs 4 configs: tight N(147,2), standard N(147,5), broad N(147,10), flat U(100,200).
    """
    enabled: bool = True
    pass_sigma: float = 1.7
    collapse_sigma: float = 1.3
    degeneracy_corr_max: float = 0.80

@dataclass
class N6Config:
    """N6 EFC sound horizon diagnostic (D2b phase).

    Computes r_d^EFC from grid-state physics (c_eff = c/(1+R)) and compares
    to GR baseline. Runs R_max sensitivity sweep. Safety gate: if the EFC
    correction exceeds the threshold, the diagnostic flags it for review.

    This is a POST-FIT diagnostic: it takes posterior samples from the
    baseline MCMC and computes r_d^EFC for each sample, giving a
    posterior distribution of the EFC correction.
    """
    enabled: bool = True
    R_max: float = 0.01
    sigma_ln_a: float = 0.5
    safety_threshold_pct: float = 0.5
    Omega_b: float = 0.0493
    sweep_R_max: list = field(default_factory=lambda: [
        0.0, 0.001, 0.005, 0.01, 0.02, 0.05
    ])

@dataclass
class N7Config:
    """N7 Global parameter-lock cross-probe test ("Domstolen").

    Couples GRAV sector (G_eff from Graph-AQUAL) into cosmological likelihood.
    Uses EFCVariantF cosmology with frozen C, k_lambda, gate params.
    No rescue μ, no free lensing amplitude.

    Verdict thresholds:
        SURVIVES:  α ≥ survives_sigma AND ΔAIC < survives_daic
        MARGINAL:  α ≥ marginal_sigma AND ΔAIC < marginal_daic
        EXPLODED:  any probe has χ²_red > max_chi2_red
        NO_SIGNAL: otherwise
    """
    enabled: bool = True
    survives_sigma: float = 2.0
    survives_daic: float = -2.0
    marginal_sigma: float = 1.5
    marginal_daic: float = 0.0
    max_chi2_red: float = 5.0
    # GRAV frozen parameters
    C_grav: float = 2.32
    k_lambda: float = 0.0014
    k_eff: float = 0.1
    a_t: float = 0.5
    delta_a: float = 0.1


@dataclass
class D2Config:
    """D2 Self-consistent sound horizon comparison.

    Runs the same MCMC as baseline, but with r_d computed from EFC physics
    (sound_horizon.py) instead of hardcoded Planck proxy (147.09 Mpc).

    Compares α signal between proxy and self-consistent runs.
    If α survives → sound horizon is not a hidden assumption.

    Verdict:
        PASS:      |Δα_sig| < pass_delta_alpha
        MARGINAL:  pass_delta_alpha ≤ |Δα_sig| < 2×pass_delta_alpha
        COLLAPSED: α_sig < 1.0 or |Δα_sig| ≥ 2×pass_delta_alpha
    """
    enabled: bool = True
    R_max: float = 0.01            # EFC grid resistance (fixed postulate)
    safety_threshold_pct: float = 1.0  # max |Δr_d| before rejecting sample
    pass_delta_alpha: float = 0.3  # max |Δα_sig| for PASS verdict

@dataclass
class RobustnessSuite:
    """Robustness diagnostic suite configuration."""
    n1: N1Config = field(default_factory=N1Config)
    n2: N2Config = field(default_factory=N2Config)
    t7: T7Config = field(default_factory=T7Config)
    n3: N3Config = field(default_factory=N3Config)
    n4: N4Config = field(default_factory=N4Config)
    n5: N5Config = field(default_factory=N5Config)
    n6: N6Config = field(default_factory=N6Config)
    n7: N7Config = field(default_factory=N7Config)
    d2: D2Config = field(default_factory=D2Config)


# ═══════════════════════════════════════════════════════════════
#  PPC GATE (Fase 2)
# ═══════════════════════════════════════════════════════════════

@dataclass
class PPCGateConfig:
    """Posterior Predictive Check gate configuration.

    Thresholds for fit quality validation:
    - chi2_red_max: maximum reduced chi-squared
    - p_value_lo/hi: Bayesian p-value range (good fit ≈ 0.5)
    - calibration_1sigma_tol: |obs_fraction - 0.6827| tolerance
    - max_outliers_3sigma: max data points with |residual| > 3σ
    - residual_std_max: max standard deviation of normalized residuals
    """
    enabled: bool = True
    auto_pass: bool = False
    n_posterior_samples: int = 200
    chi2_red_max: float = 3.0
    p_value_lo: float = 0.05
    p_value_hi: float = 0.95
    calibration_1sigma_tol: float = 0.20
    max_outliers_3sigma: int = 3
    residual_std_max: float = 2.0


# ═══════════════════════════════════════════════════════════════
#  DISABLED GATE (SBC — Fase 3)
# ═══════════════════════════════════════════════════════════════

@dataclass
class DisabledGate:
    """Gate that auto-passes. Used for SBC in Fase 1-2."""
    enabled: bool = False
    auto_pass: bool = True


@dataclass
class SBCGateConfig:
    """Simulation-Based Calibration gate configuration.

    SBC validates sampler calibration by checking rank statistics
    and coverage probabilities against expected uniform distributions.
    """
    enabled: bool = False
    auto_pass: bool = True
    n_simulations: int = 50
    nwalkers: int = 24         # reduced for SBC (speed)
    nsteps: int = 1500         # reduced for SBC (speed)
    burnin: int = 500
    ks_p_value_min: float = 0.05
    coverage_68_tol: float = 0.15   # |obs - 0.6827| < tol
    coverage_95_tol: float = 0.10   # |obs - 0.9545| < tol


# ═══════════════════════════════════════════════════════════════
#  STOP CONDITIONS
# ═══════════════════════════════════════════════════════════════

@dataclass
class StopRule:
    """Configuration for a single stop condition."""
    enabled: bool = True
    threshold: float = 0.0
    action: str = "ESCALATE"

@dataclass
class StopConditionsConfig:
    """All stop condition rules."""
    prior_dominance: StopRule = field(default_factory=lambda: StopRule(
        enabled=True, threshold=0.95, action="ESCALATE"
    ))
    no_value: StopRule = field(default_factory=lambda: StopRule(
        enabled=True, threshold=5.0, action="CLOSE"
    ))
    degeneracy_persists: StopRule = field(default_factory=lambda: StopRule(
        enabled=True, threshold=3.0, action="ESCALATE"
    ))
    manual: StopRule = field(default_factory=lambda: StopRule(
        enabled=True, threshold=0.0, action="ESCALATE"
    ))


# ═══════════════════════════════════════════════════════════════
#  PROMOTION RULES
# ═══════════════════════════════════════════════════════════════

@dataclass
class PromotionGates:
    """Required gates for a promotion level."""
    data_hygiene: bool = True
    convergence: bool = True
    signal: bool = True
    robustness: bool = False
    ppc: bool = False
    sbc: bool = False

@dataclass
class PromotionLevel:
    """A single promotion level (e.g., WATCHLIST→CANDIDATE)."""
    from_state: str = ""
    to_state: str = ""
    required_gates: PromotionGates = field(default_factory=PromotionGates)

@dataclass
class PromotionRules:
    """All promotion rules."""
    to_watchlist: PromotionLevel = field(default_factory=lambda: PromotionLevel(
        from_state="RUNNING", to_state="WATCHLIST",
        required_gates=PromotionGates(
            data_hygiene=True, convergence=True, signal=True,
            robustness=False, ppc=False, sbc=False
        )
    ))
    to_candidate: PromotionLevel = field(default_factory=lambda: PromotionLevel(
        from_state="WATCHLIST", to_state="CANDIDATE",
        required_gates=PromotionGates(
            data_hygiene=True, convergence=True, signal=True,
            robustness=True, ppc=False, sbc=False
        )
    ))
    to_robust: PromotionLevel = field(default_factory=lambda: PromotionLevel(
        from_state="CANDIDATE", to_state="ROBUST",
        required_gates=PromotionGates(
            data_hygiene=True, convergence=True, signal=True,
            robustness=True, ppc=True, sbc=True
        )
    ))


# ═══════════════════════════════════════════════════════════════
#  LOGGING
# ═══════════════════════════════════════════════════════════════

@dataclass
class LoggingConfig:
    """Logging and artifact configuration."""
    required_artifacts: list = field(default_factory=lambda: [
        "manifest.json", "summary.json", "baseline_chains.npz",
        "data_hashes.json", "diagnostics.json", "code_commit.txt"
    ])
    neo4j_nodes: list = field(default_factory=lambda: [
        "ResearchCycleResult", "DiagnosticResult", "ResearchCase",
        "DataHygieneResult", "StopCondition"
    ])
    llm_usage: str = "narrative_only"


# ═══════════════════════════════════════════════════════════════
#  TOP-LEVEL POLICY
# ═══════════════════════════════════════════════════════════════

@dataclass
class ResearchPolicy:
    """
    Top-level research policy loaded from YAML.

    Usage:
        policy = ResearchPolicy.from_yaml("path/to/research_policy.yaml")
    """
    version: str = "1.0"
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    case_lifecycle: CaseLifecycleConfig = field(default_factory=CaseLifecycleConfig)
    data_hygiene_gate: DataHygieneGate = field(default_factory=DataHygieneGate)
    inference_gates: InferenceGates = field(default_factory=InferenceGates)
    robustness_suite: RobustnessSuite = field(default_factory=RobustnessSuite)
    ppc_gate: PPCGateConfig = field(default_factory=PPCGateConfig)
    sbc_gate: SBCGateConfig = field(default_factory=SBCGateConfig)
    stop_conditions: StopConditionsConfig = field(default_factory=StopConditionsConfig)
    promotion_rules: PromotionRules = field(default_factory=PromotionRules)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def from_yaml(cls, path: str) -> "ResearchPolicy":
        """Load policy from YAML file."""
        if not os.path.exists(path):
            logger.warning(f"Policy file not found: {path} — using defaults")
            return cls()

        with open(path, 'r') as f:
            raw = yaml.safe_load(f)

        if raw is None:
            logger.warning(f"Empty policy file: {path} — using defaults")
            return cls()

        return cls._from_dict(raw)

    @classmethod
    def _from_dict(cls, d: dict) -> "ResearchPolicy":
        """Recursively build policy from dict."""
        policy_data = d.get("policy", d)

        # Runtime
        rt_raw = policy_data.get("runtime", {})
        mcmc_raw = rt_raw.get("mcmc", {})
        mcmc = MCMCConfig(**{k: v for k, v in mcmc_raw.items() if k in MCMCConfig.__dataclass_fields__})
        runtime = RuntimeConfig(
            cycle_interval_sec=rt_raw.get("cycle_interval_sec", 21600),
            mcmc=mcmc,
        )

        # Case lifecycle
        cl_raw = policy_data.get("case_lifecycle", {})
        _default_cl = CaseLifecycleConfig()
        case_lifecycle = CaseLifecycleConfig(
            states=cl_raw.get("states", _default_cl.states),
            initial_state=cl_raw.get("initial_state", "OPEN"),
            data_hash_determines_case=cl_raw.get("data_hash_determines_case", True),
        )

        # Data hygiene gate
        dh_raw = policy_data.get("data_hygiene_gate", {})
        data_hygiene_gate = DataHygieneGate(
            **{k: v for k, v in dh_raw.items() if k in DataHygieneGate.__dataclass_fields__}
        )

        # Inference gates
        ig_raw = policy_data.get("inference_gates", {})
        conv_raw = ig_raw.get("convergence", {})
        convergence = ConvergenceGate(
            **{k: v for k, v in conv_raw.items() if k in ConvergenceGate.__dataclass_fields__}
        )
        mc_raw = ig_raw.get("model_comparison", {})
        model_comparison = ModelComparisonGate(
            hint=_parse_signal_tier(mc_raw.get("hint", {})),
            candidate=_parse_signal_tier(mc_raw.get("candidate", {})),
            robust=_parse_signal_tier(mc_raw.get("robust", {})),
        )
        deg_raw = ig_raw.get("degeneracy", {})
        degeneracy = DegeneracyConfig(
            **{k: v for k, v in deg_raw.items() if k in DegeneracyConfig.__dataclass_fields__}
        )
        inference_gates = InferenceGates(
            convergence=convergence,
            model_comparison=model_comparison,
            degeneracy=degeneracy,
        )

        # Robustness suite
        rs_raw = policy_data.get("robustness_suite", {})
        n1_raw = rs_raw.get("n1", {})
        n2_raw = rs_raw.get("n2", {})
        t7_raw = rs_raw.get("t7", {})
        n3_raw = rs_raw.get("n3", {})
        n4_raw = rs_raw.get("n4", {})
        n5_raw = rs_raw.get("n5", {})
        n6_raw = rs_raw.get("n6", {})
        n7_raw = rs_raw.get("n7", {})
        robustness_suite = RobustnessSuite(
            n1=N1Config(**{k: v for k, v in n1_raw.items() if k in N1Config.__dataclass_fields__}),
            n2=N2Config(**{k: v for k, v in n2_raw.items() if k in N2Config.__dataclass_fields__}),
            t7=T7Config(**{k: v for k, v in t7_raw.items() if k in T7Config.__dataclass_fields__}),
            n3=N3Config(**{k: v for k, v in n3_raw.items() if k in N3Config.__dataclass_fields__}),
            n4=N4Config(**{k: v for k, v in n4_raw.items() if k in N4Config.__dataclass_fields__}),
            n5=N5Config(**{k: v for k, v in n5_raw.items() if k in N5Config.__dataclass_fields__}),
            n6=N6Config(**{k: v for k, v in n6_raw.items() if k in N6Config.__dataclass_fields__}),
            n7=N7Config(**{k: v for k, v in n7_raw.items() if k in N7Config.__dataclass_fields__}),
        )

        # PPC gate (Fase 2 — full config)
        ppc_raw = policy_data.get("ppc_gate", {})
        _default_ppc = PPCGateConfig()
        ppc_gate = PPCGateConfig(
            enabled=ppc_raw.get("enabled", _default_ppc.enabled),
            auto_pass=ppc_raw.get("auto_pass", _default_ppc.auto_pass),
            n_posterior_samples=ppc_raw.get("n_posterior_samples", _default_ppc.n_posterior_samples),
            chi2_red_max=ppc_raw.get("chi2_red_max", _default_ppc.chi2_red_max),
            p_value_lo=ppc_raw.get("p_value_lo", _default_ppc.p_value_lo),
            p_value_hi=ppc_raw.get("p_value_hi", _default_ppc.p_value_hi),
            calibration_1sigma_tol=ppc_raw.get("calibration_1sigma_tol", _default_ppc.calibration_1sigma_tol),
            max_outliers_3sigma=ppc_raw.get("max_outliers_3sigma", _default_ppc.max_outliers_3sigma),
            residual_std_max=ppc_raw.get("residual_std_max", _default_ppc.residual_std_max),
        )

        # SBC gate (Fase 3 — still disabled)
        sbc_raw = policy_data.get("sbc_gate", {})
        sbc_gate = SBCGateConfig(
            enabled=sbc_raw.get("enabled", False),
            auto_pass=sbc_raw.get("auto_pass", True),
            n_simulations=sbc_raw.get("n_simulations", 50),
            nwalkers=sbc_raw.get("nwalkers", 24),
            nsteps=sbc_raw.get("nsteps", 1500),
            burnin=sbc_raw.get("burnin", 500),
            ks_p_value_min=sbc_raw.get("ks_p_value_min", 0.05),
            coverage_68_tol=sbc_raw.get("coverage_68_tol", 0.15),
            coverage_95_tol=sbc_raw.get("coverage_95_tol", 0.10),
        )

        # Stop conditions
        sc_raw = policy_data.get("stop_conditions", {})
        stop_conditions = StopConditionsConfig(
            prior_dominance=_parse_stop_rule(sc_raw.get("prior_dominance", {}), "ESCALATE", 0.95),
            no_value=_parse_stop_rule(sc_raw.get("no_value", {}), "CLOSE", 5.0),
            degeneracy_persists=_parse_stop_rule(sc_raw.get("degeneracy_persists", {}), "ESCALATE", 3.0),
            manual=_parse_stop_rule(sc_raw.get("manual", {}), "ESCALATE", 0.0),
        )

        # Promotion rules
        pr_raw = policy_data.get("promotion_rules", {})
        promotion_rules = PromotionRules(
            to_watchlist=_parse_promotion_level(pr_raw.get("to_watchlist", {}), "RUNNING", "WATCHLIST"),
            to_candidate=_parse_promotion_level(pr_raw.get("to_candidate", {}), "WATCHLIST", "CANDIDATE"),
            to_robust=_parse_promotion_level(pr_raw.get("to_robust", {}), "CANDIDATE", "ROBUST"),
        )

        # Logging
        log_raw = policy_data.get("logging", {})
        logging_config = LoggingConfig(
            required_artifacts=log_raw.get("required_artifacts", LoggingConfig().required_artifacts),
            neo4j_nodes=log_raw.get("neo4j_nodes", LoggingConfig().neo4j_nodes),
            llm_usage=log_raw.get("llm_usage", "narrative_only"),
        )

        return cls(
            version=policy_data.get("version", "1.0"),
            runtime=runtime,
            case_lifecycle=case_lifecycle,
            data_hygiene_gate=data_hygiene_gate,
            inference_gates=inference_gates,
            robustness_suite=robustness_suite,
            ppc_gate=ppc_gate,
            sbc_gate=sbc_gate,
            stop_conditions=stop_conditions,
            promotion_rules=promotion_rules,
            logging=logging_config,
        )

    def to_research_rules(self) -> "ResearchRulesCompat":
        """Convert to legacy ResearchRules-compatible object for backward compat."""
        return ResearchRulesCompat(
            signal_threshold=self.inference_gates.model_comparison.hint.alpha_sigma_min,
            pass_sigma=self.inference_gates.model_comparison.candidate.alpha_sigma_min,
            pass_daic=self.inference_gates.model_comparison.candidate.daic_max,
            collapse_sigma=self.inference_gates.degeneracy.collapse_sigma,
            loo_min_pass=self.robustness_suite.t7.min_pass,
            rd_ci_trigger=self.robustness_suite.n1.rd_ci_trigger,
        )


@dataclass
class ResearchRulesCompat:
    """Backward-compatible shim matching the old ResearchRules interface."""
    signal_threshold: float = 1.5
    pass_sigma: float = 1.7
    pass_daic: float = 0.0
    collapse_sigma: float = 1.3
    loo_min_pass: int = 5
    rd_ci_trigger: float = 20.0


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def _parse_signal_tier(raw: dict) -> SignalTier:
    """Parse a signal tier from YAML dict."""
    return SignalTier(
        alpha_sigma_min=raw.get("alpha_sigma_min", 0.0),
        daic_max=raw.get("daic_max", 0.0),
        p_negative_min=raw.get("p_negative_min", 0.0),
    )

def _parse_stop_rule(raw: dict, default_action: str, default_threshold: float) -> StopRule:
    """Parse a stop rule from YAML dict."""
    return StopRule(
        enabled=raw.get("enabled", True),
        threshold=raw.get("threshold", default_threshold),
        action=raw.get("action", default_action),
    )

def _parse_promotion_level(raw: dict, from_state: str, to_state: str) -> PromotionLevel:
    """Parse a promotion level from YAML dict."""
    gates_raw = raw.get("required_gates", {})
    return PromotionLevel(
        from_state=raw.get("from_state", from_state),
        to_state=raw.get("to_state", to_state),
        required_gates=PromotionGates(
            data_hygiene=gates_raw.get("data_hygiene", True),
            convergence=gates_raw.get("convergence", True),
            signal=gates_raw.get("signal", True),
            robustness=gates_raw.get("robustness", False),
            ppc=gates_raw.get("ppc", False),
            sbc=gates_raw.get("sbc", False),
        ),
    )
