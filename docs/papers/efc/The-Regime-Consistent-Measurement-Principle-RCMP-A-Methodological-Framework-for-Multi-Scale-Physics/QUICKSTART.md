# RCMP Quick Start Guide

## What is RCMP?

The **Regime-Consistent Measurement Principle** is a methodological guard against regime-mixing errors in multi-scale physics. It ensures measurements are interpreted through the most appropriate variables within their operative regime.

## The Five Core Principles

### 1. Driver Proximity
Choose the observable most directly coupled to the physical driver.

**Example:** In galaxy dynamics where gravity is the driver, use acceleration-based variables rather than mass-based proxies that require additional modeling assumptions.

### 2. Regime Tagging
Label each measurement with its epistemic layer (L0-L3):

| Layer | Type | Example |
|-------|------|---------|
| L0 | Direct measurement | Spectral line velocity |
| L1 | Calibrated observable | Rotation velocity V(R) |
| L2 | Derived quantity | Centripetal acceleration |
| L3 | Theoretical construct | Dark matter density |

### 3. Proxy Accounting
Document the full transformation chain:

```
Raw Data (L0) → Calibration → Observable (L1) → Derivation → Quantity (L2)
     ↓              ↓              ↓                ↓            ↓
   σ_raw        σ_calib        σ_obs           σ_deriv      σ_total
```

Each step adds to the uncertainty budget.

### 4. Coordinate Humility
Recognize that coordinate systems may be:
- **Background** (fixed reference) in some regimes
- **Dynamic** (physically meaningful) in others

The choice is not epistemically neutral.

### 5. Cross-Validation
Test consistency across independent proxy chains. Divergence between pathways is informative.

## Quick Implementation

### Step 1: Identify the Driver

```python
# Define what drives the phenomenon in your regime
driver = {
    "name": "gravitational_response",
    "regime": "low_acceleration",
    "boundary": "g_bar < 1e-11 m/s²"
}
```

### Step 2: Tag Your Measurements

```python
from src.regime_tagger import RegimeTagger

tagger = RegimeTagger()

# Tag each measurement
measurements = [
    {"value": 125.3, "type": "velocity", "layer": "L1"},
    {"value": 2.3e-11, "type": "acceleration", "layer": "L2"},
]

for m in measurements:
    regime = tagger.classify(m, driver)
    print(f"{m['type']}: {regime}")
```

### Step 3: Document Proxy Chain

```python
from src.proxy_chain import ProxyChain

chain = ProxyChain()

# Add each transformation step
chain.add_step(
    name="spectral_measurement",
    layer="L0",
    sigma=0.005,
    description="Raw spectral line velocity"
)

chain.add_step(
    name="rotation_velocity",
    layer="L1",
    sigma=0.02,
    transformation="inclination_correction",
    assumptions=["thin disk", "circular orbits"]
)

chain.add_step(
    name="centripetal_acceleration",
    layer="L2",
    sigma=0.05,
    transformation="g = V²/R",
    assumptions=["distance estimate"]
)

# Get total propagated uncertainty
print(f"Total σ: {chain.total_uncertainty()}")
print(f"Proxy depth: {chain.depth()}")
```

### Step 4: Validate RCMP Compliance

```python
from src.rcmp_validator import RCMPValidator

validator = RCMPValidator()

result = validator.validate(
    driver=driver,
    proxy_chain=chain,
    measurements=measurements
)

# Check validation status
print(f"Valid: {result.is_valid}")
for item in result.checklist:
    status = "✓" if item.passed else "✗"
    print(f"  {status} {item.name}: {item.message}")
```

## RCMP Validation Checklist

Before publishing results, verify:

- [ ] **Driver identified** - Physical driver explicit for each regime
- [ ] **Regime tagged** - Each data point labeled with dominant regime
- [ ] **Proxy chain documented** - Full transformation sequence recorded
- [ ] **Uncertainties propagated** - Each transformation adds to error budget
- [ ] **Cross-validation performed** - Multiple proxy chains compared

## Common Pitfalls

### 1. Implicit Regime Mixing
**Wrong:** Comparing measurements from regime A with predictions calibrated in regime B.

**Right:** Apply explicit transformation rules when crossing regime boundaries.

### 2. Hidden Proxy Assumptions
**Wrong:** Treating derived quantities as if they were direct measurements.

**Right:** Document every assumption in the proxy chain.

### 3. Conflating Analysis Levels
**Wrong:** Using per-point scatter to draw conclusions about inter-system physics.

**Right:** Separate per-point analysis (internal structure) from per-system analysis (class-level physics).

## Example Output

```
RCMP Validation Report
======================
Driver: gravitational_response (low_acceleration regime)
Proxy Chain Depth: 3 layers (L0 → L1 → L2)
Total Uncertainty: σ = 0.054 (propagated)

Checklist:
  ✓ Driver identified: gravitational_response
  ✓ Regime tagged: low_acceleration (g < 1e-11 m/s²)
  ✓ Proxy chain: 3 steps documented
  ✓ Uncertainties: properly propagated
  ✗ Cross-validation: single chain only

Status: PARTIAL - add alternative proxy chain for full validation
```

## Next Steps

1. Read the [full framework documentation](docs/RCMP-framework.md)
2. Explore the [galaxy rotation curve example](docs/application-galaxy.md)
3. Review [epistemic layer definitions](docs/epistemic-layers.md)
4. Run the [worked example](examples/rcmp_galaxy_analysis.py)

---

*For questions or contributions, see the main [README](README.md).*
