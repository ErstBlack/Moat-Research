# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-05-06T15:30:00.000Z
> Files: 91 tracked | Anatomy hits: 0 | Misses: 0

## ../claude-runner/config/projects/faa-alerts/

- `system-prompt.md` — faa-alerts project — additional rules (~493 tok)

## ../faa-alerts/

- `.gitignore` — Git ignore rules (~97 tok)
- `CLAUDE.md` — faa-alerts (~707 tok)
- `README.md` — Project documentation (~675 tok)

## ./

- `.calibrate_tmp.py` (~1130 tok)
- `.pre-commit-config.yaml` (~138 tok)
- `.score_t3.py` — composite (~126 tok)
- `.score_tmp.py` (~261 tok)
- `CLAUDE.md` — OpenWolf (~57 tok)
- `CONSTRAINTS.md` — CONSTRAINTS (~666 tok)
- `FOCUS.md` — FOCUS (~8875 tok)
- `LANES.md` — LANES (~901 tok)
- `RUBRIC.md` — RUBRIC (~861 tok)
- `WISHLIST.md` — WISHLIST (~4909 tok)

## .claude/

- `settings.json` (~441 tok)

## .claude/rules/

- `openwolf.md` (~313 tok)

## .wolf/

- `anatomy.md` — OpenWolf file index (~290 tok)
- `cerebrum.md` — Learning memory: patterns, decisions, do-not-repeat (~2100 tok)
- `memory.md` — Chronological action log (~1800 tok)

## briefs/approved/

- `07.898-20260505-faa-notams-aviation-alerts.md` — Declares researchers (~6803 tok)

## briefs/candidates/

- `06.470-20260505-msha-mine-safety-enforcement-corpus.md` (~6314 tok)
- `06.483-20260505-multi-state-insurance-dept-enforcement.md` (~6717 tok)
- `06.499-20260505-multi-state-attorney-bar-discipline.md` — Declares to (~6696 tok)
- `06.608-20260505-epa-echo-enforcement-corpus.md` (~6476 tok)
- `06.701-20260504-us-transit-gtfsrt-smaller-agencies.md` (~6220 tok)
- `06.723-20260505-osha-enforcement-inspection-corpus.md` (~6182 tok)
- `06.799-20260505-hud-fheo-fair-housing-enforcement.md` (~6100 tok)
- `06.799-20260505-hud-fheo-fair-housing-enforcement.md` — Declares distribution (~5300 tok)
- `06.802-20260505-nlrb-unfair-labor-practice-cases.md` (~6176 tok)
- `06.805-20260505-usda-aphis-animal-welfare-inspections.md` (~6419 tok)
- `06.892-20260504-multi-state-medical-board-enforcement.md` (~5831 tok)
- `06.907-20260506-multi-state-pharmacy-board-enforcement.md` — Declares brief (~6501 tok)
- `06.911-20260505-uspto-patent-claim-citation-corpus.md` (~7836 tok)
- `06.914-20260506-multi-state-real-estate-commission-enforcement.md` — Declares brief (~6634 tok)
- `06.997-20260505-wsdot-traffic-cameras.md` — Declares to (~5556 tok)
- `07.006-20260505-ferc-elibrary-regulatory-filings.md` (~7539 tok)
- `07.009-20260504-cslb-ca-contractor-disciplinary-corpus.md` (~5449 tok)
- `07.063-20260505-ftc-consumer-antitrust-enforcement-corpus.md` (~6500 tok)
- `07.063-20260505-ftc-consumer-antitrust-enforcement-corpus.md` — Declares and (~5255 tok)
- `07.139-20260505-caltrans-quickmap-cameras.md` — Declares to (~5850 tok)
- `07.141-20260506-gdot-ga511-cameras.md` — Declares used (~5922 tok)
- `07.216-20260505-txdot-drivetexas-cameras.md` (~5986 tok)
- `07.274-20260505-cra-exam-narrative-corpus.md` (~6400 tok)
- `07.274-20260505-cra-exam-narrative-corpus.md` — Declares edges (~5479 tok)
- `07.279-20260505-odot-tripcheck-cameras.md` — Declares at (~5368 tok)
- `07.283-20260506-fdot-fl511-cameras.md` (~5617 tok)
- `07.315-20260505-bis-oee-export-enforcement-corpus.md` (~6300 tok)
- `07.315-20260505-bis-oee-export-enforcement-corpus.md` — Declares taxonomy (~5307 tok)
- `07.360-20260504-njdot-511-cameras.md` (~4876 tok)
- `07.509-20260505-sec-enforcement-structured-corpus.md` — Declares filters (~6763 tok)
- `07.898-20260505-faa-notams-aviation-alerts.md` (~6463 tok)

## briefs/graduated/

- `07.221-20260504-somd-cameras.md` — Discovery story (~3777 tok)

## docs/

- `wishlist-dismissals.md` — Wishlist dismissals — full reasoning (~1000 tok)

## docs/calibration/

- `2026-05-05-n11-defer.md` — Calibration check — n=11 active scored cluster (n=10 candidates + 1 graduated) (~681 tok)
- `2026-05-05-n15-pass.md` — Calibration pass — n=15 active scored cluster (n=16 incl. graduated) (~3709 tok)
- `2026-05-05-n25-pass.md` — Calibration Pass — n≥25 Cluster (2026-05-05) (~1625 tok)
- `2026-05-05-n8-pass.md` — Calibration pass — n=8 active scored cluster (n=9 incl. graduated) (~2708 tok)

## docs/superpowers/specs/

- `2026-05-04-moat-research-design.md` — moat-research (~7373 tok)

## scripts/

- `politeness_lint.py` — lint, main (~555 tok)

## stacks/

- `moat-research.yml` — Single-node Docker swarm stack for moat-research workers. (~546 tok)

## tests/fixtures/

- `brief_approved.md` (~361 tok)
- `brief_candidate_unscored.md` (~147 tok)
- `brief_valid_scored.md` (~360 tok)
- `brief_zero_financial.md` (~360 tok)
- `brief_zero_hardware.md` (~359 tok)
- `brief_zero_implementation.md` (~360 tok)
- `sources_clean.yml` (~54 tok)
- `sources_missing_rate_budget.yml` (~46 tok)

## tests/integration/

- `test_lifecycle.py` — repo, test_scored_to_rejected_path, test_scored_to_approved_to_init_prompt_path, test_promoter_index (~845 tok)

## tests/unit/

- `test_brief.py` — TestCompositeScore: test_all_tens_returns_ten, test_zero_financial_returns_zero, test_zero_implement (~1633 tok)
- `test_coordinator.py` — TestTokenBucket: test_first_request_succeeds, test_capacity_limit, test_refill_over_time, test_unkno (~518 tok)
- `test_indexer.py` — TestIndexer: repo, test_empty_repo_writes_empty_index, test_single_brief_indexed, test_briefs_from_a (~810 tok)
- `test_ingest_base.py` — TestThrottleClient: test_consume_calls_coordinator, fake_get, json, test_consume_returns_false_on_42 (~895 tok)
- `test_init_prompt_gen.py` — TestInitPromptGen: repo, test_renders_for_approved_brief, test_idempotent, test_skips_non_approved_s (~528 tok)
- `test_politeness_lint.py` — TestPolitenessLint: test_clean_passes, test_missing_rate_budget_violates, test_missing_url_violates, (~680 tok)
- `test_promoter.py` — TestPromoter: repo, test_valid_brief_stays_in_scored, test_zero_financial_moves_to_rejected, test_ze (~828 tok)

## workers/common/

- `brief.py` — class: composite_score, format_score_prefix, filename_for, parse_brief + 3 more (~1462 tok)
- `throttle.py` — _Resp: json, consume (~349 tok)

## workers/coordinator/

- `coordinator.py` — from: consume, from_yaml, consume, make_handler + 3 more (~956 tok)
- `Dockerfile` — Docker container definition (~70 tok)

## workers/indexer/

- `Dockerfile` — Docker container definition (~68 tok)
- `indexer.py` — rebuild, main (~530 tok)

## workers/ingest/

- `base.py` — for: fetch_one, write, healthcheck, startup + 1 more (~893 tok)
- `Dockerfile.base` — Base image for ingestor services. Concrete ingestors FROM this and add their (~75 tok)

## workers/init_prompt_gen/

- `Dockerfile` — Docker container definition (~77 tok)
- `init_prompt_gen.py` — render, sweep, main (~1137 tok)
- `template.md` — Project init prompt: $title (~1309 tok)

## workers/promoter/

- `Dockerfile` — Docker container definition (~70 tok)
- `promoter.py` — sweep, main (~625 tok)
