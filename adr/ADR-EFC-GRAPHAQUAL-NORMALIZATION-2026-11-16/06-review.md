# Independent review record

**Reviewer:** pending. **Route/model:** pending. **Model verified:** pending.

Review must receive this ADR, the exact diff and test outputs. It must independently inspect the discrete derivation and answer:

1. Is the face reconstruction for `mu(|∇Φ|/a0)` consistent with a conservative cubic finite-volume discretization, including diagonal linear fields?
2. Are signs, `h²` scaling, source mass measure, boundary treatment and Gauss-flux accounting internally consistent?
3. Do the tests detect the original defects and fail under mutants (missing source normalization, missing `h²`, edge-component `mu`, unnormalized gradient)?
4. Are A/B/C/D runs genuinely one-factor/combined comparisons with common physical bins and target mass?
5. Are generic AQUAL, the historical DGS edge model and Lambda-locked EFC kept separate in all claims?
6. Is rollback and exact-head readback adequate?

**Initial findings:** pending.

**Disposition:** pending; no self-approval.
