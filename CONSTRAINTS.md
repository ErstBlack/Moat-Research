# CONSTRAINTS

> Mirrors `docs/superpowers/specs/2026-05-04-moat-research-design.md` §3. If you change this file, also update the spec.

The following are **automatic disqualifiers** during scoring and must be re-checked at the init-prompt step:

1. Anything requiring authentication-bypass or CFAA-adjacent activity.
2. Anything requiring a request rate that violates published rate limits, robots.txt, or upstream ToS.
3. Anything requiring ongoing un-automatable human labor (curation, sales motion, partnerships) that a solo operator cannot sustain.
4. Anything that, in aggregate across the swarm, would constitute a DDOS-grade load against any single source. The orchestrator throttles the *whole swarm*, not just per-service.

A brief that scores `0` on any axis is auto-routed to `rejected/`.
