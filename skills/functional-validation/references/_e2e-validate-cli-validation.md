# CLI Validation

> Real-system validation for command-line tools: build, execute, capture stdout/stderr/exit codes, verify side effects. No mocks. The binary you ship is the binary you validate.

## Detection signals

A project is CLI when ONE of these holds:

| Manifest | Marker | Build target |
|----------|--------|--------------|
| `Cargo.toml` | `[[bin]]` section | `cargo build --release` → `target/release/<name>` |
| `go.mod` | `package main` in root or `cmd/<name>/main.go` | `go build -o ./bin/<name> ./cmd/<name>` |
| `pyproject.toml` | `[project.scripts]` table | `pip install -e .` → console script |
| `package.json` | `"bin"` field | `npm link` or direct invocation via `npx` |
| `setup.py` | `entry_points={'console_scripts': ...}` | `pip install -e .` |
| `Makefile` | `install:` target | `make && make install` |

If multiple match, the closest-to-root manifest wins.

## Validation protocol

### Phase 1 — Build

Build before you execute. Builds can fail in ways that hide execution failures (stale binary, missing dependency). Always rebuild before a validation run.

```bash
# Rust
cargo build --release 2>&1 | tee e2e-evidence/build.log
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "BUILD_FAIL"; exit 1; }

# Go
go build -o ./bin/<name> ./cmd/<name>/... 2>&1 | tee e2e-evidence/build.log

# Python (editable install captures pyproject changes)
pip install -e . --break-system-packages 2>&1 | tee e2e-evidence/build.log

# Node
npm install 2>&1 | tee e2e-evidence/build.log

# Make
make 2>&1 | tee e2e-evidence/build.log
```

Capture the build log to `e2e-evidence/build.log` so a failed validation can be reproduced.

### Phase 2 — Smoke test

Every CLI ships `--help` and `--version`. If those don't return cleanly, nothing else will.

```bash
./bin/<name> --version 2>&1 | tee e2e-evidence/smoke-version.txt
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "SMOKE_VERSION_FAIL"; exit 1; }

./bin/<name> --help 2>&1 | tee e2e-evidence/smoke-help.txt
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "SMOKE_HELP_FAIL"; exit 1; }
```

**PASS criterion:** exit 0 + non-empty stdout. **FAIL criterion:** anything else.

### Phase 3 — Journey execution

For each user journey identified in the plan, execute the real binary with real arguments. Examples:

```bash
# Journey 1: process a file
./bin/<name> process input.txt --format=json 2>&1 \
  | tee e2e-evidence/journey-01-process.log
echo "exit=$?" >> e2e-evidence/journey-01-process.log

# Journey 2: pipe through stdin
echo "test input" | ./bin/<name> filter 2>&1 \
  | tee e2e-evidence/journey-02-filter.log

# Journey 3: subcommand chain
./bin/<name> init --name=test-run 2>&1 | tee e2e-evidence/journey-03-init.log
./bin/<name> add --target=foo 2>&1 | tee -a e2e-evidence/journey-03-init.log
./bin/<name> status 2>&1 | tee -a e2e-evidence/journey-03-init.log
```

### Phase 4 — Side-effect verification

Most CLIs do something — write files, mutate state, emit to a database, send a network call. Capture and verify:

```bash
# Created files
find /path/to/output-dir -newer e2e-evidence/build.log -type f \
  | tee e2e-evidence/journey-01-files-created.txt

# Mutated config
diff config.json.before config.json.after \
  | tee e2e-evidence/journey-01-config-diff.txt

# Network calls (if the CLI hits an API, validate at the API level too — see api-validation.md)

# Database writes (validate by curling/connecting to the DB)
```

### Phase 5 — Verdict

For every journey, write a verdict:

```
e2e-evidence/journey-01-process.verdict.md
---
**Journey**: process input.txt
**Command**: ./bin/<name> process input.txt --format=json
**Expected**: exit 0, stdout contains '"status":"ok"', file output.json exists and parses as JSON
**Observed**:
  - exit code: 0 ✓
  - stdout: '{"status":"ok","items":[…]}' ✓
  - output.json: 1247 bytes, parses ✓
**Verdict**: PASS
**Evidence**: e2e-evidence/journey-01-process.log, e2e-evidence/journey-01-files-created.txt
```

## Iron Rule for CLI

NEVER write `test_<name>.py` or `<name>_test.go` etc. as part of CLI validation. Tests are RUNS of the real binary, captured to disk. If you find yourself reaching for a test framework, stop — you're validating the framework, not the CLI.

## Exit-code semantics

CLI tools encode meaning in exit codes. Validate the SPECIFIC code, not just "non-zero":

| Exit | Meaning | Validate by |
|------|---------|-------------|
| 0 | Success | `[ $? -eq 0 ]` |
| 1 | General error | `[ $? -eq 1 ]` (often "shouldn't happen on PASS path") |
| 2 | Misuse (bad args) | Validate with intentionally-bad args; expect 2 |
| 64-78 | sysexits.h codes (POSIX) | Match each documented code |
| 124 | Timeout | If you ran via `timeout <N> ./bin`, 124 = timed out |
| 130 | SIGINT (Ctrl-C) | Expect 130 if you wired a Ctrl-C test |
| 137 | SIGKILL (OOM/kill -9) | If observed, something forcibly killed it |

Save the exit code into the journey log: `echo "exit=$?" >> log` immediately after the command.

## Stdout vs stderr discipline

A clean CLI sends:
- **Structured output** to stdout (parseable, can be piped)
- **Diagnostic messages** to stderr (logs, errors, warnings)

Validate both streams separately:

```bash
./bin/<name> command \
  > e2e-evidence/journey-01.stdout \
  2> e2e-evidence/journey-01.stderr

# Stdout should parse cleanly
jq . e2e-evidence/journey-01.stdout > /dev/null \
  || { echo "stdout is not valid JSON"; exit 1; }

# Stderr should be diagnostic only (not contain stdout-shaped data)
grep -E '^\{|^\[' e2e-evidence/journey-01.stderr \
  && { echo "stderr contains structured data — split is wrong"; exit 1; }
```

## Long-running CLI

Some CLIs run for minutes/hours (data processors, watchers, daemons). Wrap in `timeout` with a generous bound:

```bash
timeout --preserve-status 300 ./bin/<name> long-running-task 2>&1 \
  | tee e2e-evidence/journey-04-long.log
case $? in
  0)   echo "completed normally" ;;
  124) echo "TIMEOUT — increase budget or split journey" ;;
  *)   echo "exit=$?" ;;
esac
```

## Common anti-patterns

| Anti-pattern | Why it's wrong | Do this instead |
|--------------|----------------|------------------|
| Running unit tests as "validation" | Unit tests test the test, not the shipping binary | Build + execute the real binary, capture stdout |
| Skipping the rebuild | Stale binary masks regressions | Always `cargo build` / `go build` / `pip install -e .` first |
| Capturing exit code but not validating it | Verdict claims PASS while exit was 1 | Assert exit code explicitly per journey |
| Mocking stdin to "simulate" the CLI | The mock doesn't have the real CLI's argument parser | Pipe real bytes via `echo`/`cat`/`<<EOF` |
| One log file for all journeys | Can't attribute a failure to a specific journey | One log file per journey |

## Cross-references

- `references/api-validation.md` — when the CLI hits a remote API, validate the API end too
- `references/fullstack-validation.md` — full-stack CLI clients (e.g., `gh`, `kubectl`) need both CLI + API validation
- `skills/no-mocking-validation-gates/` — prevents the test-file temptation during CLI work
- `skills/gate-validation-discipline/` — enforces transcript-evidence Iron Rule on the verdict
