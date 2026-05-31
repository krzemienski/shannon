---
name: enforce
description: "Activate or deactivate Shannon enforcement for the current project. Replaces the legacy enable/disable pair."
argument-hint: "<on|off> [--force]"
---

# /shannon:enforce

Toggle Shannon enforcement for the current project.

> v1 consolidation: absorbs legacy `/shannon:enable` (=`on`) and `/shannon:disable` (=`off`).

## Inputs

- Positional: `on` or `off` (required)
- `--force` — override sticky disabled state (only meaningful with `on`)

## Behavior

### enforce=on
1. Resolve project root: `$CLAUDE_PROJECT_DIR` if set, else `pwd`.
2. `mkdir -p .shannon`.
3. If `.shannon/disabled` exists: remove it ONLY if `--force`; else refuse.
4. Write `.shannon/active` with ISO timestamp + Shannon version.
5. Print confirmation + gate semantics summary.

### enforce=off
1. Resolve project root.
2. `mkdir -p .shannon`.
3. Remove `.shannon/active` if present.
4. Write `.shannon/disabled` with ISO timestamp + reason (from `$2` if given).
5. Sticky: survives until `/shannon:enforce on --force`.

## Implementation (Bash)

```bash
MODE="$1"
ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
mkdir -p "$ROOT/.shannon"
case "$MODE" in
  on)
    if [ -f "$ROOT/.shannon/disabled" ]; then
      if [ "$2" = "--force" ]; then rm "$ROOT/.shannon/disabled"
      else echo "Refusing: .shannon/disabled present. Re-run with --force." >&2; exit 1; fi
    fi
    printf '{"activated":"%s","version":"0.1.0"}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$ROOT/.shannon/active"
    echo "Shannon enforcement ON at $ROOT/.shannon/active"
    ;;
  off)
    rm -f "$ROOT/.shannon/active"
    REASON="${2:-user-requested}"
    printf '{"disabled":"%s","reason":"%s"}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$REASON" > "$ROOT/.shannon/disabled"
    echo "Shannon enforcement OFF at $ROOT/.shannon/disabled"
    ;;
  *)
    echo "Usage: /shannon:enforce <on|off> [--force]" >&2; exit 1
    ;;
esac
```

## Gate semantics

- `.shannon/active` present, `.shannon/disabled` absent → hooks fire
- `.shannon/disabled` present → hooks no-op (sticky off)
- neither present → hooks no-op (default off; explicit opt-in required)
- `SHANNON_DISABLE=1` env → hooks no-op (per-shell escape)
- `SHANNON_GLOBAL=1` env → hooks fire everywhere (override; for testing)

## Skills + agents

- `Skill: observability-report` (state-file inspection verification — run automatically after toggle to confirm the sentinel file was written and downstream hooks see the new state)

## Examples

```
/shannon:enforce on
/shannon:enforce off "legacy repo; manual workflow"
/shannon:enforce on --force    # override sticky disabled
```
