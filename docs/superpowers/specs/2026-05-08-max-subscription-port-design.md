# Max-Subscription Port — Design

**Date:** 2026-05-08
**Status:** Draft for review
**Scope:** Port `mr` from the metered Anthropic API to the Claude Max subscription via the Claude Agent SDK.

## Motivation

The current `mr` codebase requires `ANTHROPIC_API_KEY` and calls `anthropic.messages.create()` directly. Claude Max plans do not include API credits — they cover Claude Code / Claude.ai usage only. The user is on Max-only and wants a clean rewrite of the synth layer to ride that subscription via the Claude Agent SDK.

## Decisions (locked)

1. **Backend strategy:** Max-only. Replace fully. Drop the Anthropic SDK from the codebase; no dual-mode shim.
2. **Cost tracking:** Rip out entirely. Max is flat-rate; per-call cost data is meaningless.
3. **Loop guardrails:** Keep wallclock + tool-turn caps as a slim `mr/synth/limits.py`.
4. **Loop ownership:** Approach B (Agent-SDK-idiomatic). Delete the hand-rolled `while True:` loops; let the SDK own the conversation; observe only the final assistant text.
5. **Custom-tool transport:** In-process MCP server (closure-captured `seen_path`).
6. **`code_execution`:** Load-bearing per `prompts/discover.md:74` ("every brief MUST emit a `code_execution` evidence row"). Replace with a custom `code_eval` MCP tool — subprocess Python with `RLIMIT_AS`/`RLIMIT_CPU` caps.
7. **Web tools:** Substitute Claude Code's `WebSearch`/`WebFetch` for Anthropic's native `web_search_20260209`/`web_fetch_20260209`. Acceptable accuracy trade-off for this project's use case.

## Architecture

```
mr discover (typer, sync)
   └─ asyncio.run(_async_discover(...))
        └─ session.run(system_prompt, user_prompt, mcp_server, allowed_tools, max_turns, model, wallclock_seconds)
             └─ asyncio.wait_for(                 ← wallclock cap
                  claude_agent_sdk.query(...)     ← SDK owns turn loop; max_turns enforces turn cap
                      ↕ MCP stdio (in-process)
                  mcp_server (5 @tool funcs:
                    seen_lookup, wayback, robots, head, code_eval)
                )
             returns final assistant text
        parse ```yaml-brief blocks → write Briefs to candidates/
```

**Async boundary:** typer commands stay sync. Each one wraps the async entry with `asyncio.run()`. No async leaks beyond the synth layer — `lifecycle/`, `dedup/`, `wishlist/`, etc. stay sync.

**Dependency change:** `pyproject.toml` removes `anthropic`, adds `claude-agent-sdk`. Runtime requires Claude Code installed locally and an active Max subscription.

## Components

### New files

**`mr/synth/session.py`** (~80 lines)

Single async function:

```python
async def run(
    *,
    system_prompt: str,
    user_prompt: str,
    model: str,
    mcp_server,
    allowed_tools: list[str],
    max_turns: int,
    wallclock_seconds: int,
) -> str: ...
```

Constructs `ClaudeAgentOptions(...)` with `permission_mode="bypassPermissions"` (unattended automation), wraps `claude_agent_sdk.query(prompt=user_prompt, options=...)` in `asyncio.wait_for(..., timeout=wallclock_seconds)`, iterates the async result to collect the final assistant text. No conversation persistence between invocations — each command run is a fresh session.

**`mr/synth/mcp_server.py`** (~150 lines, replaces `tools.py` + `dispatch.py`)

Six `@tool`-decorated async functions, exposed via `claude_agent_sdk.create_sdk_mcp_server`:

| Tool | Body |
|------|------|
| `seen_lookup` | Delegates to `mr.tools.seen_lookup.seen_lookup(seen_path, ...)` |
| `wayback` | Delegates to `mr.tools.wayback.wayback_check(...)` |
| `robots` | Delegates to `mr.tools.robots.robots_check(...)` |
| `head` | Delegates to `mr.tools.head.head_check(...)` |
| `code_eval` | `subprocess.run(["python", "-c", code], ...)` with `RLIMIT_AS=256 MB`, `RLIMIT_CPU=30s`, working dir = `tempfile.mkdtemp()`, no `PATH` inheritance. Returns `{stdout, stderr, exit_code}` or `{error: "timeout", ...}` on `TimeoutExpired`. |

The four domain tools delegate to existing implementations under `mr/tools/` and `mr/dedup/seen_lookup.py` — those files are unchanged.

State problem: `seen_lookup` needs `seen_path` (per-invocation). Solution: a factory function `build_server(seen_path: Path) -> MCPServer` whose closures capture `seen_path`. Server is rebuilt per command run.

Per-command tool whitelist (passed as `allowed_tools` to `session.run`):

| Command | MCP tools | Claude Code built-ins |
|---------|-----------|------------------------|
| `discover` | `seen_lookup`, `wayback`, `code_eval` | `WebSearch`, `WebFetch` |
| `score` | `wayback`, `robots`, `head`, `code_eval` | `WebFetch` (no `WebSearch` — preserves §`prevents drift into adjacent opportunities`) |
| `wishlist expand` | `seen_lookup`, `code_eval` | `WebSearch`, `WebFetch` |

`Bash`, `Read`, `Edit`, `Write` and other Claude Code built-ins are **never** in `allowed_tools`.

**`mr/synth/limits.py`** (~40 lines, replaces `budget.py`)

```python
class LimitExceeded(Exception): ...

@dataclass
class RunLimits:
    max_tool_turns: int
    max_wallclock_seconds: int

def cold_corpus_preflight(wishlist_path: Path) -> None: ...
    # Verbatim from budget.py; raises LimitExceeded if WISHLIST < 5 sources or missing.
```

No `BudgetTracker` equivalent class. Enforcement is delegated:
- `max_tool_turns` → SDK `max_turns` option (raises SDK exception when hit)
- `max_wallclock_seconds` → `asyncio.wait_for` timeout (`session.py` translates `asyncio.TimeoutError` → `LimitExceeded`)

### Replaced files (mechanical trim)

**`mr/cli/discover.py`** (~100 lines down from 216)

Drop: `_run_loop`, `_block_to_dict`, all `BudgetTracker` / `append_cost` / `cli.create_message` / `cli.extract_usage` / `cli.compute_cost_usd` references.

Keep: `cold_corpus_preflight` import (now from `mr.synth.limits`), summary-block build, prompt assembly, MCP server construction, single `await session.run(...)`, then `_extract_candidates` + `_write_candidates` (verbatim — they parse the assistant's final text, which is unchanged).

The `discover` typer command body becomes `asyncio.run(_async_discover(...))`. The `--budget` flag is removed.

**`mr/cli/score.py`** — same trim pattern. Drop `BudgetTracker`, `append_cost`, `_block_to_dict`, the explicit `while True:` loop, `worst_case_ceiling` ceiling check. Keep `_score_one`, `_extract_scores`, `_serialize_brief`, `_route_to_rejected`. Replace `run_score_loop` with a `session.run` call. The `--budget` flag is removed.

**`mr/wishlist/expand.py`** — same trim pattern.

**`mr/cli/main.py`** — drop `gain` subcommand registration.

**`mr/util/config.py` + `mr/util/config_schema.json`** — drop `budgets` section; add `limits` section:

```yaml
limits:
  max_tool_turns:
    default: 12
    discover: 20
    score: 8
    wishlist_expand: 10
  max_wallclock_seconds: 600
```

`models.per_command` preserved (passed to SDK as `model` option per command).

**Schema version bump:** `mr/util/config.py` currently asserts `schema_version: 1` only. The port bumps to `schema_version: 2`. Loader behavior:
- v2 config: validate against new schema (with `limits`, no `budgets`).
- v1 config: print a one-line deprecation notice; ignore `budgets`; require user to re-run `mr init --migrate` (new flag) to write a fresh v2 `mr.yaml`. No automatic in-place rewriting.

**`mr/cli/init.py`** — default `mr.yaml` template updated to v2 with the `limits` section. Add `--migrate` flag that overwrites an existing v1 `mr.yaml` after backing it up to `mr.yaml.bak`.

**`pyproject.toml`** — `anthropic` out, `claude-agent-sdk` in. Python `>=3.10` (already required for the SDK).

### Deleted files

- `mr/synth/client.py`
- `mr/synth/dispatch.py`
- `mr/synth/tools.py`
- `mr/synth/pricing.py`
- `mr/synth/budget.py` (superseded by `limits.py`)
- `mr/util/costs.py`
- `mr/cli/gain.py`
- Tests: `tests/synth/test_client.py`, `tests/synth/test_pricing.py`, `tests/synth/test_budget.py`, `tests/synth/test_dispatch.py`, `tests/synth/test_tools.py`, `tests/util/test_costs.py`, `tests/cli/test_gain.py`

## Data flow (mr discover happy path)

**Setup (sync, before SDK):**
1. `discover` typer command loads config, runs `cold_corpus_preflight`, acquires `.lock`, regenerates `seen.jsonl` if stale.
2. Builds three pieces of static text: `system_text` (from `prompts/discover.md`), `wishlist_text` (from `WISHLIST.md`), `seen_summary` (from `build_summary_block(read_seen(...))`).
3. Concatenates all three into a single `system_prompt` string. Order: system_text → "## Current WISHLIST" block → "## Seen Summary" block. Relies on Claude Code's automatic prompt caching.
4. Builds `user_prompt` = the existing lane/n directive ("Generate exactly N candidates in lane X…").
5. Calls `mcp_server.build_server(seen_path=layout.seen_path)`.

**Async hand-off:**
6. `asyncio.run(session.run(system_prompt=..., user_prompt=..., model=cfg.models.per_command["discover"], mcp_server=server, allowed_tools=[...], max_turns=cfg.limits.max_tool_turns["discover"], wallclock_seconds=cfg.limits.max_wallclock_seconds))`

**Inside the SDK (opaque):**
7. The SDK runs the conversation. Each turn: model emits text and/or tool_use; if tool_use, SDK routes to our in-process MCP server (closure-captured `seen_path` lets `seen_lookup` work); tool_result fed back; repeat until model emits final text or `max_turns` hit.

**Async return:**
8. `session.run` collects assistant text from the message stream and returns the concatenated final-turn text as a single string.

**Post-SDK (sync):**
9. `_extract_candidates(final_text)` — unchanged; parses ```yaml-brief fenced blocks.
10. `_write_candidates(...)` — unchanged; writes Briefs to `candidates/`.

`mr score` and `mr wishlist expand` follow the same shape.

## Error handling

| Failure mode | Behavior |
|---|---|
| `LimitExceeded` (preflight, turn cap, wallclock cap) | Caught at typer command, printed as `error: <msg>` to stderr, exit 2. |
| SDK transport errors (network, auth, Claude Code missing, Max not active) | Caught at typer command, printed verbatim, exit 1. We don't wrap — the SDK's own messages are clearer. |
| MCP tool exceptions | Each `@tool` function catches its own internal errors and returns `{"error": "..."}` in the result dict. Model decides how to react. Matches current `dispatch.py` contract. |
| `code_eval` timeout | `subprocess.TimeoutExpired` → returns `{"error": "timeout", "stdout": <partial>, "stderr": <partial>}`. Model retries with smaller scope. |
| Final-text parse failure | `_extract_candidates` returns `[]`; `mr discover` exits 0 with `created 0 candidates`. Intentional — alternative wastes the whole invocation on a single malformed run. |

No retry logic at the session layer. Agent SDK handles transport-level retries internally.

## Testing

**Deletions:** `tests/synth/test_client.py`, `tests/synth/test_pricing.py`, `tests/synth/test_budget.py`, `tests/synth/test_dispatch.py`, `tests/synth/test_tools.py`, `tests/util/test_costs.py`, `tests/cli/test_gain.py`.

**New tests:**

- **`tests/synth/test_session.py`** — mocks `claude_agent_sdk.query` to yield a fixed sequence of messages; asserts `session.run` returns expected concatenated text. Covers: happy path, wallclock timeout → `LimitExceeded`, SDK-raised exception passthrough.
- **`tests/synth/test_mcp_server.py`** — calls each `@tool` function directly as a Python coroutine (no MCP transport). Asserts: `seen_lookup` returns `matches`/`near_matches` structure, `wayback`/`robots`/`head` delegate to existing `mr.tools.*`, `code_eval` succeeds on simple math + handles timeout + handles syntax error.
- **`tests/synth/test_limits.py`** — `RunLimits` config loading, `cold_corpus_preflight` raises on missing/short WISHLIST.

**Modified tests:**

- `tests/integration/test_e2e.py` — replace existing mocked-LLM seam (`SynthClient`) with mocked-`claude_agent_sdk.query` seam.
- `tests/cli/test_discover.py`, `tests/cli/test_score.py` — drop `_anthropic_api_key_missing` cases; preserve dispatch/budget-routing assertions adapted to the new flow.
- `tests/synth/test_prompts.py`, `tests/synth/test_verify.py` — unchanged.
- `tests/cli/test_status.py`, `tests/cli/test_promote.py`, etc. — no changes (don't touch synth path).

**Test fixture pattern for the SDK mock:** add `tests/synth/conftest.py` with a `mock_query(messages: list)` fixture that returns an async generator yielding the given sequence. Reused across `test_session.py` and `test_e2e.py`.

## Migration order

Strict step-by-step to keep tests green at each commit:

1. Add `claude-agent-sdk` to `pyproject.toml` (don't remove `anthropic` yet).
2. Create `mr/synth/mcp_server.py` with the six `@tool` functions; no callsite. Add `tests/synth/test_mcp_server.py`. Green.
3. Create `mr/synth/limits.py`. Add `tests/synth/test_limits.py`. Green.
4. Create `mr/synth/session.py`. Add `tests/synth/test_session.py` with mocked SDK. Green.
5. Update `mr/util/config.py` + `config_schema.json`: add `limits` section, keep `budgets` section temporarily. Update `tests/util/test_config.py`. Green.
6. Rewrite `mr/cli/discover.py` to use `session.run` + new MCP server; update `tests/cli/test_discover.py` and `tests/integration/test_e2e.py`. Green.
7. Rewrite `mr/cli/score.py` and `mr/wishlist/expand.py` similarly. Green.
8. Drop `gain` from `mr/cli/main.py`. Delete `mr/cli/gain.py` + `tests/cli/test_gain.py`. Green.
9. Delete `mr/synth/client.py`, `mr/synth/dispatch.py`, `mr/synth/tools.py`, `mr/synth/pricing.py`, `mr/synth/budget.py`, `mr/util/costs.py` and their tests. Green.
10. Bump `schema_version` to 2 in `config_schema.json`; remove `budgets` from v2 schema. Update `mr/cli/init.py` default template + add `--migrate` flag. Update `tests/cli/test_init.py` and `tests/util/test_config.py`. Green.
11. Remove `anthropic` from `pyproject.toml`. Green.
12. Update `README.md` and `WISHLIST.md` references to API key / metered cost; document Max + Claude Code requirement.

Each step is a clean commit. Step 6 is the highest-risk — it's where actual behavior changes.

## Open verification items (resolved at implementation time, not now)

- Exact name/shape of the SDK's `max_turns` option on `ClaudeAgentOptions` (current docs at the time of plan-writing).
- Whether `claude_agent_sdk.query` exposes a final-message helper or if we collect via async iteration.
- Whether `WebFetch` accepts URL-only input or requires explicit prompt context per call (affects how `score` re-verifies cited URLs).

## Out of scope

- Migrating away from Claude Code as the runtime (e.g., to a third-party Max-via-OAuth proxy).
- Concurrency / parallel runs (single-process, single-session today; preserved).
- Persisting conversation across invocations (deliberately not supported).
- Rate-limit handling beyond what the SDK provides natively.
