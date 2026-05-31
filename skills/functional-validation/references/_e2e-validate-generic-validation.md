# Generic Validation

> Fallback protocol for projects that don't match a standard platform (CLI / API / Web / iOS / Full-stack). Detect what the user actually runs to "use" the project, run that, capture evidence, write a verdict.

## When this applies

You're here when:
- `xcodeproj` is absent → not iOS/macOS
- `Cargo.toml [[bin]]` / `go.mod` / `package.json bin` are absent → not standard CLI
- No REST routes / OpenAPI / handlers → not API
- No JSX / Vue / Svelte / Next config → not Web

Examples:
- Pure library projects (no executable; published as a package)
- Browser extensions (Manifest V3, no traditional dev server)
- VS Code / IntelliJ extensions
- Game projects (Unity, Godot, Unreal — partial coverage via their own validation patterns)
- Embedded firmware (Arduino, ESP32, STM32)
- Data pipelines (DAGs in Airflow, Prefect, Dagster)
- Shell-script collections
- Documentation sites (mkdocs, Hugo, Jekyll — partial overlap with web)
- ML model artifacts (checkpoints, ONNX exports, GGUF)

## The discovery protocol

Generic validation is mostly: **figure out what "running" means for this project, then make it run**.

### Step 1 — README archaeology

```bash
# Read every README at every level
find . -maxdepth 4 -iname 'readme*' -type f \
  | head -10 \
  > e2e-evidence/readme-list.txt

# Look for invocation patterns
grep -rE '```(bash|sh|console|shell)' . --include='README*' -A 10 \
  | head -100 \
  > e2e-evidence/invocation-patterns.txt
```

If the README says `make demo`, that's a journey. If it says `./run.sh`, that's a journey. If it says `import mylib; mylib.do_thing()` in a Python REPL, that's a journey.

### Step 2 — Manifest archaeology

Check every dependency manifest for invocation hints:

```bash
# package.json scripts
[ -f package.json ] && jq -r '.scripts // {} | keys[]' package.json > e2e-evidence/npm-scripts.txt

# Makefile targets
[ -f Makefile ] && grep -E '^[a-z][a-zA-Z0-9_-]*:' Makefile | cut -d: -f1 > e2e-evidence/make-targets.txt

# pyproject.toml entries
[ -f pyproject.toml ] && grep -E '^\[tool|\[project' pyproject.toml > e2e-evidence/pyproject-sections.txt

# justfile / task / etc.
[ -f justfile ] && just --list > e2e-evidence/just-recipes.txt
```

The user-facing "run" commands usually surface in one of these.

### Step 3 — Build-then-run

If a build step exists, run it first:

```bash
# Try in order:
[ -f Makefile ] && make build 2>&1 | tee e2e-evidence/build.log

[ -f package.json ] && npm run build 2>&1 | tee e2e-evidence/build.log

[ -f Cargo.toml ] && cargo build 2>&1 | tee e2e-evidence/build.log

[ -f setup.py ] && pip install -e . --break-system-packages 2>&1 | tee e2e-evidence/build.log

# … etc per language
```

A build failure is the first finding. Stop and report — there's no point validating broken artifacts.

### Step 4 — Identify the "running" surface

What does the project DO when used?

- **Library**: `import` it from a real script, exercise its public surface
- **Extension**: install it (browser / IDE), open the host, capture what changed
- **DAG**: run it (locally — Airflow standalone, Prefect local, Dagster dev), verify outputs
- **Shell collection**: invoke each script with realistic args, capture stdout
- **Firmware**: flash to real hardware (or QEMU if available), verify expected serial output
- **Documentation site**: build, serve locally, smoke-test the rendered pages (drops into web-validation territory)

### Step 5 — Library validation (most common generic case)

A library doesn't ship with a launcher. Write a real-system exerciser:

```bash
# Example: Python library
cat > e2e-evidence/exercise.py <<'PY'
from mylib import compute, transform, serialize

# Real input, not a mock
data = {"id": 1, "values": [1, 2, 3, 4, 5]}
result = compute(data)
print(f"compute: {result}")

transformed = transform(result)
print(f"transform: {transformed}")

output = serialize(transformed)
with open("e2e-evidence/exercise-output.json", "w") as f:
    f.write(output)

print("PASS" if "id" in output else "FAIL")
PY

python3 e2e-evidence/exercise.py 2>&1 | tee e2e-evidence/exercise.log
```

The "test" is: does the library, exercised through its real public API, produce expected outputs? PASS criteria are from the library's docs (compute returns N, transform preserves shape, etc.).

NEVER write a unit test for this. The exerciser IS the validation, the output file IS the evidence.

### Step 6 — Extension validation

Browser extensions need the real browser:

```bash
# Build the extension bundle
npm run build:extension 2>&1 | tee e2e-evidence/build.log

# Load it into the browser (Chrome via CLI)
google-chrome \
  --user-data-dir=/tmp/extension-validation \
  --load-extension=$(pwd)/dist \
  https://example.com  # a page the extension should affect

# After interaction:
# 1. screenshot the page
# 2. check storage.local for expected values
# 3. capture console.log output via --enable-logging
```

VS Code extensions can be validated similarly with `code --extensionDevelopmentPath=$(pwd)`.

### Step 7 — DAG / pipeline validation

```bash
# Airflow standalone
airflow standalone &
sleep 10
airflow dags trigger my_dag --conf '{"date":"2024-01-01"}'
airflow dags list-runs -d my_dag | tee e2e-evidence/dag-run.txt

# Prefect local
prefect deployment run my_flow/local
prefect flow-run logs latest > e2e-evidence/flow-run.log

# Verify outputs landed where expected
ls -la /path/to/expected/output | tee e2e-evidence/dag-outputs.txt
```

## Verdict template

```
e2e-evidence/journey-NN.verdict.md
---
**Journey**: <what the user does to "use" the project>
**Invocation**: <exact command>
**Expected**:
  - <concrete observable 1>
  - <concrete observable 2>
**Observed**:
  - <what actually happened — cite evidence>
**Verdict**: PASS | FAIL | INDETERMINATE
**Evidence**: <list of files in e2e-evidence/>
**Notes**: <if INDETERMINATE, what would resolve it>
```

INDETERMINATE is a legitimate verdict for generic validation when the project's "running" surface is genuinely ambiguous. Better to say "I couldn't determine PASS/FAIL because the project's expected output isn't documented" than to fabricate a PASS.

## Iron Rule for generic

The Iron Rule still applies in the generic case — sometimes MORE strictly because the temptation to "just write a quick test" is highest when the project doesn't have an obvious user-facing surface.

If you find yourself reaching for a test framework instead of an exerciser script, STOP. The question is: what does a real user DO with this project? Whatever that is, that's the journey. Capture it.

## Common anti-patterns

| Anti-pattern | Why it's wrong | Do this instead |
|--------------|----------------|------------------|
| "There's no entry point, can't validate" | Every project has SOMETHING someone runs | Read the README for invocation; if absent, document that as a finding |
| Writing pytest cases for a library | pytest tests test the test framework, not your library's real use | Write an exerciser script that uses the public API |
| Validating only the build | Build success ≠ runtime success | Build, then exercise the artifact |
| Skipping the discovery phase | Wrong assumption about what the project IS leads to wrong validation | Read the README, manifests, and at least one source file before starting |

## Cross-references

- `references/cli-validation.md` — if the project surfaces a CLI binary, even unintentionally
- `references/web-validation.md` — for doc sites or browser extensions
- `references/api-validation.md` — for embedded HTTP servers
- `skills/functional-validation/` — Iron Rule + per-platform routing
- `skills/no-mocking-validation-gates/` — applies extra-strictly to generic / library cases
- `skills/gate-validation-discipline/` — verdict gate enforcement
