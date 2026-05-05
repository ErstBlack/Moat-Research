# FOCUS

This file is the operator's priority-override channel for `maximizer`. **Maximizer reads this file first** when it rotates to the `moat-research` project, before any other work (discovery, scoring, re-scoring, init-prompt generation, signal triage).

## Rules

- Items are processed **top-to-bottom, in order**. Do not skip ahead unless an item is explicitly marked `[parallel-ok]`.
- Each item has a status checkbox: `[ ]` pending, `[~]` in-progress, `[x]` done.
- When an item is completed, mark it `[x]` and append a one-line note (what was produced + path to artifact). Do not delete completed items in the same iteration — the next iteration may garbage-collect them.
- An item without an explicit acceptance criterion is **not actionable**; treat it as `[ ]` blocked and surface a question rather than guessing.
- If every actionable item is `[x]` or `[~]` and blocked, fall through to the standard synthesis menu defined in the design spec (§9.5).
- The operator may rewrite, reorder, or remove items at any time. Maximizer must re-read `FOCUS.md` at the start of every iteration; never cache it across iterations.
- Hard constraints from `CONSTRAINTS.md` and disqualifiers from `RUBRIC.md` apply to focus items too. A focus item that would violate them must be flagged back to the operator, not silently downgraded.

## Key documents

Read these before acting on any focus item:

- **Design spec** — `docs/superpowers/specs/2026-05-04-moat-research-design.md` — full architecture, lifecycle, rubric, file format, component design.
- **Implementation plan** — `docs/superpowers/plans/2026-05-04-moat-research-implementation.md` — 17 task plan with TDD steps, file structure, and self-review checklist (all tasks complete as of 2026-05-04).

## Active queue

### 1. [ ] Recheck DC rideshare/micromobility GBFS feeds against new endpoint list

**Spec reference:** `docs/superpowers/specs/2026-05-04-moat-research-design.md` §5 (rubric, lanes), §7.3 (wishlist lifecycle); `CONSTRAINTS.md` (robots/ToS/rate-limit).

**Why:** The 2026-05-04 verification pass dropped Capital Bikeshare GBFS after `gbfs.lyft.com` returned HTTP 403. The DDOT shared-mobility program page lists actual public endpoints for all five operators currently permitted to operate in DC, so the prior dismissal was based on the wrong URL. These are GBFS feeds (free_bike_status.json in particular), which are by design ephemeral — the location of every available bike/scooter at minute T cannot be reconstructed from any later snapshot. Lane-1 candidate worth re-evaluating.

**Endpoints to check** (sourced from the DDOT rideshare program page):

- Capital Bikeshare (Lyft-operated): https://gbfs.capitalbikeshare.com/gbfs/gbfs.json
- Lime: https://data.lime.bike/api/partners/v1/gbfs/washington_dc/free_bike_status.json
- Lyft scooters/e-bikes: https://s3.amazonaws.com/lyft-lastmile-production-iad/lbs/dca/free_bike_status.json
- Helbiz: https://api.helbiz.com/admin/reporting/washington/gbfs/gbfs.json
- Spin: https://web.spin.pm/api/gbfs/v1/washington_dc/free_bike_status

**Acceptance criteria:**

1. For each of the five endpoints, verify: (a) HTTP reachability without auth, (b) robots.txt for the host (or document its absence), (c) any published GBFS rate-limit / `ttl` value in the feed itself, (d) ToS or program-page language about archival or third-party use. Record findings in a working note (e.g., a comment block in the wishlist entry or a short doc under `docs/`), with the verification date.
2. Hard-constraint check per `CONSTRAINTS.md`: any endpoint that fails robots.txt or has explicit ToS language forbidding archival is dismissed individually with `dismissed_reason` rather than dragging the whole batch down.
3. Surviving endpoints land as a single `WISHLIST.md` entry under `sources:` with `id: dc_gbfs_micromobility` (or split into per-operator entries if their constraints diverge meaningfully). Use the schema in WISHLIST.md's "How to append" section. `lane_hint: 1` (ephemeral) unless evidence shows a non-trivial provider-side archive.
4. The `why_interesting` paragraph must explicitly address the moat thesis: GBFS `free_bike_status.json` is overwritten on each poll (typical TTL 60s); a multi-operator continuous archive across all five DC fleets does not exist as a public dataset, and the cross-operator fusion (substitution patterns, modal share, dwell-time-by-zone) is the value-add over any single operator's own internal logs.
5. The "Capital Bikeshare GBFS — dropped, revisit if public endpoint is found" line is removed from `WISHLIST.md`'s `## Notes for the operator` once the recheck is complete (regardless of outcome — either a wishlist entry or a fresh `dismissed`-style note replaces it).
6. Do **not** start ingestion or write a brief in this item — this is a wishlist-stage recheck only. Promotion to a candidate brief happens later via the normal lifecycle.

**Out of scope:** scoring, brief authoring, signal-source registration in `signals/sources.yml`, ingestor implementation. Those follow if and only if the wishlist entry survives operator review.

---

## Recently completed

- **2026-05-04** — Implementation plan Tasks 5–17 (workers, coordinator, ingest base, stack, pre-commit). Branch `maximizer/moat/20260504T061153Z-8c8eb4`; 65 tests pass; politeness lint, docker stack config, pre-commit all green. Plan: `docs/superpowers/plans/2026-05-04-moat-research-implementation.md`.
- **2026-05-04** — Rescored `somd-cameras` against `RUBRIC.md`. Brief: `briefs/graduated/07.221-20260504-somd-cameras.md` (composite 7.221, lane 1). All five disqualifiers re-checked; calibration note recommends no rubric edits until ≥3 more lane-1 candidates are scored.
- **2026-05-04** — Bootstrapped maximizer-facing context surfaces: `/home/runner/claude-runner/config/projects/moat/system-prompt.md` (commit `d28a8a2`); `CLAUDE.md`, `RUBRIC.md`, `LANES.md`, `CONSTRAINTS.md` at repo root.
- **2026-05-04** — Seeded `WISHLIST.md` with 4 entries spanning lanes 1 (NDBC buoys, NJDOT 511 cameras) and 3 (USGS×NWS flood fusion, CO-OPS×AIS coastal fusion).

## Notes for the operator

- `FOCUS.md` is meant to be terse. If a focus item needs more than a few paragraphs of context, link to a doc under `docs/` rather than inlining it here.
- Treat this file like a sticky-note pad on top of the project. Long-running themes belong in the design spec; short-lived priorities belong here.
