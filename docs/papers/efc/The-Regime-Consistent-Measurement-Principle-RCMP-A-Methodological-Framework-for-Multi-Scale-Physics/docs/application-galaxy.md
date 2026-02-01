# Application: Galaxy Rotation Curves

## RCMP-Guided Analysis of the Radial Acceleration Relation

### 1. The Problem

Galaxy rotation curves exhibit a tight relationship between:
- **Observed centripetal acceleration** ($g_{obs}$)
- **Baryonic acceleration** ($g_{bar}$) - predicted from visible matter

This is the **Radial Acceleration Relation (RAR)** (McGaugh et al., 2016).

However, scatter in this relation varies:
- Higher scatter at low accelerations ($g_{bar} < 10^{-11}$ m/s²)
- Particularly pronounced in dwarf galaxies

### 2. Competing Interpretations

Without RCMP, interpretations are often conflated:

| Interpretation | Claim | Proxy Chain |
|----------------|-------|-------------|
| Measurement systematics | Scatter from distance/inclination errors | L0→L1 |
| Kinematic effects | Non-circular motions, pressure support | L1→L2 |
| Intrinsic physics | Additional degrees of freedom in response | L2→L3 |

**Problem:** These occur at different epistemic layers but are compared directly.

### 3. RCMP-Guided Analysis

#### Step 1: Driver Identification

In the low-acceleration regime:
- **Driver:** Gravitational response to baryonic mass
- **Primary variable:** Acceleration (L2)
- **Justification:** Gravity couples directly to acceleration, not mass proxies

```python
driver = {
    "name": "gravitational_response",
    "regime": "low_acceleration",
    "boundary": "g_bar < 1e-11 m/s²",
    "primary_variable": "acceleration"
}
```

#### Step 2: Regime Tagging

Data points tagged by:
1. **Acceleration regime:** High-g vs. Low-g
2. **Quality flag:** Q = 1 (highest quality) for primary analysis
3. **Galaxy type:** Spiral vs. Dwarf

```python
for point in sparc_data:
    point.regime = "low_g" if point.g_bar < 1e-11 else "high_g"
    point.quality = point.Q_flag
    point.galaxy_type = "dwarf" if point.T >= 8 else "spiral"
```

#### Step 3: Proxy Accounting

The transformation chain from velocity to acceleration:

| Step | Transformation | Uncertainty Source |
|------|----------------|-------------------|
| V_obs → V_rot | Inclination correction | Inc, eInc |
| V_rot → g_obs | $g = V^2/R$ | Distance (affects R) |
| Photometry → g_bar | Mass-to-light ratio | M/L calibration |

**Documented proxy chain:**
```json
{
  "chain": [
    {"from": "V_obs", "to": "V_rot", "uncertainty_params": ["Inc", "eInc"]},
    {"from": "V_rot", "to": "g_obs", "uncertainty_params": ["D", "eD"]},
    {"from": "L_3.6", "to": "g_bar", "uncertainty_params": ["M/L_disk", "M/L_bulge"]}
  ]
}
```

#### Step 4: Analysis Structure Separation

**Critical RCMP insight:** Separate analysis levels:

| Level | Analysis | Tests |
|-------|----------|-------|
| **Per-point** | All individual data points | Internal structure, measurement effects |
| **Per-galaxy** | Median residual per galaxy | Class-level physics, systematic offsets |

### 4. Results

#### 4.1 Per-Point vs. Per-Galaxy Analysis

| Finding | Per-Point | Per-Galaxy |
|---------|-----------|------------|
| Dwarf vs. spiral scatter | **1.27× higher** (p = 0.02) | **Identical** (p = 0.47) |
| Interpretation | Intra-galaxy variability | No class-level offset |

**Resolution:** Dwarf galaxies show more internal variability (per-point), but their median response follows the same law as spirals (per-galaxy).

#### 4.2 Systematic Hypothesis Tests

| Hypothesis | Proxy Tested | Result | Holm p |
|------------|--------------|--------|--------|
| High-frequency kinematic noise | Roughness ratio | Not supported | > 0.15 |
| Outer-disk systematic | Radius trend | Not supported | > 0.15 |
| Pressure support | V_flat correlation | Wrong sign | - |
| Distance uncertainty | eD correlation | **Supported** | 0.035 |

#### 4.3 RCMP Validation Checklist

| Item | Status | Evidence |
|------|--------|----------|
| Driver identified | ✓ | Gravitational response in low-g regime |
| Regime tagged | ✓ | High-g/Low-g + Q-flag + galaxy type |
| Proxy chain documented | ✓ | Inc → D → M/L chain recorded |
| Uncertainties propagated | ✓ | eD correlation quantified |
| Cross-validation | ✓ | Per-point vs. per-galaxy comparison |

### 5. RCMP-Compliant Conclusion

Following RCMP, the epistemologically valid statement is:

> "The low-acceleration manifold is real at the galaxy level. Excess scatter in dwarfs is internal and low-frequency. Distance uncertainty explains some amplitude variation. High-frequency kinematic and simple pressure-support explanations are disfavored. A weak V_flat anomaly remains unexplained."

**This is a problem definition, not a conclusion.**

It maps the boundary between:
- ✓ **Explained:** Distance uncertainty contribution
- ✓ **Ruled out:** High-frequency kinematic noise, pressure support
- ✗ **Open:** V_flat–median residual correlation

### 6. Code Implementation

```python
from src.rcmp_validator import RCMPValidator
from src.regime_tagger import RegimeTagger
from src.proxy_chain import ProxyChain

# Load SPARC data
sparc = load_sparc_data()

# Tag regimes
tagger = RegimeTagger()
for galaxy in sparc.galaxies:
    for point in galaxy.points:
        point.regime = tagger.classify(point.g_bar, threshold=1e-11)

# Document proxy chain
chain = ProxyChain()
chain.add_step("V_obs", "L0", sigma=0.01)
chain.add_step("V_rot", "L1", sigma=0.02,
               transformation="inclination_correction",
               params=["Inc", "eInc"])
chain.add_step("g_obs", "L2", sigma=0.05,
               transformation="g = V²/R",
               params=["D", "eD"])

# Per-point analysis
per_point_scatter = compute_scatter(sparc.all_points, by="galaxy_type")

# Per-galaxy analysis
per_galaxy_scatter = compute_scatter(sparc.galaxy_medians, by="galaxy_type")

# Statistical tests with multiplicity correction
tests = [
    ("eD_correlation", correlate(sparc.eD, sparc.residual_amplitude)),
    ("roughness_ratio", compare_roughness(sparc.dwarfs, sparc.spirals)),
    ("Vflat_correlation", correlate(sparc.Vflat, sparc.median_residual))
]
adjusted_p = holm_bonferroni(tests)

# Validate RCMP compliance
validator = RCMPValidator()
result = validator.validate(
    driver=driver,
    proxy_chain=chain,
    analyses={"per_point": per_point_scatter, "per_galaxy": per_galaxy_scatter}
)

print(result.summary())
```

### 7. Lessons for Other Domains

The RCMP approach demonstrated here applies wherever:
- Measurements span multiple regimes
- Multiple proxy chains exist
- Per-instance vs. per-class effects need separation

**Examples:**
- CMB anisotropy analysis (per-mode vs. per-patch)
- Particle physics (per-event vs. per-experiment)
- Climate science (per-station vs. per-region)

---

*Reference: Magnusson (2026), Section 4 and Appendix A*
*Data: SPARC Database (Lelli et al., 2017)*
