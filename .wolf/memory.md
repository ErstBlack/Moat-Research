# Memory

> Chronological action log. Hooks and AI append to this file automatically.
> Old sessions are consolidated by the daemon weekly.

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
