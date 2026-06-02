# Migration / Consolidation Map — legacy fork → Shannon v1.2.0

> Rollback ledger for the 2026-06-02 maximal-migration consolidation.
> Source: `/Users/nick/Desktop/shannon-framework/` (4-era V3→V7 archive + nested `v1/shannon/` ancestor).
> Target: this plugin. Evidence: `evidence/legacy-consolidation/forge-fullmig-20260602T005139/`.

## Lineage (read first)

`shannon-framework/v1/shannon/` is the **direct ancestor** of this plugin (identical 20 commands, 9 agents, DECISIONS.md; ancestor = v0.1.4, this = v1.2.0). The fork's **top-level** dirs are *older eras*, not richer functionality. "Migration" therefore = port the genuinely-additive deltas, retire the superseded/dead/forbidden remainder with cause.

## Per-directory disposition

| Legacy top-level dir | Disposition | New location / reason |
|---|---|---|
| `commands/` (28) | PARTIAL PORT | Only `forge.md` was additive → `commands/forge.md` (adapted: `evidence/` paths, oracle→critic+reviewer+validator quorum). plan-deep/tournament/converge already folded into target `plan --mode`. |
| `modules/completion/skills/` | PARTIAL PORT | `documentation-research` + `oracle-review` → `skills/` (forge's 2 missing deps). Rest already present in target (newer). |
| `modes/WAVE_EXECUTION.md` | PORT (adapted) | → `skills/wave-execution/SKILL.md` (Serena dependency replaced with evidence-tree + `.shannon/state/`). Drives `deepplan-architect` agent + `plan --mode deep`. |
| `benchmarks/` (Group B drivers) | PORT | `drive-tests.sh` + `drive-tests-csd.sh` → `scripts/harness/` (hardcoded fork path → `SHANNON_DIR`); `innocent-corpus.json` → `benchmarks/`. |
| `benchmarks/run-activation.js` | RETIRE-WITH-REASON | Hard-required `core/layers/invocation/module.js` (V6 engine retired under D8; target `core/` empty). Superseded by `scripts/skills10x/eval_skill.py` (real probes, not regex). |
| `fixtures/` (55) | PORT | → `fixtures/` (52 files; heavy regenerable `.mimirs/index.db` blobs excluded). Iron-Rule: 55/55 ALLOWED seed-data. |
| `orchestration/*.py` (4) | RETIRE-WITH-REASON | Simulated executor — tasks are `asyncio.sleep(0.01)` fakes, no real dispatch. Real parallel work done by target `dispatch-parallel`/`team`/`wave-execution`. Importing fake-execution violates `no-fakes-discipline`. |
| `dashboard/` (13) + `server/` (2) | DEFER → v0.2.0 | Dead V5.6 React SPA (socket.io never wired, empty-state) + SocketIO server (no launcher/auth/port-bind). Per signed D7, the approval UI is a separate v0.2.0 train — rebuilt real, not migrated dead. |
| `modules/` (V6 prose, 151) | RETIRE-WITH-REASON | Superseded ancestor — target commands/agents/skills are the newer realization. Salvaged: forge spec, consensus-engine prose (already in target). |
| `core/` (V3 prose + V6 layer JS, 24) | RETIRE-WITH-REASON | Target uses 7 markdown-driven JS hooks; V6 `layers/*.js` + V3 prose doctrine superseded. |
| `modes/SHANNON_INTEGRATION.md` | RETIRE-WITH-REASON | SuperClaude-bridge era; not applicable to the standalone v1 plugin. |
| `docs/` (103, 4-era) | REFERENCE-ONLY | Not bulk-copied; consulted for provenance. Target `docs/` (19) + this map + registry are canonical. |
| `templates/SKILL_TEMPLATE.md` (1) | RETIRE | v4 skill schema differs from current `name`+`description`+`triggers`. No consumer. |
| `skills/` (218, top-level era) | RETIRE-WITH-REASON | Older/superset; target's 33 are the curated newer set. No additive skill beyond the 2 forge deps. |
| `hooks/` (28, V6 js + orphaned py) | RETIRE-WITH-REASON | Target's 7 js hooks + `_lib.js` are the newer subset; legacy py hooks were already orphaned (Serena-dep, not in hooks.json). |
| `pytest.ini`, `conftest.py`, `tests/`, `*_test.py`, `run_tests.py` | RETIRE (Iron Rule) | Test files / test doubles — **forbidden** by `block-fab-files` hook. Behavior re-expressed as functional-validation, not ported. |

## Rollback

To revert this consolidation: `git revert` the v1.2.0 consolidation commit. Added files (`commands/forge.md`, `skills/{documentation-research,oracle-review,wave-execution}/`, `agents/deepplan-architect.md`, `scripts/harness/`, `benchmarks/`, `fixtures/`) are net-new — removable without touching the v1.1 surface. The version pin (`1.1.0-dev.4`) and the 4 `plan-author` cross-refs are the only in-place edits.
