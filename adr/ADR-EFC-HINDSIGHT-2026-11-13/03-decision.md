# Decision

Implement one fail-closed compatibility adapter for the three page operations. Prefer documented Pages names (`get_page_tree`, `create_page_folder`, `create_page`) and fall back to installed legacy names (`get_knowledge_base_tree`, `create_knowledge_folder`, `create_knowledge_page`). Resolve all needed operations before any write; an unknown client fails closed.

Treat all HTTP 2xx responses as transport success, including 204; always GET the config and verify exact returned values before proceeding to directives/pages. A non-2xx response or mismatched readback stops downstream writes.

Add `_mission_additions` to the repo spec for the missing instructions. Merge each addition into the live bank-authored mission idempotently, preserving its exact existing text. Keep current default mission values for fresh-bank initialization and preserve `--replace-missions` as explicit full replacement.

Keep all label definitions. Their meanings are distinct despite shared L0–L3 terms. Do not run reprocess, bulk PATCH, or any historical write. The measured malformed entity examples make migration a real outstanding issue, but no safe, semantically reliable bulk correction is established.

**Human/production gate:** critical configuration/data-boundary change. No production bank write or merge before independent review, green gates, and explicit owner approval. Status remains proposed until those gates are satisfied.
