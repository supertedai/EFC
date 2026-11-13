# Independent review record

**Reviewer:** delegated fresh-context reviewer `sa-0-7a2b2a83`. **Route/model:** delegated GPT-6 Luna review. **Model verified:** delegated route completed; treat as independent review evidence, not a GitHub approval.

## Initial findings
- **REQUEST_CHANGES:** mixed SDK/REST config writes could partially apply if the direct client update succeeded before a failed REST PATCH.
- Documentation incorrectly said `physical_regime` and `rcmp_regime` both use L0–L3, conflicting with the measured live `physical_regime` definition (`S_flow`/`S_trans`/`S_latent`).

## Disposition
Both findings were fixed before the follow-up review round: when any field needs REST, the complete change set now uses one REST request, and the README distinguishes the repository target from the measured live definition. Added regression test `test_mixed_client_and_rest_fields_do_not_partially_write`. Focused suite after the fixes: 11 passed. A fresh review round is required before merge.
