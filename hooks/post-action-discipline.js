// META
// name: post-action-discipline
// event: PostToolUse:Bash|Edit|Write|MultiEdit
// consumed_by_skills: no-fakes-discipline, evidence-gate, completion-gate, functional-validation
// description: Merged dispatcher: validation-not-compilation + validation-skill-tripwire + completion-claim-validator + fab-pattern-detection + evidence-quality-check. Absorbs 5 inherited hooks; branches by tool name.

const { runHook } = require('./_lib.js');
const fs = require('fs');
const os = require('os');
const path = require('path');

// ---- Build/compilation regex (shared by validation-not-compilation + tripwire) ----
const BUILD_CMDS = /\b(npm run build|pnpm build|yarn build|cargo build|go build|make build|xcodebuild|gradle build|mvn package|tsc)\b/i;
const BUILD_SUCCESS = /(build (succeeded|complete|successful)|compiled successfully|0 errors|✓ built|Build SUCCESSFUL)/i;
const CLAIM = /\b(it works|all done|complete|finished|shipped|ready to ship|ready for review|done!)\b/i;

const FAB_HINTS = [
  /\bjest\.fn\(/i,
  /\bsinon\.stub\b/i,
  /\bvi\.fn\(/i,
  /\bfaker\.(name|address|company)/i,
  /\bMockedFunction\b/,
  /^\s*describe\(\s*['"]/m,
  /^\s*it\(\s*['"]/m,
];

function appendTripwire(entry) {
  try {
    const dir = path.join(os.homedir(), '.claude', 'logs', 'shannon');
    fs.mkdirSync(dir, { recursive: true });
    fs.appendFileSync(path.join(dir, 'tripwires.jsonl'), JSON.stringify(entry) + '\n');
  } catch (_) {}
}

// ---- Bash branch ----
function runBashChecks(payload) {
  const tin = (payload && payload.tool_input) || {};
  const tres = (payload && (payload.tool_result || payload.tool_response)) || {};
  const cmd = String(tin.command || '');
  const out = typeof tres === 'string' ? tres : String((tres.stdout || tres.output || ''));
  const msgs = [];
  if (BUILD_CMDS.test(cmd) && BUILD_SUCCESS.test(out)) {
    msgs.push('[shannon] validation-not-compilation: build succeeded, but compilation is NOT functional validation. Invoke /shannon:validate to verify through real interfaces.');
    appendTripwire({ ts: new Date().toISOString(), event: 'build-success-without-validation', command: cmd.slice(0, 200) });
    msgs.push('[shannon] TRIPWIRE: build succeeded but functional-validation skill has not been invoked since last build. Run /shannon:validate before claiming completion.');
  }
  if (CLAIM.test(out)) {
    msgs.push('[shannon] completion-claim-validator: completion phrase detected. Verify with cited evidence (screenshot path, log line, response body) before claiming done.');
  }
  return msgs;
}

// ---- Edit/Write/MultiEdit branch ----
function runEditWriteChecks(payload) {
  const tin = (payload && payload.tool_input) || {};
  const fp = tin.file_path || tin.filePath || '';
  const content = String(tin.content || tin.new_string || '');
  const msgs = [];

  // fab-pattern-detection
  if (content) {
    const matched = FAB_HINTS.find(re => re.test(content));
    if (matched) msgs.push(`[shannon] fab-pattern-detection: content matches fabrication pattern ${matched}. IRON RULE: build the real system; never wire fake-test scaffolding.`);
  }

  // evidence-quality-check
  if (fp && (/\/e2e-evidence\//.test(fp) || /\/evidence\//.test(fp))) {
    try {
      if (fs.existsSync(fp)) {
        const st = fs.statSync(fp);
        if (st.size === 0) msgs.push(`[shannon] evidence-quality-check: "${fp}" is 0 bytes. Empty files are INVALID evidence.`);
      }
    } catch (_) {}
  }
  return msgs;
}

runHook('post-action-discipline', (payload) => {
  const tool = String(payload && (payload.tool_name || payload.tool) || '');
  let msgs = [];
  if (/^Bash$/.test(tool)) msgs = runBashChecks(payload);
  else if (/^(Edit|Write|MultiEdit)$/.test(tool)) msgs = runEditWriteChecks(payload);
  if (!msgs.length) return { decision: 'allow', exitCode: 0 };
  return {
    decision: 'allow',
    exitCode: 2,
    stderrPayload: msgs.join('\n') + '\n',
  };
});
