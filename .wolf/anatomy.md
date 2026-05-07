# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-05-07T19:50:55.363Z
> Files: 35 tracked | Anatomy hits: 0 | Misses: 0

## ./

- `.gitignore` — Git ignore rules (~160 tok)
- `CLAUDE.md` — OpenWolf (~1315 tok)
- `pyproject.toml` — Solo-operator CLI for discovering, scoring, and graduating data-moat opportunities (~292 tok)
- `uv.lock` — uv lockfile for 42 resolved packages, Python 3.14+ (~1484 tok)
- `WISHLIST.md` — WISHLIST (~571 tok)

## .claude/

- `settings.json` (~441 tok)

## .claude/rules/

- `openwolf.md` (~313 tok)

## .rtk/

- `filters.toml` — Project-local RTK filters — commit this file with your repo. (~136 tok)

## docs/superpowers/plans/

- `2026-05-07-moat-research-implementation.md` — moat-research Implementation Plan (~72771 tok)

## docs/superpowers/specs/

- `2026-05-07-moat-research-design.md` — moat-research — design (greenfield, v2) (~13027 tok)

## mr/

- `__init__.py` — moat-research: solo-operator CLI for data-moat opportunities. (~26 tok)
- `__main__.py` (~19 tok)

## mr/cli/

- `__init__.py` (~0 tok)
- `main.py` — Entry point for the `mr` CLI. (~149 tok)

## mr/dedup/

- `__init__.py` (~0 tok)

## mr/handoff/

- `__init__.py` (~0 tok)

## mr/lifecycle/

- `__init__.py` (~0 tok)

## mr/scoring/

- `__init__.py` (~0 tok)

## mr/synth/

- `__init__.py` (~0 tok)

## mr/tools/

- `__init__.py` (~0 tok)

## mr/util/

- `__init__.py` (~0 tok)
- `config_schema.json` (~973 tok)
- `config.py` — mr.yaml loader with JSON-Schema validation, schema-version-1-only. (~1387 tok)
- `costs.py` — costs.jsonl writer and reader for spend tracking. (~518 tok)
- `lock.py` — POSIX flock(2)-based exclusive lock for .moat-research/.lock. (~472 tok)
- `slug.py` — Slug normalization for filenames and identifiers. (~228 tok)

## mr/wishlist/

- `__init__.py` (~0 tok)

## tests/

- `__init__.py` (~0 tok)
- `conftest.py` — Shared pytest fixtures for moat-research tests. (~71 tok)
- `test_package.py` — test_mr_imports, test_cli_main_app_callable (~45 tok)

## tests/util/

- `__init__.py` (~0 tok)
- `test_config.py` — Tests for mr.util.config. (~636 tok)
- `test_costs.py` — test_append_and_read_roundtrip, test_appends_to_existing_file, test_running_total_for_command, test_ (~708 tok)
- `test_lock.py` — test_acquires_and_releases, test_blocks_then_times_out, test_creates_parent_dir, test_releases_on_ex (~513 tok)
- `test_slug.py` — test_basic_lowercase_kebab, test_strips_punctuation, test_max_40_chars, test_truncates_at_word_bound (~239 tok)
