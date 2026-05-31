#!/usr/bin/env bash
# scripts/harness/run-all.sh — orchestrate SDK + Tmux harness runs.
#
# Usage:
#   bash scripts/harness/run-all.sh                  # --dry-run --all (default)
#   bash scripts/harness/run-all.sh --dry-run --sdk
#   bash scripts/harness/run-all.sh --dry-run --tmux
#   bash scripts/harness/run-all.sh --live --all     # requires API + tmux + claude
#
# Iron Rule:
#   - Never silently substitutes --dry-run for --live when live tooling is missing;
#     --live failures are explicit and exit 1.

set -e
HARNESS_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HARNESS_DIR/../.." && pwd)"
EVIDENCE_DIR="$REPO_ROOT/.planning/phases/05-harnesses/evidence"
mkdir -p "$EVIDENCE_DIR"

MODE="--dry-run"
TARGET="all"
BENCHMARK=""

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) MODE="--dry-run"; shift ;;
    --live) MODE="--live"; shift ;;
    --sdk) TARGET="sdk"; shift ;;
    --tmux) TARGET="tmux"; shift ;;
    --all) TARGET="all"; shift ;;
    --benchmark) BENCHMARK="--benchmark $2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

echo "=== Shannon v1 harness orchestrator ==="
echo "Mode: $MODE"
echo "Target: $TARGET"
echo "Repo: $REPO_ROOT"
echo ""

SDK_RC=0
TMUX_RC=0

if [ "$TARGET" = "all" ] || [ "$TARGET" = "sdk" ]; then
  echo "--- SDK runner ---"
  python3 "$HARNESS_DIR/sdk_runner.py" $MODE $BENCHMARK > "$EVIDENCE_DIR/sdk-${MODE#--}.json" 2>&1
  SDK_RC=$?
  python3 -c "
import json
try:
    d = json.load(open('$EVIDENCE_DIR/sdk-${MODE#--}.json'))
    print('  mode:', d.get('mode'))
    if 'summary' in d: print('  summary:', json.dumps(d['summary']))
    print('  verdicts:', len(d.get('verdicts', [])))
except Exception as e:
    print('  PARSE-ERROR:', e)
"
  echo "  exit code: $SDK_RC"
  echo ""
fi

if [ "$TARGET" = "all" ] || [ "$TARGET" = "tmux" ]; then
  echo "--- Tmux runner ---"
  python3 "$HARNESS_DIR/tmux_runner.py" $MODE $BENCHMARK > "$EVIDENCE_DIR/tmux-${MODE#--}.json" 2>&1
  TMUX_RC=$?
  python3 -c "
import json
try:
    d = json.load(open('$EVIDENCE_DIR/tmux-${MODE#--}.json'))
    print('  mode:', d.get('mode'))
    if 'summary' in d: print('  summary:', json.dumps(d['summary']))
    print('  verdicts:', len(d.get('verdicts', [])))
except Exception as e:
    print('  PARSE-ERROR:', e)
"
  echo "  exit code: $TMUX_RC"
  echo ""
fi

echo "=== Aggregate ==="
echo "SDK runner exit: $SDK_RC"
echo "Tmux runner exit: $TMUX_RC"

if [ "$SDK_RC" -ne 0 ] || [ "$TMUX_RC" -ne 0 ]; then
  exit 1
fi
exit 0
