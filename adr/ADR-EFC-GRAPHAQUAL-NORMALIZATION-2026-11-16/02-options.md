# Options considered

## Observable gradient

1. Leave the current six-neighbor sum — rejected for a physical vector observable: it returns twice the axis gradient on an interior cubic node.
2. Divide only the reported `g` by two — rejected as a complete fix: it leaves the nonlinear field solve and its constitutive coefficient untouched.
3. Implement a sign-explicit central vector gradient, test axis/diagonal/quadratic fields, and define the gravitational acceleration from the chosen potential convention — selected for the observable.

## AQUAL constitutive law

1. Keep `mu(|ΔΦ|/(a0*h))` independently on each edge and call it continuum AQUAL — rejected: on diagonal fields this uses one component rather than the full local gradient norm.
2. Apply a blind `1/2` to every edge derivative — rejected: a directional face derivative `ΔΦ/h` is not the six-neighbor vector-gradient estimator.
3. Use directional `ΔΦ/h` for normal face flux and a symmetric reconstructed full-vector gradient norm (average of endpoint gradients) for `mu`; validate isotropy with axis/diagonal linear fields — selected for the continuum-calibrated Native v2 solver.
4. Replace the graph formulation wholesale with an unrelated external solver — rejected for this bounded change.

## Source measure and scale

1. Keep continuous sphere density sampled at nodes without a discrete mass readback — rejected for a solver advertised in physical `M` and `h` units.
2. Normalize node density so `sum_i rho_i*h^3=M`, then use the derived finite-volume relation for `L=D-A` and the source `h^2` factor — selected as an explicit continuum-mesh convention. The ADR must state that this is not a derivation of the fundamental graph's ontology.
3. Use cut-cell/sphere-intersection weights — retained as a possible higher-accuracy alternative; not selected unless the source-normalization tests show uniform node-cell weights are insufficient for acceptance.
4. Invent a graph node measure — rejected until a separately derived measure exists.

## Potential, sign, and boundaries

1. Preserve the current implicit sign convention — rejected because it obscures the relation between `L=D-A`, Poisson source sign, and `g`.
2. Select a conventional potential/acceleration convention, derive `L≈-h^2∇²`, and encode it in tests — selected. Keep the existing Dirichlet boundary rule for the primary A/B/C/D comparison; any alternate analytic boundary condition is a separately labeled sensitivity check.

## Scope boundary

Preserve the DGS paper/package edge rule as a distinct historical graph model for this change. The corrected Native v2 solver is a generic continuum-calibrated AQUAL implementation; do not retroactively change published/specification semantics or claim it proves Lambda locking.
