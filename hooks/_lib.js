// Shannon v1 hook helpers — self-contained, no external dependencies.
// Replaces v7's ../lib/hook-runner. Reads CC hook payload from stdin (JSON),
// runs the supplied handler, writes optional stdout/stderr, exits with rc.

const fs = require('fs');
const os = require('os');
const path = require('path');

function readStdinJson() {
  try {
    const buf = fs.readFileSync(0, 'utf8');
    if (!buf || !buf.trim()) return {};
    return JSON.parse(buf);
  } catch (e) {
    return {};
  }
}

function logError(scriptName, err) {
  try {
    const dir = path.join(os.homedir(), '.claude', 'logs', 'shannon');
    fs.mkdirSync(dir, { recursive: true });
    const entry = JSON.stringify({
      ts: new Date().toISOString(),
      script: scriptName,
      error: String(err),
      stack: err && err.stack,
    }) + '\n';
    fs.appendFileSync(path.join(dir, 'hook-errors.jsonl'), entry);
  } catch (_) { /* silent */ }
}

function shannonActive() {
  // Honor SHANNON_DISABLE escape; honor SHANNON_GLOBAL override.
  if (process.env.SHANNON_GLOBAL === '1') return true;
  if (process.env.SHANNON_DISABLE === '1') return false;
  const root = process.env.CLAUDE_PROJECT_DIR || process.cwd();
  try {
    if (fs.existsSync(path.join(root, '.shannon', 'disabled'))) return false;
    return fs.existsSync(path.join(root, '.shannon', 'active'));
  } catch (_) {
    return false;
  }
}

function runHook(scriptName, handler) {
  // If Shannon not active in this project, no-op (per gate semantics in
  // /shannon:enforce command). Always exit 0; never disturb host project.
  if (!shannonActive()) {
    process.exit(0);
  }
  const payload = readStdinJson();
  let result;
  try {
    result = handler(payload) || { decision: 'allow', exitCode: 0 };
  } catch (e) {
    logError(scriptName, e);
    process.exit(0); // fail-safe: never break the user's session
  }
  if (result.stdoutPayload) process.stdout.write(result.stdoutPayload);
  if (result.stderrPayload) process.stderr.write(result.stderrPayload);
  process.exit(result.exitCode || 0);
}

module.exports = { runHook, readStdinJson, shannonActive, logError };
