# Shannon Benchmarks — skill-activation harness

Ported from the legacy fork (signed decision **G1**, 2026-06-02). Proves the skill-activation gate empirically in **real Claude Code sessions** — Iron-Rule compliant, no mocks. This is the **third** harness alongside the SDK + Tmux pillar harnesses (`scripts/harness/sdk_runner.py`, `tmux_runner.py`); those prove the 5 pillars, this proves the opt-in activation gate. See `docs/SCAFFOLDING_v1.2.md` § "The three harnesses".

## Two harness layers

### Group B — live-fire gate proof (the load-bearing harness)
`scripts/harness/drive-tests.sh` and `scripts/harness/drive-tests-csd.sh`.

Spawns a **real headless `claude -p` session** per fixture (loaded via `--plugin-dir`, no global install) and asserts the opt-in gate by diffing `~/.claude/logs/shannon/hooks.jsonl`:

| Fixture | Sentinel | Expected |
|---|---|---|
| `fixtures/enabled` | `.shannon/active` | hook FIRES → new log row |
| `fixtures/unset` | (none) | gate no-ops → NO new row |
| `fixtures/disabled` | `.shannon/disabled` | gate no-ops → NO new row |

- `drive-tests.sh` — minimal: greps `skill-activation-check` fires from the hook log delta.
- `drive-tests-csd.sh` — richer: drives the session via `claude-session-driver` under tmux, captures `events.jsonl` + `shannon-hooks-delta.jsonl` per fixture.

Run:
```bash
SHANNON_DIR="$(pwd)" scripts/harness/drive-tests.sh
```
`SHANNON_DIR` defaults to the plugin root (`scripts/harness/..`); no hardcoded paths.

### Group A — recall/precision matcher benchmark — RETIRED-WITH-REASON
The legacy `run-activation.js` (in-process recall/precision over a trigger DB) is **NOT ported**. It hard-required `core/layers/invocation/module.js`, a V6 engine **retired in v1 under decision D8** (target `core/` is intentionally empty). Its job — per-skill recall/precision/F1 from real activation — is now done *better* by `scripts/skills10x/eval_skill.py`, which scores against **real `claude -p --debug` probes** instead of a regex matcher. `innocent-corpus.json` (40 false-positive prompts) is retained here as the precision corpus for skills10x.

See `docs/migration-map.md` for the full retired-with-reason ledger.

## Fixtures
`fixtures/{enabled,unset,disabled,minimal,complex}` — real sample project trees + `.shannon` sentinels. Classified 55/55 ALLOWED seed-data under the Iron Rule (no test doubles). Heavy regenerable `.mimirs/index.db` blobs (3.3 MB each) were excluded from the port; the RAG index regenerates on demand.

## Iron rules
- Real sessions only — every assertion reads a real hook log written by a real `claude -p` run.
- No mocks, no synthetic log rows. A zero-delta on `enabled` is a FAIL, not a pass.
