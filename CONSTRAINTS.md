# CONSTRAINTS

> Mirrors `docs/superpowers/specs/2026-05-04-moat-research-design.md` §3. If you change this file, also update the spec.

The following are **automatic disqualifiers** during scoring and must be re-checked at the init-prompt step:

1. Anything requiring authentication-bypass or CFAA-adjacent activity.
2. Anything requiring a request rate that violates published rate limits, robots.txt, or upstream ToS.
3. Anything requiring ongoing un-automatable human labor (curation, sales motion, partnerships) that a solo operator cannot sustain.
4. Anything that, in aggregate across the swarm, would constitute a DDOS-grade load against any single source. The orchestrator throttles the *whole swarm*, not just per-service.
5. **No-moat reconstructibility.** Anything whose dataset or derived artifact can be reconstructed later by any analyst from currently-public archived sources. Lane-1 ("ephemeral public data") fails this test if the publisher or any third party archives the source at the cadence the brief depends on. Lane-3 ("cross-source fusion") fails this test if both raw inputs are publicly archived with timestamps and historical access (the join is then reconstructible by anyone). A brief failing this test must score Defensibility=0 (financial sub-criterion), which triggers axis-zero → composite-zero → auto-reject. Verification of source ephemerality / archive completeness is mandatory before brief authoring; if it cannot be confirmed, the wishlist entry is dismissed rather than promoted.

A brief that scores `0` on any axis is auto-routed to `rejected/`.

## Discovery: Akamai-gated federal endpoints

When a federal agency endpoint returns HTTP 403 during discovery, do **not** dismiss immediately. Apply the 3-step polite-alternate-path checklist (see `.wolf/cerebrum.md` "Akamai-edge UA gating" entry) before finalizing dismissal:

1. **data.gov bulk mirror** — search `catalog.data.gov` for the agency + topic; bulk downloads often bypass the Akamai-gated Drupal front-end.
2. **FOIA reading room** — check `<domain>/foia` or `<domain>/about/foia-reading-room` for proactively-released datasets.
3. **Direct subdomain / alternate domain** — try program-office subdomains, `api.<agency>.gov`, or individual member-agency sites for multi-regulator portals.

Document which steps were attempted and their HTTP status. Dismiss with revisit trigger only after all three steps fail. Four confirmed Akamai-gated endpoints as of 2026-05-05: FAA Aircraft Registry (registry.faa.gov), DOL WHD (dol.gov/agencies/whd), PHMSA (phmsa.dot.gov), FFIEC CRA portal (ffiec.gov) — see WISHLIST.md Notes for per-endpoint alternate-path outcomes.
