# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-05-04T22:52:42.932Z
> Files: 37 tracked | Anatomy hits: 0 | Misses: 0

## ./

- `.pre-commit-config.yaml` (~138 tok)
- `CLAUDE.md` — OpenWolf (~57 tok)
- `FOCUS.md` — FOCUS (~3258 tok)

## .claude/

- `settings.json` (~441 tok)

## .claude/rules/

- `openwolf.md` (~313 tok)

## briefs/graduated/

- `07.221-20260504-somd-cameras.md` — Discovery story (~3777 tok)

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
