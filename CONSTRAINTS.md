# CONSTRAINTS

> Mirrors `docs/superpowers/specs/2026-05-04-moat-research-design.md` §3. If you change this file, also update the spec.

The following are **automatic disqualifiers** during scoring and must be re-checked at the init-prompt step:

1. Anything requiring authentication-bypass or CFAA-adjacent activity.
2. Anything requiring a request rate that violates published rate limits, robots.txt, or upstream ToS.
3. Anything requiring ongoing un-automatable human labor (curation, sales motion, partnerships) that a solo operator cannot sustain.
4. Anything that, in aggregate across the swarm, would constitute a DDOS-grade load against any single source. The orchestrator throttles the *whole swarm*, not just per-service.
5. **No-moat reconstructibility.** Anything whose dataset or derived artifact can be reconstructed later by any analyst from currently-public archived sources. Lane-1 ("ephemeral public data") fails this test if the publisher or any third party archives the source at the cadence the brief depends on. Lane-3 ("cross-source fusion") fails this test if both raw inputs are publicly archived with timestamps and historical access (the join is then reconstructible by anyone). A brief failing this test must score Defensibility=0 (financial sub-criterion), which triggers axis-zero → composite-zero → auto-reject. Verification of source ephemerality / archive completeness is mandatory before brief authoring; if it cannot be confirmed, the wishlist entry is dismissed rather than promoted.

A brief that scores `0` on any axis is auto-routed to `rejected/`.
