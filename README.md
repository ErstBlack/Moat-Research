# moat-research

A solo-operator CLI tool plus structured corpus for discovering, scoring, and graduating **data-moat opportunities** — projects whose structural advantage cannot be overcome by capital and compute alone.

See `docs/superpowers/specs/2026-05-07-moat-research-design.md` for the full design.

## Install

```bash
uv sync
mr init
```

## First-session walkthrough

```bash
mr wishlist expand --seed --budget 0.50    # populate WISHLIST from empty
mr discover --lane ephemeral_public --n 5 --budget 5.0
mr score candidates/*.md --budget 3.0
mr status                                   # see counts
mr promote scored/<top-composite>.md        # accept best brief
mr graduate approved/<top>.md > /tmp/init.txt
mkdir ~/<slug> && cd ~/<slug> && git init
claude < /tmp/init.txt                      # spawn the new project
```

## Subcommands

| Command | LLM? | Purpose |
|---|---|---|
| `mr init` | no | Bootstrap dirs, mr.yaml, prompts/ (idempotent) |
| `mr discover` | yes | Generate candidates from WISHLIST + live web tools |
| `mr score` | yes | Score candidates; route to scored/ or rejected/ |
| `mr promote` | no | Move scored → approved |
| `mr graduate` | no | Emit hand-off prompt; move approved → graduated |
| `mr reject` | no | Move scored → rejected with operator reason |
| `mr wishlist add` | no | Append validated source to WISHLIST.md |
| `mr wishlist expand` | yes | LLM proposes new sources for review |
| `mr wishlist refresh` | no | Re-verify sources (HEAD + robots + Wayback) |
| `mr status` | no | Counts + stale-approved + exploration flags |
| `mr gain` | no | Spend summary from costs.jsonl |

## Configuration

`mr.yaml` controls model selection, weights, budgets, lanes, niche aliases, interest filters, and hardware envelope. Defaults are baked-in; only override what you need to change. Schema is JSON-Schema-validated at load.

## Spec coverage

| Spec section | Implementing tasks |
|---|---|
| §4 Operational envelope (hardware) | T4 (config defaults), T45 (discover prompt) |
| §5 Scoring rubric | T12 (rubric), T13 (auto-reject) |
| §6 Lifecycle | T8 (paths), T9 (filename), T10 (frontmatter), T11 (transitions) |
| §7 CLI commands | T36–T44 |
| §8 Synthesis | T17–T21 (tools), T22–T28 (synth), T45–T47 (prompts) |
| §9 Configuration | T4 |
| §10 State, concurrency, costs | T6 (lock), T7 (costs) |
| §11 WISHLIST | T29–T32, T44 |
| §12 Idea index (dedup) | T14 (niche_key), T15 (seen.jsonl), T16 (summary) |
| §13 Hand-off | T33 (adjacent rejections), T34–T35 (project/feature) |
| §14 Migration / cleanup | T1, T2 |
| §16 Success criteria | T48 (e2e) |

## License

UNLICENSED. Personal-use tool.
