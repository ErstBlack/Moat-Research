# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-05-05T07:52:40.945Z
> Files: 51 tracked | Anatomy hits: 0 | Misses: 0

## ./

- `.pre-commit-config.yaml` (~138 tok)
- `.score_tmp.py` — c (~43 tok)
- `CLAUDE.md` — OpenWolf (~57 tok)
- `CONSTRAINTS.md` — CONSTRAINTS (~398 tok)
- `FOCUS.md` — FOCUS (~3659 tok)
- `RUBRIC.md` — RUBRIC (~861 tok)
- `WISHLIST.md` — WISHLIST (~13775 tok)

## .claude/

- `settings.json` (~441 tok)

## .claude/rules/

- `openwolf.md` (~313 tok)

## briefs/candidates/

- `06.701-20260504-us-transit-gtfsrt-smaller-agencies.md` — Declares reference (~5831 tok)
- `06.805-20260505-usda-aphis-animal-welfare-inspections.md` — Declares vetting (~6018 tok)
- `06.892-20260504-multi-state-medical-board-enforcement.md` — Declares cross (~5467 tok)
- `07.006-20260505-ferc-elibrary-regulatory-filings.md` (~7068 tok)
- `07.009-20260504-cslb-ca-contractor-disciplinary-corpus.md` (~5108 tok)
- `07.360-20260504-njdot-511-cameras.md` — Declares on (~4571 tok)
- `07.600-20260504-ndbc-realtime-buoys.md` (~5882 tok)
- `07.771-20260504-usgs-nws-flood-fusion.md` (~6892 tok)
- `07.898-20260505-faa-notams-aviation-alerts.md` — Declares researchers (~6059 tok)

## briefs/graduated/

- `07.221-20260504-somd-cameras.md` — Discovery story (~3777 tok)

## docs/superpowers/specs/

- `2026-05-04-moat-research-design.md` — moat-research (~7094 tok)

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
- `init_prompt_gen.py` — render, sweep, main (~932 tok)
- `template.md` — Project init prompt: $title (~705 tok)

## workers/promoter/

- `Dockerfile` — Docker container definition (~70 tok)
- `promoter.py` — sweep, main (~625 tok)
