// META
// name: block-fab-files
// event: PreToolUse:Write|Edit|MultiEdit
// consumed_by_skills: no-fakes-discipline
// description: Iron Rule fab-file blocker — refuses Write/Edit on *.test.*, *.spec.*, tests/, __tests__/, mocks/.

const { runHook } = require('./_lib.js');

const FAB_PATTERNS = [
  /\.test\.[a-z]+$/i,
  /\.spec\.[a-z]+$/i,
  /\/tests?\//i,
  /\/__tests?__\//i,
  /\/__mocks__\//i,
  /\/mocks?\//i,
  /\/fixtures?\//i,
  /\/stubs?\//i,
];

runHook('block-fab-files', (payload) => {
  const tin = (payload && payload.tool_input) || {};
  const fp = tin.file_path || '';  // CC docs: file_path is snake_case
  if (!fp) return { decision: 'allow', exitCode: 0 };
  const matched = FAB_PATTERNS.find(re => re.test(fp));
  if (!matched) return { decision: 'allow', exitCode: 0 };
  return {
    decision: 'block',
    exitCode: 2,
    stderrPayload: `[shannon] block-fab-files: refusing Write/Edit on "${fp}" — matches Iron Rule fabrication pattern ${matched}. Shannon v1 does not allow mocks/stubs/test files (no-fakes-discipline skill). Build the real system instead.\n`,
  };
});
