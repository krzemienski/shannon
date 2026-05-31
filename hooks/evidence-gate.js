// META
// name: evidence-gate
// event: PreToolUse:TaskUpdate
// consumed_by_skills: evidence-gate, completion-gate, refusal-discipline
// description: Blocks TaskUpdate(status=completed) without a recent evidence file reference. Soft block (exit 2).

const { runHook } = require('./_lib.js');
const fs = require('fs');
const path = require('path');

function hasRecentEvidence() {
  // Heuristic: look for any file mtime < 30 min in e2e-evidence/, plans/reports/, or reports/.
  const cwd = process.env.CLAUDE_PROJECT_DIR || process.cwd();
  const candidates = [
    path.join(cwd, 'e2e-evidence'),
    path.join(cwd, 'plans', 'reports'),
    path.join(cwd, 'reports'),
  ];
  const cutoff = Date.now() - 30 * 60 * 1000;
  for (const root of candidates) {
    try {
      if (!fs.existsSync(root)) continue;
      const stack = [root];
      while (stack.length) {
        const d = stack.pop();
        for (const ent of fs.readdirSync(d, { withFileTypes: true })) {
          const p = path.join(d, ent.name);
          try {
            const st = fs.statSync(p);
            if (st.isDirectory()) stack.push(p);
            else if (st.mtimeMs > cutoff && st.size > 0) return true;
          } catch (_) {}
        }
      }
    } catch (_) {}
  }
  return false;
}

runHook('evidence-gate', (payload) => {
  const tin = (payload && payload.tool_input) || {};
  const status = String(tin.status || '');
  if (status !== 'completed') return { decision: 'allow', exitCode: 0 };
  if (hasRecentEvidence()) return { decision: 'allow', exitCode: 0 };
  return {
    decision: 'allow',
    exitCode: 2,
    stderrPayload: '[shannon] evidence-gate: about to mark task completed but no fresh evidence file (e2e-evidence/, plans/reports/, reports/) modified in last 30 min. Cite specific evidence before claiming done (refusal-discipline + completion-gate skills).\n',
  };
});
