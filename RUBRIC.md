# RUBRIC

> Mirrors `docs/superpowers/specs/2026-05-04-moat-research-design.md` §5. If you change this file, also update the spec.

Each brief is scored on three axes, each 0–10. Composite = weighted product (zeros kill the brief).

## Financial return (weight 0.4)

Sub-criteria, averaged:

- **Buyer existence** — Identifiable parties who would pay (data brokers, hedge funds, journalists, researchers, vertical SaaS, ad-hoc consulting clients). Concrete > theoretical.
- **Pricing precedent** — Comparable data sells where, at what order of magnitude.
- **Time-to-revenue** — Months until the dataset is valuable enough to monetize.
- **Ongoing revenue potential** — Distinguishes one-shot sales (a frozen archive) from recurring/subscription value (a live feed, an API others depend on, a dataset that compounds). Briefs that score well on *both* one-shot and ongoing get the highest financial mark.
- **Market gap** — Is there a *current, identifiable gap* in what existing providers offer that a solo operator on a single server can fill? A high score requires both (a) no incumbent currently sells this exact thing, *and* (b) the gap is not one an incumbent can plausibly close by minor tweaks to their existing product. A 10 means the gap exists *because* incumbents structurally can't or won't enter; a 0 means the market is either saturated or one product-meeting away from being saturated.
- **Defensibility** — Once acquired, how hard is it for a well-resourced incumbent to catch up. The past being unrecoverable is the strongest form. Distinct from *Market gap*: gap is "is there room today?", defensibility is "once we're in, how long do we hold it?"

## Implementation possibility (weight 0.3)

Sub-criteria, averaged:

- **Source stability** — Likelihood the upstream changes format, adds auth, or shuts down.
- **Legal/ToS risk** — Clearly public > grey area > scraped-against-ToS. Anything violating ToS, rate limits, robots.txt, or applicable law is a hard `0` (and thus a rejection).
- **Solo-operator load** — Ongoing curation, partnerships, or sales. Lower is better.
- **Failure modes** — What breaks if the operator is unavailable for two weeks.

## Hardware fit (weight 0.3)

Sub-criteria, averaged:

- **Storage growth rate** — GB/month vs. 17 TB headroom.
- **Compute profile** — CPU-bound (good, 56 cores), GPU-bound (constrained, P4 shared), RAM-bound (good, 250 GB), I/O-bound (NAS-dependent).
- **Stack fit** — Must be expressible as one or more isolated microservices in a single-node Docker swarm.
- **Concurrency cost** — How many of these can run in parallel before they fight each other or external rate limits.

## Composite

`composite = (financial^0.4) * (implementation^0.3) * (hardware^0.3)`

Range 0.000–10.000. Any axis = 0 → composite = 0 → auto-reject.
