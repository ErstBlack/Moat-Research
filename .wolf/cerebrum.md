# Cerebrum

> OpenWolf's learning memory. Updated automatically as the AI learns from interactions.
> Do not edit manually unless correcting an error.
> Last updated: 2026-05-07

## User Preferences

- **Strict on defensibility.** A "moat" must survive a focused quarter of competitor effort with capital + compute. Theoretical defensibility is rejected. Anything a well-funded company can replicate within ~13 weeks does not count. Encoded as `defensibility ≤ 4 → auto-reject` in the v2 rubric.
- **Solo-operator scope.** Prefers single-CLI form factor over multi-project orchestration; rejects daemons, cron, swarms, coordinators, and shared-state designs across sibling repos.
- **Self-contained synthesis.** moat-research owns its LLM caller; no dependency on a separate "maximizer" or any other project for synthesis.
- **Hand-off via init-prompt.** Graduated briefs leave the repo and run as a fresh project directory; moat-research does not scaffold inside its own tree.
- **Greenfield restart over migration.** When given a stale corpus (26 prior briefs at session start), preferred discarding all and restarting clean over partial migration.
- **Dedup is mandatory in any LLM-driven discovery loop.** Without an explicit cross-run check against summarized prior output, the LLM keeps re-proposing the same ideas. Operator considers re-proposing identical/very-similar ideas a defect, not noise.
- **Dedup must be synthesis-friendly.** Re-using a familiar source in a new combination (`cross_source_fusion`) is *encouraged*, not penalized. The dedup key is the **set of source hosts** for the brief (primary + corroborating + counter-evidence), not any single host. Single-host overlap → not a duplicate; exact source-set match → duplicate.
- **Minimize prompt-context spend on derived data.** Operator pushes back on designs that pre-pend ever-growing derived state (e.g., a 25k-token seen-index at n=500). Prefer two-tier: small bounded summary in the prompt + a custom tool the model calls on demand for precise checks against the full artifact.

## Key Learnings

- **Project:** moat-research — solo-operator CLI + structured corpus for discovering, scoring, promoting data-moat opportunities. Lifecycle: `candidates/ → scored/ → {rejected, approved} → graduated/`. Filenames are score-prefixed: `<composite_padded>-<yyyymmdd>-<slug>.md`.
- **Anthropic 2026 native server tools** are the right default: `web_search_20260209` ($10/1k searches), `web_fetch_20260209` (with dynamic filtering — model writes code to filter content before it enters context), and `code_execution` (FREE when bundled with web_search or web_fetch). Available on Opus 4.7, Sonnet 4.6.
- **`code_execution` is essentially free Python** when the call already includes web tools. Use it aggressively for deterministic checks (robots.txt parsing, rate-budget arithmetic, dedup, schema validation).
- **Wayback Machine CDX API** (via `waybackpy`) is the canonical counter-evidence tool for "ephemeral" claims — if Wayback has 100+ snapshots over 3+ years and the source publishes archives, the moat thesis fails.
- **Firecrawl Python SDK** (`firecrawl-py` 4.21.0) is the right fallback for JS-rendered/structured-extraction targets where `web_fetch` returns thin content.
- **Hardware envelope:** 2× Intel Xeon E5-2698 v4 (40c/80t), 250 GB RAM, NVIDIA P4 (8 GB shared), 17 TB NAS, residential broadband. This is referenced verbatim in graduated briefs' hand-off prompts.

## Do-Not-Repeat

<!-- Format: [YYYY-MM-DD] Description of what went wrong and what to do instead. -->

- [2026-05-07] **Don't propose `defensibility = 0` as the auto-reject floor.** The user is strict — anything below 5 falls apart in a focused competitor quarter. Encode the threshold as `defensibility ≤ 4 → auto-reject`, not `= 0`.
- [2026-05-07] **Don't quote the old CPU spec (E5-2695 v3) for hardware envelope.** Operator upgraded to E5-2698 v4 (40c/80t); use the new spec without footnotes about the transition.
- [2026-05-07] **Don't enable `web_search` during `mr score`.** It causes the model to drift into adjacent opportunities mid-evaluation. Score uses `web_fetch` only (verify cited URLs + counter-evidence), never `web_search`.
- [2026-05-07] **Don't design a discovery/synthesis loop without a dedup mechanism.** Operator flagged this as missing from v1 of the v2 spec. Any LLM-driven generator that runs more than once needs a summarized index of prior output pre-pended to the prompt — otherwise it converges on the same ideas every run.
- [2026-05-07] **Don't dedup on individual sources.** A "host already mined ≥3 times → skip" rule kills `cross_source_fusion` lane entirely. Operator pushes back on this. Dedup key is `source_set` (the *set* of all hosts on a brief, primary + corroborating); a host can reappear forever as long as it's combined with a new partner.
- [2026-05-07] **Don't pre-pend unbounded derived context.** A naive seen-index that grows linearly with corpus size (~25k tokens at n=500) draws operator pushback. Use a two-tier mechanism: bounded summary block in the prompt (top-N most-recent + frequency aggregates, ~3k tokens regardless of n) + a custom lookup tool (~200 tokens of tool description) for precise checks.

## Decision Log

- [2026-05-07] **4-axis weighted geometric mean** for the scoring rubric — defensibility (0.35), financial (0.30), implementation (0.20), hardware (0.15). Geometric mean (vs. arithmetic) deliberately penalizes single-axis weakness so projects with one fatal flaw cannot compensate via strength elsewhere. Composite ∈ [0, 10].
- [2026-05-07] **Hardware promoted from constraint to scoring axis** (was implicit in v1). Operator's hardware envelope materially constrains feasibility — making it a top-level axis forces every brief to think about fit explicitly.
- [2026-05-07] **Score-prefixed filenames over a separate index.** `<composite × 1000 padded>-<date>-<slug>.md` makes `ls -r` sort by descending composite without any index file or grep.
- [2026-05-07] **No `web_search` during `mr score`** — see Do-Not-Repeat above.
- [2026-05-07] **Anthropic native server tools over hand-rolled wrappers.** 2026 API exposes `web_search_20260209`, `web_fetch_20260209` (with dynamic filter), and `code_execution` (free when bundled). Don't rebuild what's native.
- [2026-05-07] **Discard all 26 prior briefs** for the greenfield v2 restart (operator confirmed). v2 spec at `docs/superpowers/specs/2026-05-07-moat-research-design.md` replaces v1 at `2026-05-04-...md`; v1 kept as historical reference only.
- [2026-05-07] **`mr wishlist expand` + `mr wishlist refresh`** added so WISHLIST is not solely operator-curated. Expand uses LLM to propose new sources; refresh runs deterministic HEAD + robots + Wayback re-verification and marks `dead_link: true` on persistent failures.
- [2026-05-07] **Dedup artifact regenerated from frontmatter, not maintained.** `.moat-research/seen.jsonl` is rebuilt when stale by walking lifecycle dirs and reading frontmatter — eliminates drift between an explicit log and the actual corpus.
- [2026-05-07] **Two-tier dedup design (final).** Bounded pre-pended summary (~3k tokens cap regardless of corpus size: lane×niche freq + 30 most-recent + top-20 hosts split into solo/fusion appearance counts) PLUS a `seen_lookup(slug?, source_set?, lane_niche?)` custom tool (host-side Python scan of `seen.jsonl`) that returns matches + near-matches. Dedup keys: exact slug, exact source_set, exact (lane, niche_key) tuple. Fusion variants (single-host overlap, source_set subset/superset) are explicitly *not* duplicates and are encouraged.
- [2026-05-07] **Geometric mean kept over weighted arithmetic for the 4-axis composite.** For solo-operator economic viability, the auto-reject floor (`defensibility ≤ 4`) handles the catastrophic-copy case; above the floor, time-to-revenue dominates. Geometric mean's "punish fatal weakness" property maps to that — a brief with d=5 (real-but-bounded moat) and others=10 ranks above d=10 (inevitability) with others=5, because the former actually ships and earns. Operators wanting strict-defensibility-first ordering can override `weights[defensibility]` to 0.50+ in mr.yaml.
- [2026-05-07] **Predicate-based verification, not value-based.** Tool re-execution must check the *threshold predicate* against the new result, not the raw value, because monotonic counters (Wayback snapshot count) drift naturally and would falsely auto-reject valid briefs.
- [2026-05-07] **Whole-invocation budget guard with cache-amortized formula.** Per-turn pre-call estimate doesn't bound a 30-turn loop where each turn carries growing tool-result history. Final formula assumes prompt caching (mandatory): `ceiling = (base + max_turns × avg_tool_result) × input_price + max_turns × max_tokens × output_price`. Per-command budget defaults: discover $5, score $3, wishlist_expand $2, default $1.
- [2026-05-07] **Free-text frontmatter taxonomies require host-computed normalization keys.** Operator-supplied `niche` is human-readable; host computes `niche_key` (lowercase, alphanumerics→underscore, sorted tokens, alias-resolved at `seen.jsonl` regen time) for dedup. Brief frontmatter `niche_key` is informational; the canonical key is recomputed each regen using current `mr.yaml: niche_aliases:` so taxonomy evolution doesn't fragment the corpus.
- [2026-05-07] **Iterative spec review loop converges in 5-6 fresh-context-Opus passes.** Each pass on a 16-section spec finds 5-15 new issues (more on early passes, fewer on later); cumulative coverage flushes contradictions (only catchable by cross-reference), subtle math errors (only catchable by computation), and predicate edge cases (only catchable by enumeration). Stopping criteria: 0 critical and ≤ 2 medium debatable findings. Pass-by-pass agent verdicts are useful proxies for convergence.
