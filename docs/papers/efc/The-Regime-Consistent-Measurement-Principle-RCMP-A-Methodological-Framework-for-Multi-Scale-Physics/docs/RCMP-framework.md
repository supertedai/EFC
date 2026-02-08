# RCMP Framework Specification

## Complete Documentation of the Regime-Consistent Measurement Principle

### 1. Formal Definition

**English:**
> An observable must be interpreted through the variable most directly coupled to the physical driver in the phenomenon's operative regime. Cross-regime mappings require explicit transformation and uncertainty propagation.

**Norwegian:**
> En observabel skal tolkes gjennom den variabelen som er mest direkte koblet til den fysiske driveren i fenomenets operative regime. Kryss-regime-mapping krever eksplisitt transformasjon og usikkerhetsføring.

### 2. The Five Core Principles

#### 2.1 Driver Proximity

**Definition:** Choose the most directly coupled observable within the operative regime.

**Rationale:** Variables that are closer to the physical driver in the causal chain introduce fewer assumptions and uncertainties.

**Application:**
- In galaxy dynamics where gravity is the driver, use acceleration-based variables
- Avoid mass-based proxies that require additional modeling assumptions
- Identify the causal distance between observable and driver

**Mathematical formulation:**
$$V^* = \arg\min_i d(V_i, D | R)$$

where:
- $V_i$ = candidate interpretive variables
- $D$ = physical driver
- $R$ = operative regime
- $d(\cdot)$ = epistemic distance function

#### 2.2 Regime Tagging

**Definition:** Each measurement must be labeled with its dominant regime(s).

**Implementation:** Use the L0-L3 epistemic hierarchy:

| Layer | Description | Characteristics |
|-------|-------------|-----------------|
| L0 | Direct measurement | Raw sensor output, minimal processing |
| L1 | Calibrated observable | Instrument corrections applied |
| L2 | Derived quantity | Computed from L1 via physical models |
| L3 | Theoretical construct | Inferred from L2 via theoretical framework |

**Requirements:**
- Every data point carries explicit layer tag
- Regime boundaries are documented
- Mixed-regime data is flagged for special handling

#### 2.3 Proxy Accounting

**Definition:** Each transformation from measurement to interpretation carries an explicit uncertainty budget entry.

**Documentation requirements:**
1. Raw measurement uncertainty ($\sigma_0$)
2. Calibration uncertainty ($\sigma_{cal}$)
3. Model-dependent uncertainty ($\sigma_{model}$)
4. Transformation uncertainty ($\sigma_{trans}$)

**Propagation formula:**
$$\sigma_{total} = \sqrt{\sum_i \sigma_i^2 + \sum_{i<j} 2\rho_{ij}\sigma_i\sigma_j}$$

where $\rho_{ij}$ captures correlations between uncertainty sources.

#### 2.4 Coordinate Humility

**Definition:** Global coordinates may be background (fixed reference) in some regimes but dynamic (physically meaningful) in others.

**Implications:**
- Coordinate choice affects interpretation
- Some coordinates are epistemically privileged in certain regimes
- Cross-regime comparisons may require coordinate transformation

**Examples:**
- Cartesian vs. spherical coordinates in galactic dynamics
- Comoving vs. physical coordinates in cosmology
- Lab frame vs. center-of-mass frame in particle physics

#### 2.5 Cross-Validation

**Definition:** Consistency must be tested across different proxy chains.

**Protocol:**
1. Identify independent measurement pathways
2. Compute conclusions from each pathway separately
3. Compare results with appropriate statistical tests
4. Document convergence or divergence

**Interpretation:**
- Convergence → increased confidence
- Divergence → informative about systematic effects

### 3. Regime-Dependent Validity

Physical theories have regimes of validity. RCMP formalizes requirements for respecting these boundaries.

#### 3.1 Regime Boundaries

Regimes are defined by:
- Physical scale (quantum ↔ classical)
- Energy scale (low ↔ high)
- Field strength (weak ↔ strong)
- Velocity (non-relativistic ↔ relativistic)

#### 3.2 Cross-Regime Rules

When measurements span regime boundaries:

1. **Identify boundary location** in parameter space
2. **Apply regime-specific models** on each side
3. **Document matching conditions** at boundary
4. **Propagate uncertainties** through transition

### 4. Mathematical Formalization

#### 4.1 Notation

| Symbol | Meaning |
|--------|---------|
| $O$ | Raw observable |
| $V_i$ | Candidate interpretive variable |
| $D$ | Physical driver in regime $R$ |
| $d(V_i, D \| R)$ | Epistemic distance from $V_i$ to $D$ |
| $T_{ij}$ | Transformation from $V_i$ to $V_j$ |
| $\sigma_{T_{ij}}$ | Uncertainty introduced by transformation |

#### 4.2 Primary Variable Selection

$$V^* = \arg\min_i d(V_i, D | R)$$

#### 4.3 Transformation Requirement

For any $V_j \neq V^*$, interpretation requires:

1. Explicit transformation: $T_{*j}: V^* \to V_j$
2. Propagated uncertainty: $\sigma_{total} = \sqrt{\sigma_O^2 + \sigma_{T_{*j}}^2}$

#### 4.4 Cross-Regime Mapping

For regime $R' \neq R$:

1. Identify $D'$ and $V'^*$ in $R'$
2. Document regime boundary conditions
3. Apply inter-regime transformation with explicit assumptions

### 5. Validation Checklist

| Item | Requirement | Verification |
|------|-------------|--------------|
| Driver identified | Physical driver explicit for each regime | Document driver and coupling |
| Regime tagged | Each data point labeled with dominant regime | Check layer assignments |
| Proxy chain documented | Full transformation sequence recorded | Review chain completeness |
| Uncertainties propagated | Each transformation adds to error budget | Verify uncertainty math |
| Cross-validation performed | Multiple proxy chains compared | Check for consistency |

### 6. Relationship to Other Frameworks

#### 6.1 Uncertainty Quantification
RCMP complements UQ by structuring where uncertainties originate. UQ provides the math; RCMP provides the epistemology.

#### 6.2 Model Selection Criteria
RCMP is pre-theoretical—it applies before model comparison. It ensures fair comparison by standardizing measurement interpretation.

#### 6.3 Dimensional Analysis
RCMP addresses interpretive choices beyond unit consistency. Variables may have correct units but inappropriate epistemic status.

### 7. Pre-Theoretical Nature

RCMP does not favor any particular physical theory. It:
- Applies equally to ΛCDM, MOND, and alternatives
- Makes theoretical assumptions explicit
- Identifies where theories disagree about primary variables
- Enables theory-neutral data analysis

Different theories may identify different drivers—this disagreement is itself informative and testable.

---

*Reference: Magnusson, M. (2026). The Regime-Consistent Measurement Principle (RCMP). DOI: 10.6084/m9.figshare.31222900*
