---
title: moat-research design
date: 2026-05-04
status: draft
owner: solo
related_projects:
  - somd-cameras
  - maximizer
---

# moat-research

## 1. Purpose

`moat-research` is a structured corpus and toolchain for **discovering, scoring, and queueing exploitable "data moat" opportunities** that a solo operator can act on with the available hardware. Its outputs are reviewed by a human and, when approved, become initialization prompts for new projects that `maximizer` then drives.

A "moat" here means a dataset, archive, derived artifact, or fused corpus that:
- is feasible to capture/produce *now* with the operator's hardware, and
- is **impossible or impractical to retroactively reconstruct later**, and
- has a plausible monetization path.

The archetype is `somd-cameras`: CHART publishes traffic-camera feeds in real time but does not archive them, so historical footage exists nowhere except where someone chose to record it. `moat-research` exists to find more situations like that — across many lanes, geographies, and verticals — and to make the pipeline from idea to executable project repeatable.

## 2. Non-goals

- `moat-research` does **not** call models. All synthesis, scoring, and prompt generation is performed by `maximizer` during its iteration windows against this repo. This keeps cost coordinated under the existing project-budget split.
- `moat-research` does **not** auto-promote ideas into projects. Promotion from `scored/` to `approved/` is always a human action.
- `moat-research` does **not** pick the technical stack for downstream projects. The init-prompt only describes the operational envelope; stack design happens interactively at project-init time.
- `moat-research` does **not** scrape or capture the moat data itself. That is the job of the project that gets spun up after a brief is approved and graduated.
- `moat-research` is geography-agnostic. Southern Maryland is a permitted lane, not a focus.

## 3. Hard constraints

The following are **automatic disqualifiers** during scoring and must be re-checked at the init-prompt step:

1. Anything requiring authentication-bypass or CFAA-adjacent activity.
2. Anything requiring a request rate that violates published rate limits, robots.txt, or upstream ToS.
3. Anything requiring ongoing un-automatable human labor (curation, sales motion, partnerships) that a solo operator cannot sustain.
4. Anything that, in aggregate across the swarm, would constitute a DDOS-grade load against any single source. The orchestrator throttles the *whole swarm*, not just per-service.

A brief that scores `0` on any axis is auto-routed to `rejected/`.

## 4. Lanes (in scope)

Briefs declare exactly one primary lane (and may list secondaries):

1. **Ephemeral public data** — published openly now, not archived by the publisher (the cameras pattern).
2. **Soon-to-be-restricted data** — currently open, visibly trending toward paywall/API-shutdown/regulatory closure; capture before the door closes.
3. **Cross-source fusion moats** — sources are individually public and archived, but the time-aligned join with derived features is what nobody else has.
4. **Derived-artifact moats** — public raw exists, but the processed artifact (embeddings, OCR, transcription, structured extraction at scale) is the moat; compute is the barrier.
5. **Niche-vertical intelligence** — pick an underserved vertical and become the only entity with a clean longitudinal dataset on it.

Lane 6 (model-training corpora) is intentionally out of scope: the "buyer" market is concentrated and harder for a solo operator to reach.

## 5. Feasibility rubric

Each brief is scored on three axes, each 0–10. Composite = weighted product (zeros kill the brief).

### 5.1 Financial return (weight 0.4)

Sub-criteria, averaged:

- **Buyer existence** — Identifiable parties who would pay (data brokers, hedge funds, journalists, researchers, vertical SaaS, ad-hoc consulting clients). Concrete > theoretical.
- **Pricing precedent** — Comparable data sells where, at what order of magnitude.
- **Time-to-revenue** — Months until the dataset is valuable enough to monetize.
- **Ongoing revenue potential** — Distinguishes one-shot sales (a frozen archive) from recurring/subscription value (a live feed, an API others depend on, a dataset that compounds). Briefs that score well on *both* one-shot and ongoing get the highest financial mark.
- **Market gap** — Is there a *current, identifiable gap* in what existing providers offer that a solo operator on a single server can fill? A high score requires both (a) no incumbent currently sells this exact thing, *and* (b) the gap is not one an incumbent can plausibly close by minor tweaks to their existing product (e.g., adding a column, extending a date range, flipping a feature flag). A 10 means the gap exists *because* incumbents structurally can't or won't enter (regulatory, geographic, vertical-knowledge, or attention-allocation reasons); a 0 means the market is either saturated or one product-meeting away from being saturated. This sub-criterion is the explicit answer to "is there a point in even trying given the team size?"
- **Defensibility** — Once acquired, how hard is it for a well-resourced incumbent to catch up. The past being unrecoverable is the strongest form. Distinct from *Market gap*: gap is "is there room today?", defensibility is "once we're in, how long do we hold it?"

### 5.2 Implementation possibility (weight 0.3)

Sub-criteria, averaged:

- **Source stability** — Likelihood the upstream changes format, adds auth, or shuts down.
- **Legal/ToS risk** — Clearly public > grey area > scraped-against-ToS. Anything violating ToS, rate limits, robots.txt, or applicable law is a hard `0` (and thus a rejection). Reputational risk is fully covered by staying inside these lines.
- **Solo-operator load** — Ongoing curation, partnerships, or sales. Lower is better.
- **Failure modes** — What breaks if the operator is unavailable for two weeks.

### 5.3 Hardware fit (weight 0.3)

Sub-criteria, averaged:

- **Storage growth rate** — GB/month vs. 17 TB headroom.
- **Compute profile** — CPU-bound (good, 56 cores), GPU-bound (constrained, P4 shared), RAM-bound (good, 250 GB), I/O-bound (NAS-dependent).
- **Stack fit** — Must be expressible as one or more isolated microservices in a single-node Docker swarm.
- **Concurrency cost** — How many of these can run in parallel before they fight each other or external rate limits.

### 5.4 Composite

`composite = (financial^0.4) * (implementation^0.3) * (hardware^0.3)`

Range 0.000–10.000. Any axis = 0 → composite = 0 → auto-reject.

## 6. Lifecycle

```
briefs/
  candidates/    discovered, not yet scored
  scored/        scored & ranked, awaiting human review
  rejected/      auto- (any axis = 0) or user-rejected, with reason
  approved/      human-promoted from scored; init-prompt generated
  graduated/     project exists in maximizer; brief archived with project backref
```

Transitions:

- `(none) → candidates/` — produced by signal ingestion or seed notes.
- `candidates/ → scored/` — produced by maximizer synthesis runs.
- `scored/ → rejected/` — automatic when any axis = 0.
- `scored/ → approved/` — **human only**.
- `approved/ → graduated/` — automatic once the new project repo exists; brief gains a backref.
- Re-scoring may rewrite a brief in place (renaming the file to update the score prefix); git history preserves the score trajectory.

## 7. File format

### 7.1 Canonical brief

YAML frontmatter + markdown body. Filename pattern:

```
<composite_score_padded>-<yyyymmdd>-<slug>.md
```

Score is `00.000`–`10.000`, zero-padded so lexical sort = numerical sort. `ls scored/ | sort -r` gives the top of the queue. Unscored candidates use `--.---`. Rejected briefs use `00.000-<failed-axis>-...` (e.g., `00.000-impl-...`).

Frontmatter schema (required unless noted):

```yaml
id: brief_2026_05_04_fcc_eas_alerts        # stable across renames
title: FCC EAS alert metadata archive
lane: 1                                     # 1..5
secondary_lanes: [3]                        # optional
status: scored                              # candidate|scored|rejected|approved|graduated
created: 2026-05-04
last_scored: 2026-05-04
last_reviewed: null                          # set when human acts on it

source_signals:
  - url: https://...
    note: "Publisher confirmed they don't archive"
    captured: 2026-05-04

description: |
  One-paragraph plain-English description of what the moat is.

proposed_capture:
  what: "Poll FCC EAS endpoint every 60s, store raw + parsed."
  retention: "Indefinite; ~50 MB/year."
  derived_artifacts: ["geo-indexed timeline", "alert-type histograms"]

estimated_resources:
  storage_gb_per_month: 0.005
  cpu_cores: 0.1
  ram_gb: 0.2
  gpu: false
  request_rate_per_min: 1
  concurrent_services: 1

feasibility_scores:
  financial:
    composite: 6.5
    sub:
      buyer_existence: 7
      pricing_precedent: 5
      time_to_revenue: 6
      ongoing_revenue: 8
      market_gap: 7                      # no one currently sells a clean longitudinal EAS archive
      defensibility: 6
    notes: "Researchers and emergency-mgmt consultancies are plausible buyers; gap exists because incumbents see EAS as a side-feed, not a product."
  implementation:
    composite: 9.0
    sub:
      source_stability: 9
      legal_tos_risk: 10
      solo_operator_load: 9
      failure_modes: 8
    notes: "Public feed, no auth, trivially automated."
  hardware:
    composite: 9.5
    sub:
      storage_growth_rate: 10
      compute_profile: 10
      stack_fit: 9
      concurrency_cost: 9
    notes: "Effectively free on this box."

composite_score: 8.031

disqualifiers_checked:
  auth_bypass: false
  rate_limit_violations: false
  tos_robots_violations: false
  unautomatable_human_labor: false
  ddos_grade_load: false

monetization_hypotheses:
  - "Quarterly snapshot sold to emergency-mgmt research orgs."
  - "API access for journalists tracking alert-system reliability."

graduated_to: null                           # set when project exists
```

The markdown body below the frontmatter is free-form analyst notes — discovery story, supporting evidence, things to verify, links.

### 7.2 Generated index

A small generator (project worker, see §9) emits `briefs/index.json`: a flat list of every brief's frontmatter, suitable for machine consumers. JSON is the chosen format for universal parseability and tool compatibility.

### 7.3 Wishlist (`WISHLIST.md`)

A living, append-only list of **known data sources that look promising but have not yet been captured by this project**. Examples: a NOAA dataset noticed in passing, a new municipal camera feed, a newly-published government bulk-data export, an obscure RSS that surfaced in a digest.

The wishlist exists because:
- Discovery is asymmetric in time — you notice a source weeks or months before you decide whether it's brief-worthy. The wishlist captures it before the memory fades.
- It gives `maximizer:discover` a high-quality, low-noise queue to draw from when proposing new `briefs/candidates/` entries (cheaper and higher-yield than re-scanning all signal digests from scratch each time).
- It separates *"this thing exists and could be captured"* (a known source) from *"this is a structured opportunity worth pursuing"* (a brief). Many wishlist entries will never become briefs; that's fine.

Format: a markdown file with a YAML-fronted list of entries, one per source. Both the operator and maximizer may append; only the operator should delete.

```yaml
sources:
  - id: noaa_hrrr_smoke
    title: "NOAA HRRR-Smoke hourly surface concentration"
    url: https://nomads.ncep.noaa.gov/...
    discovered: 2026-05-04
    discovered_by: operator           # operator | maximizer
    lane_hint: 1                       # speculative — not authoritative
    why_interesting: |
      Hourly surface PM2.5 forecasts. NOAA retains rolling 24h only;
      historical reconstruction would require recomputing the model.
    known_constraints: |
      Public, no auth, ~2 GB/day if grib2 is kept; consider derived
      tabular extraction to cut storage.
    estimated_size: "2 GB/day raw, ~50 MB/day extracted"
    rate_limit_notes: "NOMADS asks for ≤120 hits/min; honor it."
    status: backlog                    # backlog | promoted-to-candidate | dismissed
    promoted_to: null                  # brief id, set when status=promoted
    dismissed_reason: null             # set when status=dismissed
```

Lifecycle:
- `backlog` — default for new entries.
- `promoted-to-candidate` — `maximizer:discover` (or the operator) decided the source warrants a real brief; `promoted_to` references the new `briefs/candidates/<...>.md`.
- `dismissed` — operator (or maximizer with a clear hard-constraint trigger) determined the source isn't worth pursuing; `dismissed_reason` captures why so the same wishlist entry isn't re-promoted later.

`maximizer:discover` is **expected to append** to `WISHLIST.md` whenever it identifies a candidate source while reading signal digests, even if it doesn't immediately turn it into a brief. This makes the wishlist the durable surface area of "things we know exist" — the brief corpus is just the subset deemed worth committing to.

`WISHLIST.md` is part of the stable interface contract (§9.5).

### 7.4 Init-prompt artifact

When a brief lands in `approved/`, a watcher generates a sibling file `approved/<id>.init-prompt.md`. Sections:

1. **Project title & suggested repo/stack name**
2. **Mission statement** — 1–2 sentences from the brief.
3. **Capture scope** — sources, rate budget, storage budget, retention policy.
4. **Operational envelope** — fixed text describing the available hardware (250 GB RAM, 56 cores, P4 shared, 17 TB NAS) and the preferred operational pattern (single-node Docker swarm, isolated microservices, polite/rate-respecting ingest, no auth-bypass).
5. **Stack-design questions for init** — concrete questions to answer when designing the stack interactively (cadence, storage shape, GPU need, etc.).
6. **Success criteria** for iteration 1.
7. **Out-of-scope guardrails** — what *not* to do in iteration 1 to avoid scope creep.
8. **Disqualifier re-check** — last pass before the project is real.

The init-prompt is a *starting point* the operator edits during project initialization; it does not pre-decide the stack.

## 8. Repo layout

```
moat-research/
  CLAUDE.md                              # project-level Claude Code context (imports FOCUS, WISHLIST, etc.)
  FOCUS.md                               # operator-curated priority overrides (read FIRST by maximizer)
  WISHLIST.md                            # known-but-not-yet-captured data sources (see §7.3)
  README.md                              # quick orientation
  RUBRIC.md                              # canonical rubric (§5), referenced by maximizer
  LANES.md                               # lane definitions (§4)
  CONSTRAINTS.md                         # hard constraints (§3)
  SEED_NOTES.md                          # operator-appendable raw idea fragments
  briefs/
    candidates/
    scored/
    rejected/
    approved/
    graduated/
    index.json                           # generated
  signals/
    sources.yml                          # registry of ingest sources (see §9)
    raw/                                 # rotating raw signal storage (NAS-mounted)
    digests/                             # daily summarized digests for synthesis
  workers/
    ingest/                              # one Dockerized ingestor per source
    promoter/                            # scored→rejected auto-promoter
    indexer/                             # rebuilds briefs/index.json
    init-prompt-gen/                     # approved → init-prompt watcher
  stacks/
    moat-research.yml                    # docker swarm stack file
  docs/
    superpowers/
      specs/
        2026-05-04-moat-research-design.md
```

## 9. Components

Every component is an isolated Docker microservice in `stacks/moat-research.yml`, runnable on the existing single-node swarm. None of them call models — model work happens when maximizer iterates against this repo.

### 9.1 Signal ingestors (`workers/ingest/*`)

One service per source. Each declares in `signals/sources.yml`:

```yaml
- id: fcc_eas_feed
  url: ...
  cadence: 60s
  rate_budget_per_min: 1
  storage_path: /signals/raw/fcc_eas
  parser: jsonl
  enabled: true
```

Behavior:
- Fetch on cadence, append to rotating raw storage on the NAS.
- Respect robots.txt at startup; refuse to start if disallowed.
- Honor `Retry-After` and 429s with exponential backoff.
- Emit a daily digest into `signals/digests/<date>/<id>.md` summarizing volume + interesting deltas (using deterministic code, not models).

The **swarm-aggregate throttle** lives in the orchestrator (a tiny coordinator service that issues fetch tokens), not per-ingestor. This is the structural defense against the DDOS disqualifier.

### 9.2 Promoter (`workers/promoter`)

Watches `briefs/scored/`. On any new/changed file, parses frontmatter; if any axis = 0, `mv`s to `briefs/rejected/` with the failed axis recorded in the filename and a `rejection_reason` field appended to the frontmatter. Pure Python/Bash, deterministic.

### 9.3 Indexer (`workers/indexer`)

On any change in `briefs/`, regenerates `briefs/index.json`. Triggered by inotify or a 60s sweep (whichever is simpler).

### 9.4 Init-prompt generator (`workers/init-prompt-gen`)

Watches `briefs/approved/`. On a new file, renders `<id>.init-prompt.md` from a template populated with the brief's frontmatter and the operator-defined operational envelope. Idempotent.

### 9.5 Synthesis (no service — runs as maximizer iteration)

When maximizer rotates to moat-research, **the very first thing it reads is `FOCUS.md`**. `FOCUS.md` is the operator's priority-override channel: anything queued there is done before any organic discovery/scoring work, in the order listed. Once a focus item is satisfied, maximizer ticks it off (or removes it) and proceeds to the next; only when `FOCUS.md` has no actionable items does it fall through to the standard menu below.

Standard synthesis actions (executed only when `FOCUS.md` is empty/satisfied):

- **Discover** — read recent `signals/digests/` *and* the `backlog`-status entries in `WISHLIST.md`. May (a) propose new entries for `briefs/candidates/`, (b) append newly-noticed sources to `WISHLIST.md` as `backlog`, (c) promote a wishlist entry to a candidate (set `status: promoted-to-candidate`, fill `promoted_to`).
- **Score** — pick a `briefs/candidates/` entry, score it against `RUBRIC.md`, write into `briefs/scored/` with the score-prefixed filename. The promoter will auto-reject if any axis is 0.
- **Re-score** — re-evaluate an existing `scored/` brief if signals have shifted; rewrite the file (filename changes if score changes, but the directory and `id` remain the same).
- **Generate init-prompt** — alternative to the watcher; useful when maximizer is already in the loop.
- **Wishlist hygiene** — when a wishlist entry has been `backlog` for >90 days without promotion, surface it for operator review (do not auto-dismiss).

The maximizer relies on: `FOCUS.md` (priority override), `WISHLIST.md` (known-source backlog), `RUBRIC.md`, `LANES.md`, `CONSTRAINTS.md`, the brief frontmatter schema, and the file-naming convention. These are the stable interfaces.

### 9.6 How the overall concept reaches maximizer

The existing `claude-runner` orchestrator (`/home/runner/claude-runner/`) injects per-project context into every iteration via three concrete surfaces. moat-research must populate all three:

1. **`claude-runner/config/projects/moat-research/system-prompt.md`** — A short (≤1 KB) per-project preamble appended to every iteration's system prompt. This is where the *thesis of the project* lives — what moat-research is, what success looks like, the hardest hard rules. Modeled on the existing `cameras/system-prompt.md`. Created and maintained as part of project bootstrap.
2. **`moat-research/CLAUDE.md`** — Project-level Claude Code context, read at session start. Imports the operator-facing artifacts via `@FOCUS.md`, `@WISHLIST.md`, `@RUBRIC.md`, `@LANES.md`, `@CONSTRAINTS.md`. Mirrors the somd-cameras pattern (which `@`-imports its `FOCUS.md`).
3. **`moat-research/FOCUS.md`** — Already specified. The Plan stage of the orchestrator (`config/prompts/plan.md`) explicitly reads this and mirrors any unchecked bullets as iteration acceptance criteria.

Together: the system-prompt sets the durable thesis, `CLAUDE.md` pulls in the live operator-facing files, `FOCUS.md` sets near-term priorities, and `WISHLIST.md` provides the known-source backlog. None of these contain implementation detail — they describe *what* and *why*; the rubric, lanes, and constraints describe *how to score*; the briefs themselves are the work product.

## 10. Data flow

```
external sources ──► ingestors ──► signals/raw ──► (daily) signals/digests
                                                           │
                                                           ▼
SEED_NOTES.md ─┐                              maximizer:discover ──► appends backlog
WISHLIST.md ───┴──────────────────────────────►        │             entries to WISHLIST.md
                                                       │             promotes wishlist
                                                       ▼             entries to candidates
                                                  briefs/candidates/
                                                           │
                                              maximizer:score
                                                           │
                                                           ▼
                                                  briefs/scored/      ◄── operator review
                                                       │     │
                                              promoter (auto)│
                                                       │     │ operator promotes
                                                       ▼     ▼
                                                rejected/  approved/
                                                                │
                                                       init-prompt-gen
                                                                │
                                                                ▼
                                            approved/<id>.init-prompt.md
                                                                │
                                                       operator + maximizer
                                                       initialize new project
                                                                │
                                                                ▼
                                                         graduated/
```

## 11. Error handling & isolation

- Every ingestor runs as its own service with a hard memory/CPU cap in the stack file. A misbehaving ingestor cannot starve the others or the swarm coordinator.
- Network errors: exponential backoff with jitter, capped retry count, circuit breaker on persistent failure (auto-disable in `sources.yml` and emit a digest entry).
- Storage: ingestors write to NAS-mounted volumes; promoter, indexer, init-prompt-gen operate on the repo working tree only.
- Parsing errors in brief frontmatter: the worker quarantines the offending file in a `_quarantine/` subdir and continues. No worker should ever crash the swarm because of a single malformed brief.
- All workers are stateless — restarting a service should never lose progress beyond the last completed unit of work.

## 12. Seeding

To bootstrap from empty:

- `RUBRIC.md`, `LANES.md`, `CONSTRAINTS.md` are committed at project start (derived from §3–§5 of this spec).
- `CLAUDE.md` is committed with `@FOCUS.md`, `@WISHLIST.md`, `@RUBRIC.md`, `@LANES.md`, `@CONSTRAINTS.md` imports.
- `claude-runner/config/projects/moat-research/system-prompt.md` is created in the orchestrator repo, modeled on `cameras/system-prompt.md`, stating the project thesis and the three or four hardest rules (no model calls in this repo; never auto-promote `scored→approved`; FOCUS.md is the priority override; respect rate limits and ToS).
- `somd-cameras` is converted into a `briefs/graduated/` reference brief, illustrating the canonical schema and serving as a synthesis pattern. (This is also Item 1 of `FOCUS.md` — the rubric calibration check.)
- `SEED_NOTES.md` starts as a one-line file the operator appends raw idea fragments to. Maximizer reads it during `discover` runs and may move structured fragments into `briefs/candidates/`.
- `WISHLIST.md` starts with a small operator-curated set of known-promising sources (e.g., 3–5 entries) so `maximizer:discover` has real material to work against on the first run.
- A tiny initial signal set (3–5 sources, e.g., one government data portal RSS, one regulatory filings feed, one HN, one arXiv category, one GitHub trending) is registered in `signals/sources.yml` so the corpus has something to chew on from day one.

## 13. Testing

- **Unit**: promoter, indexer, init-prompt-gen, and the rubric composite-score function each get unit tests against fixture briefs. The composite-score function in particular gets edge-case tests (zeros on each axis, all-tens, tied scores).
- **Integration**: a fixtures-driven test that walks a sample brief through `candidate → scored → rejected` and `candidate → scored → approved → init-prompt` end-to-end against a temp repo.
- **Ingestor contract test**: every ingestor implements a shared interface (start, fetch, digest, healthcheck) verified by a contract-test harness, so adding a new source is mechanical.
- **Politeness test**: a static linter scans every entry in `signals/sources.yml` against a checklist (declared rate budget, robots.txt check at startup, retry/backoff policy present). CI fails if any source skips the checklist.

## 14. Open questions

None blocking. The following are intentionally deferred to first iteration and not part of this spec:

- The exact set of seed signal sources beyond the small starter set (will grow organically as the operator and maximizer find them).
- Whether `briefs/index.json` should also be emitted in TOON form for token-efficient reads — defer until a measurable token cost on the maximizer side justifies it.
- Whether the composite-score formula should be tunable per-operator (e.g., shifting weights as priorities change) — defer; the current weights are written into `RUBRIC.md` and any change is a deliberate edit.
