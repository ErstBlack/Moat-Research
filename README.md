# moat-research

Discovery, scoring, and queueing of "data moat" opportunities — datasets, archives, derived artifacts, or fused corpora that are feasible to capture *now* but impossible or impractical to retroactively reconstruct, and have a plausible monetization path.

This repo is **a corpus + a stateless worker stack**. It does not call models. All synthesis (ideation, scoring, init-prompt generation) is performed by `maximizer` iterating against this repo.

## Where to look first

- `FOCUS.md` — operator priority queue. Read by maximizer before anything else.
- `WISHLIST.md` — known data sources awaiting evaluation.
- `RUBRIC.md`, `LANES.md`, `CONSTRAINTS.md` — scoring rules.
- `briefs/` — the corpus, organized by lifecycle stage.
- `docs/superpowers/specs/2026-05-04-moat-research-design.md` — the design.

## Lifecycle

```
candidates → scored → rejected | approved → graduated
```

- `candidates/` — discovered, not yet scored.
- `scored/` — scored & ranked, awaiting human review.
- `rejected/` — auto- (any axis = 0) or operator-rejected.
- `approved/` — operator-promoted from scored; init-prompt artifact generated.
- `graduated/` — project exists in maximizer; brief archived with backref.

Files are score-prefixed (`08.031-20260504-fcc-eas-alerts.md`); `ls scored/ | sort -r` is the queue.

## Workers

All workers are Python, stateless, deployed as a single-node Docker swarm stack (`stacks/moat-research.yml`). See `docs/superpowers/specs/2026-05-04-moat-research-design.md` §9 for the full component list.
