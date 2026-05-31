# CLI Functional Validation

This reference is loaded by the `functional-validation` skill ONLY when the project is a command-line application (Rust, Go, Python with `[project.scripts]`, Node CLI, shell, etc.). It expands the build/execute/capture protocol for binary or module-style executables.

Do not load this file for projects with a UI surface — use `ios-validation.md` or `web-validation.md` instead.

## The protocol at a glance

```
build -> run with real input -> capture stdout/stderr/exit code ->
inspect any side-effect files -> verify against PASS criteria -> verdict
```

CLI validation looks the simplest of the four platforms but has the most ways to silently lie. Exit code 0 with nothing on stdout is a common false PASS. Stderr contains the real story. Side-effect files (database rows, written files, modified caches) are where regressions actually hide.

## Detection signals (parent skill already checked)

| File present | Implication | Build/run |
|---|---|---|
| `Cargo.toml` | Rust CLI | `cargo build --release && ./target/release/<bin>` |
| `go.mod` with `main.go` | Go CLI | `go build -o bin/<name> && ./bin/<name>` |
| `pyproject.toml` with `[project.scripts]` | Python CLI | `pip install -e . && <entry-point>` |
| `package.json` with `"bin":` | Node CLI | `npm link && <bin-name>` |
| `.sh` entry point | Shell CLI | `chmod +x ./<script>.sh && ./<script>.sh` |
| `composer.json` with `"bin":` | PHP CLI | `composer install && ./vendor/bin/<name>` |
| `Gemfile` with executable spec | Ruby CLI | `bundle install && bundle exec <name>` |

If the project provides both an entry-point script and a `main` function, run the entry point — that is what users invoke.

## Phase 1 — Build the real binary

Build with the same flags a release build uses. Debug builds may hide optimization-only bugs; debug-only flags may mask production behavior.

```bash
RUN_DIR="e2e-evidence/$(date +%Y-%m-%dT%H-%M-%S)/cli-journey"
mkdir -p "$RUN_DIR"

# Pick ONE that matches the project
cargo build --release 2>&1 | tee "$RUN_DIR/build.log"
# OR
go build -trimpath -ldflags='-s -w' -o bin/myapp ./cmd/myapp 2>&1 | tee "$RUN_DIR/build.log"
# OR
pip install -e . 2>&1 | tee "$RUN_DIR/build.log"

# Verify build succeeded by inspecting both exit code AND the artifact
test -x target/release/myapp || { echo "Build artifact missing"; exit 1; }
```

NEVER mark validation PASS based on a build that didn't actually produce an executable. A successful compile of half the code, with the link step erroring quietly, is still "exit 0" from many toolchains.

## Phase 2 — Run against a real input

Pass real arguments. Use a real file path, a real URL, a real piece of data. Synthetic minimal inputs hide everything the real ones expose.

```bash
# Capture all three: stdout, stderr, exit code. ALL THREE.
./target/release/myapp \
  --input /Users/me/real-data/input.json \
  --output "$RUN_DIR/output.json" \
  > "$RUN_DIR/stdout.txt" \
  2> "$RUN_DIR/stderr.txt"
EXIT_CODE=$?
echo "$EXIT_CODE" > "$RUN_DIR/exit-code.txt"
```

For CLIs that consume stdin, pipe a real input file in. Echo-ing a string is fine for trivial cases; for anything non-trivial, use the same file a real user would.

```bash
cat /path/to/real-input.json | ./target/release/myapp --transform \
  > "$RUN_DIR/stdout.txt" 2> "$RUN_DIR/stderr.txt"
```

For long-running CLIs (servers, watchers, REPLs) wrap in a timeout:

```bash
timeout --preserve-status 30s ./target/release/myapp serve \
  > "$RUN_DIR/stdout.txt" 2> "$RUN_DIR/stderr.txt" &
PID=$!
sleep 3
# Exercise the running process via signals or sibling commands
curl -fsS http://localhost:8080/ping > "$RUN_DIR/curl-ping.txt" || true
kill "$PID" 2>/dev/null
wait
```

## Phase 3 — Capture side-effects

CLIs that modify state are far more common than CLIs that only print. Diff before/after to expose everything the CLI did.

```bash
# Snapshot before
git -C "$TARGET_REPO" status --porcelain > "$RUN_DIR/git-before.txt"
sha256sum data/cache/*.bin > "$RUN_DIR/cache-before.txt" 2>/dev/null || true

# Run
./target/release/myapp migrate

# Snapshot after
git -C "$TARGET_REPO" status --porcelain > "$RUN_DIR/git-after.txt"
sha256sum data/cache/*.bin > "$RUN_DIR/cache-after.txt" 2>/dev/null || true

# Diff — the real evidence
diff "$RUN_DIR/git-before.txt" "$RUN_DIR/git-after.txt" > "$RUN_DIR/git-diff.txt" || true
diff "$RUN_DIR/cache-before.txt" "$RUN_DIR/cache-after.txt" > "$RUN_DIR/cache-diff.txt" || true
```

For database-touching CLIs, capture a row count or representative query both before and after.

## Phase 4 — Verify

A PASS for a CLI requires all of:

1. **Exit code matches expectation.** `echo $?` is the most important number. Document the expected value BEFORE you run.
2. **Stdout matches expectation.** "It printed something" is not a PASS. Either the output exactly matches a fixed expected string, or a structured field in the output (e.g., a JSON key) holds a specific value.
3. **Stderr is empty OR contains only known-OK lines.** A non-empty stderr from a tool that claims to be silent is a bug. Document explicitly which stderr lines are acceptable.
4. **Side-effects match expectation.** If the CLI claimed to write a file, the file must exist AND have non-zero size AND contain the expected content. If the CLI claimed to skip writing, the file must not exist or be unchanged.
5. **Performance is sane.** Wrap the run in `time` and check wall-clock time. Performance regressions are bugs; they don't bubble up as exit-code-nonzero failures.

```bash
# A canonical CLI verdict snippet
EXIT_CODE=$(cat "$RUN_DIR/exit-code.txt")
EXPECTED=0

if [ "$EXIT_CODE" != "$EXPECTED" ]; then
  echo "FAIL: exit code $EXIT_CODE, expected $EXPECTED"
  echo "stderr tail:"
  tail -20 "$RUN_DIR/stderr.txt"
  exit 1
fi

# Verify a structured field in stdout
TOTAL=$(jq -r .processed "$RUN_DIR/stdout.txt" 2>/dev/null)
test "$TOTAL" -ge 1 || { echo "FAIL: processed=$TOTAL"; exit 1; }

# Verify output file exists and is non-empty
test -s "$RUN_DIR/output.json" || { echo "FAIL: empty output"; exit 1; }
```

Then invoke `evidence-gate` to apply the refusal-discipline checklist.

## Evidence quality table

| Evidence | Good | Bad |
|---|---|---|
| stdout | `Processed 1500 records in 2.3s` | `Done` |
| stderr | (empty) or `INFO loaded config from /etc/myapp.toml` | (large; contains "warning" but ignored) |
| exit code | `0` (matches expected) | `0` (but expected was non-zero failure case) |
| side-effect | `output.json` with `{"records": 1500, "errors": 0}` | `output.json` exists, content not checked |
| time | `real 2.3s` | `real 0.001s` (suspiciously fast — did it run?) |

## Common CLI failure modes

| Symptom | Likely cause | Remedy |
|---|---|---|
| Exit 0 with empty stdout | Wrong subcommand, or CLI fell into help/usage path | Check `--help` is not the active path; re-run with `--verbose` |
| Exit 1 with no stderr | Panic or unhandled exception swallowed | Set `RUST_BACKTRACE=1` / `PYTHONUNBUFFERED=1` / `GOTRACEBACK=all` |
| Output file empty | Race condition or buffered writer not flushed | Add explicit flush/close in CLI; verify with `lsof` while running |
| Different output on subsequent runs | Non-determinism — random seed, time-based, or unsorted | Pin seed; pipe through `sort` for comparison; capture both runs |
| Works locally, fails in CI | Missing env var, locale, or PATH entry | Diff `env` output between environments |
| OOM kill | Memory leak or unbounded loop | Wrap in `/usr/bin/time -v` to capture max RSS |

## When CLI path does NOT apply

- The "CLI" is actually a TUI (curses, blessed, ratatui) — combine with screenshot capture via `tmux capture-pane` or a terminal screenshot tool
- The "CLI" spawns a UI window (Electron-without-CLI-UI, Tauri) — fall back to web or platform-native validation
- The CLI is a shell completion or hook — validate via the surrounding shell's behavior

## Evidence checklist

A PASS for a CLI feature requires at least:
- `build.log` ending in success
- `stdout.txt`, `stderr.txt`, `exit-code.txt` for every run
- Side-effect diffs (`git-diff.txt`, `cache-diff.txt`, etc.) when the CLI modifies state
- A `verdict.md` citing exact lines from stdout/stderr that prove the PASS criteria
- Wall-clock time captured (regression signal)
