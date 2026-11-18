# Decision

**Implemented in this branch; full run matrix and independent review remain pending.**

For `pipelines/efc/native_v2_graph`, implement a conservative finite-volume-style discretization of generic continuum AQUAL:

1. Adopt and document one conventional potential sign, with gravitational acceleration explicitly defined from it. For the standard convention `∇²Φ=4πGρ`, `g=-∇Φ`, and the graph stencil `L=D-A`, derive `LΦ=-4πGρh²` (subject to the tests confirming the code's exact operator and sign).
2. Reconstruct a physical node gradient from centered differences (one-sided at the outermost boundary as needed); use a symmetric face value such as `g_face=(g_i+g_j)/2` for the constitutive norm. The edge-normal derivative remains `(Φ_j-Φ_i)/h`. The `mu` weight is `mu(|g_face|/a0)`, not `mu(|ΔΦ|/(a0h))` on each edge component.
3. Build a node-sampled uniform source density with the declared discrete measure `sum_i rho_i h^3=M` for each source. Retain strict `r<r_source` support unless a boundary test demonstrates a better documented convention. Apply the field-equation `h²` factor explicitly.
4. Return the physical vector gradient and acceleration with an explicit sign; do not repair only radial profiles or the final `C` value.
5. Preserve current boundary behavior in the primary matrix and fix physical box size and radial bins across resolutions. Report analytic-boundary variants separately if tested.
6. Keep the DGS paper operator and the Lambda-locked mechanism outside this code patch; report the Native v2 change as a continuum-calibrated solver variant, not a physical EFC result.
7. Document the actual boundary treatment: the Dirichlet condition applies only to the spherical margin shell `r > r_max - boundary_margin*h` (the `boundary_mask`), while outer cube faces are graph-truncated (fewer neighbours) and are NOT Dirichlet-pinned. This is pre-existing solver behaviour, preserved and now stated in the KT6 metadata and this ADR rather than left implicit.
8. Guard the discrete mass measure: a source whose support overlaps the Dirichlet boundary mask is rejected at solve time (`reject_source_on_boundary` raises `ValueError`), and both solvers return the measured `active_source_mass` on non-boundary rows, so the `sum rho h³ = M` claim can never silently overstate the mass that actually enters the solved equation.

The decision is conditional on RED tests confirming the relevant behavior and on the independent review accepting the face-gradient discretization. If diagonal-field or flux-conservation tests reject it, stop and revise this ADR before broad implementation.
