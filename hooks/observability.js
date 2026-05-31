// META
// name: observability
// event: SessionStart + UserPromptSubmit + PostToolUse:* + PostToolUse:TaskCreate|TaskUpdate
// consumed_by_skills: (none)
// description: Merged dispatcher: hooks-fired-log + context-threshold-warn + task-list-tracker + skill-activation-check + session-context-inject. Absorbs 5 inherited hooks; branches by event.

const { runHook } = require('./_lib.js');
const fs = require('fs');
const os = require('os');
const path = require('path');

const LOG_DIR = path.join(os.homedir(), '.claude', 'logs', 'shannon');

function ensureLogDir() {
  try { fs.mkdirSync(LOG_DIR, { recursive: true }); } catch (_) {}
}

function appendHookLog(entry) {
  ensureLogDir();
  try {
    fs.appendFileSync(path.join(LOG_DIR, 'hooks.jsonl'), JSON.stringify(entry) + '\n');
  } catch (_) {}
}

function appendOpenTask(taskId) {
  ensureLogDir();
  try {
    const p = path.join(LOG_DIR, 'open-tasks.txt');
    const existing = fs.existsSync(p) ? fs.readFileSync(p, 'utf8').split('\n').filter(Boolean) : [];
    if (!existing.includes(taskId)) {
      existing.push(taskId);
      fs.writeFileSync(p, existing.join('\n') + '\n');
    }
  } catch (_) {}
}

function removeOpenTask(taskId) {
  try {
    const p = path.join(LOG_DIR, 'open-tasks.txt');
    if (!fs.existsSync(p)) return;
    const lines = fs.readFileSync(p, 'utf8').split('\n').filter(Boolean).filter(l => l !== taskId);
    fs.writeFileSync(p, lines.join('\n') + (lines.length ? '\n' : ''));
  } catch (_) {}
}

const CTX_THRESHOLD = parseInt(process.env.SHANNON_CTX_WARN_BYTES || '', 10) || 200 * 1024;

function findSessionJsonl() {
  const sid = process.env.CLAUDE_SESSION_ID;
  if (!sid) return null;
  const root = path.join(os.homedir(), '.claude', 'projects');
  try {
    if (!fs.existsSync(root)) return null;
    for (const proj of fs.readdirSync(root)) {
      const cand = path.join(root, proj, `${sid}.jsonl`);
      if (fs.existsSync(cand)) return cand;
    }
  } catch (_) {}
  return null;
}

function contextWarning() {
  const j = findSessionJsonl();
  if (!j) return null;
  try {
    const st = fs.statSync(j);
    if (st.size < CTX_THRESHOLD) return null;
    return `[shannon] context-threshold-warn: session JSONL is ${Math.round(st.size/1024)}KB (>${Math.round(CTX_THRESHOLD/1024)}KB). Consider /compact before auto-compact fires.`;
  } catch (_) { return null; }
}

// Minimal skill-activation cache — for v0.1.0, hard-coded most-likely triggers
// (in v1.x this will load from skills/<name>/SKILL.md frontmatter dynamically).
const TRIGGERS = {
  'validate': 'functional-validation',
  'prove it works': 'functional-validation',
  'no mocks': 'no-fakes-discipline',
  'add a fake': 'no-fakes-discipline',
  'marking complete': 'evidence-gate',
  'mark as done': 'evidence-gate',
  'ready to ship': 'completion-gate',
};

function skillHints(prompt) {
  if (!prompt) return null;
  const matches = [];
  for (const [trig, skill] of Object.entries(TRIGGERS)) {
    if (prompt.toLowerCase().includes(trig)) matches.push({ trig, skill });
    if (matches.length >= 5) break;
  }
  if (!matches.length) return null;
  const lines = matches.map(m => `  • Skill: ${m.skill} (trigger: "${m.trig}")`);
  return `<system-reminder>\n[shannon] Skill hints (${matches.length} match):\n${lines.join('\n')}\n</system-reminder>\n`;
}

runHook('observability', (payload) => {
  const event = String(payload && (payload.hook_event_name || payload.event) || '');
  const tool = String(payload && (payload.tool_name || payload.tool) || '');
  const tin = (payload && payload.tool_input) || {};

  // SessionStart: record session boundary
  if (/SessionStart/i.test(event)) {
    appendHookLog({ ts: new Date().toISOString(), event: 'SessionStart', matcher: payload.matcher });
    return { decision: 'allow', exitCode: 0 };
  }

  // UserPromptSubmit: maybe emit skill hint to stdout
  if (/UserPromptSubmit/i.test(event)) {
    const prompt = payload.prompt || payload.user_prompt || payload.text || '';
    appendHookLog({ ts: new Date().toISOString(), event: 'UserPromptSubmit', promptLen: String(prompt).length });
    const hint = skillHints(prompt);
    return { decision: 'allow', exitCode: 0, stdoutPayload: hint || '' };
  }

  // PostToolUse: always log, optionally update task list, optionally warn on ctx
  appendHookLog({ ts: new Date().toISOString(), event: 'PostToolUse', tool });
  if (/^TaskCreate$/.test(tool)) {
    const id = tin.taskId || tin.id || '';
    if (id) appendOpenTask(id);
  } else if (/^TaskUpdate$/.test(tool)) {
    const id = tin.taskId || tin.id || '';
    const status = tin.status || '';
    if (id) {
      if (status === 'completed' || status === 'deleted') removeOpenTask(id);
      else appendOpenTask(id);
    }
  }
  const warn = contextWarning();
  return { decision: 'allow', exitCode: 0, stderrPayload: warn ? warn + '\n' : '' };
});
