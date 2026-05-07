# moat-research — design (greenfield, v2)

**Date:** 2026-05-07
**Replaces:** `docs/superpowers/specs/2026-05-04-moat-research-design.md` (kept as historical reference)
**Status:** under review

---

## 1. Purpose & operator

`moat-research` is a single-operator CLI tool plus structured corpus for discovering, scoring, and promoting **data-moat opportunities** — projects whose structural advantage (knowledge, geography, hardware, archive history, source aggregation) creates a barrier that capital and compute alone cannot overcome.

The operator runs the tool on demand, reviews scored briefs, and promotes the most promising into independent project directories. There is no daemon, scheduler, swarm, or shared state with sibling projects (e.g., `~/somd-cameras/`, `~/claude-runner/`); siblings are produced by hand-off, not orchestrated from here.

---

## 2. Definition of "moat" (strict)

A *moat* is a structural barrier that **cannot** be overcome by:
- spending more money,
- acquiring more compute,
- hiring more staff, or
- acquiring competing entities.

If a well-funded company can replicate the project after one quarter of focused effort, the project does **not** have a moat. The defensibility axis (Section 5) is scored strictly with this in mind.

### 2.1 Hard disqualifiers (any → auto-reject)
1. `defensibility ≤ 4` — the moat is theoretical or fragile.
2. Any axis = 0 — fundamentally infeasible on at least one dimension.
3. Single-source aggregation — fully replaceable by paying the source.
4. Unrestricted archives exist — Wayback Machine has ≥100 snapshots over ≥3 years **OR** the source publishes archives. Either condition alone makes the corpus accessible to a competitor.
5. Source TOS prohibits redistribution with no transformative-use carve-out.
6. Hardware demand exceeds operator envelope (Section 4).

---

## 3. Architecture decisions

| Decision | Choice | Rationale |
|---|---|---|
| Form factor | Single Python CLI (`mr`) | Solo operator, no team-coordination overhead |
| Synthesis | Self-contained — own LLM caller in this repo | No cross-project dependency; full control over prompts, caching, cost log |
| Hand-off | Spawned project directory | Graduated briefs leave this repo, freeing it from per-project state |
| Scheduling | On-demand only | Operator triggers each run |
| Source discovery | WISHLIST + live web tools during synthesis | Hybrid: operator-curated seed list, LLM-driven expansion via `mr wishlist expand` |
| Scoring stability | No `web_search` during `mr score` | Prevents the model from drifting into adjacent opportunities mid-evaluation |
| Hardware as scoring axis | Promoted to its own axis (15% weight) | Hardware envelope materially constrains feasibility |
| Concurrency | `flock(2)` on `.moat-research/.lock` | Prevents two `mr` invocations from racing on the same brief |

---

## 4. Operational envelope (hardware)

| Resource | Capacity |
|---|---|
| CPU | 2 × Intel Xeon E5-2698 v4 — **40 cores / 80 threads** |
| RAM | 250 GB |
| GPU | NVIDIA P4 (8 GB), shared across projects |
| Storage | 17 TB NAS |
| Network | Residential broadband |

This envelope is rendered into every graduated brief's hand-off prompt (Section 12) and scored against by the hardware axis (Section 5.4).

---

## 5. Scoring rubric (4-axis weighted geometric mean)

Each axis is scored 0–10. Composite:

```
composite = (defensibility ^ 0.35) × (financial ^ 0.30) × (implementation ^ 0.20) × (hardware ^ 0.15)
```

Geometric mean (vs. arithmetic) means a single weak axis disproportionately penalizes the composite — a deliberate choice to reject projects with one fatal weakness even when other axes are strong. Composite range is `[0, 10]` (max when every axis is 10: `10^(0.35+0.30+0.20+0.15) = 10^1 = 10`).

### 5.1 Defensibility (35%)
*Question: can a well-funded competitor replicate this in one focused quarter?*
- **0–2:** Pure data resale, single source, no transformation.
- **3–4:** Some aggregation or processing, but a competitor can match it within a quarter. **Auto-reject zone.**
- **5–6:** Real but bounded moat — geographic exclusivity, single transformative pipeline, niche relationship.
- **7–8:** Multi-layered moat — combines two or more of: archive history, geographic exclusivity, multi-source fusion, derived artifacts hard to reverse.
- **9–10:** Structural inevitability — moat compounds with use, or is contractually exclusive.

### 5.2 Financial (30%)
*Question: annualized profit potential vs. operating cost?*
- **0–2:** Cannot cover its own inference bill.
- **3–4:** Marginally positive, no operator surplus.
- **5–6:** $5–25k/yr net.
- **7–8:** $25–100k/yr net.
- **9–10:** $100k+/yr net or low-effort recurring revenue.

### 5.3 Implementation (20%)
*Question: time/effort to MVP and ongoing maintenance?*
- **0–2:** Multi-quarter MVP; ongoing ≥20 hrs/wk.
- **3–4:** 6–12 weeks to MVP; ongoing 5–10 hrs/wk.
- **5–6:** 2–6 weeks to MVP; ongoing 1–4 hrs/wk.
- **7–8:** 1–2 weeks to MVP; ongoing <1 hr/wk.
- **9–10:** <1 week to MVP; near-zero ongoing.

### 5.4 Hardware (15%)
*Question: fits the operator's envelope (Section 4)?*
- **0–2:** Requires GPU class above P4, or >250 GB RAM, or >17 TB.
- **3–4:** Squeezes the envelope — sustained >50% utilization needed.
- **5–6:** Comfortable at peak, idle most of the time.
- **7–8:** Trivial fit; runs alongside existing workloads.
- **9–10:** Could run on a Raspberry Pi.

### 5.5 Auto-reject
Composite is forced to `0` and the brief is routed to `rejected/` whenever **any** of these is true:
- `defensibility ≤ 4`
- any axis = 0
- any hard disqualifier from Section 2.1

**Auto-reject reason strings (normative).** `scores.auto_reject_reason` is set to one of these exact strings, consumed by `seen.jsonl` (§12.1) and §13.3 severity classification:

| Reason string | Trigger | §13.3 tier |
|---|---|---|
| `"defensibility ≤ 4"` | `scores.defensibility ≤ 4` | 2 |
| `"any axis = 0"` | any axis score is 0 | 2 |
| `"single source"` | `single_source.fail` (§6.4) | 1 |
| `"unrestricted archives"` | `unrestricted_archives.fail` (§6.4) | 1 |
| `"TOS prohibits redistribution"` | `tos_redistribution.fail` (§6.4) | 1 |
| `"hardware over envelope"` | `hardware_over_envelope.fail` (§6.4) | 1 |
| `"code_execution result missing required hardware keys"` | hardware verification crash (§6.4) | 1 |
| `"claimed verdict inconsistent with cited evidence"` | model-fabrication detected (§6.4 step 4) | 1 |
| `"manual: <operator text>"` | `mr reject --reason TEXT` | 3 |

The classifier in §13.3 keys off this exact string (`startswith` for `"manual: "`, equality otherwise).

### 5.6 Sensitivity note

Per-axis elasticity equals the axis weight: a 1% change in defensibility moves composite by 0.35%; a 1% change in hardware moves composite by 0.15%. Doubling defensibility (5 → 10) lifts composite by `2^0.35 ≈ 1.27` (27%); doubling hardware lifts it by `2^0.15 ≈ 1.11` (11%). The geometric mean is therefore *less* sensitive to defensibility than the 0.35 weight visually suggests, but proportionally more sensitive than to hardware.

The `defensibility ≤ 4 → auto-reject` floor (§5.5) prevents the most pathological low-end behavior. Briefs in the 5–10 range on each axis produce composites that distinguish meaningfully (range ≈ 5.0 to 10.0).

**Operator-noticeable consequence:** `ls -r scored/` may show a brief with all-tens-except-defensibility-5 (composite ≈ 7.85, computed `5^0.35 × 10^0.65`) ranked higher than a brief with defensibility-10-others-5 (composite ≈ 6.37, computed `10^0.35 × 5^0.65`). This reflects the rubric's intent: a structurally-defensible-at-5 project that excels everywhere else *is* better-graduated than one with structural inevitability but poor financials, slow implementation, and tight hardware fit. Operators wanting strict defensibility-first ordering can override `mr.yaml: weights` to e.g., `{defensibility: 0.50, financial: 0.20, implementation: 0.15, hardware: 0.15}`.

---

## 6. Lifecycle: directories, filename convention, transitions

```
candidates/   ← discover writes here, no score
scored/       ← score writes here, score-prefixed filename
rejected/     ← score routes here on auto-reject; manual reject also lands here
approved/     ← promote moves here
graduated/    ← graduate moves here, hand-off prompt is emitted
```

### 6.1 Filename convention

```
<composite_padded>-<yyyymmdd>-<slug>.md
```

- `composite_padded` = `int(round(composite × 1000))`, zero-padded to 5 digits (e.g., `7.221 → 07221`, auto-rejected → `00000`, max → `10000`).
- `yyyymmdd` = ISO date the brief was first written.
- `slug` = lowercase-kebab from the brief's title, ≤40 characters, ASCII-only.
- **Collision policy:** if `<padded>-<date>-<slug>.md` already exists, append `-02`, `-03`, … (zero-padded to 2 digits, max 99) until unique. Two-digit padding preserves `ls -r` ordering through ten or more collisions; without it `-10` would sort before `-2`.

**Candidate-stage filenames** use the bare form `<yyyymmdd>-<slug>.md` (no score prefix; no score exists yet). On `mr score`, the file is renamed to the score-prefixed form above; on auto-reject, it is moved to `rejected/` with the `00000-` prefix and same date/slug suffix.

`ls -r scored/` therefore sorts by descending composite.

### 6.2 Transitions (always move, never mutate in place)

| From | To | Command | Side-effect |
|---|---|---|---|
| (new) | `candidates/` | `mr discover` | LLM call |
| `candidates/` | `scored/` or `rejected/` | `mr score <path>` | LLM call; computes filename |
| `scored/` | `rejected/` | `mr reject <path> [--reason TEXT]` | writes `scores.auto_reject_reason: "manual: <TEXT>"` to the brief's frontmatter so manual rejections appear in §13.3's adjacent-rejection appendix |
| `scored/` | `approved/` | `mr promote <path>` | none |
| `approved/` | `graduated/` | `mr graduate <path>` | emits hand-off prompt to stdout (idempotent — re-emits if already in `graduated/`; see §13.4) |

### 6.3 Re-scoring
v1 does not support in-place re-scoring. To re-score, the operator must `mv` the file back to `candidates/` (not `cp` — `mv` ensures only one copy exists, avoiding the lifecycle-violation handling in §12.1) and then re-run `mr score`. The operator may edit the brief between the `mv` and the `mr score` invocation. This keeps the lifecycle DAG one-directional.

### 6.4 Brief markdown structure

Every brief is a markdown file with YAML frontmatter. `mr discover` writes briefs without the `scores:` block; `mr score` fills it in and rewrites the filename.

```markdown
---
schema_version: 1
title: <human title>
slug: <kebab-slug, ≤40 chars>
lane: ephemeral_public | soon_to_be_restricted | cross_source_fusion | derived_artifact | niche_vertical | other
lane_note: <one-sentence justification>     # required iff lane == other; mr status flags these
niche: <1-3-word human-readable tag>        # populated by mr discover (model output)
niche_key: <normalized tag>                 # HOST-COMPUTED post-write from `niche` using mr.yaml: niche_aliases:; the model's value (if any) is overwritten before write. The frontmatter value is informational — `seen.jsonl` regeneration recomputes `niche_key` from `niche` using the *current* alias map, so editing aliases retroactively re-buckets old briefs without rewriting them.
delivery_form: project | feature            # see §13 hand-off branching
parent_project: <slug>                      # required iff delivery_form == feature; otherwise omit
date_created: yyyy-mm-dd
sources:
  - url: https://…
    role: primary | corroborating | counter_evidence
    archive_status: none | partial | unrestricted
verification_evidence:                      # populated by mr discover from tool-use return values
  - id: e1
    tool: wayback_check
    args: {url: https://…}
    result: {count: 47, first: "2023-04-12", last: "2026-04-30"}
  - id: e2
    tool: web_fetch
    args: {url: https://…/tos}
    excerpt: "Users may not redistribute…"
  - id: e3
    tool: code_execution
    args: {code: "<utilization-estimate computation>"}
    result: {peak_gpu_gb: 4.2, sustained_ram_gb: 32, storage_tb: 0.5}
disqualifier_verdicts:                      # `mr discover` writes initial values; `mr score` verifies host-side and may overwrite
  defensibility_threshold: n/a              # mr discover writes n/a; mr score overwrites with pass|fail derived from scores
  any_axis_zero: n/a                        # mr discover writes n/a; mr score overwrites with pass|fail derived from scores
  single_source:
    verdict: pass | fail                    # predicate: fail iff |distinct_hosts(s for s in sources if s.role in {primary, corroborating})| ≤ 1 — counter_evidence is excluded; zero sources is also a fail (vacuous-truth guard)
  unrestricted_archives:
    verdict: pass | fail
    wayback_evidence_id: e1                 # required; verifies the Wayback arm of §2.1.4
    publisher_archive_evidence_id: null     # nullable; if set, references a verification_evidence row whose tool=web_fetch and excerpt or result documents publisher's own archive
  tos_redistribution:
    verdict: pass | fail | n/a
    evidence_id: e2
  hardware_over_envelope:
    verdict: pass | fail                    # predicate: fail iff result.peak_gpu_gb > 8 OR result.sustained_ram_gb > 250 OR result.storage_tb > 17
    evidence_id: e3                         # REQUIRED; code_execution result MUST contain all three keys {peak_gpu_gb, sustained_ram_gb, storage_tb} as numeric values (missing keys → reject brief with auto_reject_reason: "code_execution result missing required hardware keys")
scores:                       # absent until mr score fills it
  defensibility: 0-10
  financial: 0-10
  implementation: 0-10
  hardware: 0-10
  composite: 0.000-10.000
  auto_reject_reason: null | string
---

# <title>

## Thesis
2–4 sentences: what is the project and why does the moat hold.

## Why this is a moat
Defensibility argument, including counter-evidence (Wayback hits, similar offerings).

## Sources
Table: URL · what it provides · archive status · access constraints.

## Financial sketch
TAM, pricing model, expected ops cost.

## Implementation sketch
MVP scope, weeks to MVP, ongoing maintenance load.

## Hardware fit
Utilization plan vs. operator envelope (Section 4).

## Disqualifier check

The frontmatter `disqualifier_verdicts` block (above) is the structured contract; this body section is human-readable prose summarizing those verdicts. `mr score` operates on the frontmatter, not on this prose.

`mr score` performs **host-driven verification** that reproduces model-emitted tool uses rather than driving new LLM reasoning. Budget treatment:

- **Exempt from tier 3 (`max_tool_turns`):** these calls are not LLM-driven and do not count toward the cap.
- **Counted against tier 2 (per-call budget tally) and tier 4 (wallclock + cache misses):** they cost money and time.
- **Capped separately by `mr.yaml: budgets.max_verification_calls`** (default 12) — bounds verification cost on briefs with many cited evidence rows.

Verification procedure:

1. For each tool-backed verdict (those with `evidence_id`), re-execute the cited tool with the recorded `args`.
2. Re-evaluate the **predicate** against the new result, not the raw value:
   - `single_source.fail` ⟺ `|distinct_hosts(s for s in sources if s.role in {primary, corroborating})| ≤ 1`. Re-evaluated host-side from the current `sources:` list; no tool call. Zero or one host both fail (zero-source brief gets a fail, not a vacuous pass).
   - `unrestricted_archives.fail` ⟺ `(wayback.count ≥ unrestricted_archive_min_snapshots AND wayback.years ≥ unrestricted_archive_min_years)` **OR** `publisher_archive_evidence_id is set AND the cited evidence content actually documents a publisher archive`. Two evidence rows may be required; either arm fails the brief. **Publisher-archive content verification:** if `publisher_archive_evidence_id` is non-null, re-fetch the cited URL and run a host-side regex check `/archive|history|past issues|back issues|backfile|rss|atom/i` against the page text. If the regex matches, the publisher-archive arm is confirmed and the brief fails. If the regex does not match, treat the model's claim as unverified — re-prompt the model on the new page text to re-derive the verdict (analogous to TOS-revision flow). Pass only when both arms come up negative after verification.
   - `tos_redistribution.fail` ⟺ the cited excerpt still appears on the page. If the excerpt is gone (TOS revised), re-prompt the model on the new page text to re-derive the verdict.
   - `hardware_over_envelope.fail` ⟺ `result.peak_gpu_gb > 8` OR `result.sustained_ram_gb > 250` OR `result.storage_tb > 17`. Re-execute the cited `code_execution` and apply the predicate to the new result. **Missing keys** in the result (e.g., a CPU-only brief that doesn't compute `peak_gpu_gb`) cause the brief to be rejected with `auto_reject_reason: "code_execution result missing required hardware keys"` — the model must compute and return all three keys, defaulting to 0 for unused resources.
3. If predicate evaluation flips the verdict, update `disqualifier_verdicts` and re-run the auto-reject decision.
4. If the brief's claimed verdict does not match the predicate evaluation against its **own cited evidence** (e.g., recorded `count: 47` but claimed `unrestricted_archives.fail`), that's a model lie — auto-reject with `auto_reject_reason: "claimed verdict inconsistent with cited evidence"`.

Predicate-based matching tolerates natural drift in monotonic counters (Wayback adds snapshots; an unchanged threshold predicate keeps the verdict valid) while still catching fabricated verifications.
```

The exact prose section names are required; downstream parsing (e.g., `mr score`) keys off these headers. Lane and disqualifier vocabularies are closed sets enforced by `mr.yaml`.

---

## 7. CLI commands

11 subcommands. All commands that call the LLM accept `--budget USD` to bound spend. **Four-tier enforcement** plus cold-corpus preflight:

1. **Whole-invocation worst-case ceiling.** At the start of every LLM-calling invocation, compute under the assumption that prompt caching (mandatory per §8.1) deduplicates repeated content across turns. The cache-aware ceiling is:
   ```
   ceiling = (base_input_tokens + max_tool_turns × avg_tool_result_tokens) × model_input_price
           + max_tool_turns × max_tokens_per_turn × model_output_price
   ```
   `base_input_tokens` (system prompt + WISHLIST + seen-summary) is paid once across the loop because caching amortizes it; each turn's only fresh input is the prior turn's tool result (`avg_tool_result_tokens`). `model_input_price` and `model_output_price` are looked up per-command from the resolved model in `mr.yaml: models:`. If the ceiling exceeds the provided budget, refuse to start. Without this check a single 30-turn loop blows the budget on output tokens alone even if every per-turn check (tier 2) passes.
2. **Per-turn pre-call estimate.** Before each LLM call, compute `(input_tokens × input_price) + (max_tokens × output_price)` and abort if `running_tally + estimate > budget × 0.9` (10% safety margin for tool-result token bloat).
3. **Tool-turn cap.** Hard limit of `mr.yaml: budgets.max_tool_turns` (per-command — see §9 for defaults: 12 default, 25 discover, 15 score, 20 wishlist_expand); aborts if exceeded. Bounds the worst case where the model loops on tool calls without converging. Host-driven verification calls from §6.4 are **exempt** from this cap (they reproduce prior tool calls rather than drive new LLM reasoning); they are bounded separately by `max_verification_calls`.
4. **Wallclock cap + cache-miss abort.** Hard limit of `mr.yaml: budgets.max_wallclock_seconds` (default 240, deliberately under Anthropic's 5-min prompt-cache TTL); aborts if exceeded. Additionally, abort if `cache_misses ≥ 2` consecutive turns **starting from turn 3** — turns 1 and 2 are exempt because turn 1 is always a creation event by construction (cache must be populated before it can be reused), and turn 2 may legitimately create a second cache block. **Definition:** a turn is a "cache miss" iff the API response reports `cache_creation_input_tokens > 0` on a cache-controlled block whose fingerprint was previously cached this run (a *re-write*, not a first-time creation). The consecutive counter is in-memory in the running process; block fingerprints (e.g., SHA-256 of the cached prefix) are also held in memory, not in `costs.jsonl`.

Post-call usage (`input_tokens`, `cached_input_tokens`, `output_tokens`, `cache_hits`, `cache_misses`, `code_execution_container_seconds`) feeds `.moat-research/costs.jsonl`, the running tally for tier 2 on subsequent calls.

**Cold-corpus preflight (`mr discover`):** if `WISHLIST.md` has fewer than 5 sources, `mr discover` aborts with an error directing the operator to run `mr wishlist expand --seed --budget 0.50` first. Discovering against an empty seed produces low-quality candidates from web search alone — the bland-slop failure mode. The "5 sources" floor is heuristic: enough for the LLM to pattern-match across (lane, niche) combinations without being limited to a single source's flavor.

| Command | LLM? | Tools | Purpose |
|---|---|---|---|
| `mr init` | no | none | Bootstrap dirs, `mr.yaml`, `prompts/` (idempotent) |
| `mr discover [--lane L] [--n N] [--budget USD]` | yes | search, fetch, code, wayback, firecrawl* | Generate candidates from WISHLIST + live scan |
| `mr score <path...> [--budget USD]` | yes | fetch, code, wayback, robots, head | Score; route to `scored/` or `rejected/` |
| `mr promote <path>` | no | none | Move scored → approved |
| `mr graduate <path>` | no | none | Move approved → graduated; print hand-off prompt |
| `mr reject <path> [--reason TEXT]` | no | none | Move scored → rejected |
| `mr wishlist add <yaml>` | no | none | Append source to `WISHLIST.md` (schema-validated) |
| `mr wishlist expand [--seed] [--budget USD]` | yes | search, fetch, code, firecrawl* | LLM scan for new sources |
| `mr wishlist refresh` | no | head, robots, wayback | Re-verify WISHLIST sources; mark `dead_link: true` on persistent failures |
| `mr status` | no | none | Counts per dir + top-3 pending in each + flags `approved/` entries older than `mr.yaml: status.stale_approved_days` (default 90) |
| `mr gain` | no | none | Spend summary from `.moat-research/costs.jsonl` |

`*` = optional, only when `MR_FIRECRAWL_API_KEY` is set.

---

## 8. Synthesis: prompts, tool set, models

### 8.1 Models

- **Default:** `claude-opus-4-7` (deep reasoning for `mr discover`, `mr score`).
- **Bulk fallback:** `claude-sonnet-4-6` (used by `mr wishlist expand` by default; configurable per command in `mr.yaml`).
- **Prompt caching:** mandatory. The system prompt for each subcommand is sent with `cache_control: {"type": "ephemeral"}`. The WISHLIST (large) is cached as a separate block from the system prompt so additions invalidate only the WISHLIST cache, not the rubric/system prompt.

### 8.2 Tool set per subcommand

The 2026 Anthropic API exposes three native server tools we lean on heavily; `code_execution` is **free** when bundled with `web_search` or `web_fetch`, so we expose it everywhere it's useful.

| Subcommand | Anthropic native | Custom Python tools |
|---|---|---|
| `mr discover` | `web_search_20260209`, `web_fetch_20260209` (with dynamic filter), `code_execution` | `seen_lookup`, `wayback_check`, `firecrawl_scrape` (opt) |
| `mr score` | `web_fetch_20260209` (with dynamic filter), `code_execution` | `wayback_check`, `robots_check`, `head_check` |
| `mr wishlist expand` | `web_search_20260209`, `web_fetch_20260209`, `code_execution` | `seen_lookup`, `firecrawl_scrape` (opt) |
| `mr wishlist refresh` | (no LLM) | `head_check`, `robots_check`, `wayback_check` |

**Why no `web_search` during `mr score`:** prevents the model from drifting into adjacent opportunities mid-evaluation. The model verifies cited URLs (`web_fetch`) and looks for counter-evidence (`wayback_check`); it does not prospect.

**Aggressive `code_execution` use:** since it is free when bundled, every LLM-calling subcommand gets it. Used for: robots.txt parsing, rate-budget arithmetic ("at 60s cadence and 2 KB/response, that's X GB/month"), dedup against `briefs/`-equivalent indices, schema validation of generated drafts before write.

### 8.3 Custom Python tool implementations

| Tool | Backing |
|---|---|
| `wayback_check(url)` | `waybackpy` → CDX API → `{first, last, count}` |
| `robots_check(url, ua)` | `urllib.robotparser` (stdlib) |
| `head_check(url)` | `httpx` HEAD → `{status, content_type, last_modified}` |
| `firecrawl_scrape(url)` | `firecrawl-py` → markdown — only loaded when `MR_FIRECRAWL_API_KEY` is set |
| `seen_lookup(slug?, source_set?, lane_niche?)` | host-side scan of `.moat-research/seen.jsonl` → matches + near-matches; see §12.3 |

### 8.4 Prompts (shipped, user-editable)

Stored in `prompts/` so the operator can tune without editing Python:

- `prompts/discover.md` — system prompt for `mr discover` (encodes the five lanes and the candidate-brief schema).
- `prompts/score.md` — system prompt for `mr score` (encodes the rubric in Section 5 and the auto-reject conditions).
- `prompts/wishlist_expand.md` — system prompt for `mr wishlist expand`.

Prompts are read from disk on each invocation; no compilation step.

### 8.4.1 Prompt content requirements (load-bearing for spec correctness)

The shipped prompts encode requirements that the rest of this spec depends on. Operator edits must preserve them:

- **`prompts/discover.md`:**
  - Every output candidate must call `seen_lookup` against its proposed `(slug, source_set, lane_niche)` before commit (§12.3).
  - **Diversity bias.** When `--lane` is not specified, prefer (lane, niche_key) cells underrepresented in the frequency table (§12.2). Mode collapse on a few favorite topics is a defect, not noise. `lane: other` is fully exempt from this bias (see §12.2 "Other-lane treatment"). The model is told the `(exploration)` and `(exploration host)` tags signal "do not penalize repetition here."
  - **`soon_to_be_restricted` lane:** candidates must cite a dated public artifact (board minutes, regulatory docket, published roadmap, official statement) as evidence of the restriction path. Speculation without a dated artifact triggers the model to either re-classify or drop the candidate.
  - **Domain interests.** Consume `mr.yaml: interests.affirm` and `interests.avoid` to bias generation; never propose candidates whose niche overlaps `avoid`.
  - **Hardware envelope evidence.** Every brief MUST emit a `code_execution` evidence row whose `result` is a JSON object with numeric keys `peak_gpu_gb`, `sustained_ram_gb`, `storage_tb` (use `0` for unused resources). The frontmatter `disqualifier_verdicts.hardware_over_envelope.evidence_id` references this row. Briefs that omit any of the three keys are auto-rejected by `mr score` with `auto_reject_reason: "code_execution result missing required hardware keys"` (§5.5).
  - **`delivery_form` heuristic.** Set `delivery_form: feature` (with `parent_project: <slug>`) when the candidate's moat materially depends on extending an existing sibling project named in `mr.yaml: interests.affirm` (e.g., adding aviation alerts to a `somd-cameras` repo); the spawned work is a feature branch + PR rather than a fresh project. Otherwise default to `delivery_form: project`.
- **`prompts/score.md`:**
  - The rubric in §5 is the only allowed scoring authority.
  - Every disqualifier-check row must cite a specific tool call; `mr score` re-executes the cited tool calls and rejects on any mismatch (§6.4).
- **`prompts/wishlist_expand.md`:**
  - Same source-set dedup rules as `discover.md` (§12.4).
  - When proposing a host already in the seen index, articulate the fusion or transformation pairing whose `source_set` is novel.

### 8.5 Lanes

Five canonical lanes plus an escape hatch (`other`). Consumed by `mr discover --lane` and §6.4 frontmatter `lane:`:

1. `ephemeral_public` — published by an authority but expires/rotates without archive (e.g., NOTAMs).
2. `soon_to_be_restricted` — currently public but on a credible path to paywall, ToS lockdown, or removal.
3. `cross_source_fusion` — multiple individually-public sources whose join produces a non-obvious derived artifact.
4. `derived_artifact` — single public source plus a transformation (model, index, normalization) hard to reverse.
5. `niche_vertical` — domain so narrow that incumbents will not bother to compete.
6. `other` — escape hatch for genuinely novel moat shapes that don't fit 1–5. Requires `lane_note:` (one-sentence justification) in frontmatter (§6.4). `mr status` flags `other`-lane briefs so the operator can canonicalize a sixth lane in v2 if a pattern emerges.

---

## 9. Configuration (`mr.yaml`)

Project-root YAML, loaded by every subcommand. Missing keys fall back to baked-in defaults so a fresh checkout works without `mr.yaml`.

```yaml
schema_version: 1

models:
  default: claude-opus-4-7
  bulk: claude-sonnet-4-6
  per_command:
    wishlist_expand: claude-sonnet-4-6
  pricing:                          # USD per million tokens; baked-in defaults; operators override on price changes
    claude-opus-4-7:    {input: 15.00, output: 75.00, cache_read: 1.50,  cache_write: 18.75}
    claude-sonnet-4-6:  {input:  3.00, output: 15.00, cache_read: 0.30,  cache_write:  3.75}
    claude-haiku-4-5:   {input:  1.00, output:  5.00, cache_read: 0.10,  cache_write:  1.25}

weights:
  defensibility: 0.35
  financial: 0.30
  implementation: 0.20
  hardware: 0.15

disqualifiers:
  defensibility_min: 5            # ≤4 auto-rejects
  any_axis_zero: true
  unrestricted_archive_min_snapshots: 100
  unrestricted_archive_min_years: 3   # disjunctive with publisher-archive presence; see §2.1.4

lanes:                              # closed set; "other" is an escape hatch requiring lane_note: in frontmatter
  - ephemeral_public
  - soon_to_be_restricted
  - cross_source_fusion
  - derived_artifact
  - niche_vertical
  - other

niche_aliases:                      # operator-edited synonym map; consumed by §6.4 niche_key normalization
  alerts_aviation: ["aviation alerts", "FAA aviation", "aviation"]
  cameras_county: ["small-county cameras", "county cam feeds"]
  # add more as patterns emerge

interests:                          # consumed by mr discover only; never by mr score
  affirm: []                        # operator fills with topic tags they want more of
  avoid: []                         # operator fills with topic tags to exclude (e.g., "cryptocurrency", "surveillance")

hardware:
  cpu: "2× Intel Xeon E5-2698 v4 (40c/80t)"
  ram_gb: 250
  gpu: "NVIDIA P4 (8GB), shared"
  storage_tb: 17
  network: "residential broadband"

budgets:
  default_per_invocation_usd:       # per-command budgets; flat $1 was unrealistic for web-heavy commands
    default: 1.00
    discover: 5.00                  # web_search + web_fetch + code_execution + custom tools, ~25 turns
    score: 3.00                     # mostly fetch+verify, ~15 turns
    wishlist_expand: 2.00           # sonnet model, ~20 turns
  max_tool_turns:                   # per-command cap; see §7 tier 3
    default: 12
    discover: 25
    score: 15
    wishlist_expand: 20
  max_tokens_per_turn: 1500         # output token cap per turn; used by §7 tier 1 ceiling
  max_wallclock_seconds: 240        # deliberately under Anthropic's 5-min prompt-cache TTL; see §7
  max_verification_calls: 12        # cap on host-driven verification re-executions per `mr score` brief (§6.4)
  base_input_tokens: 6000           # cache-amortized estimate of system prompt + WISHLIST + seen-summary; §7 tier 1
  avg_tool_result_tokens: 1500      # estimate of average tool-call result size; §7 tier 1

status:
  stale_approved_days: 90           # mr status flags approved/ entries older than this
  dead_link_window_days: 14         # §11 mr wishlist refresh; "consecutive failures" must fall within this window
```

`mr.yaml` is JSON-Schema-validated at load (`mr/util/config.py` ships the schema). **In v1, only `schema_version: 1` is supported** — any other value is a fatal error rather than a migration trigger, since the migration framework is deferred to §15.2 implementation hardening. When the migration framework lands, mismatched `schema_version` values will run pending migrations from `mr/util/migrations/` before validation. Strict-key validation (unknown keys raise an error) prevents typo-silent misconfiguration like `weight:` instead of `weights:`.

The same v1-only `schema_version: 1` rule applies to brief frontmatter and `WISHLIST.md` schemas.

---

## 10. State, concurrency, cost tracking

`.moat-research/` (gitignored):

| File | Purpose |
|---|---|
| `lock` | `flock(2)` exclusive lock — held for the duration of any LLM-calling subcommand |
| `costs.jsonl` | One line per API call: `{ts, command, model, input_tokens, cached_input_tokens, output_tokens, cache_hits, cache_misses, code_execution_container_seconds, cost_usd}`. **Cache semantics:** `cache_hits` is the API-response `cache_read_input_tokens` count for the call; `cache_misses` is `cache_creation_input_tokens` (a non-zero value means a cache block was rewritten, not reused). **`code_execution` cost** is recorded conservatively even when bundled with `web_search`/`web_fetch` (which Anthropic currently documents as free): `container_seconds` is stored so spend reconstruction is possible if pricing changes. |
| `seen.jsonl` | Canonical dedup artifact — one JSON object per brief ever written; consumed by the bounded summary block and the `seen_lookup` tool (§12) |
| `cache/` | Optional response cache for deterministic tool calls (Wayback, robots) |

`mr gain` aggregates `costs.jsonl` (modeled on `rtk gain`).

**Concurrency contract:** if a second `mr` invocation arrives while the lock is held, it blocks for up to 60 s, then errors with a message naming the holding command. This is a soft guard; the operator is expected not to fan out invocations.

**Filesystem assumption:** the lock and `seen.jsonl` regeneration assume a local POSIX filesystem. Running `mr` against an NFS-mounted repo is **unsupported in v1** — `flock(2)` semantics on NFS are unreliable and could permit concurrent corruption. Operators with multiple machines should sync the repo via git/rsync, not via shared mount.

---

## 11. WISHLIST: schema, expansion, refresh

`WISHLIST.md` is a single YAML document at repo root:

```yaml
sources:
  - id: faa-notams                   # stable kebab-id, primary key
    url: https://notams.aim.faa.gov/notamSearch
    lane: ephemeral_public
    rationale: |
      NOTAMs expire and are not archived by the FAA.
    last_verified: 2026-05-07
    dead_link: false
  # …more sources…
```

- **`mr wishlist add <yaml-fragment>`:** appends a fragment validated against the schema; rejects if `id` collides.
- **`mr wishlist expand`:** runs an LLM scan with the existing list as a cached context block and emits *candidate* new entries to stdout. The operator reviews and runs `mr wishlist add` on the ones they like. With `--seed`, bootstraps from an empty list — used on first install.
- **`mr wishlist refresh`** (deterministic, no LLM): for each source, runs `head_check` + `robots_check` + `wayback_check`. Updates `last_verified` only on a 2xx HEAD result; records every attempt's timestamp in `last_attempted` regardless of outcome. Sets `dead_link: true` on 4xx/5xx persistence across two consecutive refreshes **whose `last_attempted` timestamps fall within `mr.yaml: status.dead_link_window_days` of each other** (default 14 days). Outside that window, the failure counter resets — a transient failure in March followed by another in October does not mark a source dead. This separates "we confirmed it works at T" from "we tried at T and failed."

---

## 12. Idea index (dedup against prior corpus)

To prevent `mr discover` and `mr wishlist expand` from re-proposing identical ideas across runs **while remaining permissive of synthesized ideas** (a familiar source recombined with a different partner), every LLM-calling generator subcommand uses a two-tier mechanism: a small **pre-pended summary block** for fast pattern recognition, plus a **`seen_lookup` custom tool** for precise checks against the full corpus.

### 12.1 Canonical artifact

`.moat-research/seen.jsonl` — one JSON object per brief, regenerated deterministically when stale. **Staleness check:** `seen.jsonl` is stale iff its mtime is older than the most-recent **lifecycle-directory** mtime (`os.stat(dir).st_mtime` for each of `candidates/ scored/ approved/ rejected/ graduated/`). Directory mtime bumps on `os.replace` rename, where individual brief mtimes are preserved — so checking dir mtime catches transitions that brief-mtime checks would miss. The walk reads each brief's YAML frontmatter (§6.4) plus the first sentence of its `## Thesis` body section.

```json
{"slug":"faa-notams","lane":"ephemeral_public","niche":"aviation alerts","niche_key":"alerts_aviation","thesis":"NOTAMs expire and are not archived by the FAA.","source_set":["notams.aim.faa.gov"],"disposition":"graduated","auto_reject_reason":null,"date_created":"2026-05-04"}
```

`auto_reject_reason` is `null` for any non-`rejected/` brief and the brief's frontmatter `scores.auto_reject_reason` value otherwise — required by §13.3's manual-rejection appendix tier.

`disposition ∈ {candidate, scored, rejected, approved, graduated}` (closed set; the singular form of each lifecycle directory name).

`source_set` is the **set of distinct hosts** across the brief's frontmatter `sources:` list (primary + corroborating + counter-evidence). `niche_key` is the normalized form of `niche` (lowercase; non-alphanumerics → `_`; tokens sorted alphabetically; aliases applied from `mr.yaml: niche_aliases:`). The dedup tuple is `(lane, niche_key)` — *not* `(lane, niche)` — preventing free-text-fragmentation false-negatives like "aviation alerts" vs. "FAA aviation" producing distinct cells in the frequency table.

**Atomicity:** every write to `seen.jsonl` is via tmpfile + `os.replace` (atomic). All brief moves (`mr score`, `mr promote`, `mr graduate`, `mr reject`) use `os.replace` for the rename.

**Lifecycle-violation recovery:** if the regeneration walk encounters the same `slug` in two lifecycle directories, recovery is **conditional and conservative**:

- **Partial-move artifact** — both copies in adjacent dirs along the canonical chain (e.g., `candidates/`+`scored/` or `scored/`+`approved/`), forward-dir copy mtime > earlier-dir copy mtime, mtime delta ≤ 60 seconds: this is a partial move interrupted between `os.replace` and `seen.jsonl` flush. Keep the forward copy, delete the earlier one.
- **Operator-error fallback (`cp` instead of `mv`)** — under §6.3's `mv` procedure, only the `candidates/` copy should exist after the operator moves the brief back. If both copies are present, the operator used `cp` against §6.3's instruction. Detected by: `candidates/` copy has newer mtime than the forward copy. **Auto-recovery does NOT trigger; the duplicate is left alone for the operator's `mr score` to consume**, and `seen.jsonl` regen records the `candidates/` copy as the canonical disposition (`candidate`). This branch is defensive against operator error — it is not a documented re-score path under §6.3.
- **Anything else** — different non-adjacent dirs (e.g., `rejected/`+`approved/`), or mtime delta > 60s, or both copies non-byte-identical: abort with a fatal violation requiring `mr doctor` intervention (deferred to §15.2).

This ruleset auto-heals interrupted batch operations without silently destroying operator-edited content during a re-score workflow.

### 12.2 Pre-pended summary block (bounded ~3k tokens)

Derived from `seen.jsonl` on each LLM-calling invocation, included as a separately-cached prompt block (independent cache slot from system prompt and WISHLIST). Bounded so context cost does not grow with corpus size:

1. **Lane × niche frequency table** — counts per `(lane, niche)` tuple, sorted descending.
2. **30 most-recent briefs** — `slug · lane · niche · thesis_sentence · source_set` (one row each).
3. **Most-mined hosts table (top 20)** — host, total appearances, **solo-appearance count**, **fusion-appearance count** (where `|source_set| > 1`). The solo/fusion split gives the model fusion-opportunity signal at a glance: a host that has appeared 5 times solo but never in fusion is a strong candidate for a synthesis brief.

**Cold-corpus exception:** if `n ≤ 50`, the full index is pre-pended instead of the bounded summary — still well under the cache budget.

**Other-lane treatment** (§8.4.1 rationale):

- The frequency table (block 1) excludes `lane: other` rows from the underrepresentation calculation — exploration cells should not be penalized for repetition.
- The 30-most-recent-briefs row (block 2) appends ` (exploration)` to the `lane` column for `other`-lane rows so the model recognizes them as exploratory rather than canonical.
- The most-mined-hosts table (block 3) tags hosts that appear *only* in `other`-lane briefs as ` (exploration host)`.

The diversity-bias instruction in `prompts/discover.md` keys off these tags to suppress its preference-for-underrepresented logic on exploration content.

Used by: `mr discover`, `mr wishlist expand`. **Not** used by `mr score` (scoring is per-brief). `mr status` surfaces the top-3 most-mined hosts as an operator sanity check.

### 12.3 `seen_lookup` custom tool

Exposed on `mr discover` and `mr wishlist expand`. The model calls it when it has a specific candidate to verify against the full corpus before committing the candidate to a draft.

```text
seen_lookup(
  slug?: str,
  source_set?: list[str],          # set semantics, order-independent
  lane_niche?: [str, str],
) → {
  "matches":      [{"file": "…", "slug": "…", "thesis": "…", "match_reason": "exact_slug" | "exact_source_set" | "exact_lane_niche"}],
  "near_matches": [{"file": "…", "slug": "…", "thesis": "…", "match_reason": "source_set_subset" | "source_set_superset" | "single_host_overlap" | "partial_niche"}],
}
```

Implementation: pure host-side Python on `.moat-research/seen.jsonl` (~100 LOC). No vector store, no LLM call. Adds ~200 tokens of tool-description context regardless of how many times the model invokes it.

### 12.4 Heuristics — duplicate vs. permitted

The system prompt instructs the model with this table:

| Match type | Verdict |
|---|---|
| Exact `slug` collision | **Duplicate.** Reject the candidate. |
| Exact `source_set` equality (host-set match across primary + corroborating) | **Duplicate of a fusion.** Reject. |
| Exact `(lane, niche)` tuple match | **Similar, not duplicate.** Articulate differential value vs. the existing brief; if you cannot, reject. |
| Single primary-host overlap, `source_set` differs | **Not a duplicate.** Re-using a familiar host in a new combination is *encouraged*. Evaluate the fusion thesis on its own merits. |
| `source_set` subset/superset (one or two hosts differ) | **Not a duplicate.** Evaluate whether the added/removed host materially changes the thesis. |
| Same niche-and-host as an `auto_reject_reason` brief in `rejected/` | **Probably duplicate of a rejection.** Evaluate whether the new framing addresses the prior rejection reason; if not, reject. |

For `mr wishlist expand` specifically: the **prior "skip host mined ≥3 times" rule is removed**. A host can be re-proposed for WISHLIST if the model articulates a fusion or transformation pairing whose `source_set` is not in the index.

Embedding-based similarity is deliberately out of scope for v1 — adds a vector store, embedding-model choice, and threshold tuning, none justified at expected corpus sizes (≤ 500 briefs over the operator's lifetime). The structured signals plus LLM judgment plus `seen_lookup` are sufficient.

### 12.5 Frontmatter contract

The `niche_key` field declared in §6.4 is the load-bearing dedup key for `(lane, niche_key)` lookups. `niche` (human-readable) is preserved alongside but never used for matching. The full `sources:` list (with `role` per entry) is load-bearing for `source_set` derivation.

**Who computes `niche_key`:** the model writes a draft `niche` (human-readable) during `mr discover`; the host then post-processes the draft, computing `niche_key` from `niche` using the current `mr.yaml: niche_aliases:` map and overwriting any `niche_key` value the model may have included. This prevents model hallucination of dedup keys. The frontmatter `niche_key` is informational because `seen.jsonl` regeneration recomputes it from `niche` using whatever alias map is current at regen time — so editing `niche_aliases` retroactively re-buckets old briefs without rewriting their frontmatter.

`mr score` does not modify `niche`, `niche_key`, or `sources`.

---

## 13. Hand-off: graduation prompt (branches on `delivery_form`)

`mr graduate <path>` prints to stdout a self-contained prompt that, pasted into a Claude session, runs the spawned work without any further `moat-research` access. Output branches on the brief's `delivery_form` frontmatter (§6.4).

### 13.1 `delivery_form: project` — fresh project init (default)

```
You are starting <slug>. Brief follows verbatim.

Hardware envelope:
  CPU: 2× Intel Xeon E5-2698 v4 (40c/80t)
  RAM: 250 GB
  GPU: NVIDIA P4 (8GB) — shared, plan for ≤4 GB sustained
  Storage: 17 TB NAS
  Network: residential broadband

Brief:
<full markdown of the brief, including rubric scores and cited sources>

Adjacent rejections (same lane and niche — known dead-ends):
<bulleted list, see §13.3>

First action: read CLAUDE.md if present, then ask 1–3 clarifying questions before scaffolding.
```

`moat-research` does **not** create the spawned project directory. The operator runs:

```bash
mr graduate approved/08412-20260507-foo.md > /tmp/init.txt
mkdir ~/foo && cd ~/foo && git init
claude < /tmp/init.txt
```

### 13.2 `delivery_form: feature` — patch proposal for an existing repo

```
You are extending the <parent_project> repo with a new feature. Brief follows verbatim.

Hardware envelope:
  <same as above>

Brief:
<full markdown of the brief>

Adjacent rejections (same lane and niche — known dead-ends):
<bulleted list, see §13.3>

First action: read this repo's CLAUDE.md, the existing architecture, and any modules relevant to the brief. Do **not** create new files until you have understood the current shape. Propose a feature branch name and a draft PR description before any code edits.
```

The operator runs:

```bash
mr graduate approved/08412-20260507-foo.md > /tmp/patch.txt
cd ~/<parent_project>/
claude < /tmp/patch.txt
```

### 13.3 Adjacent-rejection appendix

Both forms include an appendix listing rejected briefs that share the graduating brief's `(lane, niche_key)` tuple. Each entry: slug · `auto_reject_reason` · one-sentence thesis.

**Capped at 3, ranked by severity** (not recency) — most-recent ranking misses old-but-deeper rejections in favor of trivial recent ones. Severity tiers (see §5.5 normative table for the exact `auto_reject_reason` strings at each tier):

1. **Hard-disqualifier rejections** — single-source, unrestricted-archives, TOS-prohibits, hardware-over-envelope, missing-hardware-keys, claimed-verdict-inconsistent. These reveal a structural barrier to the niche or evidence that the framing was unverifiable.
2. **Floor rejections** — `defensibility ≤ 4` and `any axis = 0`. Moat-thesis weakness specific to that framing.
3. **Manual rejections** — `auto_reject_reason` starting with `"manual: "`. Operator's own reasoned dead-end, surfaced with the operator's note text.

Purpose: prevent the spawned project from rediscovering known dead-ends without overwhelming it with shallow rejections.

### 13.4 Idempotency

`mr graduate` is idempotent on briefs already in `graduated/` — re-running emits the same hand-off prompt to stdout without moving the file or mutating state. Operators who lose the original output (terminal cleared, `/tmp` wiped) can re-run safely. The hand-off prompt is also written to `graduated/<slug>.handoff.txt` alongside the brief at first graduation, providing a durable copy without dependence on shell history.

---

## 14. Migration / cleanup of current repo

**Delete:**
- `briefs/` (all 26 prior artifacts + `index.json` ~107k tok).
- `FOCUS.md` (its three priorities are stale; status moves into `mr status`).

**Keep verbatim:**
- `.gitignore`, `CLAUDE.md`, `.claude/`, `.wolf/`, `.rtk/`.
- `docs/superpowers/specs/2026-05-04-moat-research-design.md` (historical).
- `docs/superpowers/plans/2026-05-04-moat-research-implementation.md` (historical).

**Augment:**
- `.gitignore` add: `/.moat-research/`, `__pycache__/`, `.venv/`, `*.egg-info/`, `dist/`, `build/`.
- `WISHLIST.md` retains its existing schema (`sources: []`); the first `mr wishlist add` extends it.

**Created in implementation phase (not by this spec):**
- `pyproject.toml` (uv-managed, Python 3.12; deps: `anthropic`, `typer`, `pyyaml`, `httpx`, `waybackpy`; optional: `firecrawl-py`).
- `mr/` Python package (`cli/`, `lifecycle/`, `synth/`, `scoring/`, `tools/`, `util/`).
- `prompts/{discover,score,wishlist_expand}.md`.

**Created lazily by `mr init`:**
- Lifecycle dirs: `candidates/ scored/ rejected/ approved/ graduated/`.
- `.moat-research/` runtime state dir.
- `mr.yaml` if missing.

---

## 15. Out of scope (v1)

### 15.1 Will not do

- Daemon mode, cron, scheduled runs.
- Multi-user support, web UI, REST API.
- Cross-project orchestration — no `signals/`, no swarm, no coordinator.
- Dependency on a separate "maximizer" project.
- Automatic graduation (operator approval is required).
- Automatic project scaffolding inside this repo — graduation hands off to a fresh directory.
- Re-scoring in place (Section 6.3).
- Embedding-based similarity for dedup (Section 12.4).
- NFS-mounted repos (Section 10).

### 15.2 Deferred to implementation hardening

In scope but tracked in the implementation plan, not specified here:

- Session-level memoization of deterministic tool calls (`wayback_check`, `robots_check`, `head_check`) so the same URL is not re-queried within a single invocation.
- `schema_version: N` migration logic — when v2 of a schema changes a field, document the migration in `mr/util/migrations/` and gate `mr` startup on running pending migrations. **Until this lands, v1 only supports `schema_version: 1` and any mismatch is a fatal error** (see §9).
- Closed-set validation of brief body section headings at write-time (`## Thesis`, `## Why this is a moat`, etc.); silently-renamed sections currently break `seen.jsonl` regeneration.
- `mr doctor` — interactive recovery for lifecycle-violation states that the deterministic rule in §12.1 cannot resolve (e.g., the same slug appearing in unrelated branches like `rejected/` and `approved/`).

---

## 16. Success criteria

1. `mr discover --lane ephemeral_public --n 5 --budget 1` produces 5 candidates with cited sources, totaling ≤ $1 in spend.
2. `mr score candidates/*.md --budget 1` routes each to `scored/` or `rejected/` with the auto-reject rules in 5.5 enforced.
3. `mr graduate approved/<top>.md` emits a hand-off prompt that, pasted into a fresh project, runs without further `moat-research` access.
4. `.moat-research/costs.jsonl` reflects every API call within ±2% of Anthropic's reported usage for the same window.
5. Two concurrent `mr` invocations on the same brief block correctly via `flock(2)`; neither corrupts state.
6. The full corpus + prompts + config can be cloned to a fresh machine and run with `uv sync && mr init`.
7. **Dedup is selective, not blunt:** running `mr discover --lane ephemeral_public --n 5` twice produces no exact-`slug`/exact-`source_set` collisions. **However**, the second run is still permitted to propose a `cross_source_fusion` candidate whose `source_set` re-uses a host from the first run's output, provided the combined set is novel. Pre-pended dedup context stays under ~3k tokens regardless of corpus size.
