# WISHLIST

Living, append-only list of **known data sources that look promising but have not yet been captured by this project**. The complement to `briefs/`: this file holds raw "things we know exist" before they become structured opportunity briefs.

## Rules

- Both the operator and `maximizer` may **append** entries. Only the operator may delete; maximizer marks entries `dismissed` instead.
- Maximizer must append a wishlist entry whenever it identifies a candidate source while reading signal digests, even if it doesn't immediately turn it into a brief. The wishlist is the durable surface area of "things we know exist"; the brief corpus is just the subset deemed worth committing to.
- Status values:
  - `backlog` — default for new entries.
  - `promoted-to-candidate` — set when a real brief has been created in `briefs/candidates/`. Set `promoted_to: <brief_id>`.
  - `dismissed` — operator (or maximizer with a clear hard-constraint trigger) determined the source isn't worth pursuing. Set `dismissed_reason` so the same entry isn't re-promoted later.
- Entries `backlog` for >90 days should be surfaced for operator review during a `wishlist hygiene` synthesis pass; do not auto-dismiss.
- Hard constraints from `CONSTRAINTS.md` apply: do not append entries whose capture would require auth-bypass, ToS/robots/rate-limit violations, or DDOS-grade load.
- Lane hints are speculative. They are not authoritative — the brief assigns the real lane during scoring.

## Sources

```yaml
sources: []
```

## How to append (for operator quick reference)

Each new entry is one YAML map under `sources:`:

```yaml
- id: <short_snake_case_id>            # stable, used for promoted_to refs
  title: "<human title>"
  url: <primary url>
  discovered: YYYY-MM-DD
  discovered_by: operator              # operator | maximizer
  lane_hint: <1..5 or null>            # speculative
  why_interesting: |
    Why this might be a moat. One paragraph max.
  known_constraints: |
    Auth, rate limits, robots.txt, ToS notes, anything you noticed.
  estimated_size: "<rough storage rate, e.g., 2 GB/day>"
  rate_limit_notes: "<published or inferred>"
  status: backlog                      # backlog | promoted-to-candidate | dismissed
  promoted_to: null
  dismissed_reason: null
```
