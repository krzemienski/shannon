// META
// name: pre-edit-discipline
// event: PreToolUse:Edit|MultiEdit|Write
// consumed_by_skills: (none)
// description: Merged dispatcher: read-before-edit reminder + plan-before-execute warning. Absorbs 2 inherited hooks.

const { runHook } = require('./_lib.js');
const fs = require('fs');
const path = require('path');

const ACTIVE_SCOPE = [/\/src\//, /\/lib\//, /\/app\//, /^src\//, /^lib\//, /^app\//];
const PLAN_FRESH_MS = 60 * 60 * 1000;

function checkReadBeforeEdit(fp) {
  // Advisory — CC tracks Read state internally; emit soft hint when an Edit is about to run.
  if (!fp) return null;
  return `[shannon] read-before-edit: confirm you Read "${fp}" before editing (stale-context risk).`;
}

function findPlansDir() {
  const cwd = process.env.CLAUDE_PROJECT_DIR || process.cwd();
  const cand = path.join(cwd, 'plans');
  try { return fs.existsSync(cand) && fs.statSync(cand).isDirectory() ? cand : null; } catch (_) { return null; }
}

function hasFreshPlan() {
  const plansDir = findPlansDir();
  if (!plansDir) return false;
  const now = Date.now();
  try {
    for (const e of fs.readdirSync(plansDir)) {
      const planMd = path.join(plansDir, e, 'plan.md');
      try {
        if (!fs.existsSync(planMd)) continue;
        if (now - fs.statSync(planMd).mtimeMs < PLAN_FRESH_MS) return true;
      } catch (_) {}
    }
  } catch (_) {}
  return false;
}

function checkPlanBeforeExecute(fp) {
  if (!fp) return null;
  if (!ACTIVE_SCOPE.some(re => re.test(fp))) return null;
  if (hasFreshPlan()) return null;
  return `[shannon] plan-before-execute: editing "${fp}" in code scope but no plans/*/plan.md modified in last hour. Consider /shannon:plan to anchor the change.`;
}

runHook('pre-edit-discipline', (payload) => {
  const tin = (payload && payload.tool_input) || {};
  const fp = tin.file_path || '';  // CC docs: file_path is snake_case
  const msgs = [
    checkReadBeforeEdit(fp),
    checkPlanBeforeExecute(fp),
  ].filter(Boolean);
  if (!msgs.length) return { decision: 'allow', exitCode: 0 };
  return {
    decision: 'allow',
    exitCode: 2,
    stderrPayload: msgs.join('\n') + '\n',
  };
});
