// META
// name: subagent-governance
// event: PreToolUse:Task|Agent
// consumed_by_skills: dispatch-parallel, multi-agent-patterns, team-coordinator
// description: Injects IRON RULE briefing into subagent spawn via stderr before Task tool runs.

const { runHook } = require('./_lib.js');

const IRON_RULE = `[shannon] Subagent IRON RULE:
- No mocks. No stubs. No test files (*.test.*, *.spec.*, tests/, __tests__/, mocks/, fixtures/).
- Real system execution only. Capture evidence to e2e-evidence/<run-id>/<journey>/.
- Refusal is a first-class outcome — write REFUSAL.md instead of fabricated PASS.
- File ownership boundaries from team charter must be respected (cross-glob writes refused).
`;

runHook('subagent-governance', () => ({
  decision: 'allow',
  exitCode: 0,
  stderrPayload: IRON_RULE,
}));
