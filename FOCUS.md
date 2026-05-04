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
- **Implementation plan** — `docs/superpowers/plans/2026-05-04-moat-research-implementation.md` — 17 task plan with TDD steps, file structure, and self-review checklist. Source of truth for Item 0 below.

## Active queue

### 0. [x] Finish the moat-research implementation (Tasks 5–17) — DONE 2026-05-04

Note: Tasks 5–17 implemented and committed on branch `maximizer/moat/20260504T061153Z-8c8eb4`. All 65 tests pass; pre-commit hooks green; politeness lint exits 0; docker stack config validates. Ready to merge to master.



**Plan:** `docs/superpowers/plans/2026-05-04-moat-research-implementation.md`
**Spec:** `docs/superpowers/specs/2026-05-04-moat-research-design.md`

**Why first:** The project is partially scaffolded but the workers do not yet exist. Items 1–3 below assume a working corpus + worker stack — rescoring somd-cameras requires the brief schema, score formula, and filename convention from `workers/common/brief.py`. Until Tasks 5–17 of the implementation plan are complete, no synthesis work can produce a properly-formatted graduated brief.

**Where things were left off (state at 2026-05-04):**

- **Implementation plan**: `docs/superpowers/plans/2026-05-04-moat-research-implementation.md` (17 tasks).
- **Tasks 1–4 complete**:
  - T1 — git repo init + `pyproject.toml`/`uv` setup (commit `2c3221f`).
  - T2 — canonical docs `RUBRIC.md`, `LANES.md`, `CONSTRAINTS.md`, `SEED_NOTES.md`, `README.md`, `CLAUDE.md` (commit `9f75f74`). Pre-existing OpenWolf/RTK `CLAUDE.md` was overwritten on purpose.
  - T3 — directory skeleton: `briefs/{candidates,scored,rejected,approved,graduated}/.gitkeep`, `signals/{raw,digests}/.gitkeep`, `signals/sources.yml` (empty list), all worker package `__init__.py` files (commit `7e94bea`).
  - T4 — per-project orchestrator preamble at `/home/runner/claude-runner/config/projects/moat-research/system-prompt.md` (committed in the **claude-runner** repo, not here; tightened to ~1156 B in a follow-up commit).
- **Tasks 5–17 outstanding**, in order:
  - T5 `workers/common/brief.py` — `composite_score()` (TDD). **This is where execution stopped.**
  - T6 — filename `format_score_prefix` / `filename_for` / `parse_score_prefix` (TDD).
  - T7 — Brief dataclass + `parse_brief` / `write_brief` / `failed_axis` + fixtures (TDD).
  - T8 — promoter worker (`scored → rejected` on any-axis-zero, quarantine on parse fail).
  - T9 — indexer worker (`briefs/index.json` regenerator).
  - T10 — init-prompt-gen worker + `template.md`.
  - T11 — coordinator (token-bucket throttle HTTP service).
  - T12 — `BaseIngestor` + `ThrottleClient` contract test.
  - T13 — `scripts/politeness_lint.py`.
  - T14 — end-to-end lifecycle integration test (and an indexer patch to skip `.init-prompt.md` artifacts).
  - T15 — Dockerfiles for the 4 workers + ingest base.
  - T16 — `stacks/moat-research.yml` (single-node swarm stack).
  - T17 — `.pre-commit-config.yaml` wiring lint + pytest, full smoke test.
- **Git state of moat-research**: branch `main`, 3 commits as above. No worktrees, no branches off main, no uncommitted work. Existing untracked dirs (`.claude/`, `.rtk/`, `.wolf/`) are scaffolding from other tools and remain intentionally untracked.
- **Git state of claude-runner**: `config/projects/moat-research/system-prompt.md` registered (2 commits — initial + tightening). No further changes pending.
- **Execution mode used so far**: subagent-driven development (`superpowers:subagent-driven-development`) with implementer → spec reviewer → (code quality reviewer when surface > pure prose) → next task. Resume with the same flow.

**Acceptance criteria:**

1. All 17 tasks of the implementation plan are checked off and committed to `main` of `/home/runner/moat-research`.
2. `cd /home/runner/moat-research && uv run pytest -v` passes (unit + integration).
3. `uv run python scripts/politeness_lint.py signals/sources.yml` exits `0` with the empty registry.
4. `docker stack config -c stacks/moat-research.yml` validates without error.
5. The five Dockerfiles (`promoter`, `indexer`, `init_prompt_gen`, `coordinator`, `ingest/Dockerfile.base`) all build cleanly.
6. `.pre-commit-config.yaml` is in place and `uv run pre-commit run --all-files` passes.
7. `git status` is clean (modulo the always-untracked scaffolding dirs).

**Out of scope for this item:** producing the somd-cameras brief, seeding the wishlist, registering any concrete ingest sources. Those are Items 1, 2 (now 3 below), and 3 (now 4) — they execute *after* this is done.

---

### 1. [x] Rescore `somd-cameras` against the current rubric, before any other research — DONE 2026-05-04

Note: Brief written to `briefs/graduated/07.221-20260504-somd-cameras.md`. Composite 7.221 (financial 6.667 × implementation 7.25 × hardware 8.0). All five disqualifiers re-checked against `/home/runner/somd-cameras/` and `chart.maryland.gov` (robots.txt 404 on 2026-05-04, no ToS clause forbidding archival located). Calibration note recommends NO rubric edits at this time; revisit financial-axis weighting only after ≥3 more lane-1 candidates have been scored.

**Spec reference:** `docs/superpowers/specs/2026-05-04-moat-research-design.md` §5 (rubric), §7.1 (brief schema), §12 (seeding).

**Why first:** `somd-cameras` is the archetype this project was built to find more of. Until it has been formally scored under `RUBRIC.md`, the rubric itself is unvalidated — we don't know whether the formula and weights actually rank a known-good moat highly. Rescoring it is both a correctness check on the scoring system and the production of the canonical seed/reference brief that future synthesis runs pattern-match against.

**Acceptance criteria:**

1. A new brief file exists at `briefs/graduated/<composite>-<yyyymmdd>-somd-cameras.md`, conforming to the frontmatter schema in the design spec §7.1.
2. `lane: 1` (ephemeral public data), with `secondary_lanes` set if cross-source fusion or derived-artifact aspects apply.
3. `source_signals` cites the existing `somd-cameras` repo (`/home/runner/somd-cameras/`) and at least one external reference (e.g., CHART's own published feed page, or evidence that CHART does not retain footage).
4. All three feasibility axes are scored with **per-sub-criterion justifications grounded in observable facts** about the existing project — storage growth rate from actual disk usage, compute profile from actual stack files, buyer/pricing assumptions from explicit reasoning (not vibes). Where a sub-criterion can't be grounded, mark it `null` and note why; do not guess.
5. `composite_score` is computed using the formula in spec §5.4 and matches the score in the filename prefix to three decimals.
6. `disqualifiers_checked` is fully populated with `false` values *and* a one-line note for each, citing the evidence (e.g., `tos_robots_violations: false  # CHART feed page lists no robots restrictions; verified <date>`).
7. `graduated_to: somd-cameras` is set, with a relative path or absolute reference to the project location.
8. The markdown body below the frontmatter contains a **discovery story** (how this moat was originally noticed) and a **rubric calibration note** — does the resulting composite score feel right relative to operator intuition? If it feels too low or too high, propose specific weight or sub-criterion changes in `RUBRIC.md` rather than fudging the score.
9. If the calibration note recommends a rubric change, do **not** apply it unilaterally — leave a follow-up focus item below this one for the operator to approve.

**Out of scope for this item:** discovering new moats, scoring anything else, generating init-prompts, modifying the cameras project itself.

---

### 2. [x] Bootstrap the maximizer-facing context surfaces — DONE 2026-05-04

Note: system-prompt.md committed to `/home/runner/claude-runner/config/projects/moat/` (directory named `moat` not `moat-research` per actual config structure); 684B, under 1 KB limit. CLAUDE.md already has @-imports; RUBRIC.md, LANES.md, CONSTRAINTS.md present at repo root.

**Spec reference:** `docs/superpowers/specs/2026-05-04-moat-research-design.md` §9.6 (how the overall concept reaches maximizer), §12 (seeding).

**Why:** Until the orchestrator has a per-project preamble and `CLAUDE.md` for `moat-research`, every iteration starts cold and has to re-derive the project thesis. This is one-time setup work that unblocks everything after Item 1.

**Acceptance criteria:**

1. ✓ `/home/runner/claude-runner/config/projects/moat/system-prompt.md` exists (684B, <1 KB), modeled on `cameras/system-prompt.md`. States: project thesis (one paragraph); the four hardest rules (no model calls in this repo; never auto-promote `scored→approved`; FOCUS.md is the priority override; respect rate limits / ToS / robots.txt); pointers to `RUBRIC.md`, `LANES.md`, `CONSTRAINTS.md`, `WISHLIST.md`.
2. ✓ `/home/runner/moat-research/CLAUDE.md` exists with `@`-imports for `FOCUS.md`, `WISHLIST.md`, `RUBRIC.md`, `LANES.md`, `CONSTRAINTS.md`. The OpenWolf and RTK preludes already present in the repo are preserved.
3. ✓ `RUBRIC.md`, `LANES.md`, `CONSTRAINTS.md` files exist at the repo root, each derived verbatim from §3–§5 of `docs/superpowers/specs/2026-05-04-moat-research-design.md`. They reference the spec section they came from at the top.
4. ✓ Item 2 runs **after** Item 1 — the rescore in Item 1 may surface rubric calibration changes; if so, the rubric edits should be merged before §3–§5 is mirrored into `RUBRIC.md`.

**Out of scope:** the workers (`promoter`, `indexer`, `init-prompt-gen`, ingestors), `stacks/moat-research.yml`, and any signal source registration. Those belong in the implementation plan, not in the bootstrap.

---

### 3. [ ] Seed `WISHLIST.md` with 3–5 known-promising sources

**Spec reference:** `docs/superpowers/specs/2026-05-04-moat-research-design.md` §7.3 (wishlist schema and lifecycle).

**Why:** `maximizer:discover` needs real material to work against on its first organic synthesis run; an empty wishlist degenerates into pure cold-start ideation. Three to five operator-curated entries make the first pass productive.

**Acceptance criteria:**

1. `WISHLIST.md` contains ≥3 and ≤5 entries under `sources:`, each conforming to the schema in the file's "How to append" section.
2. Entries span at least 2 different lanes (so the rubric isn't validated against only one shape of opportunity).
3. Each entry has a non-trivial `why_interesting` (not "looks cool") and a `known_constraints` that has actually been checked, not guessed (operator may use WebFetch / WebSearch to verify before appending).
4. No entry violates a hard constraint from `CONSTRAINTS.md`. If any candidate did, that candidate is dismissed in a one-line entry under `## Notes for the operator` of `WISHLIST.md` rather than silently dropped.
5. Item 3 runs **after** Item 2 — `WISHLIST.md` should exist as a real interface before being seeded.

**Out of scope:** scoring these sources, turning them into briefs, registering them in `signals/sources.yml`. Those happen later, organically.

---

## Recently completed

*(empty — populated as items are finished and before garbage collection in subsequent iterations)*

## Notes for the operator

- `FOCUS.md` is meant to be terse. If a focus item needs more than a few paragraphs of context, link to a doc under `docs/` rather than inlining it here.
- Treat this file like a sticky-note pad on top of the project. Long-running themes belong in the design spec; short-lived priorities belong here.
