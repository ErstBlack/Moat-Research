# moat-research Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the moat-research corpus + worker stack so that maximizer can discover, score, queue, and (on operator approval) generate project-init prompts for "data moat" opportunities — without making any model calls inside this repo.

**Architecture:** A single git repo containing (a) operator-facing canonical docs (RUBRIC, LANES, CONSTRAINTS, FOCUS, WISHLIST, CLAUDE), (b) a brief corpus on disk in five lifecycle directories with score-prefixed filenames, (c) a small set of stateless Python microservices (promoter, indexer, init-prompt-gen, swarm coordinator, ingestor base) deployed as a single-node Docker swarm stack, and (d) one orchestrator-side per-project system-prompt at `claude-runner/config/projects/moat-research/system-prompt.md`. Synthesis (idea generation, scoring, init-prompt rendering) is performed by maximizer iterating against this repo, not by anything in the repo itself.

**Tech Stack:**
- Python 3.11+, managed with `uv` (matches existing claude-runner pattern)
- `pyyaml` for frontmatter, `pytest` for tests
- Stdlib `http.server` for the coordinator (no FastAPI dependency)
- Docker / Docker Swarm for deployment (single-node swarm already in use)
- `pre-commit` for the politeness lint + unit-test gate

---

## File structure

To be created in `/home/runner/moat-research/` (operator working dir):

```
moat-research/
  pyproject.toml                                  # uv project, deps + pytest config
  uv.lock                                         # generated
  .python-version                                 # 3.11
  .gitignore
  .pre-commit-config.yaml
  README.md                                       # quick orientation
  CLAUDE.md                                       # project-level Claude Code context (@-imports)
  FOCUS.md                                        # exists
  WISHLIST.md                                     # exists
  RUBRIC.md                                       # canonical rubric, mirrors spec §5
  LANES.md                                        # canonical lanes, mirrors spec §4
  CONSTRAINTS.md                                  # canonical hard constraints, mirrors spec §3
  SEED_NOTES.md                                   # operator-appendable raw fragments
  briefs/
    candidates/.gitkeep
    scored/.gitkeep
    rejected/.gitkeep
    approved/.gitkeep
    graduated/.gitkeep
  signals/
    sources.yml                                   # registry: empty list to start
    raw/.gitkeep                                  # NAS-mounted in prod; gitkeep locally
    digests/.gitkeep
  workers/
    __init__.py
    common/
      __init__.py
      brief.py                                    # parse/serialize/score/filename helpers
      throttle.py                                 # coordinator client (token-bucket caller)
    promoter/
      __init__.py
      promoter.py                                 # scored→rejected on any-axis-zero
      Dockerfile
    indexer/
      __init__.py
      indexer.py                                  # briefs/index.json regenerator
      Dockerfile
    init_prompt_gen/
      __init__.py
      init_prompt_gen.py                          # approved → init-prompt artifact watcher
      template.md                                 # init-prompt template
      Dockerfile
    ingest/
      __init__.py
      base.py                                     # BaseIngestor abstract class + contract
      Dockerfile.base
    coordinator/
      __init__.py
      coordinator.py                              # swarm-aggregate token-bucket HTTP service
      Dockerfile
  scripts/
    politeness_lint.py                            # CI-blocking lint of signals/sources.yml
  stacks/
    moat-research.yml                             # docker swarm stack file
  tests/
    __init__.py
    fixtures/
      brief_valid_scored.md
      brief_zero_financial.md
      brief_zero_implementation.md
      brief_zero_hardware.md
      brief_candidate_unscored.md
      brief_approved.md
      sources_clean.yml
      sources_missing_rate_budget.yml
    unit/
      test_brief.py
      test_promoter.py
      test_indexer.py
      test_init_prompt_gen.py
      test_coordinator.py
      test_ingest_base.py
      test_politeness_lint.py
    integration/
      test_lifecycle.py                           # candidate→scored→rejected and →approved→init-prompt
  docs/
    superpowers/
      specs/2026-05-04-moat-research-design.md    # exists
      plans/2026-05-04-moat-research-implementation.md  # this file
```

To be created outside this repo:

```
/home/runner/claude-runner/config/projects/moat-research/
  system-prompt.md                                # per-project orchestrator preamble
```

Each file has one responsibility. The `workers/common/brief.py` module is the single source of truth for the brief schema, score formula, and filename convention — every worker imports from it. This is the most important boundary in the project; if the schema changes, only this file and its tests change.

---

## Task 1: Initialize git repo and Python project

**Files:**
- Create: `/home/runner/moat-research/.gitignore`
- Create: `/home/runner/moat-research/pyproject.toml`
- Create: `/home/runner/moat-research/.python-version`

- [ ] **Step 1: Initialize git in the project directory**

```bash
cd /home/runner/moat-research && git init -b main
```

Expected: `Initialized empty Git repository in /home/runner/moat-research/.git/`

- [ ] **Step 2: Write `.gitignore`**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.egg-info/

# uv
.python-version

# Editor
.vscode/
.idea/
*.swp

# OS
.DS_Store

# Local data — must NEVER be committed
signals/raw/*
!signals/raw/.gitkeep
signals/digests/*
!signals/digests/.gitkeep

# Generated
briefs/index.json
```

- [ ] **Step 3: Write `pyproject.toml`**

```toml
[project]
name = "moat-research"
version = "0.1.0"
description = "Discovery, scoring, and queueing of data-moat opportunities for maximizer"
requires-python = ">=3.11"
dependencies = [
    "pyyaml>=6.0.1",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.6.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"
markers = [
    "integration: marks tests as integration (slower, hit the filesystem)",
]

[tool.ruff]
line-length = 100
target-version = "py311"
```

- [ ] **Step 4: Write `.python-version`**

```
3.11
```

- [ ] **Step 5: Create the venv and install deps**

```bash
cd /home/runner/moat-research && uv sync
```

Expected: `.venv/` is created; `uv.lock` is generated.

- [ ] **Step 6: Commit**

```bash
cd /home/runner/moat-research && git add .gitignore pyproject.toml uv.lock .python-version FOCUS.md WISHLIST.md docs/superpowers/specs/2026-05-04-moat-research-design.md docs/superpowers/plans/2026-05-04-moat-research-implementation.md && git commit -m "chore: initialize moat-research repo"
```

---

## Task 2: Materialize canonical docs (RUBRIC / LANES / CONSTRAINTS / SEED_NOTES / README / CLAUDE)

**Files:**
- Create: `/home/runner/moat-research/RUBRIC.md`
- Create: `/home/runner/moat-research/LANES.md`
- Create: `/home/runner/moat-research/CONSTRAINTS.md`
- Create: `/home/runner/moat-research/SEED_NOTES.md`
- Create: `/home/runner/moat-research/README.md`
- Create: `/home/runner/moat-research/CLAUDE.md`

These mirror the spec sections verbatim so maximizer can read them without re-resolving the spec. Each file's first line cites the spec section it came from so drift is easy to spot.

- [ ] **Step 1: Write `RUBRIC.md`**

```markdown
# RUBRIC

> Mirrors `docs/superpowers/specs/2026-05-04-moat-research-design.md` §5. If you change this file, also update the spec.

Each brief is scored on three axes, each 0–10. Composite = weighted product (zeros kill the brief).

## Financial return (weight 0.4)

Sub-criteria, averaged:

- **Buyer existence** — Identifiable parties who would pay (data brokers, hedge funds, journalists, researchers, vertical SaaS, ad-hoc consulting clients). Concrete > theoretical.
- **Pricing precedent** — Comparable data sells where, at what order of magnitude.
- **Time-to-revenue** — Months until the dataset is valuable enough to monetize.
- **Ongoing revenue potential** — Distinguishes one-shot sales (a frozen archive) from recurring/subscription value (a live feed, an API others depend on, a dataset that compounds). Briefs that score well on *both* one-shot and ongoing get the highest financial mark.
- **Market gap** — Is there a *current, identifiable gap* in what existing providers offer that a solo operator on a single server can fill? A high score requires both (a) no incumbent currently sells this exact thing, *and* (b) the gap is not one an incumbent can plausibly close by minor tweaks to their existing product. A 10 means the gap exists *because* incumbents structurally can't or won't enter; a 0 means the market is either saturated or one product-meeting away from being saturated.
- **Defensibility** — Once acquired, how hard is it for a well-resourced incumbent to catch up. The past being unrecoverable is the strongest form. Distinct from *Market gap*: gap is "is there room today?", defensibility is "once we're in, how long do we hold it?"

## Implementation possibility (weight 0.3)

Sub-criteria, averaged:

- **Source stability** — Likelihood the upstream changes format, adds auth, or shuts down.
- **Legal/ToS risk** — Clearly public > grey area > scraped-against-ToS. Anything violating ToS, rate limits, robots.txt, or applicable law is a hard `0` (and thus a rejection).
- **Solo-operator load** — Ongoing curation, partnerships, or sales. Lower is better.
- **Failure modes** — What breaks if the operator is unavailable for two weeks.

## Hardware fit (weight 0.3)

Sub-criteria, averaged:

- **Storage growth rate** — GB/month vs. 17 TB headroom.
- **Compute profile** — CPU-bound (good, 56 cores), GPU-bound (constrained, P4 shared), RAM-bound (good, 250 GB), I/O-bound (NAS-dependent).
- **Stack fit** — Must be expressible as one or more isolated microservices in a single-node Docker swarm.
- **Concurrency cost** — How many of these can run in parallel before they fight each other or external rate limits.

## Composite

`composite = (financial^0.4) * (implementation^0.3) * (hardware^0.3)`

Range 0.000–10.000. Any axis = 0 → composite = 0 → auto-reject.
```

- [ ] **Step 2: Write `LANES.md`**

```markdown
# LANES

> Mirrors `docs/superpowers/specs/2026-05-04-moat-research-design.md` §4. If you change this file, also update the spec.

Each brief declares exactly one primary lane (and may list secondaries):

1. **Ephemeral public data** — published openly now, not archived by the publisher (the cameras pattern).
2. **Soon-to-be-restricted data** — currently open, visibly trending toward paywall/API-shutdown/regulatory closure; capture before the door closes.
3. **Cross-source fusion moats** — sources are individually public and archived, but the time-aligned join with derived features is what nobody else has.
4. **Derived-artifact moats** — public raw exists, but the processed artifact (embeddings, OCR, transcription, structured extraction at scale) is the moat; compute is the barrier.
5. **Niche-vertical intelligence** — pick an underserved vertical and become the only entity with a clean longitudinal dataset on it.

Lane 6 (model-training corpora) is intentionally out of scope: the buyer market is concentrated and harder for a solo operator to reach.
```

- [ ] **Step 3: Write `CONSTRAINTS.md`**

```markdown
# CONSTRAINTS

> Mirrors `docs/superpowers/specs/2026-05-04-moat-research-design.md` §3. If you change this file, also update the spec.

The following are **automatic disqualifiers** during scoring and must be re-checked at the init-prompt step:

1. Anything requiring authentication-bypass or CFAA-adjacent activity.
2. Anything requiring a request rate that violates published rate limits, robots.txt, or upstream ToS.
3. Anything requiring ongoing un-automatable human labor (curation, sales motion, partnerships) that a solo operator cannot sustain.
4. Anything that, in aggregate across the swarm, would constitute a DDOS-grade load against any single source. The orchestrator throttles the *whole swarm*, not just per-service.

A brief that scores `0` on any axis is auto-routed to `rejected/`.
```

- [ ] **Step 4: Write `SEED_NOTES.md`**

```markdown
# SEED_NOTES

Operator-appendable raw idea fragments. No structure required. Maximizer reads this during `discover` runs and may extract structured fragments into `briefs/candidates/` (or `WISHLIST.md` if the fragment is just a known source).

Append freely; do not delete. Garbage collection is a deliberate operator action.
```

- [ ] **Step 5: Write `README.md`**

```markdown
# moat-research

Discovery, scoring, and queueing of "data moat" opportunities — datasets, archives, derived artifacts, or fused corpora that are feasible to capture *now* but impossible or impractical to retroactively reconstruct, and have a plausible monetization path.

This repo is **a corpus + a stateless worker stack**. It does not call models. All synthesis (ideation, scoring, init-prompt generation) is performed by `maximizer` iterating against this repo.

## Where to look first

- `FOCUS.md` — operator priority queue. Read by maximizer before anything else.
- `WISHLIST.md` — known data sources awaiting evaluation.
- `RUBRIC.md`, `LANES.md`, `CONSTRAINTS.md` — scoring rules.
- `briefs/` — the corpus, organized by lifecycle stage.
- `docs/superpowers/specs/2026-05-04-moat-research-design.md` — the design.

## Lifecycle

```
candidates → scored → rejected | approved → graduated
```

- `candidates/` — discovered, not yet scored.
- `scored/` — scored & ranked, awaiting human review.
- `rejected/` — auto- (any axis = 0) or operator-rejected.
- `approved/` — operator-promoted from scored; init-prompt artifact generated.
- `graduated/` — project exists in maximizer; brief archived with backref.

Files are score-prefixed (`08.031-20260504-fcc-eas-alerts.md`); `ls scored/ | sort -r` is the queue.

## Workers

All workers are Python, stateless, deployed as a single-node Docker swarm stack (`stacks/moat-research.yml`). See `docs/superpowers/specs/2026-05-04-moat-research-design.md` §9 for the full component list.
```

- [ ] **Step 6: Write `CLAUDE.md`**

```markdown
# moat-research

This is the moat-research project. Read `docs/superpowers/specs/2026-05-04-moat-research-design.md` for the full design.

## Hard rules

1. **No model calls in this repo.** All synthesis is done by maximizer iterating against this repo. Workers here are stateless Python.
2. **`scored → approved` is human-only.** Never auto-promote.
3. **`FOCUS.md` is the priority override.** Read it first; complete its items in order before any organic work.
4. **Respect rate limits, ToS, robots.txt.** Hard disqualifiers, no exceptions. See `CONSTRAINTS.md`.

## Operator-facing surfaces (read these before acting)

@FOCUS.md
@WISHLIST.md
@RUBRIC.md
@LANES.md
@CONSTRAINTS.md
```

- [ ] **Step 7: Commit**

```bash
cd /home/runner/moat-research && git add RUBRIC.md LANES.md CONSTRAINTS.md SEED_NOTES.md README.md CLAUDE.md && git commit -m "docs: materialize canonical rubric/lanes/constraints from spec"
```

---

## Task 3: Create directory skeleton

**Files:**
- Create: `briefs/{candidates,scored,rejected,approved,graduated}/.gitkeep`
- Create: `signals/{raw,digests}/.gitkeep`
- Create: `signals/sources.yml`
- Create: `workers/__init__.py`, `tests/__init__.py`

- [ ] **Step 1: Create empty directories with `.gitkeep`**

```bash
cd /home/runner/moat-research && \
  mkdir -p briefs/{candidates,scored,rejected,approved,graduated} \
           signals/{raw,digests} \
           workers/common workers/promoter workers/indexer \
           workers/init_prompt_gen workers/ingest workers/coordinator \
           scripts stacks tests/fixtures tests/unit tests/integration && \
  touch briefs/{candidates,scored,rejected,approved,graduated}/.gitkeep \
        signals/raw/.gitkeep signals/digests/.gitkeep
```

- [ ] **Step 2: Create empty `signals/sources.yml`**

```yaml
# signals/sources.yml
# Registry of ingest sources. See docs/superpowers/specs/2026-05-04-moat-research-design.md §9.1.
# Each entry must declare: id, url, cadence, rate_budget_per_min, storage_path, parser, enabled.
sources: []
```

- [ ] **Step 3: Create Python package `__init__.py` files (all empty)**

```bash
cd /home/runner/moat-research && \
  touch workers/__init__.py workers/common/__init__.py workers/promoter/__init__.py \
        workers/indexer/__init__.py workers/init_prompt_gen/__init__.py \
        workers/ingest/__init__.py workers/coordinator/__init__.py \
        tests/__init__.py tests/unit/__init__.py tests/integration/__init__.py
```

- [ ] **Step 4: Verify the tree**

```bash
cd /home/runner/moat-research && find briefs signals workers tests -type f | sort
```

Expected (subset): `briefs/candidates/.gitkeep`, `signals/sources.yml`, `workers/common/__init__.py`, etc.

- [ ] **Step 5: Commit**

```bash
cd /home/runner/moat-research && git add briefs/ signals/ workers/ tests/ scripts/ stacks/ && git commit -m "chore: directory skeleton for briefs/signals/workers/tests"
```

---

## Task 4: Write the per-project orchestrator system-prompt

**Files:**
- Create: `/home/runner/claude-runner/config/projects/moat-research/system-prompt.md`

This file is read by the maximizer orchestrator as the per-project preamble injected into every iteration. It is intentionally small (≤1 KB).

- [ ] **Step 1: Confirm the orchestrator config dir exists**

```bash
ls /home/runner/claude-runner/config/projects/
```

Expected: at least `cameras/` and `maximizer/` listed.

- [ ] **Step 2: Create the `moat-research` project subdir**

```bash
mkdir -p /home/runner/claude-runner/config/projects/moat-research
```

- [ ] **Step 3: Write `system-prompt.md`**

```markdown
# moat-research project — additional rules

You are working in `/home/runner/moat-research`. This project is a structured corpus and stateless worker stack for discovering, scoring, and queueing "data moat" opportunities — datasets/archives that are feasible to capture *now* but impossible to retroactively reconstruct, and have a plausible monetization path. The somd-cameras project is the archetype; moat-research exists to find more situations like it.

- **No model calls in this repo.** All synthesis (ideation, scoring, init-prompt generation) is *your* job during this iteration. Workers in `workers/` are deterministic Python.
- **Read `FOCUS.md` first**, then `WISHLIST.md`. Items in FOCUS run in order before any organic discovery work; unchecked FOCUS items must map onto this iteration's tasks.
- **Never auto-promote `scored → approved`.** That transition is human-only.
- **Hard constraints from `CONSTRAINTS.md` apply.** Never propose or score a brief that requires auth-bypass, ToS/rate-limit/robots.txt violations, or DDOS-grade load.
- For any new file you create, label docker resources with `maximizer-iter=$MAXIMIZER_ITERATION_ID` so cleanup can find them.
- `RUBRIC.md`, `LANES.md`, `CONSTRAINTS.md` mirror sections of the design spec at `docs/superpowers/specs/2026-05-04-moat-research-design.md`. If you change one, change the other.
```

- [ ] **Step 4: Verify size and content**

```bash
wc -c /home/runner/claude-runner/config/projects/moat-research/system-prompt.md
```

Expected: ≤1024 bytes.

- [ ] **Step 5: Commit (in claude-runner repo, not moat-research)**

```bash
cd /home/runner/claude-runner && git add config/projects/moat-research/system-prompt.md && git commit -m "feat(projects): register moat-research project preamble"
```

---

## Task 5: Build `workers/common/brief.py` — composite_score function (TDD)

**Files:**
- Create: `tests/unit/test_brief.py`
- Create: `workers/common/brief.py`

This is the most-imported function in the codebase; it must be exact.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_brief.py
import math
import pytest
from workers.common import brief


class TestCompositeScore:
    def test_all_tens_returns_ten(self):
        assert brief.composite_score(10, 10, 10) == pytest.approx(10.0)

    def test_zero_financial_returns_zero(self):
        assert brief.composite_score(0, 10, 10) == 0.0

    def test_zero_implementation_returns_zero(self):
        assert brief.composite_score(10, 0, 10) == 0.0

    def test_zero_hardware_returns_zero(self):
        assert brief.composite_score(10, 10, 0) == 0.0

    def test_known_values_match_formula(self):
        # financial=6.5, implementation=9.0, hardware=9.5 — example from spec §7.1
        result = brief.composite_score(6.5, 9.0, 9.5)
        expected = (6.5 ** 0.4) * (9.0 ** 0.3) * (9.5 ** 0.3)
        assert result == pytest.approx(expected, rel=1e-9)
        assert result == pytest.approx(8.031, abs=0.005)

    def test_rejects_negative(self):
        with pytest.raises(ValueError):
            brief.composite_score(-1, 5, 5)

    def test_rejects_above_ten(self):
        with pytest.raises(ValueError):
            brief.composite_score(10.1, 5, 5)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /home/runner/moat-research && uv run pytest tests/unit/test_brief.py -v
```

Expected: ImportError or AttributeError on `brief.composite_score`.

- [ ] **Step 3: Write minimal implementation**

```python
# workers/common/brief.py
"""
Single source of truth for the brief schema, score formula, and filename convention.

Every worker imports from this module. If the schema changes, only this file and its
tests change. See docs/superpowers/specs/2026-05-04-moat-research-design.md §5, §7.
"""
from __future__ import annotations


def composite_score(financial: float, implementation: float, hardware: float) -> float:
    """
    Composite feasibility score per spec §5.4.

    Formula: financial^0.4 * implementation^0.3 * hardware^0.3.
    Any axis = 0 short-circuits to 0 (auto-reject).

    Inputs must be in [0, 10]; raises ValueError otherwise.
    """
    for name, value in (("financial", financial), ("implementation", implementation), ("hardware", hardware)):
        if value < 0 or value > 10:
            raise ValueError(f"{name} must be in [0, 10], got {value}")
    if financial == 0 or implementation == 0 or hardware == 0:
        return 0.0
    return (financial ** 0.4) * (implementation ** 0.3) * (hardware ** 0.3)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /home/runner/moat-research && uv run pytest tests/unit/test_brief.py::TestCompositeScore -v
```

Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/runner/moat-research && git add tests/unit/test_brief.py workers/common/brief.py && git commit -m "feat(brief): composite_score function with axis-zero short-circuit"
```

---

## Task 6: Build `workers/common/brief.py` — filename format and parse (TDD)

**Files:**
- Modify: `tests/unit/test_brief.py`
- Modify: `workers/common/brief.py`

Filename convention from spec §7.1: `<00.000-10.000>-<yyyymmdd>-<slug>.md`, with `--.---` for unscored and `00.000-<failed_axis>-...` for rejected.

- [ ] **Step 1: Append failing tests**

```python
# tests/unit/test_brief.py — append below TestCompositeScore

class TestFilename:
    def test_format_score_prefix_padding(self):
        assert brief.format_score_prefix(8.031) == "08.031"
        assert brief.format_score_prefix(10.0) == "10.000"
        assert brief.format_score_prefix(0.0) == "00.000"
        assert brief.format_score_prefix(0.001) == "00.001"

    def test_format_score_prefix_rejects_out_of_range(self):
        with pytest.raises(ValueError):
            brief.format_score_prefix(-0.1)
        with pytest.raises(ValueError):
            brief.format_score_prefix(10.001)

    def test_filename_for_scored(self):
        assert brief.filename_for(8.031, "20260504", "fcc-eas-alerts") == "08.031-20260504-fcc-eas-alerts.md"

    def test_filename_for_unscored(self):
        assert brief.filename_for(None, "20260504", "fcc-eas-alerts") == "--.----20260504-fcc-eas-alerts.md"

    def test_filename_for_rejected(self):
        assert brief.filename_for(0.0, "20260504", "some-thing", failed_axis="financial") == "00.000-financial-20260504-some-thing.md"

    def test_filename_for_rejected_requires_zero_score(self):
        with pytest.raises(ValueError):
            brief.filename_for(5.0, "20260504", "x", failed_axis="financial")

    def test_parse_score_prefix_scored(self):
        assert brief.parse_score_prefix("08.031-20260504-fcc-eas-alerts.md") == 8.031

    def test_parse_score_prefix_unscored(self):
        assert brief.parse_score_prefix("--.----20260504-fcc-eas-alerts.md") is None

    def test_parse_score_prefix_rejected(self):
        # rejected files are 00.000 prefix; the parser returns 0.0
        assert brief.parse_score_prefix("00.000-financial-20260504-x.md") == 0.0

    def test_parse_score_prefix_invalid_raises(self):
        with pytest.raises(ValueError):
            brief.parse_score_prefix("nope.md")

    def test_natural_sort_order(self):
        names = [
            brief.filename_for(7.115, "20260504", "a"),
            brief.filename_for(9.412, "20260504", "b"),
            brief.filename_for(8.730, "20260503", "c"),
        ]
        # Lexical sort = numerical sort (descending = highest first)
        sorted_desc = sorted(names, reverse=True)
        assert sorted_desc[0].startswith("09.412")
        assert sorted_desc[1].startswith("08.730")
        assert sorted_desc[2].startswith("07.115")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/runner/moat-research && uv run pytest tests/unit/test_brief.py::TestFilename -v
```

Expected: AttributeError on `brief.format_score_prefix`, etc.

- [ ] **Step 3: Append implementation**

```python
# workers/common/brief.py — append below composite_score

import re

_SCORED_RE = re.compile(r"^(\d{2}\.\d{3})-")
_UNSCORED_PREFIX = "--.---"


def format_score_prefix(score: float) -> str:
    """Format a score in [0, 10] as a 6-char zero-padded string (e.g. 8.031 -> '08.031')."""
    if score < 0 or score > 10:
        raise ValueError(f"score must be in [0, 10], got {score}")
    return f"{score:06.3f}"


def filename_for(
    score: float | None,
    date: str,
    slug: str,
    *,
    failed_axis: str | None = None,
) -> str:
    """
    Build a brief filename per spec §7.1.

    - score is None -> unscored candidate prefix '--.---'.
    - failed_axis set -> rejected file; score must be 0.0.
    - otherwise -> scored file with score prefix.
    """
    if failed_axis is not None:
        if score != 0.0:
            raise ValueError("failed_axis requires score == 0.0")
        return f"00.000-{failed_axis}-{date}-{slug}.md"
    if score is None:
        return f"{_UNSCORED_PREFIX}-{date}-{slug}.md"
    return f"{format_score_prefix(score)}-{date}-{slug}.md"


def parse_score_prefix(filename: str) -> float | None:
    """
    Extract the leading score from a brief filename.

    Returns None for unscored candidates ('--.---' prefix).
    Returns 0.0 for rejected files (also leading '00.000-').
    Raises ValueError on anything else.
    """
    if filename.startswith(_UNSCORED_PREFIX):
        return None
    m = _SCORED_RE.match(filename)
    if not m:
        raise ValueError(f"no score prefix in filename: {filename}")
    return float(m.group(1))
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /home/runner/moat-research && uv run pytest tests/unit/test_brief.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
cd /home/runner/moat-research && git add tests/unit/test_brief.py workers/common/brief.py && git commit -m "feat(brief): filename format/parse with natural sort guarantee"
```

---

## Task 7: Build `workers/common/brief.py` — frontmatter parse/serialize (TDD)

**Files:**
- Modify: `tests/unit/test_brief.py`
- Modify: `workers/common/brief.py`
- Create: `tests/fixtures/brief_valid_scored.md`
- Create: `tests/fixtures/brief_zero_financial.md`
- Create: `tests/fixtures/brief_zero_implementation.md`
- Create: `tests/fixtures/brief_zero_hardware.md`
- Create: `tests/fixtures/brief_candidate_unscored.md`
- Create: `tests/fixtures/brief_approved.md`

- [ ] **Step 1: Write fixture `brief_valid_scored.md`**

```markdown
---
id: brief_2026_05_04_fcc_eas_alerts
title: FCC EAS alert metadata archive
lane: 1
secondary_lanes: [3]
status: scored
created: 2026-05-04
last_scored: 2026-05-04
last_reviewed: null
source_signals:
  - url: https://example.gov/eas
    note: "Publisher confirmed they don't archive"
    captured: 2026-05-04
description: |
  One-paragraph description.
proposed_capture:
  what: "Poll endpoint every 60s."
  retention: "Indefinite."
  derived_artifacts: ["timeline"]
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
      market_gap: 7
      defensibility: 6
    notes: "n"
  implementation:
    composite: 9.0
    sub:
      source_stability: 9
      legal_tos_risk: 10
      solo_operator_load: 9
      failure_modes: 8
    notes: "n"
  hardware:
    composite: 9.5
    sub:
      storage_growth_rate: 10
      compute_profile: 10
      stack_fit: 9
      concurrency_cost: 9
    notes: "n"
composite_score: 8.031
disqualifiers_checked:
  auth_bypass: false
  rate_limit_violations: false
  tos_robots_violations: false
  unautomatable_human_labor: false
  ddos_grade_load: false
monetization_hypotheses:
  - "Quarterly snapshot."
graduated_to: null
---

Body text goes here.
```

- [ ] **Step 2: Write the three zero-axis fixtures**

```bash
cd /home/runner/moat-research/tests/fixtures && \
  cp brief_valid_scored.md brief_zero_financial.md && \
  cp brief_valid_scored.md brief_zero_implementation.md && \
  cp brief_valid_scored.md brief_zero_hardware.md
```

Then edit each:

In `brief_zero_financial.md`, change `feasibility_scores.financial.composite: 6.5` to `0.0` and `composite_score: 8.031` to `0.0`.

In `brief_zero_implementation.md`, change `feasibility_scores.implementation.composite: 9.0` to `0.0` and `composite_score: 8.031` to `0.0`.

In `brief_zero_hardware.md`, change `feasibility_scores.hardware.composite: 9.5` to `0.0` and `composite_score: 8.031` to `0.0`.

- [ ] **Step 3: Write fixture `brief_candidate_unscored.md`**

```markdown
---
id: brief_2026_05_04_unscored_example
title: Unscored candidate
lane: 2
status: candidate
created: 2026-05-04
last_scored: null
last_reviewed: null
source_signals: []
description: |
  Discovered, not yet scored.
proposed_capture:
  what: "TBD"
  retention: "TBD"
  derived_artifacts: []
estimated_resources:
  storage_gb_per_month: null
  cpu_cores: null
  ram_gb: null
  gpu: null
  request_rate_per_min: null
  concurrent_services: null
feasibility_scores: null
composite_score: null
disqualifiers_checked: {}
monetization_hypotheses: []
graduated_to: null
---

Free-form notes.
```

- [ ] **Step 4: Write fixture `brief_approved.md`**

```bash
cd /home/runner/moat-research/tests/fixtures && cp brief_valid_scored.md brief_approved.md
```

Then edit `brief_approved.md` to change `status: scored` → `status: approved`.

- [ ] **Step 5: Append failing tests**

```python
# tests/unit/test_brief.py — append below TestFilename

from pathlib import Path

FIXTURES = Path(__file__).parent.parent / "fixtures"


class TestParse:
    def test_parse_scored_brief(self):
        b = brief.parse_brief(FIXTURES / "brief_valid_scored.md")
        assert b.id == "brief_2026_05_04_fcc_eas_alerts"
        assert b.lane == 1
        assert b.secondary_lanes == [3]
        assert b.status == "scored"
        assert b.composite_score == pytest.approx(8.031, abs=0.005)
        assert b.feasibility_scores["financial"]["composite"] == 6.5
        assert b.body.strip() == "Body text goes here."

    def test_parse_unscored_candidate(self):
        b = brief.parse_brief(FIXTURES / "brief_candidate_unscored.md")
        assert b.status == "candidate"
        assert b.composite_score is None
        assert b.feasibility_scores is None

    def test_any_axis_zero_detected(self):
        b = brief.parse_brief(FIXTURES / "brief_zero_financial.md")
        assert brief.failed_axis(b) == "financial"
        b2 = brief.parse_brief(FIXTURES / "brief_zero_implementation.md")
        assert brief.failed_axis(b2) == "implementation"
        b3 = brief.parse_brief(FIXTURES / "brief_zero_hardware.md")
        assert brief.failed_axis(b3) == "hardware"

    def test_no_failed_axis_for_valid_brief(self):
        b = brief.parse_brief(FIXTURES / "brief_valid_scored.md")
        assert brief.failed_axis(b) is None

    def test_no_failed_axis_for_unscored(self):
        b = brief.parse_brief(FIXTURES / "brief_candidate_unscored.md")
        assert brief.failed_axis(b) is None


class TestSerialize:
    def test_round_trip(self, tmp_path):
        b = brief.parse_brief(FIXTURES / "brief_valid_scored.md")
        out = tmp_path / "out.md"
        brief.write_brief(b, out)
        b2 = brief.parse_brief(out)
        assert b2.id == b.id
        assert b2.composite_score == pytest.approx(b.composite_score)
        assert b2.body.strip() == b.body.strip()

    def test_lane_validation(self, tmp_path):
        b = brief.parse_brief(FIXTURES / "brief_valid_scored.md")
        b.lane = 99  # out of range
        with pytest.raises(ValueError, match="lane"):
            brief.write_brief(b, tmp_path / "x.md")

    def test_status_validation(self, tmp_path):
        b = brief.parse_brief(FIXTURES / "brief_valid_scored.md")
        b.status = "wat"
        with pytest.raises(ValueError, match="status"):
            brief.write_brief(b, tmp_path / "x.md")
```

- [ ] **Step 6: Run to verify they fail**

```bash
cd /home/runner/moat-research && uv run pytest tests/unit/test_brief.py::TestParse tests/unit/test_brief.py::TestSerialize -v
```

Expected: AttributeError on `brief.parse_brief`.

- [ ] **Step 7: Append implementation**

```python
# workers/common/brief.py — append below filename helpers

from dataclasses import dataclass, field, asdict
from pathlib import Path
import yaml

LANE_VALUES = {1, 2, 3, 4, 5}
STATUS_VALUES = {"candidate", "scored", "rejected", "approved", "graduated"}


@dataclass
class Brief:
    id: str
    title: str
    lane: int
    status: str
    created: str
    source_signals: list
    description: str
    proposed_capture: dict
    estimated_resources: dict
    disqualifiers_checked: dict
    monetization_hypotheses: list
    last_scored: str | None = None
    last_reviewed: str | None = None
    secondary_lanes: list = field(default_factory=list)
    feasibility_scores: dict | None = None
    composite_score: float | None = None
    graduated_to: str | None = None
    body: str = ""


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def parse_brief(path: Path) -> Brief:
    """Parse a brief markdown file with YAML frontmatter into a Brief dataclass."""
    text = Path(path).read_text(encoding="utf-8")
    m = _FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"no YAML frontmatter found in {path}")
    fm = yaml.safe_load(m.group(1)) or {}
    body = m.group(2)
    # Construct, allowing missing optional fields
    fm["body"] = body
    return Brief(**fm)


def write_brief(b: Brief, path: Path) -> None:
    """Serialize a Brief back to disk as YAML frontmatter + body."""
    if b.lane not in LANE_VALUES:
        raise ValueError(f"lane must be one of {sorted(LANE_VALUES)}, got {b.lane}")
    if b.status not in STATUS_VALUES:
        raise ValueError(f"status must be one of {sorted(STATUS_VALUES)}, got {b.status}")
    data = asdict(b)
    body = data.pop("body", "") or ""
    fm = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    Path(path).write_text(f"---\n{fm}---\n{body}", encoding="utf-8")


def failed_axis(b: Brief) -> str | None:
    """
    Return the name of the failed axis ('financial' | 'implementation' | 'hardware')
    if any axis composite is 0, else None. Returns None for unscored briefs.
    """
    fs = b.feasibility_scores
    if not fs:
        return None
    for axis in ("financial", "implementation", "hardware"):
        sub = fs.get(axis) or {}
        if sub.get("composite", None) == 0 or sub.get("composite", None) == 0.0:
            return axis
    return None
```

- [ ] **Step 8: Run to verify they pass**

```bash
cd /home/runner/moat-research && uv run pytest tests/unit/test_brief.py -v
```

Expected: all tests pass.

- [ ] **Step 9: Commit**

```bash
cd /home/runner/moat-research && git add tests/unit/test_brief.py tests/fixtures/brief_*.md workers/common/brief.py && git commit -m "feat(brief): frontmatter parse/serialize and failed_axis detector"
```

---

## Task 8: Build the promoter worker (TDD)

**Files:**
- Create: `tests/unit/test_promoter.py`
- Create: `workers/promoter/promoter.py`

The promoter watches `briefs/scored/`. On each pass, for any brief with an axis = 0, it moves the file to `briefs/rejected/` with the rejected-axis filename and appends `rejection_reason` to the frontmatter. It runs as a 60s sweep loop in production; the function under test takes one repo root and runs one sweep.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_promoter.py
import shutil
from pathlib import Path
import pytest
from workers.promoter import promoter
from workers.common import brief as brief_lib

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def repo(tmp_path):
    """Build a temp repo with briefs/{scored,rejected,_quarantine} dirs."""
    for sub in ("scored", "rejected", "_quarantine"):
        (tmp_path / "briefs" / sub).mkdir(parents=True)
    return tmp_path


def _place(repo, fixture_name, target_subdir, target_filename):
    src = FIXTURES / fixture_name
    dst = repo / "briefs" / target_subdir / target_filename
    shutil.copy(src, dst)
    return dst


class TestPromoter:
    def test_valid_brief_stays_in_scored(self, repo):
        _place(repo, "brief_valid_scored.md", "scored", "08.031-20260504-fcc.md")
        moved = promoter.sweep(repo)
        assert moved == []
        assert (repo / "briefs" / "scored" / "08.031-20260504-fcc.md").exists()
        assert list((repo / "briefs" / "rejected").iterdir()) == []

    def test_zero_financial_moves_to_rejected(self, repo):
        _place(repo, "brief_zero_financial.md", "scored", "00.000-20260504-bad.md")
        moved = promoter.sweep(repo)
        assert len(moved) == 1
        # Rejected filename uses the failed axis
        rejected = list((repo / "briefs" / "rejected").iterdir())
        assert len(rejected) == 1
        assert rejected[0].name == "00.000-financial-20260504-bad.md"
        # The original is gone
        assert not (repo / "briefs" / "scored" / "00.000-20260504-bad.md").exists()
        # Frontmatter has rejection_reason
        b = brief_lib.parse_brief(rejected[0])
        # rejection_reason was injected as a body suffix or frontmatter field
        # We accept either; here we check the parsed brief or the raw text
        raw = rejected[0].read_text()
        assert "rejection_reason" in raw
        assert "financial" in raw

    def test_zero_implementation_moves_to_rejected(self, repo):
        _place(repo, "brief_zero_implementation.md", "scored", "00.000-20260504-bad.md")
        promoter.sweep(repo)
        rejected = list((repo / "briefs" / "rejected").iterdir())
        assert rejected[0].name == "00.000-implementation-20260504-bad.md"

    def test_zero_hardware_moves_to_rejected(self, repo):
        _place(repo, "brief_zero_hardware.md", "scored", "00.000-20260504-bad.md")
        promoter.sweep(repo)
        rejected = list((repo / "briefs" / "rejected").iterdir())
        assert rejected[0].name == "00.000-hardware-20260504-bad.md"

    def test_malformed_brief_quarantined(self, repo):
        bad = repo / "briefs" / "scored" / "08.000-20260504-malformed.md"
        bad.write_text("no frontmatter here, just text")
        promoter.sweep(repo)
        # Quarantined, not crashed
        assert not bad.exists()
        quarantined = list((repo / "briefs" / "_quarantine").iterdir())
        assert len(quarantined) == 1
        assert quarantined[0].name == "08.000-20260504-malformed.md"

    def test_idempotent(self, repo):
        _place(repo, "brief_valid_scored.md", "scored", "08.031-20260504-fcc.md")
        promoter.sweep(repo)
        promoter.sweep(repo)
        assert (repo / "briefs" / "scored" / "08.031-20260504-fcc.md").exists()
```

- [ ] **Step 2: Run to verify it fails**

```bash
cd /home/runner/moat-research && uv run pytest tests/unit/test_promoter.py -v
```

Expected: ImportError on `workers.promoter`.

- [ ] **Step 3: Write the implementation**

```python
# workers/promoter/promoter.py
"""
Promoter worker: scans briefs/scored/, moves any brief with an axis=0 to briefs/rejected/.

Stateless; runs as a 60s sweep loop in production. The unit-tested function is sweep().
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

from workers.common import brief as brief_lib


def sweep(repo_root: Path) -> list[Path]:
    """
    One pass over briefs/scored/. Returns the list of files moved to rejected/.
    Malformed files are moved to briefs/_quarantine/ instead of crashing.
    """
    repo_root = Path(repo_root)
    scored_dir = repo_root / "briefs" / "scored"
    rejected_dir = repo_root / "briefs" / "rejected"
    quarantine_dir = repo_root / "briefs" / "_quarantine"
    quarantine_dir.mkdir(exist_ok=True)

    moved: list[Path] = []
    for path in sorted(scored_dir.glob("*.md")):
        try:
            b = brief_lib.parse_brief(path)
        except Exception as exc:
            dst = quarantine_dir / path.name
            path.rename(dst)
            print(f"[promoter] quarantined {path.name}: {exc}", file=sys.stderr)
            continue

        axis = brief_lib.failed_axis(b)
        if axis is None:
            continue

        # Build new filename: 00.000-<axis>-<date>-<slug>.md
        # Reuse the date+slug from the original filename if possible.
        original = path.name
        # Strip score prefix (first 7 chars + dash)
        if "-" in original:
            tail = original.split("-", 1)[1]  # everything after first dash
        else:
            tail = original
        new_name = f"00.000-{axis}-{tail}"
        dst = rejected_dir / new_name

        # Inject rejection_reason into frontmatter via Brief object
        b.status = "rejected"
        # Write to the new location, then delete the old
        # We append a trailing comment-style line in the body to keep parsing simple
        b.body = (b.body or "") + f"\n\n<!-- rejection_reason: axis={axis} composite=0 (auto) -->\n"
        # Also expose rejection_reason via composite_score=0 invariant; add to disqualifiers note
        # Re-write
        brief_lib.write_brief(b, dst)
        # Append rejection_reason as a frontmatter field by re-reading raw + re-writing
        raw = dst.read_text()
        raw = raw.replace("---\n", f"---\nrejection_reason: \"axis={axis}\"\n", 1)
        dst.write_text(raw)
        path.unlink()
        moved.append(dst)
        print(f"[promoter] rejected {original} -> {new_name} (axis={axis})")

    return moved


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    interval = 60
    while True:
        try:
            sweep(repo)
        except Exception as exc:
            print(f"[promoter] sweep failed: {exc}", file=sys.stderr)
        time.sleep(interval)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run to verify it passes**

```bash
cd /home/runner/moat-research && uv run pytest tests/unit/test_promoter.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/runner/moat-research && git add tests/unit/test_promoter.py workers/promoter/promoter.py && git commit -m "feat(promoter): scored→rejected on any-axis-zero with quarantine on parse fail"
```

---

## Task 9: Build the indexer worker (TDD)

**Files:**
- Create: `tests/unit/test_indexer.py`
- Create: `workers/indexer/indexer.py`

The indexer regenerates `briefs/index.json` containing the frontmatter of every brief across all five lifecycle dirs. JSON is the chosen format per spec §7.2.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_indexer.py
import json
import shutil
from pathlib import Path
import pytest
from workers.indexer import indexer

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def repo(tmp_path):
    for sub in ("candidates", "scored", "rejected", "approved", "graduated"):
        (tmp_path / "briefs" / sub).mkdir(parents=True)
    return tmp_path


class TestIndexer:
    def test_empty_repo_writes_empty_index(self, repo):
        indexer.rebuild(repo)
        out = json.loads((repo / "briefs" / "index.json").read_text())
        assert out == {"briefs": []}

    def test_single_brief_indexed(self, repo):
        shutil.copy(FIXTURES / "brief_valid_scored.md", repo / "briefs" / "scored" / "08.031-20260504-fcc.md")
        indexer.rebuild(repo)
        out = json.loads((repo / "briefs" / "index.json").read_text())
        assert len(out["briefs"]) == 1
        entry = out["briefs"][0]
        assert entry["id"] == "brief_2026_05_04_fcc_eas_alerts"
        assert entry["lifecycle_dir"] == "scored"
        assert entry["filename"] == "08.031-20260504-fcc.md"
        assert entry["composite_score"] == pytest.approx(8.031)

    def test_briefs_from_all_dirs(self, repo):
        shutil.copy(FIXTURES / "brief_valid_scored.md", repo / "briefs" / "scored" / "08.031-20260504-a.md")
        shutil.copy(FIXTURES / "brief_candidate_unscored.md", repo / "briefs" / "candidates" / "--.----20260504-b.md")
        shutil.copy(FIXTURES / "brief_approved.md", repo / "briefs" / "approved" / "08.031-20260504-c.md")
        indexer.rebuild(repo)
        out = json.loads((repo / "briefs" / "index.json").read_text())
        dirs = {b["lifecycle_dir"] for b in out["briefs"]}
        assert dirs == {"scored", "candidates", "approved"}

    def test_sorted_by_score_descending(self, repo):
        # Two scored briefs with different scores
        for score, slug in [(8.031, "fcc"), (5.500, "lower"), (9.200, "higher")]:
            dst = repo / "briefs" / "scored" / f"{score:06.3f}-20260504-{slug}.md"
            shutil.copy(FIXTURES / "brief_valid_scored.md", dst)
            # Patch composite_score in the file so the index reflects it
            text = dst.read_text().replace("composite_score: 8.031", f"composite_score: {score}")
            dst.write_text(text)
        indexer.rebuild(repo)
        out = json.loads((repo / "briefs" / "index.json").read_text())
        scores = [b["composite_score"] for b in out["briefs"]]
        assert scores == sorted(scores, reverse=True)

    def test_malformed_brief_skipped_not_crash(self, repo):
        (repo / "briefs" / "scored" / "08.000-bad.md").write_text("garbage")
        shutil.copy(FIXTURES / "brief_valid_scored.md", repo / "briefs" / "scored" / "08.031-20260504-fcc.md")
        indexer.rebuild(repo)
        out = json.loads((repo / "briefs" / "index.json").read_text())
        # Only the valid one is indexed
        assert len(out["briefs"]) == 1
        assert out["briefs"][0]["id"] == "brief_2026_05_04_fcc_eas_alerts"
```

- [ ] **Step 2: Run to verify it fails**

```bash
cd /home/runner/moat-research && uv run pytest tests/unit/test_indexer.py -v
```

Expected: ImportError on `workers.indexer`.

- [ ] **Step 3: Write the implementation**

```python
# workers/indexer/indexer.py
"""
Indexer worker: regenerates briefs/index.json from all briefs across lifecycle dirs.

Stateless; runs as a 60s sweep loop in production. The unit-tested function is rebuild().
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from dataclasses import asdict

from workers.common import brief as brief_lib

LIFECYCLE_DIRS = ("candidates", "scored", "rejected", "approved", "graduated")


def rebuild(repo_root: Path) -> None:
    """Walk all lifecycle dirs, parse every brief, write briefs/index.json."""
    repo_root = Path(repo_root)
    entries = []
    for sub in LIFECYCLE_DIRS:
        d = repo_root / "briefs" / sub
        if not d.exists():
            continue
        for path in sorted(d.glob("*.md")):
            try:
                b = brief_lib.parse_brief(path)
            except Exception as exc:
                print(f"[indexer] skipping {path}: {exc}", file=sys.stderr)
                continue
            entry = asdict(b)
            entry.pop("body", None)  # keep index small
            entry["lifecycle_dir"] = sub
            entry["filename"] = path.name
            entries.append(entry)
    # Sort by composite_score desc, treating None as -inf
    entries.sort(key=lambda e: (e.get("composite_score") if e.get("composite_score") is not None else float("-inf")), reverse=True)
    out_path = repo_root / "briefs" / "index.json"
    out_path.write_text(json.dumps({"briefs": entries}, indent=2, default=str), encoding="utf-8")


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    interval = 60
    while True:
        try:
            rebuild(repo)
        except Exception as exc:
            print(f"[indexer] rebuild failed: {exc}", file=sys.stderr)
        time.sleep(interval)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run to verify it passes**

```bash
cd /home/runner/moat-research && uv run pytest tests/unit/test_indexer.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/runner/moat-research && git add tests/unit/test_indexer.py workers/indexer/indexer.py && git commit -m "feat(indexer): regenerate briefs/index.json sorted by composite score"
```

---

## Task 10: Build the init-prompt generator + template (TDD)

**Files:**
- Create: `workers/init_prompt_gen/template.md`
- Create: `tests/unit/test_init_prompt_gen.py`
- Create: `workers/init_prompt_gen/init_prompt_gen.py`

For each brief in `briefs/approved/`, the generator renders a sibling `<id>.init-prompt.md` from a template. Idempotent (re-rendering produces the same output unless the brief changed).

- [ ] **Step 1: Write `template.md`** (Jinja-style placeholders, but rendered with stdlib `string.Template` for zero deps beyond pyyaml)

```markdown
# Project init prompt: $title

> Generated by moat-research init-prompt-gen for brief `$id`. Edit before using.

## Mission

$description

## Suggested project name

$slug (rename freely)

## Capture scope

- **What:** $capture_what
- **Retention:** $capture_retention
- **Derived artifacts:** $capture_derived_artifacts
- **Source signals:**
$source_signals_block

## Operational envelope

You will deploy on a single Fedora 42 host with 250 GB RAM, 56 cores (Xeon E5-2695 v3 ×2), an NVIDIA Tesla P4 GPU shared with other services, and 17 TB of free space on a Synology BTRFS SHR1 NAS. The preferred operational pattern is a single-node Docker swarm with isolated microservices, one stack-yml per project. Ingest must be polite: respect robots.txt, ToS, and published rate limits. No auth-bypass. The orchestrator throttles the swarm in aggregate, not just per-service.

## Stack-design questions for init

Answer these interactively when initializing the project; the answers will determine the stack:

1. What ingest cadence does this source require? Is it pull (polling) or push (webhook/stream)?
2. Is the raw payload best stored as JSONL append-log, parquet, blob (mp4/png/gz), or something else?
3. Does any service need GPU (P4 is shared — confirm fit before committing)?
4. Does this need a dedicated database (Postgres? SQLite? Parquet store?) or can it append to a shared store?
5. What's the per-service concurrency cap that respects the rate budget below?

## Resource budget (initial estimate)

- **Storage growth:** $resource_storage_gb_per_month GB/month
- **CPU cores:** $resource_cpu_cores
- **RAM:** $resource_ram_gb GB
- **GPU required:** $resource_gpu
- **External request rate:** $resource_request_rate_per_min /min
- **Concurrent services:** $resource_concurrent_services

## Success criteria for iteration 1

(Operator: fill these in during init. Suggested defaults below.)

- [ ] Ingest service running in Docker, capturing into NAS-mounted volume.
- [ ] At least 24 hours of data captured without errors.
- [ ] Storage rate within $resource_storage_gb_per_month GB/month estimate ±25%.
- [ ] No 429 / 403 / robots-disallow events in the logs.

## Out-of-scope guardrails for iteration 1

- No derived artifacts yet — capture first, derive later.
- No web UI or external API — local files only.
- No alerting / dashboards — stdout logs only.

## Disqualifier re-check

Verify each is still false before proceeding:

- [ ] Auth-bypass / CFAA-adjacent? (must remain `false`)
- [ ] ToS / robots / rate-limit violations? (must remain `false`)
- [ ] Un-automatable human labor? (must remain `false`)
- [ ] DDOS-grade load against any source? (must remain `false`)

## Provenance

- Brief: `briefs/approved/$filename`
- Lane: $lane
- Composite score: $composite_score
- Last reviewed: $last_reviewed
```

- [ ] **Step 2: Write the failing test**

```python
# tests/unit/test_init_prompt_gen.py
import shutil
from pathlib import Path
import pytest
from workers.init_prompt_gen import init_prompt_gen

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "briefs" / "approved").mkdir(parents=True)
    return tmp_path


class TestInitPromptGen:
    def test_renders_for_approved_brief(self, repo):
        src = FIXTURES / "brief_approved.md"
        dst = repo / "briefs" / "approved" / "08.031-20260504-fcc.md"
        shutil.copy(src, dst)
        init_prompt_gen.sweep(repo)
        artifact = repo / "briefs" / "approved" / "brief_2026_05_04_fcc_eas_alerts.init-prompt.md"
        assert artifact.exists()
        text = artifact.read_text()
        assert "FCC EAS alert metadata archive" in text
        assert "Composite score: 8.031" in text
        assert "Lane: 1" in text

    def test_idempotent(self, repo):
        shutil.copy(FIXTURES / "brief_approved.md", repo / "briefs" / "approved" / "08.031-20260504-fcc.md")
        init_prompt_gen.sweep(repo)
        artifact = repo / "briefs" / "approved" / "brief_2026_05_04_fcc_eas_alerts.init-prompt.md"
        first = artifact.read_text()
        init_prompt_gen.sweep(repo)
        second = artifact.read_text()
        assert first == second

    def test_skips_non_approved_status(self, repo):
        # An approved-dir file with status: scored should be skipped (sanity guard)
        shutil.copy(FIXTURES / "brief_valid_scored.md", repo / "briefs" / "approved" / "08.031-20260504-fcc.md")
        init_prompt_gen.sweep(repo)
        artifact = repo / "briefs" / "approved" / "brief_2026_05_04_fcc_eas_alerts.init-prompt.md"
        assert not artifact.exists()

    def test_ignores_existing_init_prompt_files(self, repo):
        shutil.copy(FIXTURES / "brief_approved.md", repo / "briefs" / "approved" / "08.031-20260504-fcc.md")
        # Pre-existing artifact with the suffix should not be re-parsed as a brief
        init_prompt_gen.sweep(repo)
        # Run again — should not crash trying to parse the artifact as a brief
        init_prompt_gen.sweep(repo)
```

- [ ] **Step 3: Run to verify it fails**

```bash
cd /home/runner/moat-research && uv run pytest tests/unit/test_init_prompt_gen.py -v
```

Expected: ImportError.

- [ ] **Step 4: Write the implementation**

```python
# workers/init_prompt_gen/init_prompt_gen.py
"""
For each brief in briefs/approved/, render a sibling <id>.init-prompt.md from template.md.

Stateless; runs as a 60s sweep loop in production. Idempotent.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from string import Template

from workers.common import brief as brief_lib

TEMPLATE_PATH = Path(__file__).parent / "template.md"
INIT_PROMPT_SUFFIX = ".init-prompt.md"


def _format_signals(signals: list) -> str:
    if not signals:
        return "  (none recorded)"
    lines = []
    for s in signals:
        url = s.get("url", "?")
        note = s.get("note", "")
        lines.append(f"  - {url} — {note}")
    return "\n".join(lines)


def render(b: brief_lib.Brief, filename: str) -> str:
    """Render the init-prompt for a single Brief."""
    tmpl = Template(TEMPLATE_PATH.read_text(encoding="utf-8"))
    pc = b.proposed_capture or {}
    er = b.estimated_resources or {}
    return tmpl.safe_substitute(
        title=b.title,
        id=b.id,
        slug=b.id.replace("brief_", "").replace("_", "-"),
        description=(b.description or "").strip(),
        capture_what=pc.get("what", ""),
        capture_retention=pc.get("retention", ""),
        capture_derived_artifacts=", ".join(pc.get("derived_artifacts") or []),
        source_signals_block=_format_signals(b.source_signals or []),
        resource_storage_gb_per_month=er.get("storage_gb_per_month", "?"),
        resource_cpu_cores=er.get("cpu_cores", "?"),
        resource_ram_gb=er.get("ram_gb", "?"),
        resource_gpu=er.get("gpu", "?"),
        resource_request_rate_per_min=er.get("request_rate_per_min", "?"),
        resource_concurrent_services=er.get("concurrent_services", "?"),
        filename=filename,
        lane=b.lane,
        composite_score=f"{b.composite_score:.3f}" if b.composite_score is not None else "?",
        last_reviewed=b.last_reviewed or "?",
    )


def sweep(repo_root: Path) -> list[Path]:
    """One pass over briefs/approved/. Returns list of artifacts written/updated."""
    repo_root = Path(repo_root)
    approved_dir = repo_root / "briefs" / "approved"
    written: list[Path] = []
    for path in sorted(approved_dir.glob("*.md")):
        if path.name.endswith(INIT_PROMPT_SUFFIX):
            continue  # Skip our own artifacts
        try:
            b = brief_lib.parse_brief(path)
        except Exception as exc:
            print(f"[init-prompt-gen] skipping {path.name}: {exc}", file=sys.stderr)
            continue
        if b.status != "approved":
            print(f"[init-prompt-gen] skipping {path.name}: status={b.status}", file=sys.stderr)
            continue
        artifact = approved_dir / f"{b.id}{INIT_PROMPT_SUFFIX}"
        new_content = render(b, path.name)
        if artifact.exists() and artifact.read_text() == new_content:
            continue  # Idempotent
        artifact.write_text(new_content, encoding="utf-8")
        written.append(artifact)
    return written


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    interval = 60
    while True:
        try:
            sweep(repo)
        except Exception as exc:
            print(f"[init-prompt-gen] sweep failed: {exc}", file=sys.stderr)
        time.sleep(interval)


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run to verify it passes**

```bash
cd /home/runner/moat-research && uv run pytest tests/unit/test_init_prompt_gen.py -v
```

Expected: 4 passed.

- [ ] **Step 6: Commit**

```bash
cd /home/runner/moat-research && git add workers/init_prompt_gen/template.md workers/init_prompt_gen/init_prompt_gen.py tests/unit/test_init_prompt_gen.py && git commit -m "feat(init-prompt-gen): render approved briefs to init-prompt artifacts"
```

---

## Task 11: Build the swarm coordinator (token-bucket throttle, TDD)

**Files:**
- Create: `tests/unit/test_coordinator.py`
- Create: `workers/coordinator/coordinator.py`

The coordinator is a tiny HTTP service that issues fetch tokens. Ingestors call `GET /token?source_id=<id>` before every external request and only proceed if the response is 200. This is the structural defense against the DDOS disqualifier. Per-source rate budgets come from `signals/sources.yml`.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_coordinator.py
import time
import pytest
from workers.coordinator import coordinator


class TestTokenBucket:
    def test_first_request_succeeds(self):
        tb = coordinator.TokenBucket(rate_per_min=60, capacity=10)
        assert tb.consume() is True

    def test_capacity_limit(self):
        tb = coordinator.TokenBucket(rate_per_min=60, capacity=5)
        # Drain the bucket
        for _ in range(5):
            assert tb.consume() is True
        # Sixth must fail
        assert tb.consume() is False

    def test_refill_over_time(self, monkeypatch):
        clock = [1000.0]
        monkeypatch.setattr(coordinator.time, "monotonic", lambda: clock[0])
        tb = coordinator.TokenBucket(rate_per_min=60, capacity=2)
        assert tb.consume() is True
        assert tb.consume() is True
        assert tb.consume() is False
        # Advance 2 seconds — at 60/min = 1/sec we should have 2 tokens
        clock[0] += 2.0
        assert tb.consume() is True
        assert tb.consume() is True
        assert tb.consume() is False


class TestRegistry:
    def test_unknown_source_denied(self):
        reg = coordinator.SourceRegistry({})
        assert reg.consume("nope") is False

    def test_per_source_buckets_independent(self):
        reg = coordinator.SourceRegistry({
            "a": {"rate_per_min": 60, "capacity": 1},
            "b": {"rate_per_min": 60, "capacity": 1},
        })
        assert reg.consume("a") is True
        # Source a is now empty, but b is independent
        assert reg.consume("a") is False
        assert reg.consume("b") is True

    def test_load_from_sources_yml(self, tmp_path):
        sources_file = tmp_path / "sources.yml"
        sources_file.write_text("""
sources:
  - id: foo
    rate_budget_per_min: 30
    enabled: true
  - id: bar
    rate_budget_per_min: 6
    enabled: false
""")
        reg = coordinator.SourceRegistry.from_yaml(sources_file)
        assert reg.consume("foo") is True
        # bar is disabled → not registered
        assert reg.consume("bar") is False
```

- [ ] **Step 2: Run to verify it fails**

```bash
cd /home/runner/moat-research && uv run pytest tests/unit/test_coordinator.py -v
```

Expected: ImportError.

- [ ] **Step 3: Write the implementation**

```python
# workers/coordinator/coordinator.py
"""
Swarm-aggregate token-bucket throttle. Ingestors call GET /token?source_id=<id>
before each external request. The coordinator owns the per-source rate budget,
so the swarm can never exceed it in aggregate (per spec §9.1).
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs, urlparse

import yaml

DEFAULT_CAPACITY_FACTOR = 2  # capacity = factor * tokens-per-second, min 1


@dataclass
class TokenBucket:
    rate_per_min: float
    capacity: int

    def __post_init__(self):
        self._tokens = float(self.capacity)
        self._last = time.monotonic()
        self._lock = Lock()

    def consume(self, n: float = 1.0) -> bool:
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last
            refill = elapsed * (self.rate_per_min / 60.0)
            self._tokens = min(float(self.capacity), self._tokens + refill)
            self._last = now
            if self._tokens >= n:
                self._tokens -= n
                return True
            return False


class SourceRegistry:
    def __init__(self, configs: dict):
        self._buckets: dict[str, TokenBucket] = {}
        for sid, cfg in configs.items():
            rate = float(cfg["rate_per_min"])
            cap = int(cfg.get("capacity") or max(1, int(rate / 60 * DEFAULT_CAPACITY_FACTOR)))
            self._buckets[sid] = TokenBucket(rate_per_min=rate, capacity=cap)

    @classmethod
    def from_yaml(cls, path: Path) -> "SourceRegistry":
        data = yaml.safe_load(Path(path).read_text()) or {}
        configs = {}
        for entry in (data.get("sources") or []):
            if not entry.get("enabled", False):
                continue
            sid = entry["id"]
            rate = float(entry.get("rate_budget_per_min", 1.0))
            configs[sid] = {"rate_per_min": rate}
        return cls(configs)

    def consume(self, source_id: str) -> bool:
        bucket = self._buckets.get(source_id)
        if bucket is None:
            return False
        return bucket.consume()


def make_handler(registry: SourceRegistry):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path != "/token":
                self.send_error(404)
                return
            qs = parse_qs(parsed.query)
            source_id = (qs.get("source_id") or [""])[0]
            if not source_id:
                self.send_error(400, "missing source_id")
                return
            ok = registry.consume(source_id)
            self.send_response(200 if ok else 429)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": ok, "source_id": source_id}).encode())

        def log_message(self, fmt, *args):
            pass  # Quiet
    return Handler


def main() -> None:
    sources_yml = Path("/app/signals/sources.yml")
    registry = SourceRegistry.from_yaml(sources_yml) if sources_yml.exists() else SourceRegistry({})
    server = HTTPServer(("0.0.0.0", 8080), make_handler(registry))
    print("[coordinator] listening on :8080")
    server.serve_forever()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run to verify it passes**

```bash
cd /home/runner/moat-research && uv run pytest tests/unit/test_coordinator.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/runner/moat-research && git add tests/unit/test_coordinator.py workers/coordinator/coordinator.py && git commit -m "feat(coordinator): swarm-aggregate token-bucket throttle service"
```

---

## Task 12: Build the ingestor base class + contract test (TDD)

**Files:**
- Create: `tests/unit/test_ingest_base.py`
- Create: `workers/ingest/base.py`
- Create: `workers/common/throttle.py`

The base class encapsulates the politeness contract: every ingestor must respect robots.txt at startup, call the coordinator before each fetch, honor `Retry-After`, and emit a daily digest. The contract test verifies any subclass implements the required methods.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_ingest_base.py
from pathlib import Path
import pytest
from workers.ingest import base
from workers.common import throttle


class TestThrottleClient:
    def test_consume_calls_coordinator(self, monkeypatch):
        calls = []

        def fake_get(url, timeout):
            calls.append(url)
            class R:
                status_code = 200
                def json(self): return {"ok": True}
            return R()

        monkeypatch.setattr(throttle, "_http_get", fake_get)
        c = throttle.ThrottleClient("http://coord:8080")
        assert c.consume("foo") is True
        assert "source_id=foo" in calls[0]

    def test_consume_returns_false_on_429(self, monkeypatch):
        def fake_get(url, timeout):
            class R:
                status_code = 429
                def json(self): return {"ok": False}
            return R()
        monkeypatch.setattr(throttle, "_http_get", fake_get)
        c = throttle.ThrottleClient("http://coord:8080")
        assert c.consume("foo") is False


class _ConcreteIngestor(base.BaseIngestor):
    SOURCE_ID = "concrete_test"

    def fetch_one(self):
        return b"payload"

    def write(self, payload):
        return Path(self.storage_path) / "out.txt"


class TestBaseIngestor:
    def test_subclass_must_set_source_id(self):
        class Bad(base.BaseIngestor):
            def fetch_one(self): return b""
            def write(self, p): return Path("/tmp/x")
        with pytest.raises(ValueError, match="SOURCE_ID"):
            Bad(storage_path="/tmp", coordinator_url="http://x", rate_budget_per_min=1)

    def test_subclass_must_implement_fetch_one(self):
        class Bad(base.BaseIngestor):
            SOURCE_ID = "x"
            def write(self, p): return Path("/tmp/x")
        with pytest.raises(TypeError):
            Bad(storage_path="/tmp", coordinator_url="http://x", rate_budget_per_min=1)

    def test_concrete_instantiates(self, tmp_path):
        ing = _ConcreteIngestor(
            storage_path=str(tmp_path),
            coordinator_url="http://coord:8080",
            rate_budget_per_min=1,
        )
        assert ing.SOURCE_ID == "concrete_test"
        assert ing.healthcheck() is True

    def test_robots_check_called_at_startup(self, tmp_path, monkeypatch):
        called = []
        monkeypatch.setattr(base, "_robots_allows", lambda url, ua: called.append(url) or True)
        ing = _ConcreteIngestor(
            storage_path=str(tmp_path),
            coordinator_url="http://coord:8080",
            rate_budget_per_min=1,
            robots_check_url="https://example.com/somepath",
        )
        ing.startup()
        assert called and "example.com" in called[0]

    def test_robots_disallow_refuses_to_start(self, tmp_path, monkeypatch):
        monkeypatch.setattr(base, "_robots_allows", lambda url, ua: False)
        ing = _ConcreteIngestor(
            storage_path=str(tmp_path),
            coordinator_url="http://coord:8080",
            rate_budget_per_min=1,
            robots_check_url="https://example.com/x",
        )
        with pytest.raises(RuntimeError, match="robots"):
            ing.startup()
```

- [ ] **Step 2: Run to verify they fail**

```bash
cd /home/runner/moat-research && uv run pytest tests/unit/test_ingest_base.py -v
```

Expected: ImportError.

- [ ] **Step 3: Write `workers/common/throttle.py`**

```python
# workers/common/throttle.py
"""
Client for the swarm coordinator. Ingestors must call ThrottleClient.consume(source_id)
before every external request and only proceed on True.
"""
from __future__ import annotations

import json
from urllib.request import urlopen
from urllib.error import HTTPError, URLError


class _Resp:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self._body = body

    def json(self):
        return json.loads(self._body)


def _http_get(url: str, timeout: float):
    """Stdlib HTTP GET; returns object with .status_code and .json()."""
    try:
        with urlopen(url, timeout=timeout) as r:
            return _Resp(r.status, r.read().decode())
    except HTTPError as e:
        return _Resp(e.code, e.read().decode() if e.fp else "{}")
    except URLError:
        return _Resp(599, "{}")


class ThrottleClient:
    def __init__(self, coordinator_url: str, timeout: float = 2.0):
        self.coordinator_url = coordinator_url.rstrip("/")
        self.timeout = timeout

    def consume(self, source_id: str) -> bool:
        url = f"{self.coordinator_url}/token?source_id={source_id}"
        r = _http_get(url, timeout=self.timeout)
        return r.status_code == 200
```

- [ ] **Step 4: Write `workers/ingest/base.py`**

```python
# workers/ingest/base.py
"""
Abstract base class for signal ingestors. Subclasses implement fetch_one() and write();
the base class provides the politeness contract (robots check at startup, coordinator
gating before each fetch, exponential backoff on 429/503, healthcheck, daily digest).
"""
from __future__ import annotations

import sys
import time
from abc import ABC, abstractmethod
from pathlib import Path
from urllib import robotparser
from urllib.parse import urlparse

from workers.common.throttle import ThrottleClient

DEFAULT_USER_AGENT = "moat-research-ingest/0.1 (+https://github.com/local/moat-research)"


def _robots_allows(url: str, user_agent: str) -> bool:
    """Check robots.txt for the URL's host. True = allowed (or robots.txt missing)."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        return True  # Missing robots.txt = no restriction
    return rp.can_fetch(user_agent, url)


class BaseIngestor(ABC):
    SOURCE_ID: str = ""  # Subclasses must set

    def __init__(
        self,
        *,
        storage_path: str,
        coordinator_url: str,
        rate_budget_per_min: float,
        robots_check_url: str | None = None,
        user_agent: str = DEFAULT_USER_AGENT,
        cadence_seconds: int = 60,
    ):
        if not self.SOURCE_ID:
            raise ValueError("Subclass must set SOURCE_ID")
        self.storage_path = storage_path
        self.coordinator = ThrottleClient(coordinator_url)
        self.rate_budget_per_min = rate_budget_per_min
        self.robots_check_url = robots_check_url
        self.user_agent = user_agent
        self.cadence_seconds = cadence_seconds
        Path(storage_path).mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def fetch_one(self) -> bytes:
        """Single fetch from upstream. Must NOT call coordinator — base class handles that."""

    @abstractmethod
    def write(self, payload: bytes) -> Path:
        """Persist payload; return the path written."""

    def healthcheck(self) -> bool:
        return Path(self.storage_path).exists()

    def startup(self) -> None:
        if self.robots_check_url:
            if not _robots_allows(self.robots_check_url, self.user_agent):
                raise RuntimeError(
                    f"robots.txt disallows {self.robots_check_url} for {self.user_agent}; refusing to start"
                )

    def run_forever(self) -> None:
        self.startup()
        backoff = 1.0
        while True:
            try:
                if not self.coordinator.consume(self.SOURCE_ID):
                    time.sleep(min(backoff, 30))
                    backoff = min(backoff * 2, 30)
                    continue
                backoff = 1.0
                payload = self.fetch_one()
                self.write(payload)
            except Exception as exc:
                print(f"[{self.SOURCE_ID}] error: {exc}", file=sys.stderr)
                time.sleep(min(backoff, 60))
                backoff = min(backoff * 2, 60)
                continue
            time.sleep(self.cadence_seconds)
```

- [ ] **Step 5: Run to verify they pass**

```bash
cd /home/runner/moat-research && uv run pytest tests/unit/test_ingest_base.py tests/unit/test_brief.py tests/unit/test_promoter.py tests/unit/test_indexer.py tests/unit/test_init_prompt_gen.py tests/unit/test_coordinator.py -v
```

Expected: all passing.

- [ ] **Step 6: Commit**

```bash
cd /home/runner/moat-research && git add tests/unit/test_ingest_base.py workers/ingest/base.py workers/common/throttle.py && git commit -m "feat(ingest): BaseIngestor with robots/coordinator/backoff contract"
```

---

## Task 13: Build the politeness lint script (TDD)

**Files:**
- Create: `tests/fixtures/sources_clean.yml`
- Create: `tests/fixtures/sources_missing_rate_budget.yml`
- Create: `tests/unit/test_politeness_lint.py`
- Create: `scripts/politeness_lint.py`

The lint scans `signals/sources.yml` and fails CI if any entry skips the politeness checklist (declared rate budget, identifiable URL, parser declared). Per spec §13.

- [ ] **Step 1: Write fixtures**

`tests/fixtures/sources_clean.yml`:

```yaml
sources:
  - id: example_feed
    url: https://example.gov/feed
    cadence: 60s
    rate_budget_per_min: 1
    storage_path: /signals/raw/example_feed
    parser: jsonl
    enabled: true
```

`tests/fixtures/sources_missing_rate_budget.yml`:

```yaml
sources:
  - id: example_feed
    url: https://example.gov/feed
    cadence: 60s
    storage_path: /signals/raw/example_feed
    parser: jsonl
    enabled: true
```

- [ ] **Step 2: Write the failing test**

```python
# tests/unit/test_politeness_lint.py
from pathlib import Path
import pytest
import sys

sys.path.insert(0, str(Path(__file__).parents[2] / "scripts"))
import politeness_lint as pl

FIXTURES = Path(__file__).parent.parent / "fixtures"


class TestPolitenessLint:
    def test_clean_passes(self):
        violations = pl.lint(FIXTURES / "sources_clean.yml")
        assert violations == []

    def test_missing_rate_budget_violates(self):
        violations = pl.lint(FIXTURES / "sources_missing_rate_budget.yml")
        assert len(violations) == 1
        assert "rate_budget_per_min" in violations[0]
        assert "example_feed" in violations[0]

    def test_missing_url_violates(self, tmp_path):
        bad = tmp_path / "sources.yml"
        bad.write_text("sources:\n  - id: x\n    rate_budget_per_min: 1\n    parser: jsonl\n    cadence: 60s\n    storage_path: /x\n    enabled: true\n")
        violations = pl.lint(bad)
        assert any("url" in v for v in violations)

    def test_zero_or_negative_rate_violates(self, tmp_path):
        bad = tmp_path / "sources.yml"
        bad.write_text("sources:\n  - id: x\n    url: https://x\n    rate_budget_per_min: 0\n    parser: jsonl\n    cadence: 60s\n    storage_path: /x\n    enabled: true\n")
        violations = pl.lint(bad)
        assert any("rate_budget_per_min" in v and ">0" in v for v in violations)

    def test_missing_parser_violates(self, tmp_path):
        bad = tmp_path / "sources.yml"
        bad.write_text("sources:\n  - id: x\n    url: https://x\n    rate_budget_per_min: 1\n    cadence: 60s\n    storage_path: /x\n    enabled: true\n")
        violations = pl.lint(bad)
        assert any("parser" in v for v in violations)

    def test_empty_sources_passes(self, tmp_path):
        bad = tmp_path / "sources.yml"
        bad.write_text("sources: []\n")
        assert pl.lint(bad) == []

    def test_main_exits_nonzero_on_violations(self, tmp_path, capsys):
        bad = tmp_path / "sources.yml"
        bad.write_text("sources:\n  - id: x\n    parser: jsonl\n    cadence: 60s\n    storage_path: /x\n    enabled: true\n")
        rc = pl.main([str(bad)])
        captured = capsys.readouterr()
        assert rc != 0
        assert "VIOLATION" in captured.out or "VIOLATION" in captured.err

    def test_main_exits_zero_on_clean(self, capsys):
        rc = pl.main([str(FIXTURES / "sources_clean.yml")])
        assert rc == 0
```

- [ ] **Step 3: Run to verify it fails**

```bash
cd /home/runner/moat-research && uv run pytest tests/unit/test_politeness_lint.py -v
```

Expected: ImportError on `politeness_lint`.

- [ ] **Step 4: Write the implementation**

```python
# scripts/politeness_lint.py
"""
Lint signals/sources.yml against the politeness checklist (spec §13).

Exit code 0 if clean, 1 if any violation. Designed to run in pre-commit / CI.

Usage: python scripts/politeness_lint.py signals/sources.yml
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REQUIRED_FIELDS = ("id", "url", "cadence", "rate_budget_per_min", "storage_path", "parser", "enabled")


def lint(path: Path) -> list[str]:
    """Return a list of human-readable violation strings; empty list = clean."""
    data = yaml.safe_load(Path(path).read_text()) or {}
    sources = data.get("sources") or []
    violations: list[str] = []
    for i, entry in enumerate(sources):
        sid = entry.get("id", f"<index {i}>")
        for field in REQUIRED_FIELDS:
            if field not in entry:
                violations.append(f"source '{sid}' is missing required field '{field}'")
        if "rate_budget_per_min" in entry and entry["rate_budget_per_min"] is not None:
            try:
                rate = float(entry["rate_budget_per_min"])
                if rate <= 0:
                    violations.append(f"source '{sid}' has rate_budget_per_min={rate}; must be >0")
            except (TypeError, ValueError):
                violations.append(f"source '{sid}' has non-numeric rate_budget_per_min")
    return violations


def main(argv: list[str]) -> int:
    if len(argv) < 1:
        print("usage: politeness_lint.py <sources.yml>", file=sys.stderr)
        return 2
    path = Path(argv[0])
    if not path.exists():
        print(f"file not found: {path}", file=sys.stderr)
        return 2
    violations = lint(path)
    if not violations:
        print(f"OK: {path} clean ({len(yaml.safe_load(path.read_text()).get('sources') or [])} source(s) checked)")
        return 0
    for v in violations:
        print(f"VIOLATION: {v}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 5: Run to verify it passes**

```bash
cd /home/runner/moat-research && uv run pytest tests/unit/test_politeness_lint.py -v
```

Expected: 8 passed.

- [ ] **Step 6: Commit**

```bash
cd /home/runner/moat-research && git add tests/fixtures/sources_clean.yml tests/fixtures/sources_missing_rate_budget.yml tests/unit/test_politeness_lint.py scripts/politeness_lint.py && git commit -m "feat(scripts): politeness_lint for signals/sources.yml"
```

---

## Task 14: End-to-end lifecycle integration test (TDD)

**Files:**
- Create: `tests/integration/test_lifecycle.py`

Walks a sample brief through both lifecycle paths against a temp repo, exercising promoter + indexer + init-prompt-gen together.

- [ ] **Step 1: Write the test**

```python
# tests/integration/test_lifecycle.py
import json
import shutil
from pathlib import Path
import pytest
from workers.promoter import promoter
from workers.indexer import indexer
from workers.init_prompt_gen import init_prompt_gen

FIXTURES = Path(__file__).parent.parent / "fixtures"

pytestmark = pytest.mark.integration


@pytest.fixture
def repo(tmp_path):
    for sub in ("candidates", "scored", "rejected", "approved", "graduated"):
        (tmp_path / "briefs" / sub).mkdir(parents=True)
    return tmp_path


def test_scored_to_rejected_path(repo):
    """Brief with axis=0 lands in scored/, promoter moves it to rejected/, indexer reflects."""
    shutil.copy(FIXTURES / "brief_zero_financial.md", repo / "briefs" / "scored" / "00.000-20260504-bad.md")
    promoter.sweep(repo)
    indexer.rebuild(repo)

    rejected = list((repo / "briefs" / "rejected").iterdir())
    assert len(rejected) == 1
    assert rejected[0].name == "00.000-financial-20260504-bad.md"

    idx = json.loads((repo / "briefs" / "index.json").read_text())
    assert len(idx["briefs"]) == 1
    assert idx["briefs"][0]["lifecycle_dir"] == "rejected"


def test_scored_to_approved_to_init_prompt_path(repo):
    """Brief in scored/ stays put on first promoter pass; operator moves to approved/; init-prompt is rendered."""
    src = repo / "briefs" / "scored" / "08.031-20260504-fcc.md"
    shutil.copy(FIXTURES / "brief_valid_scored.md", src)

    # Promoter: no-op (no zeros)
    promoter.sweep(repo)
    assert src.exists()

    # Operator promotion: edit status to approved + move
    text = src.read_text().replace("status: scored", "status: approved")
    src.write_text(text)
    dst = repo / "briefs" / "approved" / "08.031-20260504-fcc.md"
    src.rename(dst)

    # Init-prompt-gen renders
    init_prompt_gen.sweep(repo)
    artifact = repo / "briefs" / "approved" / "brief_2026_05_04_fcc_eas_alerts.init-prompt.md"
    assert artifact.exists()
    text = artifact.read_text()
    assert "Operational envelope" in text
    assert "FCC EAS alert metadata archive" in text

    # Indexer sees the approved brief
    indexer.rebuild(repo)
    idx = json.loads((repo / "briefs" / "index.json").read_text())
    # Index includes the brief; the .init-prompt.md sibling is NOT indexed (suffix filter)
    brief_entries = [b for b in idx["briefs"] if b["id"] == "brief_2026_05_04_fcc_eas_alerts"]
    assert len(brief_entries) == 1
    assert brief_entries[0]["lifecycle_dir"] == "approved"


def test_promoter_indexer_init_prompt_gen_idempotent(repo):
    shutil.copy(FIXTURES / "brief_valid_scored.md", repo / "briefs" / "scored" / "08.031-20260504-fcc.md")
    shutil.copy(FIXTURES / "brief_zero_hardware.md", repo / "briefs" / "scored" / "00.000-20260504-bad.md")
    shutil.copy(FIXTURES / "brief_approved.md", repo / "briefs" / "approved" / "08.031-20260504-app.md")

    for _ in range(3):
        promoter.sweep(repo)
        indexer.rebuild(repo)
        init_prompt_gen.sweep(repo)

    assert (repo / "briefs" / "rejected" / "00.000-hardware-20260504-bad.md").exists()
    assert (repo / "briefs" / "scored" / "08.031-20260504-fcc.md").exists()
    assert (repo / "briefs" / "approved" / "brief_2026_05_04_fcc_eas_alerts.init-prompt.md").exists()
```

> **Note on the indexer filter:** `briefs/approved/<id>.init-prompt.md` files end with `.init-prompt.md`, which the indexer currently does not filter. The next step adds that filter.

- [ ] **Step 2: Run to verify what fails**

```bash
cd /home/runner/moat-research && uv run pytest tests/integration/test_lifecycle.py -v
```

Expected: `test_scored_to_approved_to_init_prompt_path` fails because the indexer tries to parse the `.init-prompt.md` artifact as a brief and either errors or includes it.

- [ ] **Step 3: Patch the indexer to skip init-prompt artifacts**

In `workers/indexer/indexer.py`, change the inner loop:

```python
        for path in sorted(d.glob("*.md")):
            if path.name.endswith(".init-prompt.md"):
                continue  # Generated artifact, not a brief
            try:
                b = brief_lib.parse_brief(path)
```

- [ ] **Step 4: Re-run integration tests**

```bash
cd /home/runner/moat-research && uv run pytest tests/integration/test_lifecycle.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Re-run full suite to confirm no regressions**

```bash
cd /home/runner/moat-research && uv run pytest -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
cd /home/runner/moat-research && git add tests/integration/test_lifecycle.py workers/indexer/indexer.py && git commit -m "test(integration): full lifecycle paths; indexer skips init-prompt artifacts"
```

---

## Task 15: Dockerize the workers

**Files:**
- Create: `workers/promoter/Dockerfile`
- Create: `workers/indexer/Dockerfile`
- Create: `workers/init_prompt_gen/Dockerfile`
- Create: `workers/coordinator/Dockerfile`
- Create: `workers/ingest/Dockerfile.base`

All workers share a tiny base image — Python 3.11 slim with pyyaml. Each Dockerfile is identical except for the entrypoint module.

- [ ] **Step 1: Write `workers/promoter/Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir pyyaml==6.0.2
COPY workers/common /app/workers/common
COPY workers/promoter /app/workers/promoter
COPY briefs /app/briefs
ENV PYTHONPATH=/app
CMD ["python", "-m", "workers.promoter.promoter"]
```

- [ ] **Step 2: Write `workers/indexer/Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir pyyaml==6.0.2
COPY workers/common /app/workers/common
COPY workers/indexer /app/workers/indexer
COPY briefs /app/briefs
ENV PYTHONPATH=/app
CMD ["python", "-m", "workers.indexer.indexer"]
```

- [ ] **Step 3: Write `workers/init_prompt_gen/Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir pyyaml==6.0.2
COPY workers/common /app/workers/common
COPY workers/init_prompt_gen /app/workers/init_prompt_gen
COPY briefs /app/briefs
ENV PYTHONPATH=/app
CMD ["python", "-m", "workers.init_prompt_gen.init_prompt_gen"]
```

- [ ] **Step 4: Write `workers/coordinator/Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir pyyaml==6.0.2
COPY workers/common /app/workers/common
COPY workers/coordinator /app/workers/coordinator
ENV PYTHONPATH=/app
EXPOSE 8080
CMD ["python", "-m", "workers.coordinator.coordinator"]
```

- [ ] **Step 5: Write `workers/ingest/Dockerfile.base`**

```dockerfile
# Base image for ingestor services. Concrete ingestors FROM this and add their
# own module + CMD.
FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir pyyaml==6.0.2
COPY workers/common /app/workers/common
COPY workers/ingest /app/workers/ingest
ENV PYTHONPATH=/app
```

- [ ] **Step 6: Verify each builds**

```bash
cd /home/runner/moat-research && \
  docker build -f workers/promoter/Dockerfile -t moat/promoter:dev . && \
  docker build -f workers/indexer/Dockerfile -t moat/indexer:dev . && \
  docker build -f workers/init_prompt_gen/Dockerfile -t moat/init-prompt-gen:dev . && \
  docker build -f workers/coordinator/Dockerfile -t moat/coordinator:dev . && \
  docker build -f workers/ingest/Dockerfile.base -t moat/ingest-base:dev .
```

Expected: five `Successfully tagged moat/...:dev` lines, no errors.

- [ ] **Step 7: Smoke-test one image**

```bash
docker run --rm -v /home/runner/moat-research/briefs:/app/briefs moat/indexer:dev python -c "from workers.indexer import indexer; from pathlib import Path; indexer.rebuild(Path('/app')); print('OK')"
```

Expected: `OK` and `briefs/index.json` exists/updates.

- [ ] **Step 8: Commit**

```bash
cd /home/runner/moat-research && git add workers/*/Dockerfile workers/ingest/Dockerfile.base && git commit -m "build: Dockerfiles for promoter, indexer, init-prompt-gen, coordinator, ingest base"
```

---

## Task 16: Write the docker swarm stack file

**Files:**
- Create: `stacks/moat-research.yml`

Mirrors the somd-cameras pattern: one stack per project, services with explicit resource limits and labels, NAS volumes mounted for raw signal storage.

- [ ] **Step 1: Write `stacks/moat-research.yml`**

```yaml
# Single-node Docker swarm stack for moat-research workers.
# Deploy with: docker stack deploy -c stacks/moat-research.yml moat-research

version: "3.8"

x-common-labels: &common_labels
  project: moat-research
  managed-by: docker-swarm

services:
  coordinator:
    image: moat/coordinator:dev
    networks: [moat]
    volumes:
      - type: bind
        source: ../signals/sources.yml
        target: /app/signals/sources.yml
        read_only: true
    deploy:
      replicas: 1
      resources:
        limits:
          cpus: "0.5"
          memory: 128M
      labels:
        <<: *common_labels
        service: coordinator
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8080/token?source_id=__healthcheck__', timeout=2)"]
      interval: 30s
      timeout: 5s
      retries: 3

  promoter:
    image: moat/promoter:dev
    networks: [moat]
    volumes:
      - type: bind
        source: ../briefs
        target: /app/briefs
    deploy:
      replicas: 1
      resources:
        limits:
          cpus: "0.25"
          memory: 128M
      labels:
        <<: *common_labels
        service: promoter

  indexer:
    image: moat/indexer:dev
    networks: [moat]
    volumes:
      - type: bind
        source: ../briefs
        target: /app/briefs
    deploy:
      replicas: 1
      resources:
        limits:
          cpus: "0.25"
          memory: 128M
      labels:
        <<: *common_labels
        service: indexer

  init-prompt-gen:
    image: moat/init-prompt-gen:dev
    networks: [moat]
    volumes:
      - type: bind
        source: ../briefs
        target: /app/briefs
    deploy:
      replicas: 1
      resources:
        limits:
          cpus: "0.25"
          memory: 128M
      labels:
        <<: *common_labels
        service: init-prompt-gen

networks:
  moat:
    driver: overlay
    attachable: true
```

> Concrete ingestor services are added to this stack as they are created (one per source, FROM `moat/ingest-base:dev`). None exist on day one.

- [ ] **Step 2: Validate the stack file syntax**

```bash
cd /home/runner/moat-research && docker stack config -c stacks/moat-research.yml >/dev/null && echo "OK"
```

Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
cd /home/runner/moat-research && git add stacks/moat-research.yml && git commit -m "build: docker swarm stack for coordinator + workers"
```

---

## Task 17: Pre-commit config and full smoke test

**Files:**
- Create: `.pre-commit-config.yaml`

Wires the politeness lint and pytest into the commit gate.

- [ ] **Step 1: Write `.pre-commit-config.yaml`**

```yaml
repos:
  - repo: local
    hooks:
      - id: politeness-lint
        name: politeness lint (signals/sources.yml)
        entry: uv run python scripts/politeness_lint.py signals/sources.yml
        language: system
        files: ^signals/sources\.yml$
        pass_filenames: false

      - id: pytest-unit
        name: pytest unit tests
        entry: uv run pytest tests/unit -q
        language: system
        files: ^(workers/|scripts/|tests/)
        pass_filenames: false
```

- [ ] **Step 2: Install pre-commit hooks**

```bash
cd /home/runner/moat-research && uv add --dev pre-commit && uv run pre-commit install
```

Expected: `pre-commit installed at .git/hooks/pre-commit`.

- [ ] **Step 3: Run the politeness lint manually against the empty registry**

```bash
cd /home/runner/moat-research && uv run python scripts/politeness_lint.py signals/sources.yml
```

Expected: `OK: signals/sources.yml clean (0 source(s) checked)`.

- [ ] **Step 4: Run the full test suite**

```bash
cd /home/runner/moat-research && uv run pytest -v
```

Expected: all tests pass (unit + integration).

- [ ] **Step 5: Smoke-test the deployed stack (manual, optional)**

This step requires a running Docker swarm. Skip if not available.

```bash
docker swarm init 2>/dev/null || true
cd /home/runner/moat-research && docker stack deploy -c stacks/moat-research.yml moat-research
sleep 10
docker stack services moat-research
docker service logs moat-research_coordinator --tail 20
docker stack rm moat-research
```

Expected: 4 services REPLICAS 1/1; coordinator log shows `listening on :8080`.

- [ ] **Step 6: Commit**

```bash
cd /home/runner/moat-research && git add .pre-commit-config.yaml pyproject.toml uv.lock && git commit -m "chore: pre-commit hooks for politeness lint + unit tests"
```

---

## Self-review (filled in)

**Spec coverage:** Each spec section maps to at least one task —

| Spec section | Implementing task(s) |
|---|---|
| §3 Hard constraints | Task 2 (CONSTRAINTS.md), Task 13 (politeness lint), Task 12 (BaseIngestor robots check + coordinator gate) |
| §4 Lanes | Task 2 (LANES.md), Task 7 (lane validation in write_brief) |
| §5 Rubric | Task 2 (RUBRIC.md), Task 5 (composite_score) |
| §6 Lifecycle | Task 3 (dirs), Task 8 (promoter), Task 14 (integration) |
| §7.1 Brief schema | Task 7 (parse/serialize/fixtures) |
| §7.2 Generated index | Task 9 (indexer) |
| §7.3 WISHLIST.md | Already exists at repo root; spec-conformant |
| §7.4 Init-prompt artifact | Task 10 (template + generator) |
| §8 Repo layout | Tasks 1, 2, 3 |
| §9.1 Ingestors | Task 12 (BaseIngestor); concrete ingestors are out-of-scope (operator adds per source) |
| §9.2 Promoter | Task 8 |
| §9.3 Indexer | Task 9 |
| §9.4 Init-prompt-gen | Task 10 |
| §9.5 Synthesis | Out-of-scope for this plan (executed by maximizer iterations against the corpus) |
| §9.6 Concept-to-maximizer surfaces | Task 4 (orchestrator system-prompt), Task 2 (CLAUDE.md) |
| §10 Data flow | Verified by Task 14 integration tests |
| §11 Error handling & isolation | Tasks 8, 9, 10 (quarantine / skip-on-parse-fail), Task 12 (backoff), Task 16 (resource limits in stack) |
| §12 Seeding | Operator action after bootstrap (FOCUS Items 1, 2, 3); Task 4 covers the orchestrator-side seed |
| §13 Testing | Tasks 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 |
| §14 Open questions | Intentionally deferred per spec |

**Placeholder scan:** No "TBD/TODO/implement later" patterns. Every code step contains the actual code. Every command step contains the actual command and expected output.

**Type consistency:** Brief dataclass field names (`feasibility_scores`, `composite_score`, `disqualifiers_checked`, etc.) are used consistently across `workers/common/brief.py`, the fixtures, the promoter, the indexer, the init-prompt-gen, and the integration tests. `SOURCE_ID` is the BaseIngestor class attribute everywhere. `ThrottleClient.consume(source_id)` is the only coordinator-call signature used.

**Out-of-scope-by-design** (called out explicitly so executors don't try to implement them):

- Concrete ingestor services per source. The base class exists; the first concrete ingestors are operator-driven (one per real source as it's registered in `signals/sources.yml`).
- Synthesis logic (idea generation, scoring, init-prompt content). All performed by maximizer; no code in this repo.
- The somd-cameras rescore (FOCUS Item 1). Executed during the first maximizer iteration after bootstrap.
- Wishlist seeding (FOCUS Item 3). Operator-curated content, not code.
- A web UI / dashboard. Not in spec.
