# Memory

> Chronological action log. Hooks and AI append to this file automatically.
> Old sessions are consolidated by the daemon weekly.

## 2026-05-05 (20260505T114726Z-af4378 T3 — scoring pass)

- Scored two T2 backlog candidates and wrote candidate briefs:
  - `briefs/candidates/07.216-20260505-txdot-drivetexas-cameras.md` (Lane 1+5, fin 6.833 / impl 7.000 / hw 8.000, composite 7.216).
  - `briefs/candidates/06.911-20260505-uspto-patent-claim-citation-corpus.md` (Lane 4+5, fin 7.167 / impl 7.000 / hw 6.500, composite 6.911).
- Both pass all 5 CONSTRAINTS hard disqualifiers including §5 Defensibility floor; no axis=0 rejections.
- WISHLIST entries flipped backlog → promoted-to-candidate (txdot_drivetexas_cameras → 07.216-...; uspto_patent_claim_citation_corpus → 06.911-...).
- FOCUS.md `Recently completed` appended with cluster snapshot + key learnings.
- Active scored cluster: n=15 candidates + 1 graduated = 16. **Calibration trigger n>15 crossed** — flag for next-iteration formal calibration pass.
- Lane balance now L1:5 / L2:5 / L4:6 (well-diversified).
- All 65 tests still pass.
- Files touched: 2 new briefs, `WISHLIST.md`, `FOCUS.md`, `.wolf/memory.md`.

## 2026-05-05 (20260505T114726Z-af4378 T2 — discovery synthesis pass)

- Iteration `20260505T114726Z-af4378` task T2 — discovery synthesis pass with explicit L1/L4 diversification (L2 cluster already at 5, per task acceptance criteria).
- Verified candidates: drivetexas.org HTTP 200 (robots.txt HTTP 500 = absent, no restriction; www.txdot.gov robots.txt HTTP 404 = absent); data.uspto.gov HTTP 200, developer.uspto.gov HTTP 200, api.patentsview.org HTTP 200, ppubs.uspto.gov HTTP 200 (robots.txt: SPA returns HTML = absent, no restriction).
- Added `txdot_drivetexas_cameras` (Lane 1) — TxDOT live traffic cameras, I-10/I-35/I-45 freight/energy corridors, extends somd/njdot camera archetype, distinct energy-sector buyer angle.
- Added `uspto_patent_claim_citation_corpus` (Lane 4) — structured claim-dependency graphs + cross-jurisdiction inventor ER + real-time citation network; PatentsView (free/USPTO-funded) does NOT include claim graphs, cross-jurisdiction ER, or weekly refresh; commercial competitors ($50k–$200k+/year) don't trigger §5.
- Dismissed: PHMSA (HTTP 403 Akamai-edge gating), FFIEC (HTTP 403 Akamai), NOAA GHCN-Daily (archived = §5), NIFC wildfire perimeters (archived or operationally sensitive = §5).
- Lane cluster after pass: L1: 5 entries, L2: 5 entries, L4: 6 entries.
- All 65 tests pass. Files touched: `WISHLIST.md`, `.wolf/memory.md`, `.wolf/anatomy.md`.

## 2026-05-05 (T1 — n=9 calibration pass)

- Iteration `20260505T083851Z-d3bb40` task T1 — calibration pass against the n=9 active scored cluster (the deferred-at-n≥6 work).
- Compiled per-axis distributions and lane-by-lane composite spread for all 9 active briefs + the rejected NDBC for reference. Cluster shape: composite 6.701–7.898 (Δ=1.197), σ=0.384, range/σ≈3.1 (normal-distribution shape, not pathological).
- Closest pair FERC 7.006 / CSLB 7.009 (Δ=0.003) examined; trade-off equivalence under the multiplicative formula is intentional and does not split operator decisions.
- Re-checked every brief against `CONSTRAINTS.md` §1–§5 under current rubric. No regressions; no score changes; no file renames; no WISHLIST `promoted_to_history` updates.
- Evaluated four formula alternatives (0.5/0.25/0.25 weights; arithmetic mean; defensibility-2x sub-weight; sub-criterion full-range anchors) — none clear a justification bar that beats comparability cost vs. graduated `07.221-somd-cameras` and the load-bearing "any-axis-zero kills" §5 enforcement property.
- Recommendation: **defer-with-rationale**. Trigger conditions for future revisit codified in `docs/calibration/2026-05-05-n8-pass.md` (composite Δ<0.10 splitting operator decisions; counter-intuitive ordering; n>15 with L1↔L4 boundary blurring; hardware-9 / defensibility-3 reaching top-quartile composite).
- Lane-5 framing observation logged: 5/9 briefs declare L5 secondary, 0 primary — healthy pattern (Lane 5 alone without temporal-loss / compute / political-vulnerability angle probably doesn't survive §5).
- Files touched: `docs/calibration/2026-05-05-n8-pass.md` (new), `FOCUS.md` Recently-completed, `.wolf/memory.md`, `.wolf/anatomy.md`. RUBRIC.md and design spec §5 untouched.

## 2026-05-04 (T3 — usgs_nws_flood_fusion scoring)

- Created `briefs/candidates/07.771-20260504-usgs-nws-flood-fusion.md` — Lane 3 cross-source fusion.
- Composite 7.771 (financial 6.833, implementation 7.75, hardware 9.25).
- Pivoted from api.weather.gov to NCEI bulk CSV path to resolve robots.txt Disallow: / ambiguity.
- One open disqualifier: ncei.noaa.gov/robots.txt not independently fetched; must verify before promoting to approved.

## Session: 2026-05-04 06:05

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 06:06

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 06:07

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 06:07

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 06:07

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 06:07

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 06:07

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 06:07

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 06:07

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 06:07

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 06:07

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 06:11

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 06:12

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 18:56

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 18:11

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 18:11

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 18:13

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 18:15 | Created workers/common/brief.py | — | ~732 |
| 18:16 | Edited tests/unit/test_brief.py | modified test_rejects_above_ten() | ~658 |
| 18:16 | Created tests/fixtures/brief_valid_scored.md | — | ~384 |
| 18:16 | Created tests/fixtures/brief_zero_financial.md | — | ~384 |
| 18:16 | Created tests/fixtures/brief_zero_implementation.md | — | ~384 |
| 18:16 | Created tests/fixtures/brief_zero_hardware.md | — | ~383 |
| 18:16 | Created tests/fixtures/brief_candidate_unscored.md | — | ~156 |
| 18:17 | Created tests/fixtures/brief_approved.md | — | ~385 |
| 18:17 | Edited workers/common/brief.py | modified parse_brief() | ~672 |
| 18:17 | Edited tests/unit/test_brief.py | modified test_natural_sort_order() | ~814 |
| 18:18 | Created tests/unit/test_promoter.py | — | ~828 |
| 18:18 | Created workers/promoter/promoter.py | — | ~625 |
| 18:18 | Created tests/unit/test_indexer.py | — | ~810 |
| 18:18 | Created workers/indexer/indexer.py | — | ~530 |
| 18:19 | Created workers/init_prompt_gen/template.md | — | ~752 |
| 18:19 | Created tests/unit/test_init_prompt_gen.py | — | ~528 |
| 18:19 | Created workers/init_prompt_gen/init_prompt_gen.py | — | ~932 |
| 18:19 | Created tests/unit/test_coordinator.py | — | ~518 |
| 18:19 | Created workers/coordinator/coordinator.py | — | ~956 |
| 18:20 | Created workers/common/throttle.py | — | ~349 |
| 18:20 | Created workers/ingest/base.py | — | ~893 |
| 18:20 | Created tests/unit/test_ingest_base.py | — | ~895 |
| 18:20 | Created tests/fixtures/sources_clean.yml | — | ~54 |
| 18:20 | Created tests/fixtures/sources_missing_rate_budget.yml | — | ~46 |
| 18:20 | Created scripts/politeness_lint.py | — | ~555 |
| 18:21 | Created tests/unit/test_politeness_lint.py | — | ~680 |
| 18:21 | Created tests/integration/test_lifecycle.py | — | ~845 |
| 18:21 | Edited workers/common/brief.py | modified parse_brief() | ~188 |
| 18:22 | Created workers/promoter/Dockerfile | — | ~70 |
| 18:22 | Created workers/indexer/Dockerfile | — | ~68 |
| 18:22 | Created workers/init_prompt_gen/Dockerfile | — | ~77 |
| 18:22 | Created workers/coordinator/Dockerfile | — | ~70 |
| 18:22 | Created workers/ingest/Dockerfile.base | — | ~75 |
| 18:22 | Created stacks/moat-research.yml | — | ~546 |
| 18:22 | Created .pre-commit-config.yaml | — | ~138 |
| 18:23 | Edited FOCUS.md | 1→5 lines | ~82 |
| 18:23 | Session end: 36 writes across 30 files (brief.py, test_brief.py, brief_valid_scored.md, brief_zero_financial.md, brief_zero_implementation.md) | 2 reads | ~17293 tok |
| 18:32 | Session end: 36 writes across 30 files (brief.py, test_brief.py, brief_valid_scored.md, brief_zero_financial.md, brief_zero_implementation.md) | 2 reads | ~17293 tok |

## Session: 2026-05-04 18:32

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 18:38 | Created briefs/graduated/07.221-20260504-somd-cameras.md | — | ~4029 |
| 18:39 | Edited FOCUS.md | 1→3 lines | ~152 |
| 18:40 | Session end: 2 writes across 2 files (07.221-20260504-somd-cameras.md, FOCUS.md) | 8 reads | ~9725 tok |

## Session: 2026-05-04 18:47

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 18:47

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 18:48

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 18:49

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 18:52 | Edited FOCUS.md | 12→14 lines | ~480 |
| 18:52 | Session end: 1 writes across 1 files (FOCUS.md) | 2 reads | ~3696 tok |

## Session: 2026-05-04 18:52

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 19:01 | Edited WISHLIST.md | expanded (+133 lines) | ~2373 |
| 19:01 | Edited WISHLIST.md | modified grounds() | ~190 |
| 19:01 | Edited FOCUS.md | 1→3 lines | ~123 |
| 19:02 | Session end: 3 writes across 2 files (WISHLIST.md, FOCUS.md) | 4 reads | ~9362 tok |

## Session: 2026-05-04 19:02

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 19:02 | Edited FOCUS.md | 3→3 lines | ~51 |
| 19:02 | Edited FOCUS.md | 3→3 lines | ~43 |
| 19:03 | Session end: 2 writes across 1 files (FOCUS.md) | 1 reads | ~3457 tok |

## Session: 2026-05-04 19:03

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 19:06

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 19:07

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 19:16

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 19:17

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 19:18

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 19:21 | Created briefs/candidates/07.600-20260504-ndbc-realtime-buoys.md | — | ~4200 |
| 19:23 | Edited briefs/candidates/07.600-20260504-ndbc-realtime-buoys.md | inline fix | ~4 |
| 19:23 | Session end: 2 writes across 1 files (07.600-20260504-ndbc-realtime-buoys.md) | 4 reads | ~10728 tok |

## Session: 2026-05-04 19:23

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 19:28 | Created briefs/candidates/07.360-20260504-njdot-511-cameras.md | — | ~4876 |
| 19:28 | Edited WISHLIST.md | 5→5 lines | ~39 |
| 19:28 | Session end: 2 writes across 2 files (07.360-20260504-njdot-511-cameras.md, WISHLIST.md) | 3 reads | ~15931 tok |

## Session: 2026-05-04 19:28

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 19:33 | Created briefs/candidates/07.771-20260504-usgs-nws-flood-fusion.md | — | ~6759 |
| 19:34 | Session end: 1 writes across 1 files (07.771-20260504-usgs-nws-flood-fusion.md) | 1 reads | ~11178 tok |

## Session: 2026-05-04 19:34

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 19:34 | Edited WISHLIST.md | 32→32 lines | ~588 |
| 19:35 | Edited WISHLIST.md | 29→29 lines | ~511 |
| 19:35 | Edited WISHLIST.md | 35→35 lines | ~662 |
| 19:35 | Session end: 3 writes across 1 files (WISHLIST.md) | 2 reads | ~5476 tok |

## Session: 2026-05-04 19:35

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 19:36

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 19:40

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-04 19:41

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 19:41 | Add FOCUS item 4: recheck DC GBFS feeds (5 endpoints from DDOT page); remove stale Capitol Bikeshare dismissal from WISHLIST operator notes | FOCUS.md, WISHLIST.md | done | ~600 |

## Session: 2026-05-05 21:55

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-05 21:58

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 22:04 | Edited WISHLIST.md | expanded (+52 lines) | ~1002 |
| 22:04 | Edited WISHLIST.md | modified grounds() | ~573 |
| 22:04 | Edited FOCUS.md | modified Outcome() | ~210 |
| 22:05 | Session end: 3 writes across 2 files (WISHLIST.md, FOCUS.md) | 0 reads | ~1912 tok |
| 22:18 | Edited WISHLIST.md | added 1 condition(s) | ~378 |
| 22:19 | Edited FOCUS.md | inline fix | ~207 |
| 22:19 | Session end: 5 writes across 2 files (WISHLIST.md, FOCUS.md) | 0 reads | ~2539 tok |
| 22:23 | Edited WISHLIST.md | modified LIMITATION() | ~913 |
| 22:23 | Session end: 6 writes across 2 files (WISHLIST.md, FOCUS.md) | 0 reads | ~3517 tok |
| 22:24 | Edited WISHLIST.md | added 1 condition(s) | ~398 |
| 22:25 | Session end: 7 writes across 2 files (WISHLIST.md, FOCUS.md) | 0 reads | ~3943 tok |
| 22:30 | Edited CONSTRAINTS.md | 6→7 lines | ~358 |
| 22:31 | Edited RUBRIC.md | inline fix | ~242 |
| 22:31 | Edited docs/superpowers/specs/2026-05-04-moat-research-design.md | 6→7 lines | ~396 |
| 22:31 | Edited docs/superpowers/specs/2026-05-04-moat-research-design.md | inline fix | ~251 |
| 22:32 | Edited FOCUS.md | modified recheck() | ~556 |
| 22:33 | Session end: 12 writes across 5 files (WISHLIST.md, FOCUS.md, CONSTRAINTS.md, RUBRIC.md, 2026-05-04-moat-research-design.md) | 1 reads | ~5876 tok |
| 22:36 | Edited briefs/candidates/07.771-20260504-usgs-nws-flood-fusion.md | modified pass() | ~293 |
| 22:36 | Edited briefs/candidates/07.771-20260504-usgs-nws-flood-fusion.md | expanded (+9 lines) | ~595 |
| 22:36 | Edited briefs/candidates/07.771-20260504-usgs-nws-flood-fusion.md | 9→9 lines | ~50 |
| 22:37 | Edited briefs/candidates/07.771-20260504-usgs-nws-flood-fusion.md | modified Defensibility() | ~392 |
| 22:37 | Edited briefs/candidates/07.771-20260504-usgs-nws-flood-fusion.md | 7.771 → 7.695 | ~6 |
| 22:37 | Edited briefs/candidates/07.771-20260504-usgs-nws-flood-fusion.md | 33→37 lines | ~610 |
| 22:38 | Edited WISHLIST.md | 5→7 lines | ~81 |
| 22:38 | Edited FOCUS.md | inline fix | ~131 |
| 22:38 | Session end: 20 writes across 6 files (WISHLIST.md, FOCUS.md, CONSTRAINTS.md, RUBRIC.md, 2026-05-04-moat-research-design.md) | 2 reads | ~14523 tok |

## Session: 2026-05-05 22:40

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 22:46 | Edited briefs/candidates/07.600-20260504-ndbc-realtime-buoys.md | added 1 condition(s) | ~764 |
| 22:46 | Edited briefs/candidates/07.600-20260504-ndbc-realtime-buoys.md | 11→11 lines | ~194 |
| 22:46 | Edited briefs/candidates/07.600-20260504-ndbc-realtime-buoys.md | density() → NDBC() | ~599 |
| 22:47 | Edited briefs/candidates/07.600-20260504-ndbc-realtime-buoys.md | expanded (+66 lines) | ~1046 |
| 22:47 | Edited briefs/candidates/07.600-20260504-ndbc-realtime-buoys.md | entry() → COMPLETE() | ~202 |
| 22:48 | Edited WISHLIST.md | added 1 condition(s) | ~627 |
| 22:48 | Edited FOCUS.md | 3→4 lines | ~407 |
| 22:49 | Session end: 7 writes across 3 files (07.600-20260504-ndbc-realtime-buoys.md, WISHLIST.md, FOCUS.md) | 2 reads | ~13270 tok |
| 22:52 | Session end: 7 writes across 3 files (07.600-20260504-ndbc-realtime-buoys.md, WISHLIST.md, FOCUS.md) | 2 reads | ~13270 tok |

## Session: 2026-05-05 22:54

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 23:04 | Edited WISHLIST.md | expanded (+140 lines) | ~2571 |
| 23:05 | Edited WISHLIST.md | expanded (+13 lines) | ~1062 |
| 23:05 | Edited FOCUS.md | 3→5 lines | ~403 |
| --- | --- | --- | --- | --- |
| 2026-05-04 | Discovery synthesis pass | WISHLIST.md +185 lines (3 new entries + dismissals); FOCUS.md +1 entry; .wolf/cerebrum.md +3 learnings | wishlist refilled from 0 to 3 backlog candidates | n/a |
| 23:06 | Session end: 3 writes across 2 files (WISHLIST.md, FOCUS.md) | 1 reads | ~10046 tok |
| 23:08 | Session end: 3 writes across 2 files (WISHLIST.md, FOCUS.md) | 1 reads | ~10046 tok |
| 23:13 | Created briefs/candidates/07.009-20260504-cslb-ca-contractor-disciplinary-corpus.md | — | ~5449 |
| 23:16 | Created briefs/candidates/06.892-20260504-multi-state-medical-board-enforcement.md | — | ~5831 |
| 23:18 | Created briefs/candidates/06.701-20260504-us-transit-gtfsrt-smaller-agencies.md | — | ~6220 |
| 23:18 | Edited WISHLIST.md | 7→7 lines | ~118 |
| 23:19 | Edited WISHLIST.md | 7→7 lines | ~124 |
| 23:19 | Edited WISHLIST.md | 6→6 lines | ~112 |
| 23:19 | Edited FOCUS.md | 3→5 lines | ~429 |
| 2026-05-04 | Scored 3 new candidates | 3 new briefs in briefs/candidates/ + WISHLIST status flips + FOCUS Recently-completed | composites 7.009 / 6.892 / 6.701, all pass §5 | n/a |
| 23:20 | Session end: 10 writes across 5 files (WISHLIST.md, FOCUS.md, 07.009-20260504-cslb-ca-contractor-disciplinary-corpus.md, 06.892-20260504-multi-state-medical-board-enforcement.md, 06.701-20260504-us-transit-gtfsrt-smaller-agencies.md) | 2 reads | ~34204 tok |

## Session: 2026-05-05 03:21

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-05 03:21

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-05 03:22

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-05 03:26

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 03:37 | Edited WISHLIST.md | expanded (+174 lines) | ~3419 |
| 03:38 | Edited WISHLIST.md | added 1 condition(s) | ~1729 |
| 03:40 | Session end: 2 writes across 1 files (WISHLIST.md) | 1 reads | ~14600 tok |

## Session: 2026-05-05 03:40

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 03:42 | Created .score_tmp.py | — | ~43 |
| 03:45 | Created briefs/candidates/07.898-20260505-faa-notams-aviation-alerts.md | — | ~6463 |
| 03:48 | Created briefs/candidates/06.805-20260505-usda-aphis-animal-welfare-inspections.md | — | ~6419 |
| 03:51 | Created briefs/candidates/07.006-20260505-ferc-elibrary-regulatory-filings.md | — | ~7539 |
| 03:51 | Edited WISHLIST.md | 7→7 lines | ~141 |
| 03:51 | Edited WISHLIST.md | 7→7 lines | ~160 |
| 03:52 | Edited WISHLIST.md | 6→6 lines | ~135 |
| 03:52 | Edited FOCUS.md | 3→5 lines | ~386 |
| 03:53 | Session end: 8 writes across 6 files (.score_tmp.py, 07.898-20260505-faa-notams-aviation-alerts.md, 06.805-20260505-usda-aphis-animal-welfare-inspections.md, 07.006-20260505-ferc-elibrary-regulatory-filings.md, WISHLIST.md) | 4 reads | ~45023 tok |

## Session: 2026-05-05 03:53

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## 2026-05-05 (T2–T3 outcomes — discovery synthesis pass 2 + scoring pass 2)

- T2: Discovery synthesis pass 2 identified 3 new candidates (FAA NOTAMs Lane 1+5, USDA APHIS Lane 2+4+5, FERC eLibrary Lane 4+5); consciously diversified lane coverage (first Lane 2 and Lane 5 entries). Eight additional candidates dismissed on hard constraints or §5 reconstructibility (Bay Area 511 robots, CMS pricing/Dolthub free aggregator, FCC ULS Akamai gate, etc.). New learnings on Lane-2 conditional-moat, free-aggregator §5 check, Akamai-gated endpoints.
- T3: Scored all 3 new candidates. Composites: FAA 7.898, FERC 7.006, USDA 6.805. All pass §5 with explicit per-lane reasoning (FAA operational-detail fidelity gap, FERC compute-as-barrier + ER, USDA political-vulnerability + archive). Active scored cluster: n=8 (NOTAMs 7.898 > flood-fusion 7.695 > others > rejected NDBC 0.000); exceeds n≥6 threshold deferred in prior calibration.
- Patterns: Lane 2 moat is conditional on archive + political risk. Free public aggregators are §5 reconstructibility. Akamai-gated endpoints need polite-alternate-path discovery before dismissal.

## Session: 2026-05-05 03:55

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-05 03:59

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-05 04:38

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-05 04:39

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-05 04:40

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 04:43 | Created .calibrate_tmp.py | — | ~1130 |
| 04:44 | Created docs/calibration/2026-05-05-n8-pass.md | — | ~2551 |
| 04:45 | Edited FOCUS.md | 3→5 lines | ~404 |
| 04:46 | Session end: 3 writes across 3 files (.calibrate_tmp.py, 2026-05-05-n8-pass.md, FOCUS.md) | 1 reads | ~7954 tok |

## Session: 2026-05-05 04:46

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 04:55 | Edited WISHLIST.md | modified check() | ~2591 |
| 04:55 | Edited WISHLIST.md | modified investigation() | ~1078 |

## 2026-05-05 T2 — Discovery synthesis pass

- Added 2 new WISHLIST.md entries: `osha_enforcement_inspection_corpus` (Lane 2+5) and `multi_state_insurance_dept_enforcement` (Lane 4+5).
- Live-verified on 2026-05-05: OSHA (data.dol.gov + osha.gov HTTP 200, benign robots.txt), NY DFS (HTTP 200, standard Drupal), Missouri DOI (HTTP 429 = rate-limited, data confirmed), NAIC (HTTP 200).
- Dismissed in Notes: CFPB complaint database (data.gov bulk archive collapses §5), Lane 3 investigation (4 candidate fusions examined, all had both inputs fully archived → redirect to Lane 4 or dismiss).
- All 65 tests pass.
| 04:57 | Session end: 2 writes across 1 files (WISHLIST.md) | 2 reads | ~20659 tok |

## Session: 2026-05-05 04:57

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 04:59 | Created .score_tmp.py | — | ~261 |
| 05:02 | Created briefs/candidates/06.723-20260505-osha-enforcement-inspection-corpus.md | — | ~6182 |
| 05:05 | Created briefs/candidates/06.483-20260505-multi-state-insurance-dept-enforcement.md | — | ~6723 |
| 05:05 | Edited WISHLIST.md | 7→7 lines | ~146 |
| 05:05 | Edited WISHLIST.md | 5→5 lines | ~112 |
| 05:06 | Edited FOCUS.md | 3→5 lines | ~430 |
| 05:06 | Session end: 6 writes across 5 files (.score_tmp.py, 06.723-20260505-osha-enforcement-inspection-corpus.md, 06.483-20260505-multi-state-insurance-dept-enforcement.md, WISHLIST.md, FOCUS.md) | 5 reads | ~48755 tok |

## Iteration 20260505T083851Z-d3bb40 (Complete)

**Outcome (2026-05-05 T1–T4):** Calibration pass (n=9, defer-with-rationale, no rubric edits) + 2 discovery passes (5 new candidates, 8 dismissed, lane diversification L1→L2+L5) + scoring (all 5 pass §5, composites 7.898–6.483) + consolidation. Cluster grows n=8→n=10 candidates, exceeds n≥6 deferred-decision threshold but no formula change justified. Key learnings: cluster-stability σ=0.384 (normal), per-lane defensibility reasoning refined (Lane 2 = conditional moat + precedent, Lane 4 = 3 pillars or weak), free aggregators collapse §5, diversity-driven discovery improves rubric confidence. All tests pass (65). FOCUS item 1 complete, Recently completed section updated.

## Session: 2026-05-05 05:06

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 05:08 | Edited FOCUS.md | 3→5 lines | ~276 |
| 05:08 | Session end: 1 writes across 1 files (FOCUS.md) | 1 reads | ~4684 tok |


## Session: 2026-05-05 06:00

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-05 06:01

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-05 06:02

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 06:03 | Created docs/calibration/2026-05-05-n11-defer.md | — | ~726 |
| 06:03 | Edited FOCUS.md | modified briefs() | ~108 |
| 06:04 | Session end: 2 writes across 2 files (2026-05-05-n11-defer.md, FOCUS.md) | 4 reads | ~19965 tok |

## Session: 2026-05-05 06:04

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 06:11 | Edited WISHLIST.md | modified comprehensive() | ~3746 |
| 06:12 | Edited WISHLIST.md | added 2 condition(s) | ~2240 |

## Session: 2026-05-05 T2 (20260505T100037Z-f26efb)

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 10:08 | Discovery synthesis pass — 3 new wishlist candidates added | WISHLIST.md | EPA ECHO + MSHA + NLRB Lane 2+5 (L2 cluster 2→5) | ~5600 |
| 10:08 | Lane-3 stress-tests + 5 dismissals documented | WISHLIST.md Notes | DOL WHD, BLM lease sales, FAA SDR, CDC FluView, USCG MISLE | ~1200 |
| 10:09 | Cerebrum updated with 5 new learnings from this pass | .wolf/cerebrum.md | Lane-2 detail-layer carve-out, Lane 3 null-lane hypothesis, Akamai gating, L5-primary §5 difficulty | ~900 |
| 06:14 | Session end: 2 writes across 1 files (WISHLIST.md) | 1 reads | ~23421 tok |

## Session: 2026-05-05 06:14

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 06:16 | Created .score_t3.py | — | ~126 |
| 06:19 | Created briefs/candidates/06.802-20260505-nlrb-unfair-labor-practice-cases.md | — | ~6176 |
| 06:21 | Created briefs/candidates/06.608-20260505-epa-echo-enforcement-corpus.md | — | ~6476 |
| 06:24 | Created briefs/candidates/06.470-20260505-msha-mine-safety-enforcement-corpus.md | — | ~6319 |
| 06:25 | Edited WISHLIST.md | 6→6 lines | ~108 |
| 06:25 | Edited WISHLIST.md | 6→6 lines | ~119 |
| 06:25 | Edited WISHLIST.md | 5→5 lines | ~118 |
| 06:26 | Edited FOCUS.md | modified briefs() | ~723 |
| 06:26 | Session end: 8 writes across 6 files (.score_t3.py, 06.802-20260505-nlrb-unfair-labor-practice-cases.md, 06.608-20260505-epa-echo-enforcement-corpus.md, 06.470-20260505-msha-mine-safety-enforcement-corpus.md, WISHLIST.md) | 3 reads | ~54580 tok |

## Iteration 20260505T100037Z-f26efb Consolidation (T4)

**Outcome:** Wolf surfaces consolidated. FOCUS.md Recently-completed consolidated into single entry for T1–T3. Anatomy.md updated to reflect iteration's file state. Memory.md appended with consolidated outcome. Cerebrum.md reviewed (no new learnings to add beyond prior T2 updates). All 65 tests pass; git status clean except auto-updated .wolf/ files.

## Session: 2026-05-05 06:26

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 06:27 | Edited FOCUS.md | 5→3 lines | ~347 |
| 06:28 | Session end: 1 writes across 1 files (FOCUS.md) | 1 reads | ~5626 tok |

## Session: 2026-05-05 06:28

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-05 06:32

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-05 07:47

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-05 07:47

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-05 07:48

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 07:49 | Edited docs/calibration/2026-05-05-n8-pass.md | expanded (+21 lines) | ~444 |
| 07:50 | Session end: 1 writes across 1 files (2026-05-05-n8-pass.md) | 2 reads | ~8790 tok |

## Session: 2026-05-05 07:50

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 07:58 | Edited WISHLIST.md | modified check() | ~2833 |
| 07:59 | Edited WISHLIST.md | added 2 condition(s) | ~1512 |
| 08:00 | Session end: 2 writes across 1 files (WISHLIST.md) | 1 reads | ~29851 tok |

## Session: 2026-05-05 08:00

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 08:03 | Created briefs/candidates/07.216-20260505-txdot-drivetexas-cameras.md | — | ~5986 |
| 08:06 | Created briefs/candidates/06.911-20260505-uspto-patent-claim-citation-corpus.md | — | ~7836 |
| 08:07 | Edited WISHLIST.md | 6→6 lines | ~128 |
| 08:07 | Edited WISHLIST.md | 5→5 lines | ~119 |
| 08:08 | Edited FOCUS.md | 3→5 lines | ~663 |
| 08:09 | Session end: 5 writes across 4 files (07.216-20260505-txdot-drivetexas-cameras.md, 06.911-20260505-uspto-patent-claim-citation-corpus.md, WISHLIST.md, FOCUS.md) | 4 reads | ~57044 tok |

## 2026-05-05 (Iteration 20260505T114726Z-af4378 Complete — T1 through T4)

### T1: Calibration pass (n=13 active scored cluster)
- Evaluated cluster stability at n=13 (12 candidates + 1 graduated). Composite range 6.470–7.898 (Δ=1.428), σ≈0.52, range/σ≈2.7.
- Closest pair: medical-board 6.892 / FERC 6.911 (Δ=0.019) — defensible trade-off, does not split decisions.
- Outcome: **defer-with-rationale** — cluster stability observed; no rubric edits justified; new n>15 trigger condition codified in docs/calibration/.

### T2: Discovery synthesis pass
- Identified 2 new wishlist candidates: `txdot_drivetexas_cameras` (Lane 1) + `uspto_patent_claim_citation_corpus` (Lane 4).
- Verified all endpoints live (drivetexas.org HTTP 200, data.uspto.gov HTTP 200). Robots.txt checks clean.
- Lane balance achieved: L1: 5 entries, L2: 5 entries, L4: 6 entries (well-diversified).
- Dismissed 4 candidates on hard constraints / Akamai gating / archived sources.

### T3: Scoring pass (2 new briefs)
- Scored TxDOT and USPTO briefs against RUBRIC.md: **07.216-txdot-drivetexas-cameras** (fin 6.833 / impl 7.000 / hw 8.000), **06.911-uspto-patent-claim-citation-corpus** (fin 7.167 / impl 7.000 / hw 6.500).
- Both pass all 5 CONSTRAINTS hard disqualifiers; no axis-zero rejections.
- WISHLIST entries flipped backlog → promoted-to-candidate.
- Active scored cluster: n=15 candidates + 1 graduated = **16 total. Calibration trigger n>15 CROSSED** — formal calibration pass recommended next iteration.

### T4: Consolidation (this task)
- Updated `.wolf/anatomy.md` to reflect T2/T3 file state (2 new briefs, 1 rejected NDBC).
- Appending `.wolf/memory.md` with consolidated T1–T3 outcomes.
- Updated `.wolf/cerebrum.md` with any new pattern observations (covered in prior sessions, no new entries needed).
- All 65 tests pass; committed on branch with iteration_id.

**Final state:** n=16 briefs (15 scored candidates + 1 graduated); 1 rejected. Cluster composite range 6.470–7.898. Lane balance L1:5 / L2:5 / L4:6 / L5: secondary on most. FOCUS.md item 1 marked complete. Cluster ready for next-iteration formal calibration and continued discovery synthesis.

## Session: 2026-05-05 08:09

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
