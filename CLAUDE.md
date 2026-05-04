# moat-research

This is the moat-research project. Read `docs/superpowers/specs/2026-05-04-moat-research-design.md` for the full design.

## Hard rules

1. **No model calls in this repo.** All synthesis is done by maximizer iterating against this repo. Workers here are stateless Python.
2. **`scored → approved` is human-only.** Never auto-promote.
3. **`FOCUS.md` is the priority override.** Read it first; complete its items in order before any organic work.
4. **Respect rate limits, ToS, robots.txt.** Hard disqualifiers, no exceptions. See `CONSTRAINTS.md`.

## Operator-facing surfaces (read these before acting)

@FOCUS.md
@WISHLIST.md
@RUBRIC.md
@LANES.md
@CONSTRAINTS.md
