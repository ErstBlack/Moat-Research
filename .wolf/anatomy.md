# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-05-08T05:31:47.624Z
> Files: 131 tracked | Anatomy hits: 0 | Misses: 0

## ./

- `.gitignore` — Git ignore rules (~160 tok)
- `CLAUDE.md` — OpenWolf (~1315 tok)
- `pyproject.toml` — Solo-operator CLI for discovering, scoring, and graduating data-moat opportunities (~304 tok)
- `README.md` — Project documentation (~662 tok)
- `WISHLIST.md` — WISHLIST (~571 tok)

## .claude/

- `settings.json` (~441 tok)

## .claude/rules/

- `openwolf.md` (~313 tok)

## .rtk/

- `filters.toml` — Project-local RTK filters — commit this file with your repo. (~136 tok)

## .ruff_cache/

- `.gitignore` — Git ignore rules (~10 tok)
- `CACHEDIR.TAG` (~12 tok)

## .ruff_cache/0.15.12/

- `18249801856637738460` (~623 tok)
- `601945587809881093` (~531 tok)

## docs/superpowers/plans/

- `2026-05-07-moat-research-implementation.md` — moat-research Implementation Plan (~72771 tok)
- `2026-05-08-max-subscription-port.md` — Max-Subscription Port Implementation Plan (~14423 tok)

## docs/superpowers/specs/

- `2026-05-07-moat-research-design.md` — moat-research — design (greenfield, v2) (~13027 tok)
- `2026-05-08-max-subscription-port-design.md` — Max-Subscription Port — Design (~3709 tok)

## mr/

- `__init__.py` — moat-research: solo-operator CLI for data-moat opportunities. (~26 tok)
- `__main__.py` (~19 tok)

## mr/cli/

- `__init__.py` (~0 tok)
- `discover.py` — mr discover — generate candidate briefs from WISHLIST + live web tools. (~2339 tok)
- `gain.py` — mr gain — summarize spend from costs.jsonl. (~311 tok)
- `graduate.py` — mr graduate — emit hand-off prompt and move approved → graduated. (~538 tok)
- `init.py` — mr init — bootstrap repo layout, mr.yaml, prompts/, WISHLIST.md. (~302 tok)
- `main.py` — Entry point for the `mr` CLI. (~1140 tok)
- `promote.py` — mr promote — move a scored brief to approved/. (~241 tok)
- `reject.py` — mr reject — move scored brief to rejected/ with operator reason. (~308 tok)
- `score.py` — mr score — score, verify, route to scored/ or rejected/. (~2460 tok)
- `status.py` — mr status — counts per dir, stale-approved warning, top-mined hosts. (~596 tok)
- `wishlist.py` — mr wishlist {add, expand, refresh} subcommand group. (~606 tok)

## mr/dedup/

- `__init__.py` (~0 tok)
- `niche_key.py` — niche_key normalization with alias resolution. (~473 tok)
- `seen.py` — seen.jsonl canonical dedup artifact. (~2263 tok)
- `summary.py` — Bounded pre-pended summary block for mr discover and mr wishlist expand. (~1180 tok)

## mr/handoff/

- `__init__.py` (~0 tok)
- `adjacent_rejections.py` — Adjacent-rejection appendix for hand-off prompts. (~377 tok)
- `feature.py` — Hand-off prompt builder for delivery_form: feature (patch proposal). (~349 tok)
- `project.py` — Hand-off prompt builder for delivery_form: project (fresh project init). (~429 tok)

## mr/lifecycle/

- `__init__.py` (~0 tok)
- `filename.py` — Filename convention for briefs. (~993 tok)
- `frontmatter.py` — Brief frontmatter parser, writer, and validator. (~1769 tok)
- `paths.py` — Repo layout — lifecycle directory names and path resolution. (~784 tok)
- `transitions.py` — Atomic lifecycle transitions via os.replace. (~225 tok)

## mr/scoring/

- `__init__.py` (~0 tok)
- `auto_reject.py` — Auto-reject decisions and the §5.5 normative reason-string table. (~897 tok)
- `rubric.py` — 4-axis weighted geometric mean composite. (~453 tok)

## mr/synth/

- `__init__.py` (~0 tok)
- `budget.py` — Four-tier budget enforcement + cold-corpus preflight. (~1690 tok)
- `client.py` — Anthropic SDK client wrapper with mandatory prompt caching. (~1063 tok)
- `dispatch.py` — Dispatch custom tool calls received from the LLM. (~596 tok)
- `mcp_server.py` — In-process MCP server wrapping the project's custom tools. (~2338 tok)
- `pricing.py` — Per-model token pricing lookup. (~341 tok)
- `prompts.py` — Prompt loader. Reads from prompts/ on each invocation, no compilation. (~152 tok)
- `tools.py` — Tool definitions for Anthropic API requests. (~1024 tok)
- `verify.py` — Host-driven disqualifier verification. (~1504 tok)

## mr/tools/

- `__init__.py` (~0 tok)
- `head.py` — HTTP HEAD wrapper for liveness checks. (~404 tok)
- `robots.py` — robots.txt check using urllib.robotparser. (~264 tok)
- `seen_lookup.py` — seen_lookup custom tool: query seen.jsonl for matches and near-matches. (~725 tok)
- `wayback.py` — Wayback Machine CDX API wrapper. (~386 tok)

## mr/util/

- `__init__.py` (~0 tok)
- `config_schema.json` (~973 tok)
- `config.py` — mr.yaml loader with JSON-Schema validation, schema-version-1-only. (~1387 tok)
- `costs.py` — costs.jsonl writer and reader for spend tracking. (~569 tok)
- `lock.py` — POSIX flock(2)-based exclusive lock for .moat-research/.lock. (~472 tok)
- `slug.py` — Slug normalization for filenames and identifiers. (~228 tok)

## mr/wishlist/

- `__init__.py` (~0 tok)
- `add.py` — Append a source to WISHLIST.md after validation. (~347 tok)
- `expand.py` — mr wishlist expand — LLM-driven source proposal. (~1692 tok)
- `refresh.py` — mr wishlist refresh — deterministic re-verification of WISHLIST sources. (~340 tok)
- `schema.py` — WISHLIST.md schema and loader. (~909 tok)

## prompts/

- `discover.md` — moat-research: mr discover (~1293 tok)
- `score.md` — moat-research: mr score (~741 tok)
- `wishlist_expand.md` — moat-research: mr wishlist expand (~502 tok)

## tests/

- `__init__.py` (~0 tok)
- `conftest.py` — Shared pytest fixtures for moat-research tests. (~71 tok)
- `test_package.py` — Tests: mr_imports, cli_main_app_callable (~45 tok)
- `test_prompts_content.py` — Tests: discover_prompt_mandates_seen_lookup, discover_prompt_lists_all_lanes, discover_prompt_mandates_hardware_keys, discover_prompt_mentions_dive... (~430 tok)

## tests/cli/

- `__init__.py` (~0 tok)
- `test_discover.py` — Tests: discover_aborts_on_empty_wishlist, discover_aborts_when_anthropic_api_key_missing, discover_dispatches_to_loop (~579 tok)
- `test_gain.py` — Tests: gain_empty, gain_summarizes_costs (~344 tok)
- `test_graduate.py` — Tests: graduate_project_emits_init_prompt, graduate_feature_emits_patch_prompt, graduate_idempotent_on_already_graduated (~662 tok)
- `test_init.py` — Tests: init_creates_dirs, init_creates_default_mr_yaml, init_creates_default_wishlist, init_idempotent (~409 tok)
- `test_promote.py` — Tests: promote_moves_to_approved, promote_nonexistent_fails (~438 tok)
- `test_reject.py` — Tests: reject_writes_manual_reason, reject_without_reason_uses_blank (~506 tok)
- `test_score.py` — Tests: score_routes_to_rejected_when_hw_keys_missing, score_routes_to_scored_when_predicates_pass, score_floor_rejection_low_defensibility (~964 tok)
- `test_status.py` — Tests: status_empty, status_counts, status_stale_approved_warning, status_other_lane_flagged (~778 tok)
- `test_wishlist_cli.py` — Tests: wishlist_add_via_cli, wishlist_refresh_via_cli, wishlist_expand_via_cli (~379 tok)

## tests/dedup/

- `__init__.py` (~0 tok)
- `test_niche_key.py` — Tests: lowercase, strips_punctuation_and_collapses_whitespace, sorts_tokens_alphabetically, unicode_to_ascii + 4 more (~410 tok)
- `test_seen.py` — Tests: regenerate_empty_repo, regenerate_with_one_brief, regenerate_recomputes_niche_key_from_aliases, partial_move_recovery + 6 more (~1434 tok)
- `test_summary.py` — Tests: empty_corpus_yields_minimal_block, small_corpus_uses_full_index, large_corpus_uses_bounded_summary, lane_niche_freq_excludes_other_lane + 3 ... (~784 tok)

## tests/handoff/

- `__init__.py` (~0 tok)
- `test_adjacent_rejections.py` — Tests: appendix_severity_ranks_hard_disqualifier_first, appendix_capped_at_3, appendix_filters_to_matching_lane_niche, appendix_empty_when_no_matches (~660 tok)
- `test_feature.py` — Tests: feature_handoff_mentions_parent_project, feature_handoff_first_action_reads_existing_repo (~388 tok)
- `test_project.py` — Tests: project_handoff_includes_hardware_envelope, project_handoff_includes_brief_body, project_handoff_first_action_prompt, project_handoff_includ... (~480 tok)

## tests/integration/

- `__init__.py` (~0 tok)
- `test_e2e.py` — End-to-end smoke test: init → seeded WISHLIST → discover (mocked LLM) (~1347 tok)

## tests/lifecycle/

- `__init__.py` (~0 tok)
- `test_filename.py` — Tests: composite_padded_basic, composite_padded_zero, composite_padded_max, composite_padded_rounds_half_to_nearest + 11 more (~893 tok)
- `test_frontmatter.py` — Tests: read_minimal_brief, extract_thesis_first_sentence, source_set_dedups_by_host, write_then_read_roundtrip + 7 more (~1700 tok)
- `test_paths.py` — Tests: lifecycle_dir_set, dispositions_match_dirs, disposition_for_dir, repo_layout + 4 more (~656 tok)
- `test_transitions.py` — Tests: move_candidate_to_scored, move_to_existing_dest_raises, move_creates_dest_parent_if_missing, move_missing_source_raises (~458 tok)

## tests/scoring/

- `__init__.py` (~0 tok)
- `test_auto_reject.py` — Tests: reason_strings_are_normative, decide_floor_rejection_low_defensibility, decide_floor_rejection_axis_zero, decide_floor_rejection_defensibili... (~800 tok)
- `test_rubric.py` — Tests: default_weights_sum_to_one, all_tens_gives_ten, all_zeros_gives_zero, any_axis_zero_zeros_composite + 6 more (~629 tok)

## tests/synth/

- `__init__.py` (~0 tok)
- `test_budget.py` — Tests: worst_case_ceiling_for_discover_fits_5usd_budget, worst_case_ceiling_for_score_fits_3usd, per_turn_estimate_aborts_at_90pct, tool_turn_cap_a... (~1116 tok)
- `test_client.py` — Tests for mr.synth.client — SynthClient and build_cached_blocks. (~923 tok)
- `test_dispatch.py` — Tests: seen_lookup_dispatched, wayback_dispatched, robots_dispatched, unknown_tool_returns_error (~471 tok)
- `test_mcp_server.py` — Tests for mr.synth.mcp_server tool factories. (~1185 tok)
- `test_pricing.py` — Tests: default_opus_pricing, default_sonnet_pricing, unknown_model_raises, estimate_input_cost_usd (~320 tok)
- `test_prompts.py` — Tests: load_existing, load_missing_raises (~133 tok)
- `test_tools.py` — test_native_tools_have_anthropic_types, test_custom_seen_lookup_schema, test_tools_for_discover_has_ (~495 tok)
- `test_verify.py` — Tests: single_source_predicate_le_1, single_source_passes_with_two_distinct_hosts, single_source_counter_evidence_excluded, unrestricted_archives_p... (~3322 tok)

## tests/tools/

- `__init__.py` (~0 tok)
- `test_head.py` — Tests: returns_status_and_headers, 4xx_status, network_error (~412 tok)
- `test_robots.py` — URL configuration (~458 tok)
- `test_seen_lookup.py` — Tests: exact_slug_match, exact_source_set_match, exact_lane_niche_match, near_match_source_set_subset + 4 more (~836 tok)
- `test_wayback.py` — Tests: returns_count_first_last, no_snapshots, years_helper (~482 tok)

## tests/util/

- `__init__.py` (~0 tok)
- `test_config.py` — Tests for mr.util.config. (~636 tok)
- `test_costs.py` — Tests: append_and_read_roundtrip, appends_to_existing_file, running_total_for_command, jsonl_format_one_object_per_line (~700 tok)
- `test_lock.py` — Tests: acquires_and_releases, blocks_then_times_out, creates_parent_dir, releases_on_exception_in_with_block (~513 tok)
- `test_slug.py` — Tests: basic_lowercase_kebab, strips_punctuation, max_40_chars, truncates_at_word_boundary + 3 more (~239 tok)

## tests/wishlist/

- `__init__.py` (~0 tok)
- `test_add.py` — Tests: add_to_empty, add_duplicate_rejected, add_invalid_kebab_rejected (~372 tok)
- `test_expand.py` — Tests: format_proposal_renders_yaml_blocks, format_proposal_empty (~190 tok)
- `test_refresh.py` — Tests: 2xx_updates_last_verified, 4xx_does_not_update_last_verified, two_consecutive_failures_within_window_marks_dead, failures_outside_window_res... (~819 tok)
- `test_schema.py` — Tests: load_empty, load_with_sources, invalid_id_kebab, duplicate_id_rejected + 2 more (~570 tok)
