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

### 1. [x] Recheck DC rideshare/micromobility GBFS feeds against new endpoint list

**Outcome (2026-05-04):** 1 of 5 DDOT-listed operators viable. Capital Bikeshare added to `WISHLIST.md` as `dc_capital_bikeshare_gbfs` and immediately marked `status: dismissed` per operator direction — the multi-operator fusion premise (the actual moat thesis behind FOCUS item 1) does NOT survive verification, and a single-operator CaBi-only archive overlaps with CaBi's existing public quarterly trip dumps. Lime dismissed on robots.txt `Disallow: /` (CONSTRAINTS §2). Lyft scooters S3 path dismissed as stale (last_updated 2023-08-17). Helbiz dismissed as defunct (504, exited US 2023). Spin dismissed as feed retired (404 "Invalid feed"). Per-operator dismissal rationale is in `WISHLIST.md` "Notes for the operator"; revisit triggers in the entry's `dismissed_reason`.

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

- **2026-05-04** — Scored the three new candidate briefs from the discovery synthesis pass against `RUBRIC.md`. Composites: `07.009-20260504-cslb-ca-contractor-disciplinary-corpus` (Lane 4, financial 6.333 / impl 7.500 / hw 7.500), `06.892-20260504-multi-state-medical-board-enforcement` (Lane 4+5, 7.333 / 6.250 / 7.000), `06.701-20260504-us-transit-gtfsrt-smaller-agencies` (Lane 1, 6.833 / 6.250 / 7.000). All three pass §5 — the two Lane-4 briefs against the cerebrum entity-resolution methodology (CSLB scores 6 on Defensibility because federation is a roadmap; medical-board scores 7 because cross-jurisdiction ER is a v1 deliverable), the Lane-1 transit brief against the strict reading that paid commercial archives (Interline) do not trigger the no-moat hard floor (Defensibility=9 with explicit per-agency §5 verification gate at onboarding). All three wishlist entries flipped backlog → promoted-to-candidate. Final score table now: 07.221 somd-cameras (graduated, L1) | 07.695 usgs-nws-flood-fusion (scored, L4) | 07.360 njdot-511-cameras (scored, L1) | 07.009 cslb-ca-contractor-disciplinary-corpus (scored, L4) | 06.892 multi-state-medical-board-enforcement (scored, L4+5) | 06.701 us-transit-gtfsrt-smaller-agencies (scored, L1) | 00.000 ndbc-realtime-buoys (rejected, L1). Lane-1 cluster now n=4 (somd, njdot, transit-gtfsrt, ndbc-rejected); Lane-4 cluster now n=3 (flood-fusion, cslb, medical-board); cluster compression observation revisits open at n≥6 per the prior calibration deferred decision.

- **2026-05-04** — Discovery synthesis pass to refill the wishlist (zero `backlog` entries remaining after the NDBC/CO-OPS-AIS/CaBi dismissals). Three new candidates added: `us_transit_gtfsrt_smaller_agencies` (Lane 1, GTFS-Realtime vehicle positions across the long tail of US transit agencies — somd-cameras pattern applied to transit telemetry, with per-agency §5 verification deferred to brief stage), `cslb_ca_contractor_disciplinary_corpus` (Lane 4, OCR + NER + entity-resolution over CA Contractors State License Board disciplinary PDFs, compute-as-barrier with cross-state federation as future moat extension), `multi_state_medical_board_enforcement` (Lane 4+5, cross-state entity-resolved physician disciplinary corpus where FSMB Physician Data Center / NPDB are paid/restricted equivalents). Eight additional candidates considered and dismissed during the pass (Bay Area 511 API on robots `Disallow:/`, regulations.gov on CloudFront 403 + already archived, NJ Judiciary public-access portal on §5 court-records archival, NYC Council Legistar on §5 system-of-record archival, AC Transit GTFS-RT live feed folded into the broader smaller-agency thesis, Chicago Open Data 311 on §5 Socrata archive, CSLB live-status Lane-1 framing folded into the Lane-4 entry, FCC ULS on dual UA-block + §5 archive). Full reasoning per candidate in `WISHLIST.md` Notes for the operator. Pattern observations folded into `.wolf/cerebrum.md`.

- **2026-05-04** — NDBC spectral archive verification (resolves the brief's self-gated `ncei_spectral_archival_unverified` flag against new CONSTRAINTS §5). Verified that NDBC itself publishes a complete public sub-hourly spectral archive at `/data/swden/{Mon}/<station><MM><YYYY>.txt.gz` (monthly) and `/data/historical/swden/<station>w<YYYY>.txt.gz` (annual), at the same :10/:40 cadence as the realtime feeds (sample evidence: 41001w2024, 41001w2025 last-modified 2026-02-11, 4100212026.txt.gz). Lane-1 ephemeral premise collapses; CONSTRAINTS §5 fires → Defensibility 9 → 0, financial axis forced 0, composite 7.600 → 0.000. Brief auto-rejected and moved: `briefs/candidates/07.600-20260504-ndbc-realtime-buoys.md` → `briefs/rejected/00.000-20260504-ndbc-realtime-buoys.md`. WISHLIST entry `ndbc_realtime_buoys` flipped `promoted-to-candidate` → `dismissed` with revisit triggers. Lane-3/Lane-4 reframe considered and dismissed (raw archive is publicly available at the proposed cadence, so a Lane-3 join is reconstructible; no concrete Lane-4 derived-artifact thesis identified yet — fresh wishlist entry required if one emerges). Final score table: `07.221-somd-cameras` (graduated, L1) | `07.360-njdot-511-cameras` (scored, L1) | `07.695-usgs-nws-flood-fusion` (scored, L4) | `00.000-ndbc-realtime-buoys` (rejected, L1). Lane-1 cluster now n=3, weakening cluster-compression observation slightly but not enough to revisit deferred score-formula edits.
- **2026-05-04** — Rubric calibration pass (n=4 lane-1 candidates, scores 7.221/7.360/7.600/7.771, spread 0.55). Findings: (a) the rubric had no "no-moat reconstructibility" hard disqualifier; codified as `CONSTRAINTS.md` §5 + `RUBRIC.md` Defensibility hard floor + design spec §3 disqualifier 5 + §5.1 Defensibility hard floor (operator policy 2026-05-04: "If there isn't a viable moat to exploit then the project can be reconstructed by anyone later without issue."). (b) Score-formula edits deferred until n≥6 — cluster compression real but not yet fatal. (c) `07.771-usgs-nws-flood-fusion` re-categorized to Lane 4 primary (operator decision 2026-05-04, option b): both raw inputs (USGS NWIS historical + NCEI Storm Events CSV) are publicly archived, so Lane-3 join is reconstructible. Defensibility nudged 8 → 7 under Lane-4 lens; financial composite 6.833 → 6.667; overall composite 7.771 → 7.695. File renamed `07.771-...md` → `07.695-...md`; wishlist `promoted_to` updated; brief calibration note rewritten to document the recategorization. The other three scored briefs are clear: `somd-cameras` and `njdot-511-cameras` are Lane 1 with verified non-archival; `ndbc-realtime-buoys` already gates on `ncei_spectral_archival_unverified` for exactly this disqualifier. See `WISHLIST.md` and the brief headers for source.
- **2026-05-04** — DC GBFS recheck (FOCUS item 1): 1 of 5 DDOT operators viable; multi-operator fusion thesis dismissed; `dc_capital_bikeshare_gbfs` added then dismissed (operator decision) on no-moat grounds. `coops_ais_coastal_fusion` re-verified the same day and dismissed for the same reason (Lane-3 thesis collapses; both inputs publicly archived). Both dismissals informed the calibration above.
- **2026-05-04** — Implementation plan Tasks 5–17 (workers, coordinator, ingest base, stack, pre-commit). Branch `maximizer/moat/20260504T061153Z-8c8eb4`; 65 tests pass; politeness lint, docker stack config, pre-commit all green. Plan: `docs/superpowers/plans/2026-05-04-moat-research-implementation.md`.
- **2026-05-04** — Rescored `somd-cameras` against `RUBRIC.md`. Brief: `briefs/graduated/07.221-20260504-somd-cameras.md` (composite 7.221, lane 1). All five disqualifiers re-checked; calibration note recommends no rubric edits until ≥3 more lane-1 candidates are scored.
- **2026-05-04** — Bootstrapped maximizer-facing context surfaces: `/home/runner/claude-runner/config/projects/moat/system-prompt.md` (commit `d28a8a2`); `CLAUDE.md`, `RUBRIC.md`, `LANES.md`, `CONSTRAINTS.md` at repo root.
- **2026-05-04** — Seeded `WISHLIST.md` with 4 entries spanning lanes 1 (NDBC buoys, NJDOT 511 cameras) and 3 (USGS×NWS flood fusion, CO-OPS×AIS coastal fusion).

## Notes for the operator

- `FOCUS.md` is meant to be terse. If a focus item needs more than a few paragraphs of context, link to a doc under `docs/` rather than inlining it here.
- Treat this file like a sticky-note pad on top of the project. Long-running themes belong in the design spec; short-lived priorities belong here.
