// META
// name: stop-semantics
// event: Stop
// consumed_by_skills: team-coordinator
// description: Blocks Stop when any in-progress subagent task is still active (prevents abandoning teammates).

const { runHook } = require('./_lib.js');
const fs = require('fs');
const os = require('os');
const path = require('path');

function inProgressTasksExist() {
  // task-list-tracker (now part of observability hook) writes open-tasks.txt
  // to logs/shannon/. If any line is present, treat as in-progress.
  try {
    const p = path.join(os.homedir(), '.claude', 'logs', 'shannon', 'open-tasks.txt');
    if (!fs.existsSync(p)) return false;
    const lines = fs.readFileSync(p, 'utf8').split('\n').filter(Boolean);
    return lines.length > 0;
  } catch (_) {
    return false;
  }
}

runHook('stop-semantics', () => {
  if (!inProgressTasksExist()) return { decision: 'allow', exitCode: 0 };
  return {
    decision: 'allow',
    exitCode: 2,
    stderrPayload: '[shannon] stop-semantics: subagent task(s) still in_progress (see ~/.claude/logs/shannon/open-tasks.txt). Resolve or explicitly cancel before Stop.\n',
  };
});
